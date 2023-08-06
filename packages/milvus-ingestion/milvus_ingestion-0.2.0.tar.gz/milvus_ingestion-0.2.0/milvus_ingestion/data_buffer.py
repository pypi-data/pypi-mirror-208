# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License
# is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
# or implied. See the License for the specific language governing permissions and limitations under
# the License.

import json
import time
import os
import numpy

from logging import Logger

from pymilvus import (
    DataType,
)

from .util import (
    Base,
    default_logger,
)

from .constants import (
    IngestionType,
    OUTPUT_FOLDER,
    MB,
    GB,
)

from .milvus_connector import (
    MilvusConnector,
    default_milvus,
)

from .uploader import (
    Uploader,
    default_uploader,
)


class DataBuffer(Base):
    def __init__(
            self,
            milvus_connector: MilvusConnector = default_milvus,
            uploader: Uploader = default_uploader,
            ingestion_type: IngestionType = IngestionType.ROW_BASED,
            logger: Logger = default_logger(),
        ):
        super().__init__(logger=logger)
        self._milvus_connector = milvus_connector
        self._uploader = uploader
        self._ingestion_type = ingestion_type
        self._target_collection_schema = None
        self._target_fields = {}
        self._output_folder = OUTPUT_FOLDER
        self._data_size_per_block = 1*GB
        self._buffer_size = 0
        self._buffer = {}
        if self._ingestion_type == IngestionType.ROW_BASED:
            self._buffer = []

        self._default_values = {
            DataType.BOOL.name: False,
            DataType.INT8.name: 0,
            DataType.INT16.name: 0,
            DataType.INT32.name: 0,
            DataType.INT64.name: 0,
            DataType.FLOAT.name: 0.0,
            DataType.DOUBLE.name: 0,
            DataType.VARCHAR.name: "",
        }

        self._type_size = {
            DataType.BOOL.name: 1,
            DataType.INT8.name: 8,
            DataType.INT16.name: 8,
            DataType.INT32.name: 8,
            DataType.INT64.name: 8,
            DataType.FLOAT.name: 8,
            DataType.DOUBLE.name: 8,
        }

        self._type_validator = {
            DataType.BOOL.name: lambda x: isinstance(x, bool),
            DataType.INT8.name: lambda x: isinstance(x, int) and -128 <= x <= 127,
            DataType.INT16.name: lambda x: isinstance(x, int) and -32768 <= x <= 32767,
            DataType.INT32.name: lambda x: isinstance(x, int) and -2147483648 <= x <= 2147483647,
            DataType.INT64.name: lambda x: isinstance(x, int),
            DataType.FLOAT.name: lambda x: isinstance(x, float),
            DataType.DOUBLE.name: lambda x: isinstance(x, float),
            DataType.VARCHAR.name: lambda x, l: isinstance(x, str) and len(x) <= l,
            DataType.FLOAT_VECTOR.name: lambda x, dim: isinstance(x, list) and len(x) == dim,
            DataType.BINARY_VECTOR.name: lambda x, dim: isinstance(x, bytes) and len(x)*8 == dim
        }

    def set_output_folder(self, folder: str):
        self._output_folder = folder

    def set_data_size_per_block(self, data_size: int):
        if data_size <= 0:
            data_size = 512*MB
        self._data_size_per_block = data_size

    def set_default_value(self, data_type: DataType, val)->bool:
        if data_type == DataType.BINARY_VECTOR or data_type == DataType.FLOAT_VECTOR:
            self._print_err("Cannot set default value for vector type")
            return False
        if val is None:
            self._print_err("Not support None default value")
            return False
        self._default_values[data_type.name] = val
        return True

    def clean_buffer(self):
        self._buffer_size = 0
        self._buffer = {}
        if self._ingestion_type == IngestionType.ROW_BASED:
            self._buffer = []

    def clean_output(self):
        def clean_files(path:str):
            for root, dirs, files in os.walk(path):
                for file in files:
                    os.unlink(os.path.join(root, file))

        for root, dirs, files in os.walk(self._output_folder):
            for file in files:
                os.unlink(os.path.join(root, file))
            for dir in dirs:
                clean_files(os.path.join(root, dir))
                os.rmdir(os.path.join(root, dir))
        self._print_info("Finished clean output folder {}".format(self._output_folder))

    def set_target_collection(self, collection_name: str)->bool:
        if self._milvus_connector is None:
            self._print_err("Milvus connector is None")
            return False

        self._target_fields = {}
        self._target_collection_schema = self._milvus_connector.collection_schema(collection_name=collection_name)
        if self._target_collection_schema is None:
            self._print_err("Failed to get schema for collection '{}'".format(collection_name))
            return False

        for field in self._target_collection_schema['fields']:
            self._target_fields[field['name']] = field

        self.clean_buffer()
        return True

    def current_row_count(self)->int:
        if self._ingestion_type == IngestionType.ROW_BASED:
            return len(self._buffer)
        elif len(self._buffer) > 0:
            return len(list(self._buffer.values())[0])
        return 0


    def append_row(self, row: dict)->bool:
        if self._target_collection_schema is None:
            self._print_err("Failed to append row, collection not specified")
            return False

        if not self._verify_row(row=row):
            return False

        if self._buffer_size >= self._data_size_per_block:
            self._print_info("Buffer size {} exceeds {}, force persist"
                             .format(self._buffer_size, self._data_size_per_block))
            self.persist()

        if self._ingestion_type == IngestionType.ROW_BASED:
            self._buffer.append(row)
        else:
            for k in self._target_fields:
                if k not in self._buffer:
                    self._buffer[k] = [row[k]]
                else:
                    self._buffer[k].append(row[k])
        return True

    def _verify_row(self, row: dict)->bool:
        if len(self._target_fields) == 0:
            self._print_err("Target collection schema is empty")
            return False

        row_size = 0
        for k in self._target_fields:
            if k not in row:
                self._print_err("'{}' is missed in the row".format(k))
                return False

            field = self._target_fields[k]
            if 'is_parimary' in field and field['auto_id']:
                self._print_err("The primary key field '{}' is auto-id, no need to provide".format(k))
                return False

            dtype = DataType(field['type'])
            validator = self._type_validator[dtype.name]
            if dtype == DataType.BINARY_VECTOR or dtype == DataType.FLOAT_VECTOR:
                dim = field['params']['dim']
                if not validator(row[k], dim):
                    self._print_err("Vector data doesn't match with {} schema".format(dtype.name))
                    return False
                row_size = row_size + len(row[k])
            elif dtype == DataType.VARCHAR:
                max_len = field['params']['max_length']
                if not validator(row[k], max_len):
                    self._print_err("Varchar value doesn't match with {} schema".format(dtype.name))
                    return False
                row_size = row_size + len(row[k])
            else:
                if not validator(row[k]):
                    self._print_err("Scalar value doesn't match with {} schema".format(dtype.name))
                    return False
                row_size = row_size + self._type_size[dtype.name]
        self._buffer_size = self._buffer_size + row_size
        return True

    def persist(self)->bool:
        os.makedirs(name=self._output_folder, exist_ok=True)
        if self._ingestion_type == IngestionType.ROW_BASED:
            n = 1
            while True:
                target_path = os.path.join(self._output_folder, "rows_{}.json".format(n))
                if not os.path.exists(target_path):
                    break
                n = n + 1

            content = {
                "rows": self._buffer,
            }
            try:
                with open(target_path, 'w', encoding='utf-8') as f:
                    json.dump(obj=content, fp=f, indent=2, ensure_ascii=False)
            except Exception as e:
                self._print_err("Failed to persist row-based file {}, error: {}".format(target_path, e))
                return False

            self._print_info("Successfully persist row-based file {}".format(target_path))
        else:
            n = 1
            while True:
                target_dir = os.path.join(self._output_folder, "columns_{}".format(n))
                if not os.path.exists(target_dir):
                    break
                n = n + 1
            os.makedirs(name=target_dir, exist_ok=True)
            for k in self._buffer:
                target_path = os.path.join(target_dir, k + ".npy")
                try:
                    numpy.save(target_path, self._buffer[k])
                except Exception as e:
                    self._print_err("Failed to persist column-based file {}, error: {}".format(target_path, e))
                    return False

                self._print_info("Successfully persist column-based file {}".format(target_path))

        self._print_info("Successfully persist, clean the buffer now")
        self.clean_buffer()
        return True

    def direct_insert(self, partition_name: str = None)->list:
        if self._milvus_connector is None:
            self._print_err("Milvus connector is None")
            return []

        if len(self._target_fields) == 0:
            self._print_err("Target collection schema is empty")
            return []

        row_count = self.current_row_count()
        if row_count == 0:
            self._print_err("Buffer is empty")
            return []

        size_per_row = self._buffer_size/row_count
        batch = int(8*MB/size_per_row)
        if batch > row_count:
            batch = row_count

        self._print_info("{} rows in buffer, prepare to insert batch by batch, {} rows per batch"
                         .format(row_count, batch))

        primary_ids = []
        if self._ingestion_type == IngestionType.ROW_BASED:
            while len(self._buffer) > 0:
                batch_data = {}
                for k in self._target_fields:
                    batch_data[k] = []
                rows = self._buffer[:batch]
                self._buffer = self._buffer[batch:]
                for row in rows:
                    for k in batch_data:
                        batch_data[k].append(row[k])

                data = []
                for k in batch_data:
                    data.append(batch_data[k])
                ids = self._milvus_connector.insert(data = data,
                                                    collection_name=self._target_collection_schema['collection_name'],
                                                    partition_name=partition_name)
                primary_ids.extend(ids)

        else:
            while len(list(self._buffer.values())[0]) > 0:
                batch_data = {}
                for k in self._target_fields:
                    batch_data[k] = self._buffer[k][:batch]
                    self._buffer[k] = self._buffer[k][batch:]
                data = []
                for k in batch_data:
                    data.append(batch_data[k])
                ids = self._milvus_connector.insert(data=data,
                                                    collection_name=self._target_collection_schema['collection_name'],
                                                    partition_name=partition_name)
                primary_ids.extend(ids)

        self._print_info("Finish insert {} rows into Milvus, clean the buffer now".format(row_count))
        self.clean_buffer()
        return primary_ids

    def upload(self, partition_name: str = None, clean:bool = False)->int:
        if self._uploader is None:
            self._print_err("Uploader is None")
            return 0

        ok, files = self._uploader.upload(self._output_folder)
        if clean:
            self.clean_output()
        if not ok:
            return 0

        if self._milvus_connector is None:
            self._print_err("Milvus connector is None")
            return False

        id = self._milvus_connector.bulk_insert(files=files,
                                                collection_name=self._target_collection_schema['collection_name'],
                                                partition_name=partition_name)
        return id

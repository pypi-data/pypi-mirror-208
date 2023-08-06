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

from logging import Logger

from pymilvus import (
    connections,
    FieldSchema, CollectionSchema, DataType,
    Collection,
    utility,
)

from .util import (
    Base,
    default_logger,
)

CONNECTION_ALIAS = "ingestion"


class MilvusConnector(Base):
    def __init__(
            self,
            address: str,
            user: str = "",
            password: str = "",
            logger: Logger = default_logger(),
        ):
        super().__init__(logger=logger)
        self._address = address
        self._user = user
        self._password = password

    def __connect(self)->bool:
        try:
            if not connections.has_connection(alias=CONNECTION_ALIAS):
                connections.connect(alias=CONNECTION_ALIAS,
                                    address=self._address,
                                    user=self._user,
                                    password=self._password)
            return True
        except Exception as e:
            self._print_err("Failed to connect milvus with address '{}', error: {}".format(self._address, e))
            return False

    def collection_schema(self, collection_name: str)->{}:
        if not self.__connect():
            return None

        if not utility.has_collection(collection_name=collection_name, using=CONNECTION_ALIAS):
            self._print_err("Collection '{}' doesn't exist".format(collection_name))
            return None

        collection = Collection(name=collection_name, using=CONNECTION_ALIAS)
        return collection.describe()

    def _verify_input(self, collection_name: str, partition_name: str)->bool:
        if not self.__connect():
            return False

        if not utility.has_collection(collection_name=collection_name, using=CONNECTION_ALIAS):
            self._print_err("Collection '{}' doesn't exist".format(collection_name))
            return False

        if partition_name is not None:
            if not utility.has_partition(collection_name=collection_name,
                                         partition_name=partition_name,
                                         using=CONNECTION_ALIAS):
                self._print_err("Partition '{}' doesn't exist".format(partition_name))
                return False

        return True

    def insert(self, data: list, collection_name: str, partition_name: str=None)->list:
        if not self._verify_input(collection_name, partition_name):
            return []

        collection = Collection(name=collection_name, using=CONNECTION_ALIAS)
        res = collection.insert(data=data, partition_name=partition_name)
        collection.flush()
        return res.primary_keys

    def bulk_insert(self, files: list, collection_name: str, partition_name: str=None)->int:
        if not self._verify_input(collection_name, partition_name):
            return 0

        id = utility.do_bulk_insert(files=files, collection_name=collection_name, partition_name=partition_name)
        self._print_info("Bulkinsert to milvus, task id: {}, files: {}, ".format(id, files))
        return id


default_milvus = MilvusConnector(address="localhost:19530")

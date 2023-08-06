# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License
# is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
# or implied. See the License for the specific language governing permissions and limitations under
# the License.

import os

from minio import Minio
from minio.error import S3Error
from logging import Logger

from .util import (
    Base,
    default_logger,
)

DEFAULT_BUCKET_NAME = "a-bucket"
DEFAULT_REMOTE_PATH = "milvus_ingestion_data"

class Uploader(Base):
    def __init__(self,
                 address: str,
                 access_key: str,
                 secret_key: str,
                 logger: Logger = default_logger()):
        super().__init__(logger=logger)
        self.address = address
        self.access_key = access_key
        self.secret_key = secret_key

    def upload(self, data_folder: str,
               bucket_name: str=DEFAULT_BUCKET_NAME,
               remote_folder: str=DEFAULT_REMOTE_PATH)->(bool, list):
        if not os.path.exists(data_folder):
            print("Data path '{}' doesn't exist".format(data_folder))
            return False, []

        files = []
        try:
            print("Prepare upload files")
            minio_client = Minio(self.address, access_key=self.access_key, secret_key=self.secret_key, secure=False)
            found = minio_client.bucket_exists(bucket_name)
            if not found:
                print("MinIO bucket '{}' doesn't exist".format(bucket_name))
                return False, []

            def upload_files(folder:str):
                for parent, dirnames, filenames in os.walk(folder):
                    if parent is folder:
                        for filename in filenames:
                            ext = os.path.splitext(filename)
                            if len(ext) != 2 or (ext[1] != ".json" and ext[1] != ".npy"):
                                continue
                            local_full_path = os.path.join(parent, filename)
                            minio_file_path = os.path.join(remote_folder, os.path.basename(folder), filename)
                            minio_client.fput_object(bucket_name, minio_file_path, local_full_path)
                            self._print_info("Upload file '{}' to '{}'".format(local_full_path, minio_file_path))
                            files.append(minio_file_path)
                        for dir in dirnames:
                            upload_files(os.path.join(parent, dir))

            upload_files(data_folder)

        except S3Error as e:
            print("Failed to connect MinIO server {}, error: {}".format(self.address, e))
            return False, []

        self._print_info("Successfully upload files: {}".format(files))
        return True, files


default_uploader = Uploader(address="0.0.0.0:9000", access_key="minioadmin", secret_key="minioadmin")
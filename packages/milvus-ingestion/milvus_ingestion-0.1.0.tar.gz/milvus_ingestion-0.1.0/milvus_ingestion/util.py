# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License
# is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
# or implied. See the License for the specific language governing permissions and limitations under
# the License.

import logging
from logging import Logger

defaultLogger = logging.getLogger()
fmt = '%(asctime)s|%(funcName)s|%(lineno)s|%(levelname)s|%(message)s'
formatter = logging.Formatter(fmt)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
defaultLogger.addHandler(handler)
defaultLogger.setLevel('DEBUG')

def default_logger()->Logger:
    return defaultLogger

class Base:
    def __init__(self, logger: Logger = default_logger()):
        self._logger = logger

    def _print_info(self, msg):
        if self._logger:
            self._logger.info(msg)

    def _print_warn(self, msg):
        if self._logger:
            self._logger.warning(msg)

    def _print_err(self, msg):
        if self._logger:
            self._logger.error(msg)
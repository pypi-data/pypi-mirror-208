# Copyright 2023 Hercules author.
#
# Acknowledgement: The structure of the Module is inspired by incubator-tvm.
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.


from . import _ffi_api

FATAL = 50
ERROR = 40
WARNING = 30
INFO = 20
DEBUG = 10

__LOGGING_LEVELS = [FATAL, ERROR, WARNING, INFO, DEBUG]


def set_cpp_logging_level(logging_level):
    """

    Parameters
    ----------
    logging_level : int
        Set the logging level of CPP

    Returns
    -------

    """
    available_logging_level = ['hercules.FATAL', 'hercules.ERROR', 'hercules.WARNING',
                               'hercules.INFO', 'hercules.DEBUG']
    err_msg = f'logging_level must be one of {available_logging_level}. Got {logging_level}'
    assert logging_level in __LOGGING_LEVELS, err_msg
    _ffi_api.SetLoggingLevel(logging_level)


def get_cpp_logging_level():
    return _ffi_api.GetLoggingLevel()

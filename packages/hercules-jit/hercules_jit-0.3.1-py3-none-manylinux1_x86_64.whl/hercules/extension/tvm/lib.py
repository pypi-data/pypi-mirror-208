# Copyright 2023 Hercules author.
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
import os
import sys
import time
import ctypes
from hercules.env import HERCULES_USER_DIR

_LOAD_HERCULES_TVM = False
_HERCULES_TVM_LIB = None
_TVM_LOADER_STATE = False


def _load_lib():
    global _LOAD_HERCULES_TVM
    global _HERCULES_TVM_LIB
    if _LOAD_HERCULES_TVM:
        return
    from .build import HERCULES_TVM_LIB_NAME
    _HERCULES_TVM_LIB_PATH = os.path.join(HERCULES_USER_DIR, HERCULES_TVM_LIB_NAME)
    curdir = os.getcwd()
    libdir = os.path.abspath(os.path.dirname(__file__))
    os.chdir(libdir)
    try:
        _HERCULES_TVM_LIB = ctypes.CDLL(_HERCULES_TVM_LIB_PATH, ctypes.RTLD_LOCAL)
    finally:
        os.chdir(curdir)
    _LOAD_HERCULES_TVM = True


def compile_or_load_lib(silent=True):
    from hercules import contrib
    from .build import HERCULES_TVM_LIB_NAME
    _HERCULES_TVM_LIB_PATH = os.path.join(HERCULES_USER_DIR, HERCULES_TVM_LIB_NAME)
    try:
        with contrib.util.filelock(_HERCULES_TVM_LIB_PATH, timeout=300):
            try:
                _load_lib()
            except:
                from .build import build_with_cmake
                try:
                    build_with_cmake()
                    _load_lib()
                except:
                    print('[WARNING] hercules tvm extension built failed.',
                          file=sys.stderr)
                    if not silent:
                        raise
    except contrib.util.FileLockTimeout:
        print(
            '\033[91mIt took too much time to wait for compiling tvm extension, please check if there is really a process hold this file \"{}.lock\".\033[0m'.format(
                _HERCULES_TVM_LIB_PATH))
        raise

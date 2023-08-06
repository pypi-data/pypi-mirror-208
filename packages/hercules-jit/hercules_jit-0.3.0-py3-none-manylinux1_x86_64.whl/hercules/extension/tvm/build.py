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
import tempfile

HERCULES_USER_DIR = os.environ.get('HERCULES_USER_DIR', os.path.expanduser('~/.hercules/'))
try:
    os.makedirs(HERCULES_USER_DIR, exist_ok=True)
except:
    print('[WARNING] User directory created failed: ', HERCULES_USER_DIR, file=sys.stderr)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# for installation by pip
HERCULES_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../"))
CMAKE_DIR = os.path.join(HERCULES_DIR, "extension/cpp/tvm")
if not os.path.exists(os.path.join(HERCULES_DIR, 'include')):
    # for development
    HERCULES_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../../../"))
    CMAKE_DIR = os.path.join(HERCULES_DIR, "python/hercules/extension/cpp/tvm")

if sys.platform.startswith('win32'):
    HERCULES_TVM_LIB_NAME = 'libhercules_tvm+tvmruntime.dll'
elif sys.platform.startswith('darwin'):
    HERCULES_TVM_LIB_NAME = 'libhercules_tvm+tvmruntime.dylib'
else:
    HERCULES_TVM_LIB_NAME = 'libhercules_tvm+tvmruntime.so'


def get_tvm_path():
    import tvm
    path = tvm.__file__
    return os.path.abspath(os.path.join(path, "../../.."))


def build_with_cmake():
    tx_module = sys.modules['hercules']
    tx_compile_flags = ' '.join(tx_module.get_cflags())
    tx_link_flags = ' '.join(tx_module.get_link_flags())
    tvm_path = get_tvm_path()
    curdir = os.getcwd()
    build_dir = tempfile.TemporaryDirectory(prefix="hercules_tvm_build")
    print(f"[BUILD DIRECTORY]: {build_dir}")
    os.chdir(build_dir.name)
    print("tx_compile_flags:", tx_compile_flags)
    print("tx_link_flags:", tx_link_flags)
    print("tvm_path:", tvm_path)
    cmake_cmd = f'''
    cmake \
    -DCMAKE_HERCULES_COMPILE_FLAGS="{tx_compile_flags}" \
    -DCMAKE_HERCULES_LINK_FLAGS="{tx_link_flags}" \
    -DTVM_PATH="{tvm_path}" \
    {CMAKE_DIR}
    '''
    try:
        print(cmake_cmd)
        ret = os.system(cmake_cmd)
        assert ret == 0, "Failed to execute with cmake."
        ret = os.system('make -j4')
        assert ret == 0 and os.path.exists(HERCULES_TVM_LIB_NAME), 'no libhercules_tvm is build.'
        os.system('cp {} {}'.format(HERCULES_TVM_LIB_NAME, HERCULES_USER_DIR))
    finally:
        os.chdir(curdir)
        build_dir.cleanup()


if __name__ == "__main__":
    build_with_cmake()

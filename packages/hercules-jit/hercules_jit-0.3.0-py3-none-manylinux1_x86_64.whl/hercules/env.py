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

HERCULES_DEV_MODE = os.environ.get('HERCULES_DEV_MODE', '').lower()
HERCULES_DEV_MODE = HERCULES_DEV_MODE == '1'

HERCULES_INFO_COLLECTION = os.environ.get('HERCULES_INFO_COLLECTION', "1").lower()
HERCULES_INFO_COLLECTION = HERCULES_INFO_COLLECTION == "1"

HERCULES_USER_DIR = os.environ.get('HERCULES_USER_DIR', os.path.expanduser('~/.hercules/'))
try:
    os.makedirs(HERCULES_USER_DIR, exist_ok=True)
except:
    print('[WARNING] User directory created failed: ', HERCULES_USER_DIR, file=sys.stderr)

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

import sys
import os
import ctypes
from . import libinfo
import hashlib


def _load_hvm():
    """Load library by searching possible path."""
    lib_path = libinfo.find_lib_path('hvm')
    print(lib_path)
    lib_pp = os.path.abspath(os.path.dirname(lib_path[0]))
    cwd = os.getcwd()
    try:
        os.chdir(lib_pp)
        print(lib_pp)
        print(lib_path[0])
        lib = ctypes.CDLL("/home/ubuntu/github/gottingen/hvm/lib/libhvm.so", ctypes.RTLD_GLOBAL)
        with open(lib_path[0], 'rb') as lib_f:
            lib_sha1 = hashlib.sha1(lib_f.read()).hexdigest()
        lib.HerculesAPIGetLastError.restype = ctypes.c_char_p
    finally:
        os.chdir(cwd)
    return lib, os.path.basename(lib_path[0]), lib_sha1


_LIB, _LIB_NAME, _LIB_SHA1 = _load_hvm()

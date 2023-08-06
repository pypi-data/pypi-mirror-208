# ******************************************************************************
# Copyright 2020 Brainchip Holdings Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ******************************************************************************
import os
from pathlib import Path
import shutil


def copytree_force(src, dest):
    # Note: we can't use shutil.copytree because the dirs_exist_ok parameter that forces the copy
    # is not available before Python 3.8
    if os.path.isdir(src):
        if not os.path.isdir(dest):
            os.makedirs(dest)
        files = os.listdir(src)
        for f in files:
            copytree_force(os.path.join(src, f),
                           os.path.join(dest, f))
    else:
        shutil.copyfile(src, dest)


def deploy_engine(dest_path):
    # Note: we cannot use importlib.resources because it has incompatible behaviours
    # when dealing with directories between python 3.7/3.8 and 3.9/3.10
    engine_path = os.path.join(Path(__file__).parent, "../engine")
    dest_path = os.path.join(dest_path, "engine")
    copytree_force(engine_path, dest_path)

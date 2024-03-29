# Copyright (c) 2017 Sony Corporation. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

FROM ubuntu-test-stand

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    clang-format \
    cmake \
    gcc \
    make \
    python3 \
    python3-pip \
    && apt-get -yqq clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install -U pip setuptools
RUN pip install -U pyyaml mako autopep8

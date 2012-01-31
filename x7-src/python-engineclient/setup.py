# Copyright 2011 X7, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import setuptools
import sys


requirements = ["httplib2", "prettytable"]
if sys.version_info < (2, 6):
    requirements.append("simplejson")
if sys.version_info < (2, 7):
    requirements.append("argparse")


def read_file(file_name):
    return open(os.path.join(os.path.dirname(__file__), file_name)).read()


setuptools.setup(
    name="python-engineclient",
    version="2012.1",
    author="Rackspace, based on work by Jacob Kaplan-Moss",
    author_email="github@racklabs.com",
    description="Client library for X7 Engine API.",
    long_description=read_file("README.rst"),
    license="Apache License, Version 2.0",
    url="https://github.com/x7/python-engineclient",
    packages=["engineclient", "engineclient.v1_1", "engineclient.v1_1.contrib",
              "engineclient.keystone"],
    install_requires=requirements,
    tests_require=["nose", "mock"],
    test_suite="nose.collector",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python"
    ],
    entry_points={
        "console_scripts": ["engine = engineclient.shell:main"]
    }
)

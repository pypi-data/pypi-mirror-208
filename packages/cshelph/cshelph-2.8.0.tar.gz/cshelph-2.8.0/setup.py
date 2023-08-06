#!/usr/bin/env python
"""
Setup script for C-SHELPh. Use like this for Unix:

$ python setup.py install

"""
#  This file is part of 'C-SHELPh' - Classification of Sub-aquatic Height Extracted Photons
#
#  Copyright 2023 Nathan Thomas
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
#
# Purpose:  Installation of the C-SHELPh software
#
# Author: Nathan Thomas
# Email: nmthomas28@gmail.com
# Date: 05/05/2023
# Version: 2.8.0
#
# History:
# Version 2.7.0

from distutils.core import setup
import os

setup(name='cshelph',
    version='2.8.0',
    description='Classification of Sub-aquatic Height Extracted Photons',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Nathan Thomas and Brian Lee',
    author_email='nmthomas28@gmail.com',
    scripts=['cshelph.py'],
    package_dir={},
    data_files=[],
    license='LICENSE.txt',
    url='https://github.com/nmt28/C-SHELPh',
    classifiers=['Intended Audience :: Developers',
                 'Intended Audience :: Science/Research',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python :: 3'])


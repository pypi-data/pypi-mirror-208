# Copyright (c) 2022, Bamboooz
# All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import os
import shutil

from setuptools import setup


description = 'Compare code execution speeds using timec!'

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'Programming Language :: Python :: 3'
]

keywords = [
    'python', 'library', 'benchmark', 'timec', 'execution', 'speed', 'code'
]

setup(
    name='timec',
    version='0.0.2',
    description=description,
    long_description=open('README.txt').read(),
    url='https://github.com/Bamboooz/timec',
    author='Bamboooz',
    author_email='bambusixmc@gmail.com',
    license='BSD-3-Clause',
    classifiers=classifiers,
    keywords=keywords
)


if __name__ == '__main__':
    # run this file using python setup.py sdist bdist_wheel
    password = input('Enter your pypi password: ')
    os.system(f'twine upload --repository-url https://upload.pypi.org/legacy/ -u Bamboooz -p {password} dist/*')

    # remove pypi build directories
    shutil.rmtree(f'{os.getcwd()}\\build')
    shutil.rmtree(f'{os.getcwd()}\\dist')
    shutil.rmtree(f"{os.getcwd()}\\{[d for d in os.listdir('.') if os.path.isdir(d) and 'egg-info' in d][0]}")

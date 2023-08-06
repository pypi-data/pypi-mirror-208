#!/usr/bin/env python
# Copyright (c) OpenMMLab. All rights reserved.
from setuptools import find_packages, setup

import openxlab.utils as utils
from openxlab.config import version

setup(
    name='openxlab-test',
    version=version.version,
    description='openxlab',
    long_description= utils.get_file_content("README.md"),
    long_description_content_type='text/markdown',
    author='Openxlab Contributors',
    author_email='myname@example.com',
    keywords='openxlab,  xxxx',
    url='https://github.com/xxx/xxxx',
    packages=find_packages(exclude=('configs', 'tools', 'demo')),
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
    ],
    license='Apache License 2.0',
    install_requires=utils.parse_requirements('requirements/runtime.txt'),
    extras_require={
        'tests': utils.parse_requirements('requirements/tests.txt'),
        'build': utils.parse_requirements('requirements/build.txt'),
        'optional': utils.parse_requirements('requirements/optional.txt'),
    },
    entry_points={
        'console_scripts': [
              'openxlab-test = openxlab.cli:main'
          ]
    },
    ext_modules=[],
)

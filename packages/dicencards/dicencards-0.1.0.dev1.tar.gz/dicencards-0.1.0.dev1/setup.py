#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages

__name__ = 'dicencards'
__version__ = '0.1.0.dev1'
__author__ = 'Xavier ROY'
__author_email__ = 'xavier@regbuddy.eu'

project_dir = os.path.dirname(os.path.realpath(__file__))
requirement_file_path = project_dir + '/requirements.txt'
requirements = []
if os.path.isfile(requirement_file_path):
    with open(requirement_file_path) as f:
        requirements = f.read().splitlines()

setup(
    name=__name__,
    version=__version__,
    author=__author__,
    author_email=__author_email__,
    url='https://bitbucket.org/monkeytechnologies/monkey-crawler',
    description='Small API to manage dice rolls and cards draws.',
    long_description=open('README.rst').read(),
    license="Apache License, Version 2.0",

    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,

    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 1 - Planning',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers'
    ]
)

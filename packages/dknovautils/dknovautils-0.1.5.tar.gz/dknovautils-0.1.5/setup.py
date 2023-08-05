#!/usr/bin/env python

import re
import setuptools

from distutils.core import setup
from setuptools import find_packages

DkAppVer = '0.1.5'

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setuptools.setup(
    name="dknovautils",
    version=DkAppVer,
    author="dknova",
    author_email="dknova@example.com",
    description="This is the tools for dknova.",
    long_description=long_description,
    # long_description_content_type="text/markdown",
    url="http://example.com",
    install_requires=[
        # 'requests!=2.9.0',
        # 'lxml',
        # 'monotonic>=1.5',
        'numpy',
        # 'beepy',
    ],
    packages=setuptools.find_packages(exclude=("test")),
    classifiers=(
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",

        "Programming Language :: Python :: 3.7"
    ),
    exclude_package_data={'': ["*.txt", "*.adoc", "*.sh", "dknovautils/test.py",
                               "dknovautils/config.txt", "dknovautils/*.sh", "dknovautils/test*.py"]},
)

#! /usr/bin/env python

import sys
from setuptools import find_packages, setup

if sys.version_info < (3, 8):
    sys.exit("\nERROR: Python versions lower than 3.8 are not supported\n")

setup(
    name="smartgpt",
    version="0.1.2",
    packages=find_packages(),
    scripts=["bin/smartgpt"],
    author_email="kiefl.evan@gmail.com",
    author="Evan Kiefl",
    url="https://github.com/ekiefl/smartgpt",
    install_requires=[
        "openai",
        "attrs",
        "cattrs",
        "pyyaml",
        "prompt_toolkit",
    ],
    include_package_data=True,
    zip_safe=False,
)

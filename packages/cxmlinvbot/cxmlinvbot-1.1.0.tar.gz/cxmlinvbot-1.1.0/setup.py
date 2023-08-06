# coding: utf-8

import sys
from   setuptools import setup, find_packages

from   cxmlinvbot.config.base import BaseConfig

NAME = "cxmlinvbot"
VERSION = BaseConfig.VERSION

# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = ['lxml>=4.9.2',
            'requests>=2.29.0',
            'encrypta>=1.0.0']

setup(
    name=NAME,
    version=VERSION,
    description="Invoice Bot - PO to Invoice in CXML",
    author_email="monkeeferret@gmail.com",
    install_requires=REQUIRES,
    python_requires=">=3.11",
    packages=find_packages(),
) 
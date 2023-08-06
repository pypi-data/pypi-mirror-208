# -*- coding: utf-8 -*-
import os
from glob import glob
from setuptools import setup, find_packages

with open('README.rst', 'r', encoding='utf-8') as file:
    LONG_DESCRIPTION = file.read() 
LONG_DESCRIPTION_CONTENT_TYPE = "text/markdown"

NAME = 'linqex'
VERSION = '1.6'
DESCRIPTION = 'The linq module in C# has been adapted for python with some modifications.'
URL = 'https://github.com/TahsinCr/python-linqex'
AUTHOR = 'TahsinCr'
AUTHOR_EMAIL = 'TahsinCr@outlook.com'
LICENSE = 'MIT'
KEYWORDS = ['linq', 'linqex', 'ex', 'enumerable']
SRC = 'linqex'
PY_REQUIRES = '>=3'
CLASSIFIERS = [
    'Programming Language :: Python :: 3',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent'
]

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type=LONG_DESCRIPTION_CONTENT_TYPE,
    url=URL,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license=LICENSE,
    keywords=KEYWORDS,
    classifiers=CLASSIFIERS,
    python_requires=PY_REQUIRES,
    py_modules=[os.path.splitext(os.path.basename(path))[0] for path in glob('{}/*.py'.format(SRC))],
    packages=find_packages()
)
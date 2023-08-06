import os
from setuptools import setup

MODULE_TITLE = "kurses_py"
MODULE_VERSION = "0.1"
MODULE_DESCRIPTION = """\
This module provides a cross-platform solution for simulating the functionality of the 'conio' and 'curses' libraries. 
It allows users to easily create text-based user interfaces with advanced features such as color and cursor control. 
The module is designed to be easy to use and provides a high level of compatibility with existing code 
that uses 'conio' or 'curses'.
"""
MODULE_DIRECTORY_SAMPLE = "sample"

sample_files = []
for dirpath, dirnames, filenames in os.walk(MODULE_DIRECTORY_SAMPLE):
    for filename in filenames:
        sample_files.append(os.path.join(dirpath, filename))


setup(
    name=MODULE_TITLE,
    version=MODULE_VERSION,
    description=MODULE_DESCRIPTION,

    author='SealtielFreak',
    author_email="sealtielfreak@yandex.com",

    license="LGPL 2.1",

    url="https://github.com/SealtielFreak/kurses.py",
    packages=["kurses"],
    install_requires=[""],
    data_files=[
        ('', ['LICENSE']),
        ('docs', ['requirements.txt']),
        ('sample', sample_files)
    ],
)
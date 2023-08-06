from setuptools import setup, find_packages
import codecs
import os
 

VERSION = '0.0.4'
DESCRIPTION = 'practical exam'

# Setting up
setup(
    name="practicalexam",
    version=VERSION,
    author="AK",
    author_email="<arkenkumar@gmail.com>",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'video', 'stream', 'video stream', 'camera stream', 'sockets']
)
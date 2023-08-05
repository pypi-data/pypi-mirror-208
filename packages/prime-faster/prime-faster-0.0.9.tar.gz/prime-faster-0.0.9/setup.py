# prime-faster - Faster Prime Number Generator
# Author: Takahashi Akari <akaritakahashioss@gmail.com>
# License: MIT License Copyright (c) 2022 Takahashi Akari <akaritakahashioss@gmail.com>
# Version: 0.0.9
# Date: 2022-08-08
# Python: 3.10.6
# Description: prime-faster - Faster Prime Number Generator

import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="prime-faster",
    version="0.0.9",
    author="Takahashi Akari",
    author_email="akaritakahashioss@gmail.com",
    description="prime-faster - Faster Prime Number Generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/takahashi-akari/prime-faster",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

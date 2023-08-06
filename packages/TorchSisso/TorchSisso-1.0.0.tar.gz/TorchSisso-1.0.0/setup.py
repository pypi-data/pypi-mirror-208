#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 17 09:33:17 2023

@author: muthyala.7
"""

import setuptools


setuptools.setup(
    name="TorchSisso",
    version="1.0.0",
    author="Madhav Muthyala",
    author_email="madhavreddymuthyala@gmail.com",
    description="GPU Supported Sure Independence Screening and Sparsifying Operator Package",
    url="https://github.com/MR1319/TorchSisso",
    packages=setuptools.find_packages(),
    install_requires=[
        "torch",
        "pandas",
        "numpy"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name="sphinx_api_sidebar",
    description="Display any generated static API documentation in a sidebar",
    version="0.2.0",
    author="Yiheng Xiong",
    author_email="georgex8866@gmail.com",
    url="https://github.com/Yihengxiong6/sphinx_api_sidebar",
    packages=["sphinx_api_sidebar"],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    install_requires=["sphinx >= 2.1"],
    entry_points={
        "sphinx.extensions": ["sphinx_api_sidebar = sphinx_api_sidebar:setup"]
    },
)

#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name='vicoco',
    version='v0.0.1',
    description='Vivado xsim compatibility',
    author='Kiran Vuksanaj',
    author_email='kiranv@mit.edu',
    package_dir={"":"src"},
    packages=find_packages(where="./src"),
    install_requires=['cocotb==1.9.2']
)

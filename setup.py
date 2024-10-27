"""
    file: setup.py

    This file is used to install the package.
"""

from setuptools import setup, find_packages

setup(
    name="openwaves",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
)

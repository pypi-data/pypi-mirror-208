#!/usr/bin/env python
from sys import exit

from setuptools import find_packages, setup

long_description = u"\n\n".join((open("README.md").read(),))

setup(
    name="pipenv-check",
    version="0.0.8",
    description="View installed pip packages and their update status.",
    long_description=long_description,
    author="3bfab",
    author_email="info@3bfab.com",
    license="MIT",
    url="https://github.com/3bfab/pipenv-check",
    classifiers=[],
    packages=find_packages(),
    package_data={},
    include_package_data=True,
    entry_points={'console_scripts': [
        'pipenv-check = pipenv_check.check:main',
    ]},
    python_requires=">=3.6",
    install_requires=[],
)
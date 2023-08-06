#!/usr/bin/env python
from setuptools import setup
from pathlib import Path
import sys
import os
import re

# require python 3.7 or newer
if sys.version_info < (3, 7):
    print("Error: dbt does not support this version of Python.")
    print("Please upgrade to Python 3.7 or higher.")
    sys.exit(1)

try:
    from setuptools import find_namespace_packages
except ImportError:
    # the user has a downlevel version of setuptools.
    print("Error: dbt requires setuptools v40.1.0 or higher.")
    print('Please upgrade setuptools with "pip install --upgrade setuptools" ' "and try again")
    sys.exit(1)

def _get_plugin_version_dict():
    _version_path = os.path.join(this_directory, "dbt", "adapters", "upsolver", "__version__.py")
    _semver = r"""(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)"""
    _pre = r"""((?P<prekind>a|b|rc)(?P<pre>\d+))?"""
    _version_pattern = rf"""version\s*=\s*["']{_semver}{_pre}["']"""
    with open(_version_path) as f:
        match = re.search(_version_pattern, f.read().strip())
        if match is None:
            raise ValueError(f"invalid version at {_version_path}")
        return match.groupdict()

def _dbt_upsolver_version():
    parts = _get_plugin_version_dict()
    upsolver_version = "{major}.{minor}.{patch}".format(**parts)
    if parts["prekind"] and parts["pre"]:
        upsolver_version += parts["prekind"] + parts["pre"]
    return upsolver_version

this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md")) as f:
    long_description = f.read()

package_name = "dbt-upsolver"
package_version = _dbt_upsolver_version()
description = """The Upsolver adapter plugin for dbt"""
dbt_version = '1.4.5'

setup(
    name=package_name,
    version=package_version,
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    author="Upsolver Team",
    author_email="info@upsolver.com",
    url="https://github.com/tanyshak/dbt-upsolver",
    packages=find_namespace_packages(include=["dbt", "dbt.*"]),
    package_data={
        "dbt": [
            "include/upsolver/dbt_project.yml",
            "include/upsolver/profile_template.yml",
            "include/upsolver/macros/*.sql",
            "include/upsolver/macros/*/*.sql"
        ]
    },
    include_package_data=True,
    install_requires = [
        "dbt-core~=1.4.6",
        "upsolver-sdk-python"
    ],
    zip_safe=False,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
)

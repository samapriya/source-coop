"""
Copyright 2025 Samapriya Roy

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Source Coop download command implementation
"""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="source-coop",
    version="0.1.0",
    author="Samapriya Roy",
    author_email="samapriya.roy@gmail.com",
    description="Unofficial Python SDK & CLI for Source Coop",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/samapriya/source-coop",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    license="Apache-2.0",
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "boto3>=1.17.0",
        "rich>=10.0.0",
        "pandas>=1.0.0",
        "pyarrow>=3.0.0",
        "tqdm>=4.60.0",
        "aiohttp>=3.8.0",
        "aiofiles>=0.7.0",
    ],
    entry_points={
        "console_scripts": [
            "source-coop=source_coop.cli:main",
        ],
    },
)

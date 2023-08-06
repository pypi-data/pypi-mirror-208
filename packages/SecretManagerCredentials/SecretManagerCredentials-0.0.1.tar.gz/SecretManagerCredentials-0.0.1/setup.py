import os
import re

from setuptools import find_packages, setup

ROOT = os.path.dirname(__file__)
MODULE_NAME = "SecretManagerCredentials"


def get_author() -> str:
    author_re = re.compile(r"""__author__ = ['"]([A-Za-z .]+)['"]""")
    init = open(os.path.join(ROOT, MODULE_NAME, "__init__.py")).read()
    return author_re.search(init).group(1)


def get_version() -> str:
    version_re = re.compile(r"""__version__ = ['"]([0-9.]+)['"]""")
    init = open(os.path.join(ROOT, MODULE_NAME, "__init__.py")).read()
    return version_re.search(init).group(1)


def get_description() -> str:
    with open(os.path.join(ROOT, "README.md"), encoding="utf-8") as f:
        description = f.read()
    return description


dependencies_list = [
    "hvac==0.11.2",
    "boto3==1.18.63",
    "botocore==1.21.65"
]

setup(
    name=MODULE_NAME,
    packages=find_packages(),
    version=get_version(),
    license="MIT",
    description="Convenient wrapper for executing codes on AWS for connecting and fetching credentials from vault",
    long_description=get_description(),
    long_description_content_type="text/markdown",
    author=get_author(),
    url="",
    download_url="",
    keywords=["Vault Credential Fetch", "Credential Fetch", "Vault"],
    install_requires=dependencies_list,
    setup_requires=dependencies_list,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
    ],
)

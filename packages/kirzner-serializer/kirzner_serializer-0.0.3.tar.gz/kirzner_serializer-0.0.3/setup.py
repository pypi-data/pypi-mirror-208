from setuptools import setup, find_packages

from codecs import open
from os import path

HERE = path.abspath(path.dirname(__file__))

with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="kirzner_serializer",
    version="0.0.3",
    description="Module for json and xml serialization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Nastya Kirzner",
    author_email="kirznernasta@gmail.com",
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent"
    ],
    packages=["kirznerSerializer"],
    include_package_data=True,
    install_requires=["regex"]
)
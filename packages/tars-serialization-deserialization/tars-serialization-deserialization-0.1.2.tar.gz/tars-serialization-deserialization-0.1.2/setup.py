from setuptools import setup, find_packages

from codecs import open
from os import path

HERE = path.abspath(path.dirname(__file__))

with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="tars-serialization-deserialization",
    version="0.1.2",
    description="library for python serialization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ACC-Stas/Python-Labs",
    author="Tarasenko Fyodor",
    author_email="tarasenkafiodar@gmail.com",
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent"
    ],
    packages=find_packages(),
    include_package_data=True
)

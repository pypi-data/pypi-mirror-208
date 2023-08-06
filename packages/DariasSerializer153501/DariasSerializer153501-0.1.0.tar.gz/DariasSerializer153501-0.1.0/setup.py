# Always prefer setuptools over distutils
from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open
from os import path

# The directory containing this file
HERE = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name="DariasSerializer153501",
    version="0.1.0",
    description="Demo library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://dariasserializer153501.readthedocs.io/",
    author="Shevtsova Daria",
    author_email="dashulianorton@gmail.com",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent"
    ],
    packages=["DariasSerializer153501"],
    include_package_data=True,
    install_requires=["regex"]
)
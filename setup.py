# See LICENSE.incore.incore for details
"""The setup script."""
import codecs
from setuptools import setup, find_packages
import os

# Base directory of package
here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with codecs.open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()


def read_requires():
    with open(os.path.join(here, "uatg/requirements.txt"),
              "r") as reqfile:
        return reqfile.read().splitlines()


# Long Description
with open("README.rst", "r") as fh:
    readme = fh.read()

setup_requirements = []

test_requirements = []

setup(
    name='uatg',
    version='1.14.0',
    description="UATG - Micro-Architecture (µArch) Tests Generator",
    long_description=readme + '\n\n',
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: BSD License",
        "Development Status :: 3 - Alpha"
    ],
    url='https://github.com/incoresemi/uatg',
    author="InCore Semiconductors Pvt. Ltd.",
    author_email='neelgala@incoresemi.com',
    license="BSD-3-Clause",
    packages=find_packages(),
    package_dir={'uatg': 'uatg'},
    package_data={'uatg': ['requirements.txt', 'target/*', 'env/*']},
    install_requires=read_requires(),
    python_requires='>=3.7.0',
    entry_points={
        'console_scripts': ['uatg=uatg.main:cli'],
    },
    include_package_data=True,
    keywords='uatg',
    test_suite='tests',
    tests_require=test_requirements,
    zip_safe=False,
)

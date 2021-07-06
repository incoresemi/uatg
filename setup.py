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
    with open(os.path.join(here, "micro-arch-tests/requirements.txt"),
              "r") as reqfile:
        return reqfile.read().splitlines()


# Long Description
with open("README.rst", "r") as fh:
    readme = fh.read()

setup_requirements = []

test_requirements = []

setup(
    name='micro-arch-tests',
    version='dev-0.0.1',
    description="RISC-V micro-architectural tests generator",
    long_description=readme + '\n\n',
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: BSD License",
        "Development Status :: 2 - Pre-Alpha"
    ],
    url='https://gitlab.com/incoresemi/micro-arch-tests/-/tree/dev-0.0.1',
    author="InCore Semiconductors Pvt. Ltd.",
    author_email='incorebot@gmail.com',
    license="BSD-3-Clause",
    packages=find_packages(),
    package_dir={'micro-arch-tests': 'micro-arch-tests'},
    package_data={'micro-arch-tests': ['requirements.txt', 'target/*', 'env/*']},
    install_requires=read_requires(),
    python_requires='>=3.6.0',
    #TODO: define entry points.
    #entry_points={
    #    'console_scripts': ['riscv_ctg=riscv_ctg.main:cli',],
    #},
    include_package_data=True,
    keywords='micro-arch-tests',
    test_suite='tests',
    tests_require=test_requirements,
    zip_safe=False,
)
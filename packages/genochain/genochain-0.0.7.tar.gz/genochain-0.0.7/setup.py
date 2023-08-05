
from setuptools import setup, find_packages
import codecs
import os


VERSION = '0.0.7'
DESCRIPTION = 'Storing and versioning genomics data on a blockchain'
LONG_DESCRIPTION = 'The provided code is a Python implementation of a simple blockchain. It allows for the creation of a genesis block with a given FASTA sequence, addition of new blocks with a given FASTA sequence and associated ID, and versioning of FASTA sequences. The blockchain can also be checked and printed. This code is licensed under the MIT License.'

# Setting up
setup(
    name="genochain",
    version=VERSION,
    author="GenoChain(Sanjana Sharma)",
    author_email="<sharmasanjana1947@gmail.com>",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    keywords=['python' , 'blockchain' , 'genomics' , 'fasta', 'block', 'biology'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)

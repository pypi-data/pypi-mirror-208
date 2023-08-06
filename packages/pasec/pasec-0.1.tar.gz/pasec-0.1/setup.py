from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.1'
DESCRIPTION = 'A password generator using passphrase'
LONG_DESCRIPTION = 'A package that allows user to generate password from given passphrase .'

# Setting up
setup(
    name="pasec",
    version='0.1',
    author="ssuroj",
    keywords=['python', 'password', 'pasec'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
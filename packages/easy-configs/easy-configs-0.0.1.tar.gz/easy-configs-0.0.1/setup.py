from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

VERSION = '0.0.1'
DESCRIPTION = 'A python package to make configs easier!'
LONG_DESCRIPTION = 'A package that allows to read and write to configs.'

setup(
    name="easy-configs",
    version=VERSION,
    author="tntgamer685347",
    author_email="gamer@fampl.de",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
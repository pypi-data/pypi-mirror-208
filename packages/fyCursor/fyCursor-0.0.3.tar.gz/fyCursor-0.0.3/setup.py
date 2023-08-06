# usage: python3 setup.py sdist bdist_wheel
from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    LONG_DESCRIPTION = "\n" + fh.read()

from fyCursor import Info
self = Info()

# Setting up
setup(
    name=self.__title__,
    version=self.__version__,
    description=self.__version__,
    author=self.__author__,
    author_email=self.__author_email__,
    license=self.__license__,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    keywords=['python', 'sqlite3', 'database'],
)

#!/usr/bin/env python
#from distutils.core import setup
from setuptools import setup, find_packages

setup(name="clientend",
      version="1.0.0",
      description="Library for OAuth version 1.0a.",
      author="Garrett Bjerkhoel",
      author_email="garrett@clientend.com",
      url="http://github.com/clientend/clientend-python",
      packages = find_packages(),
      install_requires = ['httplib2'],
      license = "MIT License",
      keywords="clientend",
      zip_safe = True,
      tests_require=['nose', 'coverage', 'mox'])
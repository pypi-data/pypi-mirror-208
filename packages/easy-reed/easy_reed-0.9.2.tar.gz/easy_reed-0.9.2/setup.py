#!/usr/bin/env python
from setuptools import setup, find_packages
from pathlib import Path

this_dir = Path(__file__).parent
long_description = (this_dir / "README.md").read_text()

setup_info = dict(
  name='easy_reed',
  python_requires=">=3.7",
  version='0.9.2',
  description='Config Library for cross module configuration',
  long_description=long_description,
  long_description_content_type="text/markdown",
  author="Reed Schick",
  author_email='rns350@nyu.edu',
  url='https://github.com/rns350/easy-reed',
  packages=find_packages(
    where='.', 
    include=['easy_reed*']
  ),
  install_requires=[],
  setup_requires=[],
  tests_require=['pytest']
)

setup(**setup_info)
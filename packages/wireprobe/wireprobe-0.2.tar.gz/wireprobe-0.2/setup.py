#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='wireprobe',
      version='0.2',
      description='A wireguard app',
      long_description="This package monitor wireguard client's tunnel if is up or down",
      author='Benjamin Gounine',
      author_email='prunus@ecuri.es',
      url='https://github.com/OpenPrunus/wireprobe/',
      python_requires='>3.9',
      install_requires=["decorator", "fabric", "invoke", "pyyaml", "urllib3"],
      packages=find_packages(),
      package_dir={"wireprobe": "wireprobe"},
      package_data={'wireprobe': ['settings.yml.example']},
      include_package_data=True,
      )

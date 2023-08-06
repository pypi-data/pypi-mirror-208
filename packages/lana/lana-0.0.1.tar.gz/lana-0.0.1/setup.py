#!/usr/bin/env python

import os
from setuptools import setup
from setuptools.extension import Extension

directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='lana',
      version='0.0.1',
      description='Linear Algebra Laboratory',
      author='Marco Salvalaggio',
      author_email='mar.salvalaggio@gmail.com',
      license='MIT',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/marcosalvalaggio/kiwigrad',
      packages = ['lana'],
      ext_modules = [Extension('lana.engine', sources = ['lana/engine.c'])],
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ],
      python_requires='>=3.6',
)

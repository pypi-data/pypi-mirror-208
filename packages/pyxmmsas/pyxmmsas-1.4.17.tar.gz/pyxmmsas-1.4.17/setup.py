#!/usr/bin/env python
from __future__ import absolute_import, division, print_function

from builtins import (bytes, str, open, super, range,
                      zip, round, input, int, pow, object, map, zip)

__author__ = 'Carlo Ferrigno'

from setuptools import setup, find_packages

#
#packs=find_packages()
#print ('packs',packs)
#

include_package_data = True

setup(name='pyxmmsas',
      scripts=[],
      version="1.4.17",
      description='It is wrapper for SAS and performs spectral analysis and plots',
      author='Carlo Ferrigno',
      author_email='carlo.ferrigno@unige.ch',
      packages=['pyxmmsas'],
      install_requires=["astropy!=3.0.*,!=3.1,!=3.1.1,>=2.0.12",
                        "numpy",
                        "astroquery",
                        "matplotlib",
                        "scipy",
                        "photutils",
                        "optimalgrouping>=1.0.3",
                        "adaptivelcbin",
                        "cython",
                        "ultranest",
                        "bxa>=4.0.5"
                    ],
      url="https://gitlab.astro.unige.ch/ferrigno/pysas",
      python_requires='>=3.0',
      license='MIT'
      )

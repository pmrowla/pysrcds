#!/usr/bin/env python

import os
from distutils.core import setup

def read(fname):
        return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='pysrcds',
      version='0.0.1.alpha',
      description='Python library for interacting with Source engine dedicated'
                  ' servers',
      long_description=read('README.rst'),
      author='Peter Rowlands',
      author_email='peter@pmrowla.com',
      url='https://github.com/pmrowla/pysrcds',
      packages=['srcds', 'srcds/events'],
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python',
          'Topic :: Games/Entertainment :: First Person Shooters',
          'Topic :: Software Development :: Libraries :: Python Modules',
     ]
    )

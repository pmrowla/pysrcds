#!/usr/bin/env python

from distutils.core import setup

setup(name='pysrcds',
      version='0.0.0',
      description='Python library for interacting with Source engine dedicated'
                  ' servers',
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

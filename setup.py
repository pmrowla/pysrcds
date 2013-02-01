#!/usr/bin/env python

import os
from distutils.core import setup

def read(fname):
        return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='pysrcds',
      version='0.1.2',
      description='Python library for interacting with Source engine dedicated'
                  ' servers',
      author='Peter Rowlands',
      author_email='peter@pmrowla.com',
      url='https://github.com/pmrowla/pysrcds',
      packages=['srcds', 'srcds/events'],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python',
          'Topic :: Games/Entertainment :: First Person Shooters',
          'Topic :: Software Development :: Libraries :: Python Modules',
     ],
     long_description=\
'''
=======
pysrcds
=======

Python library for interacting with Source engine dedicated servers.

pysrcds provides the functionality to communicate with a dedicated server via
RCON and also provides the ability to parse Source engine logs. There are also
some utility classes that may be useful for developing other Source related
functionality.

License
=======

pysrcds is distributed under the MIT license.
''',
    )

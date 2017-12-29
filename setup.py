#!/usr/bin/env python

from setuptools import setup

setup(
    name='pysrcds',
    version='0.1.5',
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
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=['future'],
    long_description='''
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

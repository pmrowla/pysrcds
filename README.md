pysrcds
=======

Python library for interacting with Source engine dedicated servers.

[![Build Status](https://travis-ci.org/pmrowla/pysrcds.svg?branch=master)](https://travis-ci.org/pmrowla/pysrcds)
[![Coverage Status](https://coveralls.io/repos/github/pmrowla/pysrcds/badge.svg?branch=master)](https://coveralls.io/github/pmrowla/pysrcds?branch=master)
[![PyPI version](https://badge.fury.io/py/pysrcds.svg)](https://pypi.python.org/pypi/pysrcds/)

pysrcds provides the functionality to communicate with a dedicated server via
RCON and also provides the ability to parse Source engine logs. There are also
some utility classes that may be useful for developing other Source related
functionality.

Python 2.7 and Python 3.5+ are supported.

Installation
------------

```
pip install pysrcds
```


HL Log Parsing
--------------

For a log parsing example see [goonpug-trueskill](https://github.com/goonpug/goonpug-trueskill).

RCON Usage
----------

```python
from srcds.rcon import RconConnection

conn = RconConnection('127.0.0.1', port=27015, password='password')
conn.exec_command('status')

# For servers that do not support multipart RCON responses like factorio,
# enable the single_packet_mode option
factorio_conn = RconConnection('127.0.0.1', single_packet_mode=True)
```

License
-------

pysrcds is distributed under the MIT license. See
[LICENSE.md](https://github.com/pmrowla/pysrcds/blob/master/LICENSE.md)
for more information.

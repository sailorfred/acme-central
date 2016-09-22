#!/usr/bin/env python

# Figure out where the openssl.cnf is, and spew it, plus a SAN section
# that has DNS:domain1,DNS:domain2... when the parameter is domain1,domain2...

import sys

try: # Mac
    with open('/System/Library/OpenSSL/openssl.cnf', 'rb') as oc:
        print(oc.read())
except Exception: # Linux
    with open('/etc/ssl/openssl.cnf', 'rb') as oc:
        print(oc.read())
print('[SAN]')
print('subjectAltName=' +
      ','.join(['DNS:' + d for d in sys.argv[1].split(',')]))

#!/usr/bin/env python

import json
import os
import re
import sys
try:
    from urllib.request import urlopen, HTTPError
except:
    from urllib2 import urlopen, HTTPError # Python 2

from send_request import send_request, b64_no_eqs

account, csr_file = sys.argv[1:]

with open(csr_file, 'rb') as cf:
    csr = cf.read()

# Get cert and reference to issuer cert
res_json, links = send_request(
    account,
    'new-cert',
    json.dumps({
            'resource': 'new-cert',
            'csr': b64_no_eqs(csr)}),
    return_headers='Link')
print(res_json)
assert len(links) == 1, 'Missing link to CA cert'
m = re.match('<([^>]+)>;rel="up"$', links[0])
ca_cert = urlopen(m.group(1)).read()
with open(os.path.join(account, 'acme_ca.crt.der'), 'wb') as caf:
    caf.write(ca_cert)

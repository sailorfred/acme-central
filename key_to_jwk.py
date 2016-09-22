#!/usr/bin/env python

from __future__ import print_function

import base64
from binascii import unhexlify
import hashlib
import json
from pprint import pprint
import re
import sys

key = sys.stdin.read()

def _b64(b):
    return base64.urlsafe_b64encode(b).decode('utf8').replace("=", "")

# Thanks to acme_tiny

pub_hex, pub_exp = re.search(
    r"modulus:\n\s+00:([a-f0-9\:\s]+?)\npublicExponent: ([0-9]+)",
    key.decode('utf8'), re.MULTILINE|re.DOTALL).groups()
pub_exp = "{0:x}".format(int(pub_exp))
pub_exp = "0{0}".format(pub_exp) if len(pub_exp) % 2 else pub_exp

header = {
    'alg': 'RS256',
    'jwk': {
        'e': _b64(unhexlify(pub_exp.encode('utf-8'))),
        'kty': 'RSA',
        'n': _b64(unhexlify(re.sub(r'(\s|:)', '', pub_hex).encode('utf-8')))}}
accountkey_json = json.dumps(header['jwk'], sort_keys=True, separators=(',', ':'))
thumbprint = _b64(hashlib.sha256(accountkey_json.encode('utf8')).digest())

sys.stdout.write('header = '.encode('utf-8'))
pprint(header, indent=4)
print("\nthumbprint = '{}'".format(thumbprint))

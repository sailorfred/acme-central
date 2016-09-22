#!/usr/bin/env python

from __future__ import print_function

from base64 import urlsafe_b64encode
from binascii import unhexlify
import copy
from hashlib import sha256
from importlib import import_module
import json
import os
import re
import subprocess
from sys import argv, stderr
try:
    from urllib.request import urlopen, HTTPError
except:
    from urllib2 import urlopen, HTTPError # Python 2

def b64_no_eqs(s):
    return urlsafe_b64encode(s).decode('utf-8').replace('=', '').encode('utf-8')

def send_request(account, url, payload, return_headers=None):
    account_jwk = import_module(account + '.account_jwk')

    dir_url = 'https://{}/directory'.format(os.environ['LE_SERVER'])
    dir_obj = urlopen(dir_url)
    dir_json = dir_obj.read()
    nonce = dir_obj.headers['replay-nonce']
    directory = json.loads(dir_json)

    if url in directory: # new-reg or new-cert
        url = directory[url]

    payload_b64 = b64_no_eqs(payload)
    protected = copy.deepcopy(account_jwk.header)
    protected['nonce'] = nonce
    protected_b64 = b64_no_eqs(json.dumps(protected).encode('utf-8'))
    accountkey_json = json.dumps(account_jwk.header['jwk'],
                                 sort_keys=True, separators=(',', ':'))
    # Sign the request
    p = subprocess.Popen(
        ['openssl', 'dgst', '-sha256', '-sign', account + '/account.key'],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate(
        '{}.{}'.format(
            protected_b64,
            payload_b64).encode('utf-8'))
    assert p.returncode == 0, 'Openssl error during digest: {}'.format(err)
    data = json.dumps({
            'header': account_jwk.header,
            'protected': protected_b64,
            'payload': payload_b64,
            'signature': b64_no_eqs(out)})
    try:
        r = urlopen(url, data.encode('utf-8'))
        if return_headers:
            return r.read(), r.headers.getheaders(return_headers)
        else:
            return r.read()
    except HTTPError as e:
        if e.code == 409:
            print('Already registered', file=stderr)
        else:
            print('{}: {}'.format(e.__str__, e.read()))
            raise

if __name__ == "__main__": # pragma: no cover
    print(send_request(*argv[1:]))

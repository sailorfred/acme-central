#!/usr/bin/env python

from base64 import urlsafe_b64encode
import json
import os
import urllib2

# TODO refactor
def jwt_b64(s):
    return urlsafe_b64encode(s).replace('=','')

dir_url = 'https://{}/directory'.format(os.environ['LE_SERVER'])
dir_obj = urllib2.urlopen(dir_url)
dir_json = dir_obj.read()
nonce = dir_obj.headers['replay-nonce']
dir = json.loads(dir_json)
reg_url = dir['new-reg']

with open(os.environ['ACCOUNT'] + '/reg.email') as f:
    email = f.read().strip()
reg = {
    'resource': 'new-reg',
    'contact': [
        ':'.join(('mailto', email))]}
b64_reg = jwt_b64(json.dumps(reg))
print(reg)
print(b64_reg)


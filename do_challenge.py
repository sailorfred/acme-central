#!/usr/bin/env python

from importlib import import_module
import json
import os
import re
import subprocess
import sys
import time

account_jwk = import_module(sys.argv[1] + '.account_jwk')
from send_request import send_request

def push_key_auth(account, domain, challenge):
    token = re.sub(r"[^A-Za-z0-9_\-]", "_", challenge['token'])
    key_auth = '.'.join((token, account_jwk.thumbprint))
    with open(os.path.join(account, token), 'wb') as tf:
        tf.write(key_auth)
    # Use make to push the token file
    # TODO make DOMAIN=example.com TOKEN=MD...ac push
    # If $DOMAIN/Makefile exists, cd there before make
    if os.path.isfile(os.path.join(account, 'Makefile')):
        make_extra = ''
    else:
        make_extra = '-f ../Makefile'
    if os.environ.get('WELL_KNOWN_DIR', False):
        make_extra += ' WELL_KNOWN_DIR=' + os.environ['WELL_KNOWN_DIR']
    retcode = subprocess.call(
        'cd {account} && make {make_extra} DOMAIN={domain} FILE={file} '
        'push_challenge'.format(
            account=account, make_extra=make_extra, domain=domain, file=token),
        shell=True)
    assert retcode == 0, 'Failed to push challenge token to {}'.format(domain)

    return key_auth

def main(account, domain, challenge_file, result_file):
    with open(challenge_file, 'rb') as cf:
        challenge_data = json.loads(cf.read())
        found_challenge = False
        for c in challenge_data['combinations']:
            if len(c) == 1:
                challenge = challenge_data['challenges'][c[0]]
                if challenge['type'] == 'http-01':
                    found_challenge = True
                    break
    assert found_challenge, "Can't find http-01 challenge for {} in {}".format(
        domain, challenge_file)
    if challenge['status'] == 'valid':
        with open(result_file, "wb") as rf:
            rf.write(json.dumps(challenge))
        sys.exit(0)
    elif challenge['status'] == 'invalid':
        print('\n\n**** Invalid challenge ****\nRemove the challenge file\n\n')
        assert False, 'Invalid challenge for {} in {}'.format(
            domain, 'challenge_file')
    elif challenge['status'] == 'pending':
        key_auth = push_key_auth(account, domain, challenge)
        while True:
            res_json = send_request(account, challenge['uri'], json.dumps({
                        'resource': 'challenge',
                        'keyAuthorization': key_auth}))
            res = json.loads(res_json)
            if res['status'] == 'valid':
                print('Challenge succeeded!')
                with open(result_file, 'wb') as rf:
                    rf.write(res_json)
                break
            elif res['status'] == 'pending':
                sys.stdout.write('.')
                time.sleep(2)
            else:
                raise ValueError('Unexpected "{}" status during challenge validation for {}'.format(
                        res['status'], domain))
    else:
        assert False, 'Unknown challenge status for {} in {}: {}'.format(
            domain, challenge_file, challenge['status'])

if __name__ == "__main__": # pragma: no cover
    main(*sys.argv[1:])

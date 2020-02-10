#!/usr/bin/env python3

import base64
import binascii
import functools
import glob
import hashlib
import json
import os
import re
import zipfile

def gen_hashes(f):
    sha1 = hashlib.sha1()
    sha256 = hashlib.sha256()
    sha512 = hashlib.sha512()
    with open(f, 'rb') as fp:
        for chunk in iter(functools.partial(fp.read, 8192), b''):
            sha1.update(chunk)
            sha256.update(chunk)
            sha512.update(chunk)
    return (binascii.hexlify(sha1.digest()).decode(),
            binascii.hexlify(sha256.digest()).decode(),
            binascii.hexlify(sha512.digest()).decode())


checksums_file = os.path.join(os.path.dirname(__file__), 'checksums.json')
if os.path.exists(checksums_file):
    with open(checksums_file) as fp:
        checksums = json.load(fp)
else:
    checksums = dict()

VERSION_REGEX = re.compile(b'.*(?:Platform)\.Version\s*=\s*(.*?)\n', re.DOTALL)
REVISION_REGEX = re.compile(b'.*Pkg\.Revision\s*=\s*(.*?)\n', re.DOTALL)

for f in sorted(glob.glob(os.path.join(os.getenv('HOME'), '.cache', 'fdroidserver', '*.zip'))):
    basename = os.path.basename(f)
    if os.path.isdir(f) or basename.startswith('gradle-'):
        continue
    url = 'https://dl.google.com/android/repository/' + basename
    print(url)
    if url not in checksums:
        checksums[url] = []
    sha1, sha256, sha512 = gen_hashes(f)
    found = False
    d = None
    for entry in checksums[url]:
        if sha256 and entry.get('sha256') == sha256:
            d = entry
            d['sha1'] = sha1
            d['sha512'] = sha512
            found = True
            break
    if not found:
        d = {
            'sha1': sha1,
            'sha256': sha256,
            'sha512': sha512,
        }
        checksums[url].append(d)
        
    with zipfile.ZipFile(f) as zfp:
        for name in zfp.namelist():
            segments = name.split('/')
            for filename in ('source.properties', 'build.prop',
                             'sdk.properties', 'runtime.properties'):
                if len(segments) == 2 and segments[1] == filename:
                    with zfp.open(name) as fp:
                        d[filename] = fp.read().decode()

    with open(checksums_file, 'w') as fp:
        json.dump(checksums, fp, indent=2, sort_keys=True)

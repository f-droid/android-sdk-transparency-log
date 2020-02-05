#!/usr/bin/python3

import glob
import json
import os
import re
from urllib.parse import urlparse, urlunsplit


checksums_file = os.path.join(os.path.dirname(__file__), 'checksums.json')
if os.path.exists(checksums_file):
    with open(checksums_file) as fp:
        checksums = json.load(fp)
else:
    checksums = dict()

with open(glob.glob('/tmp/fdroidserver/makebuildserver*')[0]) as fp:
    data = fp.read().replace(
        'https://verification.f-droid.org/build-metadata/96ddff1a5034fcc4340f2d482635eeaccaa6707b6b0f82d26d1435476a2f52e5/',
        'https://dl.google.com/android/repository/')
for m in re.finditer(r'''['"](https?://[^'"]+/android/*[^'"]+)['"],\s*['"]([0-9a-f]+)['"]''', data, re.DOTALL):
    path = urlparse(m.group(1)).path.replace('/android/ndk/', '/android/repository/')\
        .replace('/build-metadata/96ddff1a5034fcc4340f2d482635eeaccaa6707b6b0f82d26d1435476a2f52e5/',
                 '/android/repository/')
    url = urlunsplit(('https', 'dl.google.com', path, '', ''))
    sha256 = m.group(2)
    if url not in checksums:
        checksums[url] = []
    add_sha256 = True
    for entry in checksums[url]:
        if sha256 and entry.get('sha256') == sha256:
            add_sha256 = False
            break
    if add_sha256:
        checksums[url].append({'sha256': sha256})

with open(checksums_file, 'w') as fp:
    json.dump(checksums, fp, indent=2, sort_keys=True)

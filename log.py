#!/usr/bin/env python3

import binascii
import hashlib
import io
import json
import os
import re
import requests
import sys
import time
import zipfile
from bs4 import BeautifulSoup


def process_url(status_codes, url, checksum_type, checksum):
    sha1_hasher = hashlib.sha1()
    sha256_hasher = hashlib.sha256()
    sha512_hasher = hashlib.sha512()
    r = requests.get(url, stream=True)
    status_codes.append([url, r.status_code])
    if r.status_code != 200:
        return
    d = None
    with io.BytesIO() as urlfp:
        for chunk in r.iter_content(chunk_size=8192):
            urlfp.write(chunk)
            urlfp.flush()
            if chunk:  # filter out keep-alive new chunks
                sha1_hasher.update(chunk)
                sha256_hasher.update(chunk)
                sha512_hasher.update(chunk)
        d = {
            'sha1': binascii.hexlify(sha1_hasher.digest()).decode(),
            'sha256': binascii.hexlify(sha256_hasher.digest()).decode(),
            'sha512': binascii.hexlify(sha512_hasher.digest()).decode(),
        }
        with zipfile.ZipFile(urlfp) as zfp:
            for name in zfp.namelist():
                segments = name.split('/')
                for filename in ('source.properties', 'build.prop',
                                 'sdk.properties', 'runtime.properties'):
                    if len(segments) == 2 and segments[1] == filename:
                        with zfp.open(name) as fp:
                            d[filename] = fp.read().decode()
        for entry in checksums.get(url, []):
            for t in ('sha1', 'sha256', 'sha512'):
                if entry.get(t) == d.get(t):
                    for k, v in d.items():
                        entry[k] = v
                    return  # alread filled in existing, no need append to list
    return d


def check_file(url, checksum_type, checksum):
    print(url, checksum_type, checksum)
    if url not in checksums:
        checksums[url] = []
    found = False
    d = None
    for entry in checksums[url]:
        if checksum and entry.get(checksum_type) == checksum:
            found = True
            d = entry
            break
    if not found:
        d = process_url(status_codes, url, checksum_type, checksum)
        if d:
            checksums[url].append(d)


def write_status_codes(l):
    write_json(sorted(status_codes), 'status_codes.json')


def write_json(l, f):
    with open(f, 'w') as fp:
        json.dump(l, fp, indent=2, sort_keys=True)


def write_repository_xml(url):
    while True:
        try:
            r = requests.get(url)
            break
        except Exception as e:
            print(url, 'retry', e)
            time.sleep(60)
    status_codes.append([url, r.status_code])
    write_status_codes(status_codes)
    if r.status_code == 200:
        with open(url.replace('https://dl.google.com/', ''), 'w') as fp:
            fp.write(r.text)
    return r.status_code


status_codes = []

BASE_URL = 'https://dl.google.com/android/repository/'
URLS = [
    'https://dl.google.com/android/repository/addon-6.xml',
    'https://dl.google.com/android/repository/addon.xml',
    'https://dl.google.com/android/repository/repository-10.xml',
    'https://dl.google.com/android/repository/sys-img/android/sys-img.xml',
    'https://dl.google.com/android/repository/sys-img/x86/addon-x86.xml',
]
for url in URLS:
    write_repository_xml(url)

VERSIONED_URLS = (
    'https://dl.google.com/android/repository/addon2-%s.xml',
    'https://dl.google.com/android/repository/addons_list-%s.xml',
    'https://dl.google.com/android/repository/repository-1%s.xml',
    'https://dl.google.com/android/repository/repository2-%s.xml',
    'https://dl.google.com/android/repository/sys-img/android/sys-img2-%s.xml',
)
for vu in VERSIONED_URLS:
    for i in range(1, 10):
        if write_repository_xml(vu % i) == 404:
            break

checksums_file = os.path.join(os.path.dirname(__file__), 'checksums.json')
if os.path.exists(checksums_file):
    with open(checksums_file) as fp:
        checksums = json.load(fp)
else:
    checksums = dict()

with open('android/repository/addon.xml') as fp:
    soup = BeautifulSoup(fp.read(), "xml")
    for archive in soup.find_all('archive'):
        filename = archive.url.string
        if filename.startswith('android_m2repository_r'):
            check_file(
                BASE_URL + filename,
                archive.checksum['type'].lower().strip(),
                archive.checksum.string.lower().strip(),
            )

with open('android/repository/repository-12.xml') as fp:
    soup = BeautifulSoup(fp.read(), "xml")
    for archive in soup.find_all('archive'):
        host_os = archive.find('host-os')
        host_bits = archive.find('host-bits')
        if (
            host_os
            and host_os.string == 'linux'
            and (not host_bits or host_bits.string == '64')
        ):
            check_file(
                BASE_URL + archive.url.string,
                archive.checksum['type'].lower().strip(),
                archive.checksum.string.lower().strip(),
            )

with open('android/repository/repository2-1.xml') as fp:
    soup = BeautifulSoup(fp.read(), "xml")
    for archive in soup.find_all('archive'):
        host_os = archive.find('host-os')
        host_bits = archive.find('host-bits')
        if (
            host_os
            and host_os.string == 'linux'
            and (not host_bits or host_bits.string == '64')
        ):
            check_file(
                BASE_URL + archive.url.string,
                'sha1',
                archive.checksum.string.lower().strip(),
            )

with open('checksums.json', 'w') as fp:
    json.dump(checksums, fp, indent=2, sort_keys=True)

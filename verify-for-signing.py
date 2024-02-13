#!/usr/bin/env python3
#
# download and verify any new entries since this repo was last signed

import deepdiff
import hashlib
import io
import json
import os
import re
import requests
import subprocess
import sys
import tempfile
from colorama import Fore, Style


def verify_url(url, sha256):
    print(url)
    sha256_hasher = hashlib.sha256()
    r = requests.get(url, stream=True)
    r.raise_for_status()
    with io.BytesIO() as urlfp:
        i = 0
        for chunk in r.iter_content(chunk_size=65536):
            if i % 10 == 0:
                print('.', end='', flush=True)
            i += 1
            urlfp.write(chunk)
            urlfp.flush()
            if chunk:  # filter out keep-alive new chunks
                sha256_hasher.update(chunk)
        print()
        if sha256 != sha256_hasher.hexdigest():
            print(
                Fore.RED
                + "ERROR: %s must have a SHA-256 of %s!" % (url, sha256)
                + Style.RESET_ALL
            )
            urlfp.seek(0)
            with open(os.path.basename(url), 'wb') as fp:
                fp.write(urlfp.read())
            return False
    return True


with open("checksums.json") as fp:
    current = json.load(fp)
with open("signed/checksums.json") as fp:
    signed = json.load(fp)

# Ensure that only valid entries are being added.  Nothing should be
# changed or removed:
#
# dictionary_item_added: if a new package is found, e.g. a new URL
# iterable_item_added: if a new entry is added to an existing URL
diff = json.loads(deepdiff.DeepDiff(signed, current).to_json())
errors = 0
for k in diff.keys():
    if k not in ("dictionary_item_added", "iterable_item_added"):
        print(
            Fore.RED + "ERROR: %s should not be present in diff!" % k + Style.RESET_ALL
        )
        errors += 1
if errors:
    sys.exit(errors)

urls = {}
for root in diff.get("dictionary_item_added", []):
    m = re.match(r""".*'(https://[^']+)""", root)
    if m:
        url = m.group(1)
        for entry in current[url]:
            urls[url] = entry.get("sha256")

for url in sorted(urls):
    if not verify_url(url, urls[url]):
        errors += 1
sys.exit(errors)

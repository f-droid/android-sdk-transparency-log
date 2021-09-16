#!/bin/sh -e

./verify-for-signing.py
git pull
mkdir -p signed
cp checksums.json signed/checksums.json
rm -f signed/checksums.json.asc
gpg --armor --detach-sign signed/checksums.json
git add signed/
git commit -m "gpg sign current checksums.json"
git push

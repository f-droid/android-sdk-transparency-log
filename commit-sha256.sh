#!/bin/sh -ex

basedir=`pwd`
cd /tmp/fdroidserver
git reset --hard master
for f in `git log --reverse -- makebuildserver makebuildserver.py | grep ^commit\ | awk '{print $2}'`; do
    git show $f | grep '^\+' | grep -E 'https?://(verification|[a-z.-]+\.google\.com)' || continue
    git checkout $f
    $basedir/get-sha256-from-makebuildserver.py
    git -C $basedir add $basedir/checksums.json
    git -C $basedir commit --allow-empty $basedir/checksums.json \
        --author="`git log -n1 --pretty=format:'%an <%ae>' $f`" \
        --date=`git log -n1 --pretty=format:%at` \
        -m "`git log -n1 --pretty=format:%s`" \
        -m "from https://gitlab.com/fdroid/fdroidserver/commit/$f"
done

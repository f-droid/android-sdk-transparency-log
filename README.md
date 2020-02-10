
# Android SDK Transparency Log

This is an automated log of the Android SDK binaries and their
checksums, as posted in the _sdkmanager_ repositories hosted on
https://dl.google.com/android/repository

This serves as a basic [binary
transparency](https://wiki.mozilla.org/Security/Binary_Transparency)
append-only log for anyone to use.  One of the key properties of any
good binary repository is that the binaries never change once they
have been published.  [Maven has been promising
this](https://blog.sonatype.com/2009/04/what-is-a-repository/) since
2009 at least.  F-Droid has for most of its history.  Occasionally,
Google forgets this, and changes packages that have already been
published:

* [Google Issue #70292819 platform-27_r01.zip was overwritten with a new update](https://issuetracker.google.com/issues/70292819) (Google login and Javascript required)


## API

This can also be used as a basic JSON API by getting the JSON files via the raw links:

* [checksums.json](https://gitlab.com/fdroid/android-sdk-transparency-log/-/raw/master/checksums.json) - a simple dictionary of download URLs and matching checksums
* [status_codes.json](https://gitlab.com/fdroid/android-sdk-transparency-log/-/raw/master/status_codes.json) - the HTTP Status Codes of the last download attempt of this process


## Local verification

If there is an F-Droid _buildserver_ instance setup on a machine, it
will cache the Android SDK components in
_~/.cache/fdroidserver_. There is a script here to log all of the
Android SDK binaries found in that folder:
`./index-cache-fdroidserver.py`.  Run that script on the machine and
user account that runs the _buildserver_ instance, and it will add any
unknown packages it finds to the local _checksums.json_.  If there are
no changes to _checksums.json_ after that script successfully
completes, that means no unknown packages were found.


# Android SDK Transparency Log

This is an automated log of the Android SDK binaries and their
checksums, as posted in the _sdkmanager_ repositories hosted on
https://dl.google.com/android/repository

This serves as a basic
[binary transparency](https://wiki.mozilla.org/Security/Binary_Transparency)
append-only log for anyone to use.

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

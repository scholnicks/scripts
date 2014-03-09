#!/usr/bin/python -B
# -*- coding: utf-8 -*-

"""
is-drop-current: Checks installed Dropbox version against latest version available.

Inspired by: https://github.com/tjluoma/is-dropbox-current (zsh version)

(c) Steven Scholnick <steve@scholnick.net>

The is-drop-current source code is published under version 2.1 of the GNU Lesser General Public License (LGPL).

In brief, this means there's no warranty and you can do anything you like with it.
However, if you make changes to rename and redistribute those changes,
then you must publish your modified version under the LGPL.
"""

from __future__ import print_function
import sys, re
import plistlib
import feedparser

STABLE_BUILD     = 'New Stable Build: '
DOWNLOAD_MESSAGE = "\tDownload latest version from https://dl-web.dropbox.com/u/17/Dropbox%20{0}.dmg\n"


def main():
    '''main method'''
    installed_version = get_installed_version()

    if options.debug:
        print("Installed version : {0}".format(installed_version))

    latest_version = get_latest_version()

    if options.debug:
        print("Latest version (from RSS) : {0}".format(latest_version))

    if installed_version != latest_version:
        print("{0} is installed. Latest version available is {1}".format(installed_version,latest_version))
        print(DOWNLOAD_MESSAGE.format(latest_version))
    elif options.debug:
        print("Versions match: {0}".format(installed_version))

    sys.exit(0)


def get_installed_version():
    '''Returns the current installed version by parsing Dropbox's client Info.plist'''
    plist_data = plistlib.readPlist('/Applications/Dropbox.app/Contents/Info.plist')
    return re.sub(r'[^0-9.]+','',plist_data['CFBundleShortVersionString'].strip())


def get_latest_version():
    '''Returns the latest version announced in the release_notes RSS feed'''
    parser = feedparser.parse("https://www.dropbox.com/release_notes/rss.xml")
    for e in parser.entries:
        if e.title.startswith(STABLE_BUILD):
            return e.title[len(STABLE_BUILD):].strip()

    raise RuntimeError("Unable to determine the latest version number")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Checks installed Dropbox version against latest version available')
    parser.add_argument('-d','--debug', dest="debug", action="store_true", help='Toggles debug mode')
    options = parser.parse_args()

    main()

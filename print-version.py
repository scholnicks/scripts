#!/usr/bin/env python -B
# -*- coding: utf-8 -*-

"""
print-version: Reads an app's Info.plist and prints the version number for the app

Usage:
   print-version [--verbose] <application>

Inspired by: https://github.com/tjluoma/is-dropbox-current (zsh version)

Options:
    -h, --help     Show this help screen
    --version      Prints the version

(c) Steven Scholnick <scholnicks@gmail.com>

The print-version source code is published under a MIT license. See http://www.scholnick.net/license.txt for details.
"""

from __future__ import print_function
import sys, re
import plistlib

def main():
    '''main method'''
    path = '/Applications/{}.app/Contents/Info.plist'.format(arguments['<application>']);
    plist_data = plistlib.readPlist(path)
    version = re.sub(r'[^0-9.]+','',plist_data['CFBundleShortVersionString'].strip())
    print("App: {0}, Version: {1}".format(arguments['<application>'],version))
    sys.exit(0)


if __name__ == '__main__':
    from docopt import docopt
    arguments = docopt(__doc__, version='1.0.0')
    main()

#!/usr/bin/python -B
# -*- coding: utf-8 -*-

"""checklinks - validate links in one or more HTML files

Requires external modules that can be installed from PyPI with:
    pip install lxml BeautifulSoup requests

(c) Steven Scholnick <steve@scholnick.net>

The checklinks source code is published under a MIT license. See http://www.scholnick.net/license.txt for details.
"""

from __future__ import print_function
from bs4 import BeautifulSoup
import os, sys
import requests

FORMAT="{0:80.70s} {1:10s}"


def main():
    try:
        for filePath in args:
            processFile(filePath)
    except KeyboardInterrupt:
        print()

    sys.exit(0)


def processFile(filePath):
    """parses an HTML file"""
    if options.verbose:
        print("Processing file {0}".format(filePath))

    with open(filePath,'r') as fp:
        soup = BeautifulSoup(fp,'lxml')
        checkLinks(soup.find_all('link'),'href')
        checkLinks(soup.find_all('a'),'href')
        if options.image:
            checkLinks(soup.find_all('img'),'src')
        checkLinks(soup.find_all('script'),'src')


def checkLinks(tags,externalAttributeName):
    """checks the links in the passed in tags"""
    for t in tags:
        try:
            link = t.attrs[externalAttributeName]
            if link.startswith('http'):
                checkRemote(link)
            else:
                checkLocal(link)
        except KeyError:
            # no src or href, just move onto the next tag
            pass


def checkRemote(link):
    """checks a remote (http/https) link"""
    try:
        request = requests.get(link)
        if request.status_code != 200 or options.showGood:
            print(FORMAT.format(link, str(request.status_code)))
    except requests.exceptions.RequestException as e:
        print(FORMAT.format(link,e.message if options.verbose else 'Cannot contact host'))


def checkLocal(path):
    """Checks for the existence of a local file on disk"""
    if 'mailto' in path or path.startswith("#"):
        return

    if path[0] == '/' and options.rootDirectory:
        root = options.rootDirectory
        path = (root[:-1] if root[-1] == '/' else root) + path

    exists = os.path.exists(path)
    if not exists or options.showGood:
        print(FORMAT.format(path, "Good" if exists else "Missing"))


if __name__ == '__main__':
    from optparse import OptionParser

    parser = OptionParser(usage="%prog [options] filenames")
    parser.add_option('-i','--image',   dest="image",         action="store_true", help='Turns on image checking')
    parser.add_option('-o','--ok',      dest="showGood",      action="store_true", help='Shows the good links')
    parser.add_option('-r','--root',    dest="rootDirectory", type='string',       help='Sets the root web directory')
    parser.add_option('-v','--verbose', dest="verbose",       action="store_true", help='Toggles verbose')

    options,args = parser.parse_args()

    if options.verbose:
        options.showGood = True

    if len(args) == 0:
        parser.print_help()
        sys.exit(1)

    if options.rootDirectory:
        options.rootDirectory = os.path.expanduser(options.rootDirectory)

    main()

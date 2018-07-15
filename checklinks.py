#!/usr/bin/env python -B
# -*- coding: utf-8 -*-

"""checklinks - validate links in one or more HTML files. The HTML files can exist locally or be accessible via a URL.

Usage:
    checklinks [options]  <filesOrURLs> ...

Options:
    -h, --help                    Show this help screen
    -i, --image                   Turns on image checking
    -o, --ok                      Shows the good links
    -r, --root=<root_directory>   Sets the root web directory
    -v, --verbose                 Verbose Mode
    --version                     Prints the version

Requires external modules that can be installed from PyPI with:
    pip install lxml
    pip install requests
    pip install beautifulsoup4

(c) Steven Scholnick <scholnicks@gmail.com>

The checklinks source code is published under a MIT license. See https://scholnick.nett/license.txt for details.
"""

from __future__ import print_function
from bs4 import BeautifulSoup
import os, sys
import requests

FORMAT="{0:80.70s} {1:10s}"


def main(html_files):
    try:
        for filePath in html_files:
            if filePath.startswith('http'):
                processRemoteFile(filePath)
            else:
                processFile(filePath)
    except KeyboardInterrupt:
        print()

    sys.exit(0)


def processRemoteFile(url):
    '''Parses a URL's text and checks all of the a links'''
    r = requests.get(url)
    if r.status_code != 200:
        print("Cannot access URL: " + url)
        return

    root = os.path.dirname(url)

    soup = BeautifulSoup(r.text)
    for tag in soup.find_all('a'):
        link = tag['href']
        if not link.startswith('http'):
            link = root + link
        checkRemote(link)


def processFile(filePath):
    """parses an HTML file"""
    if arguments['--verbose']:
        print("Processing file {0}".format(filePath))

    with open(filePath,'r') as fp:
        soup = BeautifulSoup(fp,'lxml')
        checkLinks(soup.find_all('link'),'href')
        checkLinks(soup.find_all('a'),'href')
        if arguments['--image']:
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
        if request.status_code != 200 or arguments['--ok']:
            print(FORMAT.format(link, str(request.status_code)))
    except requests.exceptions.RequestException as e:
        print(FORMAT.format(link,e.message if arguments['--verbose'] else 'Cannot contact host'))


def checkLocal(path):
    """Checks for the existence of a local file on disk"""
    if 'mailto' in path or path.startswith("#"):
        return

    if path[0] == '/' and arguments['--root']:
        root = arguments['--root']
        path = (root[:-1] if root[-1] == '/' else root) + path

    exists = os.path.exists(path)
    if not exists or arguments['--ok']:
        print(FORMAT.format(path, "Good" if exists else "Missing"))


if __name__ == '__main__':
    from docopt import docopt
    arguments = docopt(__doc__, version='2.0.0')

    if arguments['--verbose']:
        arguments['--ok'] = True

    if arguments['--root']:
        arguments['--root'] = os.path.expanduser(arguments['--root'])

    main(arguments['<filesOrURLs>'])

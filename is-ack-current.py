#!/usr/bin/python -B
# -*- coding: utf-8 -*-

"""
is-ack-current: Checks installed ack version against latest version available.

(c) Steven Scholnick <steve@scholnick.net>

The is-ack-current source code is published under a MIT license. See http://www.scholnick.net/license.txt for details.
"""

from __future__ import print_function
import sys, re, subprocess
import requests

def main():
    '''main method'''
    installed_version = get_installed_version()

    if options.debug:
        print("Installed version : {0}".format(installed_version))

    latest_version = get_latest_version()

    if options.debug:
        print("Latest version (from website) : {0}".format(latest_version))

    if installed_version != latest_version:
        print("{0} is installed. Latest version available is {1}".format(installed_version,latest_version))
        print('To Install\n\tcurl http://beyondgrep.com/ack-{0}-single-file > ~/bin/ack && chmod 0755 !#:3'.format(latest_version))
    elif options.debug:
        print("Versions match: {0}".format(installed_version))

    sys.exit(0)


def get_installed_version():
    '''Returns the current installed version by parsing ack --version'''
    process = subprocess.Popen(['ack',"--version"],stdout=subprocess.PIPE)
    line = process.stdout.readline()
    return re.sub(r'[^0-9.]+','',line).strip()


def get_latest_version():
    '''Returns the latest version announced on the install page'''
    request = requests.get('http://beyondgrep.com/install/')
    match = re.search(r'The current stable version of ack is version ([0-9.]+),',request.text,re.IGNORECASE)
    if len(match.groups()):
        return match.groups()[0]

    raise RuntimeError("Unable to determine the latest version number")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Checks installed ack version against latest version available')
    parser.add_argument('-d','--debug', dest="debug", action="store_true", help='Toggles debug mode')
    options = parser.parse_args()

    main()

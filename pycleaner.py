#!/usr/bin/python -B
# -*- coding: utf-8 -*-

"""
pycleaner [--verbose] FILES DIRECTORIES

The following cleaning is performed:

* All ending whitespace is removed
* All tabs are converted to 4 spaces
* Spaces before a : are removed

(c) Steven Scholnick <steve@scholnick.net>

The rename source code is published under version 2.1 of the GNU Lesser General Public License (LGPL).

In brief, this means there's no warranty and you can do anything you like with it.
However, if you make changes to rename and redistribute those changes,
then you must publish your modified version under the LGPL.
"""

from __future__ import print_function
import os, sys, re


def main():
    for path in args:
        path = os.path.abspath(path)
        if os.path.isdir(path):
            processDirectory(path)
        else:
            processFile(filePath)

    sys.exit(0)


def processDirectory(startingDirectory):
    for root, dirs, files in os.walk(startingDirectory):
        for f in files:
            if f.endswith(".py"):
                processFile(os.path.join(root,f))


def processFile(filePath):
    if options.verbose:
        print("Cleaning {0}".format(filePath))

    lines = []
    with open(filePath,'r') as inStream:
        for line in inStream:
            line = line.rstrip()
            line = line.expandtabs(4)
            line = re.sub(r'\s+:',':',line)
            lines.append(line)

    with open(filePath,'w') as outStream:
        for line in lines:
            print(line,file=outStream)

            if options.verbose:
                print(line)


if __name__ == '__main__':
    from optparse import OptionParser

    parser = OptionParser(usage=__doc__)
    parser.add_option('-v','--verbose',dest="verbose", action="store_true", help='Toggles verbose')

    options,args = parser.parse_args()

    if len(args) == 0:
        parser.print_help()
        sys.exit(1)

    main()

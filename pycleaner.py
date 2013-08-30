#!/usr/bin/python -B
# -*- coding: utf-8 -*-

"""
pycleaner.py - cleans Python scripts

(c) Steven Scholnick <steve@scholnick.net>

The rename source code is published under version 2.1 of the GNU Lesser General Public License (LGPL).

In brief, this means there's no warranty and you can do anything you like with it.
However, if you make changes to rename and redistribute those changes,
then you must publish your modified version under the LGPL.
"""

from __future__ import print_function
import os, sys, re


def main():
    for filePath in args:
        filePath = os.path.abspath(filePath)

        if options.verbose:
            print("Procesing {0}".format(filePath))

        processFile(filePath)

    sys.exit(0)


def processFile(filePath):
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

    parser = OptionParser(usage="%prog [options] filenames")
    parser.add_option('-v','--verbose',dest="verbose", action="store_true", help='Toggles verbose')

    options,args = parser.parse_args()

    if len(args) == 0:
        parser.print_help()
        sys.exit(1)

    main()

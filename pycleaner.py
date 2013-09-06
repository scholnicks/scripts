#!/usr/bin/python -B
# -*- coding: utf-8 -*-

"""
pycleaner [--verbose] FILES DIRECTORIES

The following cleaning is performed:

* Ending whitespace is removed
* Tabs are converted to 4 spaces
* Spaces before a colon are removed
* Trailing blank lines

(c) Steven Scholnick <steve@scholnick.net>

The rename source code is published under version 2.1 of the GNU Lesser General Public License (LGPL).

In brief, this means there's no warranty and you can do anything you like with it.
However, if you make changes to rename and redistribute those changes,
then you must publish your modified version under the LGPL.
"""

from __future__ import print_function
import os, sys, re


def main():
    """main method"""
    for path in args:
        path = os.path.abspath(path)
        if os.path.isdir(path):
            processDirectory(path)
        else:
            processFile(path)

    sys.exit(0)


def processDirectory(startingDirectory):
    """Cleans all .py files in the startingDirectory and any .py files in any child directories"""
    for root, dirs, files in os.walk(startingDirectory):
        for f in files:
            if f.endswith(".py"):
                processFile(os.path.join(root,f))


def processFile(filePath):
    """cleans a single .py file"""
    if options.verbose:
        print("Cleaning {0}".format(filePath))

    lines = []
    with open(filePath,'r') as inStream:
        for line in inStream:
            line = line.rstrip()
            line = line.expandtabs(4)
            line = re.sub(r'\s+:',':',line)
            lines.append(line)

    count = countTrailingBlankLines(lines)

    if count > 0:
        lines = lines[:len(lines) - count]

    with open(filePath,'w') as outStream:
        for line in lines:
            print(line,file=outStream)


def countTrailingBlankLines(lines):
    """Returns the number of trailing blank lines"""
    count = 0
    for line in reversed(lines):
        line = line.rstrip()
        if line:
            break
        else:
            count = count + 1

    return count


if __name__ == '__main__':
    from optparse import OptionParser

    parser = OptionParser(usage=__doc__)
    parser.add_option('-v','--verbose',dest="verbose", action="store_true", help='Toggles verbose')

    options,args = parser.parse_args()

    if len(args) == 0:
        parser.print_help()
        sys.exit(1)

    main()

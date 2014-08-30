#!/usr/bin/python -B
# -*- coding: utf-8 -*-

"""
Find and replace all instances of a string with a new string in a directory and all its sub-directories. Extension (-x|--extension) and
substitute pattern (-s|--substitute) are required.

Example
-------
far -x .html -s 'foo/bar' website

For all files starting with the directory website, all foo references are changed to bar.

Similar to find . -name "*.txt" -print0 | xargs -0 sed -i '' -e 's/foo/bar/g'

(c) Steven Scholnick <steve@scholnick.net>

The far source code is published under a MIT license. See http://www.scholnick.net/license.txt for details.
"""

from __future__ import print_function
import os, sys, re

def main(startingDirectory):
    eligible_files = []
    for root, dirs, files in os.walk(os.path.abspath(startingDirectory)):
        eligible_files += [os.path.join(root,f) for f in files if f.lower().endswith(options.extension)]

    try:
        for file in eligible_files:
            processFile(file)
            if options.verbose:
                print("Processed {0}".format(file))
    except AttributeError:
        print("far: Illegal substitute pattern. Pattern must be old/new",file=sys.stderr)
        sys.exit(-1)

    sys.exit(0)


def processFile(file):
    (old,new) = re.match(r'^(.*)/(.*)$',options.substitute).groups()

    with open(file,"r") as inFile:
        input_data = inFile.readlines()

    input_data = [line.replace(old,new) for line in input_data]

    with open(file,'w') as outFile:
        outFile.writelines(input_data)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-x','--extension',  dest="extension",  action="store",      required="true", help='File extension')
    parser.add_argument('-s','--substitute', dest="substitute", action="store",      required="true", help='Substitution a pattern (old/new)')
    parser.add_argument('-v','--verbose',    dest="verbose",    action="store_true", help='Toggles verbose')
    parser.add_argument('startingDirectory', type=str)

    options = parser.parse_args()

    main(options.startingDirectory)

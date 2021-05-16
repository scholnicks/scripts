#!/usr/bin/env python -B
# -*- coding: utf-8 -*-
#
# (c) Steven Scholnick <scholnicks@gmail.com>
# The far source code is published under a MIT license.

"""
far: Find and replace all instances of a string with a new string in a directory and all its sub-directories.

Usage:
    far [options] [<extension>] [<pattern>] [<starting-directory>]

Options:
    -h, --help                Show this help screen
    -r,--replacement=<text>   Replacement text
    --usage                   Detailed usage information
    -v, --verbose             Verbose Mode
    --version                 Prints the version

if <starting-directory> is not specified, the current working directory is used.
"""

import os, sys, re

def main(startingDirectory):
    if arguments['--usage'] or not startingDirectory or not arguments['<extension>'] or not arguments['<pattern>']:
        usage()

    eligible_files = []
    for root, dirs, files in os.walk(os.path.abspath(startingDirectory if startingDirectory else '.')):
        eligible_files += [os.path.join(root,f) for f in files if f.lower().endswith(arguments['<extension>'])]

    for file in eligible_files:
        processFile(file)
        if arguments['--verbose']:
            print("Processed {0}".format(file))

    sys.exit(0)


def processFile(file):
    old = arguments['<pattern>']
    new = arguments['--replacement'] if arguments['--replacement'] else ''

    with open(file,"r") as inFile:
        input_data = inFile.readlines()

    output = [line.replace(old,new) for line in input_data]

    with open(file,'w') as outFile:
        outFile.writelines(output)


def usage():
    print(__doc__ + """
Example
-------
far .html --replacement "bar" foo .

For all files starting with the directory website, all foo references are changed to bar.

Similar to find . -name "*.html" -print0 | xargs -0 sed -i '' -e 's/foo/bar/g'

""")
    sys.exit(0)


if __name__ == '__main__':
    from docopt import docopt
    arguments = docopt(__doc__, version='1.1.0')
    main(arguments['<starting-directory>'])

#!/usr/bin/env python -B
# -*- coding: utf-8 -*-
#
# (c) Steven Scholnick <scholnicks@gmail.com>
# The far source code is published under a MIT license.

"""
far: Find and replace all instances of a string with a new string in a directory and all its sub-directories.

Usage:
    far [options] [<replacement>] [<pattern>]

Options:
    -d, --directory=<directory>   Starting directory [default: .]
    --dry-run                     Just list the files to be changed, no actual changes
    -e, --extension=<extension>   File extension
    -h, --help                    Show this help screen
    --usage                       Detailed usage information
    -v, --verbose                 Verbose Mode
    --version                     Prints the version
"""

import os
import sys
import re

def main():
    if arguments['--usage'] or not arguments['<pattern>'] or not arguments['<replacement>']:
        usage()

    if arguments['--dry-run']:
        arguments['--verbose'] = True

    eligibleFiles = []
    for root, dirs, files in os.walk(os.path.abspath(arguments['--directory'])):
        eligibleFiles += [os.path.join(root,f) for f in files if matches(f)]

    for file in eligibleFiles:
        if not arguments['--dry-run']:
            processFile(file)
        if arguments['--verbose']: print("Processed {0}".format(file))

    sys.exit(0)


def processFile(file):
    old = arguments['<pattern>']
    new = arguments['<replacement>']

    with open(file,"r") as inFile:
        input_data = inFile.readlines()

    output = [line.replace(old,new) for line in input_data]

    with open(file,'w') as outFile:
        outFile.writelines(output)


def matches(filename):
    return filename.lower().endswith(arguments['--extension']) if arguments['--extension'] else True


def usage():
    print(__doc__ + """
Example
-------
far -e .html bar foo

For all files starting with the directory website, all foo references are changed to bar.

Similar to find . -name "*.html" -print0 | xargs -0 sed -i '' -e 's/foo/bar/g'

""")
    sys.exit(0)


if __name__ == '__main__':
    from docopt import docopt
    arguments = docopt(__doc__, version='1.1.1')
    main()

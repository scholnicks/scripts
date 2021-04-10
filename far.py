#!/usr/bin/env python -B
# -*- coding: utf-8 -*-
#
# (c) Steven Scholnick <scholnicks@gmail.com>
# The far source code is published under a MIT license.

"""
far: Find and replace all instances of a string with a new string in a directory and all its sub-directories.

Usage:
    far [--verbose] <extension> <substitution-pattern> [<starting-directory>]

Options:
    -h, --help     Show this help screen
    -v, --verbose  Verbose Mode
    --version      Prints the version

if <starting-directory> is not specified, the current working directory is used.

Example
-------
far .html 'foo/bar' .

For all files starting with the directory website, all foo references are changed to bar.

Similar to find . -name "*.html" -print0 | xargs -0 sed -i '' -e 's/foo/bar/g'
"""

import os, sys, re

def main(startingDirectory):
    eligible_files = []
    for root, dirs, files in os.walk(os.path.abspath(startingDirectory if startingDirectory else '.')):
        eligible_files += [os.path.join(root,f) for f in files if f.lower().endswith(arguments['<extension>'])]

    try:
        for file in eligible_files:
            processFile(file)
            if arguments['--verbose']:
                print("Processed {0}".format(file))
    except AttributeError:
        print("far: Illegal substitute pattern. Pattern must be old/new",file=sys.stderr)
        sys.exit(-1)

    sys.exit(0)


def processFile(file):
    (old,new) = re.match(r'^(.*)/(.*)$',arguments['<substitution-pattern>']).groups()

    with open(file,"r") as inFile:
        input_data = inFile.readlines()

    output = [line.replace(old,new) for line in input_data]

    with open(file,'w') as outFile:
        outFile.writelines(output)


if __name__ == '__main__':
    from docopt import docopt
    arguments = docopt(__doc__, version='1.0.1')
    main(arguments['<starting-directory>'])

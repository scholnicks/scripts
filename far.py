#!/usr/bin/env python -B
# -*- coding: utf-8 -*-
#
# (c) Steven Scholnick <scholnicks@gmail.com>
# The far source code is published under a MIT license.

"""
far: Find and replace all instances of a string with a new string in a directory and all its sub-directories.

Usage:
    far [options] <pattern> [<replacement>]

Options:
    -d, --directory=<directory>   Starting directory [default: .]
    -e, --extension=<extension>   Only process file with this extension
    -h, --help                    Show this help screen
    -l, --list                    Just list the files to be changed, no actual changes
    -r, --remove                  Removes the line, that matches pattern, from all files
    -v, --verbose                 Verbose Mode
    --version                     Prints the version
"""

import os
import re
import sys

EXCLUDED_DIRECTORIES = ('.git','.hg','.svn','.vscode','.idea','.metadata','node_modules')

def main():
    """Main method"""
    if not arguments['--remove'] and not arguments['<replacement>']:
        raise SystemExit('far: <replacement> is required')

    eligibleFiles = []
    for root, dirs, files in os.walk(os.path.abspath(arguments['--directory']),topdown=True):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRECTORIES]
        eligibleFiles += [os.path.join(root,f) for f in files if matches(f)]

    for file in eligibleFiles:
        if arguments['--list']:
            print("{}".format(file))
        else:
            processFile(file)
            if arguments['--verbose']: print("Processed {}".format(file))

    sys.exit(0)


def processFile(file):
    """Processes a file"""
    with open(file,"r") as inFile:
        input_data = inFile.readlines()

    if arguments['--remove']:
        output = [line for line in input_data if arguments['<pattern>'] not in line]
    else:
        output = [line.replace(arguments['<pattern>'],arguments['<replacement>']) for line in input_data]

    with open(file,'w') as outFile:
        outFile.writelines(output)


def matches(filename):
    """Returns if the filename should be processed"""
    return filename.lower().endswith(arguments['--extension']) if arguments['--extension'] else True


if __name__ == '__main__':
    from docopt import docopt
    arguments = docopt(__doc__, version='1.3.0')
    main()

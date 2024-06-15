#!/usr/bin/env python -B
# vi: set syntax=python ts=4 sw=4 sts=4 et ff=unix ai si :
#
# (c) Steven Scholnick <scholnicks@gmail.com>
# The pycleaner source code is published under a MIT license.

"""
pycleaner: clean python source files

Usage:
   pycleaner [--verbose] <files> ...

Files can be a directory. If it is a directory, the directory and all of its sub-directories are search for .py files.

The following cleaning is performed:

* Ending whitespace is removed
* Tabs are converted to 4 spaces
* Spaces before a colon are removed
* Trailing blank lines are removed

Options:
    -h, --help     Show this help screen
    -v, --verbose  Verbose Mode
    --version      Prints the version
"""

import os, sys, re


def main(files):
    """main method"""
    for path in files:
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
    if arguments['--verbose']:
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
    from docopt import docopt
    arguments = docopt(__doc__, version='1.0.1')
    main(arguments['<files>'])

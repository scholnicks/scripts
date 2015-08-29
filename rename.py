#!/usr/bin/python -B
# -*- coding: utf-8 -*-

"""
rename:  Renames files in powerful ways

Usage:
    rename [options] <files> ...

Options:
    -a, --append=<suffix>                      Suffix to be appended
    -d, --delimiter=<delimiter>                Specifies the delimiter for fixing numerical filenames
    -f, --fix=<number of digits to fix>        Fixes numerical file names [default: 4]
    -h, --help                                 Show this help screen
    -l, --lower                                Translates the filenames to lowercase
    -p, --prepend=<prefix>                     Prefix to be prepended
    -r, --remove=<pattern>                     Pattern to be removed
    -s, --substitute=<substitution pattern>    Substitutes a pattern (old/new)
    -t, --test                                 Test mode (Just prints the renames)
    -v, --verbose                              Verbose Mode
    --version                                  Prints the version

(c) Steven Scholnick <scholnicks@gmail.com>

The rename source code is published under a MIT license. See http://www.scholnick.net/license.txt for details.
"""

from __future__ import print_function
import os, sys, re

def main(files):
    """Main Method"""
    if arguments['--verbose']:
        print("Renaming: {0}".format(", ".join(files)))

    for fileName in files:
        renameFile(fileName)

    sys.exit(0)

def renameFile(fileName):
    """Renames an individual file"""
    if not os.path.exists(fileName):
        print("{0} does not exist, skipping.".format(fileName),file=sys.stderr)
        return

    newFileName = fileName

    if arguments['--lower']:
        newFileName = newFileName.lower()

    if arguments['--append']:
        newFileName = newFileName + arguments['--append']

    if arguments['--prepend']:
        newFileName = arguments['--prepend'] + newFileName

    if arguments['--remove']:
        newFileName = re.sub(arguments['--remove'],r'',newFileName)

    if arguments['--delimiter']:
        newFileName = fixNumbers(newFileName,arguments['--delimiter'],arguments['--fix'])

    if arguments['--substitute']:
        newFileName = substitute(newFileName,arguments['--substitute'])

    if newFileName != fileName:
        if arguments['--verbose']:
            print("Renaming {0} to {1}".format(fileName,newFileName))

        if not arguments['--test']:
            os.rename(fileName,newFileName)


def substitute(fileName,pattern):
    """Performs the pattern substitution"""
    try:
        (old,new) = re.match(r'^(.*)/(.*)$',pattern).groups()
        return re.sub(old,new,fileName)
    except AttributeError:
        print("rename: Illegal substitute pattern. Pattern must be old/new",file=sys.stderr)
        sys.exit(-1)


def fixNumbers(fileName,delimiter,numberLength):
    """Fixes the numeric part of a filename"""
    if delimiter not in fileName:
        return fileName

    (base,extension) = os.path.splitext(fileName)
    (prefix,number)  = base.split(delimiter,2)

    sequenceValue = number

    for i in xrange(len(number),int(numberLength)):
        sequenceValue = "0" + sequenceValue

    return prefix + delimiter + sequenceValue + extension


if __name__ == '__main__':
    from docopt import docopt
    arguments = docopt(__doc__, version='1.1.0')

    if arguments['--test']:
        arguments['--verbose'] = True

    main(arguments['<files>'])

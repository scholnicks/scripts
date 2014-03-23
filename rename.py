#!/usr/bin/python -B
# -*- coding: utf-8 -*-

"""
rename:  Renames files in powerful ways

(c) Steven Scholnick <steve@scholnick.net>

The rename source code is published under version 2.1 of the GNU Lesser General Public License (LGPL).

In brief, this means there's no warranty and you can do anything you like with it.
However, if you make changes to rename and redistribute those changes,
then you must publish your modified version under the LGPL.
"""

from __future__ import print_function
import os, sys, re

MINIMUM_NUMBER_LENGTH = 4


def main(files):
    """Main Method"""
    if options.verbose:
        print("Renaming {0}".format(", ".join(files)))

    for fileName in files:
        renameFile(fileName)

    sys.exit(0)

def renameFile(fileName):
    """Renames an individual file"""
    if not os.path.exists(fileName):
        print("{0} does not exist, skipping.".format(fileName),file=sys.stderr)
        return

    newFileName = fileName

    if options.lower:
        newFileName = newFileName.lower()

    if options.append:
        newFileName = newFileName + options.append

    if options.prepend:
        newFileName = options.prepend + newFileName

    if options.remove:
        newFileName = re.sub(options.remove,r'',newFileName)

    if options.fixNumbers:
        newFileName = fixNumbers(newFileName,options.fixNumbers)

    if options.substitute:
        newFileName = substitute(newFileName,options.substitute)

    if newFileName != fileName:
        if options.verbose: print("Renaming {0} to {1}".format(fileName,newFileName))

        if not options.test:
            os.rename(fileName,newFileName)


def substitute(fileName,pattern):
    """Performs the pattern substitution"""
    try:
        (old,new) = re.match(r'^(.*)/(.*)$',pattern).groups()
        return re.sub(old,new,fileName)
    except AttributeError:
        print("rename: Illegal substitute pattern. Pattern must be old/new",file=sys.stderr)
        sys.exit(-1)


def fixNumbers(fileName,delimiter):
    """Fixes the nnumeric part of a filename"""
    if delimiter not in fileName:
        return fileName

    (base,extension) = os.path.splitext(fileName)
    (prefix,number)  = base.split(delimiter,2)

    sequenceValue = number

    # TODO: rewrite using the * operator for strings
    for i in xrange(len(number),MINIMUM_NUMBER_LENGTH):
        sequenceValue = "0" + sequenceValue

    return prefix + delimiter + sequenceValue + extension


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Renames files in powerful ways')
    parser.add_argument('-a','--append',     dest="append",     action="store",      help='Appends a suffix to each filename')
    parser.add_argument('-f','--fix-numbers',dest="fixNumbers", action="store",      help='Fix numbers. Ensures that a minimum number of leading zeroes is present')
    parser.add_argument('-l','--lower',      dest="lower",      action="store_true", help='Translates the filenames to lowercase')
    parser.add_argument('-p','--prepend',    dest="prepend",    action="store",      help='Prepend a prefix to each filename')
    parser.add_argument('-r','--remove',     dest="remove",     action="store",      help='Removes a pattern')
    parser.add_argument('-s','--substitute', dest="substitute", action="store",      help='Substitutes a pattern (old/new)')
    parser.add_argument('-t','--test',       dest="test",       action="store_true", help='Toggles test mode (pretends to rename only)')
    parser.add_argument('-v','--verbose',    dest="verbose",    action="store_true", help='Toggles verbose')
    parser.add_argument('files', nargs="+", type=str)

    options = parser.parse_args()

    if options.test:
        options.verbose = True

    main(options.files)

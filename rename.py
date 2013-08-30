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


def main():
    if options.verbose: print("Renaming {}".format(", ".join(args)))

    for fileName in args:
        renameFile(fileName)


def renameFile(fileName):
    if not os.path.exists(fileName):
        print("{} does not exist, skipping.".format(fileName),file=sys.stderr)
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
        if options.verbose: print("Renaming {} to {}".format(fileName,newFileName))

        if not options.test:
            os.rename(fileName,newFileName)


def substitute(fileName,pattern):
    try:
        (old,new) = re.match(r'^(.*)/(.*)$',pattern).groups()
        return re.sub(old,new,fileName)
    except AttributeError:
        print("rename: Illegal substitute pattern",file=sys.stderr)
        sys.exit(-1)


def fixNumbers(fileName,delimiter):
    if delimiter not in fileName:
        return fileName

    (base,extension) = os.path.splitext(fileName)
    (prefix,number)  = base.split(delimiter,2)

    sequenceValue = number

    for i in xrange(len(number),MINIMUM_NUMBER_LENGTH):
        sequenceValue = "0" + sequenceValue

    return prefix + delimiter + sequenceValue + extension


if __name__ == '__main__':
    from optparse import OptionParser

    parser = OptionParser(usage="%prog [options] filenames")
    parser.add_option('-a','--append',dest="append", type='string', help='Append')
    parser.add_option('-f','--fix-numbers',dest="fixNumbers", type='string', help='fix numbers')
    parser.add_option('-l','--lower',dest="lower", action="store_true", help='Toggles lower')
    parser.add_option('-p','--prepend',dest="prepend", type='string', help='Prepend')
    parser.add_option('-r','--remove',dest="remove", type='string', help='Remove')
    parser.add_option('-s','--substitute',dest="substitute", type='string', help='Substitute')
    parser.add_option('-t','--test',dest="test", action="store_true", help='Toggles test')
    parser.add_option('-v','--verbose',dest="verbose", action="store_true", help='Toggles verbose')

    options,args = parser.parse_args()

    if options.test:
        options.verbose = True

    if len(args) == 0:
        parser.print_help()
        sys.exit(1)

    main()

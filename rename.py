#!/usr/bin/python -B
# -*- coding: utf-8 -*-

"""
rename: Renames files in powerful ways

Usage:
    rename [options] <files> ...

Options:
    -a, --append=<suffix>                      Suffix to be appended
    -d, --delimiter=<delimiter>                Specifies the delimiter for fixing numerical filenames
    --directory=<directory>                    Destination directory
    -f, --fix=<maximum number of digits>       Fixes numerical file names [default: 4]
    -h, --help                                 Show this help screen
    -l, --lower                                Translates the filenames to lowercase
    -p, --prepend=<prefix>                     Prefix to be prepended
    -r, --remove=<pattern>                     Pattern to be removed
    --random                                   Randomize the files (--prepend can be used to specify the prefix, defaults to "file")
    --merge                                    Merges the files in order specfied on command line (See below for details/examples)
    -s, --substitute=<substitution pattern>    Substitutes a pattern (old/new)
    -t, --test                                 Test mode (Just prints the renames)
    -v, --verbose                              Verbose Mode
    --version                                  Prints the version

Using merge

merge requires directory to be specified. prepend (defaults to file) is used for the base name for the merged files.
For example to merge files from two different directories into the current directory:

rename --merge --directory=. directory1/* directory2/*

Input Files: directory1/file1.txt directory1/file2.txt directory2/file1.txt
Results: ./file_0001.txt ./file_0002.txt ./file_0003.txt

where file_0003.txt is directory2/file3.txt


(c) Steven Scholnick <scholnicks@gmail.com>
The rename source code is published under a MIT license. See http://www.scholnick.net/license.txt for details.
"""

from __future__ import print_function
import os, sys, re, random

def main(files):
    """Main Method"""
    if arguments['--verbose']:
        print("Renaming: {0}\n".format(", ".join(files)))

    if arguments['--random']:
        randomizeFiles(files)
    elif arguments['--merge']:
        mergeFiles(files)
    else:
        for fileName in files:
            performRenameOperation(fileName)

    sys.exit(0)


def randomizeFiles(files):
    '''randomly shuffles a list of files with the same extension'''

    # determine the extension
    extension = calculateExtension(files)

    # do the shuffle
    random.shuffle(files)

    prefix = arguments['--prepend'] if arguments['--prepend'] else 'file'

    # rename the files in numeric order
    for (index,filename) in enumerate(files,1):
        new_file_name = os.path.join(os.path.dirname(filename),'{prefix}_{num:04d}'.format(prefix=prefix,num=index) + extension)
        rename_file(filename,new_file_name)


def mergeFiles(files):
    '''reorders a set of files in order in a target directory'''

    if not arguments['--directory']:
        raise SystemExit("--directory must be set")

    # determine the extension
    extension = calculateExtension(files)

    prefix = arguments['--prepend'] if arguments['--prepend'] else 'file'

    # rename the files in command line specified order
    for (index,filename) in enumerate(files,1):
        new_file_name = os.path.join(arguments['--directory'],'{prefix}_{num:04d}'.format(prefix=prefix,num=index) + extension)
        rename_file(filename,new_file_name)


def calculateExtension(files):
    '''determines the extension'''
    extensions = set((os.path.splitext(f)[1].lower() for f in files))
    if len(extensions) > 1:
        raise SystemExit("Only one extension allowed. Found: {0}".format(", ".join(extensions)))

    return extensions.pop()


def performRenameOperation(fileName):
    """Performs a renaming operation on the specififed filename"""
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
        rename_file(fileName,newFileName)


def rename_file(old_file_name, new_file_name):
    """Performs the actual file rename"""
    if arguments['--verbose']:
        print("Renaming {0} to {1}".format(old_file_name,new_file_name))

    if not arguments['--test']:
        os.rename(old_file_name,new_file_name)


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
    arguments = docopt(__doc__, version='1.1.1')

    if arguments['--test']:
        arguments['--verbose'] = True

    main(arguments['<files>'])

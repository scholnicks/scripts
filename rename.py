#!/usr/bin/env python -B
# -*- coding: utf-8 -*-

"""
rename: Renames files in powerful ways

Usage:
    rename [options] <files> ...

Options:
    -a, --append=<suffix>                      Suffix to be appended
    -d, --delimiter=<delimiter>                Specifies the delimiter for fixing numerical filenames
    --directory=<directory>                    Destination directory
    -f, --fix=<maximum number of digits>       Fixes numerical file names
    -h, --help                                 Show this help screen
    -l, --lower                                Translates the filenames to lowercase
    -o, --order                                Take any input files and rename them in numerical order (01 - File.mp3, 02 - File.mp3, etc)
    -p, --prepend=<prefix>                     Prefix to be prepended
    -r, --remove=<pattern>                     Pattern to be removed, can be a regex
    --random                                   Randomizes the files (--prepend can be used to specify the prefix, defaults to "file")
    --merge                                    Merges the files in order specfied on command line (See below for details/examples)
    -s, --substitute=<substitution pattern>    Substitutes a pattern (old/new, old can be a regex)
    -t, --test                                 Test mode (Just prints the rename operations)
    -v, --verbose                              Verbose mode
    --version                                  Prints the version

Using merge

merge requires a directory to be specified. prepend (defaults to file) is used for the base name for the merged files.
For example to merge files from two different directories into the current directory:

rename --merge --directory=. directory1/* directory2/*

Input Files: directory1/file1.txt directory1/file2.txt directory2/file1.txt
Results: ./file_0001.txt ./file_0002.txt ./file_0003.txt

where file_0003.txt is directory2/file3.txt

(c) Steven Scholnick <scholnicks@gmail.com>
The rename source code is published under a MIT license. See https://scholnick.net/license.txt for details.
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
    elif arguments['--order']:
        orderFiles(files)
    else:
        for fileName in files:
            performRenameOperation(fileName)

    sys.exit(0)

def orderFiles(files):
    '''Orders the files'''
    filename_template = r'{num:02d} - {filename}' if len(files) < 100 else r'{num:04d} - {filename}'

    for (index,current_file_path) in enumerate(sorted(files),1):
        new_file_path = os.path.join(
            os.path.dirname(current_file_path),
            filename_template.format(num=index,filename=os.path.basename(current_file_path))
        )
        rename_file(current_file_path,new_file_path)


def randomizeFiles(files):
    '''randomly shuffles a list of files with the same extension'''

    # determine the extension
    extension = calculateExtension(files)

    # do the shuffle
    random.shuffle(files)

    prefix = arguments['--prepend'] if arguments['--prepend'] else 'file'

    # rename the files in numeric order
    for (index,filename) in enumerate(files,1):
        new_file_name = os.path.join(os.path.dirname(filename),'{prefix}_{num:04d}{extension}'.format(prefix=prefix,num=index,extension=extension))
        rename_file(filename,new_file_name)


def mergeFiles(files):
    '''reorders a set of files in order in a target directory'''

    if not arguments['--directory']:
        raise SystemExit("--directory must be set")

    # determine the extension
    extension = calculateExtension(files)

    prefix = arguments['--prepend'] if arguments['--prepend'] else 'file'

    # rename the files in argument specified order
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
        if not (arguments['--delimiter'] and arguments['--fix']):
            raise SystemExit("--delimiter and --fix are both required")
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
        raise SystemExit("rename: Illegal substitute pattern. Pattern must be old/new")


def fixNumbers(fileName,delimiter,numberLength):
    """Fixes the numeric part of a filename"""
    if delimiter not in fileName:
        return fileName

    (base,extension) = os.path.splitext(fileName)
    (prefix,number)  = base.split(delimiter,2)

    sequenceValue = number

    for i in range(len(number),int(numberLength)):
        sequenceValue = "0" + sequenceValue

    return prefix + delimiter + sequenceValue + extension


if __name__ == '__main__':
    from docopt import docopt
    arguments = docopt(__doc__, version='1.2.0')

    if arguments['--test']:
        arguments['--verbose'] = True

    main(arguments['<files>'])

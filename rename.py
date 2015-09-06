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
    --random                                   Randomize the files (--prepend can be used to specify the prefix, defaults to "file")
    -s, --substitute=<substitution pattern>    Substitutes a pattern (old/new)
    -t, --test                                 Test mode (Just prints the renames)
    -v, --verbose                              Verbose Mode
    --version                                  Prints the version

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
        random_files(files)
    else:
        for fileName in files:
            renameFile(fileName)

    sys.exit(0)

def random_files(files):
    '''randomly shuffles a list of files with the same extension'''

    # determine the extension
    extensions = set((os.path.splitext(f)[1].lower() for f in files))
    if len(extensions) > 1:
        print("Only one extension allowed for randomization. Found: {0}".format(", ".join(extensions)),file=sys.stderr)
        sys.exit(1)

    extension = list(extensions)[0]

    # do the shuffle
    random.shuffle(files)

    prefix = arguments['--prepend'] if arguments['--prepend'] else 'file'

    # rename the files in numeric order
    for f in enumerate(files,1):
        new_file_name = os.path.join(os.path.dirname(f[1]),'{prefix}_{num:04d}'.format(prefix=prefix,num=f[0]) + extension)
        rename_file(f[1],new_file_name)


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
    arguments = docopt(__doc__, version='1.1.0')

    if arguments['--test']:
        arguments['--verbose'] = True

    main(arguments['<files>'])

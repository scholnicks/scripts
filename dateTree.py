#!/usr/bin/env python -B
# -*- coding: utf-8 -*-

"""
dateTree: Creates a tree of pictures separated into date directories
          All duplicates will be removed.
          All filenames will be converted to all lowercase
          Only JPEGs will be copied

Usage:
    dateTree [--quiet] <starting-directory> <destination-directory>

Requires external modules that can be installed from PyPI with:
    pip install pillow

Options:
    -h, --help     Show this help screen
    -q, --quiet    Quiet Mode
    --version      Prints the version

(c) Steven Scholnick <scholnicks@gmail.com>

The dateTree source code is published under a MIT license. See https://scholnick.nett/license.txt for details.
"""

from __future__ import print_function
import os, sys, shutil
import datetime

from PIL import Image
from PIL.ExifTags import TAGS

DATE_FORMAT = '%Y-%m-%d'


def main(startingDirectory):
    try:
        pictureFiles    = getPictureFiles(os.path.abspath(startingDirectory))
        destinationRoot = createDirectory(arguments['<destination-directory>'])

        for p in pictureFiles:
            if not arguments['--quiet']:
                print("Processing {0}".format(p))

            directoryName = getDate(p)
            destinationDirectory = createDirectory(os.path.join(destinationRoot,directoryName), True)
            shutil.copyfile(p, os.path.join(destinationDirectory,os.path.basename(p)))
    except KeyboardInterrupt:
        print()

    sys.exit(0)


def getPictureFiles(sourceDirectory):
    """ Returns a list of all of the JPEGs for the sourceDirectory and any sub-directories """
    pictureFiles = []
    for root, dirs, files in os.walk(sourceDirectory):
        pictureFiles += [os.path.join(root,f) for f in files if f.lower().endswith(".jpg")]

    return pictureFiles


def getDate(filePath):
    """ Returns the date for the specified file """
    # first try reading the creation date from the image itself
    for (k,v) in Image.open(filePath)._getexif().iteritems():
        if TAGS[k] == 'DateTimeOriginal':
            dateTime = datetime.datetime.strptime(v,'%Y:%m:%d %H:%M:%S')
            return dateTime.strftime(DATE_FORMAT)

    # unable to get the date from the image, just return the file's modification date
    return datetime.datetime.fromtimestamp(os.path.getmtime(filePath)).strftime(DATE_FORMAT)


def createDirectory(path,allowExisting=False):
    try:
        os.mkdir(path)
        os.chmod(path,0o755)
        return os.path.abspath(path)
    except OSError:
        if allowExisting:
            return os.path.abspath(path)
        else:
            raise

if __name__ == '__main__':
    from docopt import docopt
    arguments = docopt(__doc__, version='1.0.1')
    main(arguments['<starting-directory>'])

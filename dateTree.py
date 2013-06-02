#!/usr/bin/python -BO
"""
dateTree:  Creates a tree of pictures separated into date directories
           All duplicates will be removed.
           All filenames will be converted to all lowercase
           Only JPEGs will be copied

Requires external modules that can be installed from PyPI with:
    pip install pillow

(c) Steven Scholnick <steve@scholnick.net>

The dateTree source code is published under version 2.1 of the GNU Lesser General Public License (LGPL).
 
In brief, this means there's no warranty and you can do anything you like with it.
However, if you make changes to dateTree and redistribute those changes, 
then you must publish your modified version under the LGPL. 
"""

from __future__ import print_function
import os, sys, re, shutil
import datetime

from PIL import Image
from PIL.ExifTags import TAGS

DATE_FORMAT = '%Y-%m-%d'

def main():
    try:
        pictureFiles    = getPictureFiles(os.path.abspath(args[0]))
        destinationRoot = createDirectory(options.destination)
        
        for p in pictureFiles:
            if not options.quiet: 
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
    try:
        return getCreationDate(filePath)
    except TypeError:
        return getModificationTime(filePath)


def getCreationDate(filePath):
    """ Returns the creation date for the image. Read from the photo's EXIF """
    for (k,v) in Image.open(filePath)._getexif().iteritems():
        if TAGS[k] == 'DateTimeOriginal':
            dateTime = datetime.datetime.strptime(v,'%Y:%m:%d %H:%M:%S')
            return dateTime.strftime(DATE_FORMAT)
    
    raise TypeError("Unable to read the DateTimeOriginal")


def getModificationTime(filePath):
    """ Returns the modification date for the file """
    datetime.datetime.fromtimestamp(os.path.getmtime(filePath)).strftime(DATE_FORMAT)


def createDirectory(path,allowExisting=False):
    try:
        os.mkdir(path)
        os.chmod(path,0755)
        return os.path.abspath(path)
    except OSError:
        if allowExisting:
            return os.path.abspath(path)
        else:
            raise

if __name__ == '__main__':
    from optparse import OptionParser
    
    parser = OptionParser(usage='%prog [options] Input_Directory')
    parser.add_option('-d','--destination',dest="destination", type='string', help='Sets the folder destination [REQUIRED]')
    parser.add_option('-q','--quiet',dest="quiet", action="store_true", help='Toggles quiet mode')

    options,args = parser.parse_args()

    if len(args) < 1 or not options.destination:
        parser.print_help()
        sys.exit(1)

    main()

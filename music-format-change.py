#!/usr/bin/env python -B
# -*- coding: utf-8 -*-

"""
music-format-change: Music Format Changer

Usage:
   music-format-change [options] <files> ...

Options:
    -a, --aiff          Convert to AIFF (default)
    --album=<album>     Album
    --artist=<artist>   Artist
    -d, --delete        Delete the input file after conversion
    -h, --help          Show this help screen
    -3, --mp3           Convert to MP3
    -q, --quiet         Quiet mode
    -w, --wav           Convert to WAV format
    -v, --version       Prints the version

(c) Steven Scholnick <scholnicks@gmail.com>

The music-format-change source code is published under a MIT license. See http://www.scholnick.net/license.txt for details.
"""

import sys
import os
import re

ENCODERS = {
    'aiff': '/usr/local/bin/sox -q',
    'mp3':  '/usr/local/bin/lame --nohist --silent',
    'wav':  '/usr/local/bin/sox -q'
}

VERBOSE_MODE = '{0} "{1}" "{2}"'
QUIET_MODE   = '{0} "{1}" "{2}" 1>/dev/null 2>&1'

EYED3_COMMAND_LINE = 'eyed3 --quiet --title "{}" --album "{}" --artist "{}" --album-artist "{}" --track {} --track-total {} "{}" 1>/dev/null 2>&1'

def main(files):
    '''Main method'''

    convertableFiles = [f for f in files if f.endswith(tuple(ENCODERS.keys()))]
    for index,musicFile in enumerate(convertableFiles,1):
        destinationFile = convertFile(musicFile)
        print(destinationFile,destinationFile.endswith(".mp3"))
        if destinationFile.endswith(".mp3"):
            addMP3Tags(destinationFile,index,len(convertableFiles))

    sys.exit(0)


def filename(filenameWithExtension):
    return os.path.splitext(filenameWithExtension)[0]


def convertFile(musicFile):
    '''Converts the musicFile to the destination format'''
    extension = getDestinationFormat()
    destinationFilename = filename(musicFile) + '.' + extension
    if not arguments['--quiet']:
        print(f"Converting {musicFile} to {destinationFilename}")

    command = QUIET_MODE if arguments['--quiet'] else VERBOSE_MODE
    os.system(command.format(ENCODERS[extension],musicFile,destinationFilename))

    if arguments['--delete']:
        os.unlink(musicFile)

    return destinationFilename


def addMP3Tags(destinationFile,index,numberOfFiles):
    match = re.match(r'^[0-9]+ - (.*)\.mp3$',destinationFile)

    os.system(EYED3_COMMAND_LINE.format(
        match.groups()[0] if match else filename(destinationFile),
        arguments['--album'],
        arguments['--artist'],
        arguments['--artist'],
        index,
        numberOfFiles,
        destinationFile
    ))

def getDestinationFormat():
    '''Returns the destination format based on the command line arguments'''
    if arguments['--wav']:
        return 'wav'
    elif arguments['--mp3']:
        return 'mp3'
    else:
        return 'aiff'


if __name__ == '__main__':
    from docopt import docopt
    arguments = docopt(__doc__, version='1.0.0')
    main(arguments['<files>'])

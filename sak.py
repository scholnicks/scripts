#!/usr/bin/env python -B
# -*- coding: utf-8 -*-
#
# sak uses several external tools: sox, ffmpeg, lame, eyeD3.
# On macOS, these can all easily be installed using homebrew.
#
# (c) Steven Scholnick <scholnicks@gmail.com>
# The sak source code is published under a MIT license.

"""
sak: Song Army Knife, manipulate song files in several ways

Usage:
    sak [options] <files>...

Options:
    -a, --aiff              Convert to AIFF
    --album=<album>         MP3 Album Tag Info
    --artist=<artist>       MP3 Artist Tag Info
    -d, --disc=<discNumber> Disk number [default: 0]
    -k, --keep              Keep the input file after conversion
    -h, --help              Show this help screen
    -3, --mp3               Convert to MP3 (default)
    -q, --quiet             Quiet mode
    -t, --tag               Add the MP3 Tags
    -w, --wav               Convert to WAV format
    -v, --version           Prints the version
"""

import sys
import os
import re
import lameenc


FFMPEG_COMMAND       = 'ffmpeg -i "{}" -acodec libmp3lame -ab 256k "{}" 1>/dev/null 2>&1'
CONVERT_COMMAND_LINE = '{} "{}" "{}" 1>/dev/null 2>&1'
EYED3_COMMAND_LINE   = 'eyed3 --quiet --title "{}" --album "{}" --artist "{}" --album-artist "{}" --disc-num {} --track {} --track-total {} "{}" 1>/dev/null 2>&1'
MP3_EXTENSION        = 'mp3'

ENCODERS = {
    'aiff': '/usr/local/bin/sox -q',
    'm4a':  FFMPEG_COMMAND,
    'mp3':  '/usr/local/bin/lame --nohist --silent',
    'opus':  FFMPEG_COMMAND,
    'wav':  '/usr/local/bin/sox -q'
}

arguments = None        # quiet VS Code's linter

def main(files):
    '''Main method'''

    destinationFormat = getDestinationFormat()
    inputFormat       = calculateInputFormat(files)

    if inputFormat == MP3_EXTENSION and destinationFormat == MP3_EXTENSION:
        arguments['--tag'] = True

    if destinationFormat == MP3_EXTENSION and not (arguments['--album'] and arguments['--artist']):
        raise SystemExit('--album and --artist are required with mp3 as the destination format')

    convertableFiles = [f for f in files if f.endswith(tuple(ENCODERS.keys()))]
    for index,musicFile in enumerate(convertableFiles,1):
        if arguments['--tag']:
            destinationFile = musicFile
        else:
            destinationFile = convertFile(musicFile,inputFormat)

        if destinationFile.endswith(MP3_EXTENSION):
            addMP3Tags(destinationFile,index,len(convertableFiles))

    sys.exit(0)


def calculateInputFormat(files):
    '''determines the extension'''
    extensions = set((os.path.splitext(f)[1].lower() for f in files))
    if len(extensions) > 1:
        raise SystemExit("Only one type of input file allowed. Found: {0}".format(", ".join(extensions)))

    return extensions.pop()[1:]


def convertFile(musicFile,inputFormat):
    '''Converts the musicFile to the destination format'''
    extension           = getDestinationFormat()
    destinationFilename = filename(musicFile) + '.' + extension
    if not arguments['--quiet']:
        print(f"Converting {musicFile} to {destinationFilename}")

    if inputFormat == 'm4a' or inputFormat == 'opus':
        ret = os.system(FFMPEG_COMMAND.format(musicFile,destinationFilename))
    else:
        ret = os.system(CONVERT_COMMAND_LINE.format(ENCODERS[extension],musicFile,destinationFilename))

    if ret != 0:
        print(f"*** Unable to convert {musicFile}. Keeping original. ***")
    else:
        if not arguments['--keep']:
            os.unlink(musicFile)

    return destinationFilename


def filename(filenameWithExtension):
    '''Returns the filename without the extension'''
    return os.path.splitext(filenameWithExtension)[0]


def addMP3Tags(destinationFile,index,numberOfFiles):
    '''Adds the MP3 Tags using the eyeD3 command line tool'''
    match = re.match(r'^[0-9]+ - (.*)\.mp3$',destinationFile)

    os.system(EYED3_COMMAND_LINE.format(
        match.groups()[0] if match else filename(destinationFile),
        arguments['--album'] if arguments['--album'] else '',
        arguments['--artist'] if arguments['--artist'] else '',
        arguments['--artist'] if arguments['--artist'] else '',
        arguments['--disc'] if arguments['--disc'] else 0,
        index,
        numberOfFiles,
        destinationFile
    ))


def getDestinationFormat():
    '''Returns the destination format based on the command line arguments'''
    if arguments['--wav']:
        return 'wav'
    elif arguments['--aiff']:
        return 'aiff'
    else:
        return MP3_EXTENSION


if __name__ == '__main__':
    from docopt import docopt
    arguments = docopt(__doc__, version='1.0.0')
    main(arguments['<files>'])

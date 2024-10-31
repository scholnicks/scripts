#!/usr/bin/env python -B
# vi: set syntax=python ts=4 sw=4 sts=4 et ff=unix ai si :
#
# mp3-tag-handler uses an external tool, eyeD3.
#
# (c) Steven Scholnick <scholnicks@gmail.com>
# The mp3-tag-handler source code is published under a MIT license.

"""
mp3-tag-handler: Update MP3 tags easily

Usage:
    mp3-tag-handler [options] <files>...

Options:
    --album=<album>         MP3 Album Tag Info
    --artist=<artist>       MP3 Artist Tag Info
    -d, --disc=<discNumber> Disk number [default: 0]
    --debug                 Debug option
    -h, --help              Show this help screen
    -s, --silent            Silent mode
    -v, --version           Prints the version
"""

import sys
import os
import re

def main(files):
    """Main method"""

    if len(files) == 0:
        sys.exit(0)

    if not arguments['--album'] and arguments['--artist']:
        raise SystemExit('--album and --artist are required')

    for index,musicFile in enumerate(files,1):
        addMP3Tags(musicFile,index,len(files))

    sys.exit(0)


def addMP3Tags(destinationFile,index,numberOfFiles):
    """Adds the MP3 Tags using the eyeD3 command line tool"""
    match = re.match(r'^[0-9]+ - (.*)\.mp3$',destinationFile)

    ret = os.system('eyed3 --quiet --title "{}" --album "{}" --artist "{}" --album-artist "{}" --disc-num {} --track {} --track-total {} "{}" 1>/dev/null 2>&1'.format(
        match.groups()[0] if match else filename(destinationFile),
        arguments['--album'] if arguments['--album'] else '',
        arguments['--artist'] if arguments['--artist'] else '',
        arguments['--artist'] if arguments['--artist'] else '',
        arguments['--disc'] if arguments['--disc'] else 0,
        index,
        numberOfFiles,
        destinationFile
    ))
    if ret != 0:
        if not arguments['--quiet']: print(f"Unable to apply MP3 IDs to {destinationFile}",file=sys.stderr)


def filename(filenameWithExtension):
    """Returns the filename without the extension"""
    return os.path.splitext(filenameWithExtension)[0]


if __name__ == '__main__':
    from docopt import docopt
    arguments = docopt(__doc__, version='3.0.0')
    main(arguments['<files>'])

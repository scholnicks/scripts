#!/usr/bin/env python -B
# -*- coding: utf-8 -*-

"""
album:  Creates a album of photos complete with thumbnails. ImageMagick's convert does the hard work.

Usage:
    album [options] <title> <source-directory>

Options:
   -h, --help                         show this help message and exit
   -d, --destination=<destination>    Sets the folder destination, [default: photos]
   -m, --max=<max number of photos>   Sets the maximum number of photos. [default: 1000]
   -o, --overwrite                    Overwrites the destination directory with the new set of photos.
   -p, --page=<photos per page>       Sets the maximum number of photos per page, [default: 48]
   -q, --quiet                        Toggles quiet mode
   -v, --verbose                      Toggles verbose mode
   --version                          Prints the version

(c) Steven Scholnick <scholnicks@gmail.com>

The album source code is published under a MIT license. See http://www.scholnick.net/license.txt for details.

"""

from __future__ import print_function
import os, sys, re, math, subprocess, shutil
from string import Template

#numberOfPages = 0

def main(startingDirectory):
    destinationDirectory = arguments['--destination']

    if os.path.exists(destinationDirectory):
        if arguments['--overwrite']:
            shutil.rmtree(destinationDirectory)
        else:
            raise SystemExit("{0} directory exists. Will not overwrite, --overwrite is not specified.".format(destinationDirectory))

    createDirectory(destinationDirectory)

    pictureFiles = []
    for root, dirs, files in os.walk(os.path.abspath(startingDirectory)):
        pictureFiles += [ImageFile(os.path.join(root,f)) for f in files if f.lower().endswith(".jpg") or f.lower().endswith(".png")]

    pageNumber    = 1
    numberOfPages = int( math.ceil(float(len(pictureFiles)) / float(arguments['--page']) ) )

    (workingDirectory,indexFilePointer) = openIndexPage(pageNumber,numberOfPages)

    if arguments['--verbose']:
        print("Number of photos = {0}, number of pages = {1}, output directory = {2}"
              .format(len(pictureFiles), numberOfPages, destinationDirectory))

    for photoIndex in xrange(0,len(pictureFiles)):
        imageFile = pictureFiles[photoIndex]
        imageFile.index = photoIndex
        calculateDimensions(imageFile)

        if photoIndex > 0 and (photoIndex % int(arguments['--page'])) == 0:
            closeIndexPage(pageNumber,numberOfPages,indexFilePointer)
            pageNumber += 1
            (workingDirectory,indexFilePointer) = openIndexPage(pageNumber,numberOfPages)

        convertImage(imageFile,workingDirectory)

        print('    <li><a class="th radius" href="{0}.html"><img src="thumbnails/{1}" width="{2}" height="{3}"></a></li>'
              .format(photoIndex + 1,
                      os.path.basename(imageFile.path),
                      imageFile.thumbnailWidth,
                      imageFile.thumbnailHeight)
              ,file=indexFilePointer)

        createIndividualHTMLFile(workingDirectory,imageFile,len(pictureFiles),pageNumber)

    closeIndexPage(pageNumber,numberOfPages,indexFilePointer)
    sys.exit(0)


def calculateDimensions(photoFile):
    """Calculates the dimensions of the photo by calling the ImageMagick standalone app, identify"""
    process = subprocess.Popen(['identify',photoFile.path],stdout=subprocess.PIPE)
    (photoFile.width,photoFile.height) = re.search(r' (\d+)x(\d+) ',process.stdout.readline()).groups()


def openIndexPage(pageNumber,numberOfPages):
    """prints out the opening of an index page and returns the current working directory and the file pointer"""
    workingDirectory = createDirectory(arguments['--destination'] + '/page' +  str(pageNumber))
    indexFilePointer = open(os.path.join(workingDirectory,"index.html"),"w")

    print( getIndexPageHeader(pageNumber,numberOfPages), file=indexFilePointer )
    print( getPaginationSection(pageNumber,numberOfPages), file=indexFilePointer)
    print( '<div class="row">\n<ul class="large-block-grid-8 medium-block-grid-6 small-block-grid-2">', file=indexFilePointer)

    return (workingDirectory,indexFilePointer)


def closeIndexPage(pageNumber,numberOfPages,indexFilePointer):
    """prints out the closing part of an index page"""
    print( '</ul>\n</div>\n', file=indexFilePointer)
    print( getPaginationSection(pageNumber,numberOfPages), file=indexFilePointer)
    print( getIndexPageFooter(pageNumber,numberOfPages), file=indexFilePointer)
    indexFilePointer.close()
    os.chmod(indexFilePointer.name,0644)


def convertImage(imageFile,workingDirectory):
    """Creates both the standard and thumbnail images in the proper directories with the correct permissions"""
    if not arguments['--quiet']: print("Processing {}".format(imageFile))

    imagesDirectory     = createDirectory(workingDirectory + '/images',True)
    thumbnailsDirectory = createDirectory(workingDirectory + '/thumbnails',True)

    createStandardImage(imagesDirectory,imageFile)
    createThumbnailImage(thumbnailsDirectory,imageFile)


def createStandardImage(imagesDirectory,imageFile):
    """Creates the standard image in the proper directory with the correct permissions"""
    outFile = os.path.join(imagesDirectory, os.path.basename(imageFile))
    createImage(imageFile,outFile,imageFile.scaledDimension)


def createThumbnailImage(imagesDirectory,imageFile):
    """Creates the thumbnail image in the proper directory with the correct permissions"""
    outFile = os.path.join(imagesDirectory, os.path.basename(imageFile))
    createImage(imageFile,outFile,imageFile.thumbnailDimension)


def createImage(inFile,outFile,scale):
    """performs the actual image file creation by using the ImageMagick standalone app, convert. The file is then optimized with jpegtran or optipng"""
    cmd = "convert {0} -size {1} -quality 100 -scale {1} -strip -auto-orient {2}"
    if subprocess.call(cmd.format(inFile,scale,outFile),shell=True) != 0:
        raise StandardError('Unable to scale the image with convert')

    compressionCommmand = None

    if inFile.endswith(".jpg"):
        compressionCommmand = 'jpegtran -copy none -optimize -perfect -outfile {0} {0}'
    elif inFile.endswith(".png"):
        compressionCommmand = 'optipng -quiet -o0 -strip all -out {0} {0}'

    if compressionCommmand:
        if subprocess.call(compressionCommmand.format(outFile),shell=True) != 0:
            raise StandardError('Unable to optimize the image jpegtran')

    os.chmod(outFile,0644)


def createDirectory(path,allowExisting=False):
    """Creates a new directory. If the directory already exists, an error may be raised (based on allowExisting)"""
    try:
        os.mkdir(path)
        os.chmod(path,0755)
        return os.path.abspath(path)
    except OSError:
        if allowExisting:
            return os.path.abspath(path)
        else:
            raise


def getPaginationSection(pageNumber,numberOfPages):
    """Returns the pagination section for the index files"""
    if numberOfPages == 1:
        return ''

    html = '<div class="row">\n<ul class="pagination right">\n'

    if pageNumber == 1:
        html += '    <li class="arrow unavailable"><a href="#">&laquo;</a></li>\n'
    else:
        html += '    <li><a href="../page{0}/">&laquo;</a></li>\n'.format(pageNumber-1)

    for number in xrange(1,numberOfPages+1):
        html += '    <li{0}><a href="../page{1}/">{1}</a></li>\n'.format(' class="current"' if number == pageNumber else '', number)

    if pageNumber == numberOfPages:
        html += '    <li class="unavailable"><a href="#">&raquo;</a></li>\n'
    else:
        html += '    <li class="arrow"><a href="../page{0}/">&raquo;</a></li>\n'.format(pageNumber+1)

    html += '</ul>\n</div>\n'

    return html


def getIndexPageFooter(pageNumber,numberOfPages):
    """Returns the footer for the index pages"""
    return r"""
<!--#include virtual="/includes/bottom-scripts-foundation.html" -->
<script type="text/javascript">
    $(function() {
        $('#nav-pictures').addClass('active');
    });
</script>

</body>
</html>
"""


def getIndexPageHeader(pageNumber,numberOfPages):
    pageTitle = arguments['<title>'] if numberOfPages == 1 else "{0}: Page {1}".format(arguments['<title>'],pageNumber)

    """Returns the header for the index pages"""
    return '''<!doctype html>
<html class="no-js" lang="en">
<head>
    <title>{0}</title>
    <meta charset="utf-8">
    <link rel="shortcut icon" href="/favicon.ico" type="image/x-icon">
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=0">
    <link rel="stylesheet" href="/foundation/css/foundation.min.css">
    <link rel="stylesheet" href="/css/base-foundation.css">
</head>
<body>

<!--#include virtual="/includes/top-navbar-foundation.html" -->

<div class="row">
   <div class="large-12 columns text-center"><h2>{0}</h2></div>
</div>
'''.format(pageTitle)


SINGLE_PAGE_TEMPLATE = r'''<!doctype html>
<html class="no-js" lang="en">
<head>
    <meta charset="utf-8">
    <title>$pictureSetTitle - Photo $index</title>
    <link rel="shortcut icon" href="/favicon.ico" type="image/x-icon">
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=0">
    <link rel="stylesheet" href="/foundation/css/foundation.min.css">
</head>
<body>

<!--#include virtual="/includes/top-navbar-foundation.html" -->

<div class="row text-center">
    $linkLine
</div>

<div class="row text-center">
    <a href="index.html" title="Click on image to return to index"><img src="images/$filename" alt="$index of $numberOfPictures" height="$height" width="$width"></a>
    <p>$index of $numberOfPictures photos</p>
</div>

<!--#include virtual="/includes/bottom-scripts-foundation.html" -->
<script src="/js/photo.js"></script>
<script type="text/javascript">
function previousPhoto() { window.location = "$lastPhotoFile"; }
function nextPhoto() { window.location = "$nextPhotoFile"; }
$$(function() {
    $$('#nav-pictures').addClass('active');
});
</script>

</body>
</html>
'''

def createIndividualHTMLFile(workingDirectory,imageFile,numberOfPhotos,pageNumber):
    """Creates an individual HTML file"""
    index = imageFile.index + 1

    prev = index - 1
    next = index + 1

    prevHTML = ''
    nextHTML = ''

    photosPerPage = int(arguments['--page'])

    if prev == 0:
        prevHTML = 'index.html'
    else:
        if (prev % photosPerPage) == 0:
            prevHTML = '../page{0}/{1}.html'.format((pageNumber-1),prev)
        else:
            prevHTML = str(prev) + '.html'

    if next > numberOfPhotos:
        nextHTML = 'index.html'
    else:
        if (index % photosPerPage) == 0:
            nextHTML = '../page{0}/{1}.html'.format((pageNumber+1),next)
        else:
            nextHTML = str(next) + ".html"

    linkLine = '''    <a title="Previous Photo" href="{0}"><img src="/images/reverse.png" width="32" height="32" alt="<-"></a>
    <a title="Return to Index" href="index.html"><img src="/images/stop.png" width="32" height="32" alt="||"></a>
    <a title="Next Photo" href="{1}"><img src="/images/forward.png" width="32" height="32" alt="->"></a>'''.format(prevHTML,nextHTML)

    html = Template(SINGLE_PAGE_TEMPLATE).substitute(
       pictureSetTitle=arguments['<title>'],
       index=index,
       numberOfPictures=numberOfPhotos,
       lastPhotoFile=prevHTML,
       nextPhotoFile=nextHTML,
       linkLine=linkLine,
       filename=os.path.basename(imageFile.path),
       height=imageFile.scaledHeight,
       width=imageFile.scaledWidth
    )

    filePath = os.path.join(workingDirectory,str(index) + ".html")
    with open(filePath,'w') as htmlFile:
        print(html,file=htmlFile)

    os.chmod(filePath,0644)


class ImageFile(object):
    """Class that holds the image path and the image's dimensions"""
    def __init__(self,path):
        self.path = path

    def isPortrait(self):
        return self.width > self.height

    # consider making another class/named tuple to hold height and width

    @property
    def thumbnailWidth(self):
        return '128' if self.isPortrait() else '96'

    @property
    def thumbnailHeight(self):
        return '96' if self.isPortrait() else '128'

    @property
    def thumbnailDimension(self):
        return '{0}x{1}'.format(self.thumbnailWidth,self.thumbnailHeight)

    @property
    def scaledWidth(self):
        return '640' if self.isPortrait() else '480'

    @property
    def scaledHeight(self):
        return '480' if self.isPortrait() else '640'

    @property
    def scaledDimension(self):
        return '{0}x{1}'.format(self.scaledWidth,self.scaledHeight)

    # duck typing methods. this class will be used in place
    # of a str in several spots

    def __str__(self):
        return self.path

    def rfind(self,target):
        return self.path.rfind(target)

    def __getitem__(self,key):
        return self.path.__getitem__(key)

    def endswith(self,suffix):
        return self.path.endswith(suffix)



if __name__ == '__main__':
    from docopt import docopt
    arguments = docopt(__doc__, version='2.1.0')

    if arguments['--verbose']:
        arguments['--quiet'] = False

    main(arguments['<source-directory>'])

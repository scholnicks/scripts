#!/usr/bin/env python -B
# -*- coding: utf-8 -*-

"""
album:  Creates a album of photos complete with thumbnails.

Usage:
    album [options] <title> <source-directory>

Options:
   -c, --cover=<cover>                Sets the cover photo for social media embedded links [default: https://scholnick.net/images/opengraph-image.jpg]
   -h, --help                         Shows this help message and exits
   -d, --destination=<destination>    Sets the folder destination, [default: photos]
   -l, --leave                        Do not convert the photos. Leave them as is.
   -m, --max=<max number of photos>   Sets the maximum number of photos. [default: 1000]
   -o, --overwrite                    Overwrites the destination directory with the new set of photos.
   -p, --page=<photos per page>       Sets the maximum number of photos per page, [default: 48]
   -q, --quiet                        Toggles quiet mode
   -u, --url=<url>                    URL for the social media embedded links [default: https://scholnick.net]
   -v, --verbose                      Toggles verbose mode
   --version                          Prints the version

(c) Steven Scholnick <scholnicks@gmail.com>

The album source code is published under a MIT license. See https://scholnick.net/license.txt for details.

"""

from __future__ import print_function
from PIL import Image
import os, sys, math, shutil
from string import Template


def main(startingDirectory):
    destinationDirectory = arguments['--destination']

    if os.path.exists(destinationDirectory):
        if arguments['--overwrite']:
            shutil.rmtree(destinationDirectory)
        else:
            raise SystemExit(f"{destinationDirectory} directory exists. Will not overwrite, --overwrite is not specified.")

    createDirectory(destinationDirectory)

    pictureFiles = []
    for root, dirs, files in os.walk(os.path.abspath(startingDirectory)):
        pictureFiles += [ImageFile(os.path.join(root,f)) for f in files if f.lower().endswith(".jpg")]

    pageNumber    = 1
    numberOfPages = int(math.ceil(float(len(pictureFiles)) / float(arguments['--page'])))

    (workingDirectory,indexFilePointer) = openIndexPage(pageNumber,numberOfPages)

    if arguments['--verbose']:
        print("Number of photos = {0}, number of pages = {1}, output directory = {2}"
              .format(len(pictureFiles), numberOfPages, destinationDirectory))


    IMAGE_TEMPLATE = '''    <div class="col-lg-2 col-sm-6 col-md-3">
        <a class="thumbnail" href="{0}.html"><img src="images/{1}"></a>
    </div>
'''

    for photoIndex in range(0,len(pictureFiles)):
        imageFile = pictureFiles[photoIndex]
        imageFile.index = photoIndex
        calculateDimensions(imageFile)

        if photoIndex > 0 and (photoIndex % int(arguments['--page'])) == 0:
            closeIndexPage(pageNumber,numberOfPages,indexFilePointer)
            pageNumber += 1
            (workingDirectory,indexFilePointer) = openIndexPage(pageNumber,numberOfPages)

        convertImage(imageFile,workingDirectory)
        print(IMAGE_TEMPLATE.format(photoIndex + 1,os.path.basename(imageFile).lower()),file=indexFilePointer)
        createIndividualHTMLFile(workingDirectory,imageFile,len(pictureFiles),pageNumber)

        if photoIndex == int(arguments['--max'])-1:
            break

    closeIndexPage(pageNumber,numberOfPages,indexFilePointer)
    sys.exit(0)


def calculateDimensions(photoFile):
    """Calculates the dimensions of the photo"""
    image = Image.open(photoFile.path)
    (photoFile.width,photoFile.height) = image.size


def openIndexPage(pageNumber,numberOfPages):
    """prints out the opening of an index page and returns the current working directory and the file pointer"""
    workingDirectory = createDirectory(arguments['--destination'] + '/page' +  str(pageNumber))
    indexFilePointer = open(os.path.join(workingDirectory,"index.html"),"w")

    print(getIndexPageHeader(pageNumber,numberOfPages), file=indexFilePointer )
    print(getPaginationSection(pageNumber,numberOfPages), file=indexFilePointer)
    print('<div class="row">', file=indexFilePointer)

    return (workingDirectory,indexFilePointer)


def closeIndexPage(pageNumber,numberOfPages,indexFilePointer):
    """prints out the closing part of an index page"""
    print('</div>', file=indexFilePointer)
    print(getPaginationSection(pageNumber,numberOfPages), file=indexFilePointer)
    print('</div>', file=indexFilePointer)
    print(getIndexPageFooter(pageNumber,numberOfPages), file=indexFilePointer)
    indexFilePointer.close()
    os.chmod(indexFilePointer.name,0o644)


def convertImage(imageFile,workingDirectory):
    """Creates both the standard and thumbnail images in the proper directories with the correct permissions"""
    if not arguments['--quiet']: print("Processing {}".format(imageFile))

    imagesDirectory = createDirectory(workingDirectory + '/images',True)
    outFile = os.path.join(imagesDirectory, os.path.basename(imageFile).lower())
    createImage(imageFile,outFile)


def createImage(inFile,outFile):
    """performs the actual image file conversion"""

    if arguments['--leave']:
        os.rename(inFile.path,outFile)
    else:
        try:
            im = Image.open(inFile.path)
            im.thumbnail(inFile.scaledSize,Image.ANTIALIAS)
            im.save(outFile,"JPEG")
        except IOError:
            print("Cannot create thumbnail for {}".format(inFile),file=sys.stderr)
            return

    os.chmod(outFile,0o644)


def createDirectory(path,allowExisting=False):
    """Creates a new directory. If the directory already exists, an error may be raised (based on allowExisting)"""
    try:
        os.mkdir(path)
        os.chmod(path,0o755)
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

    html = r'''<div class="row">
    <div class="col-xs-12">
    <div class="pull-right">
    <nav>
        <ul class="pagination">
'''

    if pageNumber == 1:
        html += '          <li class="disabled"><a href="#">&laquo;</a></li>\n'
    else:
        html += '          <li><a href="../page{0}/">&laquo;</a></li>\n'.format(pageNumber-1)

    for number in range(1,numberOfPages+1):
        html += '          <li{0}><a href="../page{1}/">{1}</a></li>\n'.format(' class="current"' if number == pageNumber else '', number)

    if pageNumber == numberOfPages:
        html += '          <li class="disabled"><a href="#">&raquo;</a></li>\n'
    else:
        html += '          <li><a href="../page{0}/">&raquo;</a></li>\n'.format(pageNumber+1)

    html += '        </ul>\n    </nav>\n    </div>\n    </div>\n</div>\n'

    return html


def getIndexPageFooter(pageNumber,numberOfPages):
    """Returns the footer for the index pages"""
    return r"""
<!--#include virtual="/includes/bottom-scripts.html" -->
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
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=0">

    <meta property="og:locale"       content="en_US">
    <meta property="og:type"         content="website">
    <meta property="og:title"        content="Steven Scholnick : {0}">
    <meta property="og:description"  content="Steven Scholnick : {0}">
    <meta property="og:url"          content="{2}">
    <meta property="og:site_name"    content="Steven Scholnick">
    <meta property="og:image"        content="{1}">

    <meta name="twitter:card"        content="summary">
    <meta name="twitter:description" content="Steven Scholnick : {0}">
    <meta name="twitter:title"       content="Steven Scholnick : {0}">
    <meta name="twitter:site"        content="@scholnicks">
    <meta name="twitter:image"       content="{1}">
    <meta name="twitter:creator"     content="@scholnicks">

    <title>Steven Scholnick : {0}</title>
    <link rel="shortcut icon" href="/favicon.ico" type="image/x-icon">

    <link href="/bootstrap/css/bootstrap.min.css" rel="stylesheet">
    <link href="/css/base.css" rel="stylesheet">

    <!--[if lt IE 9]>
      <script src="https://oss.maxcdn.com/html5shiv/3.7.3/html5shiv.min.js"></script>
      <script src="https://oss.maxcdn.com/respond/1.4.2/respond.min.js"></script>
    <![endif]-->
 </head>
<body>

<!--#include virtual="/includes/top-navbar.html" -->

<div class="container">
    <div class="row">
        <div class="col-xs-12">
            <h1 class="page-header text-center">{0}</h1>
        </div>
    </div>
'''.format(pageTitle,arguments['--cover'],arguments['--url'])


SINGLE_PAGE_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=0">

    <meta property="og:locale"       content="en_US">
    <meta property="og:type"         content="website">
    <meta property="og:title"        content="Steven Scholnick : $pictureSetTitle - Photo $index">
    <meta property="og:description"  content="Steven Scholnick : $pictureSetTitle - Photo $index">
    <meta property="og:url"          content="https://scholnick.net/">
    <meta property="og:site_name"    content="Steven Scholnick">
    <meta property="og:image"        content="$coverPhoto">

    <meta name="twitter:card"        content="summary">
    <meta name="twitter:description" content="Steven Scholnick : $pictureSetTitle - Photo $index">
    <meta name="twitter:title"       content="Steven Scholnick : $pictureSetTitle - Photo $index">
    <meta name="twitter:site"        content="@scholnicks">
    <meta name="twitter:image"       content="$coverPhoto">
    <meta name="twitter:creator"     content="@scholnicks">

    <title>Steven Scholnick : $pictureSetTitle - Photo $index</title>
    <link rel="shortcut icon" href="/favicon.ico" type="image/x-icon">

    <link href="/bootstrap/css/bootstrap.min.css" rel="stylesheet">
    <link href="/css/base.css" rel="stylesheet">

    <!--[if lt IE 9]>
      <script src="https://oss.maxcdn.com/html5shiv/3.7.3/html5shiv.min.js"></script>
      <script src="https://oss.maxcdn.com/respond/1.4.2/respond.min.js"></script>
    <![endif]-->
 </head>
<body>

<!--#include virtual="/includes/top-navbar.html" -->

<div class="container">

<div class="row">
    <div class="col-xs-12 text-center">
        $linkLine
    </div>
</div>

<div class="row">
    <div class="col-xs-12 text-center">
        <a href="index.html" title="Click on image to return to index"><img src="images/$filename" alt="$index of $numberOfPictures"></a>
        <p>$index of $numberOfPictures photos</p>
    </div>
</div>

</div>

<!--#include virtual="/includes/bottom-scripts.html" -->
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

    linkLine = '''<a title="Previous Photo" href="{0}"><img src="/images/reverse.png" width="32" height="32" alt="<-"></a>
    <a title="Return to Index" href="index.html"><img src="/images/stop.png" width="32" height="32" alt="||"></a>
    <a title="Next Photo" href="{1}"><img src="/images/forward.png" width="32" height="32" alt="->"></a>'''.format(prevHTML,nextHTML)

    html = Template(SINGLE_PAGE_TEMPLATE).substitute(
       pictureSetTitle=arguments['<title>'],
       index=index,
       numberOfPictures=numberOfPhotos,
       lastPhotoFile=prevHTML,
       nextPhotoFile=nextHTML,
       linkLine=linkLine,
       coverPhoto=arguments['--cover'],
       filename=os.path.basename(imageFile.path).lower()
    )

    filePath = os.path.join(workingDirectory,f"{index}.html")
    with open(filePath,'w') as htmlFile:
        print(html,file=htmlFile)

    os.chmod(filePath,0o644)


class ImageFile(os.PathLike):
    """Class that holds the image path and the image's dimensions"""
    def __init__(self,path):
        self.path   = path
        self.width  = -1
        self.height = -1

    def isPortrait(self):
        return self.width > self.height

    @property
    def scaledWidth(self):
        return 640 if self.isPortrait() else 480

    @property
    def scaledHeight(self):
        return 480 if self.isPortrait() else 640

    @property
    def scaledDimension(self):
        return '{0}x{1}'.format(self.scaledSize)

    @property
    def scaledSize(self):
        return (self.scaledWidth,self.scaledHeight)

    def __fspath__(self):
        return self.path

    def __str__(self):
        return self.path


if __name__ == '__main__':
    from docopt import docopt
    arguments = docopt(__doc__, version='3.0.0')

    if arguments['--verbose']:
        arguments['--quiet'] = False

    main(arguments['<source-directory>'])

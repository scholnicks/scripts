#!/usr/bin/python -B
# -*- coding: utf-8 -*-

"""album:  Creates a album of photos complete with thumbnails. ImageMagick's convert does the hard work

(c) Steven Scholnick <steve@scholnick.net>

The album source code is published under version 2.1 of the GNU Lesser General Public License (LGPL).

In brief, this means there's no warranty and you can do anything you like with it.
However, if you make changes to album and redistribute those changes,
then you must publish your modified version under the LGPL.

"""

from __future__ import print_function
import os, sys, re, math, subprocess, shutil
from string import Template

numberOfPages = 0

def main(startingDirectory):
    if os.path.exists(options.destination):
        if options.overwrite:
            shutil.rmtree(options.destination)
        else:
            raise SystemExit("{0} directory exists. Will not overwrite, --overwrite is set to false".format(options.destination))

    createDirectory(options.destination)

    pictureFiles = []
    for root, dirs, files in os.walk(os.path.abspath(startingDirectory)):
        pictureFiles += [ImageFile(os.path.join(root,f)) for f in files if f.lower().endswith(".jpg")]

    pageNumber    = 1
    rowCount      = 0
    numberOfPages = int( math.ceil(float(len(pictureFiles)) / float(options.page)) )

    (workingDirectory,indexFilePointer) = openIndexPage(pageNumber,numberOfPages)

    if options.verbose:
        print("Number of photos = {0}, number of pages = {1}, output directory = {2}"
              .format(len(pictureFiles), numberOfPages, options.destination))

    for photoIndex in xrange(0,len(pictureFiles)):
        imageFile = pictureFiles[photoIndex]
        imageFile.index = photoIndex
        calculateDimensions(imageFile)

        if photoIndex > 0 and (photoIndex % options.page) == 0:
            closeIndexPage(pageNumber,numberOfPages,indexFilePointer)
            pageNumber += 1
            rowCount   = 0
            (workingDirectory,indexFilePointer) = openIndexPage(pageNumber,numberOfPages)

        convertImage(imageFile,workingDirectory)

        if rowCount > 0 and (rowCount % options.rowCount) == 0:
            print('</tr>\n<tr>', file=indexFilePointer)

        print('    <td><a class="picture" href="{0}.html"><img src="thumbnails/{1}" width="{2}" height="{3}"></a></td>'
              .format(photoIndex + 1,
                      os.path.basename(imageFile.path),
                      imageFile.thumbnailWidth,
                      imageFile.thumbnailHeight)
              ,file=indexFilePointer)

        createIndividualHTMLFile(workingDirectory,imageFile,len(pictureFiles),pageNumber)

        rowCount += 1

    closeIndexPage(pageNumber,numberOfPages,indexFilePointer)
    sys.exit(0)


def calculateDimensions(photoFile):
    """Calculates the dimensions of the photo by calling the ImageMagick standalone app, identify"""
    process = subprocess.Popen(['identify',photoFile.path],stdout=subprocess.PIPE)
    (photoFile.width,photoFile.height) = re.search(r' (\d+)x(\d+) ',process.stdout.readline()).groups()


def openIndexPage(pageNumber,numberOfPages):
    """prints out the opening of an index page and returns the current working directory and the file pointer"""
    workingDirectory = createDirectory(options.destination + '/page' +  str(pageNumber))
    indexFilePointer = open(os.path.join(workingDirectory,"index.html"),"w")

    print( getIndexPageHeader(pageNumber), file=indexFilePointer )
    print( getPaginationSection(pageNumber,numberOfPages), file=indexFilePointer)
    print( '\n<table>\n<tr>', file=indexFilePointer)

    return (workingDirectory,indexFilePointer)


def closeIndexPage(pageNumber,numberOfPages,indexFilePointer):
    """prints out the closing part of an index page"""
    print( '</tr>\n</table>\n', file=indexFilePointer)
    print( getPaginationSection(pageNumber,numberOfPages), file=indexFilePointer)
    print( getIndexPageFooter(pageNumber,numberOfPages), file=indexFilePointer)
    indexFilePointer.close()
    os.chmod(indexFilePointer.name,0644)


def convertImage(imageFile,workingDirectory):
    """Creates both the standard and thumbnail images in the proper directories with the correct permissions"""
    if not options.quiet: print("Processing {}".format(imageFile))

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
    """performs the actual image file creation by using the ImageMagick standalone app, convert. The file is then optimized with jpegtran"""
    cmd = "convert {0} -size {1} -quality 100 -scale {1} -strip -auto-orient {2}"
    if subprocess.call(cmd.format(inFile,scale,outFile),shell=True) != 0:
        raise StandardError('Unable to scale the image with convert')

    cmd = 'jpegtran -copy none -optimize -perfect -outfile {0} {0}'
    if subprocess.call(cmd.format(outFile),shell=True) != 0:
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

    html = '<div class="pagination pagination-right">\n<ul>\n'

    if pageNumber == 1:
        html += '    <li class="disabled"><a href="#">&laquo;</a></li>\n'
    else:
        html += '    <li><a href="../page{0}/">&laquo;</a></li>\n'.format(pageNumber-1)

    for number in xrange(1,numberOfPages+1):
        html += '    <li{0}><a href="../page{1}/">{1}</a></li>\n'.format(' class="active"' if number == pageNumber else '', number)

    if pageNumber == numberOfPages:
        html += '    <li class="disabled"><a href="#">&raquo;</a></li>\n'
    else:
        html += '    <li><a href="../page{0}/">&raquo;</a></li>\n'.format(pageNumber+1)

    html += '</ul>\n</div>'

    return html


def getIndexPageFooter(pageNumber,numberOfPages):
    """Returns the footer for the index pages"""
    return r"""
</div>
</div>

<!--#include virtual="/includes/bottom-scripts.html" -->
<script type="text/javascript">
    $(function() {
        $('#nav-pictures').addClass('active');
    });
</script>

</body>
</html>
"""


def getIndexPageHeader(pageNumber):
    pageTitle = options.title if numberOfPages == 1 else "{0}: Page {1}".format(options.title,pageNumber)

    """Returns the header for the index pages"""
    return '''<!DOCTYPE html>
<html lang="en">
    <meta charset="utf-8">
    <title>{0}</title>
    <link rel="shortcut icon" href="/favicon.ico" type="image/x-icon">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="/bootstrap/css/bootstrap.css" rel="stylesheet">
    <link href="/bootstrap/css/bootstrap-responsive.css" rel="stylesheet">
    <link href="/css/base.css" rel="stylesheet">
    <script type="text/javascript" src="/bootstrap/js/bootstrap.js"></script>
    <script type="text/javascript" src="/js/jquery.js"></script>
    <!--#include virtual="/includes/ieshiv" -->
</head>
<body>

<!--#include virtual="/includes/top-navbar.html" -->

<!-- main center content -->

<div class="container-fluid">
<div class="span9">

<div class="page-header text-center"><h2>{0}</h2></div>
'''.format(pageTitle)


SINGLE_PAGE_TEMPLATE = r'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>$pictureSetTitle - Photo $index</title>
    <link rel="shortcut icon" href="/favicon.ico" type="image/x-icon">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="/bootstrap/css/bootstrap.css" rel="stylesheet">
    <link href="/bootstrap/css/bootstrap-responsive.css" rel="stylesheet">
    <link href="/css/base.css" rel="stylesheet">
    <link rel="stylesheet" type="text/css" href="/css/picture-bootstrap.css">
    <script type="text/javascript" src="/bootstrap/js/bootstrap.js"></script>
    <script type="text/javascript" src="/js/jquery.js"></script>
    <!--#include virtual="/includes/ieshiv" -->
</head>
<body>

<!--#include virtual="/includes/top-navbar.html" -->

<!-- main center content -->

<div class="container-fluid">

<div class="span10 navigation">
$linkLine
</div>

<div class="span10">
<a href="index.html" title="Click on image to return to index"><img src="images/$filename" alt="$index of $numberOfPictures" height="$height" width="$width"></a>
<p>$index of $numberOfPictures photos</p>
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

$$('body').touchwipe({
    wipeLeft: nextPhoto,
    wipeRight: previousPhoto
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

    if prev == 0:
        prevHTML = 'index.html'
    else:
        if (prev % options.page) == 0:
            prevHTML = '../page{0}/{1}.html'.format((pageNumber-1),prev)
        else:
            prevHTML = str(prev) + '.html'

    if next > numberOfPhotos:
        nextHTML = 'index.html'
    else:
        if (index % options.page) == 0:
            nextHTML = '../page{0}/{1}.html'.format((pageNumber+1),next)
        else:
            nextHTML = str(next) + ".html"

    linkLine = '''    <a title="Previous Photo" href="{0}"><img src="/images/reverse.png" width="32" height="32" alt="<-"></a>
    <a title="Return to Index" href="index.html"><img src="/images/stop.png" width="32" height="32" alt="||"></a>
    <a title="Next Photo" href="{1}"><img src="/images/forward.png" width="32" height="32" alt="->"></a>'''.format(prevHTML,nextHTML)

    html = Template(SINGLE_PAGE_TEMPLATE).substitute(
       pictureSetTitle=options.title,
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
    # of a str in os.path.join() and open() calls

    def __str__(self):
        return self.path

    def rfind(self,target):
        return self.path.rfind(target)

    def __getitem__(self,key):
        return self.path.__getitem__(key)


if __name__ == '__main__':
    from optparse import OptionParser

    parser = OptionParser(usage='%prog [options] Input_Directory')
    parser.add_option('-d','--destination',dest="destination", type='string',       help='Sets the folder destination, defaults to photos')
    parser.add_option('-m','--max',        dest="max",         type='int',          help='Sets the maximum number of photos')
    parser.add_option('-o','--overwrite',  dest="overwrite",   action="store_true", help='Overwrites the destination directory with the new set of photos.')
    parser.add_option('-p','--page',       dest="page",        type='int',          help='Sets the maximum number of photos per page, defaults to 50')
    parser.add_option('-q','--quiet',      dest="quiet",       action="store_true", help='Toggles quiet mode')
    parser.add_option('-r','--row-count',  dest="rowCount",    type="int",          help='Sets the row count per index page, defaults to 7')
    parser.add_option('-t','--title',      dest="title",       type='string',       help='Sets the title [REQUIRED]')
    parser.add_option('-v','--verbose',    dest="verbose",     action="store_true", help='Toggles verbose mode')
    parser.set_defaults(max=10000, page=50, rowCount=7, destination="photos")

    options,args = parser.parse_args()

    if options.verbose:
        options.quiet = False

    if len(args) < 1 or not options.title:
        parser.print_help()
        sys.exit(1)

    main(args[0])

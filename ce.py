#!/usr/bin/python -B
# -*- coding: utf-8 -*-

"""
ce: Mac Contacts Exporter

(c) Steven Scholnick <steve@scholnick.net>

The ce source code is published under version 2.1 of the GNU Lesser General Public License (LGPL).
 
In brief, this means there's no warranty and you can do anything you like with it.
However, if you make changes to rename and redistribute those changes, 
then you must publish your modified version under the LGPL. 

"""

from __future__ import print_function
import os, sys, glob 
import sqlite3

SQL = """select
        R.ZLASTNAME, R.ZFIRSTNAME, P.ZSTREET, P.ZCITY, P.ZSTATE, P.ZZIPCODE
from
        ZABCDRECORD R, ZABCDPOSTALADDRESS P
where
        R.Z_PK = P.ZOWNER and 
        R.ZLASTNAME is not null and P.ZCITY is not null and P.ZZIPCODE is not null
order by 
        1, 2
"""

def main():
    with open(options.outputPath,"w") as fp:
        conn = sqlite3.connect(getAddressDatabaseFile())
        for row in conn.cursor().execute(SQL):
            printRow(fp,row)
        conn.close()

    if options.verbose: print("{0} has been created".format(options.outputPath))
    sys.exit(0)


def printRow(fileHandle,row):
    print("""{1} {0}
{2}
{3}, {4}, {5}
    """.format(*row),file=fileHandle)


def getAddressDatabaseFile():
    files = glob.glob(os.environ['HOME'] +  "/Library/Application Support/AddressBook/Address*")
    return files[0] if files else None


if __name__ == '__main__':
    from optparse import OptionParser
    
    parser = OptionParser(usage='%prog [--output PATH] [--verbose]')
    parser.add_option('-v','--verbose',dest="verbose", action="store_true", help='Toggles verbose')
    parser.add_option('-o','--output',dest="outputPath", type='string', help='Output filepath')
    parser.set_defaults(outputPath="Addresses.txt")
    
    options,args = parser.parse_args()
    main()

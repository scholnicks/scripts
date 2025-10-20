#!/usr/bin/env python -B
# vi: set syntax=python ts=4 sw=4 sts=4 et ff=unix ai si :
#
# ce: Mac Contacts Exporter
#
# (c) Steven Scholnick <scholnicks@gmail.com>
# The ce source code is published under a MIT license.

import glob
import os
import sqlite3
import sys

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
    """main method"""
    with open(options.outputPath, "w") as fp:
        with sqlite3.connect(getAddressDatabaseFile()) as conn:
            for row in conn.cursor().execute(SQL):
                printRow(fp, row)

    if options.verbose:
        print("{0} has been created".format(options.outputPath))

    sys.exit(0)


def printRow(fileHandle, row):
    """prints a single row of data"""
    print(
        """{1} {0}
{2}
{3}, {4}, {5}
    """.format(
            *row
        ),
        file=fileHandle,
    )


def getAddressDatabaseFile():
    """Returns the path to the addressbook SQLite database file"""
    files = glob.glob(os.environ["HOME"] + "/Library/Application Support/AddressBook/Address*")
    return files[0] if files else None


if __name__ == "__main__":
    from optparse import OptionParser

    parser = OptionParser(usage="%prog [--output PATH] [--verbose]")
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true", help="Toggles verbose")
    parser.add_option("-o", "--output", dest="outputPath", type="string", help="Output filepath")
    parser.set_defaults(outputPath="Addresses.txt")

    options, args = parser.parse_args()
    main()

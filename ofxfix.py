#!/usr/bin/env python3

import sys
import os.path
import argparse
import hashlib
import decimal
import datetime

from xml.dom.minidom import parse
import subprocess


def fix_ofx_fitid(ofx, dups):
    """
    Attempt to generate a unique FITID based on the transaction contents.
    """

    x = ofx.getElementsByTagName('OFX')[0]
    x = x.getElementsByTagName('BANKMSGSRSV1')[0]
    x = x.getElementsByTagName('BANKTRANLIST')[0]
    x = x.getElementsByTagName('STMTTRN')
    for t in x:
        ttype = t.getElementsByTagName('TRNTYPE')[0].firstChild.data
        dtposted = t.getElementsByTagName('DTPOSTED')[0].firstChild.data
        trnamt = t.getElementsByTagName('TRNAMT')[0].firstChild.data

        nametag = t.getElementsByTagName('NAME')[0].firstChild
        memotag = t.getElementsByTagName('MEMO')[0].firstChild

        nhash = hashlib.sha1(nametag.data.encode('utf-8')).hexdigest().upper()
        mhash = hashlib.sha1(memotag.data.encode('utf-8')).hexdigest().upper()

        fitid = 'SUNFIX_{0}{1}{2}-{3}{4}'.format(dtposted, ttype[0], abs(decimal.Decimal(trnamt)), nhash, mhash)

        t.getElementsByTagName('FITID')[0].firstChild.data = fitid
        # nametag.data = memotag.data

        if fitid in dups:
            print('WARNING: Duplicate generated FITID, manual intervention required...', file=sys.stderr)
            print('  {0}'.format(nametag.data), file=sys.stderr)
            print('  {0}'.format(fitid), file=sys.stderr)

        dups.add(fitid)


def fix_ofx_balace(ofx):
    """
    Fix the balance dates
    DD/MM/YYYY -> YYYYMMDD
    """

    x = ofx.getElementsByTagName('OFX')[0]
    x = x.getElementsByTagName('BANKMSGSRSV1')[0]

    ledgerbal = x.getElementsByTagName('LEDGERBAL')[0].getElementsByTagName('DTASOF')[0].firstChild
    ldate = datetime.datetime.strptime(ledgerbal.data, '%d/%m/%Y')
    ledgerbal.data = ldate.strftime('%Y%m%d')

    availbal = x.getElementsByTagName('AVAILBAL')[0].getElementsByTagName('DTASOF')[0].firstChild
    adate = datetime.datetime.strptime(availbal.data, '%d/%m/%Y')
    availbal.data = ldate.strftime('%Y%m%d')


def main():
    parser = argparse.ArgumentParser(description='OFXFix')
    parser.add_argument('infile', metavar='infile.ofx', type=str, help='Input file')
    parser.add_argument('outfile', metavar='outfile.ofx', type=str, nargs='?')

    args = parser.parse_args(sys.argv[1:])

    if not args.outfile:
        filename = os.path.basename(args.infile)
        base, ext = os.path.splitext(filename)
        args.outfile = '{0}.fixed{1}'.format(base, ext)

    with open(args.infile, 'r') as f:
        ofxdom = parse(f)

    dups = set()
    fix_ofx_fitid(ofxdom, dups)
    fix_ofx_balace(ofxdom)

    xmlstr = ofxdom.toprettyxml(indent='  ', newl='')

    if args.outfile == '-':
        print(xmlstr, file=sys.stdout, end='')
    else:
        with open(args.outfile, 'w') as f:
            print(xmlstr, file=f, end='')
    return 0


if __name__ == '__main__':
    exit(main())

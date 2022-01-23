#!/usr/bin/env python3
##
# Extract LEGO Stunt Rally RFD/RFH archives.
#
# https://github.com/vs49688/scripts/
# Zane van Iperen <zane@zanevaniperen.com>
#
# SPDX-License-Identifier: CC0-1.0
#
# Usage: stuntxtract.py <game-path> [out-path]
##

import struct
import collections
import os.path
import subprocess
import zlib
import json
import sys

ARCHIVES = [
    'ART0001',
    'CITY0001',
    'DESERT0001',
    'ICE0001',
    'JUNGLE0001',
    'SPEECH0001',
    'TEXT0001',
]

SRIndexEntry = collections.namedtuple('SRIndexEntry', [
    'unk1',
    'unk2',
    'unk3',
    'size',
    'offset',
    'path'
])

if len(sys.argv) == 2:
    gamedir = sys.argv[1]
    outdir = '.'
elif len(sys.argv) == 3:
    gamedir = sys.argv[1]
    outdir = sys.argv[2]
else:
    print(f'Usage: {sys.argv[0]} <game-path> [out-path]')
    exit(2)

index = {}

for a in ARCHIVES:
    rfh = os.path.join(gamedir, 'res', f'{a}.RFH')
    with open(rfh, 'rb') as f:
        data = f.read()

    entries = []
    while len(data) > 0:

        fields = data[:20]
        data = data[20:]

        idx = data.index(b'\0')

        unk1, unk2, unk3, size, offset = struct.unpack('<IIIII', fields)

        name = data[:idx].decode('utf-8')
        data = data[idx + 1:]

        entries.append(SRIndexEntry(
            unk1=unk1,
            unk2=unk2,
            unk3=unk3,
            size=size,
            offset=offset,
            path=name
        ))

    index[a] = entries

os.makedirs(outdir, exist_ok=True)

for a, entries in index.items():
    rfd = os.path.join(gamedir, 'res', f'{a}.RFD')
    with open(rfd, 'rb') as f:
        data = f.read()

    for entry in entries:
        json.dump({
            'unk1': entry.unk1,
            'unk2': entry.unk2,
            'unk3': entry.unk3,
            'size': entry.size,
            'offset': entry.offset,
            'path': entry.path,
        }, sys.stdout)
        print()

        path = entry.path.replace('\\', '/')
        dirname = os.path.dirname(path)

        outpath = os.path.join(outdir, path)
        os.makedirs(os.path.join(outdir, dirname), exist_ok=True)

        try:
            decdata = zlib.decompress(data[entry.offset + 4:entry.offset + entry.size])
        except zlib.error as e:
            msg = e.args[0]

            if msg.startswith('Error -3'):
                pass
            elif msg.startswith('Error -5'):
                pass
            else:
                raise e

            decdata = data[entry.offset:entry.offset + entry.size]

        with open(outpath, 'wb') as f:
            f.write(decdata)

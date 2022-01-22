#!/usr/bin/env python3

import struct
import collections
import os.path
import subprocess
import zlib

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

index = {}

for a in ARCHIVES:
    with open(f'{a}.RFH', 'rb') as f:
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

os.makedirs('ext', exist_ok=True)

for a, entries in index.items():
    with open(f'{a}.RFD', 'rb') as f:
        data = f.read()

    for entry in entries:
        print(entry)
        path = entry.path.replace('\\', '/')
        dirname = os.path.dirname(path)

        outpath = os.path.join('ext', path)
        os.makedirs(os.path.join('ext', dirname), exist_ok=True)

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

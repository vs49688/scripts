#!/usr/bin/env python3
##
# Extract "Starscape.000". Well, enough of it for the music.
# No guarantees are provided for the other assets.
#
# See bt/starscape.000.bt
#
# https://github.com/vs49688/scripts/
# Zane van Iperen <zane@zanevaniperen.com>
#
# SPDX-License-Identifier: CC0-1.0
#
# Usage: starscape_extract.py /path/to/Starscape.000 [out-path]
##

import io
import os
import struct
import sys
import pathlib

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class MoonEntry(object):
    tag: int
    unk_04h: int
    unk_08h: int
    unk_0Ah: int
    unk_0Ch: int
    unk_0Eh: int
    unk_10h: int
    size_1: int
    size_2: int
    name_len: int
    name: str
    data: bytes

    @staticmethod
    def from_stream(f: io.IOBase) -> 'MoonEntry':
        fields = struct.unpack('<IIHHHHHIII', f.read(30))

        name_len = fields[9]
        name = f.read(name_len).decode('us-ascii')

        return MoonEntry(
            *fields,
            name=name,
            data=f.read(fields[7]),
        )


if len(sys.argv) == 2:
    ss_path = sys.argv[1]
    out_dir = pathlib.Path('.')
elif len(sys.argv) == 3:
    ss_path = sys.argv[1]
    out_dir = pathlib.Path(sys.argv[2])
else:
    print(f'Usage: {sys.argv[0]} /path/to/Starscape.000 [out-path]')
    exit(2)

with open(ss_path, 'rb') as f:
    moon_entries = []

    while True:
        tag_bytes = f.peek(4)[:4]
        if len(tag_bytes) == 0:
            break

        tag, = struct.unpack('<I', tag_bytes)

        match tag:
            case 0x4E4F4F4D:  # "MOON"
                entry = MoonEntry.from_stream(f)
                print(f'Read MOON index {entry.name}, {entry.size_1} bytes')
                moon_entries.append(entry)

            case 0x02014B50:  # "PK\x01\x02"
                # Irrelevant for our purposes
                f.seek(28, os.SEEK_CUR)
                name_len, = struct.unpack('<H', f.read(2))
                f.seek(16, os.SEEK_CUR)
                f.seek(name_len, os.SEEK_CUR)

            case 0x6054b50:  # "PK\x05\x06"
                # Irrelevant for our purposes
                f.seek(22, os.SEEK_CUR)

            case _:
                raise RuntimeError(f'Unknown chunk {tag}')

    for entry in moon_entries:
        if entry.name.endswith('/'):
            continue

        ext_dir = out_dir / os.path.dirname(entry.name)
        ext_dir.mkdir(exist_ok=True, parents=True)

        ext_path = out_dir / entry.name

        with open(ext_path, 'wb') as f:
            f.write(entry.data)

        print(f'Wrote {entry.name} -> {ext_path}')

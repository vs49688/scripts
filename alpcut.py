#!/usr/bin/env python3

import struct
import collections
import os
import sys

ALPHeader = collections.namedtuple('ALPHeader', [
	'magic',
	'header_size',
	'adpcm',
	'unk1',
	'num_channels',
	'sample_rate'
])

def main():
	if len(sys.argv) != 4:
		print('Usage: {0} <infile> <nbytes> <outfile>'.format(sys.argv[0]), file=sys.stderr)
		return 2

	nbytes = int(sys.argv[2])

	with open(sys.argv[1], 'rb') as f:
		_magic, _header_size, _adpcm, _unk1, _num_channels = struct.unpack('<II6sBB', f.read(16))

		if _magic != 0x20504c41: # Little "ALP "
			print('Not a ALP file', file=sys.stderr)
			return 1

		if _header_size == 8:
			_sample_rate = 11025 * _num_channels
		elif _header_size == 12:
			_sample_rate = struct.unpack('<I', f.read(4))
		else:
			print('Invalid header size', file=sys.stderr)
			return 1

		fhdr = ALPHeader(
			magic=_magic,
			header_size=_header_size,
			adpcm=_adpcm,
			unk1=_unk1,
			num_channels=_num_channels,
			sample_rate=_sample_rate
		)

		data = f.read(nbytes)

	with open(sys.argv[3], 'wb') as f:

		f.write(struct.pack('<II6sBB',
			fhdr.magic, fhdr.header_size, fhdr.adpcm,
			fhdr.unk1, fhdr.num_channels
		))

		if fhdr.header_size == 12:
			f.write(struct.pack('<I', fhdr.sample_rate))

		f.write(data)

if __name__ == '__main__':
	exit(main())
#!/usr/bin/env python3

import struct
import collections
import os
import sys

KVAGHeader = collections.namedtuple('KVAGHeader', [
	'magic',
	'data_size',
	'sample_rate',
	'stereo'
])

def main():
	if len(sys.argv) != 4:
		print('Usage: {0} <infile> <nbytes> <outfile>'.format(sys.argv[0]), file=sys.stderr)
		return 2

	nbytes = int(sys.argv[2])

	with open(sys.argv[1], 'rb') as f:
		rawhdr = f.read(14)
		fhdr = KVAGHeader(*struct.unpack('<IIIH', rawhdr))

		if fhdr.magic != 0x4741564b: # little "KVAG"
			print('Not a VAG file', file=sys.stderr)
			return 1

		if fhdr.data_size > fhdr.data_size:
			print('Not enough bytes in the file', file=sys.stderr)
			return 1

		data = f.read(nbytes)

	with open(sys.argv[3], 'wb') as f:
		f.write(struct.pack('<IIIH', *fhdr._replace(data_size=nbytes)))
		f.write(data)

if __name__ == '__main__':
	exit(main())
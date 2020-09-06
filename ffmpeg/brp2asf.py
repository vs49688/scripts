#!/usr/bin/env python3

# Extract the embedded ASF from a BRP file

import sys
import os
import struct
import collections

BRPFileHeader = collections.namedtuple('BRPFileHeader', [
	'magic',
	'num_streams',
	'byte_rate'
])

BRPStreamHeader = collections.namedtuple('BRPStreamHeader', [
	'codec_id',
	'id',
	'duration_ms',
	'byte_rate',
	'extradata_size',
	'extradata'
])

BRPBlockHeader = collections.namedtuple('BRPBlockHeader', [
	'stream_id',
	'start_ms',
	'size'
])

def read_brp(f):
	streams = []

	rawhdr = f.read(12)
	fhdr = BRPFileHeader(*struct.unpack('<III', rawhdr))

	if fhdr.magic != 0x50505242:
		raise Exception('Not a BRP file')

	for i in range(fhdr.num_streams):
		rawhdr = f.read(20)
		shdr = BRPStreamHeader(*struct.unpack('<IIIII', rawhdr), None)
		shdr = shdr._replace(extradata=f.read(shdr.extradata_size))
		streams.append(shdr)

	return fhdr, streams

def main():
	if len(sys.argv) != 2:
		print(f'Usage: {sys.argv[0]} <infile>')
		return 2

	with open(sys.argv[1], 'rb') as f:
		fhdr, streams = read_brp(f)

		st = None
		for s in streams:
			if s.codec_id == 0x46534142:
				st = s
				break

		if st is None:
			print('No BASF streams in file', file=sys.stderr)
			return 1

		blkhdr = BRPBlockHeader(*struct.unpack('<iII', f.read(12)))
		if blkhdr.stream_id != st.id:
			print('First block isn\'t BASF', file=sys.stderr)
			return 1

		data = f.read(blkhdr.size)

	outname = os.path.splitext(os.path.basename(sys.argv[1]))[0] + '.ASF'
	with open(outname, 'wb') as f:
		f.write(st.extradata)
		f.write(data)

	return 0

if __name__ == '__main__':
	exit(main())
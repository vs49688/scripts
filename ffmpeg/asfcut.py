#!/usr/bin/env python3

import struct
import collections
import os
import sys

ASFFileHeader = collections.namedtuple('ASFFileHeader', [
	'magic',
	'version_major',
	'version_minor',
	'num_chunks',
	'chunk_offset',
	'name'
])

ASFChunkHeader = collections.namedtuple('ASFChunkHeader', [
	'num_blocks',
	'num_samples',
	'unk1',
	'sample_rate',
	'unk2',
	'flags'
])

ASF_CF_STEREO = 1 << 1


def main():
	if len(sys.argv) != 4:
		print('Usage: {0} <infile> <nblocks> <outfile>'.format(sys.argv[0]), file=sys.stderr)
		return 2

	nblocks = int(sys.argv[2])

	with open(sys.argv[1], 'rb') as f:
		rawhdr = f.read(24)
		fhdr = ASFFileHeader(*struct.unpack('<IHHII8s', rawhdr))

		if fhdr.magic != 0x00465341: # little "ASF\0
			print('Not an ASF file', file=sys.stderr)
			return 1

		f.seek(fhdr.chunk_offset, os.SEEK_SET)

		rawhdr = f.read(20)
		ckhdr = ASFChunkHeader(*struct.unpack('<IIIHHI', rawhdr))

		if nblocks > ckhdr.num_blocks:
			print('Not enough blocks in the file')
			return 1

		nchannels = (ckhdr.flags & ASF_CF_STEREO != 0) + 1

		cksize = int(ckhdr.num_samples / 2 * nchannels) + nchannels

		chunkdata = f.read(cksize * nblocks)

	with open(sys.argv[3], 'wb') as f:
		f.write(struct.pack('<IHHII8s', *fhdr._replace(chunk_offset=24)))
		f.write(struct.pack('<IIIHHI', *ckhdr._replace(num_blocks=nblocks)))
		f.write(chunkdata)

if __name__ == '__main__':
	exit(main())
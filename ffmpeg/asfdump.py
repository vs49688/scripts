#!/usr/bin/env python3

import sys
import os
import struct
import collections
import json
from asfcut import ASFFileHeader, ASFChunkHeader, ASF_CF_STEREO

def read_asf(f):
	rawhdr = f.read(24)
	fhdr = ASFFileHeader(*struct.unpack('<IHHII8s', rawhdr))

	if fhdr.magic != 0x00465341: # little "ASF\0
		raise Exception('Not an ASF file')

	f.seek(fhdr.chunk_offset, os.SEEK_SET)

	rawhdr = f.read(20)
	ckhdr = ASFChunkHeader(*struct.unpack('<IIIHHI', rawhdr))

	return fhdr, ckhdr

def main():
	if len(sys.argv) != 2:
		print(f'Usage: {sys.argv[0]} <infile>')
		return 2

	with open(sys.argv[1], 'rb') as fp:
		fhdr, ckhdr = read_asf(fp)

		x = fhdr._asdict()
		x['name'] = x['name'].decode('us-ascii')
		x['chunks'] = [ckhdr._asdict()]
		x['_version'] = f'{fhdr.version_major}.{fhdr.version_minor}'
		x['_filename'] = os.path.basename(sys.argv[1])

		print(json.dumps(x, indent=4))

if __name__ == '__main__':
	exit(main())
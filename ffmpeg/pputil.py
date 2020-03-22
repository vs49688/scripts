#!/usr/bin/env python3
##
# Pro Pinball Series Soundbank Utilities
#
# https://{github.com,codeberg.org}/vs49688/scripts
# Zane van Iperen <zane@zanevaniperen.com>
#
# SPDX-License-Identifier: CC0-1.0
##

import struct
import collections
import os
import sys
import argparse
import json

PPBnkHeader = collections.namedtuple('PPBnkHeader', [
	'bank_id',
	'sample_rate',
	'always1',
	'track_count',
	##
	# I think these are flags.
	# SFX seem to be 1, Music has this at 2
	##
	'flags',
	'tracks'
])

PPBnkTrack = collections.namedtuple('PPBnkTrack', [
	'id',
	'size',
	'sample_rate',
	'always1_1',
	'always1_2',
	'file_offset' # NB: Not actually part of the header
], rename=True)

def read_bnk(fp):

	tracks = []

	hdr = PPBnkHeader(*struct.unpack('<IIIII', fp.read(20)), tracks)

	for i in range(hdr.track_count):
		t = PPBnkTrack(*struct.unpack('<IIIII', fp.read(20)), fp.tell())
		tracks.append(t)
		#print(t._asdict())
		fp.seek(t.size, os.SEEK_CUR)

	return hdr

def dumphdr(file):
	with open(file, 'rb') as fp:
		info = read_bnk(fp)

		tracks2 = []
		for t in info.tracks:
			trk = t._asdict()
			trk['_file_offset'] = t.file_offset
			del trk['file_offset']

			tracks2.append(trk)

		info.tracks.clear()
		info.tracks.extend(tracks2)

		print(json.dumps(info._asdict(), indent=4))

	return 0

def split(file, outdir):
	basename = os.path.basename(file)

	with open(file, 'rb') as fp:
		info = read_bnk(fp)

		i = 0
		for track in info.tracks:
			fp.seek(track.file_offset, os.SEEK_SET)

			data = fp.read(track.size)

			dest = os.path.join(outdir, '{0}.{1:>03}.data'.format(basename, i))

			with open(dest, 'wb') as fp2:
				fp2.write(data)

			i += 1

	return 0

##
# Strip the file down to a single maxtracks tracks,
# where the size of each track is no more than maxsize bytes.
##
def fate_cut(file, outdir, maxtracks, maxsize):
	tracks = []
	datum = []

	with open(file, 'rb') as fp:
		info = read_bnk(fp)

		if info.sample_rate < 10000:
			extnum = str(info.sample_rate)[0]
		else:
			extnum = str(info.sample_rate)[0:2]

		hdr = info._replace(
			track_count = min(info.track_count, maxtracks),
			flags = 1,
			tracks = tracks
		)

		for i in range(hdr.track_count):
			trk = info.tracks[i]
			trk2 = trk._replace(
				size = min(trk.size, maxsize)
			)

			tracks.append(trk2)

			fp.seek(trk.file_offset, os.SEEK_SET)
			datum.append(fp.read(trk2.size))

	outname = os.path.splitext(os.path.basename(file))[0]
	outname = '{0}-cut.{1}c'.format(outname, extnum)

	dest = os.path.join(outdir, outname)

	with open(dest, 'wb') as fp:
		fp.write(struct.pack('<IIIII', *hdr[:-1]))

		for i in range(hdr.track_count):
			fp.write(struct.pack('<IIIII', *hdr.tracks[i][:-1]))
			fp.write(datum[i])


	return 0

def main():
	parser = argparse.ArgumentParser(description='Pro Pinball Series Soundbank Utilities')
	sp = parser.add_subparsers(dest='operation')
	sp.required = True

	dumpparse = sp.add_parser('dumphdr')
	dumpparse.add_argument('filename', help='soundbank (*.{5,11,22,44}[cC])')

	splitparse = sp.add_parser('split')
	splitparse.add_argument('-o', '--outdir', help='output directory', default=os.getcwd())
	splitparse.add_argument('filename', help='soundbank (*.{5,11,22,44}[cC])')

	fatecutparse = sp.add_parser('fate-cut')
	fatecutparse.add_argument('-o', '--outdir', help='output directory', default=os.getcwd())
	fatecutparse.add_argument('-n', '--max-track-count', help='maximum track count', default=1, type=int)
	fatecutparse.add_argument('-s', '--max-track-size', help='maximum track size', default=30720, type=int)
	fatecutparse.add_argument('filename', help='soundbank (*.{5,11,22,44}[cC])')

	args = parser.parse_args(sys.argv[1:])
	if args.operation == 'dumphdr':
		return dumphdr(args.filename)
	elif args.operation == 'split':
		return split(args.filename, args.outdir)
	elif args.operation == 'fate-cut':
		return fate_cut(args.filename, args.outdir, args.max_track_count, args.max_track_size)

	return 0

if __name__ == '__main__':
	exit(main())

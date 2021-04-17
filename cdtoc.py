#!/usr/bin/env python3

##
# THIS IS WRONG, DO NOT USE.
# MusicBrainz and CTDB use different TOC formats.
##

import re
import sys
import urllib.parse
import collections

Track = collections.namedtuple('Track', ['track', 'start', 'length', 'start_sector', 'end_sector'])

# [CTDB TOCID: KLIgMJoeKteuikQA1WuxfA9vO0A-] found
REGEX_TOCID = re.compile(r'^\[CTDB TOCID: (?P<tocid>[A-Za-z0-9-]{28})\]', re.MULTILINE)
REGEX_TOC   = re.compile(r'^\s+(?P<track>\d+)\s*\|\s*(?P<start>\d+:\d+\.\d+)\s*\|\s*(?P<length>\d+:\d+\.\d+)\s*\|\s*(?P<start_sector>\d+)\s*\|\s*(?P<end_sector>\d+)\s*$', re.MULTILINE)

with open(sys.argv[1], 'rb') as f:
	data = f.read()

try:
	data = data.decode('utf-8')
except UnicodeDecodeError as e:
	data = data.decode('utf-16')

m = REGEX_TOCID.search(data)
if not m:
    tocid = None
else:
    tocid = m.group('tocid')

tracks = []
for t in REGEX_TOC.finditer(data):
	no = int(t.group('track'))
	tracks.append(Track(
		track=no,
		start=t.group('start'),
		length=t.group('length'),
		start_sector=int(t.group('start_sector')),
		end_sector=int(t.group('end_sector'))
	))

def build_toc(tracks) -> str:
	vals = [tracks[0].track, len(tracks)]
	vals.append(tracks[-1].end_sector + 150)
	for t in tracks:
		vals.append(t.start_sector + 150)

	print(len(vals))
	return ' '.join([str(i) for i in vals])

url = urllib.parse.urlunparse((
	'https',
	'musicbrainz.org',
	'/cdtoc/attach',
	'',
	urllib.parse.urlencode({
		#'id': tocid,
		#'tracks': len(tracks),
		'toc': build_toc(tracks)
	}),
	''
))

print(url)

#!/usr/bin/env python3

import sys
import json
import urllib.request
import urllib.parse
import argparse

def main():
	parser = argparse.ArgumentParser(description='Get an iTunes podcast url')
	parser.add_argument('id', metavar='podcast-id', type=int, help='podcast id', nargs='+')

	args = parser.parse_args(sys.argv[1:])
	podurl = urllib.parse.urlunparse((
		'https',
		'itunes.apple.com',
		'/lookup',
		'',
		urllib.parse.urlencode({'entity': 'podcast', 'id': ','.join([str(i) for i in args.id])}),
		''
	))

	req = urllib.request.Request(
		url=podurl,
		headers={
			'User-Agent': 'Mozilla/5.0',
			'Accept': 'application/json'
		},
		method='GET'
	)

	with urllib.request.urlopen(req) as x:
		payload = json.loads(x.read().decode('utf-8'))

	if payload['resultCount'] < 1:
		print('No results returned.', file=sys.stderr)
		exit(1)

	for r in payload['results']:
		print(r['feedUrl'])

	exit(0)

if __name__ == '__main__':
	exit(main())

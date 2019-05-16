#!/usr/bin/env python3

import urllib.parse
import urllib.request
import hashlib
import io
import os
import os.path
import json
import uritemplate

class ghapi(object):
	def __init__(self, api, token):
		self._api = api
		self._token = token

	def _post_url_raw(self, url, data, content_type, method='POST'):
		req = urllib.request.Request(
			url=url,
			headers={
				'User-Agent': 'Mozilla/5.0',
				'Accept': 'application/json',
				'Content-Type': content_type,
				'Authorization': 'token {0}'.format(self._token)
			},
			data=data,
			method=method
		)

		with urllib.request.urlopen(req) as x:
			return (x.getcode(), json.loads(x.read().decode('utf-8')))

	def _post_url_json(self, url, data, method='POST'):
		return self._post_url_raw(url, json.dumps(data).encode('utf-8'), 'application/json', method)

	def create_release(self, owner, repo, tag, body, files):
		release = {
			'tag_name': tag,
			'target_commitish': 'master',
			'name': tag,
			'body': body,
			'draft': True
		}

		x = urllib.parse.urlparse(self._api)
		url = urllib.parse.urlunparse((
			x.scheme,
			x.netloc,
			urllib.parse.quote('/repos/{0}/{1}/releases'.format(owner, repo)),
			'',
			'',
			''
		))

		result = self._post_url_json(url, release)
		if result[0] != 201:
			raise Exception('Error {0} when creating release'.format(result[0]))

		return result[1]

	def upload_file(self, rel, f):
		fname = os.path.basename(f)

		flname = fname.lower()

		# https://www.iana.org/assignments/media-types/media-types.xhtml
		if flname.endswith('.deb'):
			content_type = 'application/vnd.debian.binary-package'
		elif flname.endswith('.rpm'):
			content_type = 'application/x-rpm'
		elif flname.endswith('.tar.gz'):
			content_type = 'application/gzip'
		elif flname.endswith('.exe'):
			content_type = 'application/vnd.microsoft.portable-executable'
		else:
			content_type = 'application/octet-stream'

		url = uritemplate.URITemplate(rel['upload_url']).expand(name=fname)

		with open(f, 'rb') as fp:
			fdata = fp.read()

		result = self._post_url_raw(url, fdata, content_type)
		if result[0] != 201:
			raise Exception('Error {0} when uploading {1}'.format(result[0], f))

		return result[1]

	def publish_release(self, rel):
		release = {
			'tag_name': rel['tag_name'],
			'target_commitish': rel['target_commitish'],
			'name': rel['name'],
			'body': rel['body'],
			'draft': False,
			'prerelease': False
		}

		result = self._post_url_json(rel['url'], release, 'PATCH')
		if result[0] != 200:
			raise Exception('Error {0} when publishing release'.format(result[0]))

		return result[1]

def build_description(files):
	# Build the Markdown description
	with io.StringIO() as desc:
		desc.write('```\r\n')
		for f in files:
			with open(f, 'rb') as fp:
				data = fp.read()

			m = hashlib.sha256()
			m.update(data)

			desc.write('{0}  {1}\r\n'.format(m.hexdigest(), os.path.basename(f)))

		desc.write('```\n')
		return desc.getvalue()


if __name__ == '__main__':
	import argparse

	parser = argparse.ArgumentParser(description='GitHub Release Publisher')
	parser.add_argument('--api',	type=str, help='the github api endpoint (default: https://api.github.com)', default='https://api.github.com')
	parser.add_argument('--token',
		type=str,
		help='the github api token (default: use the GITHUB_API_TOKEN environment variable)',
		default=os.environ['GITHUB_API_TOKEN'] if 'GITHUB_API_TOKEN' in os.environ else None,
		required='GITHUB_API_TOKEN' not in os.environ
	)
	parser.add_argument('owner',	type=str, help='the user or organisation')
	parser.add_argument('repo',		type=str, help='the repo name')
	parser.add_argument('tag',		type=str, help='the git tag')
	parser.add_argument('file',		type=str, nargs='+', help='a list of assets to upload')
	
	args = parser.parse_args()
	gh = ghapi(args.api, args.token)

	release = gh.create_release(args.owner, args.repo, args.tag, build_description(args.file), args.file)
	for f in args.file:
		gh.upload_file(release, f)
	gh.publish_release(release)
	exit(0)

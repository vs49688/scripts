#!/usr/bin/env python3

import os
import urllib.parse
import urllib.request
from collections import OrderedDict
import xml.etree.ElementTree

class NameSilo(object):
	def __init__(self, apikey):
		self._apikey = apikey

	def _make_url(self, op, **args):
		x = OrderedDict(
			version=1,
			type='xml',
			key=self._apikey
		)

		x.update(args)
		urltuple = (
			'https',
			'www.namesilo.com',
			'/api/{0}'.format(op),
			'',
			urllib.parse.urlencode(x),
			''
		)

		uu = urllib.parse.urlunparse(urltuple)
		#print(uu)
		return uu

	def _get_url(self, op, **args):
		url = self._make_url(op, **args)
		req = urllib.request.Request(
			url=url,
			headers={'User-Agent': 'Mozilla/5.0'}
		)
		data = urllib.request.urlopen(req).read().decode('utf-8')
		#print(data)
		root = xml.etree.ElementTree.fromstring(data)

		code = int(root.find('./reply/code').text)
		if code != 300:
			raise Exception('{0}: {1}'.format(op, root.find('./reply/detail').text))

		return root.find('./reply')

	def add_record(self, domain, host, value, ttl):
		reply = self._get_url('dnsAddRecord', domain=domain, rrtype='TXT', rrhost=host, rrvalue=value, rrttl=ttl)
		return reply.find('./record_id').text

	def del_record(self, domain, id):
		self._get_url('dnsDeleteRecord', domain=domain, rrid=id)

	def list_records(self, domain):
		reply = self._get_url('dnsListRecords', domain=domain)
		return [{e.tag:e.text for e in r} for r in reply.findall('./resource_record')]

def amce_build_host(domain):
	parts = domain.split('.')
	if len(parts) > 2:
			host = '_acme-challenge.{0}'.format('.'.join(parts[:-2]))
			cdomain = '.'.join(parts[-2:])
	else:
			host = '_acme-challenge'
			cdomain = domain

	fullhost = '_acme-challenge.{0}'.format(domain)
	return (host, cdomain, fullhost)

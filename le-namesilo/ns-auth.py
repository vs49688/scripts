#!/usr/bin/env python3

import os
import namesilo
import json
import time

CERTBOT_DOMAIN = os.environ['CERTBOT_DOMAIN']
CERTBOT_VALIDATION = os.environ['CERTBOT_VALIDATION']
API_KEY = os.environ['NAMESILO_API_KEY']

host, domain, fullhost = namesilo.amce_build_host(CERTBOT_DOMAIN)
value = CERTBOT_VALIDATION

ns = namesilo.NameSilo(API_KEY)
#print('Searching for \'{0}\' on \'{1}\'...'.format(host, domain), end='')
records = ns.list_records(domain)

def find_record(records):
	for r in records:
		#print(r)
		if r['host'] == fullhost:
			id = r['record_id']
			return id
	return None

#print({True: 'FOUND', False: 'NOT FOUND'}[bool(id)])

id = find_record(records)
if id:
	#print('  Record Id: {0}, deleting...'.format(id))
	ns.del_record(domain, id)

#print('Adding record...', end='')
id = ns.add_record(domain, host, value, 3600)

time.sleep(1200)
#while True:
#	records = ns.list_records(domain)
#	id = find_record(records)
#	if id:
#		break
#
#	time.sleep(60)

print(json.dumps({'host': host, 'domain': domain, 'fullhost': fullhost, 'id': id}))


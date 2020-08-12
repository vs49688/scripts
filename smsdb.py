#!/usr/bin/env python3

##
# SMSDB
# Store SMSBackup+'d emails into a SQLite3 database.
#
# SPDX-License-Identifier: CC0-1.0
#
# https://{github.com,codeberg.org}/vs49688/scripts/
# Zane van Iperen <zane@zanevaniperen.com>
#
# - Originally at https://github.com/vs49688/BackupTools.
# - Taken from last commit (64e6544bd0899256518632594b937466542e43d2)
# - Relicensed to CC0-1.0 as of 2020-08-12.
##

import os
import sys
import argparse
import sqlite3
import re
import urllib.parse
import imaplib
import email
import getpass
import time

def parse_field(line):
	"""
	Will match:
	Number -> (Number, None, None)
	+Number -> (+Number, None, None)
	Name -> (None, Name, None)
	Name (Number) -> (None, Name, Number)
	Name (+Number) -> (None, Name, +Number)
	"""
	p = re.compile(r'^\+?(\d+)$|^(.*?)\s*(?:\(\+?(\d+)\))?$')
	m = p.match(line)
	if not m:
		return None

	grps = m.groups()
	if grps[0]:
		return ('', grps[0])
	else:
		return grps[1:]

def connect_imap(uri):
	puri = urllib.parse.urlparse(uri)

	scheme = None
	if puri.scheme == None or puri.scheme == 'imap':
		scheme = 'imap'
		port = 143
	elif puri.scheme == 'imaps':
		scheme = 'imaps'
		port = 993
	else:
		raise Exception('Invalid IMAP Uri')

	if puri.port:
		port = puri.port

	#print(scheme, port)

	if scheme == 'imaps':
		return imaplib.IMAP4_SSL(puri.hostname, port)
	else:
		return imaplib.IMAP4(puri.hostname, port)

def parse_message(db, smsg, verbose=False):
	msg = email.message_from_bytes(smsg)

	fromaddr = email.utils.parseaddr(msg['from'])
	toaddr = email.utils.parseaddr(msg['to'])

	if fromaddr[0] == '':
		fromaddr = parse_field(fromaddr[1])
	else:
		fromaddr = parse_field(fromaddr[0])

	if toaddr[0] == '':
		toaddr = parse_field(toaddr[1])
	else:
		toaddr = parse_field(toaddr[0])

	attachments = []
	content = b''

	if msg.is_multipart():
		parts = msg.get_payload()
		#print(parts)
		for part in parts:
			#print({h:part[h] for h in part.keys()})
			if 'Content-Disposition' in part:
				p = re.compile(r'^attachment;\s+filename=(.*)$')
				m = p.match(part['Content-Disposition'])
				if m:
					attachments.append((m.group(1), part.get_content_type(), part.get_payload(decode=True)))
			else:
				if part.get_content_type() != 'text/plain':
					raise Exception('Invalid content')
				# If there's multiple text/plain sections, just merge them and stick a newline between them
				content += b"\n\n"
				content += part.get_payload(decode=True)
	else:
		content = msg.get_payload(decode=True)

	content = content.strip()

	dt = email.utils.parsedate_tz(msg['Date'])
	ts = email.utils.mktime_tz(dt)

	# SMS Backup+ uses "<UUID@sms-backup-plus.local>", except the UUID has no -
	p = re.compile(r'^<(\w{32})')
	m = p.match(msg['Message-ID'])
	if not m:
		raise Exception('Invalid Message-ID')

	uuid = m.group(1)
	uuid = "{0}-{1}-{2}-{3}-{4}".format(uuid[0:8], uuid[8:12], uuid[12:16], uuid[16:20], uuid[20:32])

	# See if this is a dup
	cur = db.cursor()
	try:
		cur.execute("SELECT id FROM messages WHERE uuid = ?", (uuid,))
		if cur.fetchone():
			if verbose:
				print('Skipping duplicate message: {0} from {1} <{2}>'.format(uuid, *fromaddr))
			return
	finally:
		cur.close()

	if verbose:
		print('Adding new message: {0} from {1} <{2}>'.format(uuid, *fromaddr))

	#print(uuid)
	db.execute("INSERT OR IGNORE INTO contacts(name, phone) VALUES(COALESCE(?, ''), COALESCE(?, ''))", fromaddr)

	cur = db.cursor()
	try:
		cur.execute("SELECT id FROM contacts WHERE name = COALESCE(?, '') AND phone = COALESCE(?, '')", fromaddr)
		fromid = int(cur.fetchone()[0])
	finally:
		cur.close()

	db.execute("INSERT OR IGNORE INTO contacts(name, phone) VALUES(COALESCE(?, ''), COALESCE(?, ''))", toaddr)

	cur = db.cursor()
	try:
		cur.execute("SELECT id FROM contacts WHERE name = COALESCE(?, '') AND phone = COALESCE(?, '')", toaddr)
		toid = int(cur.fetchone()[0])
	finally:
		cur.close()

	cur = db.cursor()
	try:
		cur.execute("INSERT INTO messages(uuid, from_id, to_id, timestamp, content) VALUES(?, ?, ?, ?, ?)", (uuid, fromid, toid, ts, content))
		msgid = cur.lastrowid
	finally:
		cur.close()

	for h in msg.items():
		db.execute("INSERT INTO headers(message_id, name, value) VALUES(?, ?, ?);", (msgid, h[0], h[1]))

	for att in attachments:
		db.execute("INSERT INTO attachments(message_id, name, type, content) VALUES(?, ?, ?, ?)", (msgid, *att))
	db.commit()

#exit(1)
def main():
	parser = argparse.ArgumentParser(description='SMSDB')
	parser.add_argument('db', type=str, help='sqlite3 connection string')
	parser.add_argument('--verbose', '-v', help='Verbose output', action='store_true')

	subparsers = parser.add_subparsers(help='operation', dest='operation')
	subparsers.required = True
	subparsers.add_parser('create', help='create the database')
	imap_parser = subparsers.add_parser('import', help='import messages from an imap server')
	imap_parser.add_argument('uri', help='IMAP URI')
	imap_parser.add_argument('path', help='IMAP Path')
	imap_parser.add_argument('processed_path', help='IMAP Processed Path')
	imap_parser.add_argument('--pass',
		dest='password',
		type=str,
		help='the password to use (default: use the SMSDB_PASS environment variable)',
		default=os.environ['SMSDB_PASS'] if 'SMSDB_PASS' in os.environ else None,
		required='SMSDB_PASS' not in os.environ
	)

	args = parser.parse_args(sys.argv[1:])

	with sqlite3.connect(args.db) as db:
		db.execute("PRAGMA foreign_keys = true;")
		db.execute("PRAGMA recursive_triggers = true;")

		if args.operation == 'create':
			db.execute("DROP VIEW IF EXISTS detailed;")
			db.execute("DROP TABLE IF EXISTS attachments;")
			db.execute("DROP TABLE IF EXISTS headers;")
			db.execute("DROP TABLE IF EXISTS messages;")
			db.execute("DROP TABLE IF EXISTS contacts;")

			db.execute("""CREATE TABLE contacts(
				id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
				name TEXT NOT NULL,
				phone TEXT NOT NULL,
				UNIQUE(name, phone)
			);""")

			db.execute("""CREATE TABLE messages(
				id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
				uuid TEXT NOT NULL UNIQUE,
				from_id INTEGER NOT NULL REFERENCES contacts(id) ON DELETE RESTRICT,
				to_id INTEGER NOT NULL REFERENCES contacts(id) ON DELETE RESTRICT,
				timestamp INTEGER NOT NULL CHECK(timestamp >= 0),
				content TEXT NOT NULL
			);""")

			db.execute("""CREATE TABLE headers(
				id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
				message_id INTEGER NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
				name TEXT NOT NULL,
				value TEXT NOT NULL,
				UNIQUE(message_id, name)
			);""")

			db.execute("""CREATE TABLE attachments(
				id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
				message_id INTEGER NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
				name TEXT NOT NULL,
				type TEXT NOT NULL,
				content BLOB NOT NULL
			)""")

			db.execute("""CREATE VIEW detailed AS
				SELECT
					m.id AS id,
					f.name || ' <' || f.phone || '>' AS `from`,
					t.name || ' <' || t.phone || '>' AS `to`,
					strftime('%Y-%m-%dT%H:%M:%SZ', m.timestamp, 'unixepoch') AS timestamp_utc,
					m.content AS content
				FROM
					messages AS m,
					contacts AS f,
					contacts AS t
				WHERE
					m.from_id = f.id AND
					m.to_id = t.id
				ORDER BY m.timestamp
			;""")

		elif args.operation == 'import':
			with connect_imap(args.uri) as imap:
				uriinfo = urllib.parse.urlparse(args.uri)

				xxx = imap.login(uriinfo.username, args.password)
				if xxx[0] != 'OK':
					print(xxx[1], file=sys.stderr)
					return 1

				rv, data = imap.select(args.path)
				if rv != 'OK':
					print("\n".join([i.decode('utf-8') for i in data]), file=sys.stderr)
					#print(data.decode('utf-8'))
					imap.logout()
					return 1

				rv, data = imap.search(None, 'ALL')
				message_set = ",".join(data[0].decode('utf-8').split())
				if len(message_set) == 0:
					imap.logout()
					return 1

				rv, data = imap.fetch(message_set, 'UID')

				REGEX_UID = re.compile(r'^(\d+)\s+\(UID\s+(\d+)\)$')

				data = [REGEX_UID.match(d.decode('utf-8')).group(2) for d in data]
				message_set = ",".join(data)

				rv, data = imap.uid('FETCH', message_set, '(RFC822)')

				data = [data[i] for i in range(len(data)) if i % 2 == 0]
				for msg in data:
					# if args.verbose:
					# 	print(msg[0])
					parse_message(db, msg[1], args.verbose)

				imap.uid('MOVE', message_set, args.processed_path)

				imap.close()
		elif args.operation == 'dummy':
			return 0
		else:
			print('Unknown operation {0}'.format(args.operation), file=sys.stderr)
			return 2

exit(main())

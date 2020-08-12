#!/usr/bin/env python3

##
# VoixDB
# Puts Skvalex and ACR calls into a consistent directory format.
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

import sys
import argparse
import sqlite3
import os
import shutil
import re
import datetime
import hashlib
from collections import namedtuple

# For skvalex
_REGEX1 = re.compile(r'^\[([^\]]*)\]_\[([^\]]*)\]_(\d{4})-(\d{2})-(\d{2})_(\d{2})-(\d{2})-(\d{2})\..*$')
_REGEX2 = re.compile(r'^\[([^\]]*)\]_\[([^\]]*)\]_(\d{2})-(\d{2})-(\d{2})_(\d{2})-(\d{2})-(\d{4})\..*$')
_REGEX3 = re.compile(r'^(\d{4})-(\d{2})-(\d{2})_(\d{2})-(\d{2})-(\d{2})_\[([^\]]*)\]_\[([^\]]*)\]\..*$')

# For ACR
_REGEX4 = re.compile(r'^call_(\d{2})-(\d{2})-(\d{2})_(OUT|IN)_(.+)?.(?:[aA][mM][rR])$')
_REGEX5 = re.compile(r'^(\d{4})-(\d{2})-(\d{2})$') # Matches the parent directory

IGNORE_FILES = ['.nomedia', 'desktop.ini', '.dropbox', 'incoming.sha1', 'outgoing.sha1']

voix_entry = namedtuple('voix_entry', 'path filename name number time')

def parse_regex1(name):
	r"""
	^\[([^\]]*)\]_\[([^\]]*)\]_(\d{4})-(\d{2})-(\d{2})_(\d{2})-(\d{2})-(\d{2})\..*$

	[Garry]_[0432542342]_2017-01-20_14-25-32.amr
	[Larry]_[0432542345]_2017-01-15_18-33-38.amr
	[Ted]_[0432542347]_2017-01-19_11-56-00.amr
	"""
	m = _REGEX1.match(name)
	if not m:
		return None

	groups = m.groups()

	dt = datetime.datetime(
		int(groups[2]),	# Year
		int(groups[3]),	# Month
		int(groups[4]),	# Day
		int(groups[5]),	# Hour
		int(groups[6]),	# Minute
		int(groups[7]),	# Second
	)

	return (groups[0], groups[1], dt)


def parse_regex2(name):
	r"""
	^\[([^\]]*)\]_\[([^\]]*)\]_(\d{2})-(\d{2})-(\d{2})_(\d{2})-(\d{2})-(\d{4})\..*$

	[Garry]_[0454345765]_11-37-35_09-03-2016.amr
	[Larry]_[0454345767]_13-22-36_19-01-2016.amr
	"""

	m = _REGEX2.match(name)
	if not m:
		return None

	groups = m.groups()

	dt = datetime.datetime(
		int(groups[7]),	# Year
		int(groups[6]),	# Month
		int(groups[5]),	# Day
		int(groups[2]),	# Hour
		int(groups[3]),	# Minute
		int(groups[4]),	# Second
	)

	return (groups[0], groups[1], dt)

def parse_regex3(name):
	r"""
	^(\d{4})-(\d{2})-(\d{2})_(\d{2})-(\d{2})-(\d{2})_\[([^\]]*)\]_\[([^\]]*)\]\..*

	2014-02-19_15-31-41_[Your Mother]_[0432546512].amr
	2014-02-25_11-01-30_[Your Mother's Lover]_[0432546513].amr
	"""

	m = _REGEX3.match(name)
	if not m:
		return None

	groups = m.groups()

	dt = datetime.datetime(
		int(groups[0]), # Year
		int(groups[1]), # Month
		int(groups[2]), # Day
		int(groups[3]), # Hour
		int(groups[4]), # Minute
		int(groups[5]), # Second
	)

	return (groups[6], groups[7], dt)

def parse_regex4(yy, mm, dd, name):
	r"""
	^call_(\d{2})-(\d{2})-(\d{2})_(OUT|IN)_(.+)?.(?:[aA][mM][rR])$

	call_14-24-10_OUT_33555400.amr
	call_11-02-32_IN_0436543215.AMR
	call_13-20-36_OUT_0436543215.AMR
	call_14-39-48_IN_0436543215.AMR
	"""

	m = _REGEX4.match(name)
	if not m:
		return None

	groups = m.groups()
	dt = datetime.datetime(
		yy,
		mm,
		dd,
		int(groups[0]),
		int(groups[1]),
		int(groups[2])
	)

	return (None, groups[4], dt, {'IN':True, 'OUT':False}[groups[3]])

def parse_filename_skvalex(name):
	data = parse_regex1(name)
	if data:
		return data

	data = parse_regex2(name)
	if data:
		return data

	data = parse_regex3(name)
	if data:
		return data

	return None

def hash_file(path):
	with open(path, 'rb') as w:
		return hashlib.sha1(w.read()).hexdigest()

def mkdirp(name):
	try:
		os.makedirs(name)
	except OSError as e:
		import errno
		if e.errno == errno.EEXIST and os.path.isdir(name):
			return

def scan_path_skvalex(path):
	incoming = []
	outgoing = []

	for root, dirs, files in os.walk(path, topdown=True):
		for f in files:
			if f in IGNORE_FILES:
				continue

			data = parse_filename_skvalex(f)
			if not data:
				continue

			path = os.path.normpath(os.path.join(root, f))
			typename = os.path.split(root)[1].lower()

			if typename == 'incoming':
				l = incoming
			elif typename == 'outgoing':
				l = outgoing
			else:
				print('  WARNING: Unknown call type \'{0}\'. Ignoring...'.format(typename))
				continue

			l.append(voix_entry(path=path, filename=f, name=data[0], number=data[1], time=data[2]))

	return incoming, outgoing

def scan_path_acr(path):
	incoming = []
	outgoing = []

	for root, dirs, files in os.walk(path, topdown=True):
		for f in files:
			if f in IGNORE_FILES:
				continue

			dirname = os.path.basename(root)
			m = _REGEX5.match(dirname)
			if not m:
				continue

			g = m.groups()
			data = parse_regex4(int(g[0]), int(g[1]), int(g[2]), f)
			if data[3]:
				l = incoming
			else:
				l = outgoing

			path = os.path.normpath(os.path.join(root, f))
			l.append(voix_entry(path=path, filename=f, name=data[0], number=data[1], time=data[2]))

	return incoming, outgoing

def add_calls(db, calls, incoming, root_path, verbose=False):
	for call in calls:
		if call.number == 'null':
			number = None
		else:
			number = call.number

		old_name, ext = os.path.splitext(call.filename)
		new_name = "{0:0>4}-{1:0>2}-{2:0>2}_{3:0>2}-{4:0>2}-{5:0>2}_[{6}]_[{7}]{8}".format(
			call.time.year, call.time.month, call.time.day,
			call.time.hour, call.time.minute, call.time.second,
			call.name, call.number, ext
		)

		type_string = {True:'incoming', False:'outgoing'}[incoming]

		local_dir = os.path.join(str(call.time.year), type_string)
		actual_dir = os.path.join(root_path, local_dir)
		local_path = os.path.join(local_dir, new_name)
		actual_path = os.path.join(actual_dir, new_name)

		mkdirp(actual_dir)
		sha1 = hash_file(call.path)

		cur = db.cursor()
		try:
			cur.execute("SELECT id FROM voix_entries WHERE sha1 = ?", (sha1,))
			exists = len(cur.fetchall()) != 0
		finally:
			cur.close()

		# Duplicate, ignore it
		if exists:
			if verbose:
				print('  Skipping existing {0} call: \'{1}\''.format(type_string, new_name))
			continue

		if verbose:
			print('  Adding new {0} call: \'{1}\''.format(type_string, new_name))

		# Copy the file first, only then insert
		shutil.copy(call.path, actual_path)
		db.execute(
			"INSERT INTO voix_entries(incoming, name, number, timestamp, path, sha1) VALUES(?, ?, ?, ?, ?, ?)",
			(incoming, call.name, number, call.time.timestamp(), local_path.replace('\\', '/'), sha1)
		)
		db.commit()

def regen_hashfiles(db, root_path):
	cur = db.cursor()
	try:
		cur.execute("SELECT id, incoming, year, line FROM voix_hashes")
		calls = cur.fetchall()
	finally:
		cur.close()

	files = {}

	for call in calls:
		if (call[2], call[1]) not in files:
			f = open(os.path.join(root_path, str(call[2]), {False:'outgoing.sha1', True:'incoming.sha1'}[call[1]]), 'w')
			files[call[2], call[1]] = f
		else:
			f = files[call[2], call[1]]

		# They're already ordered in the query, so just write them.
		f.write(call[3])
		f.write('\n')

	for f in files:
		files[f].close()

def main():
	parser = argparse.ArgumentParser(description='VOIXDB')
	parser.add_argument('db', type=str, help='SQLite3 connection string')
	parser.add_argument('--verbose', '-v', help='Verbose output', action='store_true')

	subparsers = parser.add_subparsers(help='DB Operations', dest='operation')
	subparsers.required = True
	subparsers.add_parser('create', help='Create the database')
	import_parser = subparsers.add_parser('import', help='Import a VOIX directory')
	import_parser.add_argument('--mode', type=str, help='Scan mode', choices=['skvalex', 'acr'], default='skvalex')
	import_parser.add_argument('--delete-input', dest='delete_input', help='Delete input files?', action='store_true')
	import_parser.add_argument('output', type=str, help='Output directory')
	import_parser.add_argument('path', type=str, help='path', nargs='*')

	args = parser.parse_args(sys.argv[1:])

	with sqlite3.connect(args.db) as db:
		db.execute("PRAGMA foreign_keys = true;")
		db.execute("PRAGMA recursive_triggers = true;")

		if args.operation == 'create':
			db.execute("DROP VIEW IF EXISTS voix_hashes;")
			db.execute("DROP TABLE IF EXISTS voix_entries;")
			db.execute("""CREATE TABLE voix_entries(
				id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
				incoming BOOLEAN NOT NULL,
				name TEXT,
				number TEXT,
				timestamp INTEGER NOT NULL CHECK(timestamp >= 0),
				path TEXT NOT NULL UNIQUE,
				sha1 TEXT NOT NULL UNIQUE
			);""")
			db.execute("""CREATE VIEW voix_hashes AS
				SELECT
					v.id AS id,
					v.incoming AS incoming,
					CAST(strftime('%Y', v.timestamp, 'unixepoch') AS INTEGER) AS year,
					substr(v.path, 6) || ' *' || v.sha1 AS line
				FROM voix_entries AS v
				ORDER BY v.incoming, v.timestamp
			;""")
			return 0
		elif args.operation == 'import':
			for path in args.path:
				if not os.path.exists(path):
					print('WARNING: Input path \'{0}\' doesn\'t exist'.format(path), file=sys.stderr)
					continue

				if args.verbose:
					print('Scanning input path \'{0}\''.format(path))

				if args.mode == 'skvalex':
					incoming, outgoing = scan_path_skvalex(path)
				elif args.mode == 'acr':
					incoming, outgoing = scan_path_acr(path)
				else:
					print('Invalid scan mode. This shouldn\'t happen', file=sys.stderr)
					return 1

				add_calls(db, incoming, True, args.output, verbose=args.verbose)
				add_calls(db, outgoing, False, args.output, verbose=args.verbose)

				if args.delete_input:
					for call in incoming:
						os.remove(call.path)

					for call in outgoing:
						os.remove(call.path)

				regen_hashfiles(db, args.output)
			return 0
		else:
			print('Unknown operation {0}'.format(args.operation), file=sys.stderr)
			return 2

exit(main())

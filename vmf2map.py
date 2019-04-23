#!/usr/bin/env python3
##
# VMF->MAP Converter
#
# https://github.com/vs49688/scripts/
# Zane van Iperen <zane@zanevaniperen.com>
#
# SPDX-License-Identifier: CC0-1.0
##

##
# VMF Loader
##
def _vmf_build_grammar():
	import pyparsing

	# Grammar for the '"key" "value"' pairs
	vmfTextValue = pyparsing.dblQuotedString
	vmfTextValue.setParseAction(pyparsing.removeQuotes)
	vmfKeyValue = pyparsing.Group(vmfTextValue + vmfTextValue)

	vmfObject = pyparsing.Forward()
	vmfSection = pyparsing.Group(pyparsing.Word(pyparsing.alphas) + vmfObject)

	vmfMembers = pyparsing.delimitedList(vmfSection | vmfKeyValue, pyparsing.White())
	vmfObject << pyparsing.Suppress('{') + vmfMembers + pyparsing.Suppress('}')

	return vmfMembers

def _vmf_add_value(d, v, name):
	if name not in d:
		d[name] = v
	else:
		vv = d[name]
		if type(vv) is not list:
			vv = [vv]
			d[name] = vv
		vv.append(v)

def _vmf_to_dict(vmf):
	d = {}
	for val in vmf[1:]:
		name = val[0]
		if len(val) == 2:
			d[name] = val[1]
		else:
			v = _vmf_to_dict(val[1:])
			_vmf_add_value(d, v, name)

	return d

def vmf_load(f):
	data = f.read()

	gram = _vmf_build_grammar()

	vmf = {}
	for s in gram.parseString(data).asList():
		v = _vmf_to_dict(s)
		_vmf_add_value(vmf, v, s[0])

	return vmf

##
# MAP Writer
##

import re
_MAP_REGEX_ORIGIN = re.compile(r'^(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)$')
_MAP_REGEX_PLANE = re.compile(r'^\(([^\)]+)\)\s+\(([^\)]+)\)\s+\(([^\)]+)\)$')
_MAP_REGEX_UVAXIS = re.compile(r'^\[(-?\d+(?:\.\d+)?)\s*(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)\]\s+(-?\d+(?:\.\d+)?)$')

def _map_fix_origin(origin):
	m = _MAP_REGEX_ORIGIN.match(origin)
	if not m:
		raise Exception('Invalid origin')

	return ' '.join(str(round(float(i))) for i in m.groups())

def _map_fix_plane(plane):
	m = _MAP_REGEX_PLANE.match(plane)
	if not m:
		raise Exception('Invalid plane')

	return ' '.join("({0})".format(_map_fix_origin(o)) for o in m.groups())

def _map_fix_uvaxis(axis):
	m = _MAP_REGEX_UVAXIS.match(axis)
	if not m:
		raise Exception('Invalid axis')

	groups = m.groups()

	return ('[{0}]'.format(' '.join(str(round(float(i))) for i in groups[:-1])), groups[4])

def _map_patch_material(mat):
	mat = mat.upper()

	# TODO: Add more obvious ones
	if mat == 'TOOLS/TOOLSTRIGGER':
		return 'AAATRIGGER'

	return mat

def _map_write_side(side, f):
	uaxis, uscale = _map_fix_uvaxis(side['uaxis'])
	vaxis, vscale = _map_fix_uvaxis(side['vaxis'])

	print('\t\t{0} {1} {2} {3} {4} {5} {6}'.format(
		_map_fix_plane(side['plane']),
		_map_patch_material(side['material']),
		uaxis,
		vaxis,
		round(float(side['rotation'])),
		uscale,
		vscale
	), file=f)

def _map_write_solid(solid, f):
	print('\t{', file=f)
	for side in solid:
		_map_write_side(side, f)
	print('\t}', file=f)

def _map_write_entity(entity, f):
	print('{', file=f)

	for key in entity:
		# MAP doesn't have these
		if key in ['editor', 'connections']:
			continue

		value = entity[key]

		if key != 'solid':
			if key == 'origin' or key == 'angles':
				value = _map_fix_origin(entity[key])

			# FIXME: Handle escaping properly
			print('\t"{0}" "{1}"'.format(key, value), file=f)
		else:
			if type(value) is str:
				# Not sure if this a index into the world solid list or just a corrupt file
				print('\t"{0}" "{1}"'.format(key, value), file=f)
				#_map_write_solid(vmf['world']['solid'][int(value)]['side'], f)
			elif type(value) is list:
				for solid in value:
					_map_write_solid(solid['side'], f)
			else:
				_map_write_solid(value['side'], f)

	print('}', file=f)

def map_write(vmf, f):
	_map_write_entity(vmf['world'], f)

	for entity in vmf['entity']:
		_map_write_entity(entity, f)

if __name__ == '__main__':
	import sys

	if len(sys.argv) != 3:
		print('Usage: {0} <infile.vmf> <outfile.map>'.format(sys.argv[0]))
		exit(2)

	with open(sys.argv[1], 'Ur', encoding='utf-8') as f:
		vmf = vmf_load(f)

	with open(sys.argv[2], 'w', encoding='utf-8') as f:
		map_write(vmf, f)

	exit(0)
	#import json
	#print(json.dumps(vmf))

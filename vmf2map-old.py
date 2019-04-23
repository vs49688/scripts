#!/usr/bin/env python
##
# VMF->MAP Converter (old 2009 version)
#
# https://github.com/vs49688/scripts/
# Zane van Iperen <zane@zanevaniperen.com>
#
# Please don't use this one, this is for reference only.
# A newer version is available in the sane repo.
#
# SPDX-License-Identifier: CC0-1.0
##
import sys;
import pyparsing;
import re;
import shlex;

def sectionToDict(data, mapDict):
	prev = ""
	for i in data:
		if(prev == ""):
			if(type(i) != str):
				raise Exception("No section header");
			else:
				prev = shlex.split(i)[0];
				continue;

		if(mapDict.get(prev, None) == None):
			mapDict[prev] = [];

		tmpDict = {};

		if(len(i) % 2 != 0):
			raise Exception("Invalid KeyValue pair");

		j = 0;
		while j < len(i):
			if(j % 2):
				safekey = shlex.split(i[j-1])[0];

				if(type(i[j]) == str):
					tmpDict[safekey] = shlex.split(i[j])[0];
				else:
					tmp2 = {};
					sectionToDict(i[j-1:j+1], tmp2);

					if(tmpDict.get(safekey, None) == None):
						tmpDict[safekey] = [];

					tmpDict[safekey].append(tmp2);
			j += 1;

		mapDict[prev].append(tmpDict);

		prev = "";

def main(args):

	if(len(args) != 3):
		sys.stdout.write("Usage: vmf2map.py infile.vmf outfile.map");
		return -1;

	vmfFile = open(args[1], "Ur");

	# I'm adding the vmffile{} section on so I don't have to scan for how
	# many sections there are
	vmf = "vmffile\n{\n" + "".join(line for line in vmfFile) + "\n}\n";
	vmfFile.close();

	expr = pyparsing.Word(pyparsing.alphas) + pyparsing.nestedExpr('{','}');

	print "Parsing..."
	result = expr.parseString(vmf).asList();
	print "Done!"

	mapDict = {};

	sectionToDict(result[1], mapDict);


	file = open(args[2], "w");
	writeClass(mapDict, "world", file);
	writeClass(mapDict, "entity", file);
	file.close();

def writeSolidList(solids, file, num):
	for s in solids:
		file.write("".join("\t" for i in range(num)) + "{\n");
		for i in s["solid"]:
			for currSide in i["side"]:
				for j in currSide:
					writeSide(currSide["side"][0], file, num + 1);
		file.write("".join("\t" for i in range(num)) + "}\n");

def splitaxis(axis):
	rg = re.compile('(\\[.*?\\])' + '(\\s+)' + '(\\d+)', re.IGNORECASE|re.DOTALL);
	m = rg.search(axis);

	return (m.group(1), m.group(3));

def splitplane(plane):
	rg = re.compile('(\\(.*?\\))' + '(\\s+)' + '(\\(.*?\\))' + '(\\s+)' + '(\\(.*?\\))');
	m = rg.search(plane);

	return (m.group(1), m.group(3), m.group(5));

def integerify(x):
	return str(int(round(float(x.strip()))));

def writeSide(side, file, num):
	file.write("".join("\t" for i in range(num)));

	uaxis, uscale = splitaxis(side.get("uaxis", "[0 0 0 0] 1"));
	vaxis, vscale = splitaxis(side.get("vaxis", "[0 0 0 0] 1"));

	uaxis = "[" + " ".join(integerify(f) for f in uaxis[1:-1].split(" ")) + "]";
	vaxis = "[" + " ".join(integerify(f) for f in vaxis[1:-1].split(" ")) + "]";

	plane = "".join(("".join(("(" + integerify(i[0]) + " " + integerify(i[1]) + " " + integerify(i[2]) + ") "))) for i in ((p[1:-1].split(" ")) for p in splitplane(side.get("plane", "(0 0 0) (0 0 0) (0 0 0)"))));

	sidestring = plane + \
		side.get("material", "NULL") + " " + \
		uaxis + " " + \
		vaxis + " " + \
		side.get("rotation", "0") + " " + \
		uscale + " " + \
		vscale + \
		"\n";

	file.write(sidestring);


def writeClass(data, classname, file):

	info = data.get(classname, None);
	if(info == None):
		return;

	for i in info:
		file.write("{\n");

		solidList = [];

		for j in i:
			if(type(i[j]) == str):
				file.write("\t\"%s\" \"%s\"\n" % (j, i[j]));

				if(j == "classname"):
					print "Writing entity %s" % (i[j]);

			elif(j == "solid"):
				solidList.append(i[j]);

		for i in solidList:
			writeSolidList(i, file, 1);

		file.write("}\n");


if(__name__ == "__main__"):
	exit(main(sys.argv));

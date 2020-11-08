#!/usr/bin/python

"""
MCMirror
Method from: http://wiki.vg/Game_Files

This will download all of the Minecraft files, including
libraries, assets, etc. for ALL of the versions, laying them
out in the same directory structure as on Mojang's (or M$'s)
servers. This is useful for having a local copy, as you can
just start a web server with the files, and redirect the domains.

"""

import urllib2, json, os

def mkdir_p(dir):
	try:
		os.makedirs(dir)
	except OSError as e:
		pass

def write_file(path, content):
	mkdir_p(os.path.dirname(path))
	f = open(path, "wb")
	f.write(content)
	f.close()

def download_jars(versionList, outNatives, outAssets):
	for ver in versionList:
		outClient = "s3.amazonaws.com/Minecraft.Download/versions/%s/%s.jar" % (ver, ver)
		outServerJar = "s3.amazonaws.com/Minecraft.Download/versions/%s/minecraft_server.%s.jar" % (ver, ver)
		outServerExe = "s3.amazonaws.com/Minecraft.Download/versions/%s/minecraft_server.%s.exe" % (ver, ver)
		outInfoJson = "s3.amazonaws.com/Minecraft.Download/versions/%s/%s.json" % (ver, ver)

		print "Downloading http://%s" % outClient
		try:
			clientJar = urllib2.urlopen("http://" + outClient).read()
			write_file(outClient, clientJar)
		except urllib2.HTTPError as e:
			print e

		print "Downloading http://%s" % outServerJar
		try:
			serverJar = urllib2.urlopen("http://" + outServerJar).read()
			write_file(outServerJar, serverJar)
		except urllib2.HTTPError as e:
			print e

		print "Downloading http://%s" % outServerExe
		try:
			serverExe = urllib2.urlopen("http://" + outServerExe).read()
			write_file(outServerExe, serverExe)
		except urllib2.HTTPError as e:
			print e

		print "Downloading http://%s" % outInfoJson
		try:
			infoJson = urllib2.urlopen("http://" + outInfoJson).read()
			write_file(outInfoJson, infoJson)
		except urllib2.HTTPError as e:
			print e

		info = json.loads(infoJson)
		outNatives.append(info["libraries"])
		outAssets.add(info.get("assets", "legacy"))
		

def download_libraries(verLibs):
	libList = set()
	for libs in verLibs:
		for lib in libs:
			package, name, version = lib["name"].split(":")

			preUrl = "libraries.minecraft.net/%s/%s/%s/%s-%s" % (package.replace(".", "/"), name, version, name, version)

			if "natives" in lib:
				for plat in lib["natives"]:
					natString = lib["natives"][plat]
					for arch in ["32", "64"]:
						postUrl = preUrl + "-" + natString.replace("${arch}", arch)
			else:
				postUrl = preUrl

			libList.add(postUrl + ".jar")

	for url in libList:
		lib = "https://" + url
		sha1 = lib + ".sha1"
		
		print "Downloading %s" % sha1
		try:
			rawSha = urllib2.urlopen(sha1).read()
			write_file(url + ".sha1", rawSha)
		except urllib2.HTTPError as e:
			print e

		print "Downloading %s" % lib
		try:
			rawLib = urllib2.urlopen(lib).read()
			write_file(url, rawLib)
		except urllib2.HTTPError as e:
			print e
		

def download_assets(assetList):
	
	hashes = set()

	# Get the indexes
	for idx in assetList:
		path = "s3.amazonaws.com/Minecraft.Download/indexes/%s.json" % idx;

		# Save the index file
		print "Downloading http://%s" % path
		try:
			raw = urllib2.urlopen("http://" + path).read()
			write_file(path, raw)
		except urllib2.HTTPError as e:
			print e

		# Now parse it and get all the hashes
		idxHash = json.loads(raw)

		for i in idxHash["objects"]:
			hashes.add(idxHash["objects"][i]["hash"])

	# Now download all the files
	for hash in hashes:
		dir = "resources.download.minecraft.net/%s/%s" % (hash[0:2], hash)

		print "Downloading https://%s" % dir
		raw = urllib2.urlopen("https://" + dir).read()
		write_file(dir, raw)

if __name__ == "__main__":
	versionsRaw = urllib2.urlopen("http://s3.amazonaws.com/Minecraft.Download/versions/versions.json").read()
	write_file("s3.amazonaws.com/Minecraft.Download/versions/versions.json", versionsRaw)
	versionList = [v["id"] for v in json.loads(versionsRaw)["versions"]]

	libs = []
	assets = set()
	download_jars(versionList, libs, assets)
	download_libraries(libs)
	download_assets(assets)

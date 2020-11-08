#!/usr/bin/env python
import sys
import os
import subprocess
import re

STREAM_PATTERN = re.compile(r'^\s*Stream\s+#(\d+):(\d+)(?:\(eng\))?:.+$')

def iterate_mkvs(path):
	for root, dirs, files in os.walk(path):
		for f in files:
			if f.endswith('.mkv'):
				yield os.path.join(root, f)

def get_english_streams(file):
	result = subprocess.run(['ffmpeg', '-i', file], stderr=subprocess.PIPE)
	lines = [l.rstrip() for l in result.stderr.decode('utf-8').split('\n')]
	return [m.groups() for m in [STREAM_PATTERN.match(l) for l in lines] if m]

	#return [m.groups() for m in [STREAM_PATTERN.match(l) for l in [l.rstrip() for l in subprocess.run(['ffmpeg', '-i', file], stderr=subprocess.PIPE).stderr.decode('utf-8').split('\n')]] if m]

if len(sys.argv) != 3:
	print("Usage: {0} <inpath> <outpath>".format(sys.argv[0]))
	exit(1)

#IN_PATH = "X:/Aqua Teen Hunger Force"
#OUT_PATH = "E:/athf"
IN_PATH = sys.argv[1]
OUT_PATH = sys.argv[2]

for f in iterate_mkvs(IN_PATH):
	dir, fn = os.path.split(f)
	outdir = os.path.join(OUT_PATH, os.path.relpath(dir, IN_PATH))
	os.makedirs(outdir, exist_ok = True)

	outfile = os.path.join(outdir, fn)

	x = [['-map', '{0}:{1}'.format(*s)] for s in get_english_streams(f)]

	args = ['ffmpeg', '-y', '-i', f]
	for l in x:
		args += l

	args += ['-c:v', 'copy', '-c:a', 'copy', '-c:s', 'copy', outfile]

	subprocess.run(args, stdout = sys.stdout, stderr = sys.stderr)


# Regex test strings. Every one with "(rus)" should be excluded
"""
    Stream #0:0: Video: h264 (High), yuv420p(tv, bt709), 1920x1080 [SAR 1:1 DAR 16:9], 23.98 fps, 23.98 tbr, 1k tbn, 2k tbc (default)
    Stream #0:1(rus): Audio: ac3, 48000 Hz, stereo, fltp, 192 kb/s (default)
    Stream #0:2(eng): Audio: eac3, 48000 Hz, 5.1(side), fltp, 192 kb/s
    Stream #0:3(rus): Subtitle: subrip (default)
    Stream #0:4(eng): Subtitle: subrip
    Stream #0:0(eng): Video: h264 (High), yuv420p, 1920x1080 [SAR 1:1 DAR 16:9], 23.98 fps, 23.98 tbr, 1k tbn, 47.95 tbc (default)
    Stream #0:1(rus): Audio: ac3, 48000 Hz, stereo, fltp, 192 kb/s (default)
    Stream #0:2(eng): Audio: eac3, 48000 Hz, 5.1(side), fltp, 192 kb/s
    Stream #0:3(rus): Subtitle: subrip (default)
    Stream #0:4(eng): Subtitle: subrip
    Stream #0:0(eng): Video: h264 (High), yuv420p, 1280x720 [SAR 1:1 DAR 16:9], 23.98 fps, 23.98 tbr, 1k tbn, 47.95 tbc (default)
    Stream #0:1(rus): Audio: ac3, 48000 Hz, stereo, fltp, 192 kb/s (default)
    Stream #0:2(eng): Audio: eac3, 48000 Hz, 5.1(side), fltp, 192 kb/s
    Stream #0:3(rus): Subtitle: subrip (default)
    Stream #0:4(eng): Subtitle: subrip
    Stream #0:0(eng): Video: h264 (High), yuv420p, 1920x1080 [SAR 1:1 DAR 16:9], 23.98 fps, 23.98 tbr, 1k tbn, 47.95 tbc (default)
    Stream #0:1(rus): Audio: ac3, 48000 Hz, stereo, fltp, 192 kb/s (default)
    Stream #0:2(eng): Audio: eac3, 48000 Hz, 5.1(side), fltp, 192 kb/s
    Stream #0:3(rus): Subtitle: subrip (default)
    Stream #0:4(eng): Subtitle: subrip
"""
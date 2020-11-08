#!/usr/bin/env python3

import sys
import os
import re
import subprocess
import collections
import json

SUBFILE_REGEX = re.compile(r'^(\d+)_(\w+)\.[sS][rR][tT]$')
LANGS = {
    'english': 'eng',
    'french': 'fre',
    'bulgarian': 'bul',
    'chinese': 'chi',
    'arabic': 'ara',
    'czech': 'cze',
    'danish': 'dan',
    'dutch': 'dut',
    'finnish': 'fin',
    'greek': 'gre',
    'spanish': 'spa',
    'hungarian': 'hun',
    'swedish': 'swe',
    'slovenian': 'slv',
    'polish': 'pol',
    'vietnamese': 'vie',
    'romanian': 'rum',
    'bokmal': 'nob',
    'portuguese': 'por',
    'korean': 'kor',
    'german': 'ger',
    'russian': 'rus',
    'italian': 'ita',
    'turkish': 'tur',
    'estonian': 'est',
    'indonesian': 'ind',
    'hebrew': 'heb'
}
DESTDIR = "/media/Collection1/Movies"

subinfo = collections.namedtuple('subinfo', ['num', 'langcode', 'file'])

if len(sys.argv) != 2:
    print(f'Usage: {sys.argv[0]} <movie-path>')
    exit(2)

srcdir = sys.argv[1]

subdir = os.path.join(srcdir, 'Subs')

def _find_subs(subdir):
    subs = []
    for root, dirs, files in os.walk(subdir):
        for s in files:
            m = SUBFILE_REGEX.fullmatch(s)
            if not m:
                print(f'WARNING: non-matching subtitle file {root}/{s}')
                continue

            num = int(m[1])
            lang = m[2].lower()
            path = os.path.join(root, s)

            if len(lang) != 3:
                langcode = LANGS.get(lang, 'und')
            else:
                langcode = lang

            if langcode == 'und' and lang != 'und':
                print(f'WARNING: unknown language {lang}, marking as unknown')

            subs.append(subinfo(num=num, langcode=langcode, file=path))
        break

    subs.sort(key=lambda x: x.num)
    return subs

mbase = os.path.basename(srcdir)
mfile = os.path.join(srcdir, f'{mbase}.mp4')

streaminfo = subprocess.run(
    ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', mfile],
    check=True,
    capture_output=True
)

nsub = 0
for st in json.loads(streaminfo.stdout)['streams']:
    if st['codec_type'] == 'subtitle':
        nsub += 1

if nsub != 0:
    print('File already has subtitles...')
    exit(1)

subs = _find_subs(subdir)

# for s in subs:
#     print(s)
# exit(0)

outdir = os.path.join(DESTDIR, mbase)
os.makedirs(outdir, 0o755, exist_ok=True)

ffargs = ['ffmpeg', '-y', '-i', mfile]
mapargs = ['-map', '0:v']
metaargs = []

# subtitle start index
suboffset = 1

i = 0
for s in subs:
    ffargs += ['-i', s.file]
    mapargs += ['-map', f'{i + suboffset}:s']
    metaargs.append(f'-metadata:s:s:{i}')
    metaargs.append(f'language={s.langcode}')
    i += 1

mapargs += ['-map', '0:a']
ffargs += mapargs

ffargs += ['-c:v', 'copy']
if len(subs) > 0:
    ffargs += ['-c:s', 'copy']
ffargs += ['-c:a', 'copy']

ffargs += metaargs
ffargs.append(os.path.join(outdir, f'{mbase}.mkv'))

#print(ffargs)
subprocess.run(ffargs, check=True)

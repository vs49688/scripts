#!/usr/bin/env bash
set -e

if [ $# -lt 1 ]; then
	echo "Usage: $0 <folder> [<folder> [...]]"
	exit 2
fi


export IFS=$'\n'

commands=

for folder in "$@"; do
	for i in $(find "$folder" -name '*.[Mm]4[Aa]'); do
		outdir=$PWD/$(dirname "$i")
		mkdir -p "$outdir"

		commands+="ffmpeg -y -i \"$i\" -c:a flac -compression_level 12 -c:v copy \"$outdir/$(basename "${i::-4}").flac\""
		commands+=$'\n'
	done
done

exec parallel --jobs 6 <<< $commands


#!/bin/bash -e

if [ $# -lt 1 ]; then
	echo "Usage: $0 <folder> [<folder> [...]]"
	exit 2
fi


export IFS=$'\n'

commands=

for folder in "$@"; do
	for i in $(find "$folder" -name '*.[Ff][Ll][Aa][Cc]'); do
		outdir=$PWD/$(dirname "$i")
		mkdir -p "$outdir"

		commands+="ffmpeg -y -i \"$i\" -c:a alac -c:v copy \"$outdir/$(basename "${i::-5}").m4a\""
		commands+=$'\n'
	done
done


exec parallel --jobs 6 <<< $commands


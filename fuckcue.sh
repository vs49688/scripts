#!/usr/bin/env bash

set -e
#set -x

##
# For reference:
# IFS=$'\n'; for i in $(find . -name '*.cue'); do fuckcue.sh "$i" "${i::-4}.flac" "$(dirname "$i")/split"; done
##

if [ $# -ne 3 ]; then
	echo "Usage: $0 <cuefile> <flacfile> <outdir>"
	exit 2
fi

if [ ! -f "$1" ]; then
	echo "Input file \"$1\" doesn't exist."
	exit 1
fi

if [ ! -f "$2" ]; then
	echo "Input file \"$2\" doesn't exist."
	exit 1
fi

mkdir -p "$3"

cuebreakpoints "$1" | shnsplit -O always -o flac -d "$3" "$2"
cuetag "$1" "$3"/split-track*

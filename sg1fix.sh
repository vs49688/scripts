#!/usr/bin/env bash
##
# Clean up my old Stargate SG-1 DVD Rips.
# After run: ~350GB -> 85GB
#
# Name format is:
#   Stargate.SG-1.SXXEXX.Name1.Name2.480i.DVDRip.MPEG2.AC3
#
# 1. Extract closed captions to srt
# 2. Deinterlace (480i -> 480p)
# 3. Denoise
# 4. Reencode to h264, stripping closed captions
#    along the way.
#
# SPDX-License-Identifier: CC0-1.0
##

set -e
#set -x

STARGATE_ROOT="/media/Collection1/Stargate/Stargate SG-1"
SCRATCH="/media/scratch/sg"
CCEXTRACTOR="ccextractor-0.88"
OUT_ROOT="/media/Data2/SG1"

if [ $# -ne 1 ]; then
	echo "$0 subs|encode"
	exit 2
fi

FILES=$(find "$STARGATE_ROOT" -type f -name '*.mkv' | grep MPEG2 | grep 480i | sort -u)

if [ "$1" = "subs" ]; then
	export IFS=$'\n'

	for i in $FILES; do
		filename=$(basename "$i")
		base=${filename::-4}
		subdir=$(dirname "$i")/Subs

		echo "$filename"
		mkdir -p "$subdir"
		ffmpeg -loglevel error -i "$i" -an -sn -c:v copy -f mpegts - | ${CCEXTRACTOR} \
			-stdin -o "$subdir/$base.srt" > /dev/null
	done
elif [ "$1" = "encode" ]; then
	export IFS=$'\n'

	mkdir -p "$OUT_ROOT"

	for i in $FILES; do
		filename=$(basename "$i")
		base=${filename::-4}
		subdir=$(dirname "$i")/Subs
		outbase=${base/MPEG2/x264}
		outbase=${outbase/480i/480p}

		##
		# Use h264 for DVDs:
		# - https://old.reddit.com/r/PleX/comments/8co82z/what_are_your_h265_settings_in_handbrake/
		# Resolution Notes:
		# - https://forum.doom9.org/showthread.php?t=172674
		# - 852x480 is mod4
		# - 720x480 is mod8, should be better, but need to keep the SAR
		#
		# Filter chain:
		# - yadif,hqdn3d=1:1:9:9
		#   - could add scale=852x480,setsar=1:1, but is better without
		#
		# Remove closed captions:
		# - filter_units=remove_types=6
		##
		ffmpeg -threads 6 -y -i "$i" -i "$subdir/$base.srt" \
			-map 0:v:0 -map 1:s:0 -map 0:a:0 -c:a copy -c:s copy \
			-vf "yadif,hqdn3d=1:1:9:9" -c:v libx264 -x264-params crf=18:keyint=240:min-keyint=20 \
			-bsf:v "filter_units=remove_types=6" \
			-metadata:s:s:0 language=eng \
			"$OUT_ROOT/$outbase.mkv"
	done
else
	echo "$0 subs|encode"
	exit 2
fi

exit 0

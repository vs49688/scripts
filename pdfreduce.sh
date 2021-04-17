#!/usr/bin/env sh

if [ $# -ne 3 ]; then
	echo "Usage: $0 <72|150|300> <infile.pdf> <outfile.pdf>"
	exit 2
fi

if [ $1 = "72" ]; then
	flag="-dPDFSETTINGS=/screen"
elif [ $1 = "150" ]; then
	flag="-dPDFSETTINGS=/ebook"
elif [ $1 = "300" ]; then
	flag="-dPDFSETTINGS=/prepress"
else
	echo "Usage: $0 <72|150|300> <infile.pdf> <outfile.pdf>"
	exit 2
fi

exec gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dNOPAUSE -dQUIET -dBATCH \
	$flag -sOutputFile="$3" "$2"

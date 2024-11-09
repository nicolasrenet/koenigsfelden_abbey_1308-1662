#!/bin/bash

# Nicolas Renet
# nprenet@gmail.com
#
# 2024/10
#
# Collate pageXML files with the image they describe.
#

if [[ $# -lt 1 ]]; then
	echo "USAGE: $0 <output directory>"
	exit
fi

test -d $1 || mkdir $1
echo $1
for xml in $(find ./exports -name "*.xml" | grep -Ev '(mets.xml|metadata.xml)') ; do
       	img_file=$(grep imageFilename $xml | sed 's/^.*imageFilename="\([^\"]\+\)".*$/\1/' ) ;
	echo $img_file
	if [[ -f "Digitalisate_JPG/$img_file" ]]; then
		cp Digitalisate_JPG/$img_file $xml $1
	else
		found=$(find . -name $img_file -type f | head -1)
		test -n "$found" && cp $found $xml $1
	fi

done


#!/bin/bash
# 
# NPR, 11.2026
#
# Building  parallel transcriptions out of the abbreviated labels.
#
# ! Assume that image and filenames have been fixed for inconsistencies first.
#
ROOT=$(realpath .)
WORKDIR=${ROOT}/curation_tools_and_files
RECTOS=1.collated_xml_recto
DIDIP=2.didip

test -d "${DIDIP}" || mkdir -p ${DIDIP}

rm $(ls ${WORKDIR}/${DIDIP}/*.{jpg,xml,json} |grep -v '\.lines\.')
${WORKDIR}/bin/to_didip.py --verbosity 2 --output_format page --output_dir ${WORKDIR}/${DIDIP} $(ls ${WORKDIR}/${RECTOS}/*.xml|grep -Ev '_v(_?([0-9]+))?\.xml')

page_xml_to_json_check=$(whereis page_xml_to_json)
test -n "${page_xml_to_json_check/*:/}" || {
	echo "page_xml_to_json script not found: check that segtformats python package has been installed!"; 
	echo "Skipping PageXML → JSON conversion.";
	exit
}

# PageXML → JSON
cd ${WORKDIR}/${DIDIP}
page_xml_to_json --file_paths *.xml --out auto --repair --validate --overwrite_existing ;
# Linking images
for json in $(ls *.json| grep -v '\.lines\.'); do
	test -L ${json%.json}.jpg || ln -s ../${RECTOS}/${json%.json}.jpg
done

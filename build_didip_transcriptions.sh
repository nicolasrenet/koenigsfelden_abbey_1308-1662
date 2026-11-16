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
INPUT=${WORKDIR}/1.collated_xml_verso
DIDIP=${WORKDIR}/2.didip

test -d "${DIDIP}" || mkdir -p ${DIDIP}

${WORKDIR}/bin/to_didip.py --verbosity 2 --output_format page --output_dir ${DIDIP} $(ls ${INPUT}/*.xml|grep -Ev '_v(_?([0-9]+))?\.xml')

page_xml_to_json_check=$(whereis page_xml_to_json)
test -n "${page_xml_to_json_check/*:/}" || {
	echo "page_xml_to_json script not found: check that segtformats python package has been installed!"; 
	echo "Skipping PageXML → JSON conversion.";
	exit
}

# PageXML → JSON
cd ${DIDIP}
page_xml_to_json --file_paths *.xml --out auto --repair --validate --overwrite_existing ;
# Linking images
for img in ${INPUT}/*.jpg; do
	img_name=$(basename $img)
	if [[ -f "${img_name%.jpg}.json" || -f "${img_name%.jpg}.xml}" ]]; then
		test -L $img_name || ln -s $img
	fi
done

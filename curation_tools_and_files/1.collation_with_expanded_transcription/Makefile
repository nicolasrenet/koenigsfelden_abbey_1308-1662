

BIN=../bin
TEIS=../../all_teis
RAW_XML_DIR=../0.collated_xml_pages_raw

raw_xmls := $(wildcard $(RAW_XML_DIR)/*.xml)
xmls := $(notdir $(raw_xmls))


.DEFAULT: all 

all:
	for tei in $(TEIS)/[Uu]-17*.xml; do $(BIN)/tei_to_collated_lines.py $${tei} $(RAW_XML_DIR) ; done


.PHONY: clean



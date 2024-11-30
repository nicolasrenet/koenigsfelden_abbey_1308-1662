

BIN=../bin
RAW_XML_DIR=../0.collated_xml_pages_raw

expanded_xmls := $(notdir $(wildcard $(RAW_XML_DIR)/*.xml))


.DEFAULT: all 


all: $(expanded_xmls) 
	


%.xml:: $(RAW_XML_DIR)/%.xml
	$(BIN)/expand_pagexml.py $< $@ 


.PHONY: clean

clean:
	rm -f *.xml

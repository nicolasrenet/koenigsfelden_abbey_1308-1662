

BIN=../bin
RAW_XML_DIR=../0.collated_xml_pages_raw

raw_xmls := $(wildcard $(RAW_XML_DIR)/*.xml)
xmls := $(notdir $(raw_xmls))


.DEFAULT: all

all: $(xmls)



%.xml :: $(RAW_XML_DIR)/%.xml
	$(BIN)/cleanup.py $< $@


.PHONY: clean

clean:
	rm -f *.xml *.jpg



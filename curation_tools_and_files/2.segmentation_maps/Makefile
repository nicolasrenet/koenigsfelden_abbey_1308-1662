

BIN=../bin
IMG_SRC=../0.collated_xml_pages_raw

xmls := $(wildcard *.xml)
maps := $(addsuffix .map.png, $(basename $(xmls)))


.DEFAULT: all


.PHONY: clean

all: $(maps)


%.map.png: %.xml
	$(BIN)/generate_line_seg_visuals.py $< $(IMG_SRC)

clean:
	rm -f *.map.png

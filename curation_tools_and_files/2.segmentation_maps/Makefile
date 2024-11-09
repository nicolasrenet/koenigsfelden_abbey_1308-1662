

BIN=../bin
IMG_SRC=../1.collation_with_expanded_transcription

xmls := $(wildcard *.xml)
maps := $(addsuffix .map.png, $(basename $(xmls)))


.DEFAULT: all


.PHONY: clean

all: $(maps)


%.map.png: %.xml
	$(BIN)/generate_line_seg_visuals.py $< $(IMG_SRC)

clean:
	rm -f *.map.png

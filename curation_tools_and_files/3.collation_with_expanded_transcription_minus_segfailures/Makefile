 
.DEFAULT: all

.PHONY: clean remove_failures remove_versos



all_xmls := $(notdir $(shell ls ../1.collation_with_expanded_transcription/*.xml))
all_jpgs := $(addsuffix .jpg, $(basename $(notdir $(shell ls ../1.collation_with_expanded_transcription/*.xml))))

to_remove_xmls := $(notdir $(shell ls ../2.segmentation_failures/*.xml))
to_remove_jpgs := $(addsuffix .jpg, $(basename $(to_remove_xmls)))


remove_failures:
	rm -f $(to_remove_xmls) $(to_remove_jpgs)

remove_versos:
	rm -f *_v.* *_v_*

all: $(all_xmls) $(all_jpgs) remove_failures remove_versos

%.xml :: ../1.collation_with_expanded_transcription/%.xml
	ln -s $<

%.jpg :: ../1.collation_with_expanded_transcription/%.jpg
	ln -s $<



clean:
	rm -f *.xml *.jpg

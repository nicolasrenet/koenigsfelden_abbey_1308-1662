A curated version of Thomas Hödel's somewhat raw data found in Zenodo:

* Original metadata: https://htr-united.github.io/share.html?uri=782b1e7da
* Files: https://zenodo.org/record/5179361

The final dataset state results from the resulting operations:

+ discard pageXML files that cannot be reliably paired with an image (because the Trankscribus mapping has been lost)
+ handwriting abbreviations have been expanded, using the TEI as a source
+ glyphs and junk that is obviously irrelevant for HTR work removed from the transcriptions
+ diacritics have been kept (they can easily be removed by a consumer program)
+ discard pages with failed line polygons

All steps but the last one are automated (scripts and Makefiles).


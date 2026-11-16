A curated version of Tobias Hödl dataset:

* Original metadata: https://htr-united.github.io/share.html?uri=782b1e7da
* Files: https://zenodo.org/record/5179361

The final dataset state results from the resulting operations:

+ discard pageXML files that cannot be reliably paired with an image (because the Trankscribus mapping has been lost)
+ ... (to be documented)


11.2026: DiDip-style parallel transcriptions

Big clean-up and homogenization that uses recent work on segmentation and transcription guidelines.

```bash
TOOLS=$(realpath ./curation_tools_and_files)
COLLATION=${TOOLS}/1.collation_with_abbreviated_transcription
cd ${TOOLS}/bin
./to_didip.py --verbosity 2 --output_format page --output_dir ${TOOLS}/didip  ${COLLATION}/*.xml
cd ${TOOLS}/didip
page_xml_to_json --file_paths *.xml --out auto --repair --validate --overwrite_existing
```

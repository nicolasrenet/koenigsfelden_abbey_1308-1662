
## Collation, clean-up

```bash
for i in ../3.collation_with_expanded_transcription_minus_segfailures/*.xml ; do name=$(basename $i) ; ln -s ../1.collation_with_abbreviated_transcription/$name ; done
```

```
mkdir bt3
mkdir bt5
$PYTHONPATH/bin/ddp_line_detect.py -img_paths *_r.jpg -img_suffix '.jpg' -layout_suffix '.xml' -verbosity 2 -apply_model_thresholds 0 -box_threshold .3 -output_dir bt3 -mask_threshold .5 -device gpu
$PYTHONPATH/bin/ddp_line_detect.py -img_paths *_r.jpg -img_suffix '.jpg' -layout_suffix '.xml' -verbosity 2 -apply_model_thresholds 0 -box_threshold .5 -output_dir bt5 -mask_threshold .5 -device gpu
for i in bt3/*.lines.pred.json ; do ln -s $i ; done
for i in *.lines.pred.json ; do $PYTHONPATH/bin/align_seg_htr.py -segfile_path $i -output_file ${i%.lines.pred.json}.htr.bt3.aligned.json -overwrite_existing 1 -verbosity 2; done
rm -f *.lines.pred.json
for i in bt5/*.lines.pred.json ; do ln -s $i ; done
for i in *.lines.pred.json ; do $PYTHONPATH/bin/align_seg_htr.py -segfile_path $i -output_file ${i%.lines.pred.json}.htr.bt5.aligned.json -overwrite_existing 1 -verbosity 2; done
```
For reviewing the alignment:

```
=======
## DiDip segmentation 

```sh
export PYTHONPATH=.
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True $PYTHONPATH/bin/ddp_line_detect.py --img_paths *_r.jpg --img_suffix '.jpg' --layout_suffix '.xml' --verbosity 2 --apply_model_thresholds --device gpu 
```

## Align DiDip segmentation with XML (HTR) ground-truths

```sh
export PYTHONPATH=.
$PYTHONPATH/bin/align_seg_htr.py --segfile_paths *.lines.pred.json --htr_suffix .xml --output_suffix .hf10.aligned.json --overwrite_existing 1 --verbosity 2
```

For reviewing the alignment:

```sh
cd $CHLAT_DIR
FLASK_flat=1 FLASK_fsdb_root='/home/nicolas/extra_data_storage/koenigsfelden_abbey_1308-1662/curation_tools_and_files/3.collation_with_abbreviated_transcriptions_minus_segfailures' FLASK_charter_img_suffix='jpg' FLASK_pregt_htr_suffix='htr.bt5.aligned.json' flask --app charter_annotation run -p 5001
```



```bash
for i in ../3.collation_with_expanded_transcription_minus_segfailures/*.xml ; do name=$(basename $i) ; ln -s ../1.collation_with_abbreviated_transcription/$name ; done
```

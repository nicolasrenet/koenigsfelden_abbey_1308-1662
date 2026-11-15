All pairs, minus the verso pages and the failed transcriptions:


~~~~~~~~~~bash
for i in $(ls ../1.collation_with_expanded_transcription/*.xml | grep -Ev '_v(_|\.)') ; do stem=$(basename $i) ; if [ ! -f "../2.segmentation_failures/$stem" ] ;  then ln -s $i ; fi ; done
for i in *.xml ; do ln -s ../1.collation_with_expanded_transcription/${i%.xml}.jpg ; done
~~~~~~~~~~~~~~~~

Or:

~~~~~~bash
for i in ../2.no_transcriptions/*.xml ; do name=$(basename $i); img_name=${name%.xml}.jpg ; test -e "$name" && (rm $name $img_name) ; done
for i in ../2.segmentation_failures/*.xml ; do name=$(basename $i); img_name=${name%.xml}.jpg ; test -e "$name" && (rm $name $img_name) ; done
~~~~~~~~~~


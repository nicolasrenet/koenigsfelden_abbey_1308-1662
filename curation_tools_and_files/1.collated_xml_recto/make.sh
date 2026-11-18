# keep only rectos with existing transcription
for i in $(ls ../0.collated_xml/*.xml|grep -Ev '_v(_?([0-9]+))?\.xml') ; do ln -s $i ; ln -s ${i%.xml}.jpg ; done
for stem in $(cat ../no_transcriptions.txt) ; do test -f "${stem}.xml" && { echo "${stem}.xml" ; rm -f ${stem}.{jpg,xml} ;} ; done

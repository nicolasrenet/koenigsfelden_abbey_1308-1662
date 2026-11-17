for i in $(ls ../0.collated_xml/*.xml|grep -Ev '_v(_?([0-9]+))?\.xml') ; do ln -s $i ; ln -s ${i%.xml}.jpg ; done
for i in $(ls ../no_transcriptions) ; do name=$(basename $i) ; test -f "${name}.xml" && { echo $name ; rm -f $name.{jpg,xml} ;} ; done

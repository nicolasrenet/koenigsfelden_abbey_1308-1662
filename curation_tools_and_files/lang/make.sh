(for i in $(grep ' ut ' ../1.collation_with_abbreviated_transcription/*.xml) ; do echo "${i/:*/}" |grep xml ; done)| uniq | sed s'/^.*\(U-.*\.xml\).*$/\1/'

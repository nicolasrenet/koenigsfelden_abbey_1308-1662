#!/usr/bin/env python3

import xml.etree.ElementTree as ET
from pathlib import Path
import sys
import re


USAGE=f"USAGE: {sys.argv[0]} <source page xml> <target page xml> ]"

def clean_up( transcr: str ) -> str:
    transcr = transcr.replace('&#13','')
    transcr = transcr.replace('\u200b','')
    transcr = transcr.replace('\uf2f7','')
    transcr = transcr.replace(u'ꝫc̄','etc')
    transcr = transcr.replace(u'','Ü')
    transcr = re.sub(r'  +',' ', transcr)
    return transcr


def expand( txt, abbreviations):
    curr, new = 0, ''
    if not abbreviations or txt is None:
        return ''
    for offset,length,exp in abbreviations:
        offset, length = int(offset), int(length)
        new += (txt[curr:offset] + exp )
        curr = offset + length
    return new + txt[curr:]
    

if __name__ == "__main__":

    if len(sys.argv) < 3:
        print(USAGE)
        sys.exit()

    page_path = Path(sys.argv[1])
    if not Path(sys.argv[1]).exists():
         print(f"Could not find {sys.arv[1]}")


    ns = { 'pc': "http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15" }
    ET.register_namespace('', ns['pc']

    with open( page_path, 'r') as page:
        print(page_path)

        page_tree = ET.parse( page )

        page_root = page_tree.getroot()
        
        for textRegionElt in page_root.findall('.//pc:TextRegion', ns):
            region_text = []
            for textLineElt in textRegionElt.findall('./pc:TextLine', ns):

                abbreviations = re.findall(r'abbrev *{ *offset:(\d+); *length:(\d+); *expansion:([^;]+); *}', textLineElt.get('custom'))
                txtLineText = textLineElt.find('./pc:TextEquiv/pc:Unicode', ns)
                if txtLineText is not None and txtLineText.text is not None:
                    transcription = clean_up( expand( txtLineText.text, abbreviations ))
                    txtLineText.text = transcription
                    region_text.append( transcription )

            region_text_unicode = textRegionElt.find('./pc:TextEquiv/pc:Unicode', ns)
            if region_text_unicode is not None:
                region_text_unicode.text = '\n'.join(region_text)

        page_tree.write(Path(sys.argv[2]).name, encoding='utf-8')



                

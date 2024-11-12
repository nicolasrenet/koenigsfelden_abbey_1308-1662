#!/usr/bin/env python3

import xml.etree.ElementTree as ET
from pathlib import Path
import sys
import re


USAGE=f"USAGE: {sys.argv[0]} <page.xml> [ <output page.xml> ]"

def clean_up( transcr: str ) -> str:
    transcr = transcr.replace(u'✳','')
    transcr = transcr.replace('&#13','')
    transcr = transcr.replace('\u200b','')
    transcr = transcr.replace('\uf2f7','')
    transcr = re.sub(r'  +',' ', transcr)
    return transcr


if __name__ == "__main__":

    if len(sys.argv)<2:
        print(USAGE)
        sys.exit()

    page_path = Path( sys.argv[1] )
    with open( page_path, 'r') as page:

        page_tree = ET.parse( page )
        ns = { 'pc': "http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15" }

        page_root = page_tree.getroot()
        
        for textRegionElt in page_root.findall('.//pc:TextRegion', ns):
            region_text = []
            for textLineElt in textRegionElt.findall('./pc:TextLine', ns):

                if textLineElt is None:
                    continue
                unicodeElt = textLineElt.find('./pc:TextEquiv/pc:Unicode', ns)

                if unicodeElt is None:
                    continue

                if unicodeElt.text is None:
                    continue

                new_text = clean_up( unicodeElt.text )
                textLineElt.find('./pc:TextEquiv/pc:Unicode', ns).text = new_text
                region_text.append( new_text )

            region_text_unicode = textRegionElt.find('./pc:TextEquiv/pc:Unicode', ns)
            if region_text_unicode is not None:
                region_text_unicode.text = '\n'.join( region_text )

        output_file = sys.argv[2] if len(sys.argv)>2 else page_path.with_suffix('.tmp').name

        page_tree.write(output_file, encoding='utf-8')   




                

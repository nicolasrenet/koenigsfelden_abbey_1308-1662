#!/usr/bin/env python3

"""
This script is intended for use on **abbreviated** transcriptions:

- expand the abbreviations
- replace abbreviation annotations with expansion annotations (offset, length, <original string>)
- very basic clean-up, that does not affect the said offsets
"""

import xml.etree.ElementTree as ET
from pathlib import Path
import sys
import re
from typing import List,Tuple


USAGE=f"USAGE: {sys.argv[0]} <source page xml> <target page xml> ]"

def clean_up( transcr: str ) -> str:
    #transcr = transcr.replace('&#13','') # not needed for line transcriptions
    transcr = re.sub(r'[\u00a0\u2000-\u200b\u202f]',' ',transcr) # thin space
    
    # koenigsfelden transcriber forgot some of those
    # in the text -> character-count keeping filtering
    transcr = transcr.replace(u'ꝫc̄','etc')
    transcr = transcr.replace(u'','Ü')
    return transcr


def expand( txt, masks, debug=False):
    """
    From a list of tuples (offset, length, <expanded text>), expand
    the abbreviation contained in the input text.

    Args:
        txt (str): the abbreviated text.
        masks (Tuple[int,int,str]): a list of tuples (offset, length, <expanded text>).
        debug (bool): return expanded bits like t<hi>s
    Returns:
        Tuple[str,List[Tuple[int,int,str]]]: A triplet with the expanded text and a list of tuples
            storing the new (offset, length) information for the expanded part, relative
            to the output string, as well as the original, abbreviation string.
    """
    input_cursor, new = 0, ''
    output_masks = []
    output_offset = 0
    if txt is None:
        return ('',[])
    if not masks:
        return (txt,[])
    for abb_offset,abb_length,abb_exp in masks:
        abb_offset, abb_length = int(abb_offset), int(abb_length)
        new += txt[input_cursor:abb_offset] + (f'<{abb_exp}>' if debug else abb_exp )
        input_cursor = abb_offset + abb_length
        output_masks.append((abb_offset+output_offset,len(abb_exp), txt[abb_offset:abb_offset+abb_length]))
        output_offset += len(abb_exp)-abb_length
    return (new + txt[input_cursor:], output_masks)

    
def rebuild_custom_annotations( annotations: str, masks:List[Tuple[int,int,str]]):
    """
    Given XML annotation string of the kind:
    
    ```xml
    readingOrder {index:0;} person {offset:0; length:62;ref:per000089;} abbrev {offset:29; length:1;expansion:et;} \
    abbrev {offset:56; length:2;expansion:gra;} abbrev {offset:66; length:4;expansion:omni;} ... 
    ```
    Replace abbreviation masks with provided list; annotations that contain an offset
    -such as 'person'-are removed (they become obsolete); other annotations are kept. 
    
    """
    if not masks:
        return annotations
    pairs = re.findall(r'(\w+) *{([^}]+)}', annotations)
    if pairs:
        pairs = [ p for p in pairs if p[0]!='abbrev' and p[1].find('offset')<0 ]
        pairs += [ ('expansion', f'offset:{m[0]}; length:{m[1]}; abbrev:{m[2]};') for m in masks ]
    return ' '.join([ f'{name} {{{value}}}' for (name,value) in pairs ])

if __name__ == "__main__":

    if len(sys.argv) < 3:
        print(USAGE)
        sys.exit()

    page_path = Path(sys.argv[1])
    if not Path(sys.argv[1]).exists():
         print(f"Could not find {sys.arv[1]}")


    ns = { 'pc': "http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15" }
    ET.register_namespace('', ns['pc'] )

    with open( page_path, 'r') as page:
        print(page_path)

        page_tree = ET.parse( page )

        page_root = page_tree.getroot()
        
        for textRegionElt in page_root.findall('.//pc:TextRegion', ns):
            region_text = []
            for textLineElt in textRegionElt.findall('./pc:TextLine', ns):

                abb_masks = re.findall(r'abbrev *{ *offset:(\d+); *length:(\d+); *expansion:([^;]+); *}', textLineElt.get('custom')) if 'custom' in textLineElt.keys() else []
    
                txtLineText = textLineElt.find('./pc:TextEquiv/pc:Unicode', ns)
                if txtLineText is not None and txtLineText.text is not None:

                    text_new, abb_masks_new = expand( txtLineText.text, abb_masks )
                    
                    transcription = clean_up( text_new )
                    # clean-up should not mess with the offsets!
                    assert len(transcription)==len(text_new)
                    txtLineText.text = transcription
                    region_text.append( transcription )
                    
                    if 'custom' in textLineElt.keys() and abb_masks_new != []:
                        textLineElt.set('custom',rebuild_custom_annotations(textLineElt.get('custom'), abb_masks_new))


            region_text_unicode = textRegionElt.find('./pc:TextEquiv/pc:Unicode', ns)
            if region_text_unicode is not None:
                region_text_unicode.text = '\n'.join(region_text)

        page_tree.write(Path(sys.argv[2]).name, encoding='utf-8')



                

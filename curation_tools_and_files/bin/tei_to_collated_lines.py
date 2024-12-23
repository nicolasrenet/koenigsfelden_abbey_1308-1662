#!/usr/bin/env python3

import xml.etree.ElementTree as ET
from pathlib import Path
import sys
import re


USAGE=f"USAGE: {sys.argv[0]} <tei.xml> [ <page_source_dir> ]"

def clean_up( transcr: str ) -> str:
    transcr = transcr.replace(u'✳','.')
    transcr = transcr.replace('&#13','')
    transcr = transcr.replace('\u200b','')
    transcr = transcr.replace('\uf2f7','')
    #transcr = transcr.replace('¶','')
    #transcr = transcr.replace(u'dˀ','der')
    transcr = transcr.replace(u'ꝫc̄','et cetera')
    transcr = re.sub(r'  +',' ', transcr)
    return transcr.strip()



def tei_path_to_line_dict( tei_path: str ) -> dict:
    """ Read TEI and construct a dictionary with pages as keys;
    Each page entry is itself a line dictionary, where the text
    has all abbreviations expanded.
    """

    line_dict = {}
    current_line = ''
    page_source_image = ''

    def text_collect( elt: ET.Element, ns, top=True, tab='') -> str:

            nonlocal current_line

            #print(tab + f"text_collect( {elt.tag} )")

            if elt.tag == "{{{}}}lb".format(ns['pc']):
                line_id = re.sub(r'^#facs_\d{1,}_(.+)', r'\1', elt.get('facs'))
                current_line = line_id
                line_dict[page_source_image][current_line]=''

            text = ''
            if elt.text is not None and not top: #and re.match(r'^\s*$', elt.text) is None:
                #text += elt.text 
                #print(tab + 'TEXT:', elt.text) 
                line_dict[page_source_image][current_line] += elt.text
            # collect inner nodes
            for child in elt.findall('./'):
                # skip abbreviations
                if child.tag == '{{{}}}abbr'.format(ns['pc']):
                    continue
                #subtext = text_collect( child, ns, False, tab+'    ' )
                text_collect( child, ns, False)
                #text += subtext
                #line_dict[current_line] += subtext 
            if elt.tail is not None and not top: # and re.match(r'^\s*$', elt.tail) is None:
                #text += ' '+elt.tail 
                #print(tab + 'TAIL:', elt.tail )
                line_dict[page_source_image][current_line] += elt.tail
            
            return text

    with open( tei_path, 'r') as tei:

        tei_tree = ET.parse( tei )
        ns = { 'pc': "http://www.tei-c.org/ns/1.0" }
        tei_root = tei_tree.getroot()
        body = tei_root.find('.//pc:text/pc:body', ns)
        page_source_image = ''
        for elt in body.iter():
            if elt.tag == "{{{}}}pb".format( ns['pc'] ):
                page_source_image = elt.get('source') 
                # assume that all source pages and images have been renamed at this stage
                page_source_image.replace('u-17', 'U-17')
                line_dict[page_source_image]={}
                print( page_source_image)
            elif elt.tag == "{{{}}}p".format( ns['pc'] ):
                line_id = ''
                text_collect( elt, ns )
        return line_dict 



def page_xml_expand_text( page_path: str, line_dict ) -> dict:
    """ In a pageXML file, replace all transcriptions with their
    expanded version, using the page dictionary provided.
    """
    with open( page_path, 'r') as page:
        print(page_path)
        page_tree = ET.parse( page )
        ns = { 'pc': "http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15" }

        page_root = page_tree.getroot()
        
        for textRegionElt in page_root.findall('.//pc:TextRegion', ns):
            region_text = []
            for textLineElt in textRegionElt.findall('./pc:TextLine', ns):

                line_id = textLineElt.get('id')
                #print(line_id)
                if line_id in line_dict:
                    new_transcription = line_dict[ line_id ]
                    txtLineElt = textLineElt.find('./pc:TextEquiv/pc:Unicode', ns)
                    #print("AFTER:", textLineElt.find('./pc:TextEquiv/pc:Unicode', ns).text)
                    clean_transc = clean_up(new_transcription)
                    txtLineElt.text = clean_transc
                    #print(f"[{new_transcription}]", clean_transc)
                    region_text.append( clean_transc )

            region_text_unicode = textRegionElt.find('./pc:TextEquiv/pc:Unicode', ns)
            if region_text_unicode is not None:
                region_text_unicode.text = '\n'.join(region_text)


        return page_tree



if __name__ == "__main__":

    if len(sys.argv) < 2:
        print(USAGE)
        sys.exit()

    page_source_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('.')
    line_dict = tei_path_to_line_dict( sys.argv[1] )

    #print(list(sorted(line_dict[lkd].keys()) for lkd in line_dict.keys()))
    #print(line_dict)

    for page_stem in line_dict.keys():

        page_source = page_source_dir.joinpath(f'{page_stem}.xml')
        if not page_source.exists():
            print(f"Could not find {page_source}")
            continue
        new_tree = page_xml_expand_text( str(page_source), line_dict[ page_stem ]  )

        new_tree.write(f"{page_stem}.xml", encoding='utf-8')



                

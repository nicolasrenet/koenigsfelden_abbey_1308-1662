#!/usr/bin/env python3
import sys
import re
from pathlib import Path
import xml.etree.ElementTree as ET
import argparse
import logging
import pytest

logging_format="%(asctime)s - %(levelname)s: %(filename)s: %(funcName)s - %(message)s"
logging_levels = {0: logging.ERROR, 1: logging.WARNING, 2: logging.INFO, 3: logging.DEBUG }
logging.basicConfig( level=logging.INFO, format=logging_format, force=True )
logger = logging.getLogger(__name__)


'''
A comprehensive script to generate labels with parallel transcriptions from raw Koenigsfelden files.

+ Use XML custom annotations to Convert abbreviated transcriptions to Didip-style `<what you read>|<what you see>` labels.
+ Enforce DiDip-style character set.


Input data:

Page XML with

+ abbreviation annotations in XML, eg.

  ```
  abbrev {offset: 132; length: 3; expansion:'ers}`
  ```

+ some abbreviation expansions have internal spaces (\u0020)!

  ```
  et\u0020cetera
  hochlöblichen\u0020herren
  manu\u0020propria
  meinen\u0020hochlöblichen\u0020gnädigen\u0020herren
  meiner\u0020gnädigen\u0020hochlöblichen
  meiner\u0020hochlöblichen\u0020gnädigen\u0020hochwohlgeborenen\u0020herren
  meines\u0020hochgeehrten\u0020herrn
  meine\u0020gnädigen\u0020herren
  meine\u0020gnädigen\u0020hochlöblichen\u0020herren
  meine\u0020hochgeachteten
  meine\u0020hochlöblichen\u0020gnädigen\u0020herren
  mines\u0020gnädigen\u0020herrn
  Ruͦdolf\u0020
  \u0020cetera
  \u0020Habsburg
  \u005cu0020cetera
  und\u0020
  ```

  - some can be rewritten eg. `et\u0020cetera` → `etc`
  - some can be ignored altogther eg. `meine\u0020hochlöblichen\u0020gnädigen\u0020herren`,
    wich involves suppressing the abbreviation annotation (while keeping the rather harmless 
    abbreviation mark in the text)

'''


def to_didip_charset( transcr: str ) -> str:
    """
    Enforce a reduced charset that complies with DiDip transcription guidelines (ASCII + generic abbreviation mark)
    """

    # 1. Deletions: superscript and diacritic marks
    superscript_charset = [['\u0363','\u0368','\u0369','\u0364','\u036a','\u0365','\u036b','\u0366','\u036c','\u036d','\u0367','\u036e','\u036f']]
    # character 0x304 is the upper bar, that allows for rewriting of abbreviation marks
    diacritic_charset = [ ["'","ʼ"] + [ chr(c) for c in range(0x300,0x316) if c not in [ 0x304, 0x305 ] ] + [ '\u0321', '\u0322', '\u0327', '\u0328', '\u1dd0'] ]
    punctuation_charset = [ [',',';'] ]

    for c in superscript_charset[0] + diacritic_charset[0] + punctuation_charset[0]:
        transcr = transcr.replace(c, '')

    # 2. Substitutions
    junk = [ '&#13', '\u200b', '\uf2f7' ]

    character_classes = [
        '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
        ['A','Á','Â','Ã','Ä','Å','Ă','Ą','À', 'Ā'], ['a','á','â','ã','ä','å','ă','ą','à','ā'],
        'B', 'b',
        ['C','Ç','Ć','Ĉ','Ċ','Č'], ['c','ç','ć','ĉ','ċ','č'],
        ['D','Ð','Ď','Đ'], ['d','ð','ď','đ'],
        ['E','È','É','Ê','Ë','Ē','Ĕ','Ė','Ę','Ě'], ['e','è','é','ê','ë','ĕ','ė','ę','ě'],
        'F', 'f',
        ['G','Ĝ','Ğ','Ġ','Ģ'], ['g','ĝ','ğ','ġ','ģ','ḡ'],
        ['H','Ĥ','Ħ'], ['h','ĥ','ħ'],
        ['I','Ì','Í','Î','Ï','Ĩ','Ī','Ĭ','Į','İ'], ['i','ì','í','î','ï','ĩ','ī','ĭ','į','ı'],
        ['J','Ĵ', 'Ɉ'], ['j','ȷ','ĵ','ɉ'],
        ['K','Ķ'], ['k','ķ','ĸ'],
        ['L','Ĺ','Ļ','Ľ','Ŀ','Ł','£'], ['l','ĺ','ļ','ľ','ŀ','ł'],
        'M', 'm',
        ['N','Ñ','Ń','Ņ','Ň','Ŋ'], ['n','ñ','ń','ņ','ň','ŉ','ŋ'],
        ['O','Ò','Ó','Ô','Õ','Ö','Ō','Ŏ','Ő'], ['o','ò','ó','ô','õ','ö','ō','ŏ','ő','°'],
        'P', 'p',
        'Q', 'q',
        ['R','Ŕ','Ŗ','Ř','Ꝛ'], ['r','ŕ','ŗ','ř','ꝛ'],
        ['S','Ś','Ŝ','Ş','Š','ß'], ['s','ś','ŝ','ş','š','ſ','ẜ','\uf2f7'], # last is German schilling sign
        ['T','Ţ','Ť','Ŧ'], ['t','ţ','ť','ŧ','ꝷ'],
        ['U','Ù','Ú','Û','Ü','Ũ','Ū','Ŭ','Ů','Ű','Ų'], ['u','ù','ú','û','ü','ũ','ū','ŭ','ů','ű','ų'],
        'V', 'v',
        ['W','Ŵ','Ẅ'], ['w','ŵ','ẅ'],
        'X', 'x',
        ['Y','Ȳ','Ý','Ÿ','Ŷ','Ẏ'], ['y','ȳ','ý','ÿ','ŷ','ẏ','ẙ'],
        ['Z','Ź','Ż','Ž','Ẑ', 'Ƶ', 'Ʒ', 'Ȥ'], ['z','ź','ż','ž', 'ẑ', 'ƶ', 'ʒ', 'ȥ'],
        # each to be replaced with a single generic abbreviation mark (%)
        ['%', 'ƺ','Ꝯ','ꝯ','Ꝫ','ꝫ','ȝ','₰','ꝰ','ꝭ','&','₎','Ꜿ','כּ','ˀ','\u0304'],
        ['$', '✳', '¶'],
        ['-','¬'],
    ]

    # those characters should not be there in the first place :(
    private_unicode_dict = {'': 'v'}

    character_to_character_dict = { c:(cc[0] if type(cc) is list else cc)for cc in character_classes for c in cc }

    # each to be replaced with the combination of a letter and an abbreviation mark
    hybrid_abbreviation_dict = { 'ē': 'e%', 'Ꝓ':'P%','Ꝑ':'P%','ꝓ':'p%', 'ꝑ':'p%', 'Ꝗ':'Q%','Ꝙ':'Q%', 'ꝗ':'q%','ꝙ':'q%', 'Ꝝ':'r%', 'ꝝ':'r%', 'ꝶ':'R%', 'ꝵ':'r%', 'ꝷ': 't%', 'Ꝟ':'V%', 'ꝟ':'v%' }

    for jk in junk:
        transcr = transcr.replace( jk, '')
    for (k,v) in private_unicode_dict.items():
        transcr = transcr.replace(k,v)
    for (k,v) in character_to_character_dict.items():
        transcr = transcr.replace(k,v)
    for (k,v) in hybrid_abbreviation_dict.items():
        transcr = transcr.replace(k,v)

    transcr = re.sub(r' +',' ', transcr).strip()
    return transcr

def expand_text( orig_txt, masks ):
    # fix annoying inconsistencies in Hödel's use of special characters
    #orig_txt = orig_txt.replace('ē','ē')
    # construct expanded version
    expanded_transcription = ''
    cursor = 0
    for mask in masks:
        start, substituded_length, expansion_str = mask
        expanded_transcription += orig_txt[cursor:start] + expansion_str
        cursor = start + substituded_length
    expanded_transcription += orig_txt[cursor:]
    return expanded_transcription

def zip_transcriptions( abbr, exp ):

    abbr_tokens = abbr.split(' ')
    exp_tokens = exp.split(' ')
    return ' '.join([ f'[{et}|{at}' if et != at else et for (et,at) in zip( exp_tokens, abbr_tokens )])
   


if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog='expand_pagexml.py')
    parser.add_argument('input_xml', help='Input PageXML file path.', nargs='+')
    parser.add_argument('--output_dir', default='', help='Directory in which the resulting files (XML or line databases) are to be written.')
    parser.add_argument('--mask_del', action='store_true')
    parser.add_argument('--output_format', choices=['page', 'plain', 'none'], default='page', help="Output format: PageXML, plain text, or no output.")
    parser.add_argument('--standard_output', action='store_true', help="Print on standard output - default writes a JSON file.")
    parser.add_argument('--verbosity', choices=[0,1,2,3], type=int, help="Verbosity level.", default=2)
    args = parser.parse_args()

    logging.basicConfig( level=logging_levels[args.verbosity], format=logging_format, force=True )

    target_dirpath = None
    if args.output_dir:
        target_dirpath = Path( args.output_dir )
        if not target_dirpath.is_dir():
            logger.info(f"Could not find {args.output_dir}")
            sys.exit()


    ns = { 'pc': "http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15" }
    ET.register_namespace('', ns['pc'] )
    abbreviation_re = re.compile( r'.+offset: *(\d+).+length: *(\d+).+expansion:([^;]+);.+' )

    for page_file in args.input_xml:
        with open(Path(page_file)) as page:
            logger.info( page_file )
            page_tree = ET.parse( page )
            page_root = page_tree.getroot()
            pageElts = page_root.findall('.//pc:Page', ns)

            for p in pageElts:
                page_root.remove( p )

            for pageElt in pageElts:
                imageFilename = pageElt.get('imageFilename')
                xmlFilename = imageFilename.replace('.jpg','.xml')
                text_line_transcriptions = []
                for textRegionElt in pageElt.findall('.//pc:TextRegion', ns):
                    for textLineElt in textRegionElt.findall('./pc:TextLine', ns):
                        custom_annotation = textLineElt.get('custom')
                        logger.debug(custom_annotation)
                        abbrev_masks = []
                        textLineText = textLineElt.find('./pc:TextEquiv/pc:Unicode', ns)
                        if textLineText is not None:

                            original_transcription = ''.join(textLineText.itertext())
                            logger.debug(f"ORIG: {original_transcription}")
                            for ab in re.findall(r'abbrev +{[^}]+expansion[^}_]+}', custom_annotation):
                                logger.debug( ab )
                                offset, length, expansion = abbreviation_re.sub(r'\1|\2|\3', ab).split('|')
                                expansion = re.sub(r'.u0020cetera', 'c', expansion )
                                # skipping all other expansions that contain a space
                                if expansion.find('u0020') >= 0:
                                    continue
                                abbrev_masks.append( (int(offset), int(length), expansion) )
                                logger.debug(abbrev_masks)
                            
                            expanded_transcription = expand_text( original_transcription, abbrev_masks )
    
                            orig_transcription_didip = to_didip_charset( orig_transcription )
                            exp_transcription_didip = to_didip_charset( expanded_transcription )
                            parallel_transcription = zip_transcription( orig_transcription_didip, exp_transcription_didip )
                            logger.debug(parallel_transcription)

                            textLineText.clear()
                            textLineText.text = parallel_transcription

                            if args.output_format == 'plain':
                                text_line_transcriptions.append( parallel_transcription )
                            
                        #del textLineElt.attrib['custom']

            if args.output_format == 'none':
                continue
            if args.output_format == 'plain':
                if args.standard_output:
                    print('\n'.join( text_line_transcriptions ))
                else:
                    print('\n'.join( text_line_transcriptions ), file=target_dirpath.joinpath(xmlFilename).with_suffix('.txt'))
            else:
                page_root.insert(1, pageElt)
                if args.standard_output:
                    page_tree.write( sys.stdout, encoding='unicode')
                else:
                    page_tree.write( target_dirpath.joinpath(xmlFilename), encoding='utf-8')
                #ET.dump(page_tree)
                page_root.remove( pageElt )

####
def test_expand_text_1():
    txt = 'mein eygen insigel, ✳ doch hochgenātt₎ mein₎ g₎ herˀ ✳ und dero gotzhusz Sanct Blasien ✳ wie obstat, ✳ mir, einē erbern gericht, ✳ all unsern erben und nachkhom̄en in alweg one schaden,'
    masks = [(33, 4, 'nant'), (37, 2, 'ten'), (43, 2, 'nen'), (46, 2, 'gnädigen'), (49, 4, 'herren'), (111, 3, 'nem'), (158, 7, 'khommen')]
    expected = 'mein eygen insigel, ✳ doch hochgenantten meinen gnädigen herren ✳ und dero gotzhusz Sanct Blasien ✳ wie obstat, ✳ mir, einem erbern gericht, ✳ all unsern erben und nachkhommen in alweg one schaden,'

    assert expand_text( txt, masks ) == expected
    
def test_expand_text_2():
    txt = 'Schicker, ernstlich gebetten unnd erbettē den ersamen, fromē, wisen unnd bescheidnen Hannsen'
    # original: mask error!
    #masks = [(39, 2, 'ten'), (58, 2, 'men')]
    masks = [(39, 2, 'ten'), (58, 3, 'men')]
    expected = 'Schicker, ernstlich gebetten unnd erbetten den ersamen, fromen, wisen unnd bescheidnen Hannsen'
    
    assert expand_text( txt, masks ) == expected

def test_didip_text_1():
    abbr_txt = 'mein eygen insigel, ✳ doch hochgenātt₎ mein₎ g₎ herˀ ✳ und dero gotzhusz Sanct Blasien ✳ wie obstat, ✳ mir, einē erbern gericht, ✳ all unsern erben und nachkhom̄en in alweg one schaden,'
    abbr_expected = 'mein eygen insigel $ doch hochgena%tt% mein% g% her% $ und dero gotzhusz Sanct Blasien $ wie obstat $ mir eine% erbern gericht $ all unsern erben und nachkhom%en in alweg one schaden'
    exp_txt = 'mein eygen insigel, ✳ doch hochgenantten meinen gnädigen herren ✳ und dero gotzhusz Sanct Blasien ✳ wie obstat, ✳ mir, einem erbern gericht, ✳ all unsern erben und nachkhommen in alweg one schaden,'
    exp_expected = 'mein eygen insigel $ doch hochgenantten meinen gnadigen herren $ und dero gotzhusz Sanct Blasien $ wie obstat $ mir einem erbern gericht $ all unsern erben und nachkhommen in alweg one schaden'
    assert to_didip_charset( abbr_txt ) == abbr_expected
    assert to_didip_charset( exp_txt ) == exp_expected

def test_didip_text_2():
    abbr_txt = 'Schicker, ernstlich gebetten unnd erbettē den ersamen, fromē, wisen unnd bescheidnen Hannsen'
    abbr_expected = 'Schicker ernstlich gebetten unnd erbette% den ersamen frome% wisen unnd bescheidnen Hannsen'
    exp_txt = 'Schicker, ernstlich gebetten unnd erbetten den ersamen, fromen, wisen unnd bescheidnen Hannsen'
    exp_expected = 'Schicker ernstlich gebetten unnd erbetten den ersamen fromen wisen unnd bescheidnen Hannsen'

    assert to_didip_charset( abbr_txt ) == abbr_expected
    assert to_didip_charset( exp_txt ) == exp_expected

def test_zip_1():
    abbr = 'mein eygen insigel $ doch hochgena%tt% mein% g% her% $ und dero gotzhusz Sanct Blasien $ wie obstat $ mir eine% erbern gericht $ all unsern erben und nachkhom%en in alweg one schaden'
    exp = 'mein eygen insigel $ doch hochgenantten meinen gnadigen herren $ und dero gotzhusz Sanct Blasien $ wie obstat $ mir einem erbern gericht $ all unsern erben und nachkhommen in alweg one schaden'
    expected = 'mein eygen insigel $ doch [hochgenantten|hochgena%tt% [meinen|mein% [gnadigen|g% [herren|her% $ und dero gotzhusz Sanct Blasien $ wie obstat $ mir [einem|eine% erbern gericht $ all unsern erben und [nachkhommen|nachkhom%en in alweg one schaden'
    assert zip_transcriptions(abbr, exp) == expected


def test_zip_2():
    abbr = 'Schicker ernstlich gebetten unnd erbette% den ersamen frome% wisen unnd bescheidnen Hannsen'
    exp = 'Schicker ernstlich gebetten unnd erbetten den ersamen fromen wisen unnd bescheidnen Hannsen'
    expected = 'Schicker ernstlich gebetten unnd [erbetten|erbette% den ersamen [fromen|frome% wisen unnd bescheidnen Hannsen'
    assert zip_transcriptions(abbr, exp) == expected


def test_all_1():
    txt = 'mein eygen insigel, ✳ doch hochgenātt₎ mein₎ g₎ herˀ ✳ und dero gotzhusz Sanct Blasien ✳ wie obstat, ✳ mir, einē erbern gericht, ✳ all unsern erben und nachkhom̄en in alweg one schaden,'
    masks = [(33, 4, 'nant'), (37, 2, 'ten'), (43, 2, 'nen'), (46, 2, 'gnädigen'), (49, 4, 'herren'), (111, 3, 'nem'), (158, 7, 'khommen')]
    expected = 'mein eygen insigel $ doch [hochgenantten|hochgena%tt% [meinen|mein% [gnadigen|g% [herren|her% $ und dero gotzhusz Sanct Blasien $ wie obstat $ mir [einem|eine% erbern gericht $ all unsern erben und [nachkhommen|nachkhom%en in alweg one schaden'
    expansion = expand_text( txt, masks )
    assert zip_transcriptions( to_didip_charset( txt ), to_didip_charset( expansion )) == expected

def test_all_2():
    txt = 'Schicker, ernstlich gebetten unnd erbettē den ersamen, fromē, wisen unnd bescheidnen Hannsen'
    # Second mask is wrong, as in the original text
    masks = masks = [(39, 2, 'ten'), (58, 2, 'men')]
    expected = 'Schicker ernstlich gebetten unnd [erbetten|erbette% den ersamen [fromen|frome% wisen unnd bescheidnen Hannsen'

    expansion = expand_text( txt, masks )
    assert zip_transcriptions( to_didip_charset( txt ), to_didip_charset( expansion )) == expected

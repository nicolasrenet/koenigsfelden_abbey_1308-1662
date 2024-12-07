#!/usr/bin/env python3

import sys
import re
"""
Filter Unicode abbreviations into 'basic' style, Nuremberg letterbooks-style.

+ abbreviations that cannot be associated with a unique letter ('ꝫ', 'ꝰ', ...) are transcribed as '*' (star)
+ abbreviations that decorate a letter are transcribed into letter+'*' (star), no matter how many symbols are involved. Eg.

'ꝓ' (1 symbol) → 'p*'
'ē' ('e'+ diacritic) → 'e*'
'ꝝ' -> r*
etc.


"""

# make room for 1 mark or more
diacritic_abbreviation_pattern = re.compile(r'([A-Za-z])[\u0300-\u0316]+')

replace_dict = {
        'Ꝑ': 'P*',
        'ꝑ': 'p*',
        'Ꝓ': 'P*',
        'ꝓ': 'p*',
        'Ꝙ': 'Q*',
        'ꝙ': 'q*',
        'Ꝗ': 'Q*',
        'ꝗ': 'q*',
        'Ꝝ': 'R*',
        'ꝝ': 'r*',
        'ẜ': 's*',
        'ꝷ': 't*',
        'ꝟ': 'v*',
        'ƺ': 'z',
        'Ꝯ': '*',
        'ꝯ': '*',
        'ꝫ': '*',
        'ȝ': '*',
        'ꝝ': 'r*',
        'Ꝝ': 'R*',
        '₰': '*',
        'Ꝛ': 'R*',
        'ꝛ': 'r*',
        'ꝰ': '*',
        'ꝭ': '*',
        '&': '*',
        '₎': '*',
        'כּ': '*',
        'ˀ': '*r',
}

for line in sys.stdin:

    for k,v in replace_dict.items():
        line = line.replace(k, v)
    line = diacritic_abbreviation_pattern.sub( r'\1*', line )
    print(line)



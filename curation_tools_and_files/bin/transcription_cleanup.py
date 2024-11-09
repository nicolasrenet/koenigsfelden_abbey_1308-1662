#!/usr/bin/env python3

import sys
import re

# Choices:
# - remove obvious junk
# - remove ambiguous subscript marks (subscript bar, tilde)
# - replace marks that map to a single character (subscript letters) or to unambiguous bi- or trigrams (eg. 'ꝝ'='rum') by what they stand for
# - 
for line in sys.stdin:
    line = line.replace(u'✳','')
    line = line.replace('&#13','')
    line = line.replace('\u200b','')
    line = line.replace('\uf2f7','')
    line = re.sub(r'  +',' ', line)

    print(line, end='')

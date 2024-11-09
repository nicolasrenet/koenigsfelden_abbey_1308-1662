#!/usr/bin/env python3

from pathlib import Path
import sys

from PIL import Image

from seglib import seglib, seg_io

USAGE=f"{sys.argv[0]} <page xml> [ <img_source> ]"

if len(sys.argv) < 2:
    print(USAGE)
    sys.exit()

xml = Path(sys.argv[1])

img_src = sys.argv[2] if len(sys.argv)>2 else '.'
img_src = Path( img_src )

img_file = img_src.joinpath( xml.name ).with_suffix('.jpg')
if img_file.with_suffix('.map.png').exists():
    sys.exit()
pmap = seglib.polygon_map_from_img_xml_files( img_file, xml )
display = seg_io.display_polygon_set_from_img_and_polygon_map( img_file, pmap )
img = Image.fromarray( display, 'RGB')
img.save(Path(img_file.name).with_suffix('.map.png'))

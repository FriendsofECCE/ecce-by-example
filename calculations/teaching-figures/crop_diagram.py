#!/usr/bin/env python3
"""Crop an MO Diagram plotshot above its "Click a level" hint and the Options
band: python3 crop_diagram.py <in.png> <out.png>"""
import sys
from PIL import Image

im = Image.open(sys.argv[1]).convert("RGB")
w, h = im.size
band = next(y for y in range(100, h) if im.getpixel((w * 3 // 5, y)) == (0xDD, 0xDC, 0xDA))
im.crop((0, 0, w, band - 28)).save(sys.argv[2])

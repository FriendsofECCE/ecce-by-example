#!/usr/bin/env python3
"""Put the pictures of one figure on one scale.

    python3 scale_group.py <out dir> <suffix> NAME=<png>:<example dir> ...

Each png is a saveimage taken after viewall and the same fixed zoom, so its
pixels per angstrom go as 1/R, R the radius of the padded atom box of the
example's stored structure (as in spec_f.py). Each picture is shrunk by
R/R_max about its centre, then all are cut to the one box that holds every
picture's content, so all come out at the same size and scale:
<out dir>/NAME<suffix>.
"""
import glob, math, os, sys
from PIL import Image, ImageChops

PAD = 0.4


def radius(example):
    mvm = glob.glob(os.path.join(example, "stored", "*", "Parameters", "chemsys.mvm"))[0]
    lines = open(mvm).read().splitlines()
    n = int(next(l for l in lines if l.startswith("num_atoms:")).split()[1])
    k = next(i for i, l in enumerate(lines) if l.startswith("atom_list:"))
    xyz = [[float(x) for x in l.split()[1:4]] for l in lines[k + 1:k + 1 + n]]
    span = [max(p[i] for p in xyz) - min(p[i] for p in xyz) + 2 * PAD for i in range(3)]
    return 0.5 * math.sqrt(sum(s * s for s in span))


out, suffix = sys.argv[1], sys.argv[2]
items = []
for arg in sys.argv[3:]:
    name, rest = arg.split("=", 1)
    png, example = rest.split(":", 1)
    items.append((name, Image.open(png).convert("RGB"), radius(example)))
rmax = max(r for _, _, r in items)
placed = []
box = None
for name, im, r in items:
    w, h = im.size
    s = r / rmax
    small = im.resize((max(1, round(w * s)), max(1, round(h * s))), Image.LANCZOS)
    canvas = Image.new("RGB", (w, h), "white")
    canvas.paste(small, ((w - small.width) // 2, (h - small.height) // 2))
    bb = ImageChops.difference(canvas, Image.new("RGB", (w, h), "white")).getbbox()
    if bb:
        box = bb if box is None else (min(box[0], bb[0]), min(box[1], bb[1]), max(box[2], bb[2]), max(box[3], bb[3]))
    placed.append((name, canvas, r))
m = 20
box = (max(0, box[0] - m), max(0, box[1] - m), box[2] + m, box[3] + m)
for name, canvas, r in placed:
    canvas.crop(box).save(os.path.join(out, name + suffix))
    print(name, "R=%.2f scale=%.2f" % (r, r / rmax))

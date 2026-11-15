#!/usr/bin/env python3
"""Cover art from ECCE Density Map exports (dmcsv): log10 of the total density,
filled in a palette built on the book's accent colour, with log-spaced contours.

    python3 render_maps.py <in.csv> <out.png> <width px> <height px> [--zoom Z]

The map is centred and padded with the background so any aspect ratio fills.
"""
import sys, numpy as np, argparse
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from scipy.ndimage import zoom

OCRE = np.array([243, 102, 25]) / 255
CMAP = LinearSegmentedColormap.from_list("book", [
    (0.00, (1, 1, 1)), (0.25, (1.0, 0.93, 0.86)), (0.55, (0.98, 0.70, 0.45)),
    (0.78, tuple(OCRE)), (1.00, (0.42, 0.13, 0.03))])
LO, HI = -3.0, 0.5           # log10 e/bohr^3: 0.001 (outer edge) .. cores clipped

ap = argparse.ArgumentParser()
ap.add_argument("csv"); ap.add_argument("png"); ap.add_argument("w", type=int); ap.add_argument("h", type=int)
ap.add_argument("--zoom", type=float, default=1.0, help=">1 crops in around the centre")
ap.add_argument("--lines", type=float, default=1.0, help="contour line width in px at 1000 px")
a = ap.parse_args()

d = np.loadtxt(a.csv, delimiter=",", comments="#", skiprows=4)
u, v = np.unique(d[:, 0]), np.unique(d[:, 1])
z = d[:, 5].reshape(len(v), len(u))
step = u[1] - u[0]
L = np.log10(np.clip(z, 1e-8, None))
# The map window can cut the outer density: start the contours above the
# highest value on the window's edge, so no contour runs into the edge, then
# crop to what is left and pad just below that level (a smooth step, so the
# upsampled outer contour stays smooth). Outside it the page stays white.
edge = max(L[0].max(), L[-1].max(), L[:, 0].max(), L[:, -1].max())
lo = max(LO, np.ceil((edge + 0.01) / 0.25) * 0.25)
ys, xs = np.nonzero(L >= lo)
m = int(0.08 * max(np.ptp(ys), np.ptp(xs)))
L = np.pad(L[ys.min():ys.max() + 1, xs.min():xs.max() + 1], m, constant_values=lo - 0.5)
# pad to the target aspect with the floor value
aspect = a.w / a.h
ny, nx = L.shape
if nx / ny < aspect:
    pad = int(round(ny * aspect - nx)); L = np.pad(L, ((0, 0), (pad // 2, pad - pad // 2)), constant_values=lo - 0.5)
else:
    pad = int(round(nx / aspect - ny)); L = np.pad(L, ((pad // 2, pad - pad // 2), (0, 0)), constant_values=lo - 0.5)
if a.zoom > 1:
    ny, nx = L.shape; cy, cx = ny // 2, nx // 2
    hy, hx = int(ny / a.zoom / 2), int(nx / a.zoom / 2)
    L = L[cy - hy:cy + hy, cx - hx:cx + hx]
f = a.w / L.shape[1]
Lz = zoom(L, f, order=3)
fig = plt.figure(figsize=(a.w / 100, a.h / 100), dpi=100)
ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
ax.imshow(np.ma.masked_less(np.clip(Lz, None, HI), lo), cmap=CMAP, vmin=LO, vmax=HI, origin="lower", interpolation="bilinear",
          extent=(0, Lz.shape[1], 0, Lz.shape[0]))
levels = np.arange(lo, HI, 0.25)
ax.contour(Lz, levels=levels, colors=[tuple(OCRE * 0.55)], linewidths=a.lines * a.w / 1000, alpha=0.55, linestyles="solid",
           extent=(0, Lz.shape[1], 0, Lz.shape[0]))
ax.set_xlim(0, Lz.shape[1]); ax.set_ylim(0, Lz.shape[0])
fig.savefig(a.png, dpi=100)

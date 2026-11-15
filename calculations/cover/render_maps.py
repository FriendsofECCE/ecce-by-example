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
ap.add_argument("--signed", action="store_true", help="orbital amplitude: blue/orange about a white node")
ap.add_argument("--nofill", action="store_true", help="contour lines only, in ECCE's own colours")
a = ap.parse_args()

d = np.loadtxt(a.csv, delimiter=",", comments="#", skiprows=4)
u, v = np.unique(d[:, 0]), np.unique(d[:, 1])
z = d[:, 5].reshape(len(v), len(u))
step = u[1] - u[0]
if a.signed:
    # The same levels ECCE's map draws (+-0.01 .. 0.32, doubling); colour by
    # sign with a symmetric log scale so the outer lobes still show.
    BLUE = np.array([31, 102, 160]) / 255
    cmap = LinearSegmentedColormap.from_list("sign", [
        (0.0, tuple(BLUE * 0.6)), (0.25, tuple(BLUE)), (0.5, (1, 1, 1)),
        (0.75, tuple(OCRE)), (1.0, tuple(OCRE * 0.55))])
    aspect = a.w / a.h
    ny, nx = z.shape
    if nx / ny < aspect:
        pad = int(round(ny * aspect - nx)); z = np.pad(z, ((0, 0), (pad // 2, pad - pad // 2)), constant_values=np.nan)
    else:
        pad = int(round(nx / aspect - ny)); z = np.pad(z, ((pad // 2, pad - pad // 2), (0, 0)), constant_values=np.nan)
    if a.zoom > 1:
        ny, nx = z.shape; cy, cx = ny // 2, nx // 2
        hy, hx = int(ny / a.zoom / 2), int(nx / a.zoom / 2)
        z = z[cy - hy:cy + hy, cx - hx:cx + hx]
    # Padding is NaN (no data), not zero, so no node line runs along it.
    zz = zoom(np.nan_to_num(z), a.w / z.shape[1], order=3)
    zz[zoom(np.isnan(z).astype(float), a.w / z.shape[1], order=0) > 0.5] = np.nan
    t = np.sign(zz) * np.clip(np.log10(np.abs(zz) / 0.005 + 1e-12), 0, None) / np.log10(0.64 / 0.005)
    fig = plt.figure(figsize=(a.w / 100, a.h / 100), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    ext = (0, zz.shape[1], 0, zz.shape[0])
    cmap.set_bad((1, 1, 1))
    lv = [0.01 * 2 ** k for k in range(6)]
    if a.nofill:
        # ECCE's map colours: one sign blue, the other orange, paler outward.
        pos = [tuple(1 - (1 - BLUE) * (0.35 + 0.65 * k / 5)) for k in range(6)]
        neg = [tuple(1 - (1 - OCRE) * (0.35 + 0.65 * k / 5)) for k in range(6)]
        ax.contour(zz, levels=lv, colors=pos, linewidths=1.8 * a.lines * a.w / 1000,
                   linestyles="solid", extent=ext)
        ax.contour(zz, levels=[-x for x in lv[::-1]], colors=neg[::-1],
                   linewidths=1.8 * a.lines * a.w / 1000, linestyles="solid", extent=ext)
    else:
        # The map's centre is not exactly white; below the outermost level it must be.
        ax.imshow(np.ma.masked_inside(np.clip(t, -1, 1), -0.01, 0.01), cmap=cmap, vmin=-1, vmax=1,
                  origin="lower", extent=ext)
        ax.contour(zz, levels=[-x for x in lv[::-1]] + lv, colors=[(0.2, 0.2, 0.2)],
                   linewidths=a.lines * a.w / 1000, alpha=0.45, linestyles="solid", extent=ext)
    ax.contour(zz, levels=[0], colors=[(0.45, 0.45, 0.45)], linewidths=1.6 * a.lines * a.w / 1000,
               linestyles="solid", extent=ext)
    ax.set_xlim(0, zz.shape[1]); ax.set_ylim(0, zz.shape[0])
    fig.savefig(a.png, dpi=100)
    sys.exit(0)
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
if not a.nofill:
  ax.imshow(np.ma.masked_less(np.clip(Lz, None, HI), lo), cmap=CMAP, vmin=LO, vmax=HI, origin="lower", interpolation="bilinear",
          extent=(0, Lz.shape[1], 0, Lz.shape[0]))
levels = np.arange(lo, HI, 0.25)
if a.nofill:
    # ECCE draws the total density's levels in viridis, dark outside.
    import matplotlib.cm as cm
    levels = [l for l in np.log10(0.001 * 2.0 ** np.arange(14)) if l >= lo]   # ECCE's doubling levels
    ax.contour(Lz, levels=levels, colors=[cm.viridis(0.05 + 0.85 * k / max(1, len(levels) - 1)) for k in range(len(levels))],
               linewidths=1.8 * a.lines * a.w / 1000, linestyles="solid", extent=(0, Lz.shape[1], 0, Lz.shape[0]))
else:
  ax.contour(Lz, levels=levels, colors=[tuple(OCRE * 0.55)], linewidths=a.lines * a.w / 1000, alpha=0.55, linestyles="solid",
           extent=(0, Lz.shape[1], 0, Lz.shape[0]))
ax.set_xlim(0, Lz.shape[1]); ax.set_ylim(0, Lz.shape[0])
fig.savefig(a.png, dpi=100)

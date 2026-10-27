"""Rebuild one iPhone screen recording of the site as a single tall page image.

Each page row is taken from the last frame in which it sat inside the clean window
(below the fixed header, above the floating chat buttons), so scroll-reveal
animations have finished by then.
Usage: python3 -I scripts/stitch-page.py recording.mov outdir
"""
import subprocess, sys
import numpy as np
from PIL import Image

src, outdir = sys.argv[1], sys.argv[2]
W, H = 1180, 2556
TOP, WB = 620, 2050           # clean content window (rows)
BAND = (700, 1300)            # rows used for matching
MAXD = 640

p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
fsize = W * H * 3

def frames():
    while True:
        b = p.stdout.read(fsize)
        if len(b) < fsize:
            return
        yield np.frombuffer(b, np.uint8).reshape(H, W, 3)

def gray(f):
    return f[:, 40:1000:4].astype(np.float32).mean(axis=2)

canvas = np.zeros((60000, W, 3), np.uint8)
it = frames()
f0 = next(it)
canvas[TOP:WB] = f0[TOP:WB]
off = 0
prev = gray(f0)
dprev = 0
for f in it:
    g = gray(f)
    if np.abs(g - prev).mean() < 0.3:
        continue  # duplicated frame
    band = g[BAND[0]:BAND[1]]
    ds = np.arange(-160, MAXD)
    costs = np.array([np.abs(band - prev[BAND[0] + d:BAND[1] + d]).mean() for d in ds])
    lo = costs.min()
    cands = np.nonzero(costs <= lo + max(0.8, lo * 0.15))[0]
    bd = int(ds[cands[np.argmin(np.abs(ds[cands] - dprev))]])
    off += bd
    canvas[off + TOP:off + WB] = f[TOP:WB]
    dprev = bd
    prev = g
page = canvas[TOP:off + WB]
page[:, 1150:] = page[:, 1149:1150]  # hide the iOS scroll indicator
Image.fromarray(page).save(f"{outdir}/page.png")
print("page height", page.shape[0], "final off", off)

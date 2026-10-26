import subprocess, sys
import numpy as np
from PIL import Image

src, outdir = sys.argv[1], sys.argv[2]
W, H = 600, 1300
TOP, BOT = 253, 1195          # scrolling content window (below header, above CTA bar)
STRIP = 700                   # rows written per frame start here
BAND = (300, 900)             # rows used for matching
MAXD = 295

p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src, "-vf", f"scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
fsize = W * H * 3

def frames():
    while True:
        b = p.stdout.read(fsize)
        if len(b) < fsize:
            return
        yield np.frombuffer(b, np.uint8).reshape(H, W, 3)

def gray(f):
    return f[:, :576:2].astype(np.float32).mean(axis=2)

canvas = np.zeros((40000, W, 3), np.uint8)
it = frames()
f0 = next(it)
first = f0.copy()
canvas[TOP:STRIP] = f0[TOP:STRIP]
off = 0
prev = gray(f0)
dprev = 0
offs = [0]
last = f0
for f in it:
    g = gray(f)
    if np.abs(g - prev).mean() < 0.4:
        continue  # duplicated frame in the recording
    band = g[BAND[0]:BAND[1]]
    ds = np.arange(-80, MAXD)
    costs = np.array([np.abs(band - prev[BAND[0] + d:BAND[1] + d]).mean() for d in ds])
    lo = costs.min()
    cands = np.nonzero(costs <= lo + max(0.8, lo * 0.15))[0]
    bd = int(ds[cands[np.argmin(np.abs(ds[cands] - dprev))]])
    off += bd
    if bd > 0:
        canvas[off + STRIP - bd:off + STRIP] = f[STRIP - bd:STRIP]
    offs.append(off)
    dprev = bd
    prev = g
    last = f
canvas[off + STRIP:off + BOT] = last[STRIP:BOT]
page = canvas[TOP:off + BOT]
# hide the iOS scroll indicator at the right edge
page[:, 586:] = page[:, 585:586]
Image.fromarray(page).save(f"{outdir}/page.png")
Image.fromarray(first[:TOP]).save(f"{outdir}/top.png")
Image.fromarray(first[BOT:]).save(f"{outdir}/bar.png")
np.save(f"{outdir}/offs.npy", np.array(offs))
print("page height", page.shape[0], "frames", len(offs), "final off", off)

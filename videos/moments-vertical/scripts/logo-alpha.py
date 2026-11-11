"""Lift the Moments logo (white on the dark-green footer of the screen recording)
into transparent PNGs, upscaled 4x: one cream, one dark green.
Usage: python3 -I scripts/logo-alpha.py footer-frame.png assets/img
The logo sits at x 113-253, y 752-802 of the 1090x1206 recording frame."""
import sys
import numpy as np
from PIL import Image
src = Image.open(sys.argv[1]).convert("RGB").crop((113, 752, 253, 802))
big = src.resize((src.width * 4, src.height * 4), Image.LANCZOS)
im = np.asarray(big).astype(float) / 255
bg = np.median(np.concatenate([im[:4].reshape(-1, 3), im[-4:].reshape(-1, 3)]), axis=0)
lum = im.mean(axis=2)
a = np.clip((lum - bg.mean() - 0.10) / 0.55, 0, 1)
a = np.clip((a - 0.5) * 1.6 + 0.5, 0, 1)  # firm up the soft upscaled edges
for name, col in (("logo-cream.png", (247, 242, 232)), ("logo-green.png", (31, 42, 34))):
    out = np.zeros((*a.shape, 4), np.uint8)
    out[..., :3] = col
    out[..., 3] = (a * 255).astype(np.uint8)
    Image.fromarray(out, "RGBA").save(f"{sys.argv[2]}/{name}")
print("bg", bg * 255, big.size)
# Afterwards the files were cropped: logo-*.png to (0, 0, 560, 150) to drop the tiny
# "FLORISTERIA VALLS" line (typeset in the video instead), icon-*.png to (0, 0, 150, 170).

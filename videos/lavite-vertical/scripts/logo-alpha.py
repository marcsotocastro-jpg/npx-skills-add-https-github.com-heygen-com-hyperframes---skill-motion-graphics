"""Lift the LA VITE logo off the cream page it was captured on (screen recording)
into a transparent PNG: alpha from the distance to the page colour, colour un-mixed.
Usage: python3 -I scripts/logo-alpha.py assets/img/logo.jpg assets/img/logo.png"""
import sys
import numpy as np
from PIL import Image
im = np.asarray(Image.open(sys.argv[1]).convert("RGB")).astype(float) / 255
h, w, _ = im.shape
edge = np.concatenate([im[:6].reshape(-1, 3), im[-6:].reshape(-1, 3), im[:, :6].reshape(-1, 3), im[:, -6:].reshape(-1, 3)])
bg = np.median(edge, axis=0)
d = np.abs(im - bg).max(axis=2)
a = np.clip((d - 0.03) / 0.30, 0, 1)
a3 = np.maximum(a, 1e-3)[..., None]
col = np.clip((im - (1 - a3) * bg) / a3, 0, 1)
out = np.dstack([col, a]) * 255
Image.fromarray(out.astype(np.uint8), "RGBA").save(sys.argv[2])
print("bg", bg * 255)

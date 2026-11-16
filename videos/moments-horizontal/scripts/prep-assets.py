"""Builds the video assets from the 7 website screenshots in assets/src.

- site-header.jpg : fixed header (logo, nav, CTA) taken from the hero capture
- site-page.jpg   : the page below the header, stitched in site order, with the
                    fixed flower button painted out (it is re-added as site-fab.png)
- img/*.jpg       : photo crops used full-bleed and as pop-out cards
- logo-*.png      : the "mo" mark as an alpha mask (dark green / cream)
Usage: python3 -I scripts/prep-assets.py <project dir>
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

P = Path(sys.argv[1])
S = P / "assets/src"
O = P / "assets"

# (file, header line row) — content starts 2px below the line, ends above the loader glyph
SEGMENTS = [
    ("1-hero.jpg", 196, 1300),
    ("2-intro.jpg", 202, 1405),
    ("3-cafe.jpg", 200, 1405),
    ("4-flors.jpg", 197, 1405),
    ("5-espai.jpg", 198, 1405),
    ("6-contacte.jpg", 195, 1405),
    ("7-quote.jpg", 197, 1405),
]


def paint_out_fab(a):
    """Replace the fixed flower button (centre ~1958,1354) with neighbouring colour."""
    a = a.copy()
    for y in range(1300, 1406):
        a[y, 1908:1924] = a[y, 1906]
        a[y, 1924:2048] = a[y, 2040] if y < 1400 else a[y, 1924]
    # loader glyph in the corner
    for y in range(1395, a.shape[0]):
        a[y, 2000:2048] = a[y, 1995]
    return a


hero = Image.open(S / "1-hero.jpg").convert("RGB")
hero.crop((0, 0, 2048, 198)).save(O / "site/site-header.jpg", quality=92)

parts = []
for f, line, end in SEGMENTS:
    a = np.asarray(Image.open(S / f).convert("RGB"))
    if f != "1-hero.jpg":
        a = paint_out_fab(a)
    parts.append(a[line + 2:end])
page = np.concatenate(parts, axis=0)
Image.fromarray(page).save(O / "site/site-page.jpg", quality=90)
print("page height", page.shape[0], "segment tops", np.cumsum([0] + [p.shape[0] for p in parts]).tolist())

# Flower button, circular crop from the L'espai capture (plain cream around it)
esp = Image.open(S / "5-espai.jpg").convert("RGB")
fab = esp.crop((1958 - 44, 1354 - 44, 1958 + 44, 1354 + 44)).resize((176, 176), Image.LANCZOS)
m = Image.new("L", (704, 704), 0)
ImageDraw.Draw(m).ellipse((4, 4, 700, 700), fill=255)
fab.putalpha(m.resize((176, 176), Image.LANCZOS))
fab.save(O / "site/site-fab.png")

CROPS = {
    "storefront": ("1-hero.jpg", (1098, 202, 1918, 1176)),
    "bouquet": ("2-intro.jpg", (1060, 450, 1918, 1092)),
    "croissant": ("2-intro.jpg", (130, 354, 990, 996)),
    "tulips": ("3-cafe.jpg", (130, 866, 958, 1327)),
    "warm-room": ("3-cafe.jpg", (560, 300, 958, 832)),
    "window-table": ("3-cafe.jpg", (130, 252, 528, 784)),
    "coffee-flower": ("4-flors.jpg", (1130, 338, 1508, 844)),
    "shopfront-flowers": ("4-flors.jpg", (1540, 397, 1918, 905)),
    "blue-table": ("4-flors.jpg", (1130, 938, 1900, 1378)),
    "plants-room": ("5-espai.jpg", (130, 381, 1007, 1081)),
}
for name, (f, box) in CROPS.items():
    Image.open(S / f).convert("RGB").crop(box).save(O / f"img/{name}.jpg", quality=92)

# Logo mask: dark ink -> alpha, upscaled and edge-sharpened
logo = hero.crop((136, 38, 270, 132)).convert("L")
logo = logo.resize((logo.width * 6, logo.height * 6), Image.LANCZOS).filter(ImageFilter.GaussianBlur(2))
L = np.asarray(logo).astype(float)
alpha = np.clip((175 - L) / 70, 0, 1)
alpha = (alpha * 255).astype(np.uint8)
for name, rgb in (("logo-green", (44, 56, 40)), ("logo-cream", (248, 243, 234))):
    im = Image.new("RGBA", logo.size, rgb + (0,))
    im.putalpha(Image.fromarray(alpha))
    bbox = im.getbbox()
    im.crop(bbox).save(O / f"site/{name}.png")
print("done")

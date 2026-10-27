"""Cut the site's cards and section headers out of the stitched pages (scripts/stitch-page.py).
Usage: python3 -I scripts/crop-panels.py <dir with st1..st5/page.png> assets/site <header-frame.png>
The header frame is any full-size frame of the first recording (ffmpeg -ss 3 ... -frames:v 1);
the Q logo is taken from its fixed header.
Coordinates are page pixels at the recording's 1180px width.
"""
import sys
from PIL import Image

src, out = sys.argv[1], sys.argv[2]
C = (50, 1130)   # card column
F = (0, 1180)    # full width
PANELS = {
    # page 1: home
    "hero":      (1, F, 40, 960),
    "hero-cta":  (1, F, 1525, 1900),
    "stats":     (1, C, 2025, 2325),
    "problem":   (1, C, 3385, 4995),
    "solution":  (1, C, 5110, 6500),
    # page 2: services + AI assistants
    "svc-head":  (2, F, 60, 1025),
    "svc-1":     (2, C, 1200, 2310),
    "svc-2":     (2, C, 2380, 3525),
    "svc-3":     (2, C, 3590, 4600),
    "svc-4":     (2, C, 4675, 5775),
    "ai-head":   (2, F, 6475, 7350),
    "ai-1":      (2, C, 7485, 8185),
    "demo-chips": (2, F, 13100, 13500),
    "chat":      (2, C, 14625, 15900),
    # page 3: web plans, method, social packs
    "web-head":  (3, F, 0, 925),
    "web-1":     (3, C, 1100, 2150),
    "web-2":     (3, C, 2225, 3300),
    "web-3":     (3, C, 3365, 4390),
    "method-head": (3, F, 5275, 6225),
    "step-1":    (3, C, 6400, 6925),
    "step-2":    (3, C, 6975, 7500),
    "step-3":    (3, C, 7550, 8075),
    "step-4":    (3, C, 8125, 8650),
    "step-5":    (3, C, 8700, 9125),
    "packs-head": (3, F, 10075, 10700),
    "pack-1":    (3, C, 10885, 11825),
    "pack-2":    (3, C, 11890, 12800),
    "pack-3":    (3, C, 12855, 13800),
    "pack-4":    (3, C, 13855, 14950),
    # page 4: cases + testimonials
    "cases-head": (4, F, 0, 950),
    "case-1":    (4, C, 1100, 2300),
    "case-2":    (4, C, 2350, 3475),
    "case-3":    (4, C, 3535, 4740),
    "quote-1":   (4, C, 6025, 7010),
    "quote-3":   (4, C, 7790, 9100),
    # page 5: CTA, FAQ, contact, footer
    "cta":       (5, C, 0, 1725),
    "contact":   (5, F, 5000, 6250),
    "form":      (5, C, 6360, 8275),
    "advice":    (5, F, 8950, 9675),
}
pages = {}
for name, (pg, (x0, x1), y0, y1) in PANELS.items():
    if pg not in pages:
        pages[pg] = Image.open(f"{src}/st{pg}/page.png").convert("RGB")
    im = pages[pg].crop((x0, y0, x1, y1))
    im.save(f"{out}/{name}.jpg", quality=90)
    print(name, im.size)
# Logo: key out the header's dark background into alpha
import numpy as np
lg = np.asarray(Image.open(sys.argv[3]).convert("RGB").crop((95, 365, 225, 502)), dtype=np.float32)
bg = np.median(np.concatenate([lg[0], lg[-1], lg[:, 0], lg[:, -1]]), axis=0)
alpha = np.clip((lg - bg).max(axis=2) / 70.0, 0, 1)
rgba = np.dstack([np.clip(lg, 0, 255), alpha * 255]).astype(np.uint8)
Image.fromarray(rgba, "RGBA").save(f"{out}/logo.png")

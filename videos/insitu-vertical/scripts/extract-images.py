"""Pull the embedded photos (data URIs) out of the Insitu site HTML into assets/img.
Usage: python3 -I scripts/extract-images.py <insitu-3d.html> assets/img
Also writes assets/img/menu.json (name, category, price, image class) from the site's DATA array."""
import sys, re, base64, json, os
src, out = sys.argv[1], sys.argv[2]
s = open(src, encoding="utf-8").read()
for cls, mime, b64 in re.findall(r'\.((?:ph-p\d+)|(?:im-[a-z]+))\{background-image:url\(["\']?data:image/([a-z+]+);base64,([A-Za-z0-9+/=]+)', s):
    ext = {"jpeg": "jpg", "svg+xml": "svg"}.get(mime, mime)
    open(os.path.join(out, f"{cls}.{ext}"), "wb").write(base64.b64decode(b64))
m = re.search(r'const DATA=(\[.*?\]);', s, re.S)
if m:
    json.dump(json.loads(m.group(1)), open(os.path.join(out, "menu.json"), "w"), ensure_ascii=False, indent=1)

# The menu photos ship at 256 px: upscale 2x (Lanczos + light unsharp) so they hold up at video size.
from PIL import Image, ImageFilter
for f in os.listdir(out):
    if f.startswith("ph-p") and f.endswith(".jpg"):
        im = Image.open(os.path.join(out, f)).convert("RGB")
        if im.width < 512:
            im = im.resize((512, 512), Image.LANCZOS).filter(ImageFilter.UnsharpMask(radius=1.6, percent=60, threshold=2))
            im.save(os.path.join(out, f), quality=92)

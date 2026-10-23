"""Resize, crop and lightly grade photos for the site.
Usage: python3 process_photos.py <uploads-root> <site-root>
Writes <site>/img/p/<slug>-<w>.webp and a sizes json used by build.py."""
import json, os, sys
from PIL import Image, ImageOps, ImageEnhance
sys.path.insert(0, os.path.dirname(__file__))
from photos import P

Image.MAX_IMAGE_PIXELS = None
src_root, site = sys.argv[1], sys.argv[2]
out = os.path.join(site, "img", "p"); os.makedirs(out, exist_ok=True)

# Gentle, consistent grade: a touch of matte (lifted blacks, softened whites),
# slightly cooler greens/blues kept, saturation eased so the set reads as one.
LUT = [int(10 + v * (246 - 10) / 255) for v in range(256)]
def grade(im):
    im = ImageEnhance.Contrast(im).enhance(1.06)
    im = ImageEnhance.Color(im).enhance(0.9)
    r, g, b = im.split()
    r = r.point(lambda v: min(255, int(LUT[v] * 1.012)))
    g = g.point(LUT)
    b = b.point(lambda v: int(LUT[v] * 0.985))
    return Image.merge("RGB", (r, g, b))

def crop_to(im, aspect, fx=.5, fy=.5):
    w, h = im.size
    if w / h > aspect:
        nw = int(h * aspect); x = int((w - nw) * fx); return im.crop((x, 0, x + nw, h))
    nh = int(w / aspect); y = int((h - nh) * fy); return im.crop((0, y, w, y + nh))

meta = {}
for p in P:
    path = os.path.join(src_root, p["src"])
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    if p.get("crop"):
        im = crop_to(im, p["crop"], p.get("fx", .5), p.get("fy", .5))
    pano = im.width / im.height > 1.8
    widths = (1200, 2400) if pano else (800, 1600)
    im = grade(im)
    made = []
    for w in widths:
        if im.width < w and made:  # don't upscale beyond first size
            continue
        tw = min(w, im.width)
        th = round(im.height * tw / im.width)
        im.resize((tw, th), Image.LANCZOS).save(os.path.join(out, f"{p['slug']}-{w}.webp"), "WEBP", quality=78, method=6)
        made.append((w, tw, th))
    meta[p["slug"]] = dict(w=made[-1][1], h=made[-1][2], sizes=[m[0] for m in made])
    print(p["slug"], im.size, [m[0] for m in made])

json.dump(meta, open(os.path.join(os.path.dirname(__file__), "photo_sizes.json"), "w"), indent=1)

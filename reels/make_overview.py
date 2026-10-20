#!/usr/bin/env python3
"""پیش‌نمایش یک‌جای کاروسل: python3 reels/make_overview.py [slug ...]
خروجی: reels/carousel/<slug>/<slug>_overview.jpg — شبکهٔ ۴ستونه با شمارهٔ اسلاید (ترتیب از چپ به راست)
"""
import glob
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "carousel")


def overview(slug, cols=4, tw=405, gap=24, bg=(236, 232, 226)):
    files = sorted(glob.glob(os.path.join(ROOT, slug, f"{slug}_[0-9][0-9].png")))
    if not files:
        print(f"[×] {slug}: اسلایدی پیدا نشد")
        return None
    th = int(tw * 1350 / 1080)
    rows = (len(files) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw + (cols + 1) * gap, rows * th + (rows + 1) * gap), bg)
    d = ImageDraw.Draw(sheet)
    for i, f in enumerate(files):
        im = Image.open(f).convert("RGB").resize((tw, th), Image.LANCZOS)
        x = gap + (i % cols) * (tw + gap)
        y = gap + (i // cols) * (th + gap)
        sheet.paste(im, (x, y))
        d.rounded_rectangle([x + 10, y + th - 52, x + 52, y + th - 10], 10, fill=(30, 30, 30))
        d.text((x + 31, y + th - 31), str(i + 1), fill="white", anchor="mm")
    out = os.path.join(ROOT, slug, f"{slug}_overview.jpg")
    sheet.save(out, quality=88, optimize=True)
    print(f"[✓] {out}  ({len(files)} اسلاید)")
    return out


if __name__ == "__main__":
    slugs = sys.argv[1:] or sorted(os.path.basename(p) for p in glob.glob(os.path.join(ROOT, "*")) if os.path.isdir(p))
    for s in slugs:
        overview(s)

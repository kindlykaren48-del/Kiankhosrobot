"""
خروجی کاروسل ثابت (مشابه اسلایدهای ریل) — PNG عمودی ۱۰۸۰×۱۹۲۰.

از همان چیدمان استاندارد make_reel.py (کاور + اسلایدهای محتوا + CTA) استفاده می‌کند،
اما به‌جای ویدیو، اسلایدها را به‌ترتیب آپلود کاروسل اینستاگرام نام‌گذاری می‌کند:
    <slug>_carousel_01.png  →  <slug>_carousel_N.png
"""
import os
import shutil

from make_reel import PALETTES, make_cover, make_cta, make_slide


def build_carousel(cfg, outdir):
    """اسلایدهای کاروسل را می‌سازد و به‌ترتیب در outdir کپی می‌کند."""
    os.makedirs(outdir, exist_ok=True)
    slug = cfg["slug"]
    pal = cfg.get("palette") if isinstance(cfg.get("palette"), list) \
        else PALETTES.get(cfg.get("palette", "aurora"), PALETTES["aurora"])

    make_cover(cfg)                      # f_cover.png
    slide_count = len(cfg["slides"])
    for i in range(slide_count):         # f_s1.png … f_sN.png
        make_slide(i, cfg, pal)
    make_cta(cfg)                        # f_cta.png

    order = (["f_cover.png"]
             + [f"f_s{i}.png" for i in range(1, slide_count + 1)]
             + ["f_cta.png"])
    outs = []
    for i, src in enumerate(order, 1):
        dst = os.path.join(outdir, f"{slug}_carousel_{i:02d}.png")
        shutil.copy(src, dst)
        outs.append(dst)
    return outs

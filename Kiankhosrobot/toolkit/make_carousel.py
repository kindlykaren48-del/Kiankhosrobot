"""
make_carousel.py — سازندهٔ کاروسل اینستاگرام (۱۰۸۰×۱۳۵۰)

خروجی: مجموعه‌ای از PNGهای شماره‌دار + فایل کپشن.
متن فارسی با fatext (HarfBuzz/FreeType) رندر می‌شود؛ فونت فقط وزیرمتن.

استفاده:
    cfg = {...}
    from make_carousel import build_carousel
    build_carousel(cfg, outdir="/path/to/out")
"""
from __future__ import annotations

import os
import sys

from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from icons import icon  # noqa: E402

try:
    from fatext import FD as _FD
    HAVE_FATEXT = True
except Exception:                                    # pragma: no cover
    _FD = None
    HAVE_FATEXT = False

try:
    from PIL import features as _features
    HAVE_RAQM = bool(_features.check("raqm"))
except Exception:                                    # pragma: no cover
    HAVE_RAQM = False

if not HAVE_FATEXT and not HAVE_RAQM:
    print("!! هشدار: نه fatext و نه libraqm موجود نیست؛ متن فارسی درست چیده نمی‌شود.")

KW = dict(language="fa", direction="rtl")


def _draw(image, mode="RGBA"):
    if HAVE_FATEXT:
        return _FD(image, mode)
    return ImageDraw.Draw(image, mode)


def _text(d, xy, txt, font, fill, anchor="mm"):
    if HAVE_FATEXT:
        return d.text(xy, txt, font=font, fill=fill, anchor=anchor)
    return d.text(xy, txt, font=font, fill=fill, anchor=anchor, **KW)


def _tw(d, txt, font):
    """پهنای تقریبی متن."""
    if HAVE_FATEXT:
        bb = d.textbbox((0, 0), txt, font=font, anchor="lm")
    else:
        bb = d.textbbox((0, 0), txt, font=font, anchor="lm", **KW)
    return bb[2] - bb[0]


def _find_font_dir():
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(os.path.dirname(here))
    cands = [os.environ.get("REEL_FONTS", ""),
             os.path.join(root, "fonttmp", "fonts", "ttf"),
             "/home/user/fonttmp/fonts/ttf",
             "/home/user/Kiankhosrobot/fonttmp/fonts/ttf"]
    for c in cands:
        if c and os.path.isfile(os.path.join(c, "Vazirmatn-Bold.ttf")):
            return c
    raise SystemExit("فونت وزیرمتن پیدا نشد")


FTDIR = _find_font_dir()
BLACK = os.path.join(FTDIR, "Vazirmatn-Black.ttf")
BOLD = os.path.join(FTDIR, "Vazirmatn-Bold.ttf")
REG = os.path.join(FTDIR, "Vazirmatn-Medium.ttf")

W, H = 1080, 1350

PALETTES = {
    "tealamber": [((8, 58, 74), (16, 118, 132)), ((150, 86, 8), (226, 158, 36)),
                  ((10, 70, 88), (26, 140, 150)), ((128, 28, 48), (208, 64, 76)),
                  ((12, 62, 96), (34, 118, 176)), ((18, 92, 72), (46, 156, 110))],
    "purple":    [((76, 24, 122), (138, 70, 198)), ((14, 118, 128), (40, 178, 186)),
                  ((164, 34, 96), (226, 82, 146)), ((150, 96, 12), (230, 174, 44)),
                  ((40, 48, 128), (84, 110, 210)), ((18, 108, 78), (52, 170, 118))],
}


def _bg(img, c1, c2):
    d = _draw(img, "RGB")
    for y in range(H):
        f = y / H
        d.line([(0, y), (W, y)],
               fill=tuple(int(c1[k] + (c2[k] - c1[k]) * f) for k in range(3)))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    for (cx, cy, r, a) in [(140, 230, 240, 38), (960, 1080, 300, 32),
                           (900, 190, 170, 28), (180, 1210, 220, 26)]:
        od.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255, a))
    ov = ov.filter(ImageFilter.GaussianBlur(40))
    return Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")


def cover_fill(im, w, h):
    r = max(w / im.width, h / im.height)
    im = im.resize((max(w, int(im.width * r)), max(h, int(im.height * r))), Image.LANCZOS)
    l, t = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((l, t, l + w, t + h))


def flatten(path):
    src = Image.open(path)
    base = Image.new("RGB", src.size, (255, 255, 255))
    if src.mode in ("RGBA", "LA"):
        base.paste(src.convert("RGB"), (0, 0), src.convert("RGBA").split()[-1])
    else:
        base.paste(src.convert("RGB"), (0, 0))
    return base


def _card(img, path, box, radius=40, ring=(255, 255, 255, 85)):
    """کارت تصویر گرد با قاب روشن. box = (x0, y0, w, h)"""
    x0, y0, cw, ch = box
    d = _draw(img)
    d.rounded_rectangle([x0 - 8, y0 - 8, x0 + cw + 8, y0 + ch + 8], radius + 8, fill=ring)
    card = cover_fill(flatten(path), cw, ch)
    mask = Image.new("L", (cw, ch), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, cw, ch], radius, fill=255)
    img.paste(card, (x0, y0), mask)


def _wrap(d, text, font, maxw):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if _tw(d, t, font) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def _fa_num(n):
    return str(n).translate(str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹"))


def _dots(img, idx, n, y, c_on=(255, 255, 255, 255), c_off=(255, 255, 255, 90)):
    d = _draw(img)
    step = 46
    x0 = W / 2 - (n - 1) * step / 2
    for k in range(n):
        x = x0 + k * step
        r = 13 if k == idx else 10
        d.ellipse([x - r, y - r, x + r, y + r], fill=c_on if k == idx else c_off)


def make_cover(cfg, pal, outdir, total):
    c1, c2 = pal[0]
    img = _bg(Image.new("RGB", (W, H)), c1, c2)
    d = _draw(img)

    fa = cfg["title_fa"]
    size = 104 if len(fa) <= 16 else (88 if len(fa) <= 24 else 74)
    f_title = ImageFont.truetype(BLACK, size)
    lines = _wrap(d, fa, f_title, W - 150)
    y = 150
    for ln in lines:
        _text(d, (W / 2, y), ln, f_title, (255, 236, 180), "mm")
        y += size + 16

    en = cfg.get("title_en", "").upper()
    if en:
        _text(d, (W / 2, y + 6), en, ImageFont.truetype(BOLD, 36), (255, 255, 255, 220), "mm")
        y += 64

    sub = cfg.get("subtitle", "")
    if sub:
        f_sub = ImageFont.truetype(BOLD, 40)
        hw = min(W / 2 - 60, _tw(d, sub, f_sub) / 2 + 40)
        d.rounded_rectangle([W / 2 - hw, y + 6, W / 2 + hw, y + 90], 42,
                            fill=(255, 255, 255, 40), outline=(255, 215, 130, 210), width=3)
        _text(d, (W / 2, y + 48), sub, f_sub, (255, 236, 190), "mm")
        y += 118

    cw = 820
    ch = int(H - 120 - y)
    _card(img, cfg["cover_ill"], ((W - cw) // 2, int(y + 18), cw, ch - 18), 44)

    d = _draw(img)
    f_sw = ImageFont.truetype(BOLD, 34)
    sw = cfg.get("swipe", "بکش ←")
    pw = _tw(d, sw, f_sw) / 2 + 34
    d.rounded_rectangle([W - 60 - 2 * pw, H - 96, W - 60, H - 28], 34, fill=(12, 6, 30, 200))
    _text(d, (W - 60 - pw, H - 62), sw, f_sw, (255, 232, 170), "mm")
    _text(d, (70, H - 62), cfg.get("brand", ""), ImageFont.truetype(BOLD, 30),
          (255, 255, 255, 210), "lm")

    p = os.path.join(outdir, f"{cfg['slug']}_01.png")
    img.save(p)
    return p


def make_slide(i, cfg, pal, outdir, total):
    num, fa, en, ill, items = cfg["slides"][i]
    c1, c2 = pal[(i + 1) % len(pal)]
    img = _bg(Image.new("RGB", (W, H)), c1, c2)
    d = _draw(img)

    # سربرگ
    d.ellipse([64, 86, 198, 220], fill=(255, 255, 255, 240))
    _text(d, (131, 153), num, ImageFont.truetype(BLACK, 72), c1, "mm")
    f_h = ImageFont.truetype(BLACK, 62 if len(fa) <= 18 else 52)
    _text(d, (W - 70, 120), fa, f_h, (255, 255, 255), "ra")
    if en:
        _text(d, (W - 70, 200), en.upper(), ImageFont.truetype(BOLD, 28),
              (255, 255, 255, 210), "ra")

    _dots(img, i + 1, total, 258)
    d = _draw(img)

    # کارت متن — بدون تصویر، متن درشت‌تر و کارت در میانهٔ کادر
    f_b = ImageFont.truetype(BOLD, 38 if ill else 43)
    lh = 50 if ill else 58
    pad = 26 if ill else 34
    bx0, bx1 = 62, W - 62
    maxw = (bx1 - bx0) - (190 if ill else 170)
    rows = []
    for ic, tx in items:
        rows.append((ic, _wrap(d, tx, f_b, maxw)))
    body_h = sum(max(1, len(r[1])) * lh + pad for r in rows) + 36
    by0 = 300 if ill else max(300, int((H - 120 - body_h) / 2) + 60)
    by1 = by0 + body_h
    d.rounded_rectangle([bx0, by0, bx1, by1], 42, fill=(10, 6, 28, 226),
                        outline=(255, 255, 255, 62), width=3)
    y = by0 + 30
    ir = 30 if ill else 36
    isz = 38 if ill else 46
    for ic, lns in rows:
        block = max(1, len(lns)) * lh
        cy = y + block / 2
        d.ellipse([bx0 + 30, cy - ir, bx0 + 30 + 2 * ir, cy + ir], fill=(255, 255, 255, 240))
        ic_im = icon(ic, isz, (26, 20, 56))
        img.paste(ic_im, (int(bx0 + 30 + ir - isz / 2), int(cy - isz / 2)), ic_im)
        d = _draw(img)
        yy = y + lh / 2
        for ln in lns:
            _text(d, (bx1 - 36, yy), ln, f_b, (255, 255, 255), "rm")
            yy += lh
        y += block + pad

    # کارت تصویر
    if ill:
        cw = 740
        ch = int(H - 110 - (by1 + 36))
        if ch > 220:
            _card(img, ill, ((W - cw) // 2, int(by1 + 36), cw, ch), 40)

    d = _draw(img)
    _text(d, (W - 70, H - 58), cfg.get("brand", ""), ImageFont.truetype(BOLD, 28),
          (255, 255, 255, 190), "rm")
    _text(d, (70, H - 58), _fa_num(i + 2) + "/" + _fa_num(total), ImageFont.truetype(BOLD, 28),
          (255, 255, 255, 170), "lm")

    p = os.path.join(outdir, f"{cfg['slug']}_{i + 2:02d}.png")
    img.save(p)
    return p


def make_last(cfg, pal, outdir, total):
    c1, c2 = pal[(len(cfg["slides"]) + 1) % len(pal)]
    img = _bg(Image.new("RGB", (W, H)), c1, c2)
    d = _draw(img)

    _text(d, (W / 2, 190), cfg.get("end_title", "ذخیره کن!"),
          ImageFont.truetype(BLACK, 96), (255, 238, 180), "mm")
    f_b = ImageFont.truetype(BOLD, 40)
    y = 330
    for tx in cfg.get("takeaways", []):
        lns = _wrap(d, tx, f_b, W - 260)
        h = len(lns) * 52 + 36
        d.rounded_rectangle([70, y, W - 70, y + h], 34, fill=(10, 6, 28, 215),
                            outline=(255, 255, 255, 60), width=2)
        yy = y + 18 + 26
        for ln in lns:
            _text(d, (W - 110, yy), ln, f_b, (255, 255, 255), "rm")
            yy += 52
        d.ellipse([92, y + h / 2 - 11, 114, y + h / 2 + 11], fill=(255, 215, 130, 240))
        y += h + 22

    d.rounded_rectangle([W / 2 - 300, y + 30, W / 2 + 300, y + 132], 50,
                        fill=(255, 255, 255, 235))
    _text(d, (W / 2, y + 81), cfg.get("cta_btn", "ذخیره  •  اشتراک‌گذاری"),
          ImageFont.truetype(BOLD, 40), (26, 20, 56), "mm")
    _text(d, (W / 2, y + 196), cfg.get("cta", ""), ImageFont.truetype(REG, 34),
          (255, 255, 255, 215), "mm")

    _dots(img, total - 1, total, H - 170)
    d = _draw(img)
    _text(d, (W / 2, H - 92), cfg.get("brand", ""), ImageFont.truetype(BOLD, 36),
          (255, 255, 255, 230), "mm")
    _text(d, (W / 2, H - 46), cfg.get("disclaimer", ""), ImageFont.truetype(REG, 26),
          (255, 255, 255, 170), "mm")

    p = os.path.join(outdir, f"{cfg['slug']}_{total:02d}.png")
    img.save(p)
    return p


def build_carousel(cfg, outdir):
    os.makedirs(outdir, exist_ok=True)
    pal = cfg["palette"] if isinstance(cfg.get("palette"), list) \
        else PALETTES.get(cfg.get("palette", "tealamber"), PALETTES["tealamber"])
    total = len(cfg["slides"]) + 2          # کاور + اسلایدها + اسلاید پایانی
    out = [make_cover(cfg, pal, outdir, total)]
    for i in range(len(cfg["slides"])):
        out.append(make_slide(i, cfg, pal, outdir, total))
    out.append(make_last(cfg, pal, outdir, total))
    if cfg.get("caption"):
        cp = os.path.join(outdir, f"{cfg['slug']}_caption.txt")
        with open(cp, "w", encoding="utf-8") as fh:
            fh.write(cfg["caption"].strip() + "\n")
        out.append(cp)
    return out

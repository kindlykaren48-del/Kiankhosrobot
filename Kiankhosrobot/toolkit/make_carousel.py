"""
make_carousel.py — موتور ساخت کاروسل ۴:۵ (۱۰۸۰×۱۳۵۰) به سبک اسلایدهای ریل
استایل: نئون مولتی‌کالر — هر اسلاید یک رنگ نئون، پس‌زمینهٔ تیره، متن با هالهٔ نئون،
کارت تصویر ۴:۵، کارت‌های نکته و نوار پیشرفت.

همهٔ متن‌های فارسی با fatext (HarfBuzz + FreeType) شکل‌دهی می‌شوند؛ نیازی به libraqm نیست.
خروجی: <outdir>/slide_1.png ... slide_N.png
"""
from __future__ import annotations

import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

from fatext import FD
from icons import icon

W, H = 1080, 1350
M = 56                                   # حاشیهٔ کناری
MAXW = W - 2 * M                         # عرض مفید
CARD_R = 40

NEXT_PAL = [
    (255, 62, 165),      # سرخابی
    (0, 226, 255),       # فیروزه‌ای
    (168, 85, 247),      # بنفش نئون
    (255, 176, 32),      # کهربایی
    (150, 255, 74),      # لیمویی
    (255, 86, 96),       # قرمز-صورتی
]


def _find_font_dir():
    cands = [os.environ.get("REEL_FONTS", ""),
             "/home/user/fonttmp/fonts/ttf/",
             os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
                 os.path.abspath(__file__)))), "fonttmp", "fonts", "ttf"),
             "/home/user/Kiankhosrobot/fonttmp/fonts/ttf/",
             os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonttmp", "fonts", "ttf")]
    for c in cands:
        if c and os.path.isfile(os.path.join(c, "Vazirmatn-Bold.ttf")):
            return c if c.endswith("/") else c + "/"
    return cands[1]


FTDIR = _find_font_dir()
BLACK = FTDIR + "Vazirmatn-Black.ttf"
BOLD = FTDIR + "Vazirmatn-Bold.ttf"
REG = FTDIR + "Vazirmatn-Medium.ttf"


def fnt(p, s):
    return ImageFont.truetype(p, s)


def fa_num(n):
    return str(n).translate(str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹"))


def cover_fill(im, w, h):
    r = max(w / im.width, h / im.height)
    im = im.resize((max(w, int(im.width * r)), max(h, int(im.height * r))), Image.LANCZOS)
    l, t = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((l, t, l + w, t + h))


def flatten(path):
    src = Image.open(path)
    base = Image.new("RGB", src.size, (12, 12, 16))
    if src.mode in ("RGBA", "LA"):
        base.paste(src.convert("RGB"), (0, 0), src.convert("RGBA").split()[-1])
    else:
        base.paste(src.convert("RGB"), (0, 0))
    return base


# ----------------------------------------------------------- text (HarfBuzz)
def tlen(img, text, font):
    return FD(img).textlength(text, font)


def wrap(img, text, font, maxw):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if tlen(img, t, font) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def ptext(img, xy, text, font, color, anchor="ra"):
    """متن فارسی با شکل‌دهی HarfBuzz."""
    return FD(img).text(xy, text, font=font, fill=color, anchor=anchor)


def neon_text(img, xy, text, font, color, anchor="ra", glow=20, galpha=0.85, gcolor=None):
    d = FD(img)
    mask, pos = d.text_mask(text, font, xy=xy, anchor=anchor)
    if glow:
        gc = gcolor or color
        gm = mask.filter(ImageFilter.GaussianBlur(glow))
        gl = Image.new("RGBA", gm.size, (gc[0], gc[1], gc[2], 0))
        gl.putalpha(gm.point(lambda v: int(v * galpha)))
        img.alpha_composite(gl, pos)
    ptext(img, xy, text, font, color, anchor=anchor)
    return mask.size


# ------------------------------------------------------------------ shapes
def layer(img):
    return Image.new("RGBA", img.size, (0, 0, 0, 0))


def glass_card(img, box, radius, acc, fill=(14, 14, 19, 232), bw=3, glow=True):
    if glow:
        gl = layer(img)
        ImageDraw.Draw(gl).rounded_rectangle([box[0] - 14, box[1] - 14, box[2] + 14, box[3] + 14],
                                             radius + 14, outline=acc + (85,), width=8)
        img.alpha_composite(gl.filter(ImageFilter.GaussianBlur(16)))
    ov = layer(img)
    ImageDraw.Draw(ov).rounded_rectangle(box, radius, fill=fill, outline=acc + (240,), width=bw)
    img.alpha_composite(ov)


def pill(img, box, radius, acc, fill=(14, 14, 19, 226), bw=3):
    ov = layer(img)
    ImageDraw.Draw(ov).rounded_rectangle(box, radius, fill=fill, outline=acc + (235,), width=bw)
    img.alpha_composite(ov)


def dot(img, cx, cy, r, col):
    ov = layer(img)
    ImageDraw.Draw(ov).ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
    img.alpha_composite(ov)


def bar(img, box, radius, col):
    ov = layer(img)
    ImageDraw.Draw(ov).rounded_rectangle(box, radius, fill=col)
    img.alpha_composite(ov)


def photo_card(img, path, x0, y0, w, h, acc, radius=CARD_R):
    gl = layer(img)
    gd = ImageDraw.Draw(gl)
    for g, a, lw in ((30, 30, 9), (18, 48, 8), (9, 78, 7)):
        gd.rounded_rectangle([x0 - g, y0 - g, x0 + w + g, y0 + h + g], radius + g,
                             outline=acc + (a,), width=lw)
    img.alpha_composite(gl.filter(ImageFilter.GaussianBlur(17)))

    card = cover_fill(flatten(path), w, h).convert("RGBA")
    cm = Image.new("L", (w, h), 0)
    ImageDraw.Draw(cm).rounded_rectangle([0, 0, w - 1, h - 1], radius, fill=255)
    card.putalpha(cm)
    img.alpha_composite(card, (x0, y0))

    ov = layer(img)
    d = ImageDraw.Draw(ov)
    d.rounded_rectangle([x0 + 3, y0 + 3, x0 + w - 3, y0 + h - 3], radius,
                        outline=(255, 255, 255, 50), width=2)
    d.rounded_rectangle([x0 - 3, y0 - 3, x0 + w + 3, y0 + h + 3], radius + 4,
                        outline=acc + (255,), width=5)
    img.alpha_composite(ov)


def paste_icon(img, name, size, col, xy):
    img.alpha_composite(icon(name, size, col), (int(xy[0]), int(xy[1])))


# ------------------------------------------------------------------ background
def make_bg(accents, seed=7):
    img = Image.new("RGB", (W, H), (9, 9, 13)).convert("RGBA")
    ov = layer(img)
    od = ImageDraw.Draw(ov)
    spots = [(110, 170, 560), (985, 600, 520), (150, 1120, 600), (955, 1300, 470),
             (540, 60, 420)]
    for i, (cx, cy, r) in enumerate(spots):
        c = accents[i % len(accents)]
        od.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(c[0], c[1], c[2], 62))
    img.alpha_composite(ov.filter(ImageFilter.GaussianBlur(215)))

    ov2 = layer(img)
    d = ImageDraw.Draw(ov2)
    for k in range(4):
        y = 60 + k * 380
        d.arc([-470, y, W + 470, y + 520], 200, 340, fill=(255, 140, 30, 20), width=5)
    for k in range(3):
        y = 240 + k * 470
        d.arc([-430, y, W + 430, y + 470], 195, 348, fill=(255, 255, 255, 14), width=4)
    img.alpha_composite(ov2)

    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).ellipse([-W * 0.34, -H * 0.26, W * 1.34, H * 1.26], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(185))
    vig = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vig.putalpha(m.point(lambda v: int(150 * (1 - v / 255))))
    img.alpha_composite(vig)

    arr = np.asarray(img.convert("RGB")).astype(np.int16)
    n = np.random.default_rng(seed).integers(-4, 5, (H, W, 1))
    return Image.fromarray(np.clip(arr + n, 0, 255).astype(np.uint8), "RGB").convert("RGBA")


# ------------------------------------------------------------------ pieces
def progress(img, i, n, pal):
    y, th, gap = 46, 13, 10
    sw = (MAXW - gap * (n - 1)) / n
    for k in range(n):
        x1 = W - M - k * (sw + gap)
        x0 = x1 - sw
        if k <= i:
            bar(img, [x0, y, x1, y + th], th / 2, pal[k % len(pal)] + (255,))
        else:
            bar(img, [x0, y, x1, y + th], th / 2, (255, 255, 255, 46))


def nameplate(img, name, glyph, acc, counter=None):
    f = fnt(BOLD, 32)
    tw = tlen(img, name, f)
    bw, bh = tw + 124, 62
    x1, y0 = W - M + 14, 90
    x0 = x1 - bw
    glass_card(img, [x0, y0, x1, y0 + bh], bh / 2, acc, fill=(16, 16, 21, 214), bw=2, glow=False)
    paste_icon(img, glyph, 34, acc, (x1 - 46, y0 + 14))
    ptext(img, (x1 - 78, y0 + bh / 2), name, f, (240, 240, 245, 245), anchor="rm")
    if counter:
        ptext(img, (M - 14, y0 + bh / 2), counter, f, (232, 232, 238, 180), anchor="lm")


def kicker(img, text, acc):
    f = fnt(BOLD, 36)
    tw = tlen(img, text, f)
    x1, y0 = W - M + 14, 178
    bw, bh = tw + 118, 60
    x0 = x1 - bw
    pill(img, [x0, y0, x1, y0 + bh], bh / 2, acc, fill=(14, 14, 19, 224), bw=3)
    dot(img, x1 - 36, y0 + bh / 2, 9, acc + (255,))
    ptext(img, (x1 - 58, y0 + bh / 2), text, f, acc + (255,), anchor="rm")


def headline(img, lines, acc):
    """lines: فهرست [(متن, 'w'|'a')] — تک‌اندازه، راست‌چین، با هالهٔ نئون."""
    size = 82
    while size > 50:
        f = fnt(BLACK, size)
        if all(tlen(img, t, f) <= MAXW for t, _ in lines):
            break
        size -= 2
    f = fnt(BLACK, size)
    lh = int(size * 1.26)
    y = 266
    for t, kind in lines:
        col = acc + (255,) if kind == "a" else (255, 255, 255, 252)
        neon_text(img, (W - M + 14, y), t, f, col, anchor="ra",
                  glow=27, galpha=0.55 if kind == "a" else 0.34)
        y += lh
    return y


def en_label(img, text, y):
    ov = layer(img)
    ImageDraw.Draw(ov).text((W - M + 14, y), "  ".join(list(text.upper())),
                            font=fnt(BOLD, 27), fill=(255, 255, 255, 130), anchor="ra")
    img.alpha_composite(ov)
    return y + 40


def note_strip(img, gl, tx, acc, x0, x1, y0):
    f = fnt(BOLD, 28)
    lines = wrap(img, tx, f, (x1 - x0) - 128)
    lh = int(28 * 1.45)
    h = 30 + len(lines) * lh
    glass_card(img, [x0, y0, x1, y0 + h], 26, acc, fill=(13, 13, 18, 226), bw=3, glow=True)
    paste_icon(img, gl, 34, acc, (x1 - 52, y0 + 16))
    ty = y0 + 17
    for ln in lines:
        ptext(img, (x1 - 72, ty), ln, f, acc + (255,), anchor="ra")
        ty += lh
    return h


def tip_cards(img, tips, card_w, x_right, y0, y1, pal, base_i):
    """ستون راست: کارت نکته با آیکون در دایرهٔ رنگی (راست) و متن چپ آن."""
    n = len(tips)
    gap = 14
    ch = (y1 - y0 - gap * (n - 1)) / n
    ir = 28
    text_w = card_w - 40 - ir * 2 - 26
    for k, (gl, tx) in enumerate(tips):
        c = pal[(base_i + k) % len(pal)]
        cy0 = y0 + k * (ch + gap)
        cx0 = x_right - card_w
        glass_card(img, [cx0, cy0, x_right, cy0 + ch], 30, c, fill=(13, 13, 18, 236), bw=3)
        ir2 = int(min(ir + 4, ch / 3.6))
        cx, cy = x_right - 28 - ir2, cy0 + 28 + ir2
        dot(img, cx, cy, ir2, c + (255,))
        paste_icon(img, gl, int(ir2 * 1.1), (12, 12, 14), (cx - ir2 * 0.55, cy - ir2 * 0.55))

        lines, fs = None, None
        for size in (36, 34, 32, 30, 28, 26, 24):
            f = fnt(BOLD, size)
            ls = wrap(img, tx, f, text_w)
            if len(ls) * int(size * 1.42) <= ch - 40:
                lines, fs = ls, size
                break
        if lines is None:
            fs = 24
            f = fnt(BOLD, fs)
            lines = wrap(img, tx, f, text_w)
        f = fnt(BOLD, fs)
        lh = int(fs * 1.42)
        ty = cy0 + (ch - len(lines) * lh) / 2 + (lh - fs) / 2
        for ln in lines:
            ptext(img, (cx - ir2 - 24, ty), ln, f, (246, 246, 250, 248), anchor="ra")
            ty += lh


# ------------------------------------------------------------------ slide
def render_slide(i, cfg, out_path):
    n = len(cfg["slides"])
    s = cfg["slides"][i]
    acc = NEXT_PAL[i % len(NEXT_PAL)]
    img = make_bg([acc, NEXT_PAL[(i + 1) % len(NEXT_PAL)], acc,
                   NEXT_PAL[(i + 3) % len(NEXT_PAL)]], seed=11 + i)

    progress(img, i, n, NEXT_PAL)
    nameplate(img, cfg.get("nameplate", ""), cfg.get("glyph", "stetho"), acc,
              counter=f"{fa_num(i + 1)}/{fa_num(n)}")
    kicker(img, s["kicker"], acc)
    y = headline(img, s["headline"], acc) + 6
    if s.get("en"):
        y = en_label(img, s["en"], y) + 6
    y0 = y + 18

    bottom = 1306
    note = s.get("note")
    strip_f = fnt(BOLD, 28)
    strip_h = 0
    if note:
        # ارتفاع نوار پایین را با فرض پهنای بیشینه حساب می‌کنیم
        ls = wrap(img, note[1], strip_f, 470)
        strip_h = 30 + len(ls) * int(28 * 1.45) + 24

    avail = bottom - y0 - strip_h
    ih = int(min(700, avail))
    iw = int(ih * 4 / 5)
    src = cfg.get("src", "")
    photo_card(img, os.path.join(src, s["img"]), M, y0, iw, ih, acc)

    tip_cards(img, s["tips"], W - 2 * M - iw - 30, W - M, y0, y0 + ih, NEXT_PAL, i)

    if note:
        note_strip(img, note[0], note[1], acc, M, M + iw, y0 + ih + 24)

    img.convert("RGB").save(out_path, quality=95)
    return out_path


def build_carousel(cfg, outdir="."):
    os.makedirs(outdir, exist_ok=True)
    outs = []
    for i in range(len(cfg["slides"])):
        p = os.path.join(outdir, f"slide_{i + 1}.png")
        render_slide(i, cfg, p)
        outs.append(p)
        print("OK", p)
    return outs

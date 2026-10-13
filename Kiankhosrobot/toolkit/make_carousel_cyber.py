"""
make_carousel_cyber.py — موتور کاروسل ۴:۵ (۱۰۸۰×۱۳۵۰) با استایل «سایبرپانک»
شامل: کاور + اسلایدها + CTA.

ویژگی‌های ظاهری: پس‌زمینهٔ تیرهٔ آبی-بنفش، گرید پرسپکتیو، اسکن‌لاین، گلیچ باندی،
گوشه‌های HUD، کارت‌های لبه‌بُر (chamfer)، برچسب‌های مونو-اسپیس لاتین و هالهٔ نئون.
متن فارسی با fatext (HarfBuzz) رندر می‌شود؛ نیازی به libraqm نیست.

خروجی: <outdir>/cover.png ، slide_1..N.png ، cta.png
"""
from __future__ import annotations

import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

from fatext import FD
from icons import icon
from make_carousel import (W, H, M, MAXW, fnt, fa_num, cover_fill, flatten,
                           tlen, wrap, ptext, neon_text, layer, paste_icon, BLACK, BOLD, REG)

MONO_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
if not os.path.isfile(MONO_PATH):
    MONO_PATH = BOLD


def mono(size):
    return ImageFont.truetype(MONO_PATH, size)


CYAN, MAGENTA, AMBER, VIOLET = (0, 229, 255), (255, 45, 149), (255, 209, 0), (150, 90, 255)
ACCENTS = [CYAN, MAGENTA, AMBER, VIOLET, CYAN, MAGENTA]


# ------------------------------------------------------------------ background
def make_bg_cyber(accents, seed=3):
    img = Image.new("RGB", (W, H), (7, 8, 17)).convert("RGBA")
    ov = layer(img)
    od = ImageDraw.Draw(ov)
    spots = [(140, 200, 620), (960, 640, 560), (200, 1180, 640), (930, 1250, 460)]
    for i, (cx, cy, r) in enumerate(spots):
        c = accents[i % len(accents)]
        od.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(c[0], c[1], c[2], 58))
    img.alpha_composite(ov.filter(ImageFilter.GaussianBlur(200)))

    # گرید پرسپکتیو کف
    g = layer(img)
    gd = ImageDraw.Draw(g)
    HOR = 1000
    vx, vy = W / 2, HOR
    for x in np.linspace(-900, 2100, 26):
        gd.line([(x, H + 60), (vx + (x - vx) * 0.12, vy)], fill=CYAN + (26,), width=2)
    for i in range(1, 17):
        y = HOR + (i ** 1.85) * 2.4
        if y < H:
            gd.line([(0, y), (W, y)], fill=CYAN + (22,), width=2)
    for i in range(9):          # گرید سقف (محو)
        y = 60 + i * 46
        gd.line([(0, y), (W, y)], fill=MAGENTA + (10,), width=1)
    for x in range(0, W, 96):
        gd.line([(x, 0), (x, 620)], fill=MAGENTA + (9,), width=1)
    img.alpha_composite(g.filter(ImageFilter.GaussianBlur(0.6)))

    # اسکن‌لاین
    sl = layer(img)
    sd = ImageDraw.Draw(sl)
    for y in range(0, H, 4):
        sd.line([(0, y), (W, y)], fill=(0, 0, 0, 26), width=1)
    img.alpha_composite(sl)

    # گلیچ‌باندها
    rng = np.random.default_rng(seed)
    gl = layer(img)
    gd = ImageDraw.Draw(gl)
    for _ in range(4):
        y = float(rng.integers(80, H - 80))
        h = float(rng.integers(6, 22))
        c = accents[int(rng.integers(0, len(accents)))]
        gd.rectangle([0, y, W, y + h], fill=c + (30,))
    img.alpha_composite(gl.filter(ImageFilter.GaussianBlur(2.2)))

    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).ellipse([-W * 0.34, -H * 0.26, W * 1.34, H * 1.26], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(185))
    vig = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vig.putalpha(m.point(lambda v: int(165 * (1 - v / 255))))
    img.alpha_composite(vig)

    arr = np.asarray(img.convert("RGB")).astype(np.int16)
    n = rng.integers(-5, 6, (H, W, 1))
    return Image.fromarray(np.clip(arr + n, 0, 255).astype(np.uint8), "RGB").convert("RGBA")


# ------------------------------------------------------------------ cyber parts
def chamfer_pts(box, cut):
    x0, y0, x1, y1 = box
    return [(x0 + cut, y0), (x1, y0), (x1, y1 - cut), (x1 - cut, y1),
            (x0, y1), (x0, y0 + cut)]


def chamfer_card(img, box, acc, cut=28, fill=(10, 12, 21, 236), bw=3, glow=True):
    pts = chamfer_pts(box, cut)
    if glow:
        gl = layer(img)
        ImageDraw.Draw(gl).polygon(pts, outline=acc + (95,), width=9)
        img.alpha_composite(gl.filter(ImageFilter.GaussianBlur(15)))
    ov = layer(img)
    d = ImageDraw.Draw(ov)
    d.polygon(pts, fill=fill, outline=acc + (245,))
    for k in range(bw):
        d.line(pts + [pts[0]], fill=acc + (150,), width=1)
    img.alpha_composite(ov)
    # نوار دادهٔ نازک داخل لبهٔ بالا
    bar(img, [box[0] + cut + 6, box[1] + 7, box[0] + cut + 76, box[1] + 11], 2, acc + (210,))


def bar(img, box, radius, col):
    ov = layer(img)
    ImageDraw.Draw(ov).rounded_rectangle(box, radius, fill=col)
    img.alpha_composite(ov)


def dot(img, cx, cy, r, col):
    ov = layer(img)
    ImageDraw.Draw(ov).ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
    img.alpha_composite(ov)


def hud_brackets(img, acc, alpha=210):
    ov = layer(img)
    d = ImageDraw.Draw(ov)
    L, w = 78, 5
    for (x, y, sx, sy) in ((M - 22, 118, 1, 1), (W - M + 22, 118, -1, 1),
                           (M - 22, H - 60, 1, -1), (W - M + 22, H - 60, -1, -1)):
        d.line([(x, y), (x + sx * L, y)], fill=acc + (alpha,), width=w)
        d.line([(x, y), (x, y + sy * L)], fill=acc + (alpha,), width=w)
    img.alpha_composite(ov)


def hazard_strip(img, acc, y1, h=16, alpha=70):
    ov = layer(img)
    d = ImageDraw.Draw(ov)
    step = 34
    for x in range(-60, W + 60, step):
        d.polygon([(x, y1 + h), (x + h, y1), (x + h + step / 2, y1),
                   (x + step / 2, y1 + h)], fill=acc + (alpha,))
    img.alpha_composite(ov)


def progress(img, i, n, pal):
    y, th, gap = 46, 14, 12
    sw = (MAXW - gap * (n - 1)) / n
    for k in range(n):
        x1 = W - M - k * (sw + gap)
        x0 = x1 - sw
        c = pal[k % len(pal)]
        ov = layer(img)
        d = ImageDraw.Draw(ov)
        d.rectangle([x0, y, x1, y + th], outline=(255, 255, 255, 70), width=2)
        if k <= i:
            d.rectangle([x0 + 3, y + 3, x1 - 3, y + th - 3], fill=c + (255,))
        img.alpha_composite(ov)


def mono_tag(img, text, xy, acc, size=30, anchor="ra"):
    ov = layer(img)
    ImageDraw.Draw(ov).text(xy, text, font=mono(size), fill=acc + (240,), anchor=anchor)
    img.alpha_composite(ov)


def nameplate(img, name, acc, counter=None):
    f = fnt(BOLD, 32)
    tw = tlen(img, name, f)
    bw, bh = tw + 210, 64
    x1, y0 = W - M + 14, 90
    x0 = x1 - bw
    chamfer_card(img, [x0, y0, x1, y0 + bh], acc, 22, fill=(10, 12, 21, 232), bw=2, glow=False)
    mono_tag(img, "DR.KS", (x0 + 22, y0 + bh / 2), acc, 30, anchor="lm")
    ptext(img, (x1 - 22, y0 + bh / 2), name, f, (238, 240, 248, 246), anchor="rm")
    if counter:
        ptext(img, (W - M + 14, 196), counter, f, (225, 230, 242, 215), anchor="rm")


def cyber_photo(img, path, x0, y0, w, h, acc, cut=36):
    pts = chamfer_pts([x0, y0, x0 + w, y0 + h], cut)
    gl = layer(img)
    gd = ImageDraw.Draw(gl)
    gd.polygon(pts, outline=acc + (110,), width=10)
    gd.polygon([(x0 - 22, y0 - 22), (x0 + w + 22, y0 - 22), (x0 + w + 22, y0 + h + 22),
                (x0 - 22, y0 + h + 22)], outline=MAGENTA + (60,), width=6)
    img.alpha_composite(gl.filter(ImageFilter.GaussianBlur(16)))

    card = cover_fill(flatten(path), w, h).convert("RGBA")
    cm = Image.new("L", (w, h), 0)
    ImageDraw.Draw(cm).polygon([(cut, 0), (w, 0), (w, h - cut), (w - cut, h), (0, h), (0, cut)],
                               fill=255)
    card.putalpha(cm)
    img.alpha_composite(card, (x0, y0))

    ov = layer(img)
    d = ImageDraw.Draw(ov)
    d.polygon(pts, outline=acc + (255,), width=5)
    for (px, py, sx, sy) in ((x0, y0, 1, 1), (x0 + w, y0, -1, 1),
                             (x0, y0 + h, 1, -1), (x0 + w, y0 + h, -1, -1)):
        d.line([(px, py), (px + sx * 60, py)], fill=(255, 255, 255, 200), width=5)
        d.line([(px, py), (px, py + sy * 60)], fill=(255, 255, 255, 200), width=5)
    img.alpha_composite(ov)


def glitch_title(img, xy, text, font, col, acc, glow=26):
    """تیتر با اعوجاج رنگی (فریج رنگی سایبرپنک)."""
    d = FD(img)
    mask, pos = d.text_mask(text, font, xy=(xy[0] - 4, xy[1]), anchor="ra")
    lay = Image.new("RGBA", mask.size, CYAN + (0,))
    lay.putalpha(mask.filter(ImageFilter.GaussianBlur(1)).point(lambda v: int(v * 0.55)))
    img.alpha_composite(lay, pos)
    mask2, pos2 = d.text_mask(text, font, xy=(xy[0] + 4, xy[1]), anchor="ra")
    lay2 = Image.new("RGBA", mask2.size, MAGENTA + (0,))
    lay2.putalpha(mask2.filter(ImageFilter.GaussianBlur(1)).point(lambda v: int(v * 0.55)))
    img.alpha_composite(lay2, pos2)
    neon_text(img, xy, text, font, col, anchor="ra", glow=glow, galpha=0.6)


def headline(img, lines, acc):
    size = 82
    while size > 50:
        f = fnt(BLACK, size)
        if all(tlen(img, t, f) <= MAXW for t, _ in lines):
            break
        size -= 2
    f = fnt(BLACK, size)
    lh = int(size * 1.26)
    y = 268
    for t, kind in lines:
        col = acc + (255,) if kind == "a" else (255, 255, 255, 252)
        if kind == "a":
            glitch_title(img, (W - M + 14, y), t, f, col, acc)
        else:
            neon_text(img, (W - M + 14, y), t, f, col, anchor="ra", glow=24, galpha=0.34)
        y += lh
    return y


def en_label(img, text, y):
    mono_tag(img, text.upper(), (W - M + 14, y + 6), (232, 236, 246), 26)
    return y + 42


def cyber_tips(img, tips, card_w, x_right, y0, y1, pal, base_i):
    n = len(tips)
    gap = 14
    ch = (y1 - y0 - gap * (n - 1)) / n
    ir = 28
    text_w = card_w - 44 - ir * 2 - 26
    for k, (gl, tx) in enumerate(tips):
        c = pal[(base_i + k) % len(pal)]
        cy0 = y0 + k * (ch + gap)
        cx0 = x_right - card_w
        chamfer_card(img, [cx0, cy0, x_right, cy0 + ch], c, 26, fill=(10, 12, 21, 240), bw=3)
        ir2 = int(min(ir + 4, ch / 3.6))
        cx, cy = x_right - 30 - ir2, cy0 + 30 + ir2
        dot(img, cx, cy, ir2 + 4, c + (60,))
        dot(img, cx, cy, ir2, c + (255,))
        paste_icon(img, gl, int(ir2 * 1.1), (8, 10, 18), (cx - ir2 * 0.55, cy - ir2 * 0.55))

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
            ptext(img, (cx - ir2 - 26, ty), ln, f, (244, 246, 252, 250), anchor="ra")
            ty += lh
        mono_tag(img, f"0{k+1}", (cx0 + 18, cy0 + ch - 18), c, 22, anchor="ls")


def cyber_note(img, gl, tx, acc, x0, x1, y0):
    f = fnt(BOLD, 28)
    lines = wrap(img, tx, f, (x1 - x0) - 190)
    lh = int(28 * 1.45)
    h = 30 + len(lines) * lh
    chamfer_card(img, [x0, y0, x1, y0 + h], acc, 24, fill=(10, 12, 21, 232), bw=3)
    paste_icon(img, gl, 34, acc, (x1 - 54, y0 + 16))
    mono_tag(img, "NOTE", (x0 + 24, y0 + h / 2), acc, 24, anchor="lm")
    ty = y0 + 17
    for ln in lines:
        ptext(img, (x1 - 72, ty), ln, f, acc + (255,), anchor="ra")
        ty += lh
    return h


# ------------------------------------------------------------------ slides
def render_slide_cyber(i, cfg, s, out_path):
    n = len(cfg["slides"])
    acc = ACCENTS[i % len(ACCENTS)]
    img = make_bg_cyber([acc, ACCENTS[(i + 1) % len(ACCENTS)], acc,
                         ACCENTS[(i + 3) % len(ACCENTS)]], seed=21 + i)
    hud_brackets(img, acc)
    hazard_strip(img, acc, H - 42, 14, 60)
    progress(img, i, n, ACCENTS)
    nameplate(img, cfg.get("nameplate", ""), acc, counter=f"{fa_num(i+1)}/{fa_num(n)}")
    mono_tag(img, s.get("code", f"// MODULE_{i+1}"), (M, 196), acc, 30, anchor="lm")

    y = headline(img, s["headline"], acc) + 8
    if s.get("en"):
        y = en_label(img, s["en"], y) + 4
    y0 = y + 16

    bottom = 1290
    note = s.get("note")
    strip_h = 0
    if note:
        ls = wrap(img, note[1], fnt(BOLD, 28), 470)
        strip_h = 30 + len(ls) * int(28 * 1.45) + 26
    avail = bottom - y0 - strip_h
    ih = int(min(700, avail))
    iw = int(ih * 4 / 5)
    src = cfg.get("src", "")
    cyber_photo(img, os.path.join(src, s["img"]), M, y0, iw, ih, acc)
    cyber_tips(img, s["tips"], W - 2 * M - iw - 30, W - M, y0, y0 + ih, ACCENTS, i)
    if note:
        cyber_note(img, note[0], note[1], acc, M, M + iw, y0 + ih + 26)

    img.convert("RGB").save(out_path, quality=95)
    return out_path


# ------------------------------------------------------------------ cover
def render_cover_cyber(cfg, out_path):
    c = cfg["cover"]
    img = make_bg_cyber([CYAN, MAGENTA, CYAN, AMBER], seed=5)
    hud_brackets(img, CYAN)
    hazard_strip(img, CYAN, H - 42, 14, 60)
    mono_tag(img, "// PEDIATRIC CYBER-CARDS", (M, 196), CYAN, 30, anchor="lm")
    mono_tag(img, cfg.get("nameplate_en", "DR. KIANOOSH SALARIAN"),
             (W - M + 14, 196), MAGENTA, 26, anchor="rm")

    f = fnt(BLACK, 84)
    y = 300
    for t, kind in c["headline"]:
        colr = CYAN + (255,) if kind == "a" else (255, 255, 255, 253)
        if kind == "a":
            glitch_title(img, (W - M + 14, y), t, f, colr, CYAN)
        else:
            neon_text(img, (W - M + 14, y), t, f, colr, anchor="ra", glow=24, galpha=0.35)
        y += int(84 * 1.26)
    mono_tag(img, c["en"].upper(), (W - M + 14, y + 10), (232, 236, 246), 27)

    sub = c["subtitle"]
    fs = fnt(BOLD, 42)
    tw = tlen(img, sub, fs)
    x1 = W - M + 14
    y0 = y + 62
    chamfer_card(img, [x1 - tw - 78, y0, x1, y0 + 66], MAGENTA, 20, fill=(10, 12, 21, 226), bw=3)
    dot(img, x1 - tw - 34, y0 + 33, 9, MAGENTA + (255,))
    ptext(img, (x1 - 26, y0 + 33), sub, fs, MAGENTA + (255,), anchor="rm")
    top = y0 + 66

    # ردیف محتوا: کارت تصویر ۴:۵ در راست، چیپ‌های داده در چپ
    content_y = top + 34
    content_h = (H - 96) - content_y
    chh = int(min(content_h, 700))
    cw = int(chh * 4 / 5)
    cx1 = W - M + 14
    cx0 = cx1 - cw
    cyber_photo(img, os.path.join(cfg.get("src", ""), c["img"]), cx0, content_y, cw, chh, CYAN, 44)

    tags = c.get("tags", [])[:4]
    fx = fnt(BOLD, 30)
    chip_x1 = cx0 - 56
    chip_w = chip_x1 - (M - 14)
    chip_h, chip_gap = 76, 20
    total = len(tags) * chip_h + (len(tags) - 1) * chip_gap
    ty = content_y + (chh - total) / 2
    for k, t in enumerate(tags):
        col = ACCENTS[k % 4]
        chamfer_card(img, [M - 14, ty, chip_x1, ty + chip_h], col, 18,
                     fill=(10, 12, 21, 234), bw=3, glow=False)
        dot(img, chip_x1 - 28, ty + chip_h / 2, 8, col + (255,))
        ptext(img, (chip_x1 - 52, ty + chip_h / 2), t, fx, col + (255,), anchor="rm")
        ty += chip_h + chip_gap
    mono_tag(img, "SWIPE >>", (W - M + 14, H - 78), CYAN, 30, anchor="rm")
    img.convert("RGB").save(out_path, quality=95)
    return out_path


# ------------------------------------------------------------------ cta
def render_cta_cyber(cfg, out_path):
    c = cfg["cta"]
    img = make_bg_cyber([MAGENTA, CYAN, AMBER, MAGENTA], seed=9)
    hud_brackets(img, MAGENTA)
    hazard_strip(img, MAGENTA, H - 42, 14, 70)
    mono_tag(img, "// END_OF_MODULE", (M, 196), MAGENTA, 30, anchor="lm")
    mono_tag(img, cfg.get("nameplate_en", "DR. KIANOOSH SALARIAN"),
             (W - M + 14, 196), CYAN, 26, anchor="rm")

    big = "ذخیره کن!"
    f = fnt(BLACK, 128)
    y = 340
    glitch_title(img, (W - M + 14, y), big, f, AMBER + (255,), AMBER, glow=30)

    sub = c.get("text", "")
    fs = fnt(BOLD, 46)
    ty = y + 132
    for ln in wrap(img, sub, fs, MAXW):
        ptext(img, (W - M + 14, ty), ln, fs, (240, 243, 250, 245), anchor="ra")
        ty += int(46 * 1.5)

    # دکمه‌ها
    y0 = ty + 30
    btn = c.get("buttons", ["ذخیره", "اشتراک‌گذاری"])
    fx = fnt(BOLD, 40)
    x1 = W - M + 14
    for k, t in enumerate(btn):
        col = [CYAN, MAGENTA][k % 2]
        tw = tlen(img, t, fx)
        chamfer_card(img, [x1 - tw - 96, y0, x1, y0 + 76], col, 22,
                     fill=(10, 12, 21, 236), bw=3)
        paste_icon(img, ["safe", "sound"][k % 2], 34, col, (x1 - tw - 76, y0 + 21))
        ptext(img, (x1 - 30, y0 + 38), t, fx, col + (255,), anchor="rm")
        y0 += 88

    # کارت تصویر پایین
    cy0 = y0 + 26
    cw = int(MAXW * 0.86)
    chh = int(cw * 5 / 4)
    if cy0 + chh > H - 210:
        chh = H - 210 - cy0
        cw = int(chh * 4 / 5)
    cx0 = (W - cw) // 2
    if chh > 180:
        cyber_photo(img, os.path.join(cfg.get("src", ""), c["img"]), cx0, cy0, cw, chh, CYAN, 40)

    mono_tag(img, c.get("follow_en", "FOLLOW FOR MORE"), (M, H - 78), MAGENTA, 30, anchor="lm")
    img.convert("RGB").save(out_path, quality=95)
    return out_path


# ------------------------------------------------------------------ build
def build_carousel_cyber(cfg, outdir="."):
    os.makedirs(outdir, exist_ok=True)
    outs = []
    if cfg.get("cover"):
        p = os.path.join(outdir, "cover.png")
        render_cover_cyber(cfg, p)
        outs.append(p)
        print("OK", p)
    for i, s in enumerate(cfg["slides"]):
        p = os.path.join(outdir, f"slide_{i + 1}.png")
        render_slide_cyber(i, cfg, s, p)
        outs.append(p)
        print("OK", p)
    if cfg.get("cta"):
        p = os.path.join(outdir, "cta.png")
        render_cta_cyber(cfg, p)
        outs.append(p)
        print("OK", p)
    return outs

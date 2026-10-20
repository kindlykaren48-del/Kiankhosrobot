"""
carousel_engine.py — موتور کاروسل اینستاگرام (۴:۵ · ۱۰۸۰×۱۳۵۰)
=================================================================
پالت رنگی، تصویرسازی، تایپوگرافی فارسی با HarfBuzz (fatext).
هر کاروسل: پوشش + اسلایدهای محتوا + اسلاید ذخیره/دعوت.

خروجی: reels/carousel/<slug>/<slug>_01.png ... + <slug>_caption.txt
"""
from __future__ import annotations

import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "Kiankhosrobot", "toolkit"))
from fatext import draw_text, measure  # noqa: E402

W, H = 1080, 1350
M = 74                      # حاشیهٔ ایمن
ROOT = os.path.abspath(os.path.join(HERE, ".."))
FONT_DIR = next((d for d in (os.environ.get("REEL_FONTS", ""),
                             os.path.join(ROOT, "fonttmp", "fonts", "ttf"),
                             "/home/user/fonttmp/fonts/ttf")
                 if d and os.path.isfile(os.path.join(d, "Vazirmatn-Bold.ttf"))), "")
BLACK = os.path.join(FONT_DIR, "Vazirmatn-Black.ttf")
BOLD = os.path.join(FONT_DIR, "Vazirmatn-Bold.ttf")
MED = os.path.join(FONT_DIR, "Vazirmatn-Medium.ttf")
REG = os.path.join(FONT_DIR, "Vazirmatn-Regular.ttf")
OUT = os.path.join(ROOT, "reels", "carousel")
BRAND = "دکتر کیانوش سالاریان"

PALETTES = {
    "terracotta": dict(bg=(253, 246, 236), bg2=(246, 229, 215), ink=(31, 42, 61),
                       accent=(206, 84, 66), accent2=(226, 158, 66), deep=(38, 60, 80),
                       card=(255, 253, 249), line=(228, 210, 196)),
    "sage": dict(bg=(248, 248, 241), bg2=(230, 238, 229), ink=(24, 57, 51),
                 accent=(78, 127, 104), accent2=(201, 139, 94), deep=(31, 74, 66),
                 card=(255, 255, 252), line=(212, 226, 214)),
    "indigo": dict(bg=(245, 243, 236), bg2=(228, 226, 218), ink=(27, 36, 64),
                   accent=(201, 138, 60), accent2=(63, 92, 134), deep=(30, 42, 72),
                   card=(255, 254, 250), line=(220, 216, 206)),
    "blush": dict(bg=(252, 243, 242), bg2=(241, 226, 228), ink=(58, 35, 51),
                  accent=(181, 70, 106), accent2=(123, 94, 167), deep=(74, 40, 66),
                  card=(255, 251, 251), line=(232, 212, 216)),
}


# ------------------------------------------------------------------ ابزار
def font(p, s):
    return ImageFont.truetype(p, s)


def wrap(text, f, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if measure(trial, f)[2] <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_block(text, max_w, max_lines, start, minimum, path=BLACK, gap=1.5):
    size = start
    while size >= minimum:
        f = font(path, size)
        lines = wrap(text, f, max_w)
        if len(lines) <= max_lines:
            return f, lines
        size -= 3
    f = font(path, minimum)
    return f, wrap(text, f, max_w)


def draw_lines(img, lines, f, fill, x, y, anchor="ra", gap=1.5):
    lh = int(f.size * gap)
    for ln in lines:
        draw_text(img, (x, y), ln, font=f, fill=fill, anchor=anchor)
        y += lh
    return y


def soft_bg(pal, blobs=True):
    img = Image.new("RGB", (W, H), pal["bg"])
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / (H - 1)
        d.line([(0, y), (W, y)], fill=tuple(int(pal["bg"][k] + (pal["bg2"][k] - pal["bg"][k]) * t)
                                            for k in range(3)))
    img = img.convert("RGBA")
    if blobs:
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(lay)
        for (cx, cy, r, a) in ((-60, 240, 300, 34), (1080, 420, 360, 26),
                               (980, 1180, 320, 22), (60, 1260, 260, 20)):
            ld.ellipse([cx - r, cy - r, cx + r, cy + r],
                       fill=(255, 255, 255, a) if a > 24 else (*pal["accent2"], a))
        img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(60)))
    return img


def rounded_image(path, box, radius=40, zoom=1.0):
    x0, y0, x1, y1 = [int(v) for v in box]
    w, h = x1 - x0, y1 - y0
    src = Image.open(path).convert("RGB")
    rs, rt = src.width / src.height, w / h
    if rs > rt:
        nh = int(src.height / zoom)
        nw = int(nh * rt)
    else:
        nw = int(src.width / zoom)
        nh = int(nw / rt)
    nw, nh = min(nw, src.width), min(nh, src.height)
    cx, cy = src.width / 2, src.height * 0.56
    left = max(0, min(src.width - nw, int(cx - nw / 2)))
    top = max(0, min(src.height - nh, int(cy - nh / 2)))
    crop = src.crop((left, top, left + nw, top + nh)).resize((w, h), Image.LANCZOS)
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w, h], radius, fill=255)
    return crop, mask


def sharp_card(img, box, radius, pal, shadow=52):
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([box[0] + 4, box[1] + 16, box[2] + 4, box[3] + 22],
                                        radius, fill=(*pal["deep"], 46))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(shadow)))


def rrect(img, box, radius, fill, outline=None, width=2):
    """مستطیل گرد با شفافیت واقعی (روی لایهٔ جدا و alpha_composite)."""
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(lay).rounded_rectangle(list(box), radius, fill=fill,
                                          outline=outline, width=width if outline else 0)
    img.alpha_composite(lay)


def chip(img, text, xy, pal, f=None, fill=None, txt=None, anchor="mm", pad=34, hh=62):
    f = f or font(BOLD, 30)
    tw = measure(text, f)[2]
    w = tw + pad * 2
    x, y = xy
    x0 = x - w / 2 if anchor[0] == "m" else (x if anchor[0] == "l" else x - w)
    y0 = y - hh / 2 if anchor[1] == "m" else y
    rrect(img, [x0, y0, x0 + w, y0 + hh], hh / 2,
          fill=fill or (*pal["card"], 235), outline=(*pal["line"], 255), width=3)
    draw_text(img, (x, y0 + hh / 2 - 2), text, font=f, fill=txt or pal["accent"], anchor="mm")
    return w


def header(img, pal, idx, total, dark=False):
    ink = (255, 255, 255, 170) if dark else (*pal["ink"], 120)
    draw_text(img, (W - M, 62), BRAND, font=font(MED, 27), fill=ink, anchor="ra")
    label = f"{to_fa(idx)} / {to_fa(total)}"
    f = font(BOLD, 26)
    tw = measure(label, f)[2]
    fill = (255, 255, 255, 60) if dark else (*pal["card"], 220)
    rrect(img, [M, 38, M + tw + 44, 88], 25, fill=fill,
          outline=(255, 255, 255, 90) if dark else (*pal["line"], 255), width=2)
    draw_text(img, (M + 22 + tw / 2, 62), label, font=f,
              fill=(255, 255, 255, 220) if dark else (*pal["ink"], 150), anchor="mm")


def to_fa(n):
    return str(n).translate(str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹"))


def footer_rule(img, pal, y=1268, dark=False):
    d = ImageDraw.Draw(img, "RGBA")
    col = (255, 255, 255, 70) if dark else (*pal["line"], 255)
    d.line([(M, y), (W - M, y)], fill=col, width=2)
    txt = "ذخیره کن تا هر وقت لازم شد بخوانی" if not dark else "ذخیره کن  ·  اشتراک‌گذاری"
    draw_text(img, (W / 2, y + 44), txt, font=font(MED, 27),
              fill=(255, 255, 255, 190) if dark else (*pal["ink"], 125), anchor="mm")


# ------------------------------------------------------------------ اسلایدها
def slide_cover(cfg, pal, idx, total):
    img = soft_bg(pal)
    header(img, pal, idx, total)

    # چیپ دسته
    chip(img, cfg["eyebrow"], (W / 2, 168), pal, f=font(BOLD, 31))

    # عنوان
    f, lines = fit_block(cfg["title"], W - 2 * M, 3, 96, 60)
    y = 238
    y = draw_lines(img, lines, f, (*pal["ink"], 255), W / 2, y, anchor="ma", gap=1.44)
    y += int(f.size * 0.22)

    # خط تأکید کوتاه
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle([W / 2 - 52, y, W / 2 + 52, y + 8], 4, fill=(*pal["accent"], 255))
    y += 30

    # زیرعنوان
    fs = font(BOLD, 41)
    sub_lines = wrap(cfg["subtitle"], fs, W - 2 * M - 40)
    y = draw_lines(img, sub_lines, fs, (*pal["accent"], 255), W / 2, y, anchor="ma", gap=1.5)

    # کارت تصویر تا پایین
    top = max(int(y + 34), 640)
    box = (M - 8, top, W - M + 8, H - 64)
    sharp_card(img, box, 44, pal)
    crop, mask = rounded_image(cfg["image"], box, 44, 1.02)
    img.paste(crop, (box[0], box[1]), mask)
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle(list(box), 44, outline=(255, 255, 255, 210), width=5)
    return img


def slide_content(cfg, pal, sc, idx, total):
    img = soft_bg(pal)
    header(img, pal, idx, total)

    f, lines = fit_block(sc["title"], W - 2 * M, 2, 66, 46)
    y = 176
    y = draw_lines(img, lines, f, (*pal["ink"], 255), W - M, y, anchor="ra", gap=1.42)

    if sc.get("sub"):
        fs = font(MED, 36)
        sub_lines = wrap(sc["sub"], fs, W - 2 * M)
        y = draw_lines(img, sub_lines, fs, (*pal["ink"], 175), W - M, y + 12, anchor="ra", gap=1.55)
    y += 22

    bullets = sc.get("bullets", [])
    has_img = bool(sc.get("image"))
    fb = font(MED, 37)
    inner = (W - M) - M - 150

    # اندازه‌گیری بولت‌ها
    plan, need = [], 54
    for b in bullets:
        lead = b.get("lead", "") if isinstance(b, dict) else ""
        rest = b.get("t", "") if isinstance(b, dict) else b
        full = (lead + " " + rest).strip() if lead else rest
        bl = wrap(full, fb, inner)
        plan.append((lead, rest, bl))
        need += int(fb.size * 1.5) * len(bl) + 18
    need += 10

    card_top = int(y)
    avail_bottom = (H - 300) if has_img else (H - 200)
    card_bottom = min(avail_bottom, card_top + need)
    if card_bottom < card_top + 240:
        card_bottom = card_top + 240
    box = (M, card_top, W - M, int(card_bottom))
    sharp_card(img, box, 40, pal)
    rrect(img, box, 40, fill=(*pal["card"], 247), outline=(*pal["line"], 255), width=3)

    # توزیع فضای باقی‌مانده بین بولت‌ها
    used = sum(int(fb.size * 1.5) * len(bl) for _, _, bl in plan)
    extra = max(0, (box[3] - box[1] - 108 - used))
    gap_extra = extra / max(1, len(plan) - 1) if len(plan) > 1 else 0
    gap_extra = min(gap_extra, 34)

    fl = font(BOLD, 37)
    space = 14
    yy = box[1] + 52
    for lead, rest, bl in plan:
        d = ImageDraw.Draw(img, "RGBA")
        d.ellipse([box[2] - 62, yy + 11, box[2] - 40, yy + 33], fill=(*pal["accent"], 255))
        x_right = box[2] - 88
        first = bl[0]
        if lead and first.startswith(lead):
            draw_text(img, (x_right, yy), lead, font=fl, fill=(*pal["accent"], 255), anchor="ra")
            lw = measure(lead, fl)[2]
            remainder = first[len(lead):].strip()
            if remainder:
                draw_text(img, (x_right - lw - space, yy), remainder,
                          font=fb, fill=(*pal["ink"], 235), anchor="ra")
        else:
            draw_text(img, (x_right, yy), first, font=fb, fill=(*pal["ink"], 235), anchor="ra")
        yy += int(fb.size * 1.5)
        for ln in bl[1:]:
            draw_text(img, (x_right, yy), ln, font=fb, fill=(*pal["ink"], 235), anchor="ra")
            yy += int(fb.size * 1.5)
        yy += 18 + gap_extra

    # نوار تصویر پایین
    if has_img:
        top = int(box[3]) + 26
        bottom = H - 150
        if bottom - top < 170:
            bottom = top + 170
        ib = (M - 8, top, W - M + 8, bottom)
        sharp_card(img, ib, 34, pal, shadow=40)
        crop, mask = rounded_image(sc["image"], ib, 34, 1.02)
        img.paste(crop, (ib[0], ib[1]), mask)
        d = ImageDraw.Draw(img, "RGBA")
        d.rounded_rectangle(list(ib), 34, outline=(255, 255, 255, 210), width=4)

    footer_rule(img, pal, y=H - 118)
    return img


def slide_cta(cfg, pal, idx, total):
    img = Image.new("RGBA", (W, H), (*pal["deep"], 255))
    # بافت نرم
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    for (cx, cy, r, a) in ((-80, 260, 340, 46), (1120, 700, 380, 36), (150, 1260, 300, 28)):
        ld.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255, a))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(70)))
    header(img, pal, idx, total, dark=True)

    chip(img, cfg.get("cta_eyebrow", "قدم بعدی"), (W / 2, 190), pal,
         f=font(BOLD, 30), fill=(255, 255, 255, 42), txt=(255, 255, 255, 240))

    f, lines = fit_block(cfg.get("cta_title", "ذخیره کن،\nبعداً بخوان"), W - 2 * M, 3, 104, 64)
    y = 260
    y = draw_lines(img, lines, f, (255, 255, 255, 255), W / 2, y, anchor="ma", gap=1.4)

    fs = font(MED, 38)
    sub = wrap(cfg.get("cta_sub", ""), fs, W - 2 * M - 60)
    y = draw_lines(img, sub, fs, (255, 255, 255, 195), W / 2, y + 24, anchor="ma", gap=1.6)

    # سه اقدام
    acts = cfg.get("cta_actions", [])
    ay = max(int(y + 46), 800)
    for i, a in enumerate(acts):
        rrect(img, [M + 20, ay, W - M - 20, ay + 108], 30,
              fill=(255, 255, 255, 26), outline=(255, 255, 255, 70), width=2)
        d = ImageDraw.Draw(img, "RGBA")
        fnum = font(BLACK, 40)
        d.ellipse([W - M - 96, ay + 26, W - M - 40, ay + 82], fill=(*pal["accent2"], 255))
        draw_text(img, (W - M - 68, ay + 52), to_fa(i + 1), font=fnum,
                  fill=(*pal["deep"], 255), anchor="mm")
        draw_text(img, (W - M - 118, ay + 54), a, font=font(BOLD, 34),
                  fill=(255, 255, 255, 240), anchor="rm")
        ay += 126

    # پلاک پایانی
    draw_text(img, (W / 2, H - 128), BRAND, font=font(BOLD, 36), fill=(255, 255, 255, 235), anchor="mm")
    draw_text(img, (W / 2, H - 78), "پیجم را دنبال کن برای آموزش‌های بیشتر",
              font=font(MED, 28), fill=(255, 255, 255, 160), anchor="mm")
    return img


# ------------------------------------------------------------------ ساخت کاروسل
def build(cfg):
    pal = PALETTES[cfg["palette"]]
    slug = cfg["slug"]
    outdir = os.path.join(OUT, slug)
    os.makedirs(outdir, exist_ok=True)
    slides = [dict(kind="cover")] + cfg["slides"] + [dict(kind="cta")]
    total = len(slides)
    files = []
    for i, sc in enumerate(slides, start=1):
        kind = sc.get("kind", "content")
        if kind == "cover":
            img = slide_cover(cfg, pal, i, total)
        elif kind == "cta":
            img = slide_cta(cfg, pal, i, total)
        else:
            img = slide_content(cfg, pal, sc, i, total)
        p = os.path.join(outdir, f"{slug}_{i:02d}.png")
        img.convert("RGB").save(p, quality=94)
        files.append(p)
    cap = os.path.join(outdir, f"{slug}_caption.txt")
    with open(cap, "w", encoding="utf-8") as f:
        f.write(cfg["caption"])
    print(f"[✓] {slug}: {len(files)} اسلاید → {outdir}")
    return files, cap

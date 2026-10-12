"""
make_carousel.py — موتور ساخت کاروسل اینستاگرام (تصویر ثابت ۱۰۸۰×۱۳۵۰، نسبت ۴:۵)

قالب سوم کارخانه در کنار «نوع قدیم / انیمیشنی» و «نوع جدید / سخنگو»:
خروجی فقط تصویر است (بدون صدا و ویدیو):

    <slug>_carousel_01.png … <slug>_carousel_NN.png     اسلایدها (اولی کاور، آخری CTA)
    <slug>_carousel_preview.png                          تماس‌نگارهٔ همهٔ اسلایدها برای بازبینی
    <slug>_caption.txt                                   کپشن و هشتگ

استفاده:
    python3 make_carousel.py            # با topic.py کنار همین فایل
    python3 make_carousel.py <outdir>

فونت: فقط وزیرمتن. متن فارسی با fatext (HarfBuzz + FreeType) شکل‌دهی می‌شود؛
ارقام و عبارت‌های لاتین داخل متن دوجهته درست می‌نشینند.
"""
import os
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from icons import icon
from fatext import FD, render_mask, _offsets, _font_info

# ------------------------------------------------------------------ ابعاد
W, H = 1080, 1350          # ۴:۵ عمودی — بهترین ابعاد کاروسل اینستاگرام


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
EXTRA = FTDIR + "Vazirmatn-ExtraBold.ttf"
BOLD = FTDIR + "Vazirmatn-Bold.ttf"
SEMI = FTDIR + "Vazirmatn-SemiBold.ttf"
MED = FTDIR + "Vazirmatn-Medium.ttf"
REG = FTDIR + "Vazirmatn-Regular.ttf"

OUTDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ------------------------------------------------------------------ پالت‌ها
PALETTES = {
    # رزگلد: رزغباری + شامپاینی طلایی روی زمینهٔ قهوه‌ای-گیلاسی تیره
    "rosegold": {
        "bg_top": (56, 24, 32), "bg_bot": (17, 9, 14),
        "glow": (214, 138, 118), "glow2": (176, 92, 104),
        "gold1": (250, 216, 176), "gold2": (208, 122, 116),
        "accent": (236, 160, 150), "text": (253, 243, 239),
        "muted": (207, 165, 162), "chip": (102, 52, 60),
        "card": (74, 36, 44),
    },
    # یاقوتی-طلایی
    "winegold": {
        "bg_top": (58, 14, 36), "bg_bot": (16, 8, 14),
        "glow": (196, 118, 92), "glow2": (150, 60, 92),
        "gold1": (247, 214, 160), "gold2": (188, 96, 110),
        "accent": (230, 152, 138), "text": (253, 242, 238),
        "muted": (203, 158, 160), "chip": (98, 40, 58),
        "card": (70, 28, 44),
    },
    # سبز یشمی-طلایی
    "emerald": {
        "bg_top": (11, 44, 40), "bg_bot": (6, 18, 20),
        "glow": (120, 196, 150), "glow2": (64, 140, 128),
        "gold1": (246, 216, 160), "gold2": (176, 150, 78),
        "accent": (178, 220, 176), "text": (243, 252, 246),
        "muted": (160, 194, 178), "chip": (22, 78, 66),
        "card": (18, 60, 54),
    },
    # آبی نفتی-نقره‌ای
    "navysilver": {
        "bg_top": (14, 30, 56), "bg_bot": (7, 12, 24),
        "glow": (128, 168, 214), "glow2": (74, 108, 176),
        "gold1": (232, 240, 250), "gold2": (150, 176, 214),
        "accent": (186, 210, 240), "text": (243, 248, 255),
        "muted": (162, 182, 208), "chip": (30, 56, 92),
        "card": (24, 46, 76),
    },
}

# ------------------------------------------------------------------ ابزارها
def F(path, size):
    return ImageFont.truetype(path, int(size))


def _len(d, txt, font):
    return d.textlength(txt, font=font)


def wrap(text, font, maxw):
    """شکستن متن فارسی بر اساس عرض واقعی (HarfBuzz)، نه تعداد نویسه."""
    d = FD(Image.new("RGB", (8, 8)))
    out, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if not cur or _len(d, t, font) <= maxw:
            cur = t
        else:
            out.append(cur)
            cur = w
    if cur:
        out.append(cur)
    return out


def fit_font(text, path, maxw, start=90, stop=38):
    """کوچک‌کردن خودکار اندازه تا متن در عرض مجاز جا شود."""
    d = FD(Image.new("RGB", (8, 8)))
    for s in range(int(start), int(stop) - 1, -2):
        f = F(path, s)
        if _len(d, text, f) <= maxw:
            return f
    return F(path, stop)


def grad_text(img, xy, text, font, c1, c2, anchor="mm"):
    """متن با پرشدگی گرادیانی (طلایی→رزگلد)."""
    path, size = _font_info(font)
    mask, x0, y0, adv, asc, desc = render_mask(text, path, size)
    if mask.width <= 1:
        return
    x1, y1 = x0 + mask.width, y0 + mask.height
    ox, base, box = _offsets(anchor, xy, (x0, y0, x1, y1), adv, asc, desc)
    g = Image.new("RGB", mask.size, c2)
    gd = ImageDraw.Draw(g)
    hgt = max(1, mask.height)
    for y in range(hgt):
        f = y / hgt
        gd.line([(0, y), (mask.width, y)],
                fill=tuple(int(c1[k] + (c2[k] - c1[k]) * f) for k in range(3)))
    img.paste(g, (int(round(ox + x0)), int(round(base + y0))), mask)


def spaced_text(img, xy, text, font, fill, sp=6, anchor="ra"):
    """متن لاتین با فاصلهٔ حروف (ترنج‌کشی دستی)."""
    d = FD(img)
    widths = [_len(d, c, font) for c in text]
    total = sum(widths) + sp * max(0, len(text) - 1)
    x = xy[0] - total if anchor == "ra" else (xy[0] - total / 2 if anchor == "ma" else xy[0])
    y = xy[1]
    for c, w in zip(text, widths):
        d.text((x, y), c, font=font, fill=fill, anchor="la")
        x += w + sp


def round_mask(size, r):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], r, fill=255)
    return m


# ------------------------------------------------------------------ پس‌زمینه
def make_bg(pal, seed=0):
    rnd = random.Random(seed)
    top = np.array(pal["bg_top"], np.float32)
    bot = np.array(pal["bg_bot"], np.float32)
    t = np.linspace(0, 1, H, dtype=np.float32)[:, None]
    arr = top * (1 - t) + bot * t                       # (H,3)
    arr = np.repeat(arr[:, None, :], W, axis=1)         # (H,W,3)

    # هالهٔ نور بالا-مرکز
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    for (cx, cy, sg, col, amp) in [
            (0.50 * W, 0.18 * H, 0.34 * W, pal["glow"], 0.42),
            (0.12 * W, 0.92 * H, 0.40 * W, pal["glow2"], 0.26),
            (0.92 * W, 0.52 * H, 0.30 * W, pal["glow"], 0.16)]:
        g = np.exp(-(((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * sg ** 2)))[..., None]
        arr += g * np.array(col, np.float32) * amp

    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")

    # دایره‌های بوکهٔ رزگلد
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    for _ in range(22):
        r = rnd.randint(40, 190)
        cx, cy = rnd.randint(-60, W + 60), rnd.randint(-60, H + 60)
        a = rnd.randint(8, 26)
        col = pal["gold1"] if rnd.random() < 0.5 else pal["accent"]
        od.ellipse([cx - r, cy - r, cx + r, cy + r], fill=tuple(col) + (a,))
    img = Image.alpha_composite(img.convert("RGBA"), ov.filter(ImageFilter.GaussianBlur(46)))

    # تاریک‌شدن حاشیه‌ها
    vg = np.clip(1.0 - 0.55 * (((xx / W) - 0.5) ** 2 + ((yy / H) - 0.45) ** 2) * 3.0, 0, 1)
    dark = np.zeros((H, W, 3), np.float32) + np.array(pal["bg_bot"], np.float32) * 0.6
    arr = (np.asarray(img.convert("RGB"), np.float32) * vg[..., None]
           + dark * (1 - vg[..., None]))
    # دانهٔ ملایم
    arr += np.random.default_rng(seed).normal(0, 2.2, (H, W, 3)).astype(np.float32)
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")


# ------------------------------------------------------------------ کارت تصویر
def image_card(src_path, cw, ch, pal, radius=44, crop=(0.04, 0.96), seed=1):
    """کارت تصویر: پس‌زمینهٔ تار و هم‌رنگ + تصویر کامل در مرکز (بدون برش چهره)."""
    src = Image.open(src_path).convert("RGB")
    a, b = int(src.height * crop[0]), int(src.height * crop[1])
    src = src.crop((0, a, src.width, b))

    # پس‌زمینه: پوشش کامل + تار + هم‌رنگ با پالت
    sc = max(cw / src.width, ch / src.height)
    back = src.resize((max(cw, int(src.width * sc)), max(ch, int(src.height * sc))), Image.LANCZOS)
    l, t = (back.width - cw) // 2, (back.height - ch) // 2
    back = back.crop((l, t, l + cw, t + ch)).filter(ImageFilter.GaussianBlur(58))
    back = Image.blend(back, Image.new("RGB", (cw, ch), pal["card"]), 0.55)
    back = Image.blend(back, Image.new("RGB", (cw, ch), pal["bg_top"]), 0.25)

    # تصویر اصلی: کامل درون کارت
    pad = 34
    k = min((cw - 2 * pad) / src.width, (ch - 2 * pad) / src.height)
    fg = src.resize((max(1, int(src.width * k)), max(1, int(src.height * k))), Image.LANCZOS)
    fgm = round_mask(fg.size, 30)

    # سایهٔ نرم پشت تصویر
    sh = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sx0 = (cw - fg.width) // 2 - 12
    sy0 = (ch - fg.height) // 2 + 14
    sd.rounded_rectangle([sx0, sy0, sx0 + fg.width + 24, sy0 + fg.height + 24], 38,
                         fill=(0, 0, 0, 130))
    sh = sh.filter(ImageFilter.GaussianBlur(26))

    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    card.paste(back, (0, 0))
    card.alpha_composite(sh)
    card.paste(fg, ((cw - fg.width) // 2, (ch - fg.height) // 2), fgm)

    # قاب رزگلد
    outer = round_mask((cw, ch), radius)
    inner = round_mask((cw - 8, ch - 8), max(2, radius - 4))
    shifted = Image.new("L", (cw, ch), 0)
    shifted.paste(inner, (4, 4))
    ring = np.clip(np.asarray(outer, np.int16) - np.asarray(shifted, np.int16), 0, 255)
    ring = Image.fromarray(ring.astype(np.uint8), "L")
    border = Image.new("RGBA", (cw, ch), tuple(pal["gold1"]) + (0,))
    border.putalpha(Image.eval(ring, lambda v: int(v * 0.55)))
    card.alpha_composite(border)

    out = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    out.paste(card, (0, 0), outer)
    return out


def circle_image(src_path, d, pal, ring=10):
    """تصویر گرد با حلقهٔ رزگلد (برای اسلاید پایانی)."""
    src = Image.open(src_path).convert("RGB")
    sc = max(d / src.width, d / src.height)
    im = src.resize((max(d, int(src.width * sc)), max(d, int(src.height * sc))), Image.LANCZOS)
    l, t = (im.width - d) // 2, (im.height - d) // 2
    im = im.crop((l, t, l + d, t + d))
    m = Image.new("L", (d, d), 0)
    ImageDraw.Draw(m).ellipse([0, 0, d - 1, d - 1], fill=255)

    out = Image.new("RGBA", (d + ring * 2, d + ring * 2), (0, 0, 0, 0))
    od = ImageDraw.Draw(out)
    od.ellipse([0, 0, d + ring * 2 - 1, d + ring * 2 - 1], fill=tuple(pal["gold1"]) + (150,))
    out.paste(im, (ring, ring), m)
    return out


# ------------------------------------------------------------------ اجزای متنی
def pill(img, box, text, font, pal, fill_a=52, outline_a=110, txt_col=None,
         icon_kind=None, icon_size=34, radius=None):
    d = ImageDraw.Draw(img, "RGBA")
    x0, y0, x1, y1 = box
    radius = radius or (y1 - y0) // 2
    d.rounded_rectangle([x0, y0, x1, y1], radius,
                        fill=tuple(pal["chip"]) + (fill_a,),
                        outline=tuple(pal["gold1"]) + (outline_a,), width=2)
    fd = FD(img)
    tx = x1 - 26
    if icon_kind:
        ic = icon(icon_kind, icon_size, tuple(pal["gold1"]))
        iy = (y0 + y1) // 2 - icon_size // 2
        img.paste(ic, (int(x0 + 22), int(iy)), ic)
    fd.text((tx, (y0 + y1) // 2), text, font=font,
            fill=txt_col or tuple(pal["text"]) + (235,), anchor="rm")
    return img


def bullets_metrics(items, box, size, gap=20):
    x0, y0, x1, y1 = box
    maxw = (x1 - 92) - (x0 + 96)
    f = F(MED, size)
    rows = [wrap(t, f, maxw) for _, t in items]
    lh = int(size * 1.42)
    total = sum(len(r) * lh for r in rows) + gap * (len(rows) - 1)
    return rows, lh, total


def pick_bullet_size(all_items, box, max_size=40, min_size=28, gap=20):
    """یک اندازهٔ واحد برای همهٔ اسلایدها تا چیدمان سراسر کاروسل یک‌دست باشد."""
    for size in range(max_size, min_size - 1, -2):
        if all(bullets_metrics(it, box, size, gap)[2] <= (box[3] - box[1])
               for it in all_items):
            return size
    return min_size


def draw_bullets(img, items, box, pal, max_size=40, min_size=28, gap=20):
    """فهرست نکته‌ها با آیکون در ستون چپ و متن راست‌چین در ستون راست."""
    x0, y0, x1, y1 = box
    txt_right = x1 - 92
    txt_left = x0 + 96
    maxw = txt_right - txt_left
    size = globals().get("BULLET_SIZE") or max_size
    rows, lh, total = bullets_metrics(items, box, size, gap)
    if total > (y1 - y0):                       # عقب‌نشینی ایمن
        size = pick_bullet_size([items], box, size - 2, min_size, gap)
        rows, lh, total = bullets_metrics(items, box, size, gap)
    f = F(MED, size)
    d = ImageDraw.Draw(img, "RGBA")
    fd = FD(img)
    y = y0
    globals()["LAST_BULLET"] = (size, total, y1 - y0)
    for (kind, _t), lines in zip(items, rows):
        cy = y + (len(lines) * lh) / 2 - lh * 0.55
        chip = 62
        d.rounded_rectangle([x0, cy + 2, x0 + chip, cy + 2 + chip], 20,
                            fill=tuple(pal["chip"]) + (150,),
                            outline=tuple(pal["gold1"]) + (70,), width=2)
        ic = icon(kind, 38, tuple(pal["gold1"]))
        img.paste(ic, (int(x0 + (chip - 38) / 2), int(cy + 2 + (chip - 38) / 2)), ic)
        d = ImageDraw.Draw(img, "RGBA")
        for i, ln in enumerate(lines):
            fd.text((txt_right, y + i * lh), ln, font=F(MED, size),
                    fill=tuple(pal["text"]) + (245,), anchor="ra")
        y += len(lines) * lh + gap
    return img


def dots(img, cx, cy, n, cur, pal, r=9, sp=34):
    d = ImageDraw.Draw(img, "RGBA")
    for i in range(n):
        x = cx + (i - (n - 1) / 2) * sp
        on = (i == cur)
        d.ellipse([x - r, cy - r, x + r, cy + r],
                  fill=tuple(pal["gold1"]) + (240 if on else 70,))


# ------------------------------------------------------------------ اسلایدها
def slide_cover(cfg, pal, idx=0, total=8):
    img = make_bg(pal, seed=3).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")

    # ردیف بالا: پلاک نام (راست) و نشان کاروسل (چپ)
    pill(img, (W - 430, 62, W - 60, 118), cfg.get("badge", "دکتر کیانوش سالاریان"),
         F(SEMI, 28), pal, icon_kind=cfg.get("badge_icon", "stetho"))
    pill(img, (60, 62, 300, 118), f"{idx + 1} / {total}", F(BOLD, 28), pal)

    # عنوان (گرادیان طلایی→رزگلد) — یک اندازهٔ واحد برای همهٔ خط‌ها
    lines = cfg["title_lines"]
    f = F(BLACK, 44)
    for ln in lines:
        ff = fit_font(ln, BLACK, W - 150, start=92, stop=44)
        if ff.size < f.size:
            f = ff
    y = 168 + int(f.size * 0.55)
    for ln in lines:
        grad_text(img, (W / 2, y), ln, f, pal["gold1"], pal["gold2"], anchor="mm")
        y += int(f.size * 1.28)

    # زیرعنوان / قلاب
    hook = cfg["hook"]
    f = fit_font(hook, SEMI, W - 200, start=48, stop=30)
    fd = FD(img)
    for i, ln in enumerate(wrap(hook, f, W - 200)):
        fd.text((W / 2, y + 18 + i * int(f.size * 1.5)), ln, font=f,
                fill=tuple(pal["text"]) + (235,), anchor="mm")
    y += 30 + len(wrap(hook, f, W - 200)) * int(f.size * 1.5)

    # خط انگلیسی
    spaced_text(img, (W / 2, y + 14), cfg.get("title_en", "").upper(),
                F(BOLD, 24), tuple(pal["muted"]) + (210,), sp=7, anchor="ma")

    # کارت تصویر
    cy0 = y + 66
    chh = min(1250 - cy0, 790)
    card = image_card(cfg["cover_ill"], W - 200, chh, pal, radius=46,
                      crop=cfg.get("cover_crop", (0.07, 0.93)))
    img.alpha_composite(card, (100, cy0))

    # چیپ‌های کلیدی روی پایین کارت
    tags = cfg.get("cover_tags", [])
    if tags:
        scrim = Image.new("RGBA", (W - 200, 220), (0, 0, 0, 0))
        sd = ImageDraw.Draw(scrim)
        for i in range(220):
            sd.line([(0, i), (W - 200, i)], fill=tuple(pal["bg_bot"]) + (int(i * 0.75),))
        img.alpha_composite(scrim, (100, cy0 + chh - 220))
        d = ImageDraw.Draw(img, "RGBA")
        widths = []
        fd = FD(img)
        for t in tags:
            widths.append(int(_len(fd, t, F(BOLD, 30))) + 56)
        gapc = 18
        total_w = sum(widths) + gapc * (len(tags) - 1)
        x = (W - total_w) / 2
        for t, w in zip(tags, widths):
            pill(img, (x, cy0 + chh - 128, x + w, cy0 + chh - 62), t, F(BOLD, 30), pal,
                 fill_a=110, outline_a=130, radius=22)
            x += w + gapc

    # پانویس
    fd = FD(img)
    fd.text((W - 60, 1274), cfg.get("cover_footer", cfg.get("footer", "")),
            font=F(MED, 26), fill=tuple(pal["muted"]) + (200,), anchor="ra")
    return img


def slide_content(cfg, pal, i, total):
    num, fa, en, ill, items = cfg["slides"][i]
    img = make_bg(pal, seed=10 + i).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")

    # هدر: نشان عدد (چپ) + عنوان فارسی و انگلیسی (راست)
    d.ellipse([70, 88, 232, 250], fill=tuple(pal["text"]) + (242,))
    grad_text(img, (151, 169), num, F(BLACK, 92), pal["gold2"], pal["gold1"], anchor="mm")
    d = ImageDraw.Draw(img, "RGBA")

    f = fit_font(fa, BLACK, 700, start=66, stop=38)
    grad_text(img, (W - 62, 128), fa, f, pal["gold1"], pal["gold2"], anchor="ra")
    spaced_text(img, (W - 62, 196), en.upper(), F(BOLD, 26),
                tuple(pal["muted"]) + (215,), sp=6, anchor="ra")

    # کارت تصویر
    cy0, chh = 268, 600
    card = image_card(ill, W - 200, chh, pal, radius=44,
                      crop=cfg.get("slide_crop", (0.12, 0.88)))
    img.alpha_composite(card, (100, cy0))

    # نکته‌ها
    draw_bullets(img, items, (100, cy0 + chh + 28, W - 100, 1236), pal)

    # پانویس
    fd = FD(img)
    fd.text((W - 60, 1278), cfg.get("footer", ""), font=F(MED, 25),
            fill=tuple(pal["muted"]) + (195,), anchor="ra")
    fd.text((62, 1278), f"{i + 2} / {total}", font=F(BOLD, 26),
            fill=tuple(pal["muted"]) + (210,), anchor="la")
    return img


def slide_cta(cfg, pal, total):
    img = make_bg(pal, seed=99).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")

    # تصویر گرد
    d0 = 430
    ci = circle_image(cfg["cta_ill"], d0, pal, ring=12)
    img.alpha_composite(ci, ((W - ci.width) // 2, 96))

    # عنوان
    grad_text(img, (W / 2, 660), cfg.get("cta_title", "ذخیره کن!"),
              F(BLACK, 104), pal["gold1"], pal["gold2"], anchor="mm")

    fd = FD(img)
    f = F(SEMI, 42)
    for i, ln in enumerate(wrap(cfg.get("cta", ""), f, W - 220)):
        fd.text((W / 2, 760 + i * 62), ln, font=f,
                fill=tuple(pal["text"]) + (240,), anchor="mm")
    y = 760 + len(wrap(cfg.get("cta", ""), f, W - 220)) * 62 + 20

    # سه چیپ action
    items = cfg.get("cta_chips", [])
    if items:
        cw, gapc = 300, 20
        total_w = cw * len(items) + gapc * (len(items) - 1)
        x = (W - total_w) / 2
        for kind, txt in items:
            pill(img, (x, y + 10, x + cw, y + 106), txt, F(BOLD, 34), pal,
                 fill_a=95, outline_a=140, icon_kind=kind, icon_size=40, radius=30)
            x += cw + gapc
        y += 130

    # جملهٔ پایانی الزامی
    fd.text((W / 2, y + 60), "پیجم را دنبال کن برای آموزش‌های بیشتر",
            font=F(SEMI, 44), fill=tuple(pal["gold1"]) + (245,), anchor="mm")

    # پلاک نام
    pill(img, ((W - 470) / 2, y + 120, (W + 470) / 2, y + 186),
         cfg.get("badge", "دکتر کیانوش سالاریان"), F(SEMI, 34), pal,
         icon_kind=cfg.get("badge_icon", "stetho"), icon_size=40)

    # سلب مسئولیت
    fd.text((W / 2, 1284), cfg.get("disclaimer", ""), font=F(MED, 24),
            fill=tuple(pal["muted"]) + (180,), anchor="mm")
    return img


def preview_grid(paths, out, cols=4, pad=26, scale=0.30):
    """تماس‌نگارهٔ همهٔ اسلایدها برای بازبینی سریع."""
    ims = [Image.open(p).convert("RGB") for p in paths]
    tw = int(W * scale)
    th = int(H * scale)
    rows = (len(ims) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw + pad * (cols + 1), rows * (th + 30) + pad * (rows + 1)),
                      (26, 12, 18))
    d = ImageDraw.Draw(sheet)
    f = F(BOLD, 22)
    fd = FD(sheet)
    for i, im in enumerate(ims):
        r, c = divmod(i, cols)
        x = pad + c * (tw + pad)
        y = pad + r * (th + 30 + pad)
        sheet.paste(im.resize((tw, th), Image.LANCZOS), (x, y))
        fd.text((x + tw - 6, y + th + 6), f"{i + 1:02d}", font=f,
                fill=(240, 200, 190), anchor="ra")
    sheet.save(out)
    return out


# ------------------------------------------------------------------ ساخت
def build(cfg, outdir=None, with_preview=True):
    outdir = outdir or OUTDIR
    os.makedirs(outdir, exist_ok=True)
    pal = PALETTES.get(cfg.get("palette", "rosegold"), PALETTES["rosegold"])
    slug = cfg["slug"]
    total = len(cfg["slides"]) + 2

    box = (100, 268 + 600 + 28, W - 100, 1236)
    globals()["BULLET_SIZE"] = pick_bullet_size([s[4] for s in cfg["slides"]], box)
    print("اندازهٔ یک‌دست نکته‌ها:", BULLET_SIZE, "px")

    imgs = [slide_cover(cfg, pal, 0, total)]
    for i in range(len(cfg["slides"])):
        imgs.append(slide_content(cfg, pal, i, total))
    imgs.append(slide_cta(cfg, pal, total))

    paths = []
    for i, im in enumerate(imgs, 1):
        p = os.path.join(outdir, f"{slug}_carousel_{i:02d}.png")
        im.convert("RGB").save(p)
        paths.append(p)
        print("OK", os.path.basename(p), im.size,
              round(os.path.getsize(p) / 1024), "KB")

    if with_preview:
        pv = os.path.join(outdir, f"{slug}_carousel_preview.png")
        preview_grid(paths, pv)
        print("OK", os.path.basename(pv))
        paths.append(pv)
    return paths


if __name__ == "__main__":
    import sys
    import topic_newbornsmell as t
    out = sys.argv[1] if len(sys.argv) > 1 else None
    build(t.cfg, out)

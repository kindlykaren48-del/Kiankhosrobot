"""
make_carousel.py — موتور کاروسل ۷ اسلایدی موشن‌گرافیک (عمودی ۱۰۸۰×۱۹۲۰)

خروجی:
    <slug>_reel.mp4        ویدیوی موشن کاروسل (بدون موسیقی، بدون نریشن در حالت بی‌صدا)
    <slug>_cover.png       کاور (کارت تصویر دارد، متن روی کارت نیست)
    <slug>_caption.txt     کپشن و هشتگ
    <slug>_slides/         تک‌تک اسلایدها به‌صورت PNG برای انتشار کاروسل

قواعد رعایت‌شده:
- متن فارسی فقط با وزیرمتن و fatext (HarfBuzz + FreeType)؛ بدون arabic_reshaper/python-bidi
- قانون طلایی: متن و تصویر هرگز روی هم نمی‌افتند (سه ناحیهٔ جدا)
- کارت تصویر ۴:۵، بدون متن روی آن
- بدون شعار تبلیغاتی روی کارت و بدون موسیقی
"""
from __future__ import annotations

import os
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

from fatext import render_mask, measure
from icons import icon
import imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 1080, 1920, 30
OUTDIR = "/home/user/Kiankhosrobot"


# --------------------------------------------------------------- فونت
def _find_font_dir():
    cands = [os.environ.get("REEL_FONTS", ""),
             "/home/user/fonttmp/fonts/ttf/",
             os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
                 os.path.abspath(__file__)))), "fonttmp", "fonts", "ttf"),
             "/home/user/Kiankhosrobot/fonttmp/fonts/ttf/"]
    for c in cands:
        if c and os.path.isfile(os.path.join(c, "Vazirmatn-Bold.ttf")):
            return c if c.endswith("/") else c + "/"
    return "/home/user/fonttmp/fonts/ttf/"


FT = _find_font_dir()
BLACK, BOLD, SEMI, MED = (FT + "Vazirmatn-Black.ttf", FT + "Vazirmatn-Bold.ttf",
                          FT + "Vazirmatn-SemiBold.ttf", FT + "Vazirmatn-Medium.ttf")

AUTO_TRIM = True

CREAM = (251, 243, 229)
CREAM2 = (245, 233, 214)
INK = (34, 44, 52)
TEAL = (26, 111, 99)
CORAL = (223, 92, 74)
MUSTARD = (226, 158, 58)
ACCENTS = [TEAL, CORAL, MUSTARD]


# ------------------------------------------------------------- کمکی‌ها
def ease_out(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def ease_io(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def seg(t, a, b):
    """پیشرفت خطی بین a و b ثانیه."""
    if b <= a:
        return 1.0
    return max(0.0, min(1.0, (t - a) / (b - a)))


def cover_fill(im, w, h):
    im = im.convert("RGB")
    r = max(w / im.width, h / im.height)
    im = im.resize((max(w, int(im.width * r)), max(h, int(im.height * r))), Image.LANCZOS)
    l, t = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((l, t, l + w, t + h))


def fit_contain(im, w, h, bg=(251, 243, 229)):
    """تصویر را کامل داخل کادر می‌گذارد (بدون برش) و حاشیه را با رنگ کارت پر می‌کند."""
    im = im.convert("RGB")
    r = min(w / im.width, h / im.height)
    nw, nh = max(1, int(im.width * r)), max(1, int(im.height * r))
    canvas = Image.new("RGB", (w, h), bg)
    canvas.paste(im.resize((nw, nh), Image.LANCZOS), ((w - nw) // 2, (h - nh) // 2))
    return canvas


def auto_trim(im, pad=0.03):
    """حاشیهٔ یکنواخت روشن اطراف تصویرسازی را می‌برد تا کارت خالی به نظر نرسد."""
    im = im.convert("RGB")
    a = np.asarray(im).astype(np.int16)
    bg = a[2, 2].astype(np.int16)
    diff = np.abs(a - bg).sum(axis=2)
    mask = diff > 10
    ys, xs = np.where(mask)
    if len(xs) < 50:
        return im
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    pw, ph = int(im.width * pad), int(im.height * pad)
    x0, y0 = max(0, x0 - pw), max(0, y0 - ph)
    x1, y1 = min(im.width - 1, x1 + pw), min(im.height - 1, y1 + ph)
    # حفظ نسبت تقریبی ۴:۵ برای پرکردن کارت
    return im.crop((int(x0), int(y0), int(x1) + 1, int(y1) + 1))


def rounded(im, r):
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, im.width - 1, im.height - 1], r, fill=255)
    out = im.convert("RGBA")
    out.putalpha(m)
    return out


def text_layer(txt, size, color, font=BLACK, maxw=None):
    """لایهٔ RGBA از متن فارسی با ماسک دقیق fatext؛ در صورت نیاز اندازه کوچک می‌شود."""
    s = size
    while True:
        mask, x0, y0, adv, asc, desc = render_mask(txt, font, s)
        if maxw is None or adv <= maxw or s <= 22:
            break
        s -= 2
    lay = Image.new("RGBA", mask.size, tuple(color) + (0,))
    lay.putalpha(mask)
    return lay, adv


def grad_text_layer(txt, size, c1, c2, font=BLACK, maxw=None):
    mask, x0, y0, adv, asc, desc = render_mask(txt, font, size)
    w, h = mask.size
    g = Image.new("RGB", (w, h))
    gd = ImageDraw.Draw(g)
    for y in range(h):
        f = y / max(1, h - 1)
        gd.line([(0, y), (w, y)], fill=tuple(int(c1[k] + (c2[k] - c1[k]) * f) for k in range(3)))
    lay = g.convert("RGBA")
    lay.putalpha(mask)
    return lay


def fade(lay, a):
    if a >= 0.999:
        return lay
    out = lay.copy()
    out.putalpha(lay.getchannel("A").point(lambda v: int(v * max(0.0, a))))
    return out


def put(base, lay, x, y):
    """جای‌گذاری امن (لبه‌ها بریده می‌شوند، خطا نمی‌دهد)."""
    x, y = int(round(x)), int(round(y))
    if x >= base.width or y >= base.height:
        return
    if x + lay.width <= 0 or y + lay.height <= 0:
        return
    if x < 0 or y < 0 or x + lay.width > base.width or y + lay.height > base.height:
        box = (max(0, x), max(0, y), min(base.width, x + lay.width), min(base.height, y + lay.height))
        lay = lay.crop((box[0] - x, box[1] - y, box[2] - x, box[3] - y))
        x, y = box[0], box[1]
    base.alpha_composite(lay, (x, y))


# ------------------------------------------------------------ پس‌زمینه
_bg_cache: dict = {}


def background(tint):
    key = tint
    if key in _bg_cache:
        return _bg_cache[key].copy()
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        f = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(CREAM[k] + (CREAM2[k] - CREAM[k]) * f) for k in range(3)))
    # لکه‌های نرم رنگی
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    for (cx, cy, r, col, a) in [(150, 260, 300, tint, 40), (980, 1620, 340, MUSTARD, 36),
                                (930, 210, 190, CORAL, 26), (120, 1720, 250, TEAL, 26)]:
        od.ellipse([cx - r, cy - r, cx + r, cy + r], fill=tuple(col) + (a,))
    ov = ov.filter(ImageFilter.GaussianBlur(70))
    img = Image.alpha_composite(img.convert("RGBA"), ov)
    _bg_cache[key] = img.copy()
    return img


# -------------------------------------------------------------- کارت
def card_layer(path, cw=840, ch=1050, r=48, trim=None, mode="cover"):
    """کارت تصویر ۴:۵ با گوشهٔ گرد و حلقهٔ سفید؛ بزرگ‌تر رندر می‌شود تا زوم نرم ممکن باشد."""
    src = Image.open(path)
    if mode == "contain":
        if AUTO_TRIM if trim is None else trim:
            src = auto_trim(src)
        big = fit_contain(src, int(cw * 1.06), int(ch * 1.06))
    else:
        if AUTO_TRIM if trim is None else trim:
            src = auto_trim(src)
        big = cover_fill(src, int(cw * 1.06), int(ch * 1.06))
    big = rounded(big, int(r * 1.06))
    ring = Image.new("RGBA", big.size, (0, 0, 0, 0))
    ImageDraw.Draw(ring).rounded_rectangle([3, 3, big.width - 4, big.height - 4],
                                           int(r * 1.06), outline=(255, 255, 255, 235), width=7)
    big.alpha_composite(ring)
    return big


def zoom(lay, z, size):
    """زوم مرکزی و تغییر اندازه به ابعاد نهایی."""
    w, h = lay.size
    cw, ch = int(w / z), int(h / z)
    x0, y0 = (w - cw) // 2, (h - ch) // 2
    return lay.crop((x0, y0, x0 + cw, y0 + ch)).resize(size, Image.LANCZOS)


def card_shadow(bg, xy, cw, ch, r=52):
    sh = Image.new("RGBA", (cw + 120, ch + 120), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([60, 66, 60 + cw, 66 + ch], r, fill=(70, 50, 30, 46))
    sh = sh.filter(ImageFilter.GaussianBlur(26))
    put(bg, sh, xy[0] - 60, xy[1] - 60)


# ------------------------------------------------------ اجزای ثابت اسلاید
def brand_plaque(alpha=255):
    lay, adv = text_layer("دکتر کیانوش سالاریان", 34, INK, MED)
    return fade(lay, alpha / 255.0), adv


def footer(bg, idx, total, accent, brand=True):
    if brand:
        lay, adv = text_layer("دکتر کیانوش سالاریان", 33, INK, MED)
        put(bg, fade(lay, 0.62), W - 84 - adv, 1846)



def persian_num(n):
    return str(n).translate(str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹"))


def dots_layer(active, total, accent):
    """نقطه‌های پیشرفت؛ نقطهٔ فعال به شکل کپسول کشیده می‌شود."""
    gap, r = 40, 9
    w = total * gap + 40
    lay = Image.new("RGBA", (w, 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    x = 20
    for i in range(total):
        if i == active:
            d.rounded_rectangle([x - 20, 14, x + 20, 26], 6, fill=tuple(accent) + (255,))
            x += gap + 20
        else:
            d.ellipse([x - r, 11, x + r, 29], fill=tuple(INK) + (58,))
            x += gap
    lay = lay.resize((int(lay.width * 1.0), lay.height), Image.LANCZOS)
    return lay


# ---------------------------------------------------------- رندر اسلایدها
class Slide:
    """یک اسلاید با لایه‌های پیش‌رندر و انیمیشن ورودی مستقل."""

    def __init__(self, kind, cfg, pal, idx, total):
        self.kind = kind
        self.idx = idx
        self.total = total
        self.accent = pal
        self.bg_clear = background(pal)  # فقط پس‌زمینه + کارت تصویر
        self.anim = []  # (layer, x, y, t0, t1, dx, dy, pop)
        self.bg_items = []  # لایه‌های ثابت روی پس‌زمینه (با همان انیمیشن)
        self.card = None
        self.card_xy = None
        self.card_size = None

    # --- افزودن عنصر متحرک: از جهت راست/پایین با فید
    def add(self, lay, x, y, t0, t1, dx=0, dy=0, pop=None):
        self.anim.append((lay, x, y, t0, t1, dx, dy, pop))

    def draw(self, t):
        base = self.bg_clear.copy()
        if self.card is not None:
            z = 1.0 + 0.024 * seg(t, 0.35, 6.0)
            rise = 48 * (1 - ease_out(seg(t, 0.30, 0.95)))
            sc = 0.965 + 0.035 * ease_out(seg(t, 0.30, 0.95))
            cw, ch = self.card_size
            im = zoom(self.card, z * sc, (cw, ch))
            put(base, im, self.card_xy[0], self.card_xy[1] + rise)
        for (lay, x, y, t0, t1, dx, dy, pop) in self.anim:
            p = ease_io(seg(t, t0, t1))
            if p <= 0:
                continue
            ox = x + dx * (1 - p)
            oy = y + dy * (1 - p)
            im = lay if p >= 1 else fade(lay, p)
            if pop:
                pz = pop[0] + (pop[1] - pop[0]) * ease_out(seg(t, t0, t1))
                if abs(pz - 1.0) > 0.004:
                    nw, nh = max(1, int(im.width * pz)), max(1, int(im.height * pz))
                    im = im.resize((nw, nh), Image.LANCZOS)
                    ox -= (nw - lay.width) / 2
                    oy -= (nh - lay.height) / 2
            put(base, im, ox, oy)
        return base


def build_cover(s: Slide, cfg):
    total = s.total
    # eyebrow
    ey, adv = text_layer(cfg.get("eyebrow", "تغذیهٔ کودک"), 40, s.accent, SEMI)
    s.add(ey, W - 84 - adv, 132, 0.10, 0.55, dy=-14)

    # عنوان (چند خط)
    y = 196
    for i, line in enumerate(cfg["title_lines"]):
        size = 122 if len(line) <= 13 else (104 if len(line) <= 16 else 88)
        tl, adv = text_layer(line, size, INK, BLACK, maxw=W - 168)
        s.add(tl, W - 84 - adv, y, 0.22 + i * 0.12, 0.62 + i * 0.12, dx=34)
        y += int(tl.height + 22)

    # خط تأکید
    bar = Image.new("RGBA", (260, 12), (0, 0, 0, 0))
    ImageDraw.Draw(bar).rounded_rectangle([0, 0, 260, 12], 6, fill=tuple(s.accent) + (255,))
    s.add(bar, W - 84 - 260, y + 6, 0.62, 1.05, dx=70)

    # زیرعنوان / هوک
    sub, adv = text_layer(cfg["subtitle"], 46, INK, MED, maxw=W - 190)
    s.add(sub, W - 84 - max(adv, 1), y + 60, 0.70, 1.10, dy=12)

    # کارت تصویر
    cw, ch = 880, 780
    cx, cy = (W - cw) // 2, 700
    card_shadow(s.bg_clear, (cx, cy), cw, ch)
    s.card = card_layer(cfg["ill_cover"], cw, ch, mode=cfg.get("cover_mode", "cover"))
    s.card_xy, s.card_size = (cx, cy), (cw, ch)

    # تگ‌ها (کف کارت، خارج از خود تصویر)
    tags = cfg.get("tags", [])[:3]
    tw = [text_layer(tg, 32, INK, SEMI)[1] for tg in tags]
    pad, gap = 30, 18
    widths = [t + pad * 2 for t in tw]
    total_w = sum(widths) + gap * (len(tags) - 1)
    x = (W - total_w) / 2
    for i, tg in enumerate(tags):
        chip_h = 74
        lay = Image.new("RGBA", (int(widths[i]), chip_h), (0, 0, 0, 0))
        ImageDraw.Draw(lay).rounded_rectangle([0, 0, widths[i] - 1, chip_h - 1], chip_h // 2,
                                              fill=(255, 255, 255, 190),
                                              outline=tuple(s.accent) + (120,), width=2)
        tx, _ = text_layer(tg, 32, INK, SEMI)
        put(lay, tx, widths[i] / 2 - tx.width / 2, (chip_h - tx.height) / 2 - 2)
        s.add(lay, x, 1508, 1.00 + i * 0.10, 1.32 + i * 0.10, dy=16)
        x += widths[i] + gap

    # پلاک نام + بج انگلیسی (پایین‌ترین ناحیه، بیرون از کارت)
    nm, adv = text_layer("دکتر کیانوش سالاریان", 42, INK, BOLD)
    s.add(nm, W / 2 - adv / 2, 1612, 1.20, 1.55, dy=12)
    en, adv = text_layer(cfg.get("brand_en", "DR. KIANOOSH SALARIAN"), 27, INK, MED)
    s.add(en, W / 2 - adv / 2, 1672, 1.28, 1.62, dy=12)

    dots = dots_layer(0, total, s.accent)
    s.add(dots, W / 2 - dots.width / 2, 140, 0.40, 0.75)


def build_content(s: Slide, cfg, item):
    # نشان شماره
    badge_d = 132
    badge = Image.new("RGBA", (badge_d, badge_d), (0, 0, 0, 0))
    bd = ImageDraw.Draw(badge)
    bd.ellipse([0, 0, badge_d - 1, badge_d - 1], fill=tuple(s.accent) + (255,))
    nb, adv = text_layer(persian_num(item["num"]), 66, (255, 255, 255), BLACK)
    put(badge, nb, badge_d / 2 - nb.width / 2, badge_d / 2 - nb.height / 2 - 4)
    s.add(badge, 72, 104, 0.08, 0.42, pop=(0.62, 1.0))

    # عنوان فارسی (ناحیهٔ بالا)
    tl, adv = text_layer(item["title_fa"], 72, INK, BLACK, maxw=W - 96 - 230)
    s.add(tl, W - 84 - adv, 118, 0.18, 0.58, dx=36)

    # عنوان انگلیسی
    en, adv2 = text_layer(item["title_en"].upper(), 30, s.accent, SEMI)
    s.add(en, W - 84 - adv2, 118 + tl.height + 16, 0.28, 0.66, dx=24)

    # نقطه‌های پیشرفت
    dots = dots_layer(s.idx, s.total, s.accent)
    s.add(dots, W / 2 - dots.width / 2, 356, 0.34, 0.70)

    # کارت تصویر ۴:۵
    cw, ch = 872, 1010
    cx, cy = (W - cw) // 2, 414
    card_shadow(s.bg_clear, (cx, cy), cw, ch)
    s.card = card_layer(item["ill"], cw, ch, mode=cfg.get("card_mode", "cover"))
    s.card_xy, s.card_size = (cx, cy), (cw, ch)

    # جعبهٔ نکته‌ها (کاملاً زیر کارت، بدون همپوشانی)
    items = item["bullets"][:4]
    lh = 80
    bx0, bx1 = 72, W - 72
    by0 = cy + ch + 36
    by1 = by0 + 26 + lh * len(items)
    box = Image.new("RGBA", (bx1 - bx0, by1 - by0), (0, 0, 0, 0))
    ImageDraw.Draw(box).rounded_rectangle([0, 0, box.width - 1, box.height - 1], 34,
                                          fill=(255, 255, 255, 214),
                                          outline=tuple(s.accent) + (95,), width=3)
    for i, (ic, txt) in enumerate(items):
        yy = 15 + i * lh + lh / 2
        ring = 58
        rd = ImageDraw.Draw(box)
        rd.ellipse([26, yy - ring / 2, 26 + ring, yy + ring / 2], fill=tuple(s.accent) + (36,))
        ii = icon(ic, 34, tuple(s.accent))
        put(box, ii.convert("RGBA"), 26 + ring / 2 - 17, yy - 17)
        tx, adv = text_layer(txt, 34, INK, SEMI, maxw=box.width - 130)
        put(box, tx, box.width - 34 - adv, yy - tx.height / 2 - 2)
    s.add(box, bx0, by0 + 12, 0.46, 0.86, dy=34)


def build_cta(s: Slide, cfg):
    # حلقه‌های تزئینی پشت متن
    for i, (r, col, a) in enumerate([(250, s.accent, 26), (370, MUSTARD, 18)]):
        ring = Image.new("RGBA", (r * 2, r * 2), (0, 0, 0, 0))
        ImageDraw.Draw(ring).ellipse([0, 0, r * 2 - 1, r * 2 - 1],
                                     outline=tuple(col) + (a,), width=9)
        s.add(ring, W / 2 - r, 430 - r + i * 40, 0.10 + i * 0.12, 0.90 + i * 0.12, pop=(0.85, 1.0))

    dots = dots_layer(s.total - 1, s.total, s.accent)
    s.add(dots, W / 2 - dots.width / 2, 132, 0.12, 0.46)

    big = grad_text_layer(cfg.get("cta_big", "ذخیره کن"), 148, (226, 158, 58), (223, 92, 74))
    s.add(big, W / 2 - big.width / 2, 280, 0.20, 0.66, pop=(0.78, 1.0))

    txt, adv = text_layer(cfg.get("cta", "این کاروسل را برای والدین دیگر بفرست"), 46, INK, SEMI, maxw=W - 200)
    s.add(txt, W / 2 - adv / 2, 490, 0.42, 0.86, dy=22)

    # سه آیکون کوچک
    icon_row = Image.new("RGBA", (420, 120), (0, 0, 0, 0))
    for i, k in enumerate(["plus", "star", "shield"]):
        cx = 70 + i * 140
        ImageDraw.Draw(icon_row).ellipse([cx - 56, 4, cx + 56, 116],
                                         fill=(255, 255, 255, 205),
                                         outline=tuple(s.accent) + (90,), width=3)
        ii = icon(k, 52, tuple(ACCENTS[i]))
        put(icon_row, ii.convert("RGBA"), cx - 26, 34)
    s.add(icon_row, W / 2 - 210, 600, 0.60, 1.00, dy=26)

    # کارت تصویر پایین (متن روی آن نمی‌افتد)
    cw, ch = 880, 620
    cx, cy = (W - cw) // 2, 780
    card_shadow(s.bg_clear, (cx, cy), cw, ch)
    s.card = card_layer(cfg.get("ill_cta", cfg["ill_cover"]), cw, ch)
    s.card_xy, s.card_size = (cx, cy), (cw, ch)

    line, adv = text_layer("پیجم را دنبال کن برای آموزش‌های بیشتر", 42, INK, MED, maxw=W - 190)
    s.add(line, W / 2 - adv / 2, 1456, 0.72, 1.10, dy=18)

    div = Image.new("RGBA", (180, 8), (0, 0, 0, 0))
    ImageDraw.Draw(div).rounded_rectangle([0, 1, 180, 7], 3, fill=tuple(s.accent) + (200,))
    s.add(div, W / 2 - 90, 1540, 0.80, 1.10)

    nm, adv = text_layer("دکتر کیانوش سالاریان", 46, INK, BOLD)
    s.add(nm, W / 2 - adv / 2, 1578, 0.86, 1.20, dy=14)
    en, adv = text_layer(cfg.get("brand_en", "DR. KIANOOSH SALARIAN"), 28, INK, MED)
    s.add(en, W / 2 - adv / 2, 1646, 0.92, 1.26, dy=14)


# ---------------- نوار پیشرفت سراسری + پاصفحه (روی همهٔ فریم‌ها)
def overlay_progress(base, frac, accent):
    bar = Image.new("RGBA", (W - 144, 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(bar)
    d.rounded_rectangle([0, 0, bar.width - 1, 7], 4, fill=tuple(INK) + (34,))
    fw = int(max(10, bar.width * frac))
    d.rounded_rectangle([0, 0, fw, 7], 4, fill=tuple(accent) + (255,))
    put(base, bar, 72, 1828)


# ------------------------------------------------------------------ ساخت
def build_all(cfg):
    slug = cfg["slug"]
    os.makedirs(OUTDIR, exist_ok=True)
    slides_dir = os.path.join(OUTDIR, slug + "_slides")
    os.makedirs(slides_dir, exist_ok=True)

    content = cfg["slides"][:5]
    total = len(content) + 2
    durs = [cfg.get("cover_dur", 3.5)] + [cfg.get("slide_dur", 3.6)] * len(content) + \
           [cfg.get("cta_dur", 3.4)]

    s0 = Slide("cover", cfg, TEAL, 0, total)
    build_cover(s0, cfg)
    slides = [s0]
    for i, item in enumerate(content):
        s = Slide("content", cfg, ACCENTS[i % 3], i + 1, total)
        build_content(s, cfg, item)
        slides.append(s)
    sc = Slide("cta", cfg, CORAL, total - 1, total)
    build_cta(sc, cfg)
    slides.append(sc)

    frames_total = [int(round(d * FPS)) for d in durs]
    total_frames = sum(frames_total)

    # --- PNG تک‌تک اسلایدها (فریم پایانی هر اسلاید)
    pngs = []
    for i, s in enumerate(slides):
        img = s.draw(durs[i] * 0.92)
        if i > 0:
            overlay_progress(img, (sum(frames_total[:i + 1])) / total_frames, s.accent)
        footer(img, i, total, s.accent, brand=(i != 0))
        out = os.path.join(slides_dir, "slide_%d.png" % (i + 1))
        img.convert("RGB").save(out, "PNG", optimize=True)
        pngs.append(out)
    Image.open(pngs[0]).save(os.path.join(OUTDIR, slug + "_cover.png"), "PNG", optimize=True)

    # --- انکود ویدیو با لولهٔ فریم خام
    out_mp4 = os.path.join(OUTDIR, slug + "_reel.mp4")
    cmd = [FF, "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H),
           "-r", str(FPS), "-i", "-", "-an",
           "-c:v", "libx264", "-preset", "medium", "-crf", "23", "-threads", "2",
           "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.0",
           "-g", "60", "-movflags", "+faststart", out_mp4]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL)

    done = 0
    prev_final = None
    for i, s in enumerate(slides):
        n = frames_total[i]
        for f in range(n):
            t = f / FPS
            img = s.draw(t)
            # گذار نرم بین اسلایدها
            rgb = img.convert("RGB")
            if prev_final is not None and t < 0.34:
                a = ease_io(t / 0.34)
                rgb = Image.blend(prev_final, rgb, a)
                img = rgb.convert("RGBA")
            overlay_progress(img, (done + f + 1) / total_frames, s.accent)
            footer(img, i, total, s.accent, brand=(i != 0))
            proc.stdin.write(rgb.tobytes())
            prev_final = rgb
        done += n
        print("slide %d/%d done" % (i + 1, len(slides)), flush=True)

    proc.stdin.close()
    proc.wait()

    # --- رعایت سقف حجم (دو-پاس با بیت‌ریت محاسبه‌شده)
    cap_mb = cfg.get("max_mb", 3.9)
    if os.path.getsize(out_mp4) / 1048576 > cap_mb:
        dur_s = total_frames / FPS
        for extra in (0.90, 0.75, 0.62):
            kbps = int((cap_mb * 8192 * extra) / dur_s)
            tmp = out_mp4 + ".tmp.mp4"
            for p in (1, 2):
                cmd2 = [FF, "-y", "-i", out_mp4, "-an", "-c:v", "libx264", "-b:v", "%dk" % kbps,
                        "-pass", str(p), "-passlogfile", "plog_carousel", "-preset", "medium",
                        "-threads", "2", "-pix_fmt", "yuv420p", "-profile:v", "high",
                        "-level", "4.0", "-g", "60"]
                cmd2 += (["-f", "mp4", "/dev/null"] if p == 1 else
                         ["-movflags", "+faststart", tmp])
                subprocess.run(cmd2, check=True, capture_output=True)
            os.replace(tmp, out_mp4)
            if os.path.getsize(out_mp4) / 1048576 <= cap_mb:
                break
        for f in ("plog_carousel-0.log", "plog_carousel-0.log.mbtree"):
            if os.path.exists(f):
                os.remove(f)

    # --- کپشن
    cap_path = os.path.join(OUTDIR, slug + "_caption.txt")
    with open(cap_path, "w", encoding="utf-8") as fh:
        fh.write(cfg["caption"].strip() + "\n")

    size_mb = os.path.getsize(out_mp4) / 1048576
    print("DONE", out_mp4, round(size_mb, 2), "MB", total_frames, "frames")
    return {"mp4": out_mp4, "cover": os.path.join(OUTDIR, slug + "_cover.png"),
            "caption": cap_path, "slides": pngs, "mb": round(size_mb, 2)}

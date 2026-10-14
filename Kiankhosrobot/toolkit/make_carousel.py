"""
make_carousel.py — سازندهٔ کاروسل اینستاگرام (اسلایدهای ثابت ۱۰۸۰×۱۳۵۰، نسبت ۴:۵)

قانون چیدمان: متن هرگز روی تصویر نمی‌افتد.
  کاور:   برند ← تیتر ← زیرتیتر ← کارت تصویر ← «ورق بزن» + نقطه‌های پیشرفت
  اسلاید: شماره + تیتر + زیرتیتر ← کارت تصویر افقی ← جعبهٔ نکات با آیکون ← پانویس/CTA

متن فارسی: Pillow + libraqm اگر موجود باشد، وگرنه fatext (HarfBuzz/FreeType).
استفاده: یک فایل topic_<slug>_carousel.py با دیکشنری CFG بنویس و build(CFG) را صدا بزن.
خروجی: <outdir>/<slug>_carousel_<i>.png برای هر اسلاید.
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, features
from icons import icon


# ------------------------------------------------------------------ فونت
def _find_font_dir():
    here = os.path.dirname(os.path.abspath(__file__))
    cands = [os.environ.get("REEL_FONTS", ""),
             os.path.join(os.path.dirname(os.path.dirname(here)), "fonttmp", "fonts", "ttf"),
             "/home/user/Kiankhosrobot/fonttmp/fonts/ttf/",
             "/home/user/fonttmp/fonts/ttf/"]
    for c in cands:
        if c and os.path.isfile(os.path.join(c, "Vazirmatn-Bold.ttf")):
            return c if c.endswith("/") else c + "/"
    raise FileNotFoundError("Vazirmatn font not found; set REEL_FONTS")


FTDIR = _find_font_dir()
BLACK = FTDIR + "Vazirmatn-Black.ttf"
XBOLD = FTDIR + "Vazirmatn-ExtraBold.ttf"
BOLD = FTDIR + "Vazirmatn-Bold.ttf"
MED = FTDIR + "Vazirmatn-Medium.ttf"
W, H = 1080, 1350

if features.check("raqm"):
    KW = dict(language="fa", direction="rtl")

    def Draw(im):
        return ImageDraw.Draw(im)
else:
    from fatext import FD
    KW = {}

    def Draw(im):
        return FD(im)


def F(path, size):
    return ImageFont.truetype(path, size)


# ------------------------------------------------------------------ پالت‌ها
PALETTES = {
    # صورتی و بنفش
    "pinkpurple": dict(
        bg=[(46, 10, 82), (112, 28, 140), (214, 58, 150)],   # گرادیان قطری
        blob1=(255, 105, 180), blob2=(150, 80, 255),
        title1=(255, 255, 255), title2=(255, 182, 225),      # گرادیان تیتر
        sub=(255, 205, 235),
        accent=(255, 92, 170), accent2=(170, 100, 255),
        box=(255, 255, 255), box_text=(60, 20, 90), icon=(255, 255, 255),
        note_bg=(255, 228, 244), note_text=(150, 20, 100),
    ),
}


# ------------------------------------------------------------------ ابزارها
def lerp(a, b, t):
    return tuple(int(a[k] + (b[k] - a[k]) * t) for k in range(3))


def background(P):
    small = Image.new("RGB", (W // 6, H // 6))
    px = small.load()
    c0, c1, c2 = P["bg"]
    sw, sh = small.size
    for y in range(sh):
        for x in range(sw):
            t = (x / sw * 0.45 + y / sh * 0.55)
            px[x, y] = lerp(c0, c1, t / 0.5) if t < 0.5 else lerp(c1, c2, (t - 0.5) / 0.5)
    bg = small.resize((W, H), Image.BICUBIC)
    # لکه‌های نور نرم
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g = ImageDraw.Draw(glow)
    g.ellipse([-260, -220, 520, 520], fill=P["blob1"] + (95,))
    g.ellipse([640, 820, 1400, 1580], fill=P["blob2"] + (110,))
    g.ellipse([760, -120, 1180, 300], fill=P["blob2"] + (60,))
    glow = glow.filter(ImageFilter.GaussianBlur(120))
    bg = bg.convert("RGBA")
    bg.alpha_composite(glow)
    return bg


def grad_text(base, xy, txt, font, c1, c2, anchor="mm", shadow=True):
    mask = Image.new("L", (W, H), 0)
    Draw(mask).text(xy, txt, font=font, fill=255, anchor=anchor, **KW)
    bb = mask.getbbox()
    if not bb:
        return
    if shadow:
        sh = Image.new("RGBA", (W, H), (30, 0, 50, 0))
        sh.putalpha(mask.filter(ImageFilter.GaussianBlur(10)).point(lambda v: v * 160 // 255))
        base.alpha_composite(sh, (0, 6))
    g = Image.new("RGBA", (W, H), c2 + (255,))
    gd = ImageDraw.Draw(g)
    for y in range(bb[1], bb[3] + 1):
        gd.line([(0, y), (W, y)], fill=lerp(c1, c2, (y - bb[1]) / max(1, bb[3] - bb[1])) + (255,))
    g.putalpha(mask)
    base.alpha_composite(g)


def fit_font(path, txt, max_w, start, minimum=40):
    s = start
    probe = Draw(Image.new("L", (10, 10)))
    while s > minimum and probe.textlength(txt, font=F(path, s), **KW) > max_w:
        s -= 4
    return F(path, s)


def wrap(txt, font, max_w):
    probe = Draw(Image.new("L", (10, 10)))
    words, lines, cur = txt.split(" "), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if probe.textlength(t, font=font, **KW) <= max_w or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def cover_crop(im, w, h, focus_y=0.5, focus_x=0.5):
    r = max(w / im.width, h / im.height)
    im = im.resize((max(w, round(im.width * r)), max(h, round(im.height * r))), Image.LANCZOS)
    l = int((im.width - w) * focus_x)
    t = int((im.height - h) * focus_y)
    return im.crop((l, t, l + w, t + h))


def rounded_mask(w, h, r):
    m = Image.new("L", (w * 2, h * 2), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w * 2 - 1, h * 2 - 1], r * 2, fill=255)
    return m.resize((w, h), Image.LANCZOS)


def shadow(base, box, r, blur=28, alpha=120, off=14, col=(25, 0, 45)):
    x0, y0, x1, y1 = box
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([x0, y0 + off, x1, y1 + off], r, fill=col + (alpha,))
    base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur)))


def image_card(base, path, box, P, focus_y=0.5, focus_x=0.5, r=44, border=10):
    x0, y0, x1, y1 = box
    shadow(base, box, r)
    frame = Image.new("RGBA", (x1 - x0, y1 - y0), (0, 0, 0, 0))
    # قاب گرادیانی صورتی → بنفش
    fg = Image.new("RGBA", frame.size)
    fd = ImageDraw.Draw(fg)
    for x in range(frame.width):
        fd.line([(x, 0), (x, frame.height)], fill=lerp(P["accent"], P["accent2"], x / frame.width) + (255,))
    frame.paste(fg, (0, 0), rounded_mask(frame.width, frame.height, r))
    iw, ih = frame.width - 2 * border, frame.height - 2 * border
    img = cover_crop(Image.open(path).convert("RGB"), iw, ih, focus_y, focus_x)
    frame.paste(img, (border, border), rounded_mask(iw, ih, r - border))
    base.alpha_composite(frame, (x0, y0))


def dots(base, n, i, y, P):
    d = ImageDraw.Draw(base)
    gap, big, small = 14, 46, 14
    widths = [big if k == i else small for k in range(n)]
    total = sum(widths) + gap * (n - 1)
    x = W / 2 + total / 2   # راست‌به‌چپ: اسلاید اول سمت راست
    for k in range(n):
        w_ = widths[k]
        col = (255, 255, 255, 255) if k == i else (255, 255, 255, 110)
        d.rounded_rectangle([x - w_, y - 7, x, y + 7], 7, fill=col)
        x -= w_ + gap


def pill(base, center, txt, font, bg, fg, pad=(34, 14)):
    d = Draw(base)
    tw = d.textlength(txt, font=font, **KW)
    cx, cy = center
    hh = font.size * 0.75 + pad[1]
    box = [cx - tw / 2 - pad[0], cy - hh, cx + tw / 2 + pad[0], cy + hh]
    lay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(lay).rounded_rectangle(box, int(hh), fill=bg)
    base.alpha_composite(lay)
    d.text((cx, cy), txt, font=font, fill=fg, anchor="mm", **KW)
    return box


def brand(base, txt, P):
    pill(base, (W / 2, 78), txt, F(BOLD, 30), (255, 255, 255, 40), (255, 255, 255))


# ------------------------------------------------------------------ کاور
def make_cover(cfg, P, n):
    im = background(P)
    brand(im, cfg["brand"], P)
    t = cfg["cover"]
    grad_text(im, (W / 2, 200), t["title"], fit_font(BLACK, t["title"], 960, 112),
              P["title1"], P["title2"])
    Draw(im).text((W / 2, 318), t["subtitle"], font=F(XBOLD, 56), fill=P["sub"], anchor="mm", **KW)
    cw = 640
    ch = int(cw * 5 / 4)
    if 390 + ch > 1180:
        ch = 1180 - 390
        cw = int(ch * 4 / 5)
    x0 = (W - cw) // 2
    image_card(im, t["image"], (x0, 390, x0 + cw, 390 + ch), P, t.get("focus_y", 0.5))
    # برچسب هوک روی گوشهٔ قاب (خارج از تصویر: نیمه روی لبهٔ پایین قاب نمی‌رود)
    hook = t.get("hook")
    if hook:
        pill(im, (W / 2, 1218), hook, F(BLACK, 40), P["accent"] + (255,), (255, 255, 255), pad=(40, 16))
    Draw(im).text((W / 2, 1280), cfg.get("swipe", "ورق بزن «"), font=F(BOLD, 30),
                  fill=(255, 255, 255), anchor="mm", **KW)
    dots(im, n, 0, 1326, P)
    return im


# ------------------------------------------------------------------ اسلاید محتوا
def make_slide(cfg, s, P, idx, n):
    im = background(P)
    d = Draw(im)
    # شمارهٔ اسلاید
    badge_r = 44
    bx, by = W - 70 - badge_r, 92
    ImageDraw.Draw(im).ellipse([bx - badge_r, by - badge_r, bx + badge_r, by + badge_r],
                               fill=P["accent"] + (255,), outline=(255, 255, 255), width=4)
    d.text((bx, by + 2), s["num"], font=F(BLACK, 50), fill=(255, 255, 255), anchor="mm", **KW)
    # تیتر کنار نشان، راست‌چین
    tx = bx - badge_r - 24
    tfont = fit_font(BLACK, s["title"], tx - 60, 72, 48)
    grad_text(im, (tx, by), s["title"], tfont, P["title1"], P["title2"], anchor="rm")
    d.text((W / 2, 196), s["subtitle"], font=F(BOLD, 40), fill=P["sub"], anchor="mm", **KW)

    # کارت تصویر افقی
    cy0 = 248
    ch = s.get("card_h", 400)
    image_card(im, s["image"], (60, cy0, W - 60, cy0 + ch), P, s.get("focus_y", 0.5), r=40)

    # جعبهٔ نکات
    by0 = cy0 + ch + 34
    foot = s.get("note")
    by1 = H - (150 if foot else 80)
    shadow(im, (60, by0, W - 60, by1), 40, alpha=90)
    ImageDraw.Draw(im).rounded_rectangle([60, by0, W - 60, by1], 40, fill=P["box"] + (255,))

    pts = s["points"]
    isz = 64
    text_right = W - 60 - 40 - isz - 26
    text_w = text_right - (60 + 40)
    fsz = s.get("font", 38)
    font = F(BOLD, fsz)
    lh = int(fsz * 1.5)
    blocks = [wrap(p_[1], font, text_w) for p_ in pts]
    content_h = sum(len(b) * lh for b in blocks)
    gap = (by1 - by0 - 60 - content_h) / max(1, len(pts) - 1)
    gap = max(14, min(gap, 46))
    total = content_h + gap * (len(pts) - 1)
    y = by0 + (by1 - by0 - total) / 2
    for (kind, _), lines in zip(pts, blocks):
        block_h = len(lines) * lh
        # دایرهٔ آیکون
        icx = W - 60 - 40 - isz / 2
        icy = y + min(block_h, lh) / 2 if len(lines) == 1 else y + lh / 2
        dd = ImageDraw.Draw(im)
        grad = Image.new("RGBA", (isz, isz))
        gdd = ImageDraw.Draw(grad)
        for k in range(isz):
            gdd.line([(0, k), (isz, k)], fill=lerp(P["accent"], P["accent2"], k / isz) + (255,))
        im.paste(grad, (int(icx - isz / 2), int(icy - isz / 2)), rounded_mask(isz, isz, isz // 2))
        ic = icon(kind, 40, P["icon"])
        im.alpha_composite(ic, (int(icx - ic.width / 2), int(icy - ic.height / 2)))
        for li, line in enumerate(lines):
            d.text((text_right, y + li * lh + lh / 2), line, font=font, fill=P["box_text"],
                   anchor="rm", **KW)
        y += block_h + gap

    if foot:
        pill(im, (W / 2, H - 100), foot, F(XBOLD, 34), P["note_bg"] + (255,), P["note_text"],
             pad=(36, 14))
    dots(im, n, idx, H - 36, P)
    return im


def build(cfg):
    P = PALETTES[cfg.get("palette", "pinkpurple")]
    n = 1 + len(cfg["slides"])
    out = []
    os.makedirs(cfg["outdir"], exist_ok=True)
    imgs = [make_cover(cfg, P, n)] + [make_slide(cfg, s, P, i + 1, n)
                                      for i, s in enumerate(cfg["slides"])]
    for i, im in enumerate(imgs, 1):
        p = os.path.join(cfg["outdir"], f"{cfg['slug']}_carousel_{i}.png")
        im.convert("RGB").save(p, optimize=True)
        out.append(p)
    if cfg.get("caption"):
        p = os.path.join(cfg["outdir"], f"{cfg['slug']}_carousel_caption.txt")
        with open(p, "w", encoding="utf-8") as f:
            f.write(cfg["caption"].strip() + "\n")
        out.append(p)
    return out

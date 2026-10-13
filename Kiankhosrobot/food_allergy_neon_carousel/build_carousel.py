#!/usr/bin/env python3
"""Generate a six-slide Persian food-allergy introduction carousel.
Requires Pillow, numpy, uharfbuzz and freetype-py; uses toolkit/fatext.py for RTL text.
"""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "Kiankhosrobot" / "toolkit"))
from fatext import FD  # noqa: E402

W, H, S = 1080, 1350, 2
P = {
    "bg": "#090C1C",
    "bg2": "#10152A",
    "card": "#141B32",
    "card2": "#1A2340",
    "white": "#F5F7FF",
    "muted": "#B5BED4",
    "line": "#2A3452",
    "cyan": "#20E8FF",
    "pink": "#FF38CB",
    "lime": "#C9FF3A",
    "orange": "#FF9E32",
    "purple": "#A76BFF",
    "red": "#FF566C",
    "skin": "#F3C7A8",
    "hair": "#28203E",
    "cream": "#FFE9BD",
    "food": "#FFCA45",
    "green": "#5DFFB2",
}
NEON = ["cyan", "pink", "lime", "orange", "purple", "red"]
FONT = {
    "regular": ROOT / "fonttmp/fonts/ttf/Vazirmatn-Regular.ttf",
    "medium": ROOT / "fonttmp/fonts/ttf/Vazirmatn-Medium.ttf",
    "bold": ROOT / "fonttmp/fonts/ttf/Vazirmatn-Bold.ttf",
    "extra": ROOT / "fonttmp/fonts/ttf/Vazirmatn-ExtraBold.ttf",
}


def z(n):
    return int(round(n * S))


def rgb(value):
    h = P.get(value, value)
    return tuple(int(h[i:i+2], 16) for i in (1, 3, 5))


def fnt(size, weight="regular"):
    return ImageFont.truetype(str(FONT[weight]), z(size))


def canvas():
    im = Image.new("RGBA", (z(W), z(H)), (*rgb("bg"), 255))
    return im, FD(im)


def rect(d, xy, fill, radius=22, outline=None, width=1):
    x0, y0, x1, y1 = xy
    d.rounded_rectangle((z(x0), z(y0), z(x1), z(y1)), radius=z(radius),
                        fill=rgb(fill) if isinstance(fill, str) else fill,
                        outline=rgb(outline) if outline else None,
                        width=z(width) if outline else 1)


def ellipse(d, xy, fill=None, outline=None, width=1):
    x0, y0, x1, y1 = xy
    d.ellipse((z(x0), z(y0), z(x1), z(y1)),
              fill=rgb(fill) if isinstance(fill, str) else fill,
              outline=rgb(outline) if outline else None,
              width=z(width) if outline else 1)


def line(d, pts, fill, width=3):
    d.line([(z(x), z(y)) for x, y in pts], fill=rgb(fill) if isinstance(fill, str) else fill,
           width=z(width), joint="curve")


def poly(d, pts, fill):
    d.polygon([(z(x), z(y)) for x, y in pts], fill=rgb(fill) if isinstance(fill, str) else fill)


def text(d, s, x, y, size=27, fill="white", weight="regular", anchor="ra"):
    d.text((z(x), z(y)), s, font=fnt(size, weight), fill=rgb(fill), anchor=anchor)


def lines(d, seq, x, y, size=25, fill="white", weight="regular", leading=None, anchor="ra"):
    if isinstance(seq, str):
        seq = seq.split("\n")
    leading = leading or int(size * 1.42)
    for i, s in enumerate(seq):
        text(d, s, x, y + i * leading, size, fill, weight, anchor)


def center(d, s, cx, cy, size=22, fill="white", weight="medium"):
    d.text((z(cx), z(cy)), s, font=fnt(size, weight), fill=rgb(fill), anchor="mm")


def pill(d, xy, label, accent="cyan", size=19, fill="card2"):
    rect(d, xy, fill, radius=(xy[3]-xy[1])/2, outline=accent, width=1)
    center(d, label, (xy[0]+xy[2])/2, (xy[1]+xy[3])/2, size, accent, "bold")


def card(d, xy, accent="cyan", fill="card"):
    rect(d, xy, fill, radius=25, outline="line", width=1)
    x0, y0, x1, y1 = xy
    rect(d, (x1-8, y0+24, x1-4, y1-24), accent, radius=2)


def neon_dot(d, cx, cy, r, col):
    ellipse(d, (cx-r, cy-r, cx+r, cy+r), col)
    ellipse(d, (cx-r-5, cy-r-5, cx+r+5, cy+r+5), None, col, 1)


def icon_ring(d, cx, cy, col="cyan", r=58):
    ellipse(d, (cx-r, cy-r, cx+r, cy+r), "bg2", outline=col, width=2)


def icon_skin(d, cx, cy):
    icon_ring(d, cx, cy, "pink")
    line(d, [(cx-36, cy+23), (cx+36, cy+23)], "orange", 5)
    for dx, yy in [(-25, -20), (0, -34), (26, -22)]:
        line(d, [(cx+dx, cy+20), (cx+dx+2, cy+yy)], "white", 3)
    ellipse(d, (cx-12, cy-6, cx+14, cy+20), "red")
    neon_dot(d, cx+32, cy-29, 4, "pink")


def icon_lungs(d, cx, cy):
    icon_ring(d, cx, cy, "cyan")
    line(d, [(cx, cy-37), (cx, cy-5), (cx-10, cy+4)], "cyan", 4)
    line(d, [(cx, cy-10), (cx+10, cy+1)], "cyan", 4)
    # two stylized lungs
    line(d, [(cx-10, cy+1), (cx-25, cy+5), (cx-34, cy+22), (cx-31, cy+37), (cx-17, cy+35), (cx-8, cy+19), (cx-8, cy+6)], "pink", 4)
    line(d, [(cx+10, cy+1), (cx+25, cy+5), (cx+34, cy+22), (cx+31, cy+37), (cx+17, cy+35), (cx+8, cy+19), (cx+8, cy+6)], "purple", 4)


def icon_stomach(d, cx, cy):
    icon_ring(d, cx, cy, "lime")
    line(d, [(cx-8, cy-34), (cx-8, cy-5), (cx-22, cy+5), (cx-25, cy+24),
             (cx-13, cy+35), (cx+15, cy+34), (cx+31, cy+18), (cx+24, cy+1),
             (cx+8, cy-4), (cx+5, cy-25)], "lime", 4)
    neon_dot(d, cx+25, cy-24, 4, "orange")


def icon_shield(d, cx, cy, accent="cyan"):
    icon_ring(d, cx, cy, accent)
    poly(d, [(cx, cy-37), (cx+29, cy-24), (cx+24, cy+13), (cx, cy+36),
             (cx-24, cy+13), (cx-29, cy-24)], "card2")
    line(d, [(cx-15, cy-2), (cx-4, cy+10), (cx+17, cy-15)], "lime", 4)


def icon_egg(d, cx, cy, accent="orange"):
    icon_ring(d, cx, cy, accent)
    ellipse(d, (cx-25, cy-36, cx+25, cy+37), "cream", outline=accent, width=3)
    ellipse(d, (cx-11, cy-5, cx+14, cy+20), "orange")
    neon_dot(d, cx+34, cy-28, 3, "pink")


def icon_peanut(d, cx, cy):
    icon_ring(d, cx, cy, "purple")
    ellipse(d, (cx-32, cy-23, cx+4, cy+25), None, "orange", 4)
    ellipse(d, (cx-3, cy-25, cx+31, cy+22), None, "pink", 4)
    for x, y in [(-19, -5), (-7, 8), (13, -8), (21, 8)]:
        neon_dot(d, cx+x, cy+y, 3, "lime")


def icon_sit(d, cx, cy, accent="cyan"):
    icon_ring(d, cx, cy, accent)
    ellipse(d, (cx-9, cy-28, cx+9, cy-10), "cream")
    line(d, [(cx, cy-8), (cx-6, cy+16), (cx+18, cy+18)], "cyan", 4)
    line(d, [(cx+18, cy+18), (cx+29, cy+31)], "pink", 4)
    line(d, [(cx-7, cy+14), (cx-25, cy+20), (cx-29, cy+33)], "lime", 4)
    line(d, [(cx+23, cy+1), (cx+23, cy+32)], "white", 3)
    line(d, [(cx+23, cy+29), (cx+38, cy+29)], "white", 3)


def icon_head(d, cx, cy, accent="pink"):
    icon_ring(d, cx, cy, accent)
    ellipse(d, (cx-22, cy-27, cx+22, cy+18), "cream")
    line(d, [(cx-28, cy+30), (cx-22, cy+8), (cx+22, cy+8), (cx+28, cy+30)], "cyan", 4)
    line(d, [(cx-15, cy-9), (cx-9, cy-9)], "purple", 3)
    line(d, [(cx+9, cy-9), (cx+15, cy-9)], "purple", 3)


def icon_swallow(d, cx, cy, accent="lime"):
    icon_ring(d, cx, cy, accent)
    line(d, [(cx-27, cy-10), (cx-9, cy-10), (cx-2, cy-2), (cx+15, cy-2)], "cyan", 4)
    poly(d, [(cx+15, cy-8), (cx+29, cy-2), (cx+15, cy+4)], "cyan")
    line(d, [(cx-8, cy+2), (cx-2, cy+13), (cx+13, cy+18)], "pink", 4)
    line(d, [(cx+7, cy+26), (cx+29, cy+26)], "lime", 3)


def icon_spoon(d, cx, cy, accent="orange"):
    icon_ring(d, cx, cy, accent)
    line(d, [(cx-24, cy+26), (cx+19, cy-18)], "cyan", 5)
    ellipse(d, (cx+4, cy-37, cx+33, cy-9), None, "pink", 4)
    neon_dot(d, cx-24, cy+26, 3, "lime")


def icon_alert(d, cx, cy):
    icon_ring(d, cx, cy, "red")
    poly(d, [(cx, cy-34), (cx+34, cy+27), (cx-34, cy+27)], "#30172A")
    line(d, [(cx, cy-14), (cx, cy+7)], "red", 4)
    ellipse(d, (cx-3, cy+14, cx+3, cy+20), "lime")


def icon_cross(d, cx, cy, accent="pink"):
    icon_ring(d, cx, cy, accent)
    line(d, [(cx-24, cy), (cx+24, cy)], accent, 5)
    line(d, [(cx, cy-24), (cx, cy+24)], accent, 5)


def add_neon_decor(d, page):
    colors = ["cyan", "pink", "purple", "lime", "orange"]
    # faint orbit rings at the corners
    ellipse(d, (935, -90, 1150, 125), None, colors[(page-1) % len(colors)], 1)
    ellipse(d, (-110, 1100, 30, 1240), None, colors[(page+1) % len(colors)], 1)
    for x, y, c in [(995, 205, colors[page % 5]), (78, 1070, colors[(page+2) % 5]),
                    (966, 1170, colors[(page+3) % 5])]:
        neon_dot(d, x, y, 3, c)


def header(d, page, title, subtitle, accent=None):
    accent = accent or NEON[(page-1) % len(NEON)]
    add_neon_decor(d, page)
    pill(d, (72, 47, 253, 96), f"اسلاید {page} از ۶", accent, 18)
    text(d, "تغذیهٔ کودک  •  آگاهی از آلرژی", 1008, 61, 19, "muted", "medium")
    rect(d, (986, 140, 997, 208), accent, radius=5)
    text(d, title, 958, 135, 46, "white", "extra")
    if isinstance(subtitle, str):
        subtitle = [subtitle]
    lines(d, subtitle, 958, 207, 24, "muted", "regular", leading=34)
    rect(d, (72, 293, 1008, 296), "line", radius=2)


def footer(d, page):
    rect(d, (72, 1280, 1008, 1288), "line", radius=4)
    used = 936 * page / 6
    start = 1008 - used
    colors = ["cyan", "pink", "purple", "lime", "orange", "red"]
    seg = 936 / 6
    for i in range(page):
        r0 = 1008 - (i+1) * seg
        r1 = 1008 - i * seg
        r0, r1 = max(start, r0), min(1008, r1)
        if r1 > r0:
            rect(d, (r0, 1280, r1, 1288), colors[5-i], radius=4)
    text(d, "آموزشی؛ نه جایگزینِ نظر پزشک", 1008, 1300, 17, "muted", "regular")


def gradient_cover():
    top, bottom = np.array(rgb("bg")), np.array(rgb("#211335"))
    arr = np.empty((z(H), z(W), 3), dtype=np.uint8)
    for y in range(z(H)):
        t = y / max(1, z(H)-1)
        arr[y, :, :] = (top*(1-t) + bottom*t).astype(np.uint8)
    return Image.fromarray(arr, "RGB").convert("RGBA")


def cover_art(d):
    # Rounded neon frame and orbit rings.
    rect(d, (72, 630, 1008, 1220), "card", radius=36, outline="cyan", width=2)
    ellipse(d, (306, 678, 774, 1146), None, "purple", 3)
    ellipse(d, (336, 708, 744, 1116), None, "pink", 2)
    # A friendly infant-like face, kept abstract and non-medical.
    ellipse(d, (418, 728, 662, 972), "hair")
    ellipse(d, (440, 748, 640, 950), "skin")
    ellipse(d, (431, 718, 648, 833), "hair")
    for dx, dy, r in [(-75, -51, 30), (-34, -75, 28), (13, -76, 30), (59, -55, 28)]:
        ellipse(d, (540+dx-r, 809+dy-r, 540+dx+r, 809+dy+r), "hair")
    ellipse(d, (482, 842, 494, 854), "purple")
    ellipse(d, (566, 842, 578, 854), "purple")
    line(d, [(500, 891), (520, 904), (540, 906), (561, 892)], "pink", 4)
    # Neon bowl with soft, colorful foods.
    rect(d, (314, 1005, 690, 1137), "bg2", radius=42, outline="cyan", width=3)
    ellipse(d, (336, 1001, 669, 1060), "#1B2341", outline="purple", width=2)
    for x, y, c, r in [(388, 1030, "orange", 18), (445, 1045, "lime", 14),
                        (497, 1027, "pink", 18), (550, 1044, "cyan", 15), (606, 1028, "purple", 17)]:
        ellipse(d, (x-r, y-r, x+r, y+r), c)
    # Spoon and a few recognizable, safe-form food symbols.
    line(d, [(703, 1005), (787, 921)], "lime", 8)
    ellipse(d, (773, 895, 818, 940), None, "lime", 4)
    icon_egg(d, 205, 857, "orange")
    icon_peanut(d, 878, 855)
    sparkle(d, 196, 1064, 15, "pink")
    sparkle(d, 850, 1058, 14, "cyan")
    pill(d, (365, 1151, 719, 1194), "با آمادگی، نه با ترس", "lime", 18)


def sparkle(d, cx, cy, r, col):
    poly(d, [(cx,cy-r),(cx+4,cy-4),(cx+r,cy),(cx+4,cy+4),
             (cx,cy+r),(cx-4,cy+4),(cx-r,cy),(cx-4,cy-4)], col)


def slide1():
    im = gradient_cover()
    d = FD(im)
    # multicolor light forms stay in the margin, away from the headline
    ellipse(d, (860, -225, 1235, 146), None, "cyan", 2)
    ellipse(d, (895, -192, 1202, 111), None, "purple", 2)
    ellipse(d, (-120, 448, 42, 610), None, "pink", 2)
    pill(d, (72, 51, 383, 102), "راهنمای والدین • تغذیهٔ کودک", "cyan", 18)
    text(d, "واکنشِ غذایی پس از مواجهه با غذا آشکار می‌شود؛", 1008, 166, 25, "lime", "medium")
    text(d, "غذاهای آلرژی‌زا", 1008, 229, 67, "white", "extra")
    text(d, "آشنایی، نه ترس", 1008, 325, 65, "pink", "extra")
    lines(d, ["اولین واکنش ممکن است هنگامِ معرفی غذا دیده شود.",
              "با آمادگی و روشِ ایمن شروع کنیم—نه با حذفِ بی‌دلیل."],
          1008, 433, 26, "muted", "regular", leading=41)
    pill(d, (781, 535, 1008, 581), "۶ نکتهٔ کاربردی", "orange", 18)
    cover_art(d)
    rect(d, (72, 1280, 1008, 1288), "line", radius=4)
    rect(d, (72, 1280, 228, 1288), "cyan", radius=4)
    center(d, "ورق بزنید  ←", 170, 1315, 19, "white", "medium")
    center(d, "۱ از ۶", 928, 1315, 18, "muted", "medium")
    return im


def slide2():
    im, d = canvas()
    header(d, 2, "واکنش غذایی چه‌طور دیده می‌شود؟", ["آلرژی می‌تواند پوست، تنفس یا گوارش را درگیر کند."], "pink")
    data = [
        (324, "پوست", "کهیر، خارش یا تورمِ لب و صورت.", icon_skin, "pink"),
        (526, "تنفس و دهان", "سرفهٔ مکرر، خس‌خس یا گرفتگی گلو.", icon_lungs, "cyan"),
        (728, "گوارش و حال عمومی", "استفراغ یا دل‌درد؛ برخی واکنش‌ها دیرترند.", icon_stomach, "lime"),
    ]
    for y, title, body, icon, accent in data:
        card(d, (72, y, 1008, y+184), accent)
        icon(d, 180, y+92)
        pill(d, (700, y+25, 923, y+68), title, accent, 18)
        text(d, body, 923, y+91, 25, "white", "medium")
    rect(d, (72, 945, 1008, 1182), "bg2", radius=27, outline="purple", width=1)
    icon_alert(d, 172, 1062)
    text(d, "زمان و شدتِ واکنش برای همه یکسان نیست.", 925, 992, 25, "white", "bold")
    lines(d, ["بسیاری از واکنش‌های فوری در چند دقیقه تا چند ساعت", "شروع می‌شوند؛ بعضی الگوها دیرتر بروز می‌کنند."],
          925, 1043, 23, "muted", "regular", leading=38)
    footer(d, 2)
    return im


def slide3():
    im, d = canvas()
    header(d, 3, "چرا بی‌دلیل عقب نیندازیم؟", ["تأخیرِ همگانی، راهِ اثبات‌شدهٔ پیشگیری نیست."], "cyan")
    card(d, (72, 330, 1008, 641), "cyan")
    icon_shield(d, 180, 482, "cyan")
    pill(d, (675, 358, 924, 405), "همهٔ آلرژن‌ها", "cyan", 18)
    lines(d, ["عقب‌انداختنِ غذاهای آلرژی‌زا،", "روشِ اثبات‌شدهٔ پیشگیری برای", "همهٔ کودکان نیست."],
          923, 436, 26, "white", "medium", leading=39)
    card(d, (72, 665, 1008, 967), "pink")
    icon_peanut(d, 180, 816)
    pill(d, (708, 692, 924, 739), "بادام‌زمینی", "pink", 18)
    lines(d, ["برای بادام‌زمینی، معرفیِ برنامه‌ریزی‌شده", "و مصرفِ منظم در شیرخوارگی می‌تواند", "خطر آلرژی را کاهش دهد."],
          923, 771, 25, "white", "medium", leading=38)
    rect(d, (72, 990, 1008, 1185), "#21162F", radius=26, outline="purple", width=1)
    icon_alert(d, 177, 1086)
    text(d, "این شواهد برای همهٔ غذاها یکسان نیست", 925, 1030, 24, "lime", "bold")
    text(d, "و معرفی زودهنگام هم تضمینِ صفرشدن آلرژی نیست.", 925, 1079, 22, "white", "regular")
    footer(d, 3)
    return im


def slide4():
    im, d = canvas()
    header(d, 4, "زمانِ شروع و آمادگی", ["غذای کمکی را با توجه به رشدِ کودک آغاز کنید."], "lime")
    rect(d, (72, 326, 1008, 509), "card", radius=27, outline="lime", width=1)
    text(d, "حدود ۶ ماهگی", 925, 355, 38, "lime", "extra")
    lines(d, ["وقتی نوزاد برای غذای کمکی آماده است؛", "غذای کمکی پیش از ۴ ماهگی توصیه نمی‌شود."],
          925, 407, 23, "white", "regular", leading=36)
    ready = [
        (530, "کنترلِ خوبِ سر و گردن", icon_head, "cyan"),
        (675, "می‌تواند با کمک بنشیند", icon_sit, "pink"),
        (820, "غذا را می‌بلعد، نه اینکه بیرون براند", icon_swallow, "lime"),
    ]
    for y, label, icon, accent in ready:
        card(d, (72, y, 1008, y+126), accent)
        icon(d, 177, y+63, accent) if icon in (icon_head, icon_sit, icon_swallow) else icon(d, 177, y+63)
        text(d, label, 923, y+42, 25, "white", "medium")
    rect(d, (72, 976, 1008, 1187), "#231A2E", radius=27, outline="orange", width=1)
    icon_alert(d, 177, 1081)
    text(d, "اگزمای شدید یا آلرژی به تخم‌مرغ؟", 925, 1004, 25, "orange", "bold")
    lines(d, ["پیش از معرفی بادام‌زمینی با پزشک برنامه‌ریزی کنید؛", "گاهی ارزیابی یا معرفیِ زیر نظر لازم است."],
          925, 1051, 22, "white", "regular", leading=37)
    footer(d, 4)
    return im


def slide5():
    im, d = canvas()
    header(d, 5, "معرفیِ ایمن، نه ترسناک", ["بافتِ مناسب و نظارت، به‌اندازهٔ زمان‌بندی مهم‌اند."], "orange")
    data = [
        (324, ["یک آلرژنِ جدید در هر نوبت؛", "مقدار کم، وقتی کودک سالم است."], icon_cross, "pink"),
        (507, ["تخم‌مرغِ کاملاً پخته؛", "کرهٔ بادام‌زمینیِ رقیق‌شده در پوره."], icon_egg, "orange"),
        (690, ["کودک صاف بنشیند و هنگامِ خوردن", "زیر نظر بزرگسال باشد."], icon_sit, "cyan"),
        (873, ["مغزِ کامل یا قاشقِ غلیظِ کرهٔ مغزها", "ندهید؛ خطرِ خفگی دارد."], icon_peanut, "purple"),
    ]
    for y, body_lines, icon, accent in data:
        card(d, (72, y, 1008, y+164), accent)
        icon(d, 178, y+82, accent) if icon is icon_cross else icon(d, 178, y+82)
        lines(d, body_lines, 923, y+43, 22, "white", "medium", leading=34)
    rect(d, (72, 1057, 1008, 1190), "#1A2034", radius=25, outline="lime", width=1)
    icon_shield(d, 177, 1123, "lime")
    lines(d, ["اگر تحمل کرد، طبق توصیهٔ پزشک در رژیم بماند؛", "برای بادام‌زمینی، مصرفِ منظم اهمیت دارد."],
          925, 1080, 22, "lime", "medium", leading=35)
    footer(d, 5)
    return im


def slide6():
    im, d = canvas()
    header(d, 6, "اگر واکنش دیدیم، چه کنیم؟", ["آرام بمانید؛ شدتِ نشانه‌ها تعیین‌کننده است."], "red")
    card(d, (72, 328, 1008, 570), "orange")
    icon_skin(d, 180, 449)
    text(d, "کهیر یا ورم دیدید؟", 923, 361, 28, "orange", "bold")
    lines(d, ["غذا را متوقف کنید و با پزشک کودک تماس بگیرید؛", "تا دریافتِ راهنمایی، دوباره در خانه معرفی نکنید."],
          923, 412, 24, "white", "medium", leading=39)
    card(d, (72, 595, 1008, 938), "red", fill="#211629")
    icon_alert(d, 180, 765)
    pill(d, (737, 624, 923, 672), "فوریت پزشکی", "red", 18, fill="#30182E")
    lines(d, ["تنگی نفس، تورمِ زبان یا گلو، بی‌حالیِ شدید", "یا علائم هم‌زمان در چند بخش بدن؟", "اگر اپی‌نفرین تجویز شده، طبق برنامه فوراً", "استفاده کنید و با اورژانس تماس بگیرید."],
          923, 700, 23, "white", "medium", leading=38)
    rect(d, (72, 966, 1008, 1190), "card2", radius=28, outline="cyan", width=1)
    sparkle(d, 174, 1022, 15, "lime")
    text(d, "آگاهی، نه ترس؛ آمادگی، نه خودتشخیصی.", 923, 998, 25, "cyan", "bold")
    text(d, "ذخیره کنید و با والدین دیگر به‌اشتراک بگذارید.", 923, 1050, 22, "white", "medium")
    pill(d, (660, 1102, 925, 1149), "این پست جای پزشک نیست", "lime", 18)
    footer(d, 6)
    return im


def flatten(im):
    if im.mode == "RGBA":
        bg = Image.new("RGBA", im.size, (*rgb("bg"), 255))
        bg.alpha_composite(im)
        im = bg.convert("RGB")
    if im.size != (z(W), z(H)):
        raise ValueError(f"Unexpected canvas size: {im.size}")
    return im.resize((W, H), Image.Resampling.LANCZOS)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    pages = [slide1(), slide2(), slide3(), slide4(), slide5(), slide6()]
    final = []
    for i, page in enumerate(pages, 1):
        im = flatten(page)
        im.save(OUT / f"slide_{i:02d}.png", "PNG", optimize=True)
        final.append(im)
    final[0].save(OUT / "carousel.pdf", "PDF", save_all=True,
                  append_images=final[1:], resolution=150, quality=92)
    bundle = OUT / "carousel_assets.zip"
    with zipfile.ZipFile(bundle, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for p in sorted(OUT.glob("slide_*.png")):
            zf.write(p, p.name)
        for name in ("caption.txt", "sources.txt", "README.md"):
            p = OUT / name
            if p.exists():
                zf.write(p, p.name)
    print("Built six 1080x1350 slides")
    for p in sorted(OUT.glob("slide_*.png")):
        print(f"{p.name}: {p.stat().st_size:,} bytes")
    print(f"PDF: {(OUT/'carousel.pdf').stat().st_size:,} bytes")
    print(f"ZIP: {bundle.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()

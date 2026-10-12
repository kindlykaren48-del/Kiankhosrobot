#!/usr/bin/env python3
"""Build a six-slide Persian Instagram carousel (1080x1350, 4:5).

Requires Pillow, numpy, uharfbuzz, and freetype-py. Persian text is shaped via
Kiankhosrobot/toolkit/fatext.py so the output remains correct without libraqm.
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

W, H, SCALE = 1080, 1350, 2
SZ = lambda v: int(round(v * SCALE))

# Palette: burgundy + mojito (fresh mint/lime) + warm paper.
C = {
    "wine": "#50152F",
    "wine2": "#742A4B",
    "wine3": "#9A4664",
    "cream": "#FFF8F0",
    "paper": "#FFFCF8",
    "white": "#FFFFFF",
    "mint": "#DDEFD2",
    "mint2": "#B5D698",
    "lime": "#D2E994",
    "jade": "#387565",
    "jade_dark": "#24594C",
    "rose": "#F5E1E3",
    "rose2": "#EFCBD3",
    "peach": "#F1C7A8",
    "skin": "#EBC4A6",
    "hair": "#38242C",
    "ink": "#382931",
    "muted": "#76636A",
    "line": "#E8DCE0",
    "gold": "#E5B860",
    "red": "#A83B50",
}

FONT_PATHS = {
    "regular": ROOT / "fonttmp/fonts/ttf/Vazirmatn-Regular.ttf",
    "medium": ROOT / "fonttmp/fonts/ttf/Vazirmatn-Medium.ttf",
    "bold": ROOT / "fonttmp/fonts/ttf/Vazirmatn-Bold.ttf",
    "extra": ROOT / "fonttmp/fonts/ttf/Vazirmatn-ExtraBold.ttf",
}


def color(name_or_hex: str):
    v = C.get(name_or_hex, name_or_hex)
    return tuple(int(v[i:i + 2], 16) for i in (1, 3, 5))


def font(size: int, weight: str = "regular"):
    return ImageFont.truetype(str(FONT_PATHS[weight]), SZ(size))


def new_slide(bg: str = "cream"):
    im = Image.new("RGBA", (SZ(W), SZ(H)), (*color(bg), 255))
    return im, FD(im)


def box(d, xy, fill, radius=24, outline=None, width=1):
    x0, y0, x1, y1 = xy
    d.rounded_rectangle((SZ(x0), SZ(y0), SZ(x1), SZ(y1)), radius=SZ(radius),
                        fill=color(fill) if isinstance(fill, str) else fill,
                        outline=color(outline) if outline else None,
                        width=SZ(width) if outline else 1)


def ellipse(d, xy, fill, outline=None, width=1):
    x0, y0, x1, y1 = xy
    d.ellipse((SZ(x0), SZ(y0), SZ(x1), SZ(y1)),
              fill=color(fill) if isinstance(fill, str) else fill,
              outline=color(outline) if outline else None,
              width=SZ(width) if outline else 1)


def line(d, xy, fill, width=3, joint="curve"):
    d.line([(SZ(x), SZ(y)) for x, y in xy], fill=color(fill) if isinstance(fill, str) else fill,
           width=SZ(width), joint=joint)


def polygon(d, xy, fill):
    d.polygon([(SZ(x), SZ(y)) for x, y in xy], fill=color(fill) if isinstance(fill, str) else fill)


def txt(d, text, x, y, size=28, fill="ink", weight="regular", anchor="ra"):
    d.text((SZ(x), SZ(y)), text, font=font(size, weight), fill=color(fill), anchor=anchor)


def txt_lines(d, lines, x, y, size=28, fill="ink", weight="regular", leading=None, anchor="ra"):
    if isinstance(lines, str):
        lines = lines.split("\n")
    leading = leading or int(size * 1.42)
    for i, row in enumerate(lines):
        txt(d, row, x, y + i * leading, size, fill, weight, anchor)


def center_txt(d, text, cx, cy, size=24, fill="ink", weight="medium"):
    d.text((SZ(cx), SZ(cy)), text, font=font(size, weight), fill=color(fill), anchor="mm")


def pill(d, xy, label, fill="mint", text_fill="wine", size=20, weight="bold"):
    box(d, xy, fill, radius=(xy[3] - xy[1]) / 2)
    center_txt(d, label, (xy[0] + xy[2]) / 2, (xy[1] + xy[3]) / 2, size, text_fill, weight)


def card(d, xy, fill="white", outline="line", radius=26, shadow=True):
    x0, y0, x1, y1 = xy
    if shadow:
        box(d, (x0, y0 + 5, x1, y1 + 5), "#F0E6E5", radius)
    box(d, xy, fill, radius, outline=outline, width=1)


def add_soft_decor(d, page):
    # Quiet rounded botanical shapes keep the layout lively without competing with copy.
    ellipse(d, (940, -112, 1175, 135), "mint")
    ellipse(d, (-118, 1110, 52, 1280), "rose")
    ellipse(d, (1008, 1130, 1150, 1272), "mint")
    # Tiny seed/dot detail.
    for x, y, r, col in [(1004, 202, 5, "mint2"), (1024, 224, 3, "wine3"),
                         (88, 1040, 4, "gold"), (970, 1160, 4, "jade")]:
        ellipse(d, (x - r, y - r, x + r, y + r), col)


def header(d, page, title, subtitle_lines=()):
    add_soft_decor(d, page)
    pill(d, (72, 48, 254, 94), f"اسلاید {page} از ۶", "mint", "wine", 18)
    txt(d, "راهنمای والدین  •  پوست و موی کودک", 1008, 59, 20, "wine2", "medium")
    # Accent dash beside the title.
    box(d, (986, 143, 1000, 214), "jade", radius=7)
    txt(d, title, 958, 137, 49, "wine", "extra")
    if isinstance(subtitle_lines, str):
        subtitle_lines = [subtitle_lines]
    txt_lines(d, list(subtitle_lines), 958, 211, 25, "muted", "regular", leading=35)
    box(d, (72, 293, 1008, 296), "line", radius=2)


def footer(d, page):
    # Progress runs right-to-left.
    box(d, (72, 1281, 1008, 1289), "line", radius=4)
    fill_w = 936 * page / 6
    box(d, (1008 - fill_w, 1281, 1008, 1289), "jade", radius=4)
    txt(d, "اطلاعات آموزشی؛ تشخیص با پزشک", 1008, 1300, 17, "muted", "regular")


def sparkle(d, cx, cy, r=14, fill="lime"):
    polygon(d, [(cx, cy-r), (cx+4, cy-4), (cx+r, cy), (cx+4, cy+4),
                (cx, cy+r), (cx-4, cy+4), (cx-r, cy), (cx-4, cy-4)], fill)


def icon_base(d, cx, cy, bg="mint", r=66):
    ellipse(d, (cx-r, cy-r, cx+r, cy+r), bg)


def icon_fungus(d, cx, cy):
    icon_base(d, cx, cy, "mint", 72)
    # Skin line and several hair shafts around a small irritated patch.
    line(d, [(cx-42, cy+25), (cx+42, cy+25)], "peach", 7)
    for dx, top in [(-33, -27), (-14, -40), (26, -33), (43, -16)]:
        line(d, [(cx+dx, cy+23), (cx+dx-3, cy+top)], "hair", 5)
    ellipse(d, (cx-10, cy-7, cx+20, cy+20), "rose2")
    for dx, dy, rr in [(-31, -29, 5), (20, -36, 5), (37, 6, 4)]:
        ellipse(d, (cx+dx-rr, cy+dy-rr, cx+dx+rr, cy+dy+rr), "wine3")


def icon_impetigo(d, cx, cy):
    icon_base(d, cx, cy, "rose", 72)
    ellipse(d, (cx-43, cy-30, cx+42, cy+34), "peach")
    ellipse(d, (cx-23, cy-25, cx+10, cy+4), "gold")
    ellipse(d, (cx-2, cy-6, cx+30, cy+22), "#E8BD63")
    ellipse(d, (cx+16, cy-28, cx+38, cy-6), "#F0D17C")
    ellipse(d, (cx-25, cy+7, cx-3, cy+27), "#F1D67E")
    # A few burgundy spots suggest a small irritated area, not a graphic wound.
    ellipse(d, (cx-39, cy-10, cx-30, cy-1), "wine3")
    ellipse(d, (cx+32, cy+27, cx+40, cy+35), "wine3")


def icon_follicle(d, cx, cy):
    icon_base(d, cx, cy, "mint", 72)
    line(d, [(cx-45, cy+29), (cx+45, cy+29)], "peach", 8)
    for dx, h in [(-28, 37), (0, 46), (29, 34)]:
        line(d, [(cx+dx, cy+26), (cx+dx+4, cy-h)], "hair", 5)
        ellipse(d, (cx+dx-8, cy+15, cx+dx+8, cy+31), "rose2")
    ellipse(d, (cx-7, cy+10, cx+9, cy+26), "red")


def icon_check(d, cx, cy, fill="jade"):
    ellipse(d, (cx-26, cy-26, cx+26, cy+26), fill)
    line(d, [(cx-13, cy), (cx-3, cy+10), (cx+15, cy-12)], "white", 6)


def icon_alert(d, cx, cy, bg="rose"):
    icon_base(d, cx, cy, bg, 51)
    polygon(d, [(cx, cy-30), (cx+30, cy+23), (cx-30, cy+23)], "wine2")
    line(d, [(cx, cy-12), (cx, cy+5)], "white", 5)
    ellipse(d, (cx-3, cy+11, cx+3, cy+17), "white")


def icon_magnifier(d, cx, cy, bg="mint", r=62):
    icon_base(d, cx, cy, bg, r)
    ellipse(d, (cx-29, cy-33, cx+14, cy+10), None, outline="wine2", width=5)
    line(d, [(cx+7, cy+7), (cx+33, cy+34)], "wine2", 7)
    ellipse(d, (cx-8, cy-13, cx+1, cy-4), "rose2")
    line(d, [(cx-20, cy+4), (cx-16, cy-12)], "hair", 3)
    line(d, [(cx+4, cy+2), (cx+9, cy-14)], "hair", 3)


def icon_swab(d, cx, cy, bg="mint"):
    icon_base(d, cx, cy, bg, 62)
    line(d, [(cx-28, cy+26), (cx+25, cy-28)], "jade", 6)
    ellipse(d, (cx-36, cy+19, cx-17, cy+39), "white", outline="jade", width=3)
    ellipse(d, (cx+18, cy-37, cx+38, cy-17), "white", outline="jade", width=3)
    sparkle(d, cx+25, cy+25, 10, "gold")


def icon_capsule(d, cx, cy, bg="mint"):
    icon_base(d, cx, cy, bg, 68)
    # Diagonal two-tone capsule.
    capsule = Image.new("RGBA", (SZ(98), SZ(52)), (0, 0, 0, 0))
    cd = ImageDraw.Draw(capsule)
    cd.rounded_rectangle((0, 0, SZ(98)-1, SZ(52)-1), radius=SZ(26), fill=color("white"), outline=color("wine2"), width=SZ(3))
    cd.rectangle((SZ(49), 0, SZ(98), SZ(52)), fill=color("wine3"))
    cd.rounded_rectangle((0, 0, SZ(98)-1, SZ(52)-1), radius=SZ(26), outline=color("wine2"), width=SZ(3))
    capsule = capsule.rotate(38, resample=Image.Resampling.BICUBIC, expand=True)
    d.image.alpha_composite(capsule, (SZ(cx)-capsule.width//2, SZ(cy)-capsule.height//2))
    line(d, [(cx-28, cy+33), (cx+23, cy+33)], "jade", 4)


def icon_bottle(d, cx, cy, bg="rose"):
    icon_base(d, cx, cy, bg, 68)
    box(d, (cx-25, cy-21, cx+25, cy+39), "white", radius=10, outline="wine2", width=3)
    box(d, (cx-15, cy-35, cx+15, cy-19), "wine2", radius=4)
    box(d, (cx-17, cy-2, cx+17, cy+13), "mint", radius=4)
    line(d, [(cx, cy), (cx, cy+11)], "jade", 3)
    line(d, [(cx-6, cy+5), (cx+6, cy+5)], "jade", 3)


def icon_wash(d, cx, cy, bg="mint"):
    icon_base(d, cx, cy, bg, 64)
    line(d, [(cx-37, cy-21), (cx+25, cy-21)], "jade", 5)
    line(d, [(cx+12, cy-21), (cx+25, cy-8), (cx+39, cy-8)], "jade", 5)
    # hand / flowing water
    line(d, [(cx-22, cy+4), (cx-7, cy-9), (cx+5, cy-2), (cx+16, cy-10), (cx+27, cy-2)], "wine2", 6)
    line(d, [(cx-13, cy+12), (cx+10, cy+18), (cx+29, cy+9)], "jade", 4)
    line(d, [(cx-19, cy+29), (cx-5, cy+34)], "jade", 3)
    line(d, [(cx+8, cy+30), (cx+23, cy+35)], "jade", 3)


def icon_comb(d, cx, cy, bg="mint"):
    icon_base(d, cx, cy, bg, 64)
    box(d, (cx-36, cy-16, cx+37, cy+6), "wine2", radius=7)
    for dx in range(-29, 34, 12):
        line(d, [(cx+dx, cy+5), (cx+dx, cy+26)], "wine2", 3)
    line(d, [(cx-35, cy-22), (cx-25, cy-32)], "gold", 4)
    line(d, [(cx+28, cy-25), (cx+36, cy-31)], "gold", 4)


def icon_towel(d, cx, cy, bg="rose"):
    icon_base(d, cx, cy, bg, 64)
    box(d, (cx-37, cy-31, cx+37, cy+31), "white", radius=12, outline="wine2", width=3)
    line(d, [(cx-25, cy-14), (cx+25, cy-14)], "mint2", 4)
    line(d, [(cx-25, cy+1), (cx+25, cy+1)], "mint2", 4)
    line(d, [(cx-25, cy+16), (cx+10, cy+16)], "mint2", 4)


def draw_child_art(d, cx, cy):
    # Soft round backdrop.
    ellipse(d, (cx-230, cy-235, cx+230, cy+225), "mint")
    ellipse(d, (cx-170, cy-178, cx+170, cy+175), "hair")
    # Ears, neck, face, and friendly facial features.
    ellipse(d, (cx-142, cy-23, cx-103, cy+40), "skin")
    ellipse(d, (cx+103, cy-23, cx+142, cy+40), "skin")
    box(d, (cx-39, cy+92, cx+39, cy+171), "skin", radius=18)
    ellipse(d, (cx-164, cy+116, cx+164, cy+366), "jade")
    ellipse(d, (cx-118, cy-128, cx+118, cy+139), "skin")
    # Hair cap and soft fringe.
    ellipse(d, (cx-149, cy-158, cx+149, cy-48), "hair")
    for x, y, r in [(-115, -102, 26), (-62, -123, 25), (-4, -130, 25), (53, -119, 27), (105, -94, 25)]:
        ellipse(d, (cx+x-r, cy+y-r, cx+x+r, cy+y+r), "hair")
    # Eyes and smile.
    ellipse(d, (cx-52, cy+5, cx-39, cy+18), "wine")
    ellipse(d, (cx+39, cy+5, cx+52, cy+18), "wine")
    line(d, [(cx-27, cy+61), (cx-8, cy+74), (cx+11, cy+74), (cx+30, cy+61)], "wine2", 4)
    # Magnifier bubble showing a small patch of irritated scalp and hair.
    ellipse(d, (cx+98, cy-120, cx+294, cy+76), "paper", outline="jade", width=8)
    ellipse(d, (cx+127, cy-91, cx+265, cy+48), "peach")
    for dx, dy in [(-25, -20), (5, -33), (34, -9), (55, 21), (-6, 35)]:
        line(d, [(cx+195+dx, cy-8+dy), (cx+199+dx, cy-27+dy)], "hair", 4)
    ellipse(d, (cx+177, cy-23, cx+222, cy+20), "rose2")
    ellipse(d, (cx+187, cy-10, cx+194, cy-3), "wine3")
    # Magnifier handle.
    line(d, [(cx+266, cy+62), (cx+322, cy+116)], "jade", 13)
    ellipse(d, (cx+291, cy+95, cx+330, cy+134), "jade")
    sparkle(d, cx-210, cy-158, 15, "gold")
    sparkle(d, cx+188, cy+194, 12, "lime")


def slide1():
    # Rich burgundy gradient with fresh mojito accents.
    top, bottom = np.array(color("wine")), np.array(color("wine2"))
    arr = np.empty((SZ(H), SZ(W), 3), dtype=np.uint8)
    for y in range(SZ(H)):
        t = y / max(1, SZ(H)-1)
        arr[y, :, :] = (top * (1-t) + bottom * t).astype(np.uint8)
    im = Image.fromarray(arr, "RGB").convert("RGBA")
    d = FD(im)
    ellipse(d, (880, -270, 1240, 90), "mint2")
    ellipse(d, (-135, 490, 55, 680), "wine3")
    pill(d, (72, 56, 421, 108), "راهنمای والدین  •  پوست و موی کودک", "mint", "wine", 19)
    txt(d, "پوسته؟ دلمه؟ یا جوش چرکی؟", 1008, 174, 28, "lime", "medium")
    txt_lines(d, ["زخم‌های عفونی", "پوست سر", "در کودکان"], 1008, 234, 69, "white", "extra", leading=91)
    txt_lines(d, ["از علت‌های شایع تا زمانِ مراجعه؛", "۶ نکتهٔ روشن و کاربردی برای والدین."],
              1008, 523, 27, "#F4E7E9", "regular", leading=41)
    # Hero panel.
    box(d, (72, 650, 1008, 1270), "cream", radius=38)
    # Friendly child + magnified scalp illustration.
    draw_child_art(d, 430, 899)
    pill(d, (693, 1115, 962, 1170), "تشخیص زودهنگام مهم است", "lime", "wine", 19)
    txt(d, "نه هر پوسته‌ای قارچ است؛ علت را پزشک مشخص می‌کند.", 1008, 1188, 18, "wine2", "medium")
    box(d, (72, 1280, 1008, 1288), "#9B6077", radius=4)
    box(d, (72, 1280, 228, 1288), "lime", radius=4)
    center_txt(d, "ورق بزنید  ←", 170, 1315, 19, "white", "medium")
    center_txt(d, "۱ از ۶", 928, 1315, 18, "#F4E7E9", "medium")
    return im


def slide2():
    im, d = new_slide()
    header(d, 2, "چند علتِ شایع", ["نشانه‌ها راهنما هستند، اما تشخیص با معاینه است."])
    rows = [
        (331, "قارچِ پوست سر", ["لکهٔ خارش‌دار و پوسته‌دار؛", "گاهی موی شکسته یا ریزشِ تکه‌ای."], icon_fungus),
        (572, "زردزخم (عفونت باکتریایی)", ["زخم یا تاولِ ترشح‌دار که ممکن است", "دلمهٔ زردِ عسلی ببندد."], icon_impetigo),
        (813, "فولیکولیت یا زخمِ عفونی", ["جوش‌های چرکی کنار ریشهٔ مو،", "یا زخمِ قرمز و دردناکِ رو به گسترش."], icon_follicle),
    ]
    for y, title, lines, icon in rows:
        card(d, (72, y, 1008, y+220), "white", "line", 25)
        icon(d, 177, y+110)
        txt(d, title, 925, y+37, 31, "wine", "bold")
        txt_lines(d, lines, 925, y+96, 26, "ink", "regular", leading=39)
    box(d, (72, 1061, 1008, 1181), "mint", radius=26)
    icon_alert(d, 927, 1121, "lime")
    txt(d, "ظاهرِ ضایعه به‌تنهایی تشخیص قطعی نمی‌دهد.", 842, 1095, 25, "jade_dark", "bold")
    txt(d, "علت‌های دیگری هم ممکن است مطرح باشند.", 842, 1136, 22, "jade_dark", "regular")
    footer(d, 2)
    return im


def slide3():
    im, d = new_slide()
    header(d, 3, "چه زمانی پیگیری کنیم؟", ["این نشانه‌ها را جدی بگیرید و درمان را عقب نیندازید."])
    signs = [
        (329, "تب، ترشح چرکی یا قرمزیِ در حال گسترش"),
        (458, "درد یا ورم که بیشتر می‌شود"),
        (587, "پوسته‌ریزی همراه موی شکسته یا ریزشِ تکه‌ای"),
    ]
    for y, text in signs:
        card(d, (72, y, 1008, y+112), "white", "line", 22)
        icon_check(d, 164, y+56, "jade")
        txt(d, text, 925, y+37, 27, "ink", "medium")
    box(d, (72, 725, 1008, 951), "rose", radius=28)
    icon_alert(d, 906, 793, "white")
    txt(d, "تورمِ نرم و دردناکِ پوست سر", 811, 762, 28, "wine", "bold")
    txt_lines(d, ["ممکن است نشانهٔ عفونتِ شدیدتر باشد؛", "برای ارزیابی زودهنگام با پزشک تماس بگیرید."],
              811, 816, 23, "wine2", "regular", leading=37)
    # A subtle hair/scalp mark on the left.
    ellipse(d, (165, 773, 310, 918), "white")
    line(d, [(197, 876), (202, 827)], "hair", 6)
    line(d, [(231, 876), (237, 816)], "hair", 6)
    line(d, [(268, 876), (265, 834)], "hair", 6)
    ellipse(d, (215, 843, 254, 882), "rose2")
    box(d, (72, 978, 1008, 1187), "wine", radius=28)
    pill(d, (748, 1002, 970, 1051), "فوری مراجعه کنید", "lime", "wine", 18)
    txt_lines(d, ["اگر کودک بدحال است یا رگهٔ قرمز روی پوست", "می‌بینید، فوراً پیگیری پزشکی کنید."],
              954, 1073, 25, "white", "medium", leading=40)
    footer(d, 3)
    return im


def slide4():
    im, d = new_slide()
    header(d, 4, "تشخیص با معاینه شروع می‌شود", ["چند مشکلِ پوست سر ممکن است ظاهری شبیه هم داشته باشند."])
    steps = [
        (341, "۱", ["پزشک پوست سر و موها", "را بررسی می‌کند."], icon_magnifier),
        (529, "۲", ["در صورت نیاز، از مو، پوسته", "یا ترشح نمونه می‌گیرد."], icon_swab),
        (717, "۳", ["علت را مشخص می‌کند تا", "درمان مناسب انتخاب شود."], icon_bottle),
    ]
    for y, n, lines, icon in steps:
        card(d, (72, y, 1008, y+166), "white", "line", 24)
        icon(d, 174, y+83)
        ellipse(d, (286, y+49, 354, y+117), "mint")
        center_txt(d, n, 320, y+83, 30, "jade_dark", "bold")
        txt_lines(d, lines, 925, y+49, 23, "ink", "medium", leading=35)
    box(d, (72, 909, 1008, 1187), "wine", radius=28)
    icon_magnifier(d, 196, 1045, "mint", 73)
    txt_lines(d, ["خارش یا پوسته‌ریزی به‌تنهایی", "قارچ را ثابت نمی‌کند."],
              928, 967, 29, "white", "bold", leading=45)
    txt(d, "اگر شک دارید، برای معاینه وقت بگیرید.", 928, 1075, 23, "#F3E6E9", "regular")
    pill(d, (693, 1124, 952, 1168), "تشخیصِ درست = درمانِ درست", "lime", "wine", 17)
    footer(d, 4)
    return im


def slide5():
    im, d = new_slide()
    header(d, 5, "درمان به علت بستگی دارد", ["برای عفونتِ پوست سر، یک درمانِ واحد وجود ندارد."])
    card(d, (72, 338, 1008, 632), "white", "line", 28)
    icon_capsule(d, 177, 477, "mint")
    pill(d, (686, 365, 935, 414), "قارچِ پوست سر", "mint", "jade_dark", 20)
    txt_lines(d, ["معمولاً به داروی ضدقارچِ خوراکیِ", "نسخه‌ای نیاز دارد؛ کرم یا شامپو", "به‌تنهایی درمانش نمی‌کند."],
              925, 438, 25, "ink", "regular", leading=39)
    card(d, (72, 654, 1008, 927), "white", "line", 28)
    icon_bottle(d, 177, 790, "rose")
    pill(d, (632, 680, 935, 729), "زردزخمِ باکتریایی", "rose", "wine", 20)
    txt_lines(d, ["پزشک با توجه به تعداد و شدتِ", "ضایعه‌ها، درمان موضعی یا خوراکی", "را انتخاب می‌کند."],
              925, 752, 25, "ink", "regular", leading=39)
    box(d, (72, 951, 1008, 1187), "rose", radius=28)
    icon_alert(d, 164, 1064, "white")
    txt(d, "خوددرمانی نکنید", 925, 979, 27, "wine", "bold")
    txt_lines(d, ["کرمِ کورتونی یا داروی باقی‌مانده را", "بدون نظر پزشک استفاده نکنید؛", "کورتون می‌تواند قارچِ احتمالی را بدتر کند."],
              925, 1024, 23, "wine2", "regular", leading=36)
    footer(d, 5)
    return im


def slide6():
    im, d = new_slide()
    header(d, 6, "تا ویزیت چه کار کنیم؟", ["چند قدمِ امن برای مراقبت و کاهشِ پخش عفونت."])
    rows = [
        (337, "زخم را آرام با آب و صابون تمیز کنید؛", "دلمه را نکنید و محل را نخارانید.", icon_wash),
        (533, "بعد از تماس دست‌ها را بشویید؛", "ناخن‌ها را کوتاه نگه دارید.", icon_check),
        (729, "شانه، کلاه، حوله و روبالشی را", "مشترک نکنید؛ وسایل را تمیز کنید.", icon_comb),
    ]
    for y, line1, line2, icon in rows:
        card(d, (72, y, 1008, y+176), "white", "line", 24)
        icon(d, 174, y+88)
        txt_lines(d, [line1, line2], 925, y+49, 24, "ink", "medium", leading=39)
    box(d, (72, 939, 1008, 1208), "wine", radius=30)
    sparkle(d, 160, 1001, 18, "lime")
    txt_lines(d, ["ذخیره کن و برای والدینی بفرست", "که مراقب سلامت پوست‌وموی کودک‌اند."],
              925, 970, 27, "white", "bold", leading=45)
    pill(d, (682, 1078, 950, 1129), "این پست جای معاینه نیست", "lime", "wine", 18)
    txt(d, "اگر نشانهٔ هشدار هست، با پزشک کودک تماس بگیرید.", 925, 1150, 20, "#F3E6E9", "regular")
    footer(d, 6)
    return im


def flatten(im):
    if im.mode == "RGBA":
        bg = Image.new("RGBA", im.size, (*color("cream"), 255))
        bg.alpha_composite(im)
        im = bg.convert("RGB")
    else:
        im = im.convert("RGB")
    if im.size != (SZ(W), SZ(H)):
        raise ValueError(f"Unexpected slide size {im.size}")
    return im.resize((W, H), Image.Resampling.LANCZOS)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    pages = [slide1(), slide2(), slide3(), slide4(), slide5(), slide6()]
    images = []
    for i, im in enumerate(pages, start=1):
        final = flatten(im)
        name = f"slide_{i:02d}.png"
        final.save(OUT / name, format="PNG", optimize=True)
        images.append(final)
    images[0].save(OUT / "carousel.pdf", "PDF", save_all=True,
                   append_images=images[1:], resolution=150, quality=92)
    bundle = OUT / "carousel_assets.zip"
    with zipfile.ZipFile(bundle, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for p in sorted(OUT.glob("slide_*.png")):
            zf.write(p, arcname=p.name)
        for extra in ("caption.txt", "sources.txt", "README.md"):
            p = OUT / extra
            if p.exists():
                zf.write(p, arcname=p.name)
    print(f"Created {len(images)} slides at {W}x{H}")
    for p in sorted(OUT.glob("slide_*.png")):
        print(f"{p.name}: {p.stat().st_size:,} bytes")
    print(f"PDF: {(OUT / 'carousel.pdf').stat().st_size:,} bytes")
    print(f"ZIP: {bundle.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()

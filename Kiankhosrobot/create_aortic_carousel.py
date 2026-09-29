from __future__ import annotations

"""Create a high-contrast Persian Instagram carousel about aortic dissection.

Output: 1080x1350 PNG slides (4:5), a contact-sheet preview, and caption.
The palette deliberately follows the brief: phosphor green, signal red, and mustard.
"""

import math
import os
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parent
TOOLKIT = ROOT / "toolkit"
sys.path.insert(0, str(TOOLKIT))
from fatext import FD  # type: ignore

S = 2
W, H = 1080 * S, 1350 * S
OUT = ROOT / "aortic_dissection_carousel"
FONT_DIR = ROOT.parent / "fonttmp" / "fonts" / "ttf"

# Brief palette: neon phosphor green + red + mustard, grounded by warm black.
BG = (9, 12, 10)
BG2 = (15, 20, 15)
PAPER = (246, 241, 223)
MUTED = (184, 187, 166)
GREEN = (190, 255, 0)
GREEN_DARK = (43, 74, 12)
RED = (255, 61, 78)
RED_DARK = (92, 21, 31)
MUSTARD = (218, 167, 37)
MUSTARD_LIGHT = (247, 205, 81)
INK = (16, 19, 14)


def sc(v: float) -> int:
    return int(round(v * S))


def font(name: str, size: int):
    path = FONT_DIR / name
    return ImageFont.truetype(str(path), sc(size))


F_REG = "Vazirmatn-Regular.ttf"
F_MED = "Vazirmatn-Medium.ttf"
F_SEMI = "Vazirmatn-SemiBold.ttf"
F_BOLD = "Vazirmatn-Bold.ttf"
F_BLACK = "Vazirmatn-Black.ttf"


def rgba(c, a=255):
    return (*c, a)


def overlay_grid(im: Image.Image, accent=GREEN):
    d = ImageDraw.Draw(im, "RGBA")
    # A restrained technical grid keeps the medical/editorial look without reducing readability.
    for x in range(0, W + 1, sc(72)):
        d.line((x, 0, x, H), fill=rgba(accent, 10), width=sc(1))
    for y in range(0, H + 1, sc(72)):
        d.line((0, y, W, y), fill=rgba(accent, 10), width=sc(1))
    for x, y, r in [(72, 100, 2), (1000, 240, 2), (160, 1130, 3), (930, 1180, 2)]:
        d.ellipse((sc(x-r), sc(y-r), sc(x+r), sc(y+r)), fill=rgba(accent, 140))


def text(im, xy, value, size, fill=PAPER, family=F_REG, anchor="rt"):
    # fatext shapes Persian correctly even on systems without libraqm.
    d = FD(im)
    return d.text((sc(xy[0]), sc(xy[1])), value, font=font(family, size), fill=fill, anchor=anchor)


def line(d, points, fill, width=2, joint="curve"):
    d.line([(sc(x), sc(y)) for x, y in points], fill=fill, width=sc(width), joint=joint)


def ellipse(d, box, fill=None, outline=None, width=1):
    box = tuple(sc(v) for v in box)
    d.ellipse(box, fill=fill, outline=outline, width=sc(width) if outline else 1)


def rect(d, box, fill=None, outline=None, width=1, radius=0):
    box = tuple(sc(v) for v in box)
    d.rounded_rectangle(box, radius=sc(radius), fill=fill, outline=outline,
                        width=sc(width) if outline else 1)


def arc(d, box, start, end, fill, width=2):
    d.arc(tuple(sc(v) for v in box), start, end, fill=fill, width=sc(width))


def draw_brand(im, page: int, label="CARDIO / EMERGENCY"):
    d = ImageDraw.Draw(im, "RGBA")
    # Page marker is deliberately left aligned so it does not fight RTL headlines.
    text(im, (74, 68), f"{page:02d} / 07", 17, GREEN, F_BOLD, "la")
    text(im, (1006, 68), label, 14, MUSTARD_LIGHT, F_BOLD, "ra")
    line(d, [(74, 100), (1006, 100)], rgba(PAPER, 46), 1)
    # Bottom signature
    line(d, [(74, 1285), (240, 1285)], rgba(RED, 160), 3)
    text(im, (260, 1276), "آموزش پزشکی | قلب و عروق", 14, MUTED, F_REG, "la")


def draw_corner_accent(im, color=GREEN):
    d = ImageDraw.Draw(im, "RGBA")
    line(d, [(966, 108), (1006, 108), (1006, 148)], rgba(color, 230), 4)
    line(d, [(74, 1202), (74, 1242), (114, 1242)], rgba(RED, 220), 4)


def draw_aorta_cross_section(im, cx, cy, r=184, tear=True):
    """Stylised, clearly labelled cross-section: wall / lumen / false lumen / intimal flap."""
    d = ImageDraw.Draw(im, "RGBA")
    # glow
    for rr, alpha in [(r + 24, 12), (r + 13, 18)]:
        ellipse(d, (cx - rr, cy - rr, cx + rr, cy + rr), fill=rgba(GREEN, alpha))
    ellipse(d, (cx-r, cy-r, cx+r, cy+r), fill=rgba(MUSTARD, 255))
    ellipse(d, (cx-r+20, cy-r+20, cx+r-20, cy+r-20), fill=rgba(RED, 235))
    ellipse(d, (cx-r+54, cy-r+54, cx+r-54, cy+r-54), fill=rgba(BG, 255))
    # true lumen
    ellipse(d, (cx-72, cy-92, cx+62, cy+88), fill=rgba(GREEN, 242))
    ellipse(d, (cx-56, cy-76, cx+48, cy+72), fill=rgba((36, 57, 15), 255))
    # false lumen, separated from true lumen by a jagged intimal flap
    if tear:
        pts = [(cx+8, cy-r+55), (cx+30, cy-96), (cx+80, cy-42), (cx+53, cy+12),
               (cx+88, cy+65), (cx+28, cy+106), (cx+8, cy+78), (cx+20, cy+18),
               (cx-2, cy-38)]
        d.polygon([(sc(x), sc(y)) for x, y in pts], fill=rgba(RED, 255))
        line(d, pts + [pts[0]], rgba(MUSTARD_LIGHT, 255), 4)
        # small crack at intima
        line(d, [(cx+6, cy-8), (cx-2, cy+12), (cx+8, cy+27)], rgba(PAPER, 245), 4)


def draw_aorta_tube(im, cx=540, cy=455, scale=1.0):
    """A simple anterior-view vessel map for the cover and treatment slide."""
    d = ImageDraw.Draw(im, "RGBA")
    def p(x, y): return (cx + x * scale, cy + y * scale)
    # thoracic silhouette, abstract not anatomical photography
    line(d, [p(-190, 270), p(-164, 110), p(-118, -8), p(-104, -148), p(-74, -235)], rgba(PAPER, 45), 3)
    line(d, [p(190, 270), p(164, 110), p(118, -8), p(104, -148), p(74, -235)], rgba(PAPER, 45), 3)
    # arterial route: mustard under-stroke, green inner stroke
    pts = [p(-8, 190), p(-8, 40), p(18, -100), p(48, -170), p(28, -230),
           p(-18, -254), p(-66, -236), p(-108, -204)]
    line(d, pts, rgba(MUSTARD, 230), 32)
    line(d, pts, rgba(GREEN, 255), 20)
    # arch branches
    for off in [-26, 6, 37]:
        line(d, [p(off, -222), p(off-10, -286), p(off-5, -333)], rgba(GREEN, 255), 13)
    # red dissection track on descending aorta
    red_pts = [p(-10, 32), p(22, -16), p(43, -79), p(43, -142), p(20, -184)]
    line(d, red_pts, rgba(RED, 255), 12)
    ellipse(d, (cx-38*scale, cy-268*scale, cx-20*scale, cy-250*scale), fill=rgba(RED, 255))


def label_box(im, xy, value, color=GREEN, size=18):
    d = ImageDraw.Draw(im, "RGBA")
    x, y = xy
    # determine rough width from plain character count, enough for a decorative pill
    w = max(112, len(value) * 10 + 34)
    rect(d, (x, y, x+w, y+36), fill=rgba(color, 24), outline=rgba(color, 210), width=1, radius=18)
    text(im, (x+w/2, y+18), value, size, color, F_BOLD, "mm")


def base(page, label="CARDIO / EMERGENCY"):
    im = Image.new("RGBA", (W, H), rgba(BG))
    overlay_grid(im)
    draw_brand(im, page, label)
    draw_corner_accent(im)
    return im


def slide_1():
    im = base(1)
    d = ImageDraw.Draw(im, "RGBA")
    # red-to-mustard block as the visual hook
    rect(d, (74, 150, 1006, 1136), fill=rgba((18, 24, 17), 230), outline=rgba(GREEN, 75), width=1, radius=28)
    rect(d, (74, 150, 258, 1136), fill=rgba(RED, 226), radius=28)
    rect(d, (220, 150, 258, 1136), fill=rgba(RED, 226))
    # diagram sits on the left stripe, giving the eye an immediate anatomy cue
    draw_aorta_tube(im, cx=172, cy=700, scale=1.08)
    # headline area
    label_box(im, (330, 218), "اورژانس عروقی", RED, 17)
    text(im, (956, 330), "دیسکسیون", 79, PAPER, F_BLACK, "rt")
    text(im, (956, 430), "آئورت", 102, GREEN, F_BLACK, "rt")
    text(im, (956, 570), "AORTIC DISSECTION", 25, MUSTARD_LIGHT, F_BOLD, "rt")
    line(d, [(610, 624), (956, 624)], rgba(RED, 235), 5)
    text(im, (956, 694), "وقتی خون به لایه‌های دیوارهٔ آئورت راه پیدا می‌کند…", 26, PAPER, F_SEMI, "rt")
    text(im, (956, 752), "زمان مهم است.", 33, MUSTARD_LIGHT, F_BLACK, "rt")
    # bottom information block
    rect(d, (330, 866, 956, 1034), fill=rgba(BG, 210), outline=rgba(MUSTARD, 170), width=2, radius=18)
    text(im, (914, 908), "این پست را ورق بزن", 24, GREEN, F_BOLD, "rt")
    text(im, (914, 969), "علائم  •  تشخیص  •  درمان", 20, PAPER, F_REG, "rt")
    text(im, (956, 1100), "آگاهی، جایگزین تشخیص نیست؛ اما می‌تواند نجات‌بخش باشد.", 17, MUTED, F_REG, "rt")
    return im


def slide_2():
    im = base(2)
    d = ImageDraw.Draw(im, "RGBA")
    text(im, (956, 180), "دیسکسیون آئورت چیست؟", 48, PAPER, F_BLACK, "rt")
    text(im, (956, 245), "WHAT HAPPENS?", 18, MUSTARD_LIGHT, F_BOLD, "rt")
    line(d, [(74, 300), (1006, 300)], rgba(GREEN, 130), 3)
    draw_aorta_cross_section(im, 430, 694, 208)
    # callouts with Arabic-compatible Persian text
    rect(d, (690, 388, 956, 487), fill=rgba(RED, 33), outline=rgba(RED, 220), width=2, radius=16)
    text(im, (932, 416), "کانال کاذب", 22, RED, F_BOLD, "rt")
    text(im, (932, 458), "خون بین لایه‌ها", 17, PAPER, F_REG, "rt")
    line(d, [(690, 438), (606, 515)], rgba(RED, 220), 2)
    rect(d, (690, 702, 956, 800), fill=rgba(GREEN, 25), outline=rgba(GREEN, 205), width=2, radius=16)
    text(im, (932, 730), "لایهٔ داخلی پاره‌شده", 20, GREEN, F_BOLD, "rt")
    text(im, (932, 773), "فلپ اینتیما", 16, PAPER, F_REG, "rt")
    line(d, [(690, 750), (526, 687)], rgba(GREEN, 220), 2)
    # body copy card
    rect(d, (74, 1010, 1006, 1168), fill=rgba((28, 35, 25), 220), outline=rgba(MUSTARD, 130), width=1, radius=18)
    text(im, (950, 1050), "یک پارگی در لایهٔ داخلی آئورت ایجاد می‌شود.", 23, PAPER, F_SEMI, "rt")
    text(im, (950, 1110), "خون وارد دیواره می‌شود و بین لایه‌ها پیش می‌رود.", 21, MUTED, F_REG, "rt")
    return im


def draw_warning_icon(d, cx, cy, r=42):
    pts = [(cx, cy-r), (cx+r, cy+r*0.72), (cx-r, cy+r*0.72)]
    d.polygon([(sc(x), sc(y)) for x, y in pts], fill=rgba(RED, 230))
    line(d, [(cx, cy-r*0.43), (cx, cy+r*0.22)], rgba(INK, 255), 7)
    ellipse(d, (cx-4, cy+r*0.31, cx+4, cy+r*0.47), fill=rgba(INK, 255))


def slide_3():
    im = base(3)
    d = ImageDraw.Draw(im, "RGBA")
    text(im, (956, 180), "علائم هشدار را بشناس", 48, PAPER, F_BLACK, "rt")
    text(im, (956, 245), "RED FLAGS", 18, RED, F_BOLD, "rt")
    rect(d, (74, 330, 1006, 502), fill=rgba(RED, 205), radius=22)
    draw_warning_icon(d, 140, 416, 48)
    text(im, (900, 365), "درد ناگهانی و بسیار شدید", 30, INK, F_BLACK, "rt")
    text(im, (900, 428), "در قفسه‌سینه یا پشت", 27, INK, F_BOLD, "rt")
    text(im, (900, 475), "ممکن است درد جابه‌جا شود.", 17, (55, 23, 20), F_REG, "rt")
    items = [
        ("غش یا تنگی نفس", "ممکن است ناگهانی شروع شود.", GREEN),
        ("ضعف یا اختلال تکلم", "درگیری جریان خون مغز را جدی بگیر.", MUSTARD_LIGHT),
        ("تفاوت نبض یا فشار دو دست", "همیشه وجود ندارد؛ اما مهم است.", GREEN),
    ]
    ys = [590, 780, 970]
    for (title, desc, color), y in zip(items, ys):
        rect(d, (74, y, 1006, y+142), fill=rgba((26, 31, 24), 235), outline=rgba(color, 140), width=2, radius=18)
        ellipse(d, (111, y+43, 143, y+75), fill=rgba(color, 255))
        text(im, (190, y+42), title, 25, color, F_BOLD, "lt")
        text(im, (190, y+90), desc, 18, PAPER, F_REG, "lt")
    text(im, (956, 1193), "این علائم همیشه همه‌باهم دیده نمی‌شوند.", 17, MUTED, F_REG, "rt")
    return im


def slide_4():
    im = base(4)
    d = ImageDraw.Draw(im, "RGBA")
    text(im, (956, 180), "چه کسانی بیشتر در خطرند؟", 46, PAPER, F_BLACK, "rt")
    text(im, (956, 245), "RISK FACTORS", 18, MUSTARD_LIGHT, F_BOLD, "rt")
    # left visual: a vessel with pressure arrows
    rect(d, (74, 354, 374, 1058), fill=rgba((24, 31, 21), 230), outline=rgba(GREEN, 90), width=1, radius=26)
    draw_aorta_tube(im, cx=222, cy=710, scale=0.76)
    for y in [500, 630, 760, 890]:
        line(d, [(105, y), (175, y)], rgba(RED, 200), 4)
        d.polygon([(sc(175), sc(y)), (sc(157), sc(y-9)), (sc(157), sc(y+9))], fill=rgba(RED, 210))
    text(im, (224, 1000), "فشار بالا", 24, RED, F_BLACK, "mm")
    factors = [
        ("فشارخون کنترل‌نشده", "مهم‌ترین عامل قابل‌اصلاح", RED),
        ("بیماری‌های بافت همبند", "مثل سندرم مارفان", GREEN),
        ("دریچهٔ آئورت دولتی", "Bicuspid aortic valve", MUSTARD_LIGHT),
        ("سابقهٔ آنوریسم یا جراحی آئورت", "یا ضربهٔ شدید به قفسه‌سینه", GREEN),
    ]
    ys = [382, 548, 714, 880]
    for (title, desc, color), y in zip(factors, ys):
        ellipse(d, (438, y+7, 466, y+35), fill=rgba(color, 255))
        text(im, (504, y), title, 24, color, F_BOLD, "lt")
        text(im, (504, y+47), desc, 17, MUTED, F_REG, "lt")
        line(d, [(438, y+86), (956, y+86)], rgba(PAPER, 35), 1)
    rect(d, (438, 1030, 956, 1124), fill=rgba(MUSTARD, 22), outline=rgba(MUSTARD, 145), width=1, radius=15)
    text(im, (930, 1062), "گاهی بدون عامل خطر شناخته‌شده هم رخ می‌دهد.", 18, MUSTARD_LIGHT, F_SEMI, "rt")
    return im


def slide_5():
    im = base(5)
    d = ImageDraw.Draw(im, "RGBA")
    text(im, (956, 180), "تشخیص چگونه انجام می‌شود؟", 46, PAPER, F_BLACK, "rt")
    text(im, (956, 245), "DIAGNOSIS", 18, GREEN, F_BOLD, "rt")
    # CT scan inspired circle and slices
    rect(d, (74, 362, 356, 1052), fill=rgba((23, 29, 21), 240), outline=rgba(MUSTARD, 100), width=1, radius=26)
    ellipse(d, (105, 484, 325, 704), fill=rgba(MUSTARD, 230))
    ellipse(d, (124, 503, 306, 685), fill=rgba(BG, 255))
    ellipse(d, (164, 543, 270, 649), fill=rgba(GREEN, 190))
    ellipse(d, (188, 567, 246, 625), fill=rgba(BG, 255))
    arc(d, (104, 483, 326, 705), 40, 220, rgba(RED, 255), 8)
    for y in [785, 835, 885]:
        line(d, [(112, y), (320, y)], rgba(GREEN, 90), 2)
    text(im, (215, 968), "CT / CTA", 28, GREEN, F_BLACK, "mm")
    text(im, (215, 1018), "سریع و پرکاربرد", 17, PAPER, F_REG, "mm")
    cards = [
        ("CT آنژیوگرافی", "در بسیاری از بیماران، انتخاب سریع و پرکاربرد است.", GREEN),
        ("اکوی قلب از راه مری یا MRI", "در شرایط و بیماران منتخب، جایگزین یا مکمل.", MUSTARD_LIGHT),
        ("ECG و آزمایش خون کافی نیستند", "طبیعی بودن آن‌ها به‌تنهایی تشخیص را رد نمی‌کند.", RED),
    ]
    ys = [384, 622, 860]
    for (title, desc, color), y in zip(cards, ys):
        rect(d, (430, y, 1006, y+176), fill=rgba((24, 30, 22), 235), outline=rgba(color, 150), width=2, radius=18)
        rect(d, (430, y, 450, y+176), fill=rgba(color, 230), radius=9)
        text(im, (948, y+37), title, 25, color, F_BOLD, "rt")
        text(im, (948, y+97), desc, 18, PAPER, F_REG, "rt")
    text(im, (956, 1158), "تصمیم‌گیری با معاینه و تصویربرداری فوری پزشکی انجام می‌شود.", 17, MUTED, F_REG, "rt")
    return im


def slide_6():
    im = base(6)
    d = ImageDraw.Draw(im, "RGBA")
    text(im, (956, 180), "درمان، وابسته به محل درگیری", 44, PAPER, F_BLACK, "rt")
    text(im, (956, 245), "TREATMENT", 18, RED, F_BOLD, "rt")
    # vertical split
    rect(d, (74, 354, 522, 1038), fill=rgba(RED, 27), outline=rgba(RED, 170), width=2, radius=22)
    rect(d, (558, 354, 1006, 1038), fill=rgba(GREEN, 22), outline=rgba(GREEN, 170), width=2, radius=22)
    text(im, (476, 405), "STANFORD A", 22, RED, F_BLACK, "rt")
    text(im, (476, 468), "آئورت صعودی", 30, PAPER, F_BLACK, "rt")
    text(im, (476, 548), "معمولاً به جراحی فوری نیاز دارد.", 23, PAPER, F_SEMI, "rt")
    line(d, [(122, 656), (476, 656)], rgba(RED, 190), 3)
    for i, t in enumerate(["درگیری نزدیک قلب", "خطر آسیب به دریچه و عروق", "ارزیابی فوری تیم تخصصی"]):
        ellipse(d, (125, 720+i*77, 151, 746+i*77), fill=rgba(RED, 255))
        text(im, (182, 718+i*77), t, 19, PAPER, F_REG, "lt")
    text(im, (960, 405), "STANFORD B", 22, GREEN, F_BLACK, "rt")
    text(im, (960, 468), "بدون درگیری آئورت صعودی", 27, PAPER, F_BLACK, "rt")
    text(im, (960, 548), "کنترل فشار و ضربان؛", 23, PAPER, F_SEMI, "rt")
    text(im, (960, 590), "مداخله اگر عارضه‌دار باشد.", 23, GREEN, F_SEMI, "rt")
    line(d, [(604, 656), (960, 656)], rgba(GREEN, 190), 3)
    for i, t in enumerate(["دارو و پایش دقیق", "بررسی خون‌رسانی اندام‌ها", "مداخله در موارد پیچیده"]):
        ellipse(d, (607, 720+i*77, 633, 746+i*77), fill=rgba(GREEN, 255))
        text(im, (664, 718+i*77), t, 19, PAPER, F_REG, "lt")
    rect(d, (74, 1090, 1006, 1166), fill=rgba(MUSTARD, 24), outline=rgba(MUSTARD, 160), width=1, radius=14)
    text(im, (956, 1115), "خوددرمانی یا صبر کردن، خطرناک است.", 21, MUSTARD_LIGHT, F_BOLD, "rt")
    return im


def slide_7():
    im = base(7, "SAVE / SHARE / ACT")
    d = ImageDraw.Draw(im, "RGBA")
    # final call-to-action uses the brief palette as a strong signal rather than a busy card.
    rect(d, (74, 164, 1006, 1086), fill=rgba((18, 23, 17), 240), outline=rgba(GREEN, 110), width=2, radius=28)
    ellipse(d, (710, 238, 942, 470), fill=rgba(RED, 232))
    # simplified pulse / tear mark
    line(d, [(745, 354), (790, 354), (815, 306), (848, 408), (873, 354), (912, 354)], rgba(INK, 255), 10)
    text(im, (948, 588), "درد ناگهانی شدید؟", 50, PAPER, F_BLACK, "rt")
    text(im, (948, 668), "صبر نکن.", 76, GREEN, F_BLACK, "rt")
    line(d, [(510, 730), (948, 730)], rgba(RED, 240), 5)
    text(im, (948, 802), "اگر درد شدید قفسه‌سینه یا پشت،", 25, PAPER, F_SEMI, "rt")
    text(im, (948, 850), "غش، یا ضعف ناگهانی دارید:", 25, PAPER, F_SEMI, "rt")
    rect(d, (560, 906, 948, 1008), fill=rgba(MUSTARD, 235), radius=18)
    text(im, (754, 957), "با اورژانس ۱۱۵ تماس بگیر", 25, INK, F_BLACK, "mm")
    text(im, (956, 1151), "این پست را ذخیره کن و برای آگاهی به اشتراک بگذار.", 19, MUSTARD_LIGHT, F_BOLD, "rt")
    text(im, (956, 1195), "این محتوا جایگزین تشخیص پزشک نیست.", 16, MUTED, F_REG, "rt")
    return im


def save_slide(im: Image.Image, path: Path):
    # Flatten transparent drawing onto the background before saving.
    flat = Image.new("RGB", im.size, BG)
    flat.paste(im, mask=im.getchannel("A"))
    flat = flat.resize((1080, 1350), Image.Resampling.LANCZOS)
    flat.save(path, optimize=True)


def make_preview(paths: list[Path], path: Path):
    thumb_w, thumb_h = 324, 405
    cols = 3
    rows = math.ceil(len(paths) / cols)
    preview = Image.new("RGB", (cols * thumb_w + 48, rows * thumb_h + 48), (21, 25, 20))
    pd = ImageDraw.Draw(preview)
    for idx, p in enumerate(paths):
        img = Image.open(p).convert("RGB").resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        x = 24 + (idx % cols) * thumb_w
        y = 24 + (idx // cols) * thumb_h
        preview.paste(img, (x, y))
        pd.rectangle((x, y, x+thumb_w-1, y+thumb_h-1), outline=(190,255,0), width=1)
    preview.save(path, optimize=True)


def main():
    OUT.mkdir(exist_ok=True)
    slides = [slide_1(), slide_2(), slide_3(), slide_4(), slide_5(), slide_6(), slide_7()]
    paths = []
    for i, im in enumerate(slides, 1):
        p = OUT / f"slide_{i:02d}.png"
        save_slide(im, p)
        paths.append(p)
    make_preview(paths, OUT / "carousel_preview.png")
    caption = """دیسکسیون آئورت چیست؟

دیسکسیون آئورت زمانی رخ می‌دهد که در لایهٔ داخلی آئورت پارگی ایجاد شود و خون بین لایه‌های دیواره پیش برود. این وضعیت می‌تواند یک اورژانس تهدیدکنندهٔ حیات باشد.

درد ناگهانی و شدید قفسه‌سینه یا پشت، غش، تنگی نفس، ضعف ناگهانی یا اختلال تکلم را جدی بگیرید. اگر چنین علائمی وجود دارد، با اورژانس ۱۱۵ تماس بگیرید.

تشخیص و درمان به محل درگیری و وضعیت بیمار بستگی دارد و فقط با ارزیابی فوری پزشکی انجام می‌شود. خوددرمانی نکنید.

این پست آموزشی است و جایگزین تشخیص یا توصیهٔ پزشک نیست.

منابع پیشنهادی برای مطالعه:
2022 ACC/AHA Guideline for the Diagnosis and Management of Aortic Disease
European Society of Cardiology Guidelines on aortic diseases

#دیسکسیون_آئورت #آئورت #قلب_و_عروق #اورژانس #آموزش_پزشکی #فشارخون
"""
    (OUT / "caption.txt").write_text(caption, encoding="utf-8")
    readme = """# کاروسل اینستاگرام: دیسکسیون آئورت

- نسبت: ۴:۵، رزولوشن هر اسلاید: ۱۰۸۰×۱۳۵۰
- تعداد اسلاید: ۷
- پالت: سبز فسفری `#BEFF00`، قرمز `#FF3D4E`، خردلی `#DAA725`، زمینهٔ مشکی گرم
- فونت: Vazirmatn

ترتیب انتشار: `slide_01.png` تا `slide_07.png`.
"""
    (OUT / "README.md").write_text(readme, encoding="utf-8")
    print(f"created {len(paths)} slides in {OUT}")


if __name__ == "__main__":
    main()

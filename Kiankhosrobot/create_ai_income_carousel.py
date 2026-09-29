from __future__ import annotations

"""Generate a high-resolution, multicolor Persian Instagram carousel.

Carousel slides: 4:5 at 7680x9600 (8K width).
Cover: 9:16 at 7680x13653 (8K width), prepared separately for a reel/story cover.
"""

import gc
import math
import os
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "toolkit"))
from fatext import FD  # type: ignore

OUT = ROOT / "ai_income_carousel"
FONT_DIR = ROOT.parent / "fonttmp" / "fonts" / "ttf"

# Multicolor advertising palette.
# Light editorial background: colorful, airy, and high-contrast for dark Persian type.
NAVY = (253, 252, 248)
NAVY_2 = (240, 250, 255)
INK = (18, 27, 54)
WHITE = (18, 27, 54)
MIST = (38, 49, 73)
# Saturated, darker accents keep colored headings legible on the light base.
VIOLET = (104, 45, 205)
PURPLE = (150, 58, 218)
CYAN = (0, 143, 190)
CORAL = (220, 47, 80)
YELLOW = (198, 137, 17)
LIME = (103, 166, 0)
ORANGE = (220, 96, 37)

F_REG = "Vazirmatn-Regular.ttf"
F_MED = "Vazirmatn-Medium.ttf"
F_SEMI = "Vazirmatn-SemiBold.ttf"
F_BOLD = "Vazirmatn-Bold.ttf"
F_BLACK = "Vazirmatn-Black.ttf"


def font(family: str, size: float, scale: float):
    return ImageFont.truetype(str(FONT_DIR / family), max(10, int(round(size * scale))))


def rgba(c, a=255):
    return (*c, int(a))


class Canvas:
    def __init__(self, base_w: int, base_h: int, out_w: int = 7680):
        self.bw, self.bh = base_w, base_h
        self.w, self.h = out_w, int(round(out_w * base_h / base_w))
        self.s = self.w / base_w
        self.im = self._background()
        self.d = ImageDraw.Draw(self.im, "RGBA")

    def x(self, n):
        return int(round(n * self.s))

    def box(self, b):
        return tuple(self.x(v) for v in b)

    def line(self, pts, fill, width=2, joint="curve"):
        self.d.line([(self.x(x), self.x(y)) for x, y in pts], fill=fill,
                    width=max(1, self.x(width)), joint=joint)

    def rect(self, b, fill=None, outline=None, width=1, radius=0):
        self.d.rounded_rectangle(self.box(b), fill=fill, outline=outline,
                                 width=self.x(width) if outline else 1,
                                 radius=self.x(radius))

    def ellipse(self, b, fill=None, outline=None, width=1):
        self.d.ellipse(self.box(b), fill=fill, outline=outline,
                       width=self.x(width) if outline else 1)

    def polygon(self, pts, fill):
        self.d.polygon([(self.x(x), self.x(y)) for x, y in pts], fill=fill)

    def arc(self, b, start, end, fill, width=2):
        self.d.arc(self.box(b), start, end, fill=fill, width=self.x(width))

    def text(self, xy, value, size, fill=WHITE, family=F_REG, anchor="rt"):
        return FD(self.im).text((self.x(xy[0]), self.x(xy[1])), value,
                                font=font(family, size, self.s), fill=fill,
                                anchor=anchor)

    def _background(self):
        # Build the atmospheric gradient at a small size, then upscale to keep 8K output practical.
        small_w = 320
        small_h = max(320, int(round(small_w * self.bh / self.bw)))
        img = Image.new("RGB", (small_w, small_h))
        pix = img.load()
        stops = [(0.0, NAVY), (0.42, NAVY_2), (1.0, (250, 246, 255))]
        for y in range(small_h):
            t = y / max(1, small_h - 1)
            for j in range(len(stops) - 1):
                if stops[j][0] <= t <= stops[j + 1][0]:
                    p0, c0 = stops[j]
                    p1, c1 = stops[j + 1]
                    q = (t - p0) / (p1 - p0)
                    c = tuple(int(c0[k] * (1-q) + c1[k] * q) for k in range(3))
                    break
            for x in range(small_w):
                pix[x, y] = c
        img = img.resize((self.w, self.h), Image.Resampling.BICUBIC).convert("RGBA")
        glow = Image.new("RGBA", (small_w, small_h), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow, "RGBA")
        # Deliberately large soft color fields create a contemporary ad campaign feel.
        gd.ellipse((-120, -80, 150, 190), fill=rgba(CYAN, 50))
        gd.ellipse((190, 70, 400, 350), fill=rgba(VIOLET, 66))
        gd.ellipse((35, small_h-190, 270, small_h+90), fill=rgba(CORAL, 46))
        gd.ellipse((small_w-155, small_h-230, small_w+70, small_h+60), fill=rgba(YELLOW, 30))
        glow = glow.filter(ImageFilter.GaussianBlur(max(8, small_w // 18)))
        glow = glow.resize((self.w, self.h), Image.Resampling.BICUBIC)
        return Image.alpha_composite(img, glow)

    def noise_grid(self):
        # Fine grid + playful confetti; keep opacity low under type.
        for x in range(0, self.bw + 1, 90):
            self.line([(x, 0), (x, self.bh)], rgba(CYAN, 16), 1)
        for y in range(0, self.bh + 1, 90):
            self.line([(0, y), (self.bw, y)], rgba(VIOLET, 14), 1)
        for x, y, c in [(72, 172, CYAN), (1015, 240, YELLOW), (118, 1240, CORAL),
                        (960, 1170, LIME), (520, 96, CORAL)]:
            self.ellipse((x-3, y-3, x+3, y+3), fill=rgba(c, 220))

    def pill(self, x, y, label, color=CYAN, width=None):
        width = width or max(128, len(label) * 15 + 44)
        self.rect((x, y, x + width, y + 42), fill=rgba(color, 28), outline=rgba(color, 210), width=2, radius=21)
        self.text((x + width/2, y + 21), label, 18, color, F_BOLD, "mm")


def header(c: Canvas, page: str, section="AI × SKILLS × INCOME"):
    c.text((74, 58), page, 18, CYAN, F_BOLD, "la")
    c.text((1006, 58), section, 16, YELLOW, F_BOLD, "ra")
    c.line([(74, 90), (1006, 90)], rgba(WHITE, 48), 1)
    c.line([(74, c.bh-62), (244, c.bh-62)], rgba(CORAL, 230), 4)
    c.text((260, c.bh-70), "آموزش کاربردی برای ساختن فرصت", 16, MIST, F_REG, "la")
    c.line([(1006, c.bh-110), (1006, c.bh-62), (958, c.bh-62)], rgba(LIME, 225), 4)


def title_block(c: Canvas, eyebrow, title_lines, subtitle, color=WHITE, title_size=58, y=145):
    c.pill(74, y, eyebrow, color, width=max(146, len(eyebrow)*13+44))
    ty = y + 90
    for i, line in enumerate(title_lines):
        c.text((1006, ty + i*(title_size+8)), line, title_size, color if i == 0 else WHITE, F_BLACK, "rt")
    sy = ty + len(title_lines)*(title_size+8) + 22
    if subtitle:
        c.text((1006, sy), subtitle, 25, MIST, F_MED, "rt")


def draw_spark(c: Canvas, x, y, r, color=YELLOW):
    c.polygon([(x, y-r), (x+5, y-5), (x+r, y), (x+5, y+5),
               (x, y+r), (x-5, y+5), (x-r, y), (x-5, y-5)], rgba(color, 245))


def draw_person(c: Canvas, x, y, scale=1.0, shirt=CYAN):
    # Simple youthful character with glossy advertising-style construction.
    c.ellipse((x-34*scale, y-198*scale, x+34*scale, y-130*scale), fill=rgba(YELLOW, 255))
    c.ellipse((x-30*scale, y-191*scale, x+30*scale, y-134*scale), fill=rgba((63, 40, 53), 255))
    c.ellipse((x-62*scale, y-130*scale, x+62*scale, y+36*scale), fill=rgba(shirt, 235))
    c.line([(x-25*scale, y+33*scale), (x-44*scale, y+160*scale)], rgba(WHITE, 230), max(5, int(12*scale)))
    c.line([(x+25*scale, y+33*scale), (x+48*scale, y+160*scale)], rgba(WHITE, 230), max(5, int(12*scale)))
    c.line([(x-56*scale, y-94*scale), (x-133*scale, y-15*scale)], rgba(shirt, 255), max(5, int(13*scale)))
    c.line([(x+56*scale, y-94*scale), (x+135*scale, y-42*scale)], rgba(shirt, 255), max(5, int(13*scale)))
    c.ellipse((x-53*scale, y+148*scale, x-22*scale, y+166*scale), fill=rgba(CORAL, 255))
    c.ellipse((x+32*scale, y+148*scale, x+63*scale, y+166*scale), fill=rgba(CORAL, 255))


def draw_ai_orb(c: Canvas, x, y, r=92):
    for rr, alpha in [(r+24, 20), (r+12, 32)]:
        c.ellipse((x-rr, y-rr, x+rr, y+rr), fill=rgba(CYAN, alpha))
    c.ellipse((x-r, y-r, x+r, y+r), fill=rgba(VIOLET, 245), outline=rgba(WHITE, 160), width=3)
    c.ellipse((x-r+20, y-r+20, x+r-20, y+r-20), fill=rgba(CYAN, 175))
    # neural-star mark
    c.line([(x-40, y+18), (x-12, y-12), (x+10, y+24), (x+43, y-34)], rgba(WHITE, 255), 9)
    c.ellipse((x-49, y+9, x-31, y+27), fill=rgba(YELLOW, 255))
    c.ellipse((x-21, y-21, x-3, y-3), fill=rgba(CORAL, 255))
    c.ellipse((x+1, y+15, x+19, y+33), fill=rgba(LIME, 255))
    c.ellipse((x+34, y-43, x+52, y-25), fill=rgba(YELLOW, 255))


def draw_card(c: Canvas, b, fill=(255,255,255,24), outline=(255,255,255,70), radius=18):
    c.rect(b, fill=rgba(fill[:3], fill[3] if len(fill)>3 else 255), outline=rgba(outline[:3], outline[3] if len(outline)>3 else 255), width=2, radius=radius)


def cover():
    c = Canvas(1080, 1920)
    c.noise_grid()
    # diagonal ad ribbons
    c.polygon([(0, 1120), (1080, 840), (1080, 1100), (0, 1400)], rgba(CORAL, 205))
    c.polygon([(0, 1195), (1080, 915), (1080, 995), (0, 1275)], rgba(YELLOW, 220))
    c.polygon([(0, 1275), (1080, 995), (1080, 1055), (0, 1335)], rgba(CYAN, 220))
    c.text((74, 66), "COVER / 09:16", 18, CYAN, F_BOLD, "la")
    c.text((1006, 66), "AI × YOUTH × INCOME", 16, YELLOW, F_BOLD, "ra")
    c.line([(74, 98), (1006, 98)], rgba(WHITE, 50), 1)
    c.pill(74, 174, "آینده را بساز", LIME, 184)
    c.text((1006, 300), "هوش مصنوعی", 86, WHITE, F_BLACK, "rt")
    c.text((1006, 414), "برای درآمدسازی", 72, YELLOW, F_BLACK, "rt")
    c.text((1006, 512), "جوان‌ها", 104, CYAN, F_BLACK, "rt")
    c.text((1006, 660), "از یک مهارت کوچک تا اولین مشتری", 28, MIST, F_MED, "rt")
    # Promotional hero scene: character + AI orb + offer cards.
    c.rect((74, 780, 1006, 1580), fill=rgba((255,255,255), 225), outline=rgba(WHITE, 70), width=2, radius=34)
    draw_person(c, 465, 1320, 1.28, shirt=VIOLET)
    draw_ai_orb(c, 746, 1038, 130)
    c.line([(550, 1140), (654, 1074)], rgba(WHITE, 180), 4)
    for b, col, lab, y in [((120, 910, 388, 1018), CYAN, "ایده", 948),
                           ((706, 1250, 970, 1360), CORAL, "مهارت", 1288),
                           ((126, 1395, 398, 1505), YELLOW, "مشتری", 1432)]:
        c.rect(b, fill=rgba(col, 224), radius=20)
        c.text(((b[0]+b[2])/2, y), lab, 27, INK, F_BLACK, "mm")
    for x, y, col in [(150, 1125, CYAN), (917, 862, YELLOW), (895, 1460, LIME), (180, 1536, CORAL)]:
        draw_spark(c, x, y, 20, col)
    c.rect((74, 1660, 1006, 1780), fill=rgba(NAVY, 205), outline=rgba(WHITE, 80), width=2, radius=20)
    c.text((948, 1700), "ایده  •  اجرا  •  درآمد", 27, WHITE, F_BOLD, "rt")
    c.text((948, 1745), "ابزار را یاد بگیر؛ مسئلهٔ واقعی حل کن.", 20, MIST, F_REG, "rt")
    c.line([(74, 1850), (244, 1850)], rgba(CORAL, 240), 4)
    c.text((260, 1841), "کاروسل کاربردی | ورق بزن", 17, MIST, F_REG, "la")
    return c


def cover_4x5():
    """A dedicated 4:5 first slide for the carousel, while 9:16 remains available for reel/story cover use."""
    c = Canvas(1080, 1350); c.noise_grid()
    c.text((74, 58), "CAROUSEL COVER / 04:05", 18, CYAN, F_BOLD, "la")
    c.text((1006, 58), "AI × YOUTH × INCOME", 16, YELLOW, F_BOLD, "ra")
    c.line([(74, 90), (1006, 90)], rgba(WHITE, 50), 1)
    c.pill(74, 138, "آینده را بساز", LIME, 184)
    c.text((1006, 235), "هوش مصنوعی", 62, WHITE, F_BLACK, "rt")
    c.text((1006, 315), "برای درآمدسازی", 57, YELLOW, F_BLACK, "rt")
    c.text((1006, 390), "جوان‌ها", 78, CYAN, F_BLACK, "rt")
    c.text((1006, 482), "از یک مهارت کوچک تا اولین مشتری", 23, MIST, F_MED, "rt")
    c.rect((74, 555, 1006, 1125), fill=rgba((255,255,255), 225), outline=rgba(WHITE, 75), width=2, radius=30)
    draw_person(c, 300, 1010, 0.98, shirt=VIOLET)
    draw_ai_orb(c, 315, 718, 92)
    c.line([(370, 790), (560, 838)], rgba(WHITE, 175), 4)
    c.rect((548, 638, 948, 726), fill=rgba(CYAN, 220), radius=18)
    c.text((748, 682), "ایده", 24, INK, F_BLACK, "mm")
    c.rect((548, 770, 948, 858), fill=rgba(CORAL, 220), radius=18)
    c.text((748, 814), "مهارت", 24, INK, F_BLACK, "mm")
    c.rect((548, 902, 948, 990), fill=rgba(YELLOW, 225), radius=18)
    c.text((748, 946), "مشتری", 24, INK, F_BLACK, "mm")
    for x, y, col in [(120, 638, YELLOW), (950, 605, LIME), (470, 1035, CORAL), (980, 1060, CYAN)]:
        draw_spark(c, x, y, 17, col)
    c.rect((548, 1020, 948, 1075), fill=rgba(VIOLET, 190), outline=rgba(VIOLET, 220), width=1, radius=14)
    c.text((748, 1048), "ایده • اجرا • درآمد", 19, WHITE, F_BLACK, "mm")
    c.line([(74, 1220), (244, 1220)], rgba(CORAL, 240), 4)
    c.text((260, 1211), "کاروسل کاربردی | ورق بزن", 17, MIST, F_REG, "la")
    return c


def slide_1():
    c = Canvas(1080, 1350); c.noise_grid(); header(c, "01 / 07")
    title_block(c, "اصل اول", ["فرصت درآمدی،", "نه وعدهٔ پولدار شدن"], "AI سرعت می‌دهد؛ ارزش را مسئلهٔ واقعی می‌سازد.", CORAL, 53, 142)
    # Hero visual on left, text dominates on right.
    c.rect((74, 545, 470, 1095), fill=rgba(NAVY, 170), outline=rgba(CYAN, 120), width=2, radius=28)
    draw_person(c, 280, 1010, 1.18, shirt=CORAL)
    draw_ai_orb(c, 280, 670, 96)
    c.line([(280, 768), (280, 870)], rgba(CYAN, 180), 4)
    for x, y, col in [(130, 620, YELLOW), (430, 640, LIME), (118, 1030, CYAN), (430, 1000, CORAL)]:
        draw_spark(c, x, y, 17, col)
    c.rect((542, 566, 1006, 1048), fill=rgba((255,255,255), 225), outline=rgba(WHITE, 88), width=2, radius=24)
    text_rows = [
        ("۱. یک مهارت را انتخاب کن", "کپی‌رایتینگ، طراحی، ویدئو، تحقیق یا اتوماسیون.", CYAN),
        ("۲. یک مشکل مشخص پیدا کن", "برای یک گروه خاص، خروجی قابل‌اندازه‌گیری بساز.", YELLOW),
        ("۳. با نمونه‌کار شروع کن", "سه نمونهٔ کوچک بهتر از یک وعدهٔ بزرگ است.", LIME),
    ]
    y = 625
    for heading, body, color in text_rows:
        c.ellipse((590, y+5, 618, y+33), fill=rgba(color, 255))
        c.text((650, y), heading, 24, color, F_BOLD, "lt")
        c.text((950, y+50), body, 23, MIST, F_REG, "rt")
        c.line([(590, y+105), (950, y+105)], rgba(WHITE, 34), 1)
        y += 145
    c.rect((542, 1100, 1006, 1188), fill=rgba(VIOLET, 48), outline=rgba(VIOLET, 170), width=2, radius=18)
    c.text((952, 1135), "فرمول ساده: مهارت × مشکل × اعتماد", 22, WHITE, F_BOLD, "rt")
    return c


def slide_2():
    c = Canvas(1080, 1350); c.noise_grid(); header(c, "02 / 07")
    title_block(c, "مسیر ۱", ["تولید محتوا", "برای کسب‌وکارها"], "با AI تقویم محتوا را سریع‌تر و حرفه‌ای‌تر بساز.", CYAN, 58, 142)
    c.rect((74, 575, 390, 1115), fill=rgba((255,255,255), 225), outline=rgba(CYAN, 145), width=2, radius=28)
    # phone + content tiles
    c.rect((150, 648, 315, 975), fill=rgba((255,255,255), 242), radius=24)
    c.rect((171, 690, 294, 812), fill=rgba(VIOLET, 230), radius=15)
    c.ellipse((203, 718, 262, 777), fill=rgba(YELLOW, 255))
    c.line([(181, 861), (275, 861)], rgba(INK, 220), 8)
    c.line([(181, 890), (290, 890)], rgba(INK, 120), 5)
    c.rect((181, 928, 286, 949), fill=rgba(CORAL, 230), radius=10)
    c.text((232, 1010), "پست / ریلز / کپشن", 18, WHITE, F_BOLD, "mm")
    c.rect((112, 1012, 352, 1081), fill=rgba(CYAN, 190), radius=14)
    c.text((232, 1046), "محتوای منظم = اعتماد", 18, INK, F_BOLD, "mm")
    c.pill(580, 590, "چه چیزی بفروشی؟", CORAL, 194)
    bullets = [
        ("تقویم محتوای ماهانه", "برای یک حوزهٔ مشخص؛ مثلاً کافه، کلینیک یا فروشگاه.", CORAL),
        ("کپشن و سناریوی ویدئو", "ایده را به متن کوتاه، هوک و CTA تبدیل کن.", YELLOW),
        ("بستهٔ شروع ۳ نمونه‌ای", "قبل از پیشنهاد، نتیجه را با نمونه نشان بده.", LIME),
    ]
    y = 692
    for head, body, col in bullets:
        c.rect((548, y, 1006, y+126), fill=rgba((255,255,255), 230), outline=rgba(col, 145), width=2, radius=18)
        c.rect((548, y, 565, y+126), fill=rgba(col, 225), radius=8)
        c.text((965, y+30), head, 23, col, F_BOLD, "rt")
        c.text((965, y+76), body, 22, MIST, F_REG, "rt")
        y += 148
    c.rect((548, 1140, 1006, 1205), fill=rgba(CYAN, 42), outline=rgba(CYAN, 180), width=1, radius=14)
    c.text((962, 1169), "AI متن می‌دهد؛ تو لحن و تجربهٔ واقعی اضافه کن.", 18, WHITE, F_SEMI, "rt")
    return c


def slide_3():
    c = Canvas(1080, 1350); c.noise_grid(); header(c, "03 / 07")
    title_block(c, "مسیر ۲", ["فایل دیجیتال", "بساز و بفروش"], "یک بار تولید کن؛ بارها با بهبود و بازاریابی عرضه کن.", YELLOW, 58, 142)
    # fantasy digital shop visual
    c.rect((74, 570, 450, 1105), fill=rgba((255,255,255), 225), outline=rgba(YELLOW, 150), width=2, radius=28)
    c.polygon([(125, 744), (300, 680), (416, 747), (242, 815)], rgba(PURPLE, 235))
    c.polygon([(125, 744), (242, 815), (242, 973), (125, 900)], rgba(VIOLET, 230))
    c.polygon([(242, 815), (416, 747), (416, 905), (242, 973)], rgba(CORAL, 225))
    c.rect((176, 790, 349, 882), fill=rgba((255,255,255), 220), radius=12)
    c.text((262, 826), "PROMPT", 20, INK, F_BLACK, "mm")
    c.text((262, 858), "PACK", 20, INK, F_BOLD, "mm")
    draw_spark(c, 155, 634, 25, CYAN); draw_spark(c, 395, 1008, 20, LIME)
    c.text((260, 1032), "محصول کوچک، ارزش روشن", 18, WHITE, F_BOLD, "mm")
    c.pill(570, 590, "ایده‌های قابل‌فروش", VIOLET, 214)
    products = [
        ("قالب و چک‌لیست", "برای برنامه‌ریزی، رزومه، ارائه یا مدیریت پروژه.", CYAN),
        ("مجموعه پرامپت", "برای یک شغل و خروجی مشخص؛ نه فهرست عمومی.", CORAL),
        ("مینی‌راهنما یا ورک‌بوک", "دانش خودت را به مسیر کوتاه و قابل‌اجرا تبدیل کن.", LIME),
    ]
    y = 692
    for head, body, col in products:
        c.rect((545, y, 1006, y+126), fill=rgba((255,255,255), 230), outline=rgba(col, 150), width=2, radius=18)
        c.ellipse((582, y+40, 622, y+80), fill=rgba(col, 235))
        c.text((965, y+27), head, 23, col, F_BOLD, "rt")
        c.text((965, y+75), body, 22, MIST, F_REG, "rt")
        y += 148
    c.rect((545, 1140, 1006, 1205), fill=rgba(YELLOW, 39), outline=rgba(YELLOW, 180), width=1, radius=14)
    c.text((962, 1169), "نسخهٔ اول با AI؛ نسخهٔ ارزشمند با ویرایش انسانی.", 18, WHITE, F_SEMI, "rt")
    return c


def slide_4():
    c = Canvas(1080, 1350); c.noise_grid(); header(c, "04 / 07")
    title_block(c, "مسیر ۳", ["خدمات AI", "برای فریلنسرها"], "به‌جای فروش ابزار، نتیجه‌ای را بفروش که مشتری می‌خواهد.", VIOLET, 58, 142)
    # Workflow / automation illustration.
    c.rect((74, 590, 442, 1104), fill=rgba((255,255,255), 225), outline=rgba(VIOLET, 165), width=2, radius=28)
    nodes = [(160, 722, CYAN, "داده"), (330, 642, YELLOW, "AI"), (358, 855, CORAL, "خروجی"), (164, 974, LIME, "مشتری")]
    for (x, y, col, lab) in nodes:
        c.ellipse((x-45, y-45, x+45, y+45), fill=rgba(col, 230), outline=rgba(WHITE, 140), width=2)
        c.text((x, y), lab, 19, INK, F_BLACK, "mm")
    c.line([(202, 700), (286, 665)], rgba(WHITE, 170), 4)
    c.line([(347, 687), (355, 810)], rgba(WHITE, 170), 4)
    c.line([(320, 887), (205, 955)], rgba(WHITE, 170), 4)
    c.text((255, 1060), "فرآیند ساده؛ خروجی قابل‌تحویل", 18, WHITE, F_BOLD, "mm")
    c.pill(575, 590, "خدمات پیشنهادی", CORAL, 180)
    services = [
        ("تحقیق و خلاصه‌سازی", "گزارش‌های طولانی را به تصمیم‌های روشن تبدیل کن.", CYAN),
        ("پاک‌سازی و تحلیل داده", "فایل‌های شلوغ را مرتب و قابل‌استفاده کن.", YELLOW),
        ("اتوماسیون و پشتیبانی", "کارهای تکراری را به جریان کاری بسپار.", CORAL),
        ("ترجمه و بومی‌سازی", "فقط ترجمه نکن؛ لحن بازار را بشناس.", LIME),
    ]
    y = 682
    for head, body, col in services:
        c.rect((545, y, 1006, y+108), fill=rgba((255,255,255), 225), outline=rgba(col, 135), width=2, radius=17)
        c.text((964, y+26), head, 22, col, F_BOLD, "rt")
        c.text((964, y+70), body, 22, MIST, F_REG, "rt")
        y += 125
    c.rect((545, 1180, 1006, 1234), fill=rgba(VIOLET, 45), outline=rgba(VIOLET, 180), width=1, radius=14)
    c.text((964, 1207), "پیشنهاد خوب = خروجی مشخص + زمان مشخص + نمونه‌کار", 17, WHITE, F_SEMI, "rt")
    return c


def slide_5():
    c = Canvas(1080, 1350); c.noise_grid(); header(c, "05 / 07")
    title_block(c, "مسیر ۴", ["آموزش بده", "آنچه بلدی"], "ترکیب تخصص تو با AI می‌تواند یک محصول آموزشی بسازد.", LIME, 58, 142)
    # Holographic classroom / microphone scene.
    c.rect((74, 596, 424, 1105), fill=rgba((255,255,255), 225), outline=rgba(LIME, 145), width=2, radius=28)
    c.ellipse((160, 684, 330, 854), fill=rgba(VIOLET, 235), outline=rgba(CYAN, 200), width=3)
    c.ellipse((205, 722, 286, 803), fill=rgba(CYAN, 205))
    c.line([(180, 905), (348, 905)], rgba(YELLOW, 230), 10)
    c.line([(201, 939), (330, 939)], rgba(WHITE, 120), 7)
    c.line([(216, 972), (315, 972)], rgba(WHITE, 100), 6)
    c.rect((129, 1012, 372, 1060), fill=rgba(CORAL, 210), radius=12)
    c.text((250, 1035), "یادگیری + اجرا", 19, INK, F_BLACK, "mm")
    for x, y, col in [(112, 650, YELLOW), (388, 715, CORAL), (128, 1084, CYAN), (395, 1008, LIME)]:
        draw_spark(c, x, y, 16, col)
    c.pill(565, 590, "محصول آموزشی", CYAN, 182)
    lessons = [
        ("کارگاه کوتاه", "یک خروجی مشخص را در ۶۰ تا ۹۰ دقیقه آموزش بده.", CYAN),
        ("مینی‌کورس", "یک مسئلهٔ پرتکرار را از صفر تا نتیجه طراحی کن.", YELLOW),
        ("جلسهٔ مشاوره", "به‌جای پاسخ آماده، مسیر حل مسئله بساز.", CORAL),
    ]
    y = 692
    for head, body, col in lessons:
        c.rect((545, y, 1006, y+126), fill=rgba((255,255,255), 225), outline=rgba(col, 145), width=2, radius=18)
        c.rect((545, y, 560, y+126), fill=rgba(col, 220), radius=8)
        c.text((964, y+28), head, 23, col, F_BOLD, "rt")
        c.text((964, y+77), body, 22, MIST, F_REG, "rt")
        y += 148
    c.rect((545, 1140, 1006, 1205), fill=rgba(LIME, 38), outline=rgba(LIME, 180), width=1, radius=14)
    c.text((964, 1169), "اعتماد از نمونه‌کار و تجربهٔ واقعی تو می‌آید.", 18, WHITE, F_SEMI, "rt")
    return c


def slide_6():
    c = Canvas(1080, 1350); c.noise_grid(); header(c, "06 / 07")
    title_block(c, "برنامهٔ شروع", ["۷ روز تا", "اولین پیشنهاد"], "قرار نیست کامل باشی؛ باید یک خروجی قابل‌ارائه داشته باشی.", ORANGE, 58, 142)
    # A colorful roadmap occupies the left third; copy dominates the right.
    c.rect((74, 592, 430, 1110), fill=rgba((255,255,255), 225), outline=rgba(ORANGE, 155), width=2, radius=28)
    c.line([(176, 736), (334, 736), (334, 920), (176, 920), (176, 1050), (334, 1050)], rgba(WHITE, 160), 5)
    days = [(176, 736, CYAN, "۱"), (334, 736, YELLOW, "۲"), (334, 920, CORAL, "۳"),
            (176, 920, LIME, "۴"), (176, 1050, VIOLET, "۵"), (334, 1050, ORANGE, "۶")]
    for x, y, col, lab in days:
        c.ellipse((x-39, y-39, x+39, y+39), fill=rgba(col, 235), outline=rgba(WHITE, 160), width=2)
        c.text((x, y), lab, 28, INK, F_BLACK, "mm")
    c.text((250, 657), "نقشهٔ حرکت", 22, WHITE, F_BOLD, "mm")
    c.pill(565, 590, "قدم‌های کوچک", ORANGE, 174)
    steps = [
        ("روز ۱–۲", "یک مشکل و یک گروه مخاطب انتخاب کن.", CYAN),
        ("روز ۳", "نمونهٔ اول را بساز و با یک نفر تست کن.", YELLOW),
        ("روز ۴–۵", "نمونه را منتشر کن و به ۱۰ مشتری احتمالی پیام بده.", CORAL),
        ("روز ۶–۷", "بازخورد بگیر، پیشنهاد را ساده‌تر و دقیق‌تر کن.", LIME),
    ]
    y = 692
    for head, body, col in steps:
        c.ellipse((566, y+14, 592, y+40), fill=rgba(col, 245))
        c.text((632, y), head, 23, col, F_BOLD, "lt")
        c.text((960, y+48), body, 23, MIST, F_REG, "rt")
        y += 122
    c.rect((545, 1168, 1006, 1236), fill=rgba(ORANGE, 48), outline=rgba(ORANGE, 190), width=1, radius=16)
    c.text((964, 1202), "یک مهارت  •  یک مشتری  •  یک نتیجه", 22, WHITE, F_BLACK, "rt")
    return c


def slide_7():
    c = Canvas(1080, 1350); c.noise_grid(); header(c, "07 / 07", "START SMALL / BUILD SMART")
    title_block(c, "حواست باشد", ["AI میانبر نیست؛", "اهرم توست"], "اعتماد، کیفیت و استمرار چیزی نیست که با یک پرامپت ساخته شود.", CORAL, 58, 142)
    c.rect((74, 584, 1006, 1038), fill=rgba((255,255,255), 225), outline=rgba(CORAL, 150), width=2, radius=28)
    warnings = [
        ("کپی بدون ویرایش", "خروجی خام را منتشر نکن؛ تجربه و نظر خودت را اضافه کن.", CORAL),
        ("وعدهٔ بزرگ بدون نمونه", "قبل از قیمت، یک نتیجهٔ کوچک و واقعی نشان بده.", YELLOW),
        ("یادگیری بدون فروش", "هر هفته فقط ابزار یاد نگیر؛ یک پیشنهاد هم ارائه کن.", LIME),
    ]
    y = 638
    for head, body, col in warnings:
        c.rect((124, y, 956, y+106), fill=rgba(col, 28), outline=rgba(col, 150), width=2, radius=17)
        c.ellipse((160, y+34, 200, y+74), fill=rgba(col, 235))
        c.text((238, y+25), head, 23, col, F_BOLD, "lt")
        c.text((238, y+70), body, 22, MIST, F_REG, "lt")
        y += 128
    c.rect((74, 1098, 1006, 1180), fill=rgba(YELLOW, 230), radius=18)
    c.text((540, 1138), "امروز فقط یک قدم بردار.", 28, INK, F_BLACK, "mm")
    c.text((1006, 1232), "ذخیره کن  •  برای یک دوست جوان بفرست  •  شروع کن", 20, WHITE, F_BOLD, "rt")
    return c


def save(c: Canvas, path: Path):
    # JPEG keeps high-resolution packages practical while preserving crisp typography.
    rgb = Image.new("RGB", c.im.size, NAVY)
    rgb.paste(c.im, mask=c.im.getchannel("A"))
    rgb.save(path, "JPEG", quality=96, subsampling=0, optimize=True)
    del rgb, c.im
    gc.collect()


def make_preview(paths, output):
    thumb_w, thumb_h = 324, 405
    cols = 3
    rows = math.ceil(len(paths) / cols)
    out = Image.new("RGB", (cols*thumb_w + 48, rows*thumb_h + 48), (8, 11, 30))
    d = ImageDraw.Draw(out)
    for i, p in enumerate(paths):
        img = Image.open(p).convert("RGB")
        # Cover is 9:16; center crop it for the contact sheet only.
        if img.height / img.width > 1.3:
            crop_h = int(img.width * 1.25)
            top = (img.height-crop_h)//2
            img = img.crop((0, top, img.width, top+crop_h))
        img.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", (thumb_w, thumb_h), (17,22,57))
        canvas.paste(img, ((thumb_w-img.width)//2, (thumb_h-img.height)//2))
        x = 24 + (i % cols)*thumb_w; y = 24 + (i // cols)*thumb_h
        out.paste(canvas, (x, y))
        d.rectangle((x, y, x+thumb_w-1, y+thumb_h-1), outline=(185,242,39), width=1)
    out.save(output, "JPEG", quality=95, optimize=True)


def main():
    OUT.mkdir(exist_ok=True)
    cover_path = OUT / "cover_9x16_8k.jpg"
    cover_canvas = cover(); save(cover_canvas, cover_path)
    carousel_cover_path = OUT / "cover_4x5_8k.jpg"
    carousel_cover_canvas = cover_4x5(); save(carousel_cover_canvas, carousel_cover_path)
    makers = [slide_1, slide_2, slide_3, slide_4, slide_5, slide_6, slide_7]
    paths = [cover_path, carousel_cover_path]
    for idx, maker in enumerate(makers, 1):
        p = OUT / f"slide_{idx:02d}_4x5_8k.jpg"
        save(maker(), p)
        paths.append(p)
    make_preview(paths, OUT / "carousel_preview.jpg")
    (OUT / "README.md").write_text("""# کاروسل اینستاگرام: هوش مصنوعی برای درآمدسازی جوان‌ها

- اسلایدهای کاروسل: ۷ فایل JPEG با ابعاد ۷۶۸۰×۹۶۰۰، نسبت ۴:۵
- کاور کاروسل: `cover_4x5_8k.jpg` با ابعاد ۷۶۸۰×۹۶۰۰، نسبت ۴:۵
- کاور جداگانهٔ ریلز/استوری: `cover_9x16_8k.jpg` با ابعاد ۷۶۸۰×۱۳۶۵۳، نسبت ۹:۱۶
- پالت مولتی‌کالر: بنفش، فیروزه‌ای، مرجانی، زرد، لیمویی و سرمه‌ای
- سبک: متن‌محور، تیترهای بزرگ، تصویرسازی تبلیغاتی فانتزی و خوانایی بالا

برای انتشار کاروسل از کاور ۴:۵ استفاده کن؛ کاور ۹:۱۶ برای ریلز یا استوری آماده شده است.
""", encoding="utf-8")
    (OUT / "caption.txt").write_text("""هوش مصنوعی فقط برای سرگرمی نیست؛ می‌تواند سرعت، مهارت و فرصت درآمدسازی تو را بیشتر کند.

از یک مسیر شروع کن:
• تولید محتوا برای کسب‌وکارها
• ساخت و فروش فایل‌های دیجیتال
• ارائهٔ خدمات AI برای فریلنسرها
• آموزش مهارتی که خودت بلدی

اما یادت باشد: AI میانبر پولدار شدن نیست. درآمد زمانی ساخته می‌شود که یک مشکل واقعی را برای یک گروه مشخص، با کیفیت و استمرار حل کنی.

این کاروسل را ذخیره کن و برای یک جوان جویای فرصت بفرست.

#هوش_مصنوعی #درآمد_آنلاین #فریلنسری #کسب_درآمد #جوانان #مهارت_دیجیتال #کارآفرینی
""", encoding="utf-8")
    print(f"created {len(paths)} high-resolution images in {OUT}")


if __name__ == "__main__":
    main()

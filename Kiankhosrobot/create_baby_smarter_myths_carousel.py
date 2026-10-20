from __future__ import annotations

"""Generate a seven-slide Persian carousel debunking baby “brain boost” products."""

import math
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "toolkit"))
from fatext import FD  # type: ignore

S = 2
W, H = 1080 * S, 1350 * S
OUT = ROOT / "baby_smarter_myths_carousel"
FONT_DIR = ROOT.parent / "fonttmp" / "fonts" / "ttf"

NAVY = (24, 31, 58)
NAVY2 = (35, 44, 77)
CREAM = (255, 249, 235)
INK = (28, 34, 55)
MUTED = (116, 119, 136)
PURPLE = (115, 86, 214)
LAVENDER = (218, 207, 255)
CORAL = (255, 105, 105)
YELLOW = (255, 201, 74)
TEAL = (50, 194, 168)
WHITE = (255, 255, 255)

F_REG = "Vazirmatn-Regular.ttf"
F_MED = "Vazirmatn-Medium.ttf"
F_BOLD = "Vazirmatn-Bold.ttf"
F_BLACK = "Vazirmatn-Black.ttf"


def sc(v): return int(round(v * S))
def rgba(c, a=255): return (*c, a)
def font(face, size): return ImageFont.truetype(str(FONT_DIR / face), sc(size))


def rect(d, box, fill=None, outline=None, width=1, radius=0):
    d.rounded_rectangle(tuple(sc(v) for v in box), radius=sc(radius), fill=fill,
                        outline=outline, width=sc(width) if outline else 1)


def ellipse(d, box, fill=None, outline=None, width=1):
    d.ellipse(tuple(sc(v) for v in box), fill=fill, outline=outline,
              width=sc(width) if outline else 1)


def line(d, pts, fill, width=2):
    d.line([(sc(x), sc(y)) for x, y in pts], fill=fill, width=sc(width), joint="curve")


def text(im, xy, value, size, fill=INK, face=F_REG, anchor="rt"):
    return FD(im).text((sc(xy[0]), sc(xy[1])), value, font=font(face, size), fill=fill, anchor=anchor)


def base(page, dark=False):
    bg = NAVY if dark else CREAM
    im = Image.new("RGBA", (W, H), rgba(bg))
    d = ImageDraw.Draw(im, "RGBA")
    # Soft editorial pattern.
    for x, y, r, c in [(58, 184, 115, PURPLE), (1030, 560, 130, TEAL), (80, 1110, 90, YELLOW)]:
        ellipse(d, (x-r, y-r, x+r, y+r), fill=rgba(c, 14 if dark else 18))
    text(im, (72, 70), f"{page:02d} / 07", 17, LAVENDER if dark else PURPLE, F_BOLD, "la")
    text(im, (1008, 70), "رشد نوزاد • بدون اغراق", 16, LAVENDER if dark else MUTED, F_BOLD, "ra")
    line(d, [(72, 105), (1008, 105)], rgba(WHITE if dark else INK, 35), 1)
    text(im, (1008, 1290), "آموزش والدین | جایگزین ارزیابی پزشک نیست", 14,
         rgba(WHITE if dark else MUTED, 190), F_REG, "ra")
    return im


def pill(im, x, y, label, color=PURPLE, dark=False):
    d = ImageDraw.Draw(im, "RGBA")
    w = max(150, 28 + len(label) * 10)
    rect(d, (x-w, y, x, y+42), fill=rgba(color, 30 if not dark else 55),
         outline=rgba(color, 180), width=1, radius=21)
    text(im, (x-18, y+21), label, 18, color if not dark else WHITE, F_BOLD, "rm")


def number_badge(im, n, color):
    d = ImageDraw.Draw(im, "RGBA")
    ellipse(d, (82, 160, 194, 272), fill=rgba(color, 255))
    text(im, (138, 216), str(n), 48, WHITE if color != YELLOW else INK, F_BLACK, "mm")


def cross_badge(im, x=870, y=1110):
    d = ImageDraw.Draw(im, "RGBA")
    ellipse(d, (x-44, y-44, x+44, y+44), fill=rgba(CORAL, 255))
    line(d, [(x-18, y-18), (x+18, y+18)], rgba(WHITE, 255), 7)
    line(d, [(x+18, y-18), (x-18, y+18)], rgba(WHITE, 255), 7)


def footer_takeaway(im, title, body, color=TEAL, dark=False):
    d = ImageDraw.Draw(im, "RGBA")
    fill = rgba((255,255,255), 18) if dark else rgba(color, 24)
    rect(d, (72, 1038, 1008, 1218), fill=fill, outline=rgba(color, 150), width=2, radius=26)
    ellipse(d, (112, 1091, 160, 1139), fill=rgba(color, 255))
    text(im, (958, 1077), title, 23, color if not dark else WHITE, F_BLACK, "rt")
    text(im, (958, 1137), body, 20, WHITE if dark else INK, F_MED, "rt")


def icon_blocks(im):
    d = ImageDraw.Draw(im, "RGBA")
    rect(d, (205, 490, 425, 710), fill=rgba(PURPLE), radius=28)
    rect(d, (442, 398, 670, 710), fill=rgba(YELLOW), radius=28)
    rect(d, (687, 520, 902, 710), fill=rgba(TEAL), radius=28)
    text(im, (315, 600), "A+", 66, WHITE, F_BLACK, "mm")
    # Fake “brain” label on the expensive toy.
    ellipse(d, (500, 454, 612, 566), fill=rgba(CORAL, 230))
    line(d, [(525, 512), (548, 480), (569, 531), (590, 493)], rgba(WHITE), 6)
    text(im, (795, 614), "IQ", 56, WHITE, F_BLACK, "mm")
    # Price tag.
    rect(d, (360, 756, 730, 848), fill=rgba(WHITE), outline=rgba(CORAL), width=3, radius=20)
    text(im, (545, 802), "گران‌تر ≠ رشد بیشتر", 28, CORAL, F_BLACK, "mm")


def icon_cards(im):
    d = ImageDraw.Draw(im, "RGBA")
    rect(d, (215, 420, 555, 790), fill=rgba(WHITE), outline=rgba(PURPLE), width=5, radius=26)
    rect(d, (520, 470, 865, 840), fill=rgba(WHITE), outline=rgba(TEAL), width=5, radius=26)
    text(im, (385, 540), "الف", 84, PURPLE, F_BLACK, "mm")
    text(im, (692, 590), "۱ ۲ ۳", 64, TEAL, F_BLACK, "mm")
    line(d, [(312, 670), (460, 670)], rgba(LAVENDER), 10)
    line(d, [(615, 716), (770, 716)], rgba((190,235,225)), 10)
    # pressure arrows
    line(d, [(165, 610), (210, 610)], rgba(CORAL), 5)
    line(d, [(870, 660), (920, 660)], rgba(CORAL), 5)


def icon_phone(im):
    d = ImageDraw.Draw(im, "RGBA")
    rect(d, (355, 350, 725, 870), fill=rgba(NAVY2), radius=52)
    rect(d, (382, 410, 698, 790), fill=rgba(LAVENDER), radius=24)
    ellipse(d, (490, 505, 590, 605), fill=rgba(YELLOW))
    line(d, [(540, 605), (540, 700)], rgba(TEAL), 14)
    line(d, [(540, 648), (475, 710)], rgba(TEAL), 12)
    line(d, [(540, 648), (605, 710)], rgba(TEAL), 12)
    ellipse(d, (510, 812, 570, 842), fill=rgba(MUTED))
    # pause sign
    rect(d, (763, 520, 890, 647), fill=rgba(CORAL), radius=64)
    rect(d, (799, 553, 816, 614), fill=rgba(WHITE), radius=4)
    rect(d, (837, 553, 854, 614), fill=rgba(WHITE), radius=4)


def icon_music(im):
    d = ImageDraw.Draw(im, "RGBA")
    # Headphones around baby face.
    ellipse(d, (370, 410, 710, 750), fill=rgba(LAVENDER))
    ellipse(d, (448, 488, 632, 672), fill=rgba((255,224,188)))
    ellipse(d, (492, 542, 510, 560), fill=rgba(INK))
    ellipse(d, (570, 542, 588, 560), fill=rgba(INK))
    d.arc(tuple(sc(v) for v in (515, 555, 565, 610)), 15, 165, fill=rgba(CORAL), width=sc(5))
    d.arc(tuple(sc(v) for v in (404, 438, 676, 710)), 190, 350, fill=rgba(PURPLE), width=sc(25))
    rect(d, (378, 555, 440, 680), fill=rgba(PURPLE), radius=20)
    rect(d, (640, 555, 702, 680), fill=rgba(PURPLE), radius=20)
    for x, y, c in [(250,440,YELLOW),(800,420,TEAL),(830,720,CORAL)]:
        line(d, [(x,y),(x,y+90),(x-42,y+105)], rgba(c), 9)
        ellipse(d, (x-70,y+88,x-26,y+132), fill=rgba(c))


def icon_bottle(im):
    d = ImageDraw.Draw(im, "RGBA")
    rect(d, (390, 402, 690, 850), fill=rgba(WHITE), outline=rgba(PURPLE), width=5, radius=36)
    rect(d, (438, 328, 642, 425), fill=rgba(NAVY2), radius=18)
    rect(d, (430, 526, 650, 716), fill=rgba(YELLOW), radius=20)
    text(im, (540, 577), "BRAIN", 25, INK, F_BLACK, "mm")
    text(im, (540, 635), "BOOST", 33, PURPLE, F_BLACK, "mm")
    ellipse(d, (750, 508, 824, 582), fill=rgba(CORAL))
    ellipse(d, (792, 610, 880, 698), fill=rgba(TEAL))
    ellipse(d, (250, 660, 334, 744), fill=rgba(YELLOW))


def icon_parent_baby(im):
    d = ImageDraw.Draw(im, "RGBA")
    # Parent
    ellipse(d, (208, 430, 350, 572), fill=rgba((255,205,160)))
    d.pieslice(tuple(sc(v) for v in (188,390,370,565)), 180, 360, fill=rgba(NAVY2))
    rect(d, (150, 570, 410, 920), fill=rgba(PURPLE), radius=80)
    # Baby
    ellipse(d, (610, 520, 748, 658), fill=rgba((255,220,182)))
    d.pieslice(tuple(sc(v) for v in (595,488,760,640)), 180, 360, fill=rgba(YELLOW))
    rect(d, (555, 655, 805, 900), fill=rgba(TEAL), radius=75)
    # Warm connection between caregiver and baby.
    line(d, [(365, 620), (585, 654)], rgba(CORAL), 16)
    text(im, (530, 540), "♥", 54, CORAL, F_BLACK, "mm")


def slide1():
    im = base(1, dark=True)
    d = ImageDraw.Draw(im, "RGBA")
    pill(im, 1008, 154, "اسطوره‌شکنی رشد نوزاد", TEAL, True)
    text(im, (1008, 265), "پنج کاری که نوزادت را", 55, WHITE, F_BLACK, "rt")
    text(im, (1008, 350), "«باهوش‌تر» نمی‌کند", 70, YELLOW, F_BLACK, "rt")
    text(im, (1008, 452), "این پنج کار فقط پول دور ریختنه", 29, LAVENDER, F_BOLD, "rt")
    # Hero: baby face surrounded by five false promises.
    ellipse(d, (370, 580, 710, 920), fill=rgba(LAVENDER, 255))
    ellipse(d, (442, 650, 638, 846), fill=rgba((255,218,180), 255))
    ellipse(d, (485, 710, 505, 730), fill=rgba(INK))
    ellipse(d, (575, 710, 595, 730), fill=rgba(INK))
    d.arc(tuple(sc(v) for v in (515,730,565,790)), 15, 165, fill=rgba(CORAL), width=sc(6))
    for i, (x,y,c,label) in enumerate([(205,610,PURPLE,"A+"),(790,600,TEAL,"APP"),(220,860,YELLOW,"IQ"),(790,850,CORAL,"♪"),(540,1030,PURPLE,"+")]):
        ellipse(d, (x-58,y-58,x+58,y+58), fill=rgba(c))
        text(im, (x,y), label, 27, WHITE if c != YELLOW else INK, F_BLACK, "mm")
    text(im, (1008, 1162), "ورق بزن؛ آخرش می‌گیم چه چیزی واقعاً کمک می‌کند.", 22, WHITE, F_BOLD, "rt")
    return im


def content_slide(page, n, title1, title2, body1, body2, color, icon_fn):
    im = base(page)
    d = ImageDraw.Draw(im, "RGBA")
    number_badge(im, n, color)
    text(im, (1008, 170), title1, 45, INK, F_BLACK, "rt")
    text(im, (1008, 232), title2, 45, color, F_BLACK, "rt")
    line(d, [(72, 302), (1008, 302)], rgba(color, 130), 3)
    icon_fn(im)
    cross_badge(im, 915, 900)
    footer_takeaway(im, body1, body2, color)
    return im


def slide2(): return content_slide(2, 1, "اسباب‌بازی‌های گران با برچسب", "«آموزشی» و «افزایش IQ»", "قیمت، معیار رشد مغز نیست.", "بازی ساده با یک بزرگسال پاسخ‌گو، ارزشمندتر است.", PURPLE, icon_blocks)
def slide3(): return content_slide(3, 2, "فلش‌کارت و آموزش اجباری", "خواندن در نوزادی", "حفظ‌کردن زودهنگام = هوش بیشتر نیست.", "دنبال علاقهٔ نوزاد برو؛ اسم اشیا را در بازی تکرار کن.", TEAL, icon_cards)
def slide4(): return content_slide(4, 3, "اپ‌ها و ویدئوهای", "«تقویت مغز نوزاد»", "صفحه‌نمایش جای تعامل زنده را نمی‌گیرد.", "چهره، صدا و پاسخ واقعی شما برای یادگیری مهم‌تر است.", CORAL, icon_phone)
def slide5(): return content_slide(5, 4, "موسیقی کلاسیک برای", "بالا بردن IQ", "موسیقی لذت‌بخش است؛ معجزهٔ IQ نیست.", "با هم آواز بخوانید و ریتم بگیرید؛ هدف ارتباط است.", YELLOW, icon_music)
def slide6(): return content_slide(6, 5, "قطره و مکمل با ادعای", "«تقویت هوش»", "مکملِ بدون نیاز پزشکی، هوش را بیشتر نمی‌کند.", "فقط مکمل توصیه‌شده برای سن و شرایط نوزاد را بدهید.", PURPLE, icon_bottle)


def slide7():
    im = base(7, dark=True)
    d = ImageDraw.Draw(im, "RGBA")
    pill(im, 1008, 154, "پس چه چیزی کمک می‌کند؟", TEAL, True)
    text(im, (1008, 250), "رشد مغز از رابطه می‌آید،", 51, WHITE, F_BLACK, "rt")
    text(im, (1008, 320), "نه از شعار روی جعبه", 55, YELLOW, F_BLACK, "rt")
    icon_parent_baby(im)
    items = ["پاسخ‌دادن به نگاه و صدا", "حرف‌زدن، کتاب و آواز", "بازی آزاد روی زمین", "خواب، تغذیه و مراقبت پزشکی"]
    y = 942
    for i, item in enumerate(items):
        x = 100 if i % 2 == 0 else 555
        yy = y + (i//2)*92
        rect(d, (x, yy, x+425, yy+68), fill=rgba(WHITE, 20), outline=rgba(TEAL, 95), width=1, radius=16)
        ellipse(d, (x+24, yy+21, x+50, yy+47), fill=rgba(TEAL))
        text(im, (x+400, yy+34), item, 18, WHITE, F_BOLD, "rm")
    text(im, (1008, 1198), "ذخیره کن و برای یک والد تازه‌کار بفرست.", 22, LAVENDER, F_BOLD, "rt")
    return im


def save_slide(im, path):
    flat = Image.new("RGB", im.size, CREAM)
    flat.paste(im, mask=im.getchannel("A"))
    flat.resize((1080, 1350), Image.Resampling.LANCZOS).save(path, optimize=True)


def make_preview(paths, path):
    tw, th, cols = 324, 405, 3
    rows = math.ceil(len(paths) / cols)
    out = Image.new("RGB", (cols*tw+48, rows*th+48), NAVY)
    d = ImageDraw.Draw(out)
    for i, p in enumerate(paths):
        im = Image.open(p).convert("RGB").resize((tw, th), Image.Resampling.LANCZOS)
        x, y = 24+(i%cols)*tw, 24+(i//cols)*th
        out.paste(im, (x,y)); d.rectangle((x,y,x+tw-1,y+th-1), outline=LAVENDER, width=2)
    out.save(path, optimize=True)


def main():
    OUT.mkdir(exist_ok=True)
    slides = [slide1(), slide2(), slide3(), slide4(), slide5(), slide6(), slide7()]
    paths = []
    for i, im in enumerate(slides, 1):
        p = OUT / f"slide_{i:02d}.png"; save_slide(im, p); paths.append(p)
    make_preview(paths, OUT / "carousel_preview.png")
    (OUT / "caption.txt").write_text("""۵ کاری که نوزادت را «باهوش‌تر» نمی‌کند 🧠

اسباب‌بازی گران، فلش‌کارت، اپ‌های موسوم به تقویت مغز، پخش موسیقی کلاسیک و مکمل‌های تبلیغاتی میان‌بُر افزایش هوش نیستند.

رشد سالم بیشتر با تعامل رفت‌وبرگشتی شکل می‌گیرد: به نگاه و صدای نوزاد پاسخ بدهید، با او حرف بزنید، کتاب بخوانید، آواز بخوانید و فرصت بازی آزاد و امن بدهید. خواب، تغذیه و مراقبت‌های معمول پزشکی هم پایه‌های مهم رشدند.

مکمل‌ها را فقط مطابق توصیهٔ پزشک و برنامهٔ رسمی متناسب با سن و شرایط کودک استفاده کنید. دربارهٔ صفحه‌نمایش نیز توصیه‌های متخصص کودک را رعایت کنید.

این محتوا آموزشی است و جایگزین ارزیابی پزشک اطفال نیست.

منابع: American Academy of Pediatrics؛ WHO Guidelines on physical activity, sedentary behaviour and sleep؛ Harvard Center on the Developing Child.

#رشد_نوزاد #هوش_نوزاد #بازی_با_نوزاد #والدگری #تربیت_کودک #پزشک_اطفال
""", encoding="utf-8")
    (OUT / "README.md").write_text("""# کاروسل ۰۱ از فهرست ۸۰ عنوان ترند

**عنوان:** ۵ کاری که نوزادت را «باهوش‌تر» نمی‌کند

- ۷ اسلاید PNG
- ابعاد: ۱۰۸۰×۱۳۵۰ (نسبت ۴:۵)
- فونت: Vazirmatn
- ترتیب انتشار: `slide_01.png` تا `slide_07.png`
- کپشن آماده در `caption.txt`
""", encoding="utf-8")
    print(f"Created {len(paths)} slides in {OUT}")

if __name__ == "__main__": main()

from __future__ import annotations

"""High-resolution Persian Instagram carousel: effective infant latch.

Carousel slides: 7680x9600, 4:5.
Separate cover: 7680x13653, 9:16.
"""

import gc
import math
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "toolkit"))
from fatext import FD  # type: ignore

OUT = ROOT / "latch_carousel"
FONT_DIR = ROOT.parent / "fonttmp" / "fonts" / "ttf"

# Light background + high-contrast green, red, and mustard palette.
BG = (252, 250, 242)
BG_BLUE = (241, 249, 246)
TEXT = (21, 39, 35)
MUTED = (70, 82, 75)
GREEN = (38, 132, 77)
GREEN_BRIGHT = (76, 169, 98)
GREEN_PALE = (224, 244, 226)
RED = (211, 55, 64)
RED_PALE = (253, 228, 225)
MUSTARD = (184, 132, 20)
MUSTARD_PALE = (252, 241, 198)
WHITE = (255, 255, 250)

F_REG = "Vazirmatn-Regular.ttf"
F_MED = "Vazirmatn-Medium.ttf"
F_SEMI = "Vazirmatn-SemiBold.ttf"
F_BOLD = "Vazirmatn-Bold.ttf"
F_BLACK = "Vazirmatn-Black.ttf"


def rgba(c, a=255):
    return (*c, int(a))


class Canvas:
    def __init__(self, bw, bh, out_w=7680):
        self.bw, self.bh = bw, bh
        self.w, self.h = out_w, int(round(out_w * bh / bw))
        self.s = self.w / bw
        self.im = self.background()
        self.d = ImageDraw.Draw(self.im, "RGBA")

    def x(self, v): return int(round(v * self.s))
    def box(self, b): return tuple(self.x(v) for v in b)

    def background(self):
        sw = 320
        sh = max(320, int(round(sw * self.bh / self.bw)))
        img = Image.new("RGB", (sw, sh))
        px = img.load()
        for y in range(sh):
            t = y / max(1, sh - 1)
            if t < .55:
                a, b, q = BG, BG_BLUE, t / .55
            else:
                a, b, q = BG_BLUE, (255, 246, 239), (t-.55)/.45
            col = tuple(int(a[i]*(1-q)+b[i]*q) for i in range(3))
            for x in range(sw): px[x, y] = col
        img = img.resize((self.w, self.h), Image.Resampling.BICUBIC).convert("RGBA")
        glow = Image.new("RGBA", (sw, sh), (0,0,0,0))
        gd = ImageDraw.Draw(glow, "RGBA")
        gd.ellipse((-90, -80, 180, 230), fill=rgba(GREEN_BRIGHT, 34))
        gd.ellipse((185, 70, 410, 330), fill=rgba(MUSTARD, 26))
        gd.ellipse((40, sh-230, 300, sh+70), fill=rgba(RED, 24))
        glow = glow.filter(ImageFilter.GaussianBlur(18))
        glow = glow.resize((self.w, self.h), Image.Resampling.BICUBIC)
        return Image.alpha_composite(img, glow)

    def line(self, pts, fill, width=2, joint="curve"):
        self.d.line([(self.x(x), self.x(y)) for x,y in pts], fill=fill,
                    width=max(1, self.x(width)), joint=joint)
    def rect(self, b, fill=None, outline=None, width=1, radius=0):
        self.d.rounded_rectangle(self.box(b), fill=fill, outline=outline,
                                 width=self.x(width) if outline else 1, radius=self.x(radius))
    def ellipse(self, b, fill=None, outline=None, width=1):
        self.d.ellipse(self.box(b), fill=fill, outline=outline,
                       width=self.x(width) if outline else 1)
    def polygon(self, pts, fill):
        self.d.polygon([(self.x(x), self.x(y)) for x,y in pts], fill=fill)
    def arc(self, b, start, end, fill, width=2):
        self.d.arc(self.box(b), start, end, fill=fill, width=self.x(width))
    def text(self, xy, value, size, fill=TEXT, family=F_REG, anchor="rt"):
        return FD(self.im).text((self.x(xy[0]), self.x(xy[1])), value,
                                font=ImageFont.truetype(str(FONT_DIR / family), max(10, int(size*self.s))),
                                fill=fill, anchor=anchor)
    def pill(self, x, y, label, color, width=None):
        width = width or max(140, len(label)*13+44)
        self.rect((x,y,x+width,y+40), fill=rgba(color, 28), outline=rgba(color,220), width=2, radius=20)
        self.text((x+width/2,y+20), label, 17, color, F_BOLD, "mm")


def grid(c):
    for x in range(0, c.bw+1, 90): c.line([(x,0),(x,c.bh)], rgba(GREEN, 12), 1)
    for y in range(0, c.bh+1, 90): c.line([(0,y),(c.bw,y)], rgba(MUSTARD, 12), 1)
    for x,y,col in [(72,160,RED),(1004,250,GREEN),(120,c.bh-150,MUSTARD),(960,c.bh-210,RED)]:
        c.ellipse((x-3,y-3,x+3,y+3), fill=rgba(col,180))


def chrome(c, page, right="BREASTFEEDING / LATCH"):
    c.text((74,58), page, 18, GREEN, F_BOLD, "la")
    c.text((1006,58), right, 15, MUSTARD, F_BOLD, "ra")
    c.line([(74,90),(1006,90)], rgba(TEXT,45), 1)
    c.line([(74,c.bh-62),(244,c.bh-62)], rgba(RED,220), 4)
    c.text((260,c.bh-70), "راهنمای دیداری شیردهی", 15, MUTED, F_REG, "la")
    c.line([(1006,c.bh-110),(1006,c.bh-62),(958,c.bh-62)], rgba(GREEN,220), 4)


def title(c, tag, lines, sub, accent, y=142, size=54):
    c.pill(74,y,tag,accent,max(150,len(tag)*13+40))
    ty=y+88
    for i, line in enumerate(lines):
        c.text((1006,ty+i*(size+8)), line, size, accent if i==0 else TEXT, F_BLACK, "rt")
    c.text((1006,ty+len(lines)*(size+8)+18), sub, 24, MUTED, F_MED, "rt")


def spark(c,x,y,r,col):
    c.polygon([(x,y-r),(x+5,y-5),(x+r,y),(x+5,y+5),(x,y+r),(x-5,y+5),(x-r,y),(x-5,y-5)], rgba(col,230))


def breast_side(c, x, y, scale=1.0, accent=GREEN):
    """Abstract side-view latch diagram, intentionally non-photographic and educational."""
    # breast silhouette and areola
    c.ellipse((x-205*scale,y-150*scale,x+115*scale,y+184*scale), fill=rgba((255,220,196),245), outline=rgba(MUSTARD,170), width=3)
    c.ellipse((x-35*scale,y-16*scale,x+55*scale,y+75*scale), fill=rgba((224,133,103),245), outline=rgba(RED,150), width=2)
    c.ellipse((x+25*scale,y+13*scale,x+77*scale,y+65*scale), fill=rgba((196,82,75),255))
    # baby head/mouth at the right side, with a wide opening around areola
    c.ellipse((x+95*scale,y-132*scale,x+250*scale,y+26*scale), fill=rgba((247,202,164),255), outline=rgba(TEXT,120), width=2)
    c.ellipse((x+210*scale,y-50*scale,x+228*scale,y-32*scale), fill=rgba(TEXT,210))
    c.arc((x+215*scale,y-84*scale,x+278*scale,y-20*scale), 80, 210, rgba(TEXT,220), max(3,int(5*scale)))
    # wide mouth / deep latch marker
    c.arc((x+58*scale,y-45*scale,x+152*scale,y+86*scale), 255, 85, rgba(accent,255), max(4,int(10*scale)))
    c.line([(x+55*scale,y+20*scale),(x+2*scale,y+30*scale)], rgba(accent,230), max(3,int(7*scale)))
    # chin contact and free nose marker
    c.line([(x+145*scale,y+30*scale),(x+90*scale,y+84*scale)], rgba(GREEN,230), max(3,int(7*scale)))
    c.line([(x+216*scale,y-102*scale),(x+292*scale,y-118*scale)], rgba(MUSTARD,220), max(3,int(6*scale)))


def baby_badge(c, x, y, label, col):
    c.ellipse((x-22,y-22,x+22,y+22), fill=rgba(col,230))
    c.text((x+42,y), label, 20, col, F_BOLD, "lm")


def slide_1():
    c=Canvas(1080,1350); grid(c); chrome(c,"01 / 07")
    title(c,"تعریف",["اتصال مؤثر", "یعنی چه؟"],"Latch خوب، فقط گرفتن نوک سینه نیست.",GREEN,142,58)
    c.rect((74,580,470,1100), fill=rgba(WHITE,245), outline=rgba(GREEN,150), width=2, radius=26)
    breast_side(c,235,830,.75,GREEN)
    spark(c,118,632,16,MUSTARD); spark(c,425,1020,16,RED)
    c.pill(578,590,"۳ نشانهٔ اصلی",RED,180)
    rows=[("دهان کاملاً باز", "بخش زیادی از هاله داخل دهان است.", GREEN),
          ("لب‌ها به بیرون", "مثل دهان یک ماهی کوچک.", RED),
          ("درد و بلع منظم", "مادر راحت است و صدای قورت‌دادن شنیده می‌شود.", MUSTARD)]
    y=694
    for head,body,col in rows:
        c.rect((545,y,1006,y+124), fill=rgba(WHITE,235), outline=rgba(col,150), width=2, radius=17)
        c.ellipse((580,y+41,620,y+81), fill=rgba(col,230))
        c.text((650,y+25),head,23,col,F_BOLD,"lt")
        c.text((650,y+73),body,21,MUTED,F_REG,"lt")
        y+=146
    c.rect((545,1140,1006,1205), fill=rgba(GREEN_PALE,235), outline=rgba(GREEN,170), width=1, radius=14)
    c.text((965,1168),"هدف: شیر خوردن بدون درد و با بلع مؤثر",18,GREEN,F_SEMI,"rt")
    return c


def slide_2():
    c=Canvas(1080,1350); grid(c); chrome(c,"02 / 07")
    title(c,"نشانهٔ اول",["دهان کاملاً باز", "لب‌ها بیرون"],"هرچه دهان بازتر، گرفتن هاله عمیق‌تر.",RED,142,56)
    c.rect((74,580,450,1110), fill=rgba(WHITE,245), outline=rgba(RED,145), width=2, radius=26)
    breast_side(c,230,830,.76,RED)
    c.arc((92,640,400,1000), 150, 310, rgba(RED,210), 7)
    c.text((230,1045),"اتصال عمیق",23,RED,F_BLACK,"mm")
    c.pill(575,590,"چک کن",MUSTARD,130)
    checks=[("دهان نوزاد کاملاً باز است",GREEN),
            ("بخش زیادی از هاله داخل دهان است",MUSTARD),
            ("لب پایین به سمت بیرون برگشته",RED),
            ("فقط نوک سینه گرفته نشده",GREEN)]
    y=690
    for text,col in checks:
        c.rect((548,y,1006,y+100), fill=rgba(WHITE,235), outline=rgba(col,145), width=2, radius=16)
        c.ellipse((580,y+34,616,y+70), fill=rgba(col,235))
        c.text((648,y+49),text,22,TEXT,F_SEMI,"lt")
        y+=123
    c.rect((548,1185,1006,1240), fill=rgba(MUSTARD_PALE,245), outline=rgba(MUSTARD,175), width=1, radius=14)
    c.text((965,1213),"دهان باز = فرصت بهتر برای یک Latch عمیق",18,MUSTARD,F_BOLD,"rt")
    return c


def slide_3():
    c=Canvas(1080,1350); grid(c); chrome(c,"03 / 07")
    title(c,"نشانهٔ دوم",["چانه چسبیده،", "بینی آزاد"],"بدن نوزاد نزدیک و در یک راستا با سر او باشد.",GREEN,142,55)
    c.rect((74,580,450,1110), fill=rgba(WHITE,245), outline=rgba(GREEN,145), width=2, radius=26)
    breast_side(c,235,830,.76,GREEN)
    c.line([(420,650),(420,780)], rgba(GREEN,190), 6)
    c.text((420,625),"بینی آزاد",19,GREEN,F_BOLD,"mm")
    c.line([(340,930),(430,1005)], rgba(RED,180), 6)
    c.text((405,1045),"چانه چسبیده",19,RED,F_BOLD,"mm")
    items=[("چانه به سینه تکیه دارد", "فشار روی بینی ایجاد نمی‌شود.", GREEN),
           ("بینی آزاد است", "تنفس نوزاد باید راحت بماند.", MUSTARD),
           ("سر، گردن و بدن هم‌راستا", "نوزاد برای چرخاندن سر مجبور نیست.", RED)]
    y=635
    for head,body,col in items:
        c.rect((552,y,1006,y+155), fill=rgba(WHITE,235), outline=rgba(col,145), width=2, radius=18)
        baby_badge(c,595,y+48,"✓",col)
        c.text((665,y+27),head,22,col,F_BOLD,"lt")
        c.text((665,y+84),body,20,MUTED,F_REG,"lt")
        y+=175
    return c


def slide_4():
    c=Canvas(1080,1350); grid(c); chrome(c,"04 / 07")
    title(c,"حس مادر",["درد تیز و مداوم؟", "نباید باشد."],"کمی کشش ممکن است؛ درد مداوم یعنی اتصال را دوباره بررسی کن.",RED,142,52)
    c.rect((74,580,450,1110), fill=rgba(RED_PALE,245), outline=rgba(RED,150), width=2, radius=26)
    c.ellipse((160,675,365,880), fill=rgba(WHITE,220), outline=rgba(RED,180), width=3)
    c.arc((205,725,320,840), 35, 320, rgba(RED,230), 9)
    c.line([(190,925),(360,925)], rgba(RED,200), 5)
    c.text((265,990),"درد مداوم",24,RED,F_BLACK,"mm")
    c.text((265,1038),"علامت نیاز به تنظیم",18,MUTED,F_REG,"mm")
    c.pill(575,590,"بلع مؤثر",GREEN,150)
    rows=[("صدای قورت‌دادن منظم", "مکیدن با مکث‌های کوتاه و بلع همراه است.", GREEN),
          ("گونه‌ها گرد می‌مانند", "گونهٔ گودافتاده می‌تواند نشانهٔ مکیدن نامؤثر باشد.", MUSTARD),
          ("مادر راحت است", "درد تیز، سوزش یا فشار مداوم را نادیده نگیر.", RED)]
    y=690
    for head,body,col in rows:
        c.rect((548,y,1006,y+145), fill=rgba(WHITE,235), outline=rgba(col,145), width=2, radius=18)
        c.text((965,y+30),head,23,col,F_BOLD,"rt")
        c.text((965,y+87),body,20,MUTED,F_REG,"rt")
        y+=166
    c.rect((548,1185,1006,1240), fill=rgba(GREEN_PALE,245), outline=rgba(GREEN,165), width=1, radius=14)
    c.text((965,1213),"اتصال مؤثر باید برای مادر هم راحت باشد.",18,GREEN,F_BOLD,"rt")
    return c


def nipple(c,x,y,good=True):
    col=GREEN if good else RED
    c.ellipse((x-110,y-85,x+110,y+85), fill=rgba(WHITE,235), outline=rgba(col,180), width=3)
    if good:
        c.ellipse((x-44,y-38,x+44,y+38), fill=rgba((221,146,115),255), outline=rgba(col,220), width=4)
        c.text((x,y+105),"گرد",23,GREEN,F_BLACK,"mm")
    else:
        c.polygon([(x-72,y-28),(x+65,y-16),(x+38,y+16),(x-70,y+28)], fill=rgba((221,146,115),255))
        c.line([(x-56,y-28),(x+45,y+26)], rgba(RED,230), 5)
        c.text((x,y+105),"صاف یا نوک‌تیز",21,RED,F_BLACK,"mm")


def slide_5():
    c=Canvas(1080,1350); grid(c); chrome(c,"05 / 07")
    title(c,"نشانهٔ بعدی",["نوک سینه بعد از", "شیردهی چه شکلی است؟"],"ظاهر نوک سینه می‌تواند سرنخ خوبی از اتصال باشد.",MUSTARD,142,48)
    c.rect((74,590,1006,1115), fill=rgba(WHITE,240), outline=rgba(MUSTARD,145), width=2, radius=26)
    c.pill(135,650,"احتمالاً اتصال خوب",GREEN,210)
    nipple(c,275,820,True)
    c.line([(445,710),(445,1000)], rgba(MUSTARD,90), 2)
    c.pill(575,650,"نیاز به بررسی",RED,168)
    nipple(c,790,820,False)
    c.rect((128,1010,421,1080), fill=rgba(GREEN_PALE,245), outline=rgba(GREEN,145), width=1, radius=14)
    c.text((274,1046),"گرد و طبیعی",19,GREEN,F_BOLD,"mm")
    c.rect((638,1010,943,1080), fill=rgba(RED_PALE,245), outline=rgba(RED,145), width=1, radius=14)
    c.text((790,1046),"صاف / خط‌دار",19,RED,F_BOLD,"mm")
    c.rect((74,1155,1006,1230), fill=rgba(MUSTARD_PALE,245), outline=rgba(MUSTARD,170), width=1, radius=14)
    c.text((965,1192),"اگر نوک سینه صاف یا فشرده شد، اتصال را دوباره برقرار کن.",20,MUSTARD,F_SEMI,"rt")
    return c


def slide_6():
    c=Canvas(1080,1350); grid(c); chrome(c,"06 / 07")
    title(c,"اصلاح اتصال",["اگر درست نبود،", "دوباره امتحان کن."],"قطع مکش و شروع دوباره، بهتر از تحمل درد است.",GREEN,142,54)
    c.rect((74,580,450,1110), fill=rgba(WHITE,245), outline=rgba(GREEN,145), width=2, radius=26)
    c.line([(180,780),(350,780),(350,940),(180,940),(180,1030),(350,1030)], rgba(MUSTARD,160), 5)
    steps=[(180,780,"۱",RED,"مکث"),(350,780,"۲",MUSTARD,"نزدیک"),(350,940,"۳",GREEN,"دهان باز"),(180,940,"۴",RED,"اتصال")]
    for x,y,n,col,lab in steps:
        c.ellipse((x-38,y-38,x+38,y+38), fill=rgba(col,235), outline=rgba(WHITE,180), width=2)
        c.text((x,y),n,27,TEXT,F_BLACK,"mm")
        c.text((x,y+65),lab,17,col,F_BOLD,"mm")
    c.text((265,660),"۴ قدم ساده",22,TEXT,F_BLACK,"mm")
    actions=[("۱", "با انگشت تمیز، مکش را آرام قطع کن.", RED),
             ("۲", "بینی نوزاد را روبه‌روی نوک سینه تنظیم کن.", MUSTARD),
             ("۳", "صبر کن دهان کاملاً باز شود.", GREEN),
             ("۴", "نوزاد را به سمت سینه بیاور؛ نه سینه را به نوزاد.", RED)]
    y=635
    for n,body,col in actions:
        c.rect((548,y,1006,y+110), fill=rgba(WHITE,235), outline=rgba(col,145), width=2, radius=16)
        c.ellipse((580,y+36,618,y+74), fill=rgba(col,235))
        c.text((599,y+55),n,18,TEXT,F_BLACK,"mm")
        c.text((660,y+55),body,20,MUTED,F_REG,"lt")
        y+=130
    c.rect((548,1175,1006,1230), fill=rgba(RED_PALE,245), outline=rgba(RED,165), width=1, radius=14)
    c.text((965,1203),"درد مداوم یا نگرانی؟ از ماما/مشاور شیردهی کمک بگیر.",17,RED,F_BOLD,"rt")
    return c


def slide_7():
    c=Canvas(1080,1350); grid(c); chrome(c,"07 / 07","SAVE / CHECK / SHARE")
    title(c,"چک سریع",["قبل از ادامه،", "این‌ها را ببین."],"یک اتصال خوب با چند نشانهٔ ساده قابل بررسی است.",MUSTARD,142,56)
    c.rect((74,580,1006,1080), fill=rgba(WHITE,245), outline=rgba(GREEN,145), width=2, radius=26)
    checks=[("دهان کاملاً باز؟",GREEN),("لب‌ها به بیرون؟",RED),("چانه چسبیده و بینی آزاد؟",MUSTARD),
            ("صدای بلع منظم؟",GREEN),("مادر بدون درد مداوم؟",RED),("نوک سینه گرد بعد از شیر؟",MUSTARD)]
    y=640
    for label,col in checks:
        c.rect((130,y,950,y+60), fill=rgba(col,22), outline=rgba(col,110), width=1, radius=14)
        c.ellipse((160,y+17,194,y+51), fill=rgba(col,230))
        c.text((230,y+30),label,22,TEXT,F_SEMI,"lt")
        y+=68
    c.rect((74,1120,1006,1200), fill=rgba(GREEN,230), radius=18)
    c.text((540,1160),"ذخیره کن و برای یک مادر بفرست.",26,WHITE,F_BLACK,"mm")
    c.text((1006,1250),"این محتوا آموزشی است؛ در صورت نگرانی با متخصص مشورت کن.",17,MUTED,F_REG,"rt")
    return c


def cover():
    c=Canvas(1080,1920); grid(c)
    c.text((74,66),"COVER / 09:16",18,GREEN,F_BOLD,"la")
    c.text((1006,66),"BREASTFEEDING / LATCH",15,MUSTARD,F_BOLD,"ra")
    c.line([(74,98),(1006,98)], rgba(TEXT,45), 1)
    c.pill(74,170,"راهنمای دیداری شیردهی",RED,245)
    c.text((1006,300),"اتصال مؤثر",88,TEXT,F_BLACK,"rt")
    c.text((1006,410),"نوزاد به سینه",70,RED,F_BLACK,"rt")
    c.text((1006,510),"Latch",100,GREEN,F_BLACK,"rt")
    c.text((1006,650),"دهان باز، هاله بیشتر، درد کمتر",29,MUTED,F_MED,"rt")
    c.rect((74,770,1006,1585), fill=rgba(WHITE,240), outline=rgba(GREEN,150), width=2, radius=32)
    breast_side(c,445,1120,1.35,GREEN)
    c.rect((120,900,388,1010), fill=rgba(GREEN,228), radius=18)
    c.text((254,955),"دهان باز",25,WHITE,F_BLACK,"mm")
    c.rect((650,1220,950,1330), fill=rgba(MUSTARD,228), radius=18)
    c.text((800,1275),"بینی آزاد",25,TEXT,F_BLACK,"mm")
    c.rect((140,1425,430,1535), fill=rgba(RED,228), radius=18)
    c.text((285,1480),"بدون درد مداوم",23,WHITE,F_BLACK,"mm")
    spark(c,145,840,22,MUSTARD); spark(c,902,870,22,RED); spark(c,878,1475,21,GREEN)
    c.rect((74,1670,1006,1790), fill=rgba(GREEN_PALE,245), outline=rgba(GREEN,150), width=1, radius=18)
    c.text((950,1710),"علائم یک Latch عمیق و مؤثر را بشناس",23,GREEN,F_BOLD,"rt")
    c.text((950,1750),"ورق بزن ←",19,MUTED,F_REG,"rt")
    c.line([(74,1860),(244,1860)], rgba(RED,220), 4)
    c.text((260,1852),"آموزش کاربردی شیردهی",17,MUTED,F_REG,"la")
    return c


def save(c, path):
    rgb=Image.new("RGB",c.im.size,BG)
    rgb.paste(c.im,mask=c.im.getchannel("A"))
    rgb.save(path,"JPEG",quality=96,subsampling=0,optimize=True)
    del rgb,c.im; gc.collect()


def preview(paths,out):
    tw,th=324,405; cols=3; rows=math.ceil(len(paths)/cols)
    im=Image.new("RGB",(cols*tw+48,rows*th+48),(245,244,237)); d=ImageDraw.Draw(im)
    for i,p in enumerate(paths):
        src=Image.open(p).convert("RGB")
        if src.height/src.width>1.3:
            ch=int(src.width*1.25); top=(src.height-ch)//2; src=src.crop((0,top,src.width,top+ch))
        src.thumbnail((tw,th),Image.Resampling.LANCZOS)
        thumb=Image.new("RGB",(tw,th),BG); thumb.paste(src,((tw-src.width)//2,(th-src.height)//2))
        x=24+(i%cols)*tw; y=24+(i//cols)*th; im.paste(thumb,(x,y)); d.rectangle((x,y,x+tw-1,y+th-1),outline=GREEN,width=2)
    im.save(out,"JPEG",quality=95,optimize=True)


def main():
    OUT.mkdir(exist_ok=True)
    paths=[]
    p=OUT/"cover_9x16_8k.jpg"; save(cover(),p); paths.append(p)
    for i,maker in enumerate([slide_1,slide_2,slide_3,slide_4,slide_5,slide_6,slide_7],1):
        p=OUT/f"slide_{i:02d}_4x5_8k.jpg"; save(maker(),p); paths.append(p)
    preview(paths,OUT/"carousel_preview.jpg")
    (OUT/"README.md").write_text("""# کاروسل تشخیص اتصال مؤثر نوزاد به سینه (Latch)

- ۷ اسلاید آموزشی: ۷۶۸۰×۹۶۰۰، نسبت ۴:۵
- کاور جداگانه: ۷۶۸۰×۱۳۶۵۳، نسبت ۹:۱۶
- پالت: سبز، قرمز و خردلی روی زمینهٔ روشن
- فونت: Vazirmatn

این طرح آموزشی جایگزین ارزیابی ماما، مشاور شیردهی یا پزشک کودک نیست.
""",encoding="utf-8")
    (OUT/"caption.txt").write_text("""اتصال مؤثر نوزاد به سینه فقط گرفتن نوک سینه نیست.

در یک Latch عمیق معمولاً:
• دهان نوزاد کاملاً باز است و بخش زیادی از هالهٔ سینه را در بر می‌گیرد.
• لب پایین به سمت بیرون برگشته است؛ شبیه دهان یک ماهی کوچک.
• چانه به سینه چسبیده و بینی آزاد است.
• مادر درد تیز و مداوم ندارد و صدای قورت‌دادن منظم شنیده می‌شود.
• بعد از پایان شیردهی، نوک سینه گرد می‌ماند؛ نه صاف، فشرده یا نوک‌تیز.

اگر درد مداوم دارید یا دربارهٔ تغذیهٔ نوزاد نگرانید، از ماما، مشاور شیردهی یا پزشک کودک کمک بگیرید.

این پست آموزشی است و جایگزین ارزیابی تخصصی نیست.

#شیردهی #اتصال_نوزاد #Latch #نوزاد #مادر_و_کودک #مشاور_شیردهی
""",encoding="utf-8")
    print(f"created {len(paths)} images in {OUT}")

if __name__=="__main__": main()

#!/usr/bin/env python3
"""Render six reel-style Persian carousel slides (1080x1920, 9:16).
Requires Pillow, numpy, uharfbuzz and freetype-py; Persian text uses toolkit/fatext.py.
"""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "Kiankhosrobot" / "toolkit"))
from fatext import FD  # noqa: E402

W, H, S = 1080, 1920, 2
AW, AH = 760, 950
P = {
    "night": "#090B20", "deep": "#11142C", "card": "#101329", "card2": "#1B203C",
    "white": "#F7F8FF", "muted": "#D7D9EA", "cyan": "#19E8FF", "pink": "#FF36CD",
    "lime": "#C6FF32", "gold": "#FFC43D", "orange": "#FF7A35", "purple": "#A669FF",
    "red": "#FF4968", "green": "#42F3A4", "skin": "#F2C39D", "hair": "#271A37",
    "cream": "#FFF0D1", "white2": "#EAF1FF", "navy": "#172040",
}
FONT = {
    "regular": ROOT / "fonttmp/fonts/ttf/Vazirmatn-Regular.ttf",
    "medium": ROOT / "fonttmp/fonts/ttf/Vazirmatn-Medium.ttf",
    "bold": ROOT / "fonttmp/fonts/ttf/Vazirmatn-Bold.ttf",
    "extra": ROOT / "fonttmp/fonts/ttf/Vazirmatn-ExtraBold.ttf",
}
DIGITS = "۰۱۲۳۴۵۶۷۸۹"

SLIDES = [
    {
        "title": "غذاهای آلرژی‌زا", "en": "INTRODUCING ALLERGENS", "accent": "cyan",
        "colors": ("#211353", "#8B1D79"), "art": 0,
        "items": [
            (["واکنشِ غذایی پس از مواجهه با غذا", "آشکار می‌شود."], "food"),
            (["ممکن است نخستین بار هنگامِ معرفی", "دیده شود."], "clock"),
            (["معرفیِ ایمن؛ نه حذفِ بی‌دلیل."], "check"),
        ],
    },
    {
        "title": "نشانه‌های واکنش", "en": "REACTION SIGNS", "accent": "pink",
        "colors": ("#07366F", "#087EAE"), "art": 1,
        "items": [
            (["پوست: کهیر، خارش یا ورمِ لب و صورت"], "skin"),
            (["تنفس: سرفهٔ مکرر، خس‌خس یا", "گرفتگیِ گلو"], "breath"),
            (["گوارش: استفراغ یا دل‌درد؛", "بعضی واکنش‌ها دیرتر بروز می‌کنند."], "gut"),
            (["بسیاری از واکنش‌های فوری در چند", "دقیقه تا چند ساعت آغاز می‌شوند."], "clock"),
        ],
    },
    {
        "title": "چرا بی‌دلیل عقب نیندازیم؟", "en": "EARLY INTRODUCTION", "accent": "lime",
        "colors": ("#123F2E", "#438D27"), "art": 2,
        "items": [
            (["تأخیرِ غذاهای آلرژی‌زا، روشِ", "اثبات‌شدهٔ پیشگیری برای همه نیست."], "clock"),
            (["برای بادام‌زمینی، معرفیِ به‌موقع و", "مصرفِ منظم می‌تواند خطر را کم کند."], "peanut"),
            (["شواهد برای همهٔ غذاها یکسان نیست؛", "پیشگیریِ کامل هم تضمین نمی‌شود."], "shield"),
        ],
    },
    {
        "title": "زمان شروع و آمادگی", "en": "WHEN TO START", "accent": "gold",
        "colors": ("#793410", "#B66C17"), "art": 3,
        "items": [
            (["غذای کمکی را حدود ۶ ماهگی،", "با آمادگیِ رشدی شروع کنید."], "clock"),
            (["کنترلِ سر و گردن، نشستن با کمک", "و تواناییِ بلعیدن مهم است."], "baby"),
            (["غذای کمکی پیش از ۴ ماهگی", "توصیه نمی‌شود."], "check"),
            (["اگزمای شدید یا آلرژی به تخم‌مرغ؟", "پیش از بادام‌زمینی با پزشک مشورت کنید."], "doctor"),
        ],
    },
    {
        "title": "معرفیِ ایمن", "en": "SAFE FEEDING", "accent": "purple",
        "colors": ("#401253", "#922B93"), "art": 4,
        "items": [
            (["هر بار یک آلرژنِ جدید؛ کودک سالم", "و نشسته باشد."], "check"),
            (["تخم‌مرغ کاملاً پخته؛ کرهٔ بادام‌زمینی", "رقیق‌شده در پوره."], "food"),
            (["مغزِ کامل یا قاشقِ غلیظِ کرهٔ مغزها", "خطرِ خفگی دارد؛ ندهید."], "alert"),
            (["اگر تحمل کرد، در رژیم بماند؛", "مصرفِ منظمِ بادام‌زمینی مهم است."], "repeat"),
        ],
    },
    {
        "title": "اگر واکنش دیدیم؟", "en": "WHAT TO DO", "accent": "red",
        "colors": ("#58152F", "#A93B2D"), "art": 5,
        "items": [
            (["کهیر یا ورم؟ غذا را متوقف کنید", "و با پزشک کودک تماس بگیرید."], "pause"),
            (["تنگی نفس، تورمِ زبان یا گلو،", "بی‌حالیِ شدید یا چند نشانه با هم؟"], "alert"),
            (["اگر اپی‌نفرین تجویز شده، طبق برنامه", "استفاده و با اورژانس تماس بگیرید."], "doctor"),
            (["بدون راهنماییِ پزشک، در خانه", "دوباره امتحان نکنید."], "stop"),
        ],
    },
]


def z(v):
    return int(round(v * S))


def rgb(col):
    h = P.get(col, col)
    if isinstance(h, tuple):
        return h
    return tuple(int(h[i:i+2], 16) for i in (1, 3, 5))


def rgba(col, alpha=255):
    if isinstance(col, tuple):
        return (*col[:3], alpha) if len(col) < 4 else col
    return (*rgb(col), alpha)


def font(size, weight="regular"):
    return ImageFont.truetype(str(FONT[weight]), z(size))


def rect(d, xy, fill, radius=20, outline=None, width=1):
    x0, y0, x1, y1 = xy
    fv = rgba(fill) if isinstance(fill, str) else fill
    ov = rgba(outline) if isinstance(outline, str) else outline
    d.rounded_rectangle((z(x0), z(y0), z(x1), z(y1)), radius=z(radius), fill=fv,
                        outline=ov, width=z(width) if outline else 1)


def ellipse(d, xy, fill=None, outline=None, width=1):
    x0, y0, x1, y1 = xy
    fv = rgba(fill) if isinstance(fill, str) else fill
    ov = rgba(outline) if isinstance(outline, str) else outline
    d.ellipse((z(x0), z(y0), z(x1), z(y1)), fill=fv, outline=ov,
              width=z(width) if outline else 1)


def line(d, pts, fill, width=3):
    fv = rgba(fill) if isinstance(fill, str) else fill
    d.line([(z(x), z(y)) for x, y in pts], fill=fv, width=z(width), joint="curve")


def poly(d, pts, fill):
    fv = rgba(fill) if isinstance(fill, str) else fill
    d.polygon([(z(x), z(y)) for x, y in pts], fill=fv)


def text(d, value, x, y, size, fill="white", weight="regular", anchor="ra"):
    d.text((z(x), z(y)), value, font=font(size, weight), fill=rgba(fill), anchor=anchor)


def centered(d, value, cx, cy, size, fill="white", weight="medium"):
    d.text((z(cx), z(cy)), value, font=font(size, weight), fill=rgba(fill), anchor="mm")


def rounded_box(d, xy, fill, radius=25, outline=None, width=1):
    rect(d, xy, fill, radius, outline, width)


def draw_spark(d, cx, cy, r, accent):
    poly(d, [(cx,cy-r),(cx+4,cy-4),(cx+r,cy),(cx+4,cy+4),
             (cx,cy+r),(cx-4,cy+4),(cx-r,cy),(cx-4,cy-4)], accent)


def mini_icon(d, cx, cy, kind, accent):
    ellipse(d, (cx-31, cy-31, cx+31, cy+31), "#13182F", outline=accent, width=2)
    if kind in ("check", "shield", "repeat"):
        line(d, [(cx-14,cy), (cx-4,cy+11), (cx+16,cy-13)], accent, 4)
        if kind == "shield":
            poly(d, [(cx,cy-21),(cx+17,cy-13),(cx+14,cy+9),(cx,cy+22),(cx-14,cy+9),(cx-17,cy-13)], "#30305A")
            line(d, [(cx-9,cy), (cx-2,cy+7), (cx+11,cy-8)], accent, 3)
        elif kind == "repeat":
            ellipse(d, (cx-18,cy-18,cx+18,cy+18), None, accent, 2)
    elif kind == "clock":
        ellipse(d, (cx-18,cy-18,cx+18,cy+18), None, accent, 3)
        line(d, [(cx,cy-11),(cx,cy),(cx+11,cy+6)], accent, 3)
    elif kind == "food":
        ellipse(d, (cx-19,cy-15,cx+19,cy+15), None, accent, 3)
        ellipse(d, (cx-8,cy-7,cx+8,cy+7), "orange")
    elif kind == "peanut":
        ellipse(d, (cx-19,cy-15,cx+2,cy+16), None, accent, 3)
        ellipse(d, (cx-2,cy-16,cx+19,cy+15), None, "gold", 3)
        line(d, [(cx-4,cy-10),(cx+4,cy+10)], accent, 2)
    elif kind == "skin":
        line(d, [(cx-19,cy+14),(cx+19,cy+14)], accent, 3)
        for dx in (-13,0,13):
            line(d, [(cx+dx,cy+12),(cx+dx,cy-14)], "white", 2)
        ellipse(d, (cx-5,cy-4,cx+7,cy+8), "pink")
    elif kind == "breath":
        line(d, [(cx,cy-19),(cx,cy-3),(cx-8,cy+2)], accent, 3)
        line(d, [(cx,cy-3),(cx+8,cy+2)], accent, 3)
        line(d, [(cx-8,cy+2),(cx-18,cy+8),(cx-16,cy+18)], "pink", 3)
        line(d, [(cx+8,cy+2),(cx+18,cy+8),(cx+16,cy+18)], "purple", 3)
    elif kind == "gut":
        line(d, [(cx-5,cy-20),(cx-5,cy-5),(cx-17,cy+2),(cx-17,cy+15),
                 (cx+4,cy+18),(cx+17,cy+8),(cx+13,cy-4),(cx+5,cy-8),(cx+5,cy-19)], accent, 3)
    elif kind in ("alert", "stop", "pause"):
        poly(d, [(cx,cy-21),(cx+21,cy+17),(cx-21,cy+17)], "#3E1B3B")
        line(d, [(cx,cy-11),(cx,cy+3)], accent, 3)
        ellipse(d, (cx-2,cy+8,cx+2,cy+12), accent)
        if kind == "stop":
            line(d, [(cx-15,cy-15),(cx+15,cy+15)], "red", 3)
    elif kind in ("doctor", "baby"):
        if kind == "doctor":
            line(d, [(cx-14,cy),(cx+14,cy)], accent, 4)
            line(d, [(cx,cy-14),(cx,cy+14)], accent, 4)
        else:
            ellipse(d, (cx-9,cy-19,cx+9,cy-1), "cream")
            line(d, [(cx,cy),(cx-8,cy+12),(cx+11,cy+15)], accent, 3)
            line(d, [(cx-8,cy+12),(cx-18,cy+19)], "pink", 3)
    else:
        draw_spark(d, cx, cy, 14, accent)


def bg_gradient(size, colors):
    w, h = size
    c1, c2 = np.array(rgb(colors[0])), np.array(rgb(colors[1]))
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    for y in range(h):
        t = y / max(1, h-1)
        arr[y] = (c1*(1-t) + c2*t).astype(np.uint8)
    return Image.fromarray(arr, "RGB")


def slide_background(spec):
    base = bg_gradient((W,H), spec["colors"]).resize((z(W),z(H)), Image.Resampling.LANCZOS).convert("RGBA")
    # soft coloured halos, like the animated reel palette, but keep the text area dark.
    haze = Image.new("RGBA", base.size, (0,0,0,0))
    hd = ImageDraw.Draw(haze)
    accent = rgba(spec["accent"], 72)
    for cx,cy,r in [(150,430,270),(950,1210,340),(865,310,210),(180,1570,260)]:
        hd.ellipse((z(cx-r),z(cy-r),z(cx+r),z(cy+r)), fill=accent)
    haze = haze.filter(ImageFilter.GaussianBlur(z(65)))
    base = Image.alpha_composite(base, haze)
    overlay = Image.new("RGBA", base.size, (0,0,0,48))
    base = Image.alpha_composite(base, overlay)
    d = FD(base)
    # Thin colored orbit arcs and small glints.
    ellipse(d, (830,-170,1185,185), None, "white", 1)
    ellipse(d, (872,-129,1148,147), None, spec["accent"], 2)
    ellipse(d, (-135,1570,70,1780), None, spec["accent"], 1)
    draw_spark(d, 1010, 395, 12, "white")
    draw_spark(d, 74, 735, 9, spec["accent"])
    return base


def bullet_text_box(d, spec, idx):
    items = spec["items"]
    line_h, gap, pad = 43, 14, 28
    rows = []
    total = pad * 2
    for label_lines, kind in items:
        if isinstance(label_lines, str):
            label_lines = [label_lines]
        h = len(label_lines) * line_h + gap
        rows.append((label_lines, kind, h))
        total += h
    top = 348
    bottom = top + total
    rounded_box(d, (68,top,1012,bottom), (8,8,25,226), 34, (255,255,255,105), 1)
    y = top + pad
    for j, (label_lines, kind, h) in enumerate(rows):
        cy = y + (h-gap)/2
        mini_icon(d, 139, cy, kind, spec["accent"])
        for k, row in enumerate(label_lines):
            text(d, row, 965, y + k*line_h, 32, "white", "medium")
        y += h
    return bottom


def draw_progress(d, idx):
    # Six reel-like progress dots under the title.
    start, spacing, cy = 405, 54, 299
    for n in range(6):
        x = start + n*spacing
        r = 12 if n == idx else 8
        fill = ["cyan","pink","lime","gold","purple","red"][n] if n == idx else (255,255,255,115)
        ellipse(d, (x-r,cy-r,x+r,cy+r), fill)


def add_header(d, spec, idx):
    # Number bubble at upper-left, heading and English slug on upper-right.
    ellipse(d, (66,74,224,232), "#FFF8EE")
    centered(d, str(idx+1).translate(str.maketrans("0123456789", DIGITS)), 145, 153, 76, spec["accent"], "extra")
    title_size = 63 if len(spec["title"]) <= 17 else (55 if len(spec["title"]) <= 22 else 49)
    text(d, spec["title"], 1003, 89, title_size, "white", "extra")
    text(d, spec["en"], 1001, 195, 25, "white", "bold")
    draw_progress(d, idx)


def art_canvas(index, colors, accent):
    art = bg_gradient((AW,AH), ("#11142D", "#191A3D")).resize((z(AW),z(AH)), Image.Resampling.LANCZOS).convert("RGBA")
    glow = Image.new("RGBA", art.size, (0,0,0,0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((z(165),z(100),z(595),z(530)), fill=rgba(accent, 85))
    gd.ellipse((z(265),z(420),z(665),z(820)), fill=rgba(colors[1], 58))
    glow = glow.filter(ImageFilter.GaussianBlur(z(85)))
    art = Image.alpha_composite(art,glow)
    d = FD(art)
    # abstract neon circles behind the illustration
    ellipse(d, (74,74,AW-74,AH-74), None, colors[0], 2)
    ellipse(d, (102,102,AW-102,AH-102), None, accent, 1)
    for x,y,r,c in [(94,122,8,accent),(665,136,7,"white"),(658,832,8,colors[1]),(100,835,6,"gold")]:
        ellipse(d,(x-r,y-r,x+r,y+r),c)
    if index == 0:
        art_baby_bowl(d, accent)
    elif index == 1:
        art_symptoms(d, accent)
    elif index == 2:
        art_intro(d, accent)
    elif index == 3:
        art_readiness(d, accent)
    elif index == 4:
        art_safe_food(d, accent)
    else:
        art_emergency(d, accent)
    return art


def art_baby_bowl(d, accent):
    # baby face and shoulders
    ellipse(d, (270,170,490,390), "hair")
    ellipse(d, (287,185,473,369), "skin")
    ellipse(d, (275,151,485,266), "hair")
    for x,y,r in [(303,205,34),(348,174,33),(397,172,32),(445,203,31)]:
        ellipse(d,(x-r,y-r,x+r,y+r),"hair")
    ellipse(d,(332,275,346,289),"purple")
    ellipse(d,(411,275,425,289),"purple")
    line(d,[(350,325),(370,339),(390,339),(409,325)],"pink",4)
    ellipse(d,(189,339,571,715),"#5C397D",outline=accent,width=4)
    # bowl + spoon
    rounded_box(d,(182,610,578,775),"#10152D",34,accent,4)
    ellipse(d,(207,592,553,677),"#242449",outline="white",width=2)
    for x,y,c,r in [(264,639,"gold",22),(326,656,"lime",17),(380,637,"pink",20),(438,657,"cyan",17),(495,636,"orange",19)]:
        ellipse(d,(x-r,y-r,x+r,y+r),c)
    line(d,[(535,563),(625,472)],"lime",9)
    ellipse(d,(606,450,655,499),None,"lime",4)
    # egg and safe puree bowl
    ellipse(d,(119,446,224,579),"cream",outline="gold",width=4)
    ellipse(d,(148,492,194,542),"orange")
    ellipse(d,(543,247,641,345),None,"purple",4)
    draw_spark(d,592,296,19,"pink")


def art_symptoms(d, accent):
    # three connected signal icons, without text
    line(d,[(205,450),(380,330),(555,450),(380,628),(205,450)],accent,4)
    # skin/hives
    ellipse(d,(102,206,330,434),"#151B37",outline="pink",width=5)
    line(d,[(153,370),(279,370)],"gold",6)
    for x in (169,210,251): line(d,[(x,365),(x,290)],"white",4)
    for x,y in [(180,282),(217,262),(249,296),(199,330)]: ellipse(d,(x-10,y-10,x+10,y+10),"pink")
    # lungs
    ellipse(d,(267,95,493,321),"#151B37",outline="cyan",width=5)
    line(d,[(380,144),(380,206),(354,224)],"cyan",5)
    line(d,[(380,204),(405,226)],"cyan",5)
    line(d,[(353,224),(319,239),(313,277),(343,286),(369,257)],"pink",5)
    line(d,[(405,226),(440,240),(447,277),(417,286),(392,257)],"purple",5)
    # stomach
    ellipse(d,(430,425,658,653),"#151B37",outline="lime",width=5)
    line(d,[(375+95,463),(470,516),(447,552),(451,583),(505,598),(554,573),(553,534),(521,509),(520,463)],"lime",6)
    for x,y in [(148,514),(603,337),(379,737)]: draw_spark(d,x,y,15,accent)


def art_intro(d, accent):
    # plate, peanut pod and a protective shield
    ellipse(d,(154,220,606,672),"#12172F",outline="white",width=5)
    ellipse(d,(204,270,556,622),"#242442",outline=accent,width=4)
    for x,y,c,r in [(294,388,"gold",30),(369,345,"pink",27),(443,397,"cyan",28),(344,469,"lime",25),(431,493,"orange",24)]:
        ellipse(d,(x-r,y-r,x+r,y+r),c)
    # peanut pod in a small neon frame
    ellipse(d,(70,93,271,294),"#11152D",outline="purple",width=4)
    ellipse(d,(107,137,166,241),None,"orange",5)
    ellipse(d,(160,131,221,236),None,"pink",5)
    line(d,[(158,147),(161,222)],"lime",3)
    # shield / check on the right
    poly(d,[(573,230),(663,269),(649,369),(613,411),(574,369),(558,269)],"#1A2440")
    line(d,[(580,319),(604,343),(643,289)],"lime",8)
    # small feed spoon
    line(d,[(230,733),(507,690)],accent,9)
    ellipse(d,(492,660,558,723),None,"white",4)
    draw_spark(d,653,589,17,"gold")


def art_readiness(d, accent):
    # clock halo and baby seated in a supportive high chair
    ellipse(d,(187,88,573,474),None,"gold",5)
    ellipse(d,(226,128,534,436),None,accent,2)
    line(d,[(380,169),(380,278),(438,320)],"white",8)
    ellipse(d,(365,153,395,183),accent)
    # chair frame and footrest
    line(d,[(237,486),(524,486),(528,634),(230,634),(237,486)],"cyan",8)
    line(d,[(257,632),(236,787)],"white",8)
    line(d,[(500,632),(526,787)],"white",8)
    line(d,[(244,716),(519,716)],"pink",8)
    # seated infant
    ellipse(d,(316,334,444,462),"skin")
    ellipse(d,(310,317,450,385),"hair")
    for x,y,r in [(326,345,22),(366,326,23),(407,342,21)]: ellipse(d,(x-r,y-r,x+r,y+r),"hair")
    ellipse(d,(342,387,352,397),"purple"); ellipse(d,(406,387,416,397),"purple")
    line(d,[(356,420),(379,429),(400,419)],"pink",3)
    line(d,[(338,462),(322,536),(378,573),(438,535),(422,462)],"#9B58D4",9)
    line(d,[(329,501),(280,540),(259,519)],"lime",8)
    line(d,[(430,500),(480,536),(501,516)],"lime",8)
    line(d,[(350,566),(324,623)],"gold",8)
    line(d,[(406,566),(438,623)],"gold",8)
    draw_spark(d,124,334,15,"pink"); draw_spark(d,635,511,14,"lime")


def art_safe_food(d, accent):
    # divided plate with egg and smooth puree; cross over a whole nut
    ellipse(d,(93,201,531,639),"#151A35",outline="white",width=5)
    ellipse(d,(128,236,496,604),"#242445",outline=accent,width=4)
    # fully-cooked egg
    ellipse(d,(183,300,333,490),"cream",outline="gold",width=4)
    ellipse(d,(225,358,291,427),"orange")
    # smooth puree bowl
    rounded_box(d,(245,485,469,591),"#11152C",27,"cyan",4)
    ellipse(d,(268,463,445,523),"#412746",outline="pink",width=3)
    for x,y in [(315,490),(355,480),(396,493)]: ellipse(d,(x-10,y-10,x+10,y+10),"gold")
    # spoon with thinned peanut puree
    line(d,[(476,403),(615,292)],"lime",9)
    ellipse(d,(594,267,650,323),None,"lime",4)
    ellipse(d,(609,281,635,307),"#C87930")
    # no whole nuts: simple outline with slash
    ellipse(d,(535,598,661,724),"#17162E",outline="purple",width=3)
    ellipse(d,(566,626,610,682),None,"orange",5)
    ellipse(d,(599,630,640,682),None,"pink",5)
    line(d,[(546,608),(649,711)],"red",9)
    draw_spark(d,141,715,14,"cyan")


def art_emergency(d, accent):
    # stylized emergency pen, phone and alert pulse; no brand text
    ellipse(d,(82,126,678,722),None,"red",4)
    ellipse(d,(112,155,648,692),None,accent,2)
    # epinephrine auto-injector style pen
    rounded_box(d,(173,290,323,662),"#E9F1FF",34,"cyan",5)
    rounded_box(d,(190,246,306,330),"#FF526E",24,"red",4)
    rect(d,(211,345,285,526),"#12172E",18)
    line(d,[(247,528),(247,630)],"gold",9)
    poly(d,[(234,626),(260,626),(247,664)],"gold")
    # pulse / alert
    poly(d,[(405,270),(496,430),(312,430)],"#30152E")
    line(d,[(404,315),(404,375)],"red",10)
    ellipse(d,(395,393,413,411),"lime")
    # phone with emergency call glyph
    rounded_box(d,(451,483,641,735),"#11162E",27,"purple",5)
    rect(d,(472,517,620,676),"#1A2547",14)
    line(d,[(502,611),(534,611),(550,575),(574,645),(590,611)],"green",8)
    ellipse(d,(530,696,563,729),"cyan")
    for r in (25,45,65):
        ellipse(d,(378-r,770-r,378+r,770+r),None,"pink",2)


def render_art(idx, spec):
    # Keep the card at 2x while placing it into the 2x slide canvas; clip to the reel-style rounded image frame.
    art = art_canvas(idx, spec["colors"], spec["accent"])
    mask = Image.new("L", art.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, art.width-1, art.height-1), radius=z(38), fill=255)
    art.putalpha(mask)
    return art


def render_slide(idx, spec):
    im = slide_background(spec)
    d = FD(im)
    add_header(d, spec, idx)
    box_bottom = bullet_text_box(d, spec, idx)
    art_top = max(810, box_bottom + 38)
    art = render_art(idx, spec)
    x0 = (W-AW)//2
    # A light rim echoes the image card used in the reel layouts; no text sits on the art.
    rect(d, (x0-11,art_top-11,x0+AW+11,art_top+AH+11), (255,255,255,215), 48)
    d.image.alpha_composite(art, (z(x0), z(art_top)))
    # slim multicolour progress line at the bottom
    ybar = 1838
    rect(d, (72,ybar,1008,ybar+10), (255,255,255,75), 5)
    seg = 936/6
    cols = ["cyan","pink","lime","gold","purple","red"]
    for n in range(idx+1):
        rect(d, (72+n*seg,ybar,72+(n+1)*seg,ybar+10), cols[n], 5)
    footer_label = "ذخیره کنید  •  برای والدین بفرستید" if idx == 5 else "تغذیهٔ کودک  •  آگاهی از آلرژی"
    text(d, footer_label, 1008, 1873, 18, "white", "medium")
    return im.convert("RGB").resize((W,H),Image.Resampling.LANCZOS)


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    slides=[]
    for idx,spec in enumerate(SLIDES):
        im=render_slide(idx,spec)
        path=OUT/f"slide_{idx+1:02d}.png"
        im.save(path,"PNG",optimize=True)
        slides.append(im)
        print(path.name, im.size, path.stat().st_size)
    slides[0].save(OUT/"carousel.pdf","PDF",save_all=True,append_images=slides[1:],resolution=150,quality=92)
    with zipfile.ZipFile(OUT/"carousel_assets.zip","w",zipfile.ZIP_DEFLATED,compresslevel=9) as zf:
        for p in sorted(OUT.glob("slide_*.png")):
            zf.write(p,p.name)
    print("PDF pages: 6 | archive contains six slide PNGs only")
    print("PDF bytes:",(OUT/"carousel.pdf").stat().st_size)
    print("ZIP bytes:",(OUT/"carousel_assets.zip").stat().st_size)

if __name__ == "__main__":
    main()

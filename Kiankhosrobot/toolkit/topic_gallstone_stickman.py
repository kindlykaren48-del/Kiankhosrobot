"""
ریلز استیکمن پزشکی: «تولید سنگ کیسهٔ صفرا»
کاراکتر با الهام از تصویر کاربر: اندام باریک، عینک گرد قرمز، پیراهن چهارخانه و کفش‌های بزرگ.
پالت مولتی‌کالر، متن فارسی و نریشن زن آموزشی.
"""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFilter

from stickman_engine import (
    W, H, INK, BOLD, BLACK, MED, OUTDIR,
    Stickman, P, pose_think, pose_shock, pose_wave,
    bg_base, text_card, footer, txt, _font, _measure_mask,
    sparkle, draw_marks, sweat, render_reel,
)

SLUG = "gallstone_stickman"
FLOOR = 1560
S = 1.62
CY = FLOOR - 158 * S
CHAR = Stickman(color=(34, 38, 48), lw=12, scale=S, hair=True)
SRC = os.path.join(OUTDIR, "gallstone_src")


def clamp01(v):
    return max(0.0, min(1.0, v))


def _pt(cx, cy, pose, p, facing=1):
    """تبدیل مختصات کاراکتر به مختصات فریم؛ همسان با موتور اصلی."""
    x, y = p
    ang = pose.get("lean", 0.0) * facing
    if ang:
        c, s = math.cos(ang), math.sin(ang)
        x, y = x * c - y * s, x * s + y * c
    cy_eff = cy - pose.get("hip_lift", 0.0) * S
    return cx + facing * x * S, cy_eff - y * S


def draw_hero(img, cx, cy, pose, facing=1, floor_y=FLOOR):
    """استیکمنِ الهام‌گرفته از تصویر: عینک قرمز، لباس چهارخانه و کفش بزرگ."""
    d = ImageDraw.Draw(img, "RGBA")

    # پیراهن چهارخانه، قبل از خطوط دست و بدن
    p1 = _pt(cx, cy, pose, (-35, 142), facing)
    p2 = _pt(cx, cy, pose, (35, 142), facing)
    p3 = _pt(cx, cy, pose, (42, 10), facing)
    p4 = _pt(cx, cy, pose, (-42, 10), facing)
    d.polygon([p1, p2, p3, p4], fill=(228, 224, 218, 255), outline=(120, 42, 48, 255))
    for f in (0.28, 0.58, 0.82):
        xa = p1[0] + (p2[0] - p1[0]) * f
        xb = p4[0] + (p3[0] - p4[0]) * f
        d.line([(xa, p1[1]), (xb, p4[1])], fill=(190, 44, 54, 210), width=7)
    for f in (0.30, 0.62):
        ya_l = p1[1] + (p4[1] - p1[1]) * f
        ya_r = p2[1] + (p3[1] - p2[1]) * f
        d.line([(p1[0], ya_l), (p2[0], ya_r)], fill=(80, 88, 104, 190), width=6)

    CHAR.draw(img, cx, cy, pose, facing=facing, floor_y=floor_y)
    d = ImageDraw.Draw(img, "RGBA")

    # کفش‌های بزرگ چهارخانه
    for side in ("l", "r"):
        fx, fy = _pt(cx, cy, pose, pose["foot_" + side], facing)
        toe = facing * (42 if side == "r" else 18)
        x0, x1 = fx - 52 + toe, fx + 72 + toe
        y0, y1 = fy - 52, fy + 28
        d.rounded_rectangle([x0, y0, x1, y1], 28, fill=(241, 240, 232, 255),
                            outline=(34, 38, 48, 255), width=7)
        d.line([(x0 + 18, y0 + 4), (x0 + 18, y1 - 3)], fill=(205, 40, 50, 230), width=12)
        d.line([(x0 + 48, y0 + 4), (x0 + 48, y1 - 3)], fill=(205, 40, 50, 220), width=8)
        d.line([(x0 + 5, y0 + 28), (x1 - 6, y0 + 28)], fill=(205, 40, 50, 210), width=8)
        d.line([(x0 + 7, y1 - 10), (x1 - 5, y1 - 10)], fill=(70, 78, 92, 180), width=7)

    # چشم‌های سبز بزرگ و عینک گرد قرمز
    hx, hy = _pt(cx, cy, pose, (0, 214), facing)
    rr = 41
    for sx in (-1, 1):
        gx = hx + sx * 43
        d.ellipse([gx - rr, hy - rr + 2, gx + rr, hy + rr + 2],
                  fill=(248, 250, 246, 255), outline=(208, 30, 54, 255), width=11)
        d.ellipse([gx - 18, hy - 18, gx + 18, hy + 18], fill=(108, 166, 98, 255),
                  outline=(30, 54, 38, 255), width=5)
        d.ellipse([gx - 7, hy - 7, gx + 7, hy + 7], fill=(16, 18, 20, 255))
        d.ellipse([gx - 3, hy - 10, gx + 3, hy - 4], fill=(255, 255, 255, 230))
    d.line([(hx - 3, hy), (hx + 3, hy)], fill=(208, 30, 54, 255), width=10)
    d.line([(hx - 85, hy - 2), (hx - 105, hy + 8)], fill=(208, 30, 54, 255), width=9)
    d.line([(hx + 85, hy - 2), (hx + 105, hy + 8)], fill=(208, 30, 54, 255), width=9)


def pose_point():
    return P(hand_l=(-38, 40), elbow_l=(-38, 96),
             hand_r=(118, 126), elbow_r=(54, 118),
             knee_l=(-28, -76), foot_l=(-38, -158),
             knee_r=(28, -76), foot_r=(38, -158),
             face="smile", eyes="wide")


def pose_crossed():
    return P(hand_l=(38, 92), elbow_l=(-45, 108),
             hand_r=(-38, 92), elbow_r=(45, 108),
             knee_l=(-28, -76), foot_l=(-38, -158),
             knee_r=(30, -70), foot_r=(76, -110),
             face="flat", eyes="wide")


def draw_liver(d, cx, cy, scale=1.0):
    c1, c2 = (164, 72, 62, 255), (192, 94, 72, 255)
    d.ellipse([cx - 205 * scale, cy - 108 * scale, cx + 160 * scale, cy + 92 * scale],
              fill=c1, outline=(82, 54, 54, 255), width=max(5, int(8 * scale)))
    d.ellipse([cx - 32 * scale, cy - 95 * scale, cx + 215 * scale, cy + 66 * scale],
              fill=c2, outline=(82, 54, 54, 255), width=max(5, int(8 * scale)))
    d.arc([cx - 170 * scale, cy - 60 * scale, cx + 130 * scale, cy + 66 * scale],
          15, 170, fill=(226, 132, 95, 190), width=max(4, int(7 * scale)))


def gall_shape(d, cx, cy, r=150, bile=(224, 190, 55, 230), outline=(44, 116, 82, 255)):
    """کیسهٔ صفرای ساده و مجرای خروجی."""
    d.polygon([(cx - r * 0.18, cy - r * 1.15), (cx + r * 0.18, cy - r * 1.15),
               (cx + r * 0.32, cy - r * 0.58), (cx - r * 0.32, cy - r * 0.58)],
              fill=bile, outline=outline)
    d.ellipse([cx - r, cy - r * 0.72, cx + r, cy + r * 1.10],
              fill=bile, outline=outline, width=max(6, int(r * 0.07)))
    d.line([(cx, cy - r * 1.15), (cx + r * 0.65, cy - r * 1.55),
            (cx + r * 1.05, cy - r * 1.55)], fill=outline, width=max(8, int(r * 0.10)))


def stone(d, x, y, r, col=(184, 126, 38, 255)):
    d.ellipse([x - r, y - r, x + r, y + r], fill=col, outline=(104, 68, 28, 255), width=max(3, int(r * .18)))
    d.ellipse([x - r * .45, y - r * .55, x - r * .05, y - r * .15], fill=(245, 207, 108, 210))


def bile_drop(d, x, y, r=14, alpha=230):
    c = (244, 194, 48, alpha)
    d.polygon([(x, y - r * 1.4), (x - r, y), (x, y + r), (x + r, y)], fill=c)
    d.ellipse([x - r, y - r * .1, x + r, y + r * 1.15], fill=c)


def symptom_badge(img, cx, cy, label, col, kind="dot"):
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle([cx - 210, cy - 58, cx + 210, cy + 58], 36,
                        fill=(255, 255, 255, 245), outline=(*col, 255), width=6)
    if kind == "pain":
        d.polygon([(cx + 156, cy - 30), (cx + 185, cy), (cx + 156, cy + 30),
                   (cx + 128, cy)], fill=(*col, 255))
    elif kind == "fever":
        d.rounded_rectangle([cx + 147, cy - 34, cx + 163, cy + 20], 7,
                            outline=(*col, 255), width=5)
        d.ellipse([cx + 140, cy + 12, cx + 170, cy + 42], fill=(*col, 255))
    else:
        d.ellipse([cx + 140, cy - 18, cx + 176, cy + 18], fill=(*col, 255))
    txt(img, (cx - 10, cy), label, _font(BOLD, 42), (46, 48, 58), anchor="mm")


def _sc1(d, img, lt, T, ctx):
    # کبد صفرا می‌سازد و کیسه آن را نگه می‌دارد
    pulse = 1.0 + 0.025 * math.sin(lt * 2.8)
    draw_liver(d, 760, 850, pulse)
    gall_shape(d, 795, 1175, 112, bile=(224, 194, 56, 235))
    for i in range(5):
        u = (lt * 0.55 + i * 0.20) % 1.0
        x = 820 + 122 * u
        y = 1000 - 55 * math.sin(u * math.pi)
        bile_drop(d, x, y, 11, int(120 + 120 * (1 - u)))
    draw_hero(img, 250, CY, pose_point(), facing=1)
    sparkle(d, 770, 1280, 15, color=(245, 194, 48))


def _sc2(d, img, lt, T, ctx):
    # غلیظ شدن صفرا: قطره‌های آب بیرون می‌روند و ذرات بیشتر می‌شوند
    gall_shape(d, 760, 1110, 190, bile=(224, 168, 42, 238))
    for i in range(16):
        a = i * 2.399
        rr = 45 + (i % 4) * 32
        x = 760 + math.cos(a + lt * .18) * rr
        y = 1130 + math.sin(a + lt * .18) * rr * .78
        stone(d, x, y, 8 + i % 3, col=(224, 165, 42, 240))
    for i in range(4):
        u = (lt * .26 + i * .28) % 1.0
        x = 615 + i * 74 + 16 * math.sin(lt + i)
        y = 930 - u * 260
        c = (72, 170, 220, int(230 * (1 - u)))
        d.ellipse([x - 13, y - 18, x + 13, y + 18], fill=c)
    draw_hero(img, 235, CY, pose_think(lt), facing=1)
    draw_marks(img, 235, 765, "؟", size=78, color=(76, 120, 205), pop=1.0)


def _sc3(d, img, lt, T, ctx):
    # بلورها مثل شن کنار هم می‌نشینند
    gall_shape(d, 750, 1110, 195, bile=(231, 187, 56, 235))
    prog = clamp01((lt - .25) / max(1.0, T * .72))
    for i in range(22):
        ph = i * 2.17
        sx = 750 + math.cos(ph + lt * .7) * (125 - 45 * prog)
        sy = 1030 + math.sin(ph + lt * .7) * 105
        tx = 680 + (i % 7) * 24
        ty = 1240 + (i % 3) * 18
        x = sx + (tx - sx) * prog
        y = sy + (ty - sy) * prog
        stone(d, x, y, 8 + (i % 4), col=(202, 139, 40, 245))
    draw_hero(img, 230, CY, pose_crossed(), facing=1)
    for i in range(3):
        sparkle(d, 650 + i * 85, 1320 - i * 26, 11 + 2 * i, color=(245, 190, 55))


def _sc4(d, img, lt, T, ctx):
    # سنگ‌های شکل‌گرفته و یک سنگ نزدیک مجرا
    gall_shape(d, 750, 1115, 190, bile=(235, 191, 58, 230))
    pop = clamp01(lt / .55)
    for i, (x, y, r) in enumerate(((680, 1240, 47), (770, 1265, 55), (840, 1210, 42))):
        stone(d, x, y, r * pop)
    stone(d, 860, 865, 31 * pop, col=(194, 126, 34, 255))
    d.arc([816, 818, 932, 925], 190, 340, fill=(220, 54, 58, 230), width=12)
    d.arc([824, 800, 950, 930], 190, 342, fill=(220, 54, 58, 150), width=8)
    draw_hero(img, 230, CY, pose_shock(lt, tr=.25), facing=1)
    draw_marks(img, 230, 755, "!", size=88, color=(220, 54, 58), pop=pop)
    sweat(d, 110, 975, s=1.0)


def _sc5(d, img, lt, T, ctx):
    # هشدارهای پیگیری پزشکی
    draw_hero(img, 225, CY, pose_wave(lt), facing=1)
    symptom_badge(img, 765, 820, "درد شدید شکم", (220, 70, 70), "pain")
    symptom_badge(img, 765, 1010, "تب", (230, 126, 44), "fever")
    symptom_badge(img, 765, 1200, "استفراغ", (120, 80, 190), "dot")
    for i in range(3):
        if math.sin(lt * 2.2 + i) > -0.2:
            sparkle(d, 555 + i * 210, 1380 - i * 45, 13,
                    color=((220, 70, 70), (230, 126, 44), (120, 80, 190))[i])


SCENES = [
    dict(bg=(241, 247, 255), accent=(46, 120, 210),
         title="صفرا کجا می‌رود؟", sub="کبد می‌سازد، کیسه نگه می‌دارد", min=4.0, draw=_sc1),
    dict(bg=(234, 250, 243), accent=(18, 154, 118),
         title="صفرا غلیظ می‌شود", sub="کلسترول زیاد یا تخلیهٔ ناقص", min=4.0, draw=_sc2),
    dict(bg=(255, 238, 246), accent=(216, 66, 132),
         title="دانه‌ها رسوب می‌کنند", sub="شروع بلورهای بسیار ریز", min=4.0, draw=_sc3),
    dict(bg=(244, 238, 255), accent=(126, 78, 210),
         title="دانه‌ها بزرگ می‌شوند", sub="سنگ کیسهٔ صفرا شکل می‌گیرد", min=4.0, draw=_sc4),
    dict(bg=(255, 247, 226), accent=(230, 132, 40),
         title="چه زمانی پیگیری کنیم؟", sub="درد شدید، تب یا استفراغ", min=4.0, draw=_sc5),
]

CFG = dict(slug=SLUG, scenes=SCENES, char=CHAR,
           footer="آموزش سلامت با زبان ساده")


def multicolor_bg():
    stops = [(61, 116, 210), (32, 170, 150), (220, 68, 132), (126, 78, 210), (238, 156, 42)]
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    d = ImageDraw.Draw(img, "RGBA")
    for y in range(H):
        p = y / (H - 1) * (len(stops) - 1)
        i = min(len(stops) - 2, int(p))
        f = p - i
        c = tuple(int(stops[i][k] + (stops[i + 1][k] - stops[i][k]) * f) for k in range(3))
        d.line([(0, y), (W, y)], fill=(*c, 255))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov, "RGBA")
    for cx, cy, r, col in ((120, 360, 300, (255,255,255,38)), (960, 750, 340, (255,230,100,42)),
                           (140, 1510, 300, (70,240,220,36)), (940, 1680, 360, (255,255,255,30))):
        od.ellipse([cx-r, cy-r, cx+r, cy+r], fill=col)
    ov = ov.filter(ImageFilter.GaussianBlur(70))
    return Image.alpha_composite(img, ov)


def build_cover(out=os.path.join(OUTDIR, f"{SLUG}_cover.png")):
    cov = multicolor_bg()
    d = ImageDraw.Draw(cov, "RGBA")
    d.rounded_rectangle([55, 85, W-55, 470], 52, fill=(20, 22, 35, 190),
                        outline=(255, 255, 255, 110), width=4)
    txt(cov, (W/2, 190), "سنگ کیسهٔ صفرا", _font(BLACK, 86),
        (255, 255, 255), anchor="mm")
    txt(cov, (W/2, 292), "چگونه ساخته می‌شود؟", _font(BLACK, 70),
        (255, 240, 150), anchor="mm")
    d.rounded_rectangle([190, 355, W-190, 438], 40, fill=(255, 255, 255, 235))
    txt(cov, (W/2, 396), "استیکمن پزشکی • مولتی‌کالر", _font(BOLD, 40),
        (126, 56, 154), anchor="mm")

    # کارت تصویری از صحنهٔ تشکیل سنگ
    full = bg_base((244, 238, 255), (126, 78, 210))
    fd = ImageDraw.Draw(full, "RGBA")
    _sc4(fd, full, 2.0, 5.0, {})
    crop = full.crop((0, 480, W, 1580)).resize((850, 1030), Image.Resampling.LANCZOS)
    mask = Image.new("L", crop.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, crop.width, crop.height], 46, fill=255)
    x0, y0 = 115, 535
    d.rounded_rectangle([x0-12, y0-12, x0+crop.width+12, y0+crop.height+12], 58,
                        fill=(255, 255, 255, 100))
    cov.paste(crop.convert("RGB"), (x0, y0), mask)
    d = ImageDraw.Draw(cov, "RGBA")
    d.rounded_rectangle([180, 1665, W-180, 1765], 48, fill=(24, 28, 42, 220))
    txt(cov, (W/2, 1715), "از رسوب ریز تا سنگ", _font(BOLD, 48),
        (255, 235, 128), anchor="mm")
    txt(cov, (W/2, 1845), "ذخیره کن و برای خانواده بفرست", _font(MED, 36),
        (255, 255, 255, 230), anchor="mm")
    cov.convert("RGB").save(out)
    print("[✓] cover:", out)
    return out


CAPTION = """🟡 سنگ کیسهٔ صفرا چطور ساخته می‌شود؟

کبد مایعی به نام «صفرا» می‌سازد و کیسهٔ صفرا آن را ذخیره و غلیظ می‌کند. وقتی غذا، به‌ویژه غذای چرب، وارد روده می‌شود، کیسه منقبض می‌شود و صفرا را برای کمک به هضم آزاد می‌کند.

اما اگر:
• مقدار کلسترول یا رنگ‌دانه‌های صفرا زیاد باشد،
• مواد لازم برای حل نگه داشتن آن‌ها کافی نباشد،
• یا کیسهٔ صفرا کامل و منظم خالی نشود،

ذره‌های بسیار ریز رسوب می‌کنند. این بلورها به هم می‌چسبند، بزرگ‌تر می‌شوند و در نهایت «سنگ کیسهٔ صفرا» را می‌سازند.

بسیاری از سنگ‌ها هیچ علامتی ندارند. اما درد شدید و مداوم سمت راست بالای شکم، تب، زردی یا استفراغ نیاز به بررسی پزشکی دارد. برای درمان خودسرانه یا مصرف داروهای موسوم به سنگ‌شکن اقدام نکنید.

📌 ذخیره کن و برای خانواده بفرست.

#سنگ_کیسه_صفرا #کیسه_صفرا #صفرا #کلسترول #درد_شکم #سلامت #پزشکی #آموزش_سلامت #استیکمن #ریلز_پزشکی"""


def build_caption(out=os.path.join(OUTDIR, f"{SLUG}_caption.txt")):
    with open(out, "w", encoding="utf-8") as f:
        f.write(CAPTION)
    print("[✓] caption:", out)
    return out


def audio_paths():
    return [os.path.join(SRC, "audio", f"s{i}.mp3") for i in range(5)]


if __name__ == "__main__":
    aud = audio_paths()
    missing = [p for p in aud if not os.path.isfile(p)]
    if missing:
        print("فایل نریشن پیدا نشد:", missing)
        sys.exit(1)
    out = render_reel(CFG, audio_files=aud)
    build_cover()
    build_caption()
    print("DONE:", out)

"""
topic_wifi.py — ریل استیکمن طنز: «وقتی وای‌فای قطع می‌شه...»
اجرا:
  python3 topic_wifi.py           → رندر بی‌صدا (تست) + کاور + کپشن
  python3 topic_wifi.py final     → رندر نهایی با نریشن‌های mp3 کنار فایل
                                    (audio/s0.mp3 … s3.mp4)
خروجی: wifi_reel.mp4 + wifi_cover.png + wifi_caption.txt
"""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFilter

from stickman_engine import (
    W, H, FPS, INK, BOLD, BLACK, MED, OUTDIR, FF, Stickman, P, lerp_pose,
    pose_stand, pose_shock, pose_sad, pose_plead, pose_sit_phone, pose_press,
    pose_think, pose_celebrate, pose_wave, pose_walk,
    wifi_symbol, router, router_label, table, couch, big_button, bubble,
    draw_marks, sweat, heart, sparkle, draw_confetti, confetti_rng,
    bg_base, text_card, progress, footer, txt, _measure_mask, _font, render_reel,
    mp3_dur,
)

SLUG = "wifi"
FLOOR = 1560
# ایستاده: پا روی کف → cy = FLOOR - 158*s
S = 2.0
CY_STAND = FLOOR - 158 * S          # 1244
# نشسته روی مبل: لگن روی نشیمن (1448) → hip_lift=-102
CY_SIT = 1448 - 102 * S             # 1448-204=1244؟ خیر: cy_eff=cy+204 → cy=1244

CHAR = Stickman(color=INK, lw=13, scale=S)

NARR = [
    "همه‌چی خوب بود تا یهو وای‌فای قطع شد!",
    "اول انکار بود؛ بعد جلوی مودم زانو زدم: بابا قربونت برم، کار کن!",
    "و آخرین امید: دکمهٔ ری‌استارت! یک، دو، سه!",
    "اینترنت برگشت! دوباره انسان شدیم!",
    None,
]


def draw_phone(img, cx, cy, w=64, h=118, ang=8):
    tmp = Image.new("RGBA", (w + 12, h + 12), (0, 0, 0, 0))
    td = ImageDraw.Draw(tmp)
    td.rounded_rectangle([6, 6, 6 + w, 6 + h], 16, fill=(40, 44, 54, 255),
                         outline=INK, width=4)
    td.rounded_rectangle([6 + 8, 6 + 12, 6 + w - 8, 6 + h - 16], 8,
                         fill=(160, 210, 190, 255))
    td.ellipse([6 + w / 2 - 5, 6 + h - 12, 6 + w / 2 + 5, 6 + h - 2], fill=(230, 230, 235))
    tmp = tmp.rotate(ang, expand=True, resample=Image.BICUBIC)
    img.alpha_composite(tmp, (int(cx - tmp.width / 2), int(cy - tmp.height / 2)))


def clamp01(x):
    return max(0.0, min(1.0, x))


def _sc1(d, img, lt, T, ctx):
    """مبل راحت + گوشی → قطع وای‌فای → شوک"""
    couch(d, 110, 1448, 440)
    table(d, 745, 1420, 280)
    cut = T * 0.38
    wifi_ok = lt < cut
    router(d, 800, 1420, 230, led=("green" if wifi_ok else "red"),
           blink=not wifi_ok, t=lt)
    router_label(img, 800, 1420, 230)
    # نماد وای‌فای بالای مودم
    if wifi_ok:
        wifi_symbol(d, 915, 1120, 130, color=(70, 180, 100), bars=3)
    else:
        pop = clamp01((lt - cut) / 0.25)
        wifi_symbol(d, 915, 1120, 130 * (1 + 0.15 * pop),
                    color=(170, 172, 178), bars=1, crossed=True,
                    alpha=int(255 * pop))
    if lt < cut:
        # نشسته روی مبل با گوشی
        pose = pose_sit_phone(lt)
        CHAR.draw(img, 330, CY_SIT - 102 * 0, pose, facing=1)   # cy_eff=1448
        draw_phone(img, 330 + 73 * S, 1448 - 96 * S, ang=10)
    else:
        k = clamp01((lt - cut) / 0.30)
        pose = lerp_pose(pose_sit_phone(lt), pose_shock(lt), k)
        cx = 330 + (660 - 330) * k
        cy = CY_SIT + (CY_STAND - CY_SIT) * k
        CHAR.draw(img, cx, cy, pose, facing=1, floor_y=FLOOR)
        if k >= 1.0:
            pop = clamp01((lt - cut - 0.30) / 0.20)
            draw_marks(img, 660, CY_STAND - 214 * S - 175, "!", size=88, pop=pop)
            sweat(d, 660 - 150, CY_STAND - 120 * S, s=1.1)
            sweat(d, 660 + 140, CY_STAND - 150 * S, s=0.9)


def _sc2(d, img, lt, T, ctx):
    """انکار → التماس به مودم"""
    table(d, 745, 1420, 280)
    router(d, 800, 1420, 230, led="red", blink=True, t=lt)
    router_label(img, 800, 1420, 230)
    wifi_symbol(d, 915, 1120, 120, color=(170, 172, 178), bars=1, crossed=True)
    t1, t2 = T * 0.16, T * 0.40
    if lt < t1:
        pose = pose_sad(lt)
        cx, cy = 430, CY_STAND
        CHAR.draw(img, cx, cy, pose, facing=1, floor_y=FLOOR)
        draw_marks(img, 430, CY_STAND - 214 * S - 175, "؟", size=92,
                   color=(80, 110, 200), pop=1.0)
    elif lt < t2:
        k = clamp01((lt - t1) / (t2 - t1))
        pose = lerp_pose(pose_sad(lt), pose_plead(lt), k)
        cx = 430 + (560 - 430) * k
        cy = CY_STAND
        CHAR.draw(img, cx, cy, pose, facing=1, floor_y=FLOOR)
    else:
        pose = pose_plead(lt)
        CHAR.draw(img, 560, CY_STAND, pose, facing=1, floor_y=FLOOR)
        pk = clamp01((lt - t2 - 0.15) / 0.22)
        if pk > 0:
            bubble(img, 560, CY_STAND - 214 * S - 195, "کار کن لطفاً!")
            sweat(d, 470, CY_STAND - 160 * S, s=1.0)


def _sc3(d, img, lt, T, ctx):
    """راه رفتن → فشردن دکمهٔ ری‌استارت → شمارش معکوس"""
    table(d, 745, 1420, 280)
    router(d, 800, 1420, 230, led="red", blink=True, t=lt)
    router_label(img, 800, 1420, 230)
    t_walk, t_press = T * 0.30, T * 0.44
    pressed = lt >= t_press
    # ستون + دکمهٔ ری‌استارت (دقیقاً زیر دستِ درازشدهٔ کاراکتر)
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle([730, 1090, 800, 1420], 14, fill=(210, 205, 220),
                        outline=INK, width=5)
    big_button(d, 765, 1040, r=64, pressed=pressed)
    txt(img, (765, 925), "ری‌استارت", _font(BOLD, 40), (90, 60, 150), anchor="mm")
    if pressed:
        # فلاش لحظهٔ فشار
        dt = lt - t_press
        if dt < 0.10:
            d.rectangle([0, 0, W, H], fill=(255, 255, 255, 110))
        router(d, 800, 1420, 230, led="amber", blink=True, t=lt)
    if lt < t_walk:
        pose = pose_walk(lt / max(0.4, t_walk) * 1.4, amp=1.0)
        cx = 150 + (500 - 150) * clamp01(lt / t_walk)
        CHAR.draw(img, cx, CY_STAND, pose, facing=1, floor_y=FLOOR)
    elif lt < t_press:
        k = clamp01((lt - t_walk) / (t_press - t_walk))
        pose = lerp_pose(pose_stand(), pose_press(lt, reach=1.0), k)
        CHAR.draw(img, 500, CY_STAND, pose, facing=1, floor_y=FLOOR)
    else:
        # بعد از فشار: انتظار با اضطراب
        pose = pose_think(lt)
        CHAR.draw(img, 500, CY_STAND, pose, facing=1, floor_y=FLOOR)
        sweat(d, 420, CY_STAND - 150 * S, s=1.0)
        # شمارش ۱ ۲ ۳
        for i, (st, num) in enumerate(((0.52, "۱"), (0.64, "۲"), (0.76, "۳"))):
            t0 = T * st
            if t0 <= lt < t0 + 0.38:
                pk = clamp01((lt - t0) / 0.16)
                alpha = int(255 * (1 - clamp01((lt - t0 - 0.26) / 0.12)))
                f = _font(BLACK, int(150 + 90 * (1 - pk)))
                txt(img, (270, 730), num, f, (90, 60, 150, max(0, alpha)), anchor="mm")


def _sc4(d, img, lt, T, ctx):
    """اینترنت برگشت: جشن + کانفتی"""
    table(d, 745, 1420, 280)
    router(d, 800, 1420, 230, led="green", blink=False)
    router_label(img, 800, 1420, 230)
    pop = clamp01(lt / 0.22)
    pulse = 1 + 0.06 * math.sin(2 * math.pi * 1.6 * lt)
    wifi_symbol(d, 915, 1120, 130 * pulse, color=(70, 180, 100), bars=3)
    if pop >= 0.3:
        sparkle(d, 915 - 150, 1120 - 60, r=16 * pop)
        sparkle(d, 915 + 150, 1120 - 40, r=13 * pop)
        sparkle(d, 915, 1120 - 150, r=12 * pop)
    pose = pose_celebrate(lt)
    CHAR.draw(img, 520, CY_STAND, pose, facing=1, floor_y=FLOOR)
    draw_confetti(d, ctx["confetti"], lt, area_bottom=1720)
    # قلب‌های بالارونده
    for i in range(3):
        y = 1460 - ((lt * 130 + i * 230) % 620)
        heart(d, 210 + i * 330 + 24 * math.sin(lt * 2 + i), y, s=1.15)


def _sc5(d, img, lt, T, ctx):
    """کارت پایانی: دنبال کن"""
    pose = pose_wave(lt)
    CHAR.draw(img, 540, CY_STAND, pose, facing=1, floor_y=FLOOR)
    draw_confetti(d, ctx["confetti"], lt + 3, area_bottom=1500)
    heart(d, 540 + 190 * math.sin(lt * 2.0), 700 - 60 * lt, s=1.3)


SCENES = [
    dict(bg=(252, 246, 235), accent=(222, 92, 60), title="وای‌فای قطع شد...",
         sub="لحظهٔ ترسناک هر خانه", dur=5.2, draw=_sc1),
    dict(bg=(235, 243, 250), accent=(58, 110, 200), title="مرحلهٔ انکار و التماس",
         sub="بابا قربونت برم، کار کن!", dur=6.4, draw=_sc2),
    dict(bg=(243, 238, 250), accent=(124, 88, 200), title="آخرین امید: ری‌استارت",
         sub="یک... دو... سه...", dur=6.0, draw=_sc3),
    dict(bg=(236, 248, 238), accent=(46, 160, 90), title="اینترنت برگشت!",
         sub="دوباره انسان شدیم", dur=4.8, draw=_sc4),
    dict(bg=(250, 238, 244), accent=(200, 70, 130), title="دنبال کن برای رولز بیشتر",
         sub="استیکمن‌لند", dur=2.8, draw=_sc5),
]

CFG = dict(slug=SLUG, scenes=SCENES, char=CHAR,
           footer="رولز استیکمن | طنز روزمره")


# ================================================================ کاور
def build_cover(out=os.path.join(OUTDIR, f"{SLUG}_cover.png")):
    cov = bg_base((252, 246, 235), (222, 92, 60))
    d = ImageDraw.Draw(cov, "RGBA")
    title = "وقتی وای‌فای قطع می‌شه..."
    f = _font(BLACK, 96 if len(title) <= 18 else 82)
    txt(cov, (W / 2, 250), title, f, (60, 30, 20), anchor="mm")
    fs = _font(BOLD, 44)
    m, _ = _measure_mask("رولز استیکمن • کمدی روزمره", fs)
    d.rounded_rectangle([W / 2 - (m.width + 90) / 2, 350, W / 2 + (m.width + 90) / 2, 424],
                        34, fill=(222, 92, 60))
    txt(cov, (W / 2, 387), "رولز استیکمن • کمدی روزمره", fs, (255, 255, 255), anchor="mm")

    # کارت تصویر: صحنهٔ شوک (با مقیاس یکنواخت 0.63 از صحنهٔ اصلی)
    cw, chh, cy0 = 880, 1030, 520
    cx0 = (W - cw) // 2
    card = Image.new("RGBA", (cw, chh), (0, 0, 0, 0))
    cd = ImageDraw.Draw(card, "RGBA")
    cd.rounded_rectangle([0, 0, cw, chh], 44, fill=(246, 240, 228, 255))
    sc = 0.63

    def X(x):
        return 100 + x * sc

    def Y(y):
        return 25 + y * sc
    # مبل و میز و مودم
    couch(cd, X(150), Y(1448), int(440 * sc))
    table(cd, X(755), Y(1420), int(280 * sc))
    router(cd, X(795), Y(1420), int(230 * sc), led="red")
    wifi_symbol(cd, X(915), Y(1120), int(120 * sc), color=(170, 172, 178),
                bars=1, crossed=True)
    ch = Stickman(color=INK, lw=10, scale=1.2)
    ch.draw(card, X(560), Y(1560) - 158 * 1.2, pose_shock(0.2), facing=1)
    draw_marks(card, X(560), 420, "!", size=84, color=(222, 60, 50))
    sweat(cd, X(415), 560, s=1.1)
    sweat(cd, X(705), 525, s=0.9)
    sparkle(cd, X(915), 640, r=16)
    # قاب کارت روی کاور
    d.rounded_rectangle([cx0 - 10, cy0 - 10, cx0 + cw + 10, cy0 + chh + 10], 54,
                        fill=(255, 255, 255, 90))
    mask = Image.new("L", (cw, chh), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, cw, chh], 44, fill=255)
    cov.paste(card.convert("RGB"), (cx0, cy0), mask)
    d = ImageDraw.Draw(cov, "RGBA")
    # CTA پایین
    fct = _font(BOLD, 46)
    m, _ = _measure_mask("ذخیره کن و برای دوستات بفرست", fct)
    d.rounded_rectangle([W / 2 - (m.width + 110) / 2, 1700, W / 2 + (m.width + 110) / 2, 1790],
                        40, fill=(222, 92, 60))
    txt(cov, (W / 2, 1745), "ذخیره کن و برای دوستات بفرست", fct, (255, 255, 255), anchor="mm")
    txt(cov, (W / 2, 1860), "هر هفته یک رول استیکمن", _font(MED, 34), (140, 100, 80),
        anchor="mm")
    cov.convert("RGB").save(out)
    print("[✓] cover:", out)
    return out


CAPTION = """وقتی وای‌فای قطع می‌شه... 😱📡

هر کی این لحظه رو تجربه نکرده، هنوز انسان نیست! 😂
از انکار تا التماس به مودم و در نهایت دکمهٔ جادویی ری‌استارت...

تو چی‌کار می‌کنی وقتی اینترنت می‌ره؟ کامنت کن 👇😂

ذخیره کن و برای دوستِ بی‌وای‌فایت بفرست 📲

#استیکمن #طنز #رولز #کمدی #وای_فای #اینترنت #فان #خنده #ریلز #استیکمن_لند"""


def build_caption(out=os.path.join(OUTDIR, f"{SLUG}_caption.txt")):
    open(out, "w", encoding="utf-8").write(CAPTION)
    print("[✓] caption:", out)
    return out


def audio_paths():
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio")
    return [os.path.join(base, f"s{i}.mp3") if NARR[i] else None for i in range(5)]


if __name__ == "__main__":
    final = len(sys.argv) > 1 and sys.argv[1] == "final"
    auds = audio_paths() if final else None
    if final:
        missing = [a for a in auds if a and not os.path.isfile(a)]
        if missing:
            print("!! نریشن‌ها پیدا نشد:", missing)
            sys.exit(1)
    out = render_reel(CFG, audio_files=auds)
    build_cover()
    build_caption()
    print("DONE:", out)

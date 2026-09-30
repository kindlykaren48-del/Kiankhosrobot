"""
stickman_engine.py — موتور انیمیشن استیکمن برای ریلز فارسی
=================================================================
کاراکتر استیکمن دو-مفصلی + پراپ‌ها (مودم، وای‌فای، مبل، دکمه، حباب گفتار)
+ رندر صحنه‌محور با کارت متن فارسی (fatext/HarfBuzz) و نوار پیشرفت.
متن‌ها فقط با فونت وزیرمتن. بدون موسیقی؛ فقط نریشن.

خروجی: <slug>_reel.mp4 (۱۰۸۰×۱۹۲۰، ۳۰fps، ≤۴MB) + <slug>_cover.png + کپشن.
"""
import math
import os
import random
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import imageio_ffmpeg
from fatext import FD as _FD, draw_text

FF = imageio_ffmpeg.get_ffmpeg_exe()

# ---------------------------------------------------------------- تنظیمات عمومی
W, H, FPS = 1080, 1920, 30
INK = (38, 40, 48)          # رنگ خط کاراکتر
OUTDIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # Kiankhosrobot/
FONT_DIR_CANDS = [
    os.environ.get("REEL_FONTS", ""),
    os.path.join(OUTDIR, "fonttmp", "fonts", "ttf"),
    "/home/user/Kiankhosrobot/fonttmp/fonts/ttf/",
    "/home/user/fonttmp/fonts/ttf/",
]
FTDIR = next((c for c in FONT_DIR_CANDS
              if c and os.path.isfile(os.path.join(c, "Vazirmatn-Bold.ttf"))),
             FONT_DIR_CANDS[1])
BLACK = os.path.join(FTDIR, "Vazirmatn-Black.ttf")
BOLD = os.path.join(FTDIR, "Vazirmatn-Bold.ttf")
MED = os.path.join(FTDIR, "Vazirmatn-Medium.ttf")


def _font(path, size):
    return ImageFont.truetype(path, size)


def txt(img, xy, text, font, fill, anchor="mm"):
    """متن فارسی درست (HarfBuzz) روی تصویر RGB/RGBA."""
    return draw_text(img, xy, text, font=font, fill=fill, anchor=anchor)


def txt_bbox(img, xy, text, font, anchor="mm"):
    d = _FD(img)
    return d.textbbox(xy, text, font=font, anchor=anchor)


def mp3_dur(path):
    o = subprocess.run([FF, "-i", path], capture_output=True).stderr.decode()
    import re
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.?\d*)", o)
    if not m:
        return 0.0
    h, mnt, s = m.groups()
    return int(h) * 3600 + int(mnt) * 60 + float(s)


# ================================================================ کاراکتر
# فضای کاراکتر: لگن در مبدأ، +y به بالا، +x به راستِ (facing=+1).
# مقادیر پیش‌فرض بر حسب پیکسل در scale=1 هستند.
HEAD_R, NECK_GAP, BODY = 50, 14, 150
SHOULDER_Y = 128
UPPER_ARM, FOREARM = 68, 66
THIGH, SHIN = 78, 78


def _rot(p, ang):
    c, s = math.cos(ang), math.sin(ang)
    return (p[0] * c - p[1] * s, p[0] * s + p[1] * c)


def P(hand_l=(-42, 38), elbow_l=(-38, 96), hand_r=(42, 38), elbow_r=(38, 96),
      knee_l=(-32, -78), foot_l=(-40, -158), knee_r=(32, -78), foot_r=(40, -158),
      head_tilt=0.0, hip_lift=0.0, lean=0.0, face="smile", eyes="dot"):
    """ساخت پوز با مقدارهای پیش‌فرضِ ایستاده."""
    return dict(hand_l=hand_l, elbow_l=elbow_l, hand_r=hand_r, elbow_r=elbow_r,
                knee_l=knee_l, foot_l=foot_l, knee_r=knee_r, foot_r=foot_r,
                head_tilt=head_tilt, hip_lift=hip_lift, lean=lean,
                face=face, eyes=eyes)


def lerp_pose(a, b, t):
    t = max(0.0, min(1.0, t))
    e = t * t * (3 - 2 * t)  # smoothstep
    out = {}
    for k in ("hand_l", "elbow_l", "hand_r", "elbow_r", "knee_l", "foot_l",
              "knee_r", "foot_r"):
        out[k] = (a[k][0] + (b[k][0] - a[k][0]) * e,
                  a[k][1] + (b[k][1] - a[k][1]) * e)
    for k in ("head_tilt", "hip_lift", "lean"):
        out[k] = a[k] + (b[k] - a[k]) * e
    out["face"] = b["face"] if t >= 0.5 else a["face"]
    out["eyes"] = b["eyes"] if t >= 0.5 else a["eyes"]
    return out


# ---------------- پوزهای ایستا ----------------
def pose_stand(**kw):
    return P(**kw)


def pose_shock(t=0.0, tr=1.0):
    tr_x = tr * 7 * math.sin(2 * math.pi * 5.3 * t)
    return P(hand_l=(-66 + tr_x, 176), elbow_l=(-52, 120),
             hand_r=(66 + tr_x, 176), elbow_r=(52, 120),
             knee_l=(-30, -72), foot_l=(-44, -150),
             knee_r=(30, -72), foot_r=(44, -150),
             head_tilt=-0.10, face="o", eyes="wide")


def pose_sad(t=0.0):
    return P(hand_l=(-26, 26), elbow_l=(-30, 84), hand_r=(26, 26), elbow_r=(30, 84),
             knee_l=(-26, -74), foot_l=(-34, -152), knee_r=(26, -74), foot_r=(34, -152),
             head_tilt=0.22, face="frown", eyes="sad")


def pose_plead(t=0.0):
    """زانو زده، دست‌ها به جلو رو به مودم."""
    w = 6 * math.sin(2 * math.pi * 2.2 * t)
    return P(hand_l=(52 + w, 118), elbow_l=(38, 62),
             hand_r=(78 + w, 104), elbow_r=(58, 52),
             knee_l=(-44, -80), foot_l=(-62, -70),
             knee_r=(26, -80), foot_r=(8, -66),
             hip_lift=-76, head_tilt=-0.16, face="frown", eyes="sad")


def pose_sit_phone(t=0.0):
    return P(hand_l=(62, 104), elbow_l=(24, 72), hand_r=(84, 96), elbow_r=(46, 64),
             knee_l=(56, -52), foot_l=(126, -58), knee_r=(62, -46), foot_r=(134, -52),
             hip_lift=-102, head_tilt=-0.20, face="smile", eyes="happy")


def pose_press(t=0.0, reach=1.0):
    """دست دراز به جلو برای فشردن دکمه."""
    r = max(0.0, min(1.0, reach))
    hand_r = (66 + 66 * r, 96 + 10 * r)
    elbow_r = (40 + 26 * r, 104)
    return P(hand_l=(-18, 112), elbow_l=(-36, 76),
             hand_r=hand_r, elbow_r=elbow_r,
             knee_l=(-34, -78), foot_l=(-52, -158),
             knee_r=(34, -78), foot_r=(52, -158),
             lean=0.10 * r, face="flat", eyes="wide")


def pose_think(t=0.0):
    return P(hand_l=(-34, 34), elbow_l=(-36, 88),
             hand_r=(30, 158), elbow_r=(52, 98),
             knee_l=(-30, -78), foot_l=(-40, -158),
             knee_r=(30, -78), foot_r=(40, -158),
             head_tilt=-0.12, face="flat", eyes="up")


def pose_celebrate(t=0.0):
    w = math.sin(2 * math.pi * 1.1 * t)
    return P(hand_l=(-78, 196 + 14 * w), elbow_l=(-56, 132),
             hand_r=(78, 196 - 14 * w), elbow_r=(56, 132),
             knee_l=(-36, -72), foot_l=(-46, -120 - 14 * abs(w)),
             knee_r=(36, -72), foot_r=(46, -122 + 14 * abs(w)),
             hip_lift=44 + 22 * abs(w), head_tilt=-0.06,
             face="big_smile", eyes="happy")


def pose_wave(t=0.0):
    w = 16 * math.sin(2 * math.pi * 2.6 * t)
    return P(hand_l=(-40, 38), elbow_l=(-36, 94),
             hand_r=(74 + w, 196), elbow_r=(52, 126),
             knee_l=(-30, -78), foot_l=(-40, -158),
             knee_r=(30, -78), foot_r=(40, -158),
             face="big_smile", eyes="happy")


def pose_walk(t=0.0, amp=1.0):
    s1, s2 = math.sin(2 * math.pi * t), -math.sin(2 * math.pi * t)
    fl, fr = amp * 58 * s1, amp * 58 * s2
    lift_l = amp * 32 * max(0.0, s1)
    lift_r = amp * 32 * max(0.0, s2)
    return P(hand_l=(46 * s2, 42), elbow_l=(24 * s2 - 8, 96),
             hand_r=(46 * s1, 42), elbow_r=(24 * s1 + 8, 96),
             knee_l=(0.5 * fl + 18, -80 + 0.4 * lift_l), foot_l=(fl, -158 + lift_l),
             knee_r=(0.5 * fr + 18, -80 + 0.4 * lift_r), foot_r=(fr, -158 + lift_r),
             hip_lift=amp * 8 * abs(math.sin(2 * math.pi * 2 * t)),
             lean=0.05 * amp, face="smile", eyes="dot")


# ---------------- چهره ----------------
def _face(d, hc, r, tilt, face, eyes, s, ink):
    """hc مرکز سر (روی صفحه)، r شعاع (پیکسل)."""
    ex_off, ey_off = 0.38 * r, 0.10 * r
    for sx in (-1, 1):
        # چرخش موقعیت چشم حول مرکز سر
        px, py = sx * ex_off, ey_off
        rx, ry = px * math.cos(tilt) - py * math.sin(tilt), px * math.sin(tilt) + py * math.cos(tilt)
        ex, ey = hc[0] + rx, hc[1] - ry
        er = max(3, int(5.5 * s))
        if eyes == "wide":
            er = max(4, int(8 * s))
            d.ellipse([ex - er, ey - er, ex + er, ey + er], fill=ink)
        elif eyes == "happy":   # ^ ^
            w2 = max(6, int(11 * s))
            d.arc([ex - w2, ey - w2 // 2, ex + w2, ey + w2 // 2 + 4], 200, 340, fill=ink, width=max(3, int(4 * s)))
        elif eyes == "sad":     # eyebrows-ish dots + droop handled by mouth
            d.ellipse([ex - er, ey - er, ex + er, ey + er], fill=ink)
        elif eyes == "closed":
            d.line([ex - er * 1.6, ey, ex + er * 1.6, ey], fill=ink, width=max(3, int(4 * s)))
        elif eyes == "up":
            d.ellipse([ex - er, ey - er - 2, ex + er, ey + er - 2], fill=ink)
        else:
            d.ellipse([ex - er, ey - er, ex + er, ey + er], fill=ink)
    # دهان
    mw2 = 0.52 * r
    my_off = 0.34 * r
    mx, my = hc[0], hc[1] + my_off
    lw2 = max(3, int(4.5 * s))
    if face in ("smile", "big_smile"):
        span = 26 if face == "smile" else 6
        d.arc([mx - mw2, my - mw2 * 0.9, mx + mw2, my + mw2 * 0.55], 20 + span // 2, 160 - span // 2,
              fill=ink, width=lw2)
        if face == "big_smile":
            d.arc([mx - mw2 * 0.92, my - mw2 * 0.5, mx + mw2 * 0.92, my + mw2 * 0.7], 15, 165, fill=ink, width=lw2)
    elif face == "frown":
        d.arc([mx - mw2, my - mw2 * 0.55, mx + mw2, my + mw2 * 0.9], 200, 340, fill=ink, width=lw2)
    elif face == "o":
        orr = max(5, int(10 * s))
        d.ellipse([mx - orr, my - orr, mx + orr, my + orr * 1.15], outline=ink, width=lw2)
    else:  # flat
        d.line([mx - mw2 * 0.7, my, mx + mw2 * 0.7, my], fill=ink, width=lw2)


class Stickman:
    """کاراکتر استیکمن؛ draw روی تصویر RGBA می‌کشد."""

    def __init__(self, color=INK, lw=13, scale=2.0, cap=None, glasses=False, hair=False):
        self.color = color
        self.lw = lw
        self.s = scale
        self.cap = cap          # رنگ کلاه یا None
        self.glasses = glasses
        self.hair = hair

    def draw(self, img, cx, cy, pose, facing=1, shadow=True, floor_y=None):
        s, lw = self.s, int(self.lw)
        ink = self.color
        d = ImageDraw.Draw(img, "RGBA")
        lift = pose.get("hip_lift", 0.0) * s
        cy_eff = cy - lift
        ang = pose.get("lean", 0.0) * facing  # خم به جلو

        def T(p):
            x, y = p
            if ang:
                x, y = _rot((x, y), ang)
            return (cx + facing * x * s, cy_eff - y * s)

        # سایه کف (زیر پایین‌ترین پا؛ هنگام پرش روی خط کف می‌ماند)
        if shadow:
            fl = T(pose["foot_l"])
            fr = T(pose["foot_r"])
            sy = max(fl[1], fr[1]) + 12
            sw = 120 * s * (0.7 if pose.get("hip_lift", 0) < -40 else 1.0)
            if floor_y is not None:
                air = floor_y - sy
                if air > 0:
                    sy = floor_y
                    sw *= max(0.55, 1.0 - air / 700.0)
            d.ellipse([cx - sw, sy - 14, cx + sw, sy + 14], fill=(60, 60, 70, 40))
        # پاها
        hip = T((0, 0))
        for side in ("l", "r"):
            k, f = T(pose["knee_" + side]), T(pose["foot_" + side])
            d.line([hip, k, f], fill=ink, width=lw, joint="curve")
            for pt in (k,):
                d.ellipse([pt[0] - lw / 2 + 1, pt[1] - lw / 2 + 1,
                           pt[0] + lw / 2 - 1, pt[1] + lw / 2 - 1], fill=ink)
            # کف پا
            d.line([f, (f[0] + facing * 26 * s * 0.5, f[1])], fill=ink, width=lw)
        # تنه
        neck = T((0, BODY))
        d.line([hip, neck], fill=ink, width=lw)
        # دست‌ها
        for side in ("l", "r"):
            sh = T((16 if side == "r" else -16, SHOULDER_Y))
            el, ha = T(pose["elbow_" + side]), T(pose["hand_" + side])
            d.line([sh, el, ha], fill=ink, width=max(4, lw - 2), joint="curve")
        # سر
        hc_char = (0, BODY + NECK_GAP + HEAD_R)
        if ang:
            hc_char = _rot(hc_char, ang)
        tilt = pose.get("head_tilt", 0.0)
        hx, hy = cx + facing * hc_char[0] * s, cy_eff - hc_char[1] * s
        r = HEAD_R * s
        d.ellipse([hx - r, hy - r, hx + r, hy + r], outline=ink, width=lw)
        # اکسسوارها (پشت چهره)
        if self.cap:
            c = self.cap
            d.pieslice([hx - r, hy - r, hx + r, hy + r], 180, 360, fill=c,
                       outline=ink, width=max(3, lw - 6))
            d.line([(hx - r * 1.30, hy - r * 0.10), (hx + r * 1.30, hy - r * 0.10)],
                   fill=c, width=max(6, int(lw * 0.8)))
            d.line([(hx - r * 1.30, hy - r * 0.10), (hx + r * 1.30, hy - r * 0.10)],
                   outline=None, fill=c, width=max(6, int(lw * 0.8)))
            d.line([(hx - r * 1.28, hy - r * 0.10), (hx + r * 1.28, hy - r * 0.06)],
                   fill=ink, width=max(2, lw - 8))
        if self.hair:
            for k in (-1, 0, 1):
                x0 = hx + k * r * 0.45
                d.line([(x0, hy - r + 2), (x0 + 8 * k, hy - r - 14 * s * 0.6)],
                       fill=ink, width=max(3, lw - 6))
        _face(d, (hx, hy), r, tilt * facing, pose.get("face", "smile"),
              pose.get("eyes", "dot"), s, ink)
        if self.glasses:
            gr = r * 0.30
            gy = hy - r * 0.10
            for sx in (-1, 1):
                gx = hx + sx * r * 0.36
                d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], outline=ink, width=max(3, lw - 7))
            d.line([(hx - r * 0.08, gy), (hx + r * 0.08, gy)], fill=ink, width=max(3, lw - 7))
        return d


# ================================================================ پراپ‌ها
def wifi_symbol(d, cx, cy, size=120, color=(60, 170, 90), bars=3, crossed=False,
                cross_color=(220, 50, 50), alpha=255):
    """نماد وای‌فای: سه کمان بالارونده + نقطه. اگر crossed=True ضربدر قرمز."""
    col = (*color, alpha)
    d.ellipse([cx - size * 0.10, cy - size * 0.10, cx + size * 0.10, cy + size * 0.10], fill=col)
    for i in range(3):
        if bars < i + 1:
            continue
        r = size * (0.30 + 0.35 * i)
        d.arc([cx - r, cy - r, cx + r, cy + r], 222, 318, fill=col, width=max(6, int(size * 0.09)))
    if crossed:
        cc = (*cross_color, alpha)
        lw = max(10, int(size * 0.14))
        r2 = size * 0.62
        d.line([(cx - r2, cy - r2), (cx + r2, cy + r2)], fill=cc, width=lw)
        d.line([(cx - r2, cy + r2), (cx + r2, cy - r2)], fill=cc, width=lw)


def router(d, x0, y0, w=230, h=90, led="red", blink=False, t=0.0, label="مودم"):
    """مودم روی میز؛ (x0,y0) گوشهٔ پایین-چپ بدنه."""
    body = (52, 56, 66)
    d.rounded_rectangle([x0, y0 - h, x0 + w, y0], 18, fill=body, outline=INK, width=5)
    # آنتن‌ها
    for i, ax in enumerate((x0 + w * 0.22, x0 + w * 0.78)):
        top = y0 - h - 62
        d.line([(ax, y0 - h + 6), (ax + (10 if i == 0 else -10), top)], fill=INK, width=7)
        d.ellipse([ax + (10 if i == 0 else -10) - 7, top - 7, ax + (10 if i == 0 else -10) + 7, top + 7],
                  fill=INK)
    # LEDها
    on = (not blink) or (math.sin(2 * math.pi * 2.4 * t) > -0.2)
    cols = {"red": (235, 70, 60), "amber": (245, 170, 40), "green": (70, 190, 100),
            "off": (150, 150, 155)}
    c = cols[led] if on else cols["off"]
    for i in range(3):
        lx = x0 + w - 34 - i * 30
        d.ellipse([lx - 9, y0 - 30, lx + 9, y0 - 12], fill=c)
    if label:
        pass  # متن بعداً با fatext روی تصویر اصلی


def router_label(img, x0, y0, w=230, label="مودم"):
    txt(img, (x0 + w * 0.35, y0 - 55), label, _font(BOLD, 30), (240, 240, 245))


def table(d, x0, y_top, w=280, h=140):
    d.rounded_rectangle([x0, y_top, x0 + w, y_top + 22], 10, fill=(196, 158, 112), outline=INK, width=5)
    for lx in (x0 + 14, x0 + w - 26):
        d.line([(lx, y_top + 22), (lx, y_top + h)], fill=INK, width=7)


def couch(d, x0, y_top, w=460, color=(120, 150, 205)):
    """مبل: (x0, y_top) بالای نشیمن."""
    seat_h, back_h = 78, 210
    d.rounded_rectangle([x0, y_top - back_h, x0 + 74, y_top + seat_h], 22, fill=color, outline=INK, width=6)
    d.rounded_rectangle([x0 + w - 74, y_top - back_h, x0 + w, y_top + seat_h], 22, fill=color, outline=INK, width=6)
    d.rounded_rectangle([x0 + 40, y_top, x0 + w - 40, y_top + seat_h], 16, fill=_lighten(color, 24), outline=INK, width=6)
    for lx in (x0 + 52, x0 + w - 68):
        d.line([(lx, y_top + seat_h), (lx, y_top + seat_h + 34)], fill=INK, width=7)


def _lighten(c, amt):
    return tuple(min(255, v + amt) for v in c)


def big_button(d, cx, cy, r=74, pressed=False, label=None):
    col = (196, 48, 48) if not pressed else (150, 40, 40)
    d.ellipse([cx - r - 16, cy - r - 16, cx + r + 16, cy + r + 16], outline=INK, width=7)
    d.ellipse([cx - r * (0.86 if pressed else 1), cy - r * (0.86 if pressed else 1),
               cx + r * (0.86 if pressed else 1), cy + r * (0.86 if pressed else 1)],
              fill=col, outline=INK, width=7)
    d.ellipse([cx - r * 0.45, cy - r * 0.45, cx + r * 0.05, cy - r * 0.05], fill=(255, 255, 255, 90))


def bubble(img, cx, cy, text, h=110, accent=(60, 90, 170)):
    """حباب گفتار با متن فارسی؛ (cx, cy) مرکز حباب."""
    d = ImageDraw.Draw(img, "RGBA")
    f = _font(BOLD, 40)
    mask, _ = _measure_mask(text, f)
    tw, th = mask.size
    w = tw + 100
    x0, y0 = cx - w / 2, cy - h / 2
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], 34, fill=(255, 255, 255, 245),
                        outline=INK, width=5)
    d.polygon([(cx - 26, y0 + h - 2), (cx + 26, y0 + h - 2), (cx - 4, y0 + h + 42)],
              fill=(255, 255, 255, 245))
    d.line([(cx - 26, y0 + h - 1), (cx - 4, y0 + h + 42)], fill=INK, width=5)
    d.line([(cx - 4, y0 + h + 42), (cx + 26, y0 + h - 1)], fill=INK, width=5)
    d.line([(cx - 24, y0 + h - 3), (cx + 24, y0 + h - 3)], fill=(255, 255, 255, 245), width=8)
    txt(img, (cx, cy - 4), text, f, (*INK,), anchor="mm")
    return (x0, y0, x0 + w, y0 + h)


_M_CACHE = {}


def _measure_mask(text, font):
    from fatext import render_mask
    key = (text, font.path, font.size)
    if key not in _M_CACHE:
        mask, x0, y0, adv, asc, desc = render_mask(text, font.path, font.size)
        _M_CACHE[key] = (mask, (x0, y0))
    return _M_CACHE[key]


def draw_marks(img, cx, cy, kind="!", color=(220, 60, 50), size=64, alpha=255,
               pop=1.0):
    """علامت ! یا ? بالای سر با پاپ."""
    f = _font(BLACK, int(size * max(0.4, pop)))
    m, _ = _measure_mask(kind, f)
    col = (*color, int(alpha * max(0.0, min(1.0, pop))))
    solid = Image.new("RGBA", m.size, col)
    solid.putalpha(m)
    for dx, dy, sc, a in ((-52, 6, 0.75, 0.8), (0, -10, 1.0, 1.0), (52, 6, 0.75, 0.8)):
        mm = m.resize((max(1, int(m.width * sc)), max(1, int(m.height * sc))))
        lay = Image.new("RGBA", mm.size, col)
        lay.putalpha(mm.point(lambda v: int(v * a)))
        img.alpha_composite(lay, (int(cx + dx - mm.width / 2), int(cy + dy - mm.height)))


def sweat(d, x, y, s=1.0, color=(90, 160, 230)):
    c = (*color, 230)
    d.polygon([(x - 10 * s, y - 16 * s), (x + 10 * s, y - 16 * s), (x, y + 12 * s)], fill=c)
    d.ellipse([x - 12 * s, y - 2 * s, x + 12 * s, y + 22 * s], fill=c)


def heart(d, x, y, s=1.0, color=(230, 70, 110)):
    c = (*color, 235)
    r = 11 * s
    d.ellipse([x - 2 * r, y - 2 * r, x, y], fill=c)
    d.ellipse([x, y - 2 * r, x + 2 * r, y], fill=c)
    d.polygon([(x - 2 * r, y - r * 0.9), (x + 2 * r, y - r * 0.9), (x, y + 2 * r)], fill=c)


def sparkle(d, cx, cy, r=16, color=(250, 200, 70), alpha=230):
    c = (*color, alpha)
    d.line([(cx - r, cy), (cx + r, cy)], fill=c, width=6)
    d.line([(cx, cy - r), (cx, cy + r)], fill=c, width=6)
    d.line([(cx - r * 0.5, cy - r * 0.5), (cx + r * 0.5, cy + r * 0.5)], fill=c, width=4)
    d.line([(cx - r * 0.5, cy + r * 0.5), (cx + r * 0.5, cy - r * 0.5)], fill=c, width=4)


def confetti_rng(seed=7):
    rnd = random.Random(seed)
    pts = []
    for i in range(70):
        pts.append(dict(x=rnd.uniform(40, W - 40), y0=rnd.uniform(-1600, -40),
                        v=rnd.uniform(180, 420), sz=rnd.uniform(8, 18),
                        col=rnd.choice([(235, 80, 90), (70, 160, 235), (250, 190, 60),
                                        (110, 200, 120), (200, 110, 220), (255, 255, 255)]),
                        ph=rnd.uniform(0, 6.28), spin=rnd.uniform(2, 6)))
    return pts


def draw_confetti(d, pts, t, area_bottom=1700):
    for p in pts:
        y = (p["y0"] + p["v"] * t) % 2100 - 200
        x = p["x"] + 26 * math.sin(p["ph"] + t * p["spin"] * 0.4)
        if y > area_bottom:
            continue
        a = math.sin(p["ph"] + t * p["spin"]) * 0.7
        w2, h2 = p["sz"], p["sz"] * 0.55
        pts4 = [(x + math.cos(a) * dx * w2 - math.sin(a) * dy * h2,
                 y + math.sin(a) * dx * w2 + math.cos(a) * dy * h2)
                for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        d.polygon(pts4, fill=(*p["col"], 225))


# ================================================================ کارت متن و نوار
def bg_base(color, accent, floor_y=1560):
    """پس‌زمینهٔ صحنه: رنگ تخت + هالهٔ نرم + خط کف."""
    img = Image.new("RGBA", (W, H), (*color, 255))
    d = ImageDraw.Draw(img, "RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    for (cx, cy, r, a) in ((150, 340, 300, 26), (950, 1280, 340, 22),
                           (880, 240, 220, 18), (170, 1760, 260, 16)):
        od.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255, a))
    ov = ov.filter(ImageFilter.GaussianBlur(60))
    img = Image.alpha_composite(img, ov)
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([0, floor_y, W, H], fill=(30, 30, 40, 14))
    d.line([(0, floor_y), (W, floor_y)], fill=(60, 62, 72, 60), width=4)
    return img


def text_card(img, title, sub, accent, y=250):
    """کارت سفید بالا + چیپ رنگی زیرش."""
    d = ImageDraw.Draw(img, "RGBA")
    f = _font(BLACK, 86 if len(title) <= 16 else (72 if len(title) <= 24 else 60))
    m, _ = _measure_mask(title, f)
    tw = m.width
    cw = min(W - 90, tw + 120)
    ch = 150
    x0 = (W - cw) / 2
    # سایه
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.rounded_rectangle([x0 + 6, y + 10, x0 + cw + 6, y + ch + 10], 40, fill=(30, 30, 40, 60))
    sh = sh.filter(ImageFilter.GaussianBlur(10))
    img.alpha_composite(sh)
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle([x0, y, x0 + cw, y + ch], 40, fill=(255, 255, 255, 250),
                        outline=(*_dark(accent, 30), 255), width=5)
    txt(img, (W / 2, y + ch / 2 - 6), title, f, (42, 44, 54), anchor="mm")
    if sub:
        fs = _font(BOLD, 42)
        ms, _ = _measure_mask(sub, fs)
        sw = ms.width + 84
        d.rounded_rectangle([W / 2 - sw / 2, y + ch + 22, W / 2 + sw / 2, y + ch + 96],
                            34, fill=(*accent, 255))
        txt(img, (W / 2, y + ch + 58), sub, fs, (255, 255, 255), anchor="mm")
    return y + ch


def _dark(c, amt):
    return tuple(max(0, v - amt) for v in c)


def progress(d, frac, accent, y=1836):
    x0, x1 = 70, W - 70
    d.rounded_rectangle([x0, y, x1, y + 16], 8, fill=(255, 255, 255, 90))
    w = max(16, (x1 - x0) * max(0.0, min(1.0, frac)))
    d.rounded_rectangle([x0, y, x0 + w, y + 16], 8, fill=(*accent, 255))


def footer(img, text, accent, y=1770):
    txt(img, (W / 2, y), text, _font(MED, 34), (*_dark(accent, 60), 210), anchor="mm")


# ================================================================ رندر ویدیو
def render_reel(cfg, audio_files=None, out_path=None):
    """
    cfg: dict با کلیدها:
      slug, scenes: [dict(bg, accent, title, sub, dur, draw(d,img,t,T,ctx))],
      char: Stickman, footer, cover(cfg), caption
    audio_files: مسیر mp3 به ازای صحنه‌های گوینده (None → صحنه بدون صدا با dur پیش‌فرض)
    """
    slug = cfg["slug"]
    out_path = out_path or os.path.join(OUTDIR, f"{slug}_reel.mp4")
    tmp = os.path.join(OUTDIR, "toolkit", f"tmp_{slug}")
    os.makedirs(tmp, exist_ok=True)

    # ۱) طول صحنه‌ها بر اساس نریشن
    LEAD, TAIL = 0.45, 0.85
    durs = []
    for i, sc in enumerate(cfg["scenes"]):
        a = audio_files[i] if audio_files else None
        if a and os.path.isfile(a):
            d = LEAD + mp3_dur(a) + TAIL
        else:
            d = sc.get("dur", 5.0)
        durs.append(max(sc.get("min", 3.8), d))
    total = sum(durs)
    nframes = int(round(total * FPS))
    print(f"[i] صحنه‌ها: {[round(x,2) for x in durs]} | کل: {total:.2f}s -> {nframes} فریم")

    # ۲) پایه‌های ایستای هر صحنه (پس‌زمینه + کارت متن) یک‌بار ساخته می‌شوند
    bases = []
    for sc in cfg["scenes"]:
        base = bg_base(sc["bg"], sc["accent"])
        text_card(base, sc["title"], sc.get("sub"), sc["accent"])
        if cfg.get("footer"):
            footer(base, cfg["footer"], sc["accent"])
        bases.append(base)

    # ۳) رندر فریم‌ها → ffmpeg
    raw = os.path.join(tmp, "v.mp4")
    proc = subprocess.Popen(
        [FF, "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
         "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
         "-crf", "25", "-pix_fmt", "yuv420p", raw],
        stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    ctx = {"confetti": confetti_rng(11)}
    for fi in range(nframes):
        t = fi / FPS
        # صحنهٔ فعال
        acc = 0.0
        si = 0
        for i, dd in enumerate(durs):
            if t < acc + dd or i == len(durs) - 1:
                si = i
                break
            acc += dd
        lt = t - acc
        T = durs[si]
        img = bases[si].copy()
        d = ImageDraw.Draw(img, "RGBA")
        cfg["scenes"][si]["draw"](d, img, lt, T, ctx)
        # نوار پیشرفت
        progress(d, t / total, cfg["scenes"][si]["accent"])
        # فید ورود/خروج کل ریل
        frame = np.asarray(img.convert("RGB"), dtype=np.uint8).copy()
        if t < 0.35:
            frame = (frame * (t / 0.35)).astype(np.uint8)
        rem = total - t
        if rem < 0.35:
            frame = (frame * (rem / 0.35)).astype(np.uint8)
        proc.stdin.write(frame.tobytes())
    proc.stdin.close()
    proc.wait()

    # ۴) صدا (در صورت وجود نریشن)
    if audio_files:
        parts = []
        for i, a in enumerate(audio_files):
            if not (a and os.path.isfile(a)):
                seg = os.path.join(tmp, f"a{i}.wav")
                subprocess.run([FF, "-y", "-f", "lavfi", "-i",
                                f"anullsrc=r=44100:cl=stereo", "-t", f"{durs[i]:.3f}",
                                "-c:a", "pcm_s16le", seg], check=True, capture_output=True)
                parts.append(seg)
                continue
            seg = os.path.join(tmp, f"a{i}.wav")
            dl = int(LEAD * 1000)
            subprocess.run([FF, "-y", "-i", a,
                            "-af", f"adelay={dl}|{dl},apad", "-t", f"{durs[i]:.3f}",
                            "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le", seg],
                           check=True, capture_output=True)
            parts.append(seg)
        lst = os.path.join(tmp, "al.txt")
        open(lst, "w").write("".join(f"file '{os.path.abspath(p)}'\n" for p in parts))
        aud = os.path.join(tmp, "mix.wav")
        subprocess.run([FF, "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c:a",
                        "pcm_s16le", aud], check=True, capture_output=True)
        final = out_path
        subprocess.run([FF, "-y", "-i", raw, "-i", aud,
                        "-af", "loudnorm=I=-15:TP=-1.5",
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "96k", "-ar", "44100",
                        "-movflags", "+faststart", "-shortest", final],
                       check=True, capture_output=True)
    else:
        final = out_path
        subprocess.run([FF, "-y", "-i", raw, "-c:v", "copy", "-movflags", "+faststart", final],
                       check=True, capture_output=True)

    size_mb = os.path.getsize(final) / 1048576
    print(f"[✓] {final} | {mp3_dur(final):.2f}s | {size_mb:.2f} MB")
    if size_mb > 4.0:   # فشرده‌تر اگر لازم بود
        small = os.path.join(tmp, "small.mp4")
        subprocess.run([FF, "-y", "-i", final, "-c:v", "libx264", "-preset", "slow",
                        "-crf", "28", "-pix_fmt", "yuv420p", "-c:a", "copy",
                        "-movflags", "+faststart", small], check=True, capture_output=True)
        if os.path.getsize(small) < os.path.getsize(final):
            import shutil
            shutil.move(small, final)
            print(f"[✓] فشرده‌سازی مجدد: {os.path.getsize(final)/1048576:.2f} MB")
    return final

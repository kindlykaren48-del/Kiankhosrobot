"""
reel_engine.py — موتور ریل انیمیشنی «کارخانهٔ ریلز» (نسخهٔ ۴)
==============================================================
- پس‌زمینهٔ گرادیانی آرام + کارت تصویر ۴:۵ با زوم آهسته (Ken Burns)
- عنوان فارسی با HarfBuzz (fatext)، کارت نکته، نوار پیشرفت، پلاک نام
- فقط نریشن؛ بدون موسیقی. ۱۰۸۰×۱۹۲۰ · ۳۰fps · ≤۴MB
- متن هیچ‌وقت روی تصویر نمی‌افتد: بالا = عنوان، وسط = تصویر، پایین = نکته

خروجی هر موضوع: <slug>_reel.mp4 + <slug>_cover.png + <slug>_caption.txt
"""
from __future__ import annotations

import os
import re
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "Kiankhosrobot", "toolkit"))
import imageio_ffmpeg  # noqa: E402
from fatext import draw_text, measure  # noqa: E402

FF = imageio_ffmpeg.get_ffmpeg_exe()

W, H, FPS = 1080, 1920, 30
ROOT = os.path.abspath(os.path.join(HERE, ".."))
FONT_DIR = next((d for d in (os.environ.get("REEL_FONTS", ""),
                             os.path.join(ROOT, "fonttmp", "fonts", "ttf"),
                             "/home/user/fonttmp/fonts/ttf")
                 if d and os.path.isfile(os.path.join(d, "Vazirmatn-Bold.ttf"))), "")
BLACK = os.path.join(FONT_DIR, "Vazirmatn-Black.ttf")
BOLD = os.path.join(FONT_DIR, "Vazirmatn-Bold.ttf")
MED = os.path.join(FONT_DIR, "Vazirmatn-Medium.ttf")
REG = os.path.join(FONT_DIR, "Vazirmatn-Regular.ttf")
OUTDIR = os.path.join(ROOT, "reels")
ASSETS = os.path.join(OUTDIR, "assets")
TMP = os.path.join(OUTDIR, "tmp")

PALETTES = {
    "warm":  {"bg1": (253, 246, 236), "bg2": (247, 231, 218), "ink": (31, 42, 61),
              "accent": (214, 92, 76), "soft": (236, 214, 200), "good": (74, 122, 96)},
    "night": {"bg1": (246, 240, 233), "bg2": (232, 220, 214), "ink": (28, 38, 58),
              "accent": (196, 122, 62), "soft": (226, 208, 196), "good": (74, 110, 122)},
    "sage":  {"bg1": (249, 247, 240), "bg2": (231, 236, 228), "ink": (30, 46, 54),
              "accent": (72, 122, 104), "soft": (214, 226, 214), "good": (196, 108, 84)},
    "mint":  {"bg1": (247, 248, 242), "bg2": (226, 236, 230), "ink": (30, 48, 56),
              "accent": (58, 112, 132), "soft": (212, 228, 226), "good": (206, 118, 86)},
    "clay":  {"bg1": (253, 245, 238), "bg2": (243, 225, 212), "ink": (48, 40, 38),
              "accent": (176, 96, 72), "soft": (238, 216, 202), "good": (86, 118, 96)},
}

NAME_PLATE = "دکتر کیانوش سالاریان"


# ------------------------------------------------------------------ ابزار متن
def font(path, size):
    return ImageFont.truetype(path, size)


def wrap_fa(text, f, max_w):
    """شکستن خط فارسی بر اساس اندازهٔ واقعی متن (HarfBuzz)."""
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        trial = (cur + " " + w_).strip()
        if measure(trial, f)[2] <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def fit_title(text, max_w, start=92, minimum=58, max_lines=2):
    size = start
    while size >= minimum:
        f = font(BLACK, size)
        lines = wrap_fa(text, f, max_w)
        if len(lines) <= max_lines and all(measure(l, f)[2] <= max_w for l in lines):
            return f, lines
        size -= 4
    f = font(BLACK, minimum)
    return f, wrap_fa(text, f, max_w)


def text_layer(lines, f, fill, xy, anchor="ma", line_gap=1.42, shadow=None):
    """متن چندخطی را روی لایهٔ RGBA شفاف می‌کشد (برای انیمیشن)."""
    lh = int(f.size * line_gap)
    pad = int(f.size * 1.2)
    wdt = max(measure(l, f)[2] for l in lines) + pad * 2
    hgt = lh * len(lines) + pad * 2
    lay = Image.new("RGBA", (int(wdt), int(hgt)), (0, 0, 0, 0))
    x = wdt / 2 if anchor[0] == "m" else (pad if anchor[0] == "l" else wdt - pad)
    y = pad + f.size * 0.85
    for ln in lines:
        if shadow:
            draw_text(lay, (x + 2, y + 3), ln, font=f, fill=shadow, anchor="ma")
        draw_text(lay, (x, y), ln, font=f, fill=fill, anchor="ma")
        y += lh
    return lay


def paste_alpha(base, layer, xy, alpha=1.0, dy=0):
    if alpha <= 0.01:
        return
    if alpha < 0.999:
        a = layer.getchannel("A").point(lambda v: int(v * alpha))
        layer = layer.copy()
        layer.putalpha(a)
    base.alpha_composite(layer, (int(xy[0]), int(xy[1] + dy)))


# ------------------------------------------------------------------ پس‌زمینه
def glow_layer():
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for (cx, cy, r, a) in ((140, 260, 300, 40), (960, 760, 320, 30),
                           (900, 1500, 280, 26), (120, 1680, 260, 22)):
        gd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255, a))
    return glow.filter(ImageFilter.GaussianBlur(70))


def make_base(pal, eyebrow, title_lay, title_y, sub_lay, sub_y, card_box):
    bg1, bg2 = pal["bg1"], pal["bg2"]
    img = Image.new("RGB", (W, H), bg1)
    d = ImageDraw.Draw(img)
    for y in range(H):
        f = y / (H - 1)
        d.line([(0, y), (W, y)], fill=tuple(int(bg1[k] + (bg2[k] - bg1[k]) * f) for k in range(3)))
    img = img.convert("RGBA")
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for (cx, cy, r, a) in ((140, 260, 300, 40), (960, 760, 320, 30),
                           (900, 1500, 280, 26), (120, 1680, 260, 22)):
        gd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255, a))
    glow = glow.filter(ImageFilter.GaussianBlur(70))
    img.alpha_composite(glow)

    d = ImageDraw.Draw(img, "RGBA")
    # نوار رنگی باریک بالای کادر
    d.rounded_rectangle([0, 0, W, 12], 6, fill=(*pal["accent"], 255))

    # چیپ دسته‌بندی
    fe = font(BOLD, 34)
    tw = measure(eyebrow, fe)[2]
    cw = tw + 76
    d.rounded_rectangle([(W - cw) / 2, 78, (W + cw) / 2, 152], 37,
                        fill=(255, 255, 255, 210), outline=(*pal["soft"], 255), width=3)
    draw_text(img, (W / 2, 115), eyebrow, font=fe, fill=pal["accent"], anchor="mm")

    paste_alpha(img, title_lay, ((W - title_lay.width) / 2, title_y))
    if sub_lay is not None:
        paste_alpha(img, sub_lay, ((W - sub_lay.width) / 2, sub_y))

    # سایهٔ کارت تصویر
    cx0, cy0, cx1, cy1 = card_box
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([cx0 + 2, cy0 + 12, cx1 + 2, cy1 + 16], 44,
                                        fill=(90, 70, 56, 34))
    sh = sh.filter(ImageFilter.GaussianBlur(34))
    img.alpha_composite(sh)

    # پلاک نام + نوار پیشرفت
    draw_text(img, (W / 2, 1806), NAME_PLATE, font=font(MED, 32),
              fill=(*pal["ink"], 130), anchor="mm")
    d = ImageDraw.Draw(img, "RGBA")
    return img


def pill(base, pal, text, y, f=None, fill=None, txt_fill=(255, 255, 255)):
    f = f or font(BOLD, 46)
    lines = wrap_fa(text, f, W - 260)
    if len(lines) > 1:
        f = font(BOLD, 38)
        lines = wrap_fa(text, f, W - 240)
    tw = max(measure(l, f)[2] for l in lines)
    hgt = 96 + (len(lines) - 1) * int(f.size * 1.35)
    cw = tw + 96
    x0, y0 = (W - cw) / 2, y
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay, "RGBA")
    d.rounded_rectangle([x0, y0 + 10, x0 + cw, y0 + hgt + 10], hgt / 2, fill=(60, 40, 30, 40))
    return lay, lines, f, (x0, y0, cw, hgt)


# ------------------------------------------------------------------ کارت تصویر
def card_frame(path, box, zoom, tilt=0.0):
    x0, y0, x1, y1 = box
    cw, chh = int(x1 - x0), int(y1 - y0)
    src = Image.open(path).convert("RGB")
    r_src = src.width / src.height
    r_tgt = cw / chh
    if r_src > r_tgt:                       # برش افقی
        nh = int(src.height * 1.06)
        nw = int(nh * r_tgt)
    else:
        nw = int(src.width * 1.06)
        nh = int(nw / r_tgt)
    # کادر برش با زوم
    nw = int(nw / zoom)
    nh = int(nh / zoom)
    cx, cy = src.width / 2, src.height * 0.55
    left = max(0, min(src.width - nw, int(cx - nw / 2)))
    top = max(0, min(src.height - nh, int(cy - nh / 2)))
    crop = src.crop((left, top, left + nw, top + nh)).resize((cw, chh), Image.LANCZOS)
    mask = Image.new("L", (cw, chh), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, cw, chh], 40, fill=255)
    return crop, mask


# ------------------------------------------------------------------ ساخت اسلاید
def build_layout(cfg, pal, slide):
    """ابعاد و لایه‌های ایستای یک اسلاید را برمی‌گرداند."""
    f_title, lines = fit_title(slide["title"], W - 150, start=88, minimum=54, max_lines=2)
    title_lay = text_layer(lines, f_title, pal["ink"], (0, 0))
    title_y = 190
    title_bottom = title_y + title_lay.height - int(f_title.size * 0.55)

    sub_lay, sub_y = None, 0
    if slide.get("sub"):
        fs = font(BOLD, 42)
        sub_lay = text_layer([slide["sub"]], fs, pal["accent"], (0, 0))
        sub_y = title_bottom - int(fs.size * 0.25)
        title_bottom = sub_y + sub_lay.height - int(fs.size * 0.18)

    top = max(486, title_bottom + 48)
    bottom = 1636
    chh = min(1130, bottom - top)
    cw = int(chh * 0.8)
    if cw > W - 150:
        cw = W - 150
        chh = int(cw / 0.8)
    box = ((W - cw) // 2, int(top), (W - cw) // 2 + cw, int(top + chh))

    base = make_base(pal, cfg["eyebrow"], title_lay, title_y, sub_lay, sub_y, box)

    # کارت نکته
    pill_lay, lines_p, f_p, (px, py, pcw, pch) = pill(base, pal, slide["tip"], 1660)
    pd = ImageDraw.Draw(pill_lay, "RGBA")
    pd.rounded_rectangle([px, py + 10, px + pcw, py + pch + 10], pch / 2, fill=(40, 30, 24, 45))
    return {
        "base": base,
        "box": box,
        "title_lay": title_lay, "title_pos": ((W - title_lay.width) / 2, title_y),
        "sub_lay": sub_lay,
        "sub_pos": ((W - sub_lay.width) / 2, sub_y) if sub_lay else None,
        "tip_lines": lines_p, "tip_font": f_p, "tip_box": (px, py, pcw, pch),
        "tip_layer": pill_lay,
        "dur": slide["dur"],
    }


def render_frame(lay, cfg, pal, t, dur):
    img = lay["base"].copy()
    zoom = 1.0 + 0.075 * min(1.0, t / max(dur, 0.01))
    crop, mask = card_frame(lay["src"], lay["box"], zoom)
    img.paste(crop, (lay["box"][0], lay["box"][1]), mask)
    d = ImageDraw.Draw(img, "RGBA")
    x0, y0, x1, y1 = lay["box"]
    d.rounded_rectangle([x0, y0, x1, y1], 40, outline=(255, 255, 255, 210), width=6)

    # ورود نرم لایه‌های متن
    if t < 0.45:
        a = t / 0.45
        dy = int(18 * (1 - a))
        img.paste(lay["base"], (0, 0))  # پایهٔ بدون متن
        img.paste(crop, (x0, y0), mask)
        d = ImageDraw.Draw(img, "RGBA")
        d.rounded_rectangle([x0, y0, x1, y1], 40, outline=(255, 255, 255, 210), width=6)
        paste_alpha(img, lay["title_lay"], lay["title_pos"], a, dy)
        if lay["sub_lay"] is not None:
            paste_alpha(img, lay["sub_lay"], lay["sub_pos"], max(0.0, a - 0.2), dy)
        paste_alpha(img, lay["tip_layer"], (0, 0), max(0.0, a - 0.35), dy)
    else:
        paste_alpha(img, lay["title_lay"], lay["title_pos"])
        if lay["sub_lay"] is not None:
            paste_alpha(img, lay["sub_lay"], lay["sub_pos"])
        paste_alpha(img, lay["tip_layer"], (0, 0))

    # نوار پیشرفت
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle([70, 1858, W - 70, 1872], 7, fill=(255, 255, 255, 110))
    prog = max(0.0, min(1.0, t / dur))
    d.rounded_rectangle([70, 1858, 70 + max(18, (W - 140) * prog), 1872], 7,
                        fill=(*pal["accent"], 255))
    return img


def draw_tip(img, lay, pal):
    """پلاک نکته را با پس‌زمینهٔ رنگی می‌کشد."""
    px, py, pcw, pch = lay["tip_box"]
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle([px, py, px + pcw, py + pch], pch / 2, fill=(*pal["accent"], 255))
    y = py + pch / 2 - (len(lay["tip_lines"]) - 1) * lay["tip_font"].size * 0.68
    for ln in lay["tip_lines"]:
        draw_text(img, (W / 2, y), ln, font=lay["tip_font"], fill=(255, 255, 255, 255), anchor="mm")
        y += lay["tip_font"].size * 1.36


def draw_tip_layer(lay, pal):
    """پلاک نکته به‌صورت لایهٔ مستقل (برای انیمیشن ورود)."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    px, py, pcw, pch = lay["tip_box"]
    ImageDraw.Draw(layer, "RGBA").rounded_rectangle(
        [px, py, px + pcw, py + pch], pch / 2, fill=(*pal["accent"], 255))
    y = py + pch / 2 - (len(lay["tip_lines"]) - 1) * lay["tip_font"].size * 0.68
    for ln in lay["tip_lines"]:
        draw_text(layer, (W / 2, y), ln, font=lay["tip_font"], fill=(255, 255, 255, 255), anchor="mm")
        y += lay["tip_font"].size * 1.36
    return layer


# ------------------------------------------------------------------ کاور
def make_cover(cfg, pal):
    f_title, lines = fit_title(cfg["cover_title"], W - 130, start=100, minimum=56, max_lines=2)
    img = Image.new("RGB", (W, H), pal["bg1"]).convert("RGBA")
    d = ImageDraw.Draw(img)
    bg1, bg2 = pal["bg1"], pal["bg2"]
    for y in range(H):
        fa = y / (H - 1)
        d.line([(0, y), (W, y)], fill=tuple(int(bg1[k] + (bg2[k] - bg1[k]) * fa) for k in range(3)))
    img.alpha_composite(glow_layer())
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle([0, 0, W, 14], 7, fill=(*pal["accent"], 255))

    # اندازه‌ها
    title_lay = text_layer(lines, f_title, pal["ink"], (0, 0))
    title_y = 214
    fs = font(BOLD, 44)
    sub_lay = text_layer([cfg["subtitle"]], fs, pal["accent"], (0, 0))
    sub_y = title_y + title_lay.height - int(f_title.size * 0.42)

    top = int(sub_y + sub_lay.height + 18)
    bottom = 1700
    chh = bottom - top
    cwid = int(chh * 0.8)
    if cwid > W - 120:
        cwid = W - 120
        chh = int(cwid / 0.8)
    box = ((W - cwid) // 2, top, (W - cwid) // 2 + cwid, top + chh)

    # سایهٔ کارت (قبل از متن‌ها)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([box[0] + 2, box[1] + 12, box[2] + 2, box[3] + 20], 46,
                                        fill=(90, 70, 56, 34))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(36)))

    # چیپ دسته‌بندی
    fe = font(BOLD, 34)
    tw = measure(cfg["eyebrow"], fe)[2]
    cw = tw + 76
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle([(W - cw) / 2, 92, (W + cw) / 2, 166], 37,
                        fill=(255, 255, 255, 220), outline=(*pal["soft"], 255), width=3)
    draw_text(img, (W / 2, 129), cfg["eyebrow"], font=fe, fill=pal["accent"], anchor="mm")

    paste_alpha(img, title_lay, ((W - title_lay.width) / 2, title_y))
    paste_alpha(img, sub_lay, ((W - sub_lay.width) / 2, sub_y))

    crop, mask = card_frame(cfg["cover_image"], box, 1.04)
    img.paste(crop, (box[0], box[1]), mask)
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle(list(box), 42, outline=(255, 255, 255, 230), width=6)

    # نوار پایین
    d.rounded_rectangle([W / 2 - 330, 1752, W / 2 + 330, 1838], 43, fill=(*pal["accent"], 255))
    draw_text(img, (W / 2, 1795), "ذخیره کن  •  برای مامان و بابای تازه بفرست",
              font=font(BOLD, 33), fill=(255, 255, 255, 255), anchor="mm")
    draw_text(img, (W / 2, 1876), NAME_PLATE, font=font(MED, 30), fill=(*pal["ink"], 145), anchor="mm")
    return img


# ------------------------------------------------------------------ صدا
def dur_of(path):
    o = subprocess.run([FF, "-i", path], capture_output=True).stderr.decode("utf-8", "ignore")
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.?\d*)", o)
    if not m:
        return 0.0
    h, mnt, s = m.groups()
    return int(h) * 3600 + int(mnt) * 60 + float(s)


def build_audio(audio_files, lengths, out_wav):
    sr = 44100
    chunks = []
    for f, L in zip(audio_files, lengths):
        d = dur_of(f)
        total = int(round(L * sr))
        pad_head = int(round(0.35 * sr))
        pcm = subprocess.run([FF, "-v", "quiet", "-i", f, "-f", "s16le", "-ac", "2",
                              "-ar", str(sr), "-"], capture_output=True).stdout
        arr = np.frombuffer(pcm, dtype="<i2")
        if arr.size == 0:
            arr = np.zeros(total * 2, dtype="<i2")
        if arr.size > total * 2:
            arr = arr[:total * 2]
        voice = np.zeros(total * 2, dtype="<i2")
        n = min(arr.size, total * 2 - pad_head * 2)
        voice[pad_head * 2: pad_head * 2 + n] = arr[:n]
        chunks.append(voice)
        print(f"    · صدا {os.path.basename(f)}: {d:.2f}s | برش {L:.2f}s")
    full = np.concatenate(chunks) if chunks else np.zeros(2, dtype="<i2")
    import wave
    with wave.open(out_wav, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(full.tobytes())
    return dur_of(out_wav)


# ------------------------------------------------------------------ رندر
def render(cfg, target_max=4.0):
    pal = PALETTES[cfg.get("palette", "warm")]
    os.makedirs(TMP, exist_ok=True)
    slug = cfg["slug"]
    out_mp4 = os.path.join(OUTDIR, f"{slug}_reel.mp4")

    # ۰) تنظیم سرعت گفتار (فقط نریشن مصنوعی؛ پیش‌فرض ۱۰٪ تندتر)
    tempo = float(cfg.get("tempo", 1.1))
    audio = list(cfg["audio"])
    if abs(tempo - 1.0) > 0.01:
        sped = []
        for i, a in enumerate(audio):
            o = os.path.join(TMP, f"{slug}_sp{i}.mp3")
            subprocess.run([FF, "-y", "-v", "quiet", "-i", a, "-filter:a", f"atempo={tempo}",
                            "-b:a", "128k", o], check=True, capture_output=True)
            sped.append(o)
        audio = sped

    # ۱) مدت هر بخش از روی نریشن
    lengths = []
    for a in audio:
        lengths.append(round(0.35 + dur_of(a) + 0.45, 2))
    total = sum(lengths)
    print(f"[i] {slug}: {len(lengths)} بخش | مجموع {total:.2f}s")

    # ۲) لایه‌های ایستا
    lays = []
    for sc, a, L in zip(cfg["slides"], cfg["audio"], lengths):
        lay = build_layout(cfg, pal, {"title": sc["title"], "sub": sc.get("sub"),
                                      "tip": sc["tip"], "dur": L})
        lay["src"] = sc["image"]
        lay["tip_layer"] = draw_tip_layer(lay, pal)
        lays.append(lay)

    # ۳) فریم‌ها → ffmpeg
    raw = os.path.join(TMP, f"{slug}_v.mp4")
    proc = subprocess.Popen(
        [FF, "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
         "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
         "-pix_fmt", "yuv420p", raw],
        stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for lay, L in zip(lays, lengths):
        n = int(round(L * FPS))
        for i in range(n):
            t = i / FPS
            frame = render_frame(lay, cfg, pal, t, L)
            proc.stdin.write(np.asarray(frame.convert("RGB"), dtype=np.uint8).tobytes())
    proc.stdin.close()
    proc.wait()
    if proc.returncode != 0:
        raise RuntimeError("ffmpeg raw render failed")

    # ۴) صدا
    wav = os.path.join(TMP, f"{slug}_a.wav")
    build_audio(audio, lengths, wav)

    # ۵) میکس + دو-پاس برای سقف حجم
    mix = os.path.join(TMP, f"{slug}_mix.mp4")
    subprocess.run([FF, "-y", "-i", raw, "-i", wav, "-af", "loudnorm=I=-15:TP=-1.5",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "96k", "-ar", "44100",
                    "-shortest", "-movflags", "+faststart", mix], check=True, capture_output=True)
    T = dur_of(mix)
    kbps = max(650, int((target_max * 0.86 * 8192) / max(T, 1)))
    for p in (1, 2):
        cmd = [FF, "-y", "-i", mix, "-c:v", "libx264", "-b:v", f"{kbps}k", "-pass", str(p),
               "-passlogfile", os.path.join(TMP, f"plog_{slug}"), "-preset", "slow",
               "-profile:v", "high", "-level", "4.0", "-pix_fmt", "yuv420p", "-g", "60"]
        cmd += (["-an", "-f", "mp4", "/dev/null"] if p == 1 else
                ["-c:a", "aac", "-b:a", "96k", "-ar", "44100",
                 "-movflags", "+faststart", out_mp4])
        subprocess.run(cmd, check=True, capture_output=True)

    # ۶) کاور + کپشن
    cover = make_cover(cfg, pal)
    cover_path = os.path.join(OUTDIR, f"{slug}_cover.png")
    cover.convert("RGB").save(cover_path, quality=95)
    cap_path = os.path.join(OUTDIR, f"{slug}_caption.txt")
    with open(cap_path, "w", encoding="utf-8") as f:
        f.write(cfg["caption"])
    mb = os.path.getsize(out_mp4) / 1048576
    print(f"[✓] {out_mp4} | {dur_of(out_mp4):.2f}s | {mb:.2f} MB | {kbps}kbps")
    return out_mp4, cover_path, cap_path

#!/usr/bin/env python3
"""کاروسل صدا-تصویری با قالب قفل‌شدهٔ ریل ۴:۵ — عنوان پنجم صف
«این اسباب‌بازی‌ها برای نوزاد خطرناک‌اند» (kid05_toys)

خروجی: ۵ اسلاید PNG + ۵ نریشن جدا MP3 + ۵ ویدیوی جدا MP4 (۱۰۸۰×۱۳۵۰ + صدا)
       + نمای کلی + کپشن + ZIP کامل
ساخت: .venv/bin/python reels/build_car07.py
"""
import os
import re
import subprocess
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import imageio_ffmpeg  # noqa: E402
from reel45_template import asset, build_carousel  # noqa: E402

FF = imageio_ffmpeg.get_ffmpeg_exe()
SLUG = "car07_toys"
EYEBROW = "ایمنی کودک"

DIS = ("⚠️ این محتوا آموزشی است و جایگزین ارزیابی پزشک نیست. "
       "اگر نگران فرزندت هستی، با پزشک کودک مشورت کن.")

SLIDES = [
    dict(palette="clay", image=asset("toys_1.png"), cover=True,
         title="این اسباب‌بازی‌ها برای نوزاد خطرناک‌اند",
         sub="۴ چیز که قبل از خرید باید چک کنی",
         tip="اسباب‌بازی خوب، یعنی اسباب‌بازی ایمن"),
    dict(palette="warm", image=asset("toys_2.png"),
         title="قطعهٔ کوچک، خطر خفگی",
         sub="هر چیزی کوچک‌تر از توپ پینگ‌پنگ، برای زیر ۳ سال خطرناک است",
         tip="تست ساده: لولهٔ دستمال کاغذی"),
    dict(palette="night", image=asset("toys_3.png"),
         title="باتری دکمه‌ای و آهنربا",
         sub="خطرناک‌ترین اشیای خانه؛ همیشه دور از دسترس و قفل‌شده",
         tip="باتری بلعید؟ فوراً اورژانس"),
    dict(palette="sage", image=asset("toys_4.png"),
         title="بند بلند و اسباب‌بازی شکسته",
         sub="بند بلندتر از ۲۰ سانتی‌متر دور گردن خطر دارد؛ شکسته را کنار بگذار",
         tip="خراب شد؟ همین حالا بردار"),
    dict(palette="mint", image=asset("toys_5.png"),
         title="پس چه بخریم؟",
         sub="سه تا پنج اسباب‌بازی ساده و ایمن کافی است؛ بقیه را بچرخان",
         tip="ساده‌تر، امن‌تر، بهتر",
         cta="ذخیره کن • برای مامان و بابای تازه بفرست"),
]

CAPTION = """🧸 این اسباب‌بازی‌ها برای نوزاد خطرناک‌اند

اسباب‌بازی خوب، اسباب‌بازی «ایمن» است؛ نه گران‌ترین. چهار چیز را قبل از خرید و بعد از هر بازی چک کن:

۱) اندازه: هر چیزی که از توپ پینگ‌پنگ کوچک‌تر است، برای کودک زیر ۳ سال خطر خفگی دارد (تست لولهٔ دستمال کاغذی).
۲) باتری دکمه‌ای: اگر بلعیده شود، در کمتر از دو ساعت می‌تواند آسیب جدی بزند. محفظهٔ باتری باید با پیچ بسته شود و باتری هرگز در دسترس کودک نباشد.
۳) آهنربا: دو آهنربای کوچک بلعیده‌شده می‌توانند به هم بچسبند و روده را آسیب بزنند. اسباب‌بازی آهنربایی برای زیر ۳ سال مناسب نیست.
۴) بند و ریسمان: بند بلندتر از ۲۰ سانتی‌متر دور گردن خطر خفگی دارد. اسباب‌بازی شکسته یا ترک‌خورده هم فوراً کنار گذاشته شود.

✅ چند اسباب‌بازی کافی است؟
سه تا پنج گزینهٔ ساده و امن جلوی کودک؛ بقیه را بچرخان. کمتر، بهتر.

🚨 اگر باتری یا آهنربا بلعید: فوراً به اورژانس برو؛ منتظر نشانه نمان.

📌 این پست را ذخیره کن و برای یک مامان یا بابای تازه بفرست.

{dis}

#ایمنی_کودک #نوزاد #اسباب_بازی #خفگی #سلامت_کودک #تربیت_کودک #مادر_و_نوزاد #والدین_آگاه #پیشگیری_از_حادثه #خانه_ایمن
""".format(dis=DIS)


def dur_of(path):
    o = subprocess.run([FF, "-i", path], capture_output=True).stderr.decode("utf-8", "ignore")
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.?\d*)", o)
    if not m:
        return 0.0
    h, mnt, s = m.groups()
    return int(h) * 3600 + int(mnt) * 60 + float(s)


def make_clip(slide_png, mp3, out_mp4):
    """ویدیوی یک اسلاید: تصویر ثابت ۴:۵ + نریشن (AAC)، مناسب اسلاید ویدیویی کاروسل."""
    cmd = [FF, "-y", "-v", "error",
           "-loop", "1", "-framerate", "30", "-i", slide_png,
           "-i", mp3,
           "-af", "apad=pad_dur=0.7",
           "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p",
           "-r", "30", "-c:a", "aac", "-b:a", "128k",
           "-shortest", "-movflags", "+faststart", out_mp4]
    subprocess.run(cmd, check=True)


def main():
    outdir, files, ov_path, cap_path, _zip = build_carousel(
        SLUG, EYEBROW, SLIDES, CAPTION,
        ov_title=("اسباب‌بازی‌های", "خطرناک برای نوزاد"), ov_palette="clay")

    clips = []
    total = 0.0
    for i, slide in enumerate(files, start=1):
        mp3 = os.path.join(outdir, f"{SLUG}_narration_{i:02d}.mp3")
        mp4 = os.path.join(outdir, f"{SLUG}_video_{i:02d}.mp4")
        make_clip(slide, mp3, mp4)
        clips.append(mp4)
        d = dur_of(mp4)
        total += d
        print(f"clip {i}: {os.path.basename(mp4)}  {d:.1f}s  "
              f"{os.path.getsize(mp4) // 1024}KB  (صدا {dur_of(mp3):.1f}s)")

    full = os.path.join(outdir, f"{SLUG}_full.zip")
    with zipfile.ZipFile(full, "w", zipfile.ZIP_DEFLATED) as z:
        for p in files + clips + [os.path.join(outdir, f"{SLUG}_narration_{i:02d}.mp3")
                                  for i in range(1, len(files) + 1)] + [cap_path]:
            z.write(p, os.path.basename(p))
    print(f"[✓] {SLUG}: {len(files)} اسلاید + {len(clips)} ویدیو "
          f"(مجموع {total:.0f} ثانیه) + ZIP کامل {os.path.getsize(full) // 1024}KB")


if __name__ == "__main__":
    main()

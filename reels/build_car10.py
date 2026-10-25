#!/usr/bin/env python3
"""کاروسل صدا-تصویری ۵ اسلایدی با قالب قفل‌شده ریل ۴:۵.

سفارش داخل چت: تبخال دهانی در کودکان، نریشن زن فارسی.
خروجی: ۵ PNG + ۵ MP3 جدا + ۵ MP4 جدا + نسخه یک‌تکه + نمای کلی + کپشن + ZIP کامل.
ساخت: .venv/bin/python reels/build_car10.py
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
SLUG = "car10_oralherpes"
EYEBROW = "سلامت کودک"

DIS = ("⚠️ این محتوا آموزشی است و جایگزین ارزیابی پزشک نیست. "
       "اگر نگران فرزندت هستی، با پزشک کودک مشورت کن.")

SLIDES = [
    dict(palette="clay", image=asset("herpes_1.png"), cover=True,
         title="تبخال دهانی در کودکان",
         sub="از کجا می‌آید و کی جدی است؟",
         tip="بوسه و قاشق مشترک؛ راه انتقال"),
    dict(palette="warm", image=asset("herpes_2.png"),
         title="نشانه‌ها را بشناس",
         sub="تب، زخم دهان و لثه، آبریزش دهان و بی‌اشتهایی",
         tip="دفعه اول ممکن است شدیدتر باشد"),
    dict(palette="night", image=asset("herpes_3.png"),
         title="انتقال را قطع کن",
         sub="نه بوسه روی صورت، نه لیوان و قاشق مشترک",
         tip="دست‌ها را بشویید؛ زخم را دست‌کاری نکنید"),
    dict(palette="sage", image=asset("herpes_4.png"),
         title="مراقبت در خانه",
         sub="مایعات خنک و غذای نرم؛ ترش، شور و تند کمتر",
         tip="دارو فقط با نظر پزشک کودک"),
    dict(palette="mint", image=asset("herpes_5.png"),
         title="این‌ها یعنی مراجعه فوری",
         sub="نوزاد خیلی کوچک، کم‌آبی، درد چشم یا ضعف ایمنی",
         tip="نتوانست بنوشد؟ صبر نکنید",
         cta="ذخیره کن • برای مامان و بابای تازه بفرست"),
]

CAPTION = """👶 تبخال دهانی در کودکان؛ از کجا می‌آید و کی جدی است؟

تبخال دهانی معمولاً با ویروس هرپس سیمپلکس نوع ۱ ایجاد می‌شود و از راه بزاق و تماس نزدیک منتقل می‌شود. در بعضی کودکان، به‌خصوص در اولین ابتلا، فقط یک زخم کوچک لب نیست؛ تب، درد و زخم‌های داخل دهان و لثه، آبریزش دهان، بدغذایی و بی‌قراری هم دیده می‌شود.

✅ انتقال را کمتر کن
• وقتی خودت یا اطرافیان تبخال فعال دارید، صورت کودک و به‌خصوص نوزاد را نبوسید.
• لیوان، قاشق، پستانک، مسواک و حوله را مشترک نکنید.
• دست‌ها را مرتب بشویید و به کودک یاد بدهید به زخم دست نزند و چشمش را نمالد.

✅ مراقبت در خانه
• مایعات خنک را کم‌کم و مکرر بدهید و غذای نرم انتخاب کنید.
• خوراکی‌های ترش، شور، تند و خیلی داغ درد دهان را بیشتر می‌کنند.
• برای تب و درد، دارو و مقدار آن را فقط طبق نظر پزشک کودک یا داروساز انتخاب کنید؛ آنتی‌بیوتیک یا کرم‌های کورتونیِ مانده در خانه را خودسرانه استفاده نکنید.

🚨 سریع با پزشک کودک یا اورژانس مشورت کن اگر کودک نوزاد خیلی کوچک است، نمی‌تواند بنوشد یا شیر بخورد، پوشک خیسش کم شده، دهانش خشک یا خواب‌آلود و بی‌حال است، چشمش قرمز و دردناک یا اشک‌آلود شده، تاول‌ها گسترده‌اند، اگزما یا ضعف ایمنی دارد، تب بالا ادامه‌دار است یا حال عمومی‌اش بدتر می‌شود.

📌 این پست را ذخیره کن و برای یک مامان یا بابای تازه بفرست.

{dis}

#تبخال_دهانی #سلامت_کودک #نوزاد #کودک #مادر_و_نوزاد #والدین_آگاه #پزشک_کودک #کم_آبی #مراقبت_کودک #تربیت_کودک
""".format(dis=DIS)


def dur_of(path):
    out = subprocess.run([FF, "-i", path], capture_output=True).stderr.decode("utf-8", "ignore")
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.?\d*)", out)
    if not m:
        return 0.0
    h, mnt, s = m.groups()
    return int(h) * 3600 + int(mnt) * 60 + float(s)


def make_clip(slide_png, mp3, out_mp4):
    """ویدیوی هر اسلاید: تصویر ثابت + نریشن همان اسلاید و ۰٫۵ ثانیه مکث پایانی."""
    d = dur_of(mp3)
    cmd = [FF, "-y", "-v", "error",
           "-loop", "1", "-framerate", "30", "-i", slide_png,
           "-i", mp3,
           "-af", "apad",
           "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p",
           "-r", "30", "-c:a", "aac", "-b:a", "128k",
           "-t", f"{d + 0.5:.2f}", "-movflags", "+faststart", out_mp4]
    subprocess.run(cmd, check=True)


MAX_TARGET_BYTES = 3_800_000


def ensure_max_size(path, max_bytes=MAX_TARGET_BYTES, audio_kbps=80):
    """اگر MP4 از سقف بزرگ‌تر بود، با بیت‌ریت محاسبه‌شده دوباره فشرده می‌شود."""
    if os.path.getsize(path) <= max_bytes:
        return False
    d = dur_of(path)
    total_kbps = (max_bytes * 8 / d) / 1000
    v_kbps = max(100, int(total_kbps - audio_kbps - 16))
    tmp = path + ".fit.mp4"
    passlog = path + ".passlog"
    common = [FF, "-y", "-v", "error", "-i", path,
              "-c:v", "libx264", "-tune", "stillimage", "-b:v", f"{v_kbps}k",
              "-pix_fmt", "yuv420p", "-r", "30", "-passlogfile", passlog]
    try:
        subprocess.run(common + ["-pass", "1", "-an", "-f", "null", os.devnull], check=True)
        subprocess.run(common + ["-pass", "2", "-c:a", "aac", "-b:a", f"{audio_kbps}k",
                                 "-movflags", "+faststart", tmp], check=True)
    finally:
        for suf in ("-0.log", "-0.log.mbtree", ".log", ".log.mbtree"):
            try:
                os.remove(passlog + suf)
            except OSError:
                pass
    os.replace(tmp, path)
    return True


def make_combined(clips, out_mp4):
    lst = out_mp4 + ".txt"
    with open(lst, "w", encoding="utf-8") as f:
        for c in clips:
            f.write(f"file '{os.path.abspath(c)}'\n")
    try:
        subprocess.run([FF, "-y", "-v", "error", "-f", "concat", "-safe", "0",
                        "-i", lst, "-c", "copy", "-movflags", "+faststart", out_mp4],
                       check=True)
    finally:
        os.remove(lst)


def main():
    outdir, files, ov_path, cap_path, all_zip = build_carousel(
        SLUG, EYEBROW, SLIDES, CAPTION,
        ov_title=("تبخال دهانی", "در کودکان"), ov_palette="clay")

    narrations = [os.path.join(outdir, f"{SLUG}_narration_{i:02d}.mp3")
                  for i in range(1, len(files) + 1)]
    missing = [p for p in narrations if not os.path.exists(p) or os.path.getsize(p) == 0]
    assert not missing, f"نریشن‌های گمشده: {missing}"

    clips = []
    total = 0.0
    total_bytes = 0
    per_slide_cap = MAX_TARGET_BYTES // len(files)
    for i, (slide, mp3) in enumerate(zip(files, narrations), start=1):
        mp4 = os.path.join(outdir, f"{SLUG}_video_{i:02d}.mp4")
        make_clip(slide, mp3, mp4)
        fitted = ensure_max_size(mp4, max_bytes=per_slide_cap)
        clips.append(mp4)
        d = dur_of(mp4)
        total += d
        total_bytes += os.path.getsize(mp4)
        print(f"clip {i}: {d:.2f}s, {os.path.getsize(mp4) / 1e6:.2f}MB"
              f"{' (فشرده شد)' if fitted else ''}; narration {dur_of(mp3):.2f}s")

    combined = os.path.join(outdir, f"{SLUG}_combined.mp4")
    make_combined(clips, combined)
    fitted_combined = ensure_max_size(combined)
    combined_dur = dur_of(combined)
    print(f"combined: {combined_dur:.2f}s, {os.path.getsize(combined) / 1e6:.2f}MB"
          f"{' (فشرده شد)' if fitted_combined else ''}")

    assert 30 <= total <= 40, f"مجموع زمان خارج از بازه ۳۰ تا ۴۰ ثانیه است: {total:.2f}"
    assert total_bytes <= 4_000_000, f"حجم مجموع ویدیوهای پست بالای ۴MB است: {total_bytes}"
    assert os.path.getsize(combined) <= MAX_TARGET_BYTES, "ویدیوی یک‌تکه بالای سقف اجرایی است"

    full = os.path.join(outdir, f"{SLUG}_full.zip")
    members = files + narrations + clips + [combined, ov_path, cap_path, all_zip]
    with zipfile.ZipFile(full, "w", zipfile.ZIP_DEFLATED) as z:
        for p in members:
            z.write(p, os.path.basename(p))

    print(f"[✓] {SLUG}: {len(files)} اسلاید صدا-تصویری، مجموع {total:.2f} ثانیه، "
          f"حجم پست {total_bytes / 1e6:.2f}MB، ZIP کامل {os.path.getsize(full) / 1e6:.2f}MB")


if __name__ == "__main__":
    main()

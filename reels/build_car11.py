#!/usr/bin/env python3
"""کاروسل صدا-تصویری ۵ اسلایدی با قالب قفل‌شده ریل ۴:۵ + موشن‌گرافی سطح ۱.

عنوان بعدی صف (CSV #7): «هفته‌به‌هفته: نوزاد ۱ تا ۴ هفته چه می‌تواند؟»
موشن سطح ۱: تصویر داخل کارت هر اسلاید حرکت نرم دوربینی (پن آرام + شناور عمودی)
دارد و متن ثابت می‌ماند؛ شروع/پایان هر کلیپ فید ملایم دارد.
خروجی: ۵ PNG + ۵ MP3 جدا + ۵ MP4 متحرک جدا + نسخه یک‌تکه + نمای کلی + کپشن + ZIP کامل.
ساخت: .venv/bin/python reels/build_car11.py
"""
import os
import re
import subprocess
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import imageio_ffmpeg  # noqa: E402
import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402
from reel45_template import PAL, asset, build_carousel, slide_reel45  # noqa: E402

FF = imageio_ffmpeg.get_ffmpeg_exe()
SLUG = "car11_firstmonth"
EYEBROW = "رشد نوزاد"

DIS = ("⚠️ این محتوا آموزشی است و جایگزین ارزیابی پزشک نیست. "
       "اگر نگران فرزندت هستی، با پزشک کودک مشورت کن.")

SLIDES = [
    dict(palette="clay", image=asset("month1_1.png"), cover=True,
         title="ماه اول نوزاد، هفته‌به‌هفته",
         sub="از هفتهٔ ۱ تا ۴ چه می‌تواند؟",
         tip="هر نوزاد ریتم خودش را دارد"),
    dict(palette="warm", image=asset("month1_2.png"),
         title="هفتهٔ ۱: خواب، شیر، بو",
         sub="بیشتر روز خواب است؛ بوی و صدای تو را می‌شناسد",
         tip="دیدش هنوز نزدیک و تار است"),
    dict(palette="night", image=asset("month1_3.png"),
         title="هفتهٔ ۲: خیره به صورت تو",
         sub="صورت‌ها را از نزدیک دنبال می‌کند و سمت صدا برمی‌گردد",
         tip="فاصلهٔ طلایی: ۲۰ تا ۳۰ سانتی‌متر"),
    dict(palette="sage", image=asset("month1_4.png"),
         title="هفتهٔ ۳: بیداریِ بیشتر",
         sub="غان‌وغون شروع می‌شود و دست‌وپایش پرتحرک‌تر است",
         tip="بیدار که بود، کمی بازی روی شکم"),
    dict(palette="mint", image=asset("month1_5.png"),
         title="هفتهٔ ۴: اولین لبخندها",
         sub="سر را لحظه‌ای بالا نگه می‌دارد؛ لبخند واقعی نزدیک است",
         tip="نگران شدی؟ از پزشک کودک بپرس",
         cta="ذخیره کن • برای مامان و بابای تازه بفرست"),
]

CAPTION = """👶 ماه اول نوزاد، هفته‌به‌هفته چه می‌تواند؟

ماه اول از بیرون آرام به نظر می‌رسد، اما مغز و بدن نوزاد هر هفته قدم‌های کوچکی برمی‌دارد. این‌ها «محدودهٔ معمول» است، نه مسابقه؛ هر نوزاد ریتم خودش را دارد و چند روز جلو یا عقب بودن به‌تنهایی نگران‌کننده نیست.

🗓 هفتهٔ ۱: بیشتر روز خواب است و برای شیر بیدار می‌شود. از همین حالا بوی و صدای تو را می‌شناسد، اما دیدش هنوز تار است و فقط فاصلهٔ نزدیک، تقریباً فاصلهٔ صورت تو هنگام بغل‌کردن، را بهتر می‌بیند.

🗓 هفتهٔ ۲: به صورت‌ها خیره می‌شود و کم‌کم نگاهش را روی صورت تو نگه می‌دارد؛ بیشتر نوزادان سر را به سمت صداهای آشنا برمی‌گردانند. بازی این هفته؟ صورت تو در فاصلهٔ ۲۰ تا ۳۰ سانتی‌متری.

🗓 هفتهٔ ۳: بیداری‌ها کمی طولانی‌تر می‌شود، دست‌وپا پرتحرک‌تر است و اولین غان‌وغون‌ها شنیده می‌شود. وقتی بیدار و سرحال است، چند دقیقه بازی روی شکم زیر نظرتو شروع کن؛ خواب همیشه به پشت، روی سطح سفت و خالی.

🗓 هفتهٔ ۴: هنگام روی شکم بودن سر را لحظه‌ای بالا نگه می‌دارد و اولین لبخندهای واقعی معمولاً در همین حوالی از راه می‌رسد.

🚨 با پزشک کودک مشورت کن اگر نوزاد خوب شیر نمی‌خورد، پوشک خیسش کم شده، بی‌حال یا سخت بیدار می‌شود، تب دارد، یا به صداهای بلند هیچ واکنشی نشان نمی‌دهد. تب در نوزاد زیر سه ماه همیشه نیازمند ارزیابی فوری است.

📌 این پست را ذخیره کن و برای یک مامان یا بابای تازه بفرست.

{dis}

#رشد_نوزاد #نوزاد #ماه_اول_نوزاد #مادر_و_نوزاد #والدین_آگاه #سلامت_نوزاد #بازی_با_نوزاد #تربیت_کودک #پزشک_کودک #نوزاد_تازه_متولد
""".format(dis=DIS)


def dur_of(path):
    out = subprocess.run([FF, "-i", path], capture_output=True).stderr.decode("utf-8", "ignore")
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.?\d*)", out)
    if not m:
        return 0.0
    h, mnt, s = m.groups()
    return int(h) * 3600 + int(mnt) * 60 + float(s)


def detect_card(sc, idx, total, base_png, tmpdir):
    """هندسهٔ دقیق کارت تصویر اسلاید را با رندرِ رنگ تخت پیدا می‌کنم:
    برمی‌گرداند (bbox, مسیر ماسک گوشه‌گرد, مسیر کراپ داخل کارت از اسلاید اصلی)."""
    solid_path = os.path.join(tmpdir, "_solid.png")
    if not os.path.exists(solid_path):
        Image.new("RGB", (800, 600), (255, 0, 255)).save(solid_path)
    sc2 = dict(sc, image=solid_path)
    img = slide_reel45(PAL[sc["palette"]], sc2, idx, total, EYEBROW).convert("RGB")
    a = np.asarray(img).astype(int)
    mask = (a[:, :, 0] > 180) & (a[:, :, 1] < 100) & (a[:, :, 2] > 180)
    ys, xs = np.where(mask)
    assert len(xs) > 1000, "کارت تصویر پیدا نشد"
    x0, x1 = int(xs.min()), int(xs.max()) + 1
    y0, y1 = int(ys.min()), int(ys.max()) + 1
    mask_png = os.path.join(tmpdir, f"_motion_mask_{idx:02d}.png")
    Image.fromarray((mask[y0:y1, x0:x1] * 255).astype("uint8")).save(mask_png)
    base = Image.open(base_png).convert("RGB")
    inner_png = os.path.join(tmpdir, f"_motion_inner_{idx:02d}.png")
    base.crop((x0, y0, x1, y1)).save(inner_png)
    return (x0, y0, x1, y1), mask_png, inner_png


def even(n):
    return int(round(n / 2.0)) * 2


def make_motion_clip(base_png, inner_png, mask_png, bbox, mp3, out_mp4, direction):
    """موشن سطح ۱: پن آرام تصویر داخل کارت (جهت متناوب) + شناور عمودی ملایم
    + فید ورود/خروج؛ متن اسلاید ثابت و خوانا می‌ماند."""
    d = dur_of(mp3)
    T = d + 0.5
    x0, y0, x1, y1 = bbox
    BW, BH = x1 - x0, y1 - y0
    sw, sh = even(BW * 1.18), even(BH * 1.18)
    if direction > 0:
        x_expr = f"(in_w-out_w)*(t/{T:.2f})"
    else:
        x_expr = f"(in_w-out_w)*(1-t/{T:.2f})"
    y_expr = f"(in_h-out_h)*(0.5+0.3*sin(6.2832*t/{T:.2f}-1.5708))"
    fc = (
        f"[1:v]scale={sw}:{sh}:flags=lanczos,"
        f"crop=w={BW}:h={BH}:x='{x_expr}':y='{y_expr}',format=rgba[layer_rgb];"
        f"[2:v]format=gray[mask];"
        f"[layer_rgb][mask]alphamerge[layer];"
        f"[0:v]format=rgba[base];"
        f"[base][layer]overlay=x={x0}:y={y0},"
        f"fade=t=in:st=0:d=0.35,fade=t=out:st={T - 0.35:.2f}:d=0.35,"
        f"format=yuv420p[v];"
        f"[3:a]apad[a]"
    )
    cmd = [FF, "-y", "-v", "error",
           "-loop", "1", "-framerate", "30", "-i", base_png,
           "-loop", "1", "-framerate", "30", "-i", inner_png,
           "-loop", "1", "-framerate", "30", "-i", mask_png,
           "-i", mp3,
           "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
           "-c:v", "libx264", "-preset", "medium", "-crf", "20",
           "-r", "30", "-c:a", "aac", "-b:a", "128k",
           "-t", f"{T:.2f}", "-movflags", "+faststart", out_mp4]
    subprocess.run(cmd, check=True)


MAX_TARGET_BYTES = 3_800_000


def ensure_max_size(path, max_bytes=MAX_TARGET_BYTES, audio_kbps=80):
    if os.path.getsize(path) <= max_bytes:
        return False
    d = dur_of(path)
    total_kbps = (max_bytes * 8 / d) / 1000
    v_kbps = max(100, int(total_kbps - audio_kbps - 16))
    tmp = path + ".fit.mp4"
    passlog = path + ".passlog"
    common = [FF, "-y", "-v", "error", "-i", path,
              "-c:v", "libx264", "-b:v", f"{v_kbps}k",
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
        ov_title=("ماه اول نوزاد", "هفته‌به‌هفته"), ov_palette="clay")

    narrations = [os.path.join(outdir, f"{SLUG}_narration_{i:02d}.mp3")
                  for i in range(1, len(files) + 1)]
    missing = [p for p in narrations if not os.path.exists(p) or os.path.getsize(p) == 0]
    assert not missing, f"نریشن‌های گمشده: {missing}"

    clips = []
    total = 0.0
    total_bytes = 0
    per_slide_cap = MAX_TARGET_BYTES // len(files)
    directions = [1, -1, 1, -1, 1]
    tmp_files = []
    for i, (sc, slide, mp3) in enumerate(zip(SLIDES, files, narrations), start=1):
        bbox, mask_png, inner_png = detect_card(sc, i, len(files), slide, outdir)
        tmp_files += [mask_png, inner_png]
        mp4 = os.path.join(outdir, f"{SLUG}_video_{i:02d}.mp4")
        make_motion_clip(slide, inner_png, mask_png, bbox, mp3, mp4,
                         directions[(i - 1) % len(directions)])
        fitted = ensure_max_size(mp4, max_bytes=per_slide_cap)
        clips.append(mp4)
        d = dur_of(mp4)
        total += d
        total_bytes += os.path.getsize(mp4)
        print(f"clip {i}: {d:.2f}s, {os.path.getsize(mp4) / 1e6:.2f}MB"
              f"{' (فشرده شد)' if fitted else ''}; narration {dur_of(mp3):.2f}s; card={bbox}")

    combined = os.path.join(outdir, f"{SLUG}_combined.mp4")
    make_combined(clips, combined)
    fitted_combined = ensure_max_size(combined)
    print(f"combined: {dur_of(combined):.2f}s, {os.path.getsize(combined) / 1e6:.2f}MB"
          f"{' (فشرده شد)' if fitted_combined else ''}")

    assert 30 <= total <= 40, f"مجموع زمان خارج از بازه ۳۰ تا ۴۰ ثانیه است: {total:.2f}"
    assert total_bytes <= 4_000_000, f"حجم مجموع ویدیوهای پست بالای ۴MB است: {total_bytes}"
    assert os.path.getsize(combined) <= MAX_TARGET_BYTES, "ویدیوی یک‌تکه بالای سقف اجرایی است"

    full = os.path.join(outdir, f"{SLUG}_full.zip")
    members = files + narrations + clips + [combined, ov_path, cap_path, all_zip]
    with zipfile.ZipFile(full, "w", zipfile.ZIP_DEFLATED) as z:
        for p in members:
            z.write(p, os.path.basename(p))

    for p in tmp_files + [os.path.join(outdir, "_solid.png")]:
        try:
            os.remove(p)
        except OSError:
            pass

    print(f"[✓] {SLUG}: {len(files)} اسلاید صدا-تصویری متحرک (موشن سطح ۱)، مجموع {total:.2f} ثانیه، "
          f"حجم پست {total_bytes / 1e6:.2f}MB، ZIP کامل {os.path.getsize(full) / 1e6:.2f}MB")


if __name__ == "__main__":
    main()

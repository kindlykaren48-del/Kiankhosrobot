#!/usr/bin/env python3
"""کاروسل صدا-تصویری ۵ اسلایدی متحرک (موشن سطح ۱) با قالب قفل‌شده ریل ۴:۵ و تصاویر سبک داوینچی.

عنوان بعدی صف (CSV #13): «این نشانه‌ها را در نوزاد جدی بگیر» — هوک: «اگر این را دیدی، صبر نکن».
موشن سطح ۱ مثل car11 و car13: حرکت نرم تصویر داخل کارت + فید؛ متن ثابت.
خروجی: ۵ PNG + ۵ MP3 جدا + ۵ MP4 متحرک جدا + نسخه یک‌تکه + نمای کلی + کپشن + ZIP کامل.
ساخت: .venv/bin/python reels/build_car17.py
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
SLUG = "car17_redflags"
EYEBROW = "علائم هشدار"

DIS = ("⚠️ این محتوا آموزشی است و جایگزین ارزیابی پزشک نیست. "
       "اگر نگران فرزندت هستی، با پزشک کودک مشورت کن.")

SLIDES = [
    dict(palette="clay", image=asset("redflags_1.png"), cover=True,
         title="این نشانه‌ها را جدی بگیر",
         sub="اگر این‌ها را دیدی، صبر نکن",
         tip="مراجعه زودتر، خیال راحت‌تر"),
    dict(palette="warm", image=asset("redflags_2.png"),
         title="تب در زیر ۳ ماه",
         sub="حتی یک تب ساده هم باید بررسی شود",
         tip="همان روز با پزشک تماس بگیر"),
    dict(palette="night", image=asset("redflags_3.png"),
         title="مشکل در نفس کشیدن",
         sub="تندنفس، دنده‌های فرورونده، لب کبود",
         tip="کمک فوری بگیر"),
    dict(palette="sage", image=asset("redflags_4.png"),
         title="شیر نخوردن و بی‌حالی",
         sub="سخت بیدار می‌شود و پوشکش کم خیس است",
         tip="این ترکیب را دست‌کم نگیر"),
    dict(palette="mint", image=asset("redflags_5.png"),
         title="به حس خودت اعتماد کن",
         sub="تو نوزادت را بهتر از همه می‌شناسی",
         tip="بی‌پاسخ یا تشنج؟ اورژانس",
         cta="ذخیره کن • برای هر پدر و مادر تازه بفرست"),
]

CAPTION = """🚨 این نشانه‌ها را در نوزاد جدی بگیر

بیشتر نگرانی‌های روزهای اول طبیعی‌اند؛ اما بعضی نشانه‌ها یعنی «صبر نکن». این فهرست را ذخیره کن تا وقت لازم دنبالش نگردی.

🌡️ ۱) تب در زیر ۳ ماه
اگر نوزاد زیر ۳ ماه دمای بدنش به ۳۸ درجه یا بالاتر رسید، همان روز با پزشک یا اورژانس تماس بگیر؛ حتی اگر ظاهرش خوب به نظر برسد و شیر بخورد. در این سن، تب همیشه نیاز به بررسی دارد.

🫁 ۲) مشکل در نفس کشیدن
تنفس خیلی تند یا سخت، فرورفتن پوست بین دنده‌ها یا زیر گردن هنگام نفس کشیدن، ناله کردن با هر بازدم، پره‌های بینیِ بازشونده یا رنگ کبود و خاکستری لب و صورت یعنی کمک فوری.

🍼 ۳) شیر نخوردن و بی‌حالی
اگر برای شیر خوردن بیدار نمی‌شود، خیلی کمتر از معمول می‌خورد، دهانش خشک است یا تعداد پوشک خیسشبه‌وضوح کم شده، منتظر نمان؛ کم‌آبی در نوزاد سریع جدی می‌شود.

😴 ۴) سخت بیدار شدن یا بی‌پاسخی
نوزادی که به سختی بیدار می‌شود، شل و بی‌حال است، گریه‌اش ضعیف یا غیرعادی شده یا به تو واکنش نشان نمی‌دهد باید فوری دیده شود. تشنج هم یعنی اورژانس.

❤️ و یک قانون ساده
تو نوزادت را بهتر از هر کس دیگری می‌شناسی. اگر حس می‌کنی «چیزی درست نیست»، به حست اعتماد کن و مراجعه کن. هیچ پزشکی از یک مراجعهٔ بی‌مورد ناراحت نمی‌شود؛ دیر رسیدن است که خطر دارد.

📌 ذخیره کن و برای هر پدر و مادر تازه بفرست.

{dis}

#علائم_هشدار_نوزاد #تب_نوزاد #سلامت_نوزاد #نوزاد #پزشک_کودک #مراقبت_نوزاد #مادر_و_نوزاد #والدین_آگاه
""".format(dis=DIS)


def dur_of(path):
    out = subprocess.run([FF, "-i", path], capture_output=True).stderr.decode("utf-8", "ignore")
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.?\d*)", out)
    if not m:
        return 0.0
    h, mnt, s = m.groups()
    return int(h) * 3600 + int(mnt) * 60 + float(s)


def detect_card(sc, idx, total, base_png, tmpdir):
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


def make_combined(clips, out_mp4, transition_dur=0.7):
    # نسخهٔ یک‌تکه با ترنزیشن نرم بین اسلایدها؛ نه شروع سیاه و نه قطع ناگهانی.
    # به‌صورت مرحله‌ای ساخته می‌شود تا هر مرحله خروجیِ CFRِ تمیز برای مرحلهٔ بعد داشته باشد.
    cur = clips[0]
    temps = []
    try:
        for i in range(1, len(clips)):
            nxt = clips[i]
            offset = max(0.0, dur_of(cur) - transition_dur)
            step = out_mp4 + f".step{i}.mp4"
            temps.append(step)
            fc = (
                "[0:v]settb=AVTB,fps=30,format=yuv420p,setsar=1[v0];"
                "[1:v]settb=AVTB,fps=30,format=yuv420p,setsar=1[v1];"
                f"[v0][v1]xfade=transition=smoothleft:duration={transition_dur:.2f}:offset={offset:.3f},format=yuv420p[v];"
                "[0:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo[a0];"
                "[1:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo[a1];"
                f"[a0][a1]acrossfade=d={transition_dur:.2f}:c1=tri:c2=tri[a]"
            )
            cmd = [FF, "-y", "-v", "error", "-i", cur, "-i", nxt,
                   "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
                   "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                   "-pix_fmt", "yuv420p", "-r", "30",
                   "-c:a", "aac", "-b:a", "128k",
                   "-movflags", "+faststart", step]
            subprocess.run(cmd, check=True)
            cur = step
        os.replace(cur, out_mp4)
    finally:
        for t in temps:
            if t != out_mp4 and os.path.exists(t):
                try:
                    os.remove(t)
                except OSError:
                    pass


def main():
    outdir, files, ov_path, cap_path, all_zip = build_carousel(
        SLUG, EYEBROW, SLIDES, CAPTION,
        ov_title=("این نشانه‌ها را", "در نوزاد جدی بگیر"), ov_palette="clay")

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
    fitted_combined = ensure_max_size(combined, max_bytes=3_600_000)
    print(f"combined: {dur_of(combined):.2f}s, {os.path.getsize(combined) / 1e6:.2f}MB"
          f"{' (فشرده شد)' if fitted_combined else ''}")

    combined_dur = dur_of(combined)
    assert 30 <= combined_dur <= 40, f"مجموع زمان نسخهٔ کامل خارج از بازه ۳۰ تا ۴۰ ثانیه است: {combined_dur:.2f}"
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

    print(f"[✓] {SLUG}: {len(files)} اسلاید صدا-تصویری متحرک (موشن سطح ۱، سبک داوینچی)، نسخهٔ کامل {combined_dur:.2f} ثانیه، "
          f"حجم پست {total_bytes / 1e6:.2f}MB، ZIP کامل {os.path.getsize(full) / 1e6:.2f}MB")


if __name__ == "__main__":
    main()

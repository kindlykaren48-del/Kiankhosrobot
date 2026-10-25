#!/usr/bin/env python3
"""کاروسل تصویری ۵ اسلایدی بدون صدا، طبق سفارش استودیو در Issue #7.

عنوان بعدی بانک: «نوزادت به اسمش برنمی‌گردد؟ این تمرین را شروع کن»
تنظیمات سفارش: پالت warm، سبک تصویر تخت مینیمال، ۱۰۸۰×۱۳۵۰، سقف مجموع پست ۲MB.
خروجی: reels/carousel/car09_namecall/
ساخت: .venv/bin/python reels/build_car09.py
"""
import os
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image  # noqa: E402
from reel45_template import asset, build_carousel  # noqa: E402

SLUG = "car09_namecall"
EYEBROW = "رشد نوزاد ۶ تا ۱۲ ماه"
MAX_POST_BYTES = 2_000_000
TARGET_POST_BYTES = 1_950_000

DIS = ("⚠️ این محتوا آموزشی است و جایگزین ارزیابی پزشک نیست. "
       "اگر نگران فرزندت هستی، با پزشک کودک مشورت کن.")

SLIDES = [
    dict(palette="warm", image=asset("namecall_1.png"), cover=True,
         title="نوزادت به اسمش برنمی‌گردد؟ این تمرین را شروع کن",
         sub="اول شرایط شنیدن را درست کن، بعد تمرین را شروع کن",
         tip="اسمش را به یک لحظهٔ شیرین وصل کن"),
    dict(palette="warm", image=asset("namecall_2.png"),
         title="مزاحم‌ها را کم کن",
         sub="تلویزیون و صدای اطراف خاموش؛ وقتی غرق بازی نیست صدا بزن",
         tip="در محیط ساکت، فرصت پاسخ بیشتر است"),
    dict(palette="warm", image=asset("namecall_3.png"),
         title="یک بار صدا بزن و مکث کن",
         sub="با صدای گرم و آهنگین اسمش را بگو و چند ثانیه منتظر بمان",
         tip="پشت سر هم تکرار نکن؛ فرصت برگشتن بده"),
    dict(palette="warm", image=asset("namecall_4.png"),
         title="برگشت؟ فوری جشن بگیر",
         sub="لبخند، دست زدن یا اسباب‌بازی محبوب را به نگاهش وصل کن",
         tip="اسمش یعنی یک اتفاق خوب در راه است"),
    dict(palette="warm", image=asset("namecall_5.png"),
         title="اگر ادامه داشت، بررسی کن",
         sub="اگر بیشتر وقت‌ها برنمی‌گردد، شنوایی و رشد را بررسی کن",
         tip="به صداها هم واکنش ندارد؟ صبر نکن",
         cta="ذخیره کن • برای مامان و بابای تازه بفرست"),
]

CAPTION = """👶 نوزادت به اسمش برنمی‌گردد؟ این تمرین را شروع کن

بعضی نوزادها وقتی غرق بازی‌اند، خسته‌اند یا اطرافشان شلوغ است به اسمشان برنمی‌گردند. قبل از نگرانی، این بازی کوتاه را درست اجرا کن:

✅ تمرین اسم
• تلویزیون و صداهای اضافه را کم کن و وقتی نوزاد آرام است و کاملاً غرق یک اسباب‌بازی نیست، نزدیکش بنشین.
• فقط با یک اسم مشخص و با صدای گرم و آهنگین صدا بزن؛ یک بار بگو و ۳ تا ۵ ثانیه مکث کن تا فرصت برگشتن داشته باشد.
• اگر نگاه کرد، فوری لبخند بزن، دست بزن، اسمش را با شادی تکرار کن یا اسباب‌بازی محبوبش را نشان بده.
• تمرین را در چند نوبت خیلی کوتاه و بازی‌وار در روز تکرار کن و وقتی خسته یا بی‌حوصله شد تمامش کن. از فریاد زدن یا پشت سر هم صدا کردن پرهیز کن.

بسیاری از نوزادها حوالی ۹ ماهگی وقتی اسمشان را صدا می‌زنیم نگاه می‌کنند، اما زمان‌بندی رشد برای هر کودک یکسان نیست و یک بار برنگشتن به‌تنهایی نشانهٔ مشکل نیست.

🚨 با پزشک کودک دربارهٔ بررسی شنوایی و رشد صحبت کن اگر کودک حدود ۹ ماهه بیشتر وقت‌ها به اسمش برنمی‌گردد، به صداهای معمولی یا بلند واکنش کمی دارد، غان‌وغون و ارتباط چشمی‌اش خیلی کم است، مهارتی را از دست داده یا عفونت‌های مکرر گوش دارد. این تمرین جای تست شنوایی یا ارزیابی رشد را نمی‌گیرد.

📌 این پست را ذخیره کن و برای یک مامان یا بابای تازه بفرست.

{dis}

#رشد_نوزاد #نوزاد #شنوایی_نوزاد #گفتار_کودک #مادر_و_نوزاد #سلامت_کودک #والدین_آگاه #نه_ماهگی #بازی_با_نوزاد #تربیت_کودک
""".format(dis=DIS)


def post_total(files):
    return sum(os.path.getsize(p) for p in files)


def optimize_slides(files):
    """مجموع PNGهای پست را بدون تغییر ابعاد به سقف سفارش می‌رساند."""
    if post_total(files) > TARGET_POST_BYTES:
        for p in files:
            with Image.open(p) as im:
                im.convert("RGB").save(p, optimize=True, compress_level=9)

    for colors in (256, 192, 128):
        if post_total(files) <= TARGET_POST_BYTES:
            break
        for p in files:
            with Image.open(p) as im:
                q = im.convert("RGB").quantize(
                    colors=colors,
                    method=Image.Quantize.FASTOCTREE,
                    dither=Image.Dither.NONE,
                )
                q.save(p, optimize=True, compress_level=9)

    total = post_total(files)
    for p in files:
        print(f"{os.path.basename(p)}: {os.path.getsize(p) / 1e6:.2f}MB")
    ok = "✓ زیر سقف ۲ مگابایت" if total <= MAX_POST_BYTES else "✗ بالای ۲ مگابایت!"
    print(f"POST TOTAL (مجموع اسلایدهای پست): {total / 1e6:.2f}MB — {ok}")
    assert total <= MAX_POST_BYTES, "مجموع اسلایدها از سقف ۲ مگابایت رد شد"
    return total


def make_zip(path, members):
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for p in members:
            z.write(p, os.path.basename(p))


def main():
    outdir, files, ov_path, cap_path, all_zip = build_carousel(
        SLUG, EYEBROW, SLIDES, CAPTION,
        ov_title=("به اسمش", "برنمی‌گردد؟"), ov_palette="warm")

    optimize_slides(files)
    make_zip(all_zip, files + [cap_path])

    full = os.path.join(outdir, f"{SLUG}_full.zip")
    make_zip(full, files + [ov_path, cap_path])
    print(f"[✓] {SLUG}: {len(files)} اسلاید تصویری بدون صدا + نمای کلی + کپشن "
          f"+ ZIP کامل {os.path.getsize(full) / 1e6:.2f}MB → {outdir}")


if __name__ == "__main__":
    main()

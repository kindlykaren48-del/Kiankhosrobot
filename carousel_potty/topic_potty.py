# -*- coding: utf-8 -*-
"""کاروسل سایبرپانک — زمان پوشک گرفتن از کودک (کاور + ۴ اسلاید + CTA، نسبت ۴:۵)"""
import sys, os
sys.path.insert(0, "/home/user/Kiankhosrobot/Kiankhosrobot/toolkit")
from make_carousel_cyber import build_carousel_cyber

cfg = {
    "src": "/home/user/Kiankhosrobot/carousel_potty/src",
    "nameplate": "دکتر کیانوش سالاریان",
    "nameplate_en": "DR. KIANOOSH SALARIAN",
    "cover": dict(
        headline=[("زمان پوشک گرفتن", "w"), ("از کودک", "a")],
        en="POTTY TRAINING TIMING",
        subtitle="آمادگی مهم‌تر از سن است",
        img="ill0.png",
        tags=["نشانه‌های آمادگی را ببین",
              "معمولاً ۱۸ تا ۳۰ ماهگی",
              "روز جلوتر از شب",
              "بدون تنبیه و فشار"],
    ),
    "slides": [
        dict(code="// SIGN_01", kicker="نشانه‌ها", en="READINESS SIGNS",
             headline=[("نشانه‌های آمادگی", "w"), ("را ببین", "a")],
             img="ill1.png",
             tips=[("clock", "پوشک دو ساعت یا بیشتر خشک می‌ماند"),
                   ("eye", "به توالت و نشستن علاقه نشان می‌دهد"),
                   ("speak", "با کلمه یا اشاره خبر می‌دهد")],
             note=("safe", "آمادگی جسمی و ذهنی مهم‌تر از سن تقویمی است")),

        dict(code="// WINDOW_02", kicker="سن مناسب", en="BEST WINDOW",
             headline=[("معمولاً بین", "w"), ("۱۸ تا ۳۰ ماهگی", "a")],
             img="ill2.png",
             tips=[("calendar", "پیش از ۱۸ ماه معمولاً زود است"),
                   ("hourglass", "پس از ۳۰ ماه با پزشک مشورت کن"),
                   ("star", "توالی مهم است، نه سرعت")],
             note=("doctor", "بعضی کودکان تا ۳ سال هم طبیعی‌اند")),

        dict(code="// DAY_NIGHT_03", kicker="روش درست", en="DAY BEFORE NIGHT",
             headline=[("اول روز،", "w"), ("بعد شب", "a")],
             img="ill3.png",
             tips=[("moon", "کنترل شبانه دیرتر به دست می‌آید"),
                   ("clock", "هر ۱ تا ۲ ساعت نشستن کوتاه یادآوری کن"),
                   ("heart", "تشویق آرام، بدون تنبیه و دعوا")],
             note=("drop", "زمین‌خوردن شبانه تا سال‌ها طبیعی است")),

        dict(code="// WAIT_04", kicker="هشدار", en="WHEN TO WAIT",
             headline=[("گاهی وقتش", "w"), ("هنوز نیست", "a")],
             img="ill4.png",
             tips=[("warn", "مقاومت شدید یا گریهٔ مداوم"),
                   ("babyhead", "تولد نوزاد جدید یا اسباب‌کشی"),
                   ("fever", "بیماری یا تغییر برنامهٔ خواب")],
             note=("safe", "دو هفته صبر و شروع دوباره بهتر از فشار است")),
    ],
    "cta": dict(
        text="این کاروسل را برای پدر و مادرهایی که تازه پوشک‌گیری را شروع کرده‌اند بفرست",
        buttons=["ذخیره‌اش کن", "پیجم را دنبال کن"],
        img="ill5.png",
        follow_en="FOLLOW FOR MORE",
    ),
}

if __name__ == "__main__":
    out = build_carousel_cyber(cfg, outdir="/home/user/Kiankhosrobot/carousel_potty")
    print("files:", len(out))

# -*- coding: utf-8 -*-
"""کاروسل نئون مولتی‌کالر — آلرژی غذایی کودک / معرفی تدریجی غذا (۶ اسلاید ۴:۵)"""
import sys, os
sys.path.insert(0, "/home/user/Kiankhosrobot/Kiankhosrobot/toolkit")
from make_carousel import W, H, NEXT_PAL, build_carousel

cfg = {
    "src": "/home/user/Kiankhosrobot/carousel_allergy/src",
    "nameplate": "دکتر کیانوش سالاریان",
    "glyph": "stetho",
    "slides": [
        dict(kicker="پایه", en="WHY IT MATTERS",
             headline=[("واکنش آلرژیک غذایی", "w"), ("موقع معرفی دیده می‌شود", "a")],
             img="ill0.png",
             tips=[("clock", "اولین واکنش معمولاً در شروع غذای کمکی"),
                   ("shield", "نه در بدو تولد؛ ایمنی تازه شکل می‌گیرد"),
                   ("eye", "پس غربالگری زودهنگام سود واقعی دارد")],
             note=("safe", "شیر مادر تا شش ماه؛ غذای جامد از شش ماه با نظر پزشک")),

        dict(kicker="مهم‌ترین نکته", en="TIMING",
             headline=[("چرا تأخیر", "w"), ("کمکی نیست؟", "a")],
             img="ill1.png",
             tips=[("clock", "وقت طلایی شروع، بین ۴ تا ۶ ماهگی است"),
                   ("hourglass", "تأخیر طولانی احتمال آلرژی را کم نمی‌کند"),
                   ("doctor", "زمان دقیقش را با پزشک کودک هماهنگ کن")],
             note=("clockwait", "زود یا دیر، هر دو ریسک‌اند؛ تعادل مهم است")),

        dict(kicker="روش درست", en="ONE AT A TIME",
             headline=[("هر بار", "w"), ("یک غذای جدید", "a")],
             img="ill2.png",
             tips=[("dropper", "مقدار کم شروع کن و تدریجی بالا ببر"),
                   ("clockwait", "بین دو غذای جدید ۳ تا ۵ روز فاصله بگذار"),
                   ("repeat", "اگر تحمل کرد، در برنامهٔ هفتگی تکرارش کن")],
             note=("plate", "همراه با شیر یا شیر مادر، در روزی که کودک سالم است")),

        dict(kicker="علائم", en="SPOT THE SIGNS",
             headline=[("این نشانه‌ها را", "w"), ("یادت باشد", "a")],
             img="ill3.png",
             tips=[("eye", "دو ساعت اول را زیر نظر داشته باش"),
                   ("skin", "کهیر، تورم لب یا دور چشم"),
                   ("lung", "تنگی نفس یا سرفهٔ پایدار")],
             note=("warn", "هر نشانهٔ شدید = تماس فوری با اورژانس")),

        dict(kicker="اشتباه رایج", en="FOODS ARE NOT ENEMIES",
             headline=[("ممنوعیت زودهنگام", "w"), ("راه‌حل نیست", "a")],
             img="ill4.png",
             tips=[("no", "حذف بی‌دلیل، ریسک حساسیت را کم نمی‌کند"),
                   ("dna", "اگزما یا سابقهٔ خانوادگی = ریسک بالاتر"),
                   ("warn", "حذف غذا فقط با دستور پزشک")],
             note=("doctor", "هر رژیم حذفی باید زیر نظر متخصص باشد")),

        dict(kicker="جمع‌بندی", en="CALM & CONFIDENT",
             headline=[("با آرامش", "w"), ("معرفی کن", "a")],
             img="ill5.png",
             tips=[("calendar", "برنامهٔ معرفی را قدم‌به‌قدم پیش ببر"),
                   ("sound", "واکنش شدید نادر است، ولی آماده باش"),
                   ("speak", "سؤالت را از متخصص بپرس، نه از شبکه‌ها")],
             note=("heart", "هر کودک مسیر خودش را دارد؛ با آرامش پیش برو")),
    ],
}

if __name__ == "__main__":
    out = build_carousel(cfg, outdir="/home/user/Kiankhosrobot/carousel_allergy")
    print("slides:", len(out))

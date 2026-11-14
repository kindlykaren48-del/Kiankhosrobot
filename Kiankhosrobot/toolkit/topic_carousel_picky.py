# کاروسل ۷ اسلایدی — عنوان ۳۲: «کودک بدغذا؟ یا فقط سلیقه‌اش تغییر کرده؟»
# اجرا:  python3 topic_carousel_picky.py
import make_carousel
from make_carousel import build_all

CFG = {
    "slug": "picky_eater",
    "eyebrow": "تغذیهٔ کودک",
    "title_lines": ["کودک بدغذا؟", "یا فقط", "سلیقه‌اش عوض شده؟"],
    "subtitle": "۷ نکته برای والدین نگران",
    "brand_en": "DR. KIANOOSH SALARIAN",
    "ill_cover": "/home/user/Kiankhosrobot/assets/carousel32/ill_cover.png",
    "tags": ["نشانه‌های هشدار", "کودکان زیر ۵ سال", "بدون برچسب"],

    "slides": [
        {"num": 1,
         "title_fa": "چیست؟",
         "title_en": "WHAT IS IT",
         "ill": "/home/user/Kiankhosrobot/assets/carousel32/ill_1_what.png",
         "bullets": [
             ("face", "بی‌اشتهایی گذرا و انتخاب‌گرانه"),
             ("chart", "شایع در کودکان زیر شش سال"),
             ("shield", "معمولاً نشانهٔ بیماری نیست"),
             ("moon", "با استقلال‌خواهی کودک گره خورده"),
         ]},

        {"num": 2,
         "title_fa": "چه چیزی طبیعی است؟",
         "title_en": "WHAT IS NORMAL",
         "ill": "/home/user/Kiankhosrobot/assets/carousel32/ill_2_normal.png",
         "bullets": [
             ("chart", "مقدار خوردن از روزی به روز دیگر"),
             ("hourglass", "خوردن یک وعدهٔ خوب در هفته"),
             ("drop", "علاقه به یک غذا و بی‌علاقگی به آن"),
             ("star", "رشد و وزن در محدودهٔ طبیعی"),
         ]},

        {"num": 3,
         "title_fa": "اشتباه‌های رایج",
         "title_en": "COMMON MISTAKES",
         "ill": "/home/user/Kiankhosrobot/assets/carousel32/ill_3_mistakes.png",
         "bullets": [
             ("no", "غذا را با قاشق به دهان کودک نکنید"),
             ("no", "راه ندادن بهانه: شیر، بیسکویت و آبمیوه"),
             ("speak", "جنگ سر غذا فقط بدغذایی را بیشتر می‌کند"),
             ("safe", "دادن غذای متفاوت فقط برای بزرگ‌ترها"),
         ]},

        {"num": 4,
         "title_fa": "سه قانون میز",
         "title_en": "THREE TABLE RULES",
         "ill": "/home/user/Kiankhosrobot/assets/carousel32/ill_4_rules.png",
         "bullets": [
             ("calendar", "یک ساعت ثابت برای وعده‌ها"),
             ("hourglass", "حداکثر ۲۰ تا ۳۰ دقیقه زمان غذا"),
             ("plate", "یک بشقاب برای همه، بدون غذاهای جایگزین"),
             ("no", "بدون تلویزیون و تبلت سر سفره"),
         ]},

        {"num": 5,
         "title_fa": "چه‌وقت نگران شویم؟",
         "title_en": "WHEN TO WORRY",
         "ill": "/home/user/Kiankhosrobot/assets/carousel32/ill_5_severity.png",
         "bullets": [
             ("chart", "افت یا توقف وزن در نمودار رشد"),
             ("drop", "کاهش نوشیدن، بی‌حالی و خواب‌آلودگی"),
             ("fever", "تب، استفراغ یا اسهال همراه با بی‌اشتهایی"),
             ("warn", "درد هنگام بلع یا زخم دهان"),
         ]},
    ],

    "cta_big": "ذخیره کن",
    "cta": "این کاروسل را برای والدین دیگر بفرست",
    "caption": """کودک بدغذا؟ یا فقط سلیقه‌اش عوض شده؟

اکثر کودکان بین دو تا شش سال دوره‌ای از انتخاب‌گرایی غذایی را تجربه می‌کنند؛ این مرحله معمولاً نشانهٔ بیماری نیست و با بزرگ‌تر شدن و با قواعد روشن سر میز بهتر می‌شود. آنچه اهمیت دارد رشد کودک است، نه مقدار غذای یک وعده.

نکته‌های کلیدی این کاروسل:
۱) اشتهای کودک از روزی به روز دیگر تغییر می‌کند؛ به یک وعده نگاه نکنید.
۲) یک ساعت ثابت، حداکثر ۲۰ تا ۳۰ دقیقه و یک بشقاب مشترک برای همه.
۳) بهانه‌های غذایی مثل شیر و بیسکویت را در دسترس و بی‌حساب نگذارید.
۴) کودک را به خوردن مجبور نکنید؛ غذا را با هیجان و کاوش معرفی کنید.
۵) اگر وزن روی نمودار رشد افت کرد یا نشانه‌های کم‌آبی دیدید، به پزشک مراجعه کنید.

این محتوا آموزشی است و جایگزین ارزیابی و مشاورهٔ پزشک نیست.

دکتر کیانوش سالاریان

منابع برای مطالعه:
https://www.healthychildren.org/English/ages-stages/toddler/nutrition/Pages/Picky-Eaters.aspx
https://www.cdc.gov/nutrition/infantandtoddlernutrition/

#کودک_بدغذا #تغذیه_کودک #بدغذایی #رشد_کودک #پزشکی_کودکان #والدین_آگاه #دکتر_کیانوش_سالاریان""",
}

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        make_carousel.OUTDIR = sys.argv[1]
    print(build_all(CFG))

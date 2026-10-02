# کاروسل: «کف پای صاف در کودکان» — پالت مولتی‌کالر aurora
from make_carousel import build_carousel

cfg = {
    "slug": "kids_flatfeet",
    "palette": "aurora",
    "title_fa": "کف پای صاف در کودکان",
    "title_en": "FLAT FEET IN CHILDREN",
    "subtitle": "چه وقت طبیعی است؟",
    "cta": "برای پدر و مادرها بفرست",
    "cover_ill": "ill0.png",
    "slides": [
        ("۱", "اغلب بخشی از رشد است", "COMMON IN CHILDHOOD", "ill1.png",
         [("babyhead", "تا حدود ۵ سالگی، قوس پا کم‌رنگ است"),
          ("leg", "چربی کف پا و نرمی رباط‌ها علت شایع‌اند"),
          ("calendar", "قوس پا با رشد کودک کم‌کم شکل می‌گیرد"),
          ("shield", "اگر درد ندارد، معمولاً جای نگرانی نیست")]),

        ("۲", "در خانه نگاه کن", "SIMPLE HOME CHECK", "ill2.png",
         [("eye", "کودک را ایستاده و روی پنجه ببین"),
          ("leg", "قوس ظاهر شد؟ احتمالاً انعطاف‌پذیر است"),
          ("repeat", "دو پا را با هم مقایسه کن"),
          ("doctor", "بررسی خانگی جای معاینه را نمی‌گیرد")]),

        ("۳", "زنگ خطرها", "RED FLAGS", "ill3.png",
         [("warn", "درد یا خستگی مداوم پا"),
          ("no", "سفتی پا یا ظاهر نشدن قوس روی پنجه"),
          ("leg", "درگیری یک‌طرفه یا بدترشونده"),
          ("run", "لنگیدن یا محدود شدن بازی کودک")]),

        ("۴", "چه کار کنیم؟", "WHAT TO DO", "ill4.png",
         [("calendar", "بدون درد: معمولاً فقط پیگیری رشد"),
          ("safe", "کفش راحت و اندازهٔ مناسب"),
          ("leg", "کفی درد را کم می‌کند؛ قوس نمی‌سازد"),
          ("doctor", "با زنگ خطرها: معاینهٔ ارتوپد اطفال")]),
    ],
}

if __name__ == "__main__":
    import sys
    outdir = sys.argv[1] if len(sys.argv) > 1 else "."
    for f in build_carousel(cfg, outdir):
        print("OK", f)

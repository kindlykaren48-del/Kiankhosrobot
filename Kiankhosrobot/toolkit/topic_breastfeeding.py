# ریل: «وضعیت‌های مختلف شیردهی» — پالت purplemustard + سبک نئون موزاییکی
import make_reel
from make_reel import build_all

cfg = {
    "slug": "breastfeeding",
    "palette": "purplemustard",
    "style": "neon",
    "neon_mosaic": True,           # بافت کاشی‌کاری مارپیچ
    "neon_base": (26, 12, 46),     # بنفش تیره برای هم‌خوانی با موزاییک
    "neon_arc": (198, 156, 40, 42),  # قوس‌های مارپیچ خردلی
    "title_fa": "وضعیت‌های شیردهی",
    "title_en": "BREASTFEEDING POSITIONS",
    "subtitle": "شیر بیشتر، درد کمتر",
    "cover_tags": ["گهواره‌ای", "فوتبالی", "خوابیده به پهلو", "بیولوژیک"],
    "cta": "این ویدیو را برای مادران شیرده بفرست",
    "cover_ill": "ill0.png",
    "slides": [
        ("۱", "اصول مشترک", "KEY POINTS", "ill1.png",
         [("speak", "بدن مادر تکیه‌داده و بدون تنش"),
          ("star", "گوش، شانه و لگن نوزاد در یک خط"),
          ("hourglass", "شکم نوزاد چسبیده به شکم مادر"),
          ("safe", "بالش زیر آرنج و زانو برای حمایت")]),

        ("۲", "چهار وضعیت", "FOUR POSITIONS", "ill2.png",
         [("babyhead", "گهواره‌ای؛ رایج‌ترین حالت روزانه"),
          ("chest", "فوتبالی؛ مناسب زایمان سزارین"),
          ("moon", "خوابیده به پهلو؛ برای شب‌ها"),
          ("safe", "بیولوژیک؛ نوزاد روی بدن مادر")]),

        ("۳", "گرفتن درست", "GOOD LATCH", "ill3.png",
         [("speak", "لب‌های نوزاد باز و به بیرون"),
          ("star", "چانه چسبیده و بینی آزاد"),
          ("ear", "صدای بلع منظم شنیده می‌شود"),
          ("no", "درد شدید و مداوم نشانهٔ هشدار")]),

        ("۴", "نکات عملی", "PRACTICAL TIPS", "ill4.png",
         [("repeat", "در هر نوبت وضعیت را عوض کنید"),
          ("calendar", "شیردهی بر اساس تقاضای نوزاد"),
          ("drop", "تخلیهٔ یک پستان، بعد تعویض"),
          ("moon", "شب‌ها خوابیدن به پهلو راحت‌تر است")]),
    ],
}

if __name__ == "__main__":
    make_reel.OUTDIR = "/home/user/Kiankhosrobot/Kiankhosrobot"
    print(build_all(cfg, target=25.0))

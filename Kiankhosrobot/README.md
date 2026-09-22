# کارخانه ریلز آموزشی پزشکی

مخزن کدها و قوانین تولید ریلز. راهنمای فعلی دو قالب در [START-PROMPT.md](../START-PROMPT.md) است:

- **نوع قدیم / انیمیشنی:** موتور موجود در `toolkit/make_reel.py`؛ مدت هدف ۲۵ ثانیه.
- **نوع جدید / سخنگو (پیش‌فرض):** ویدیوی خود کاربر کوچک پایین‌چپ، پس‌زمینهٔ علمی در تمام ویدیو و صدای اصلی بدون موسیقی؛ مدت هدف ۳۰ ثانیه. کلیپ‌ها و اسکریپت‌های این حالت هنگام ثبت راهنما در این checkout موجود نبودند.

ادامهٔ این README راهنمای موتور **انیمیشنی** است. قواعد جدید نام‌گذاری، تحویل و بررسی وجود فایل‌ها را از `START-PROMPT.md` بخوان.

---

## 🚀 دستور شروع سریع (در چت جدید این را بفرست)

> کارخانهٔ ریلز — فایل `START-PROMPT.md` در ریشهٔ مخزن را بخوان.
> قالب: «نوع قدیم / انیمیشنی» یا «نوع جدید / سخنگو»
> موضوع: «...» — پالت در صورت نیاز: «...»
> برای نوع جدید، سه کلیپ یا لینک دانلود آن‌ها به‌ترتیب: «...»

در چت مستقل، خود راهنما و رسانه‌ها یا لینک‌های قابل‌دسترسی آن‌ها را نیز همراه بفرست؛ صرف مسیر محلی یا لینک `main` وجود فایل‌های این شاخه و گفتگوی قبلی را تضمین نمی‌کند.

---

## 📦 ساختار

```
Kiankhosrobot/
  DASTOOR-OLAMAL.md      ← قوانین و استانداردها (مهم‌ترین فایل)
  toolkit/
    make_reel.py         ← موتور اصلی ساخت ریلز
    icons.py             ← ۹۱ آیکون وکتور
    fatext.py            ← شکل‌دهی متن فارسی با HarfBuzz (جایگزین libraqm)
    check_output.py      ← بررسی مشخصات فایل نهایی (وضوح، فریم، مدت، حجم، صدا)
    topic_adhd.py        ← نمونهٔ پیکربندی یک موضوع
```

### بررسی خروجی پیش از تحویل

```bash
python3 toolkit/check_output.py <slug>_reel.mp4 4 20 30
# آرگومان‌ها: مسیر فایل · حداکثر حجم (MB) · حداقل مدت · حداکثر مدت
```

مشخصات را از خود فایل می‌خواند (نه از نام یا تنظیمات مورد انتظار) و برای هر معیار ✔/✘ می‌دهد.

### مسیر فونت

موتور فونت را خودکار پیدا می‌کند: متغیر محیطی `REEL_FONTS`، سپس `/home/user/fonttmp/fonts/ttf/`،
سپس پوشهٔ `fonttmp` کنار خود مخزن. برای مسیر دلخواه:

```bash
export REEL_FONTS=/path/to/vazirmatn/fonts/ttf/
```

لینک خام فایل‌ها (برای دانلود مستقیم):
```
https://raw.githubusercontent.com/kindlykaren48-del/Kiankhosrobot/main/Kiankhosrobot/toolkit/make_reel.py
https://raw.githubusercontent.com/kindlykaren48-del/Kiankhosrobot/main/Kiankhosrobot/toolkit/icons.py
https://raw.githubusercontent.com/kindlykaren48-del/Kiankhosrobot/main/Kiankhosrobot/toolkit/fatext.py
https://raw.githubusercontent.com/kindlykaren48-del/Kiankhosrobot/main/Kiankhosrobot/DASTOOR-OLAMAL.md
```

---

## ⚙️ آماده‌سازی محیط (هر چت جدید)

```bash
pip install -q imageio-ffmpeg numpy pillow uharfbuzz freetype-py
# فونت وزیرمتن (در مخزن نیست، باید دانلود شود)
curl -sL -o /tmp/v.zip https://github.com/rastikerdar/vazirmatn/releases/download/v33.003/vazirmatn-v33.003.zip
mkdir -p /home/user/fonttmp && unzip -qo /tmp/v.zip -d /home/user/fonttmp
# مسیر نهایی: /home/user/fonttmp/fonts/ttf/
```

---

## 🎨 پالت‌های موجود

`neon` · `neonpurple` · `neonmosaic` · `aurora` · `nuclear` · `wineamber` · `kiddo`
`purplegreen` · `purplemustard` · `redmustard` · `bluegreen` · `orangeteal`

### سبک نئونی
با `"style": "neon"` فعال می‌شود. تنظیمات اختیاری:

| کلید | توضیح | پیش‌فرض |
|---|---|---|
| `neon_base` | رنگ زمینه | `(8,8,10)` مشکی |
| `neon_arc` | رنگ قوس‌ها | نارنجی کم‌رنگ |
| `neon_mosaic` | بافت کاشی‌کاری | `False` |

---

## 📝 نمونه پیکربندی

```python
from make_reel import build_all

cfg = {
    "slug": "example",
    "palette": "neonpurple",
    "style": "neon",
    "neon_base": (26, 6, 54),
    "title_fa": "عنوان فارسی",
    "title_en": "ENGLISH TITLE",
    "subtitle": "زیرعنوان",
    "cover_tags": ["تگ ۱", "تگ ۲", "تگ ۳", "تگ ۴"],
    "cta": "این ویدیو را برای دوستانت بفرست",
    "cover_ill": "ill0.png",
    "slides": [
        ("۱", "عنوان", "TITLE", "ill1.png",
         [("dna", "متن گلوله اول"),
          ("heart", "متن گلوله دوم")]),
        # مجموعاً ۴ اسلاید
    ],
}
build_all(cfg)
```

⚠️ نکته: کلید تگ‌های کاور **`cover_tags`** است، نه `tags`.

---

## 🔁 مراحل ساخت

1. `mkdir <dir>` و کپی `icons.py` + `make_reel.py` داخلش
2. ساخت ۵ فایل صوتی `s0..s4.mp3` (مجموع خام ≈ ۲۳ ثانیه)
3. ساخت ۵ تصویر `ill0..ill4.png` و `cp ill0.png bg_cover.png`
4. نوشتن `topic.py` و اجرای `python3 topic.py`
5. بررسی `f_cover.png` و یک اسلاید
6. نوشتن کپشن
7. کپی به ریشه با نام‌های کوتاه: `reel.mp4` / `cover.png` / `caption.txt`
8. **تحویل سه کادر لینک**
9. `rm -rf <dir>`

---

## ⚠️ نکات حیاتی

- **شکل‌دهی متن:** اگر Pillow با libraqm نصب باشد، فارسی خودکار درست می‌شود. اگر نباشد (خطای `setting text direction ... not supported without libraqm`)، فایل `fatext.py` را کنار `make_reel.py` بگذار؛ موتور خودش از آن استفاده می‌کند و متن دوجهته (لاتین/عدد داخل جملهٔ فارسی) هم درست چیده می‌شود.

- **فارسی:** فقط Pillow با libraqm و `language="fa", direction="rtl"`. هرگز `arabic_reshaper` یا `python-bidi`.
- **فونت:** فقط وزیرمتن. DejaVu حروف فارسی را نمی‌چسباند.
- **ایموجی:** رندر نمی‌شود (مربع خالی) — از آیکون‌های وکتور استفاده کن.
- **تمپو:** مجموع خام روایت باید ≈ ۲۳ ثانیه باشد تا تمپو زیر ۱.۳ بماند. بالای ۱.۵ تند و ناخوشایند است.
- **آیکون:** قبل از ساخت، وجود نام هر آیکون در `icons.py` را بررسی کن.
- **صدا:** شناسه صدا به هر نشست گره خورده و در مخزن ذخیره نمی‌شود؛ در هر چت جدید باید دوباره ثبت شود.

---

## 📐 استانداردهای ثابت

۱۰۸۰×۱۹۲۰ · ۳۰ فریم · ۲۵ ثانیه · زیر ۴ مگابایت · بدون موسیقی · متن بالا / تصویر پایین

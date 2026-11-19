# پروژه انیمیشن توضیحی سه‌بعدی — Explainer 3D

> ⛔ **پروژه دائمی — هرگز پاک نشود.** (رجوع کنید به `DO_NOT_DELETE.md`)

تولید انیمیشن توضیحی سه‌بعدی **۲۵ ثانیه‌ای** با **Three.js** — ابعاد **۱۹۲۰×۱۰۸۰** (۱۶:۹)، **۶۰fps**، خروجی **MP4**، با پشتیبانی از ویس‌اور فارسی و متن **RTL** با فونت **Vazirmatn**.

## دستور کار (خلاصه)

وقتی کاربر یک **موضوع** و یک **شماره استایل (۰۱ تا ۱۰)** می‌دهد:

1. پرامپت همان استایل را از `PROJECT_INSTRUCTIONS.md` بردار و `[YOUR TOPIC HERE]` را با موضوع جایگزین کن.
2. اول فقط یک **استوری‌بورد ۵ بیتی** کوتاه ارائه بده و منتظر تأیید کاربر بمان.
3. بعد از تأیید، پروژه کامل و قابل اجرا را بساز: `index.html` با تابع قطعی `renderAtTime(t)` و اسکریپت `render.mjs` (Playwright/FFmpeg) برای خروجی `output.mp4`.
4. اگر کاربر `voiceover.mp3` و تایم‌کد جملات را داد، انیمیشن را دقیقاً با صدا سینک کن.
5. اگر کاربر استایل را نگفت، با توجه به موضوع بهترین استایل را از جدول پیشنهاد بده.

متن کامل دستور و هر ۱۰ استایل در **`PROJECT_INSTRUCTIONS.md`** آمده است.

## استایل‌ها

| # | استایل | بهترین کاربرد |
|---|---|---|
| ۰۱ | Dark Industrial Precision | مهندسی، تکنولوژی، SaaS، سخت‌افزار |
| ۰۲ | Soft Clay Isometric Diorama | آموزش، استارتاپ، داستان‌گویی |
| ۰۳ | Architectural Blueprint | معماری نرم‌افزار، نقشه‌راه، تحلیل فنی |
| ۰۴ | Paper Pop-Up & Origami | خلاصه کتاب، تاریخچه، داستان برند |
| ۰۵ | Neon Cyberpunk Megacity | هوش مصنوعی، امنیت سایبری، گیمینگ |
| ۰۶ | Low-Poly Isometric World | اقتصاد، محیط‌زیست، بهره‌وری |
| ۰۷ | Swiss Museum Marble & Gold | مالی، سرمایه‌گذاری، برند لوکس |
| ۰۸ | Retro 80s Synthwave Grid | بازاریابی، فرهنگ عامه، موسیقی |
| ۰۹ | Voxel Isometric Block World | برنامه‌نویسی، دیتابیس، آموزش نوجوانان |
| ۱۰ | Bioluminescent Organic Glass | پزشکی، علوم اعصاب، روان‌شناسی |

## ساختار

```
explainer-3d/
├── DO_NOT_DELETE.md            # هشدار حفاظت — هرگز پاک نشود
├── PROJECT_INSTRUCTIONS.md     # دستور کامل کاربر (منبع اصلی)
├── README.md                   # همین راهنما
├── template/                   # قالب آماده و قابل اجرا
│   ├── index.html              # صحنه Three.js با renderAtTime(t) قطعی
│   ├── render.mjs              # رندر ۶۰fps با Playwright + FFmpeg → output.mp4
│   ├── package.json
│   └── README.md
└── projects/                   # خروجی هر موضوع (یک پوشه برای هر پروژه)
```

## استفاده از قالب

```bash
cd explainer-3d/template
npm install
npx playwright install chromium   # یک‌بار برای نصب مرورگر
node render.mjs                   # خروجی: output.mp4 (۲۵ ثانیه، ۱۹۲۰×۱۰۸۰، ۶۰fps)
```

اگر فایل `voiceover.mp3` کنار `render.mjs` باشد، به‌صورت خودکار روی ویدیو میکس می‌شود.

## پشتیبان‌گیری

- **Git:** این پروژه در تاریخچه گیت ثبت و روی GitHub پشتیبان‌گیری شده است.
- **Google Drive:** نسخه پشتیبان دستور کامل در Google Drive ذخیره شده است.

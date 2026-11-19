# قالب انیمیشن توضیحی سه‌بعدی

قالب آماده و قابل اجرای پروژه دائمی `explainer-3d` — استایل پیش‌فرض **۰۱ (Dark Industrial Precision)**.

## فایل‌ها

| فایل | توضیح |
|---|---|
| `index.html` | صحنه Three.js با تابع قطعی `renderAtTime(t)`، HUD فارسی RTL با Vazirmatn، پست‌پروسس Bloom |
| `render.mjs` | رندر ۶۰fps با Playwright و خروجی FFmpeg به `output.mp4` |
| `package.json` | وابستگی‌ها |

## اجرا

```bash
npm install
npx playwright install chromium
node render.mjs        # → output.mp4
```

## سفارشی‌سازی برای هر موضوع

1. در `index.html` بخش `CONFIG` را ویرایش کنید: `topic`، شماره `style` و ۵ بیت استوری‌بورد.
2. پالت/متریال/نور را طبق استایل انتخابی در `../PROJECT_INSTRUCTIONS.md` تغییر دهید.
3. اگر `voiceover.mp3` دارید، آن را کنار `render.mjs` بگذارید تا خودکار میکس شود؛ تایم‌کد جملات را با بیت‌ها هم‌زمان کنید.

> ⛔ این قالب بخشی از پروژه دائمی است — هرگز پاک نشود.

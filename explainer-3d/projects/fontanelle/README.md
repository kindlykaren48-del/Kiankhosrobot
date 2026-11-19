# ملاج نوزاد — انیمیشن توضیحی سه‌بعدی

استوری‌بورد پنج‌بخشی؛ موضوع شمارهٔ ۲ فهرست مراقبت‌های نوزاد، سبک ۰۲ خمیری؛ رنگ کاور سرخ و نارنجی. کد `renderAtTime(t)` قطعی است. خروجی هدف: ۲۵ ثانیه، ۱۹۲۰×۱۰۸۰، ۶۰ فریم، MP4. تصویر کاور تولیدشده با هوش مصنوعی است و مدل جمجمه نمای شماتیک است.

## منابع پزشکی
- American Academy of Pediatrics: https://www.healthychildren.org/English/ages-stages/baby/Pages/How-Your-Newborn-Looks.aspx — ملاج و لمس ملایم
- American Academy of Pediatrics: https://www.healthychildren.org/English/ages-stages/baby/bathing-skin-care/Pages/Bathing-Your-Newborn.aspx — شست‌وشوی ملایم
- MedlinePlus: https://medlineplus.gov/ency/article/003310.htm — ملاج برجسته در آرامش نیازمند ارزیابی اورژانسی است.
- Pregnancy, Birth and Baby: https://www.pregnancybirthbaby.org.au/about-the-fontanelle — فرورفتگی یا برجستگی، مراجعه فوری.

محتوا جایگزین تشخیص پزشکی نیست و قبل از انتشار باید بازبینی پزشکی شود.

## اجرا
از ریشه مخزن `cd explainer-3d/projects/fontanelle && npm install && node render.mjs`. فایل محلی `voiceover.mp3` اختیاری است؛ در صورت وجود روی ویدیو قرار می‌گیرد و برای هماهنگی باید جملات آن مطابق بازه‌های ۵ ثانیه‌ای باشند. در صورت نبود فایل صدا، رندر بی‌صدا تولید می‌شود. متون نریشن پیشنهادی در narration.txt است. FFmpeg باید نصب باشد یا مسیر آن در متغیر `FFMPEG` تنظیم شود. فایل فونت وزیرمتن از `fonttmp` همین مخزن ارائه می‌شود.

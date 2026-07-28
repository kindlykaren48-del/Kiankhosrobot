import os
import requests
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openrouter/free"


SYSTEM_PROMPT = """
تو مدیر ارشد تولید محتوای اینستاگرام برای یک متخصص کودکان و نوزادان هستی.

هدف:
تولید محتوای علمی، جذاب و قابل اعتماد برای والدین، با تمرکز بر ریلزهای کوتاه اینستاگرام.

هویت برند:
- تخصص: کودکان و نوزادان
- مخاطب: والدین و مراقبین کودک
- زبان: فارسی طبیعی و روان ایرانی
- لحن: علمی، حرفه‌ای، آرام، صمیمی و قابل اعتماد
- از ترساندن مخاطب، اغراق و ادعاهای پزشکی بدون پشتوانه خودداری کن.

قوانین ریلز:

1. مدت ویدئو باید بین 20 تا 30 ثانیه باشد.
2. پیش‌فرض را نزدیک 30 ثانیه تنظیم کن، مگر اینکه موضوع با زمان کمتر بهتر منتقل شود.
3. ریلز فقط یک پیام علمی اصلی داشته باشد.
4. در خود ریلز فقط:
   - Hook
   - توضیح علمی
   - نکته کلیدی
   قرار بگیرد.
5. در ریلز جمع‌بندی جداگانه ننویس.
6. در ریلز باور غلط، هشدار طولانی، علائم خطر و نکات فرعی را وارد نکن.
7. این موارد را در کپشن قرار بده.
8. دعوت به ذخیره و اشتراک‌گذاری فقط به صورت کوچک روی تصویر یا آیکون باشد و زمان گویندگی را نگیرد.
9. متن گویندگی باید طبیعی باشد و برای خواندن توسط پزشک مناسب باشد.
10. از اصطلاحات پزشکی غیرضروری و پیچیده برای والدین استفاده نکن.
11. اگر موضوع از نظر پزشکی حساس است، دقت علمی را بر جذابیت ترجیح بده.
12. اطلاعاتی که ممکن است به‌سرعت تغییر کنند را بدون اطمینان قطعی بیان نکن.

دو سبک تولید:

STYLE A:
حضور پزشک جلوی دوربین.
برای هر صحنه، پیشنهاد ساده و عملی فیلم‌برداری بده.

STYLE B:
بدون حضور پزشک.
برای هر صحنه، پیشنهاد تصویر، انیمیشن یا ویدئوی مناسب برای تولید با AI بده.

اگر کاربر سبک را مشخص نکرد، هر دو سبک را پیشنهاد بده اما محتوای علمی مشترک باشد.

ساختار خروجی:

🎬 عنوان

🔥 Hook

⏱ مدت پیشنهادی

🎙 متن کامل گویندگی
20 تا 30 ثانیه، فقط توضیح علمی و نکته کلیدی.

🎥 STYLE A — حضور پزشک
صحنه‌ها با زمان تقریبی.

🤖 STYLE B — بدون حضور پزشک
صحنه‌ها با زمان تقریبی و پیشنهاد Visual.

🖥 متن‌های کوتاه روی تصویر
فقط موارد ضروری.

🔖 CTA تصویری
پیشنهاد کوچک برای آیکون Save و Share، بدون اضافه کردن به متن گویندگی.

📝 کپشن
کپشن باید شامل:
- توضیح تکمیلی
- باورهای غلط مرتبط، در صورت وجود
- هشدارهای مهم، در صورت وجود
- موارد مراجعه یا ارجاع پزشکی، در صورت نیاز
- یک سؤال مناسب برای افزایش تعامل

#️⃣ هشتگ‌ها

📌 نکته علمی کلیدی

خروجی را کاربردی و آماده استفاده کن.
"""


def ask_openrouter(user_message: str) -> str:

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://telegram.org/",
        "X-Title": "Kiankhosrobot",
    }

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": user_message,
            },
        ],
        "temperature": 0.7,
        "max_tokens": 3000,
    }

    response = requests.post(
        OPENROUTER_URL,
        headers=headers,
        json=payload,
        timeout=90,
    )

    if response.status_code != 200:
        try:
            error_data = response.json()
        except Exception:
            error_data = response.text

        raise RuntimeError(
            f"OpenRouter error {response.status_code}: {error_data}"
        )

    data = response.json()

    if "choices" not in data or not data["choices"]:
        raise RuntimeError("OpenRouter پاسخ قابل استفاده‌ای برنگرداند.")

    return data["choices"][0]["message"]["content"]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "سلام 👋\n\n"
        "من Kiankhosrobot هستم؛ دستیار تولید محتوای اینستاگرام "
        "برای برند پزشکی کودکان.\n\n"
        "موضوع ریلز را برایم بفرست.\n\n"
        "مثال:\n"
        "تب در کودک\n\n"
        "یا:\n"
        "/reel زردی نوزاد"
    )


async def reel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    topic = " ".join(context.args).strip()

    if not topic:
        await update.message.reply_text(
            "موضوع ریلز را بعد از /reel بنویس.\n\n"
            "مثال:\n"
            "/reel تب کودک"
        )
        return

    await update.message.reply_text(
        "🎬 در حال ساخت ریلز...\n"
        "موضوع را از نظر علمی و ساختار اینستاگرامی بررسی می‌کنم."
    )

    try:
        result = ask_openrouter(
            f"برای این موضوع یک ریلز حرفه‌ای بساز:\n\n{topic}"
        )

        await send_long_message(update, result)

    except Exception as error:

        print("ERROR:", error)

        await update.message.reply_text(
            "⚠️ فعلاً در اتصال به موتور هوش مصنوعی مشکلی پیش آمد.\n\n"
            "چند لحظه بعد دوباره امتحان کن."
        )


async def normal_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_message = update.message.text.strip()

    if not user_message:
        return

    await update.message.reply_text(
        "🧠 دارم محتوای مناسب برای این موضوع را آماده می‌کنم..."
    )

    try:

        result = ask_openrouter(user_message)

        await send_long_message(update, result)

    except Exception as error:

        print("ERROR:", error)

        await update.message.reply_text(
            "⚠️ خطایی در ارتباط با هوش مصنوعی رخ داد."
        )


async def send_long_message(update: Update, text: str):

    # Telegram پیام‌های بسیار طولانی را قبول نمی‌کند.
    # خروجی را به قطعات کوچک‌تر تقسیم می‌کنیم.

    max_length = 3800

    for i in range(0, len(text), max_length):

        await update.message.reply_text(
            text[i:i + max_length]
        )


def main():

    if not TELEGRAM_TOKEN:
        raise RuntimeError(
            "TELEGRAM_TOKEN در Environment Variables تنظیم نشده است."
        )

    if not OPENROUTER_API_KEY:
        raise RuntimeError(
            "OPENROUTER_API_KEY در Environment Variables تنظیم نشده است."
        )

    app = (
        Application.builder()
        .token(TELEGRAM_TOKEN)
        .build()
    )

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CommandHandler("reel", reel)
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            normal_message
        )
    )

    print("Kiankhosrobot is running...")

    app.run_polling(
        allowed_updates=Update.ALL_TYPES
    )


if __name__ == "__main__":
    main()

import os
import requests

from flask import Flask, request
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

RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL")

PORT = int(os.getenv("PORT", "10000"))

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

MODEL = "openrouter/free"

WEBHOOK_PATH = "/telegram-webhook"


SYSTEM_PROMPT = """
تو مدیر ارشد تولید محتوای اینستاگرام برای یک متخصص کودکان و نوزادان هستی.

هدف:
تولید محتوای علمی، جذاب و قابل اعتماد برای والدین.

هویت برند:
- تخصص: کودکان و نوزادان
- مخاطب: والدین و مراقبین کودک
- زبان: فارسی طبیعی و روان ایرانی
- لحن: علمی، حرفه‌ای، آرام، صمیمی و قابل اعتماد

قوانین ریلز:

1. مدت ویدئو فقط بین 20 تا 30 ثانیه باشد.
2. ترجیحاً نزدیک 30 ثانیه باشد.
3. ریلز فقط یک پیام علمی اصلی داشته باشد.
4. در خود ریلز فقط:
   - Hook
   - توضیح علمی
   - نکته کلیدی
   قرار بگیرد.
5. جمع‌بندی جداگانه در پایان ریلز نداشته باش.
6. باور غلط، هشدار، علائم خطر و نکات تکمیلی را داخل متن گویندگی نیاور.
7. این موارد در کپشن قرار بگیرند.
8. دعوت به Save و Share فقط به صورت آیکون یا نوشته بسیار کوچک روی تصویر باشد.
9. CTA نباید زمان گویندگی را بگیرد.
10. متن گویندگی طبیعی و مناسب صحبت کردن پزشک باشد.
11. از ترساندن والدین و اغراق خودداری کن.
12. اطلاعات پزشکی باید تا حد ممکن مبتنی بر شواهد باشد.

STYLE A:
پزشک جلوی دوربین حضور دارد.

STYLE B:
بدون حضور پزشک؛ با تصویر، انیمیشن یا ویدئوی تولیدشده با AI.

خروجی:

🎬 عنوان

🔥 Hook

⏱ مدت

🎙 متن گویندگی
20 تا 30 ثانیه

🎥 STYLE A
صحنه‌بندی و پیشنهاد فیلم‌برداری

🤖 STYLE B
صحنه‌بندی و پیشنهاد Visual

🖥 متن روی تصویر

🔖 CTA تصویری

📝 کپشن
شامل:
- توضیح تکمیلی
- باورهای غلط
- هشدارهای لازم
- علائم خطر در صورت نیاز
- زمان مراجعه به پزشک
- سؤال مناسب برای تعامل

#️⃣ هشتگ‌ها

📌 نکته علمی کلیدی
"""


def ask_openrouter(user_message: str) -> str:

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": RENDER_EXTERNAL_URL or "https://render.com",
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
            error = response.json()
        except Exception:
            error = response.text

        raise RuntimeError(
            f"OpenRouter error {response.status_code}: {error}"
        )

    data = response.json()

    if not data.get("choices"):
        raise RuntimeError("OpenRouter پاسخ معتبری برنگرداند.")

    return data["choices"][0]["message"]["content"]


async def send_long_message(update: Update, text: str):

    max_length = 3800

    for i in range(0, len(text), max_length):
        await update.message.reply_text(
            text[i:i + max_length]
        )


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "سلام 👋\n\n"
        "من Kiankhosrobot هستم.\n"
        "دستیار تولید محتوای اینستاگرام پزشکی کودکان.\n\n"
        "برای ساخت ریلز بنویس:\n\n"
        "/reel تب کودک\n\n"
        "یا فقط موضوع را بفرست."
    )


async def reel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    topic = " ".join(context.args).strip()

    if not topic:
        await update.message.reply_text(
            "موضوع ریلز را بنویس.\n\n"
            "مثال:\n"
            "/reel زردی نوزاد"
        )
        return

    await update.message.reply_text(
        "🎬 در حال ساخت ریلز...\n\n"
        "موضوع را از نظر علمی و ساختار اینستاگرام بررسی می‌کنم."
    )

    try:

        result = ask_openrouter(
            f"""
یک ریلز حرفه‌ای 20 تا 30 ثانیه‌ای درباره این موضوع بساز:

{topic}

فقط یک پیام علمی اصلی را آموزش بده.
"""

        )

        await send_long_message(update, result)

    except Exception as error:

        print("ERROR:", error)

        await update.message.reply_text(
            "⚠️ در اتصال به موتور هوش مصنوعی مشکلی پیش آمد.\n"
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
        "🧠 دارم محتوا را آماده می‌کنم..."
    )

    try:

        result = ask_openrouter(user_message)

        await send_long_message(update, result)

    except Exception as error:

        print("ERROR:", error)

        await update.message.reply_text(
            "⚠️ خطایی در ارتباط با هوش مصنوعی رخ داد."
        )


app = Flask(__name__)

telegram_app = (
    Application.builder()
    .token(TELEGRAM_TOKEN)
    .updater(None)
    .build()
)

telegram_app.add_handler(
    CommandHandler("start", start)
)

telegram_app.add_handler(
    CommandHandler("reel", reel)
)

telegram_app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        normal_message
    )
)


@app.get("/")
def home():

    return "Kiankhosrobot is running."


@app.get("/health")
def health():

    return "OK"


@app.post(WEBHOOK_PATH)
async def telegram_webhook():

    data = request.get_json(force=True)

    update = Update.de_json(
        data,
        telegram_app.bot
    )

    await telegram_app.process_update(update)

    return "OK"


async def setup_webhook():

    await telegram_app.initialize()

    webhook_url = (
        RENDER_EXTERNAL_URL.rstrip("/")
        + WEBHOOK_PATH
    )

    await telegram_app.bot.set_webhook(
        url=webhook_url,
        allowed_updates=Update.ALL_TYPES
    )

    print("Webhook set to:")
    print(webhook_url)


if __name__ == "__main__":

    import asyncio

    asyncio.run(setup_webhook())

    app.run(
        host="0.0.0.0",
        port=PORT
        )

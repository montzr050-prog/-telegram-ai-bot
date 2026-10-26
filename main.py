import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from openai import AsyncOpenAI

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logging.getLogger("httpx").setLevel(logging.WARNING)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("Missing TELEGRAM_BOT_TOKEN environment variable")
if not OPENAI_API_KEY:
    raise RuntimeError("Missing OPENAI_API_KEY environment variable")

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "هلا بيك! أنا بوت ذكاء اصطناعي 🤖\n"
        "اكتب سؤالك وأجاوبك.\n"
        "ملاحظة: استخدام الذكاء الاصطناعي يحتاج رصيد API."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("أرسل أي سؤال برسالة نصية، أو اكتب /start للبدء.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return

    user_text = update.message.text.strip()
    if not user_text:
        return

    # Basic per-chat conversation history, kept in memory while the worker runs.
    history = context.chat_data.setdefault("history", [])
    history.append({"role": "user", "content": user_text})
    history[:] = history[-10:]

    try:
        response = await client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "أنت مساعد مفيد. أجب باللغة التي يستخدمها الشخص، "
                        "وإذا كتب باللهجة العراقية فحاول الرد باللهجة العراقية بوضوح."
                    ),
                },
                *history,
            ],
        )
        answer = response.choices[0].message.content or "ما كدرت أطلع جواب، جرّب مرة ثانية."
        history.append({"role": "assistant", "content": answer})
        history[:] = history[-10:]

        # Telegram message limit is about 4096 characters.
        for i in range(0, len(answer), 4000):
            await update.message.reply_text(answer[i:i+4000])
    except Exception:
        logging.exception("Error while processing message")
        await update.message.reply_text(
            "صار خطأ أثناء معالجة رسالتك. تأكد من إعداد مفاتيح التشغيل ورصيد OpenAI API."
        )

def main() -> None:
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logging.info("Telegram AI bot is starting")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()

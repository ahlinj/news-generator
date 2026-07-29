from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import json
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

SUBSCRIBERS_FILE = Path("subscribers.json")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def load_subscribers():
    return json.loads(SUBSCRIBERS_FILE.read_text())

def save_subscribers(subscribers):
    SUBSCRIBERS_FILE.write_text(
        json.dumps(subscribers, indent=2)
    )

def subscribe(chat_id):
    subscribers = load_subscribers()

    if chat_id not in subscribers:
        subscribers.append(chat_id)
        save_subscribers(subscribers)

def unsubscribe(chat_id):
    subscribers = load_subscribers()

    if chat_id in subscribers:
        subscribers.remove(chat_id)
        save_subscribers(subscribers)

async def subscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    subscribe(chat_id)

    await update.message.reply_text("✅ This chat is now subscribed.")

async def unsubscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    unsubscribe(chat_id)

    await update.message.reply_text("❌ This chat has been unsubscribed.")

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(
        CommandHandler("subscribe", subscribe_command)
    )

    app.add_handler(
        CommandHandler("unsubscribe", unsubscribe_command)
    )

    app.run_polling()


if __name__ == "__main__":
    main()
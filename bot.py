import os
import asyncio
from flask import Flask
from threading import Thread

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
MOVIE_LINK = os.getenv("MOVIE_LINK")

CHANNELS = []

for i in range(1, 7):
    channel_id = os.getenv(f"CHANNEL_{i}")
    channel_link = os.getenv(f"CHANNEL_{i}_LINK")

    if channel_id and channel_link:
        CHANNELS.append((channel_id, channel_link))


app = Flask(__name__)


@app.route("/")
def home():
    return "Bot is running!"


def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = []

    for i, (channel_id, channel_link) in enumerate(CHANNELS, start=1):
        keyboard.append([
            InlineKeyboardButton(
                f"🔗 JOIN Channel {i}",
                url=channel_link
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "✅ CHECK JOIN",
            callback_data="check_join"
        )
    ])

    text = (
        "🎬 Welcome!\n\n"
        "Content ရယူရန် Channel ၆ ခုလုံးကို အရင် Join လုပ်ပေးပါ။\n\n"
        "1️⃣ JOIN Channel 1\n"
        "2️⃣ JOIN Channel 2\n"
        "3️⃣ JOIN Channel 3\n"
        "4️⃣ JOIN Channel 4\n"
        "5️⃣ JOIN Channel 5\n"
        "6️⃣ JOIN Channel 6\n\n"
        "Join ပြီးရင် အောက်က\n"
        "✅ CHECK JOIN ကိုနှိပ်ပါ။"
    )

    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    not_joined = []

    for channel_id, channel_link in CHANNELS:
        try:
            member = await context.bot.get_chat_member(
                chat_id=channel_id,
                user_id=user_id
            )

            if member.status in ["left", "kicked"]:
                not_joined.append(channel_link)

        except Exception:
            not_joined.append(channel_link)

    if not_joined:
        await query.answer(
            "❌ Channel 6 ခုလုံး Join လုပ်ပြီးမှ Check Join နှိပ်ပါ။",
            show_alert=True
        )
        return

    await query.message.reply_text(
        f"✅ Join အားလုံးမှန်ပါတယ်!\n\n"
        f"🎬 Movie Link:\n{MOVIE_LINK}"
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    if query.data == "check_join":
        await check_join(update, context)


def main():

    Thread(target=run_flask, daemon=True).start()

    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    application.add_handler(CommandHandler("start", start))

    application.add_handler(
        __import__(
            "telegram.ext",
            fromlist=["CallbackQueryHandler"]
        ).CallbackQueryHandler(
            button_handler,
            pattern="^check_join$"
        )
    )

    application.run_polling()


if __name__ == "__main__":
    main()

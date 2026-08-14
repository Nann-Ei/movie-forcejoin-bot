import os
import threading

from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# =========================
# ENVIRONMENT VARIABLES
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN")
MOVIE_LINK = os.getenv("MOVIE_LINK")

CHANNELS = [
    {
        "id": os.getenv("CHANNEL_1"),
        "link": os.getenv("CHANNEL_1_LINK"),
        "name": "Channel 1",
    },
    {
        "id": os.getenv("CHANNEL_2"),
        "link": os.getenv("CHANNEL_2_LINK"),
        "name": "Channel 2",
    },
    {
        "id": os.getenv("CHANNEL_3"),
        "link": os.getenv("CHANNEL_3_LINK"),
        "name": "Channel 3",
    },
    {
        "id": os.getenv("CHANNEL_4"),
        "link": os.getenv("CHANNEL_4_LINK"),
        "name": "Channel 4",
    },
    {
        "id": os.getenv("CHANNEL_5"),
        "link": os.getenv("CHANNEL_5_LINK"),
        "name": "Channel 5",
    },
    {
        "id": os.getenv("CHANNEL_6"),
        "link": os.getenv("CHANNEL_6_LINK"),
        "name": "Channel 6",
    },
]


# =========================
# FLASK WEB SERVER
# =========================

web_app = Flask(__name__)


@web_app.route("/")
def home():
    return "Telegram Bot is running!"


def run_web_server():
    port = int(os.getenv("PORT", "8000"))
    web_app.run(
        host="0.0.0.0",
        port=port
    )


# =========================
# TELEGRAM BOT
# =========================

def join_keyboard():
    keyboard = []

    for channel in CHANNELS:
        if channel["link"]:
            keyboard.append([
                InlineKeyboardButton(
                    f"🔗 JOIN {channel['name']}",
                    url=channel["link"]
                )
            ])

    keyboard.append([
        InlineKeyboardButton(
            "✅ CHECK JOIN",
            callback_data="check_join"
        )
    ])

    return InlineKeyboardMarkup(keyboard)


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    text = (
        "🎬 Welcome!\n\n"
        "Content ရယူရန် Channel ၆ ခုလုံးကို "
        "အရင် Join လုပ်ပေးပါ။\n\n"
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
        reply_markup=join_keyboard()
    )


async def check_member(
    bot,
    user_id,
    channel_id
):
    try:
        member = await bot.get_chat_member(
            chat_id=channel_id,
            user_id=user_id
        )

        return member.status in (
            "member",
            "administrator",
            "creator"
        )

    except Exception:
        return False


async def check_join(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query

    await query.answer()

    user_id = query.from_user.id

    not_joined = []

    for index, channel in enumerate(CHANNELS, start=1):

        if not channel["id"]:
            not_joined.append(index)
            continue

        joined = await check_member(
            context.bot,
            user_id,
            channel["id"]
        )

        if not joined:
            not_joined.append(index)

    # =========================
    # ALL CHANNELS JOINED
    # =========================

    if not not_joined:

        if MOVIE_LINK:
            keyboard = [[
                InlineKeyboardButton(
                    "🎬 WATCH CONTENT",
                    url=MOVIE_LINK
                )
            ]]

            await query.edit_message_text(
                "✅ Channel ၆ ခုလုံး Join ထားပါတယ်။\n\n"
                "🎬 အခု Content ကို ဝင်ကြည့်နိုင်ပါပြီ။",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        else:
            await query.edit_message_text(
                "✅ Channel ၆ ခုလုံး Join ထားပါတယ်။\n\n"
                "⚠️ Content link မထည့်ရသေးပါ။"
            )

    # =========================
    # NOT ALL JOINED
    # =========================

    else:

        missing = ", ".join(
            f"Channel {number}"
            for number in not_joined
        )

        await query.answer(
            f"❌ Join မလုပ်ရသေးတာ: {missing}",
            show_alert=True
        )


# =========================
# START BOT
# =========================

def main():

    if not BOT_TOKEN:
        raise ValueError(
            "BOT_TOKEN is missing!"
        )

    # Start Flask server
    threading.Thread(
        target=run_web_server,
        daemon=True
    ).start()

    # Start Telegram bot
    bot_app = (
        Application
        .builder()
        .token(BOT_TOKEN)
        .build()
    )

    bot_app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    bot_app.add_handler(
        CallbackQueryHandler(
            check_join,
            pattern="^check_join$"
        )
    )

    print("Telegram Bot is running...")

    bot_app.run_polling()


if __name__ == "__main__":
    main()

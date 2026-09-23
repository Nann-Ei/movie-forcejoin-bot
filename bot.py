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

BOT_TOKEN = os.getenv("BOT_TOKEN")
CONTENT_CHANNEL = os.getenv("CONTENT_CHANNEL")
ADMIN_ID = os.getenv("ADMIN_ID")

CHANNELS = []

for i in range(1, 7):
    channel_id = os.getenv(f"CHANNEL_{i}")
    channel_link = os.getenv(f"CHANNEL_{i}_LINK")

    if channel_id and channel_link:
        CHANNELS.append({
            "id": channel_id,
            "link": channel_link,
            "name": f"Channel {i}"
        })


# =========================
# Flask
# =========================

app = Flask(__name__)

@app.route("/")
def home():
    return "Telegram Bot is running!"


def run_web():
    port = int(os.getenv("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)


# =========================
# Join Buttons
# =========================

def join_keyboard():
    keyboard = []

    for channel in CHANNELS:
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


def join_text():
    return (
        "🎬 Welcome!\n\n"
        "Movie ရယူရန် Channel ၆ ခုလုံးကို အရင် Join လုပ်ပေးပါ။\n\n"
        "1️⃣ JOIN Channel 1\n"
        "2️⃣ JOIN Channel 2\n"
        "3️⃣ JOIN Channel 3\n"
        "4️⃣ JOIN Channel 4\n"
        "5️⃣ JOIN Channel 5\n"
        "6️⃣ JOIN Channel 6\n\n"
        "အားလုံး Join ပြီးရင်\n"
        "✅ CHECK JOIN ကိုနှိပ်ပါ။"
    )


# =========================
# /start
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    movie_id = None

    if context.args:
        arg = context.args[0]

        if arg.startswith("movie_"):
            movie_id = arg.replace("movie_", "", 1)

            if movie_id.isdigit():
                context.user_data["movie_id"] = int(movie_id)

    await update.message.reply_text(
        join_text(),
        reply_markup=join_keyboard()
    )


# =========================
# Check Join
# =========================

async def is_joined(bot, user_id, channel_id):

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

    except Exception as e:
        print("JOIN CHECK ERROR:", repr(e))
        return False


async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    missing = []

    for channel in CHANNELS:

        joined = await is_joined(
            context.bot,
            user_id,
            channel["id"]
        )

        if not joined:
            missing.append(channel)

    if missing:

        names = ", ".join(
            channel["name"] for channel in missing
        )

        await query.answer(
            f"❌ Join မလုပ်ရသေးတာ: {names}",
            show_alert=True
        )

        return

    movie_id = context.user_data.get("movie_id")

    if not movie_id:

        await query.message.reply_text(
            "⚠️ Movie ID မပါသေးပါ။"
        )

        return

    if not CONTENT_CHANNEL:

        await query.message.reply_text(
            "⚠️ CONTENT_CHANNEL မသတ်မှတ်ရသေးပါ။"
        )

        return

    try:

        await context.bot.copy_message(
            chat_id=user_id,
            from_chat_id=CONTENT_CHANNEL,
            message_id=movie_id
        )

        await query.message.reply_text(
            "🎬 Movie ကို ပို့ပေးလိုက်ပါပြီ။"
        )

    except Exception as e:

        print("COPY ERROR:", repr(e))

        await query.message.reply_text(
            "❌ Movie ပို့မရသေးပါ။\n\n"
            "Content Channel ထဲမှာ Bot ကို Admin ထည့်ထားခြင်းရှိ/မရှိ စစ်ပေးပါ။"
        )


# =========================
# /link
# =========================

async def make_link(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if not ADMIN_ID or str(user_id) != str(ADMIN_ID):

        await update.message.reply_text(
            "❌ ဒီ command ကို Admin သာ အသုံးပြုနိုင်ပါတယ်။"
        )

        return

    if not context.args:

        await update.message.reply_text(
            "အသုံးပြုပုံ:\n\n"
            "/link POST_ID\n\n"
            "ဥပမာ:\n"
            "/link 123"
        )

        return

    post_id = context.args[0]

    if not post_id.isdigit():

        await update.message.reply_text(
            "❌ POST_ID ကို ဂဏန်းနဲ့ပဲ ထည့်ပါ။\n\n"
            "ဥပမာ: /link 123"
        )

        return

    me = await context.bot.get_me()

    bot_link = (
        f"https://t.me/{me.username}?start=movie_{post_id}"
    )

    await update.message.reply_text(
        "✅ Movie Bot Link ပြီးပါပြီ!\n\n"
        f"🎬 Post ID: {post_id}\n\n"
        f"🔗 {bot_link}\n\n"
        "ဒီ Link ကို User တွေကို ပေးနိုင်ပါပြီ။"
    )


# =========================
# Main
# =========================

def main():

    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is missing!")

    threading.Thread(
        target=run_web,
        daemon=True
    ).start()

    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    application.add_handler(
        CommandHandler("start", start)
    )

    application.add_handler(
        CommandHandler("link", make_link)
    )

    application.add_handler(
        CallbackQueryHandler(
            check_join,
            pattern="^check_join$"
        )
    )

    print("Bot is running...")

    application.run_polling()


if __name__ == "__main__":
    main()


import os
import logging
import threading
from flask import Flask

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
            "name": f"Channel {i}",
        })

web_app = Flask(__name__)

@web_app.route("/")
def home():
    return "KyawEiBot is running!"

def run_web():
    port = int(os.getenv("PORT", "10000"))
    web_app.run(host="0.0.0.0", port=port)

def join_keyboard():
    buttons = []
    for channel in CHANNELS:
        buttons.append([
            InlineKeyboardButton(
                f"🔗 JOIN {channel['name']}",
                url=channel["link"],
            )
        ])

    buttons.append([
        InlineKeyboardButton(
            "✅ CHECK JOIN",
            callback_data="check_join",
        )
    ])
    return InlineKeyboardMarkup(buttons)

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    movie_id = None

    # Read the movie ID from /start movie_8
    if context.args:
        payload = context.args[0]
        if payload.startswith("movie_"):
            value = payload[len("movie_"):]
            if value.isdigit():
                movie_id = int(value)
                context.user_data["movie_id"] = movie_id

    logger.info(
        "START received: user=%s args=%s movie_id=%s",
        update.effective_user.id,
        context.args,
        movie_id,
    )

    text = (
        "🎬 Welcome to KyawEiBot!\n\n"
        "Movie ရယူရန် Channel ၆ ခုလုံး Join လုပ်ပါ။\n"
        "Join ပြီးရင် CHECK JOIN ကိုနှိပ်ပါ။"
    )

    if movie_id:
        text += f"\n\n🎞 Movie ID: {movie_id}"

    await update.effective_message.reply_text(
        text,
        reply_markup=join_keyboard(),
    )

async def check_join(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query
    user_id = query.from_user.id
    missing = []

    for channel in CHANNELS:
        try:
            member = await context.bot.get_chat_member(
                chat_id=channel["id"],
                user_id=user_id,
            )

            if (
                member.status in ("left", "kicked")
                or (
                    member.status == "restricted"
                    and not getattr(member, "is_member", False)
                )
            ):
                missing.append(channel["name"])

        except Exception:
            logger.exception(
                "JOIN CHECK ERROR for %s", channel["name"]
            )
            missing.append(channel["name"])

    if missing:
        await query.answer(
            "❌ Join လုပ်ရန်ကျန်နေသော Channel: "
            + ", ".join(missing),
            show_alert=True,
        )
        return

    movie_id = context.user_data.get("movie_id")

    if not movie_id:
        await query.answer(
            "Movie Link ကနေ ပြန်ဝင်ပေးပါ။",
            show_alert=True,
        )
        await query.message.reply_text(
            "⚠️ Movie ID မရှိသေးပါ။\n\n"
            "သက်ဆိုင်ရာ Movie Bot Link ကို ပြန်ဖွင့်ပြီး "
            "START ကိုနှိပ်ပါ။"
        )
        return

    if not CONTENT_CHANNEL:
        await query.answer(
            "CONTENT_CHANNEL မသတ်မှတ်ရသေးပါ။",
            show_alert=True,
        )
        return

    await query.answer("✅ Join စစ်ဆေးပြီးပါပြီ!")

    try:
        await context.bot.copy_message(
            chat_id=user_id,
            from_chat_id=CONTENT_CHANNEL,
            message_id=movie_id,
        )
        await query.message.reply_text(
            "🎬 Movie Post ပို့ပေးပြီးပါပြီ။"
        )

    except Exception:
        logger.exception("MOVIE COPY ERROR")
        await query.message.reply_text(
            "❌ Movie Post ပို့မရပါ။\n\n"
            "CONTENT_CHANNEL နဲ့ Post ID မှန်မမှန်၊ "
            "Bot က Content Channel ကို ဝင်ကြည့်နိုင်မနိုင် "
            "စစ်ပေးပါ။"
        )

async def make_link(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    user_id = update.effective_user.id

    if not ADMIN_ID or str(user_id) != str(ADMIN_ID):
        await update.effective_message.reply_text(
            "❌ ဒီ Command ကို Admin သာ အသုံးပြုနိုင်ပါတယ်။"
        )
        return

    if not context.args or not context.args[0].isdigit():
        await update.effective_message.reply_text(
            "အသုံးပြုပုံ:\n/link POST_ID\n\nဥပမာ:\n/link 8"
        )
        return

    post_id = context.args[0]
    bot_info = await context.bot.get_me()
    link = (
        f"https://t.me/{bot_info.username}"
        f"?start=movie_{post_id}"
    )

    await update.effective_message.reply_text(
        "✅ Movie Bot Link ပြီးပါပြီ!\n\n"
        f"🎬 Post ID: {post_id}\n\n"
        f"🔗 {link}"
    )

async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE,
):
    logger.error(
        "BOT ERROR",
        exc_info=context.error,
    )

def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is missing!")

    threading.Thread(
        target=run_web,
        daemon=True,
    ).start()

    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("link", make_link))
    application.add_handler(
        CallbackQueryHandler(
            check_join,
            pattern="^check_join$",
        )
    )
    application.add_error_handler(error_handler)

    logger.info("KyawEiBot is starting...")
    application.run_polling()

if __name__ == "__main__":
    main()
        

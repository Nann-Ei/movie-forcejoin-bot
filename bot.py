import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
MOVIE_LINK = os.getenv("MOVIE_LINK")

CHANNELS = [
    {
        "id": os.getenv("CHANNEL_1"),
        "link": os.getenv("CHANNEL_1_LINK"),
        "name": "Channel 1"
    },
    {
        "id": os.getenv("CHANNEL_2"),
        "link": os.getenv("CHANNEL_2_LINK"),
        "name": "Channel 2"
    },
    {
        "id": os.getenv("CHANNEL_3"),
        "link": os.getenv("CHANNEL_3_LINK"),
        "name": "Channel 3"
    },
    {
        "id": os.getenv("CHANNEL_4"),
        "link": os.getenv("CHANNEL_4_LINK"),
        "name": "Channel 4"
    },
    {
        "id": os.getenv("CHANNEL_5"),
        "link": os.getenv("CHANNEL_5_LINK"),
        "name": "Channel 5"
    },
    {
        "id": os.getenv("CHANNEL_6"),
        "link": os.getenv("CHANNEL_6_LINK"),
        "name": "Channel 6"
    }
]


async def check_member(bot, user_id, channel_id):
    try:
        member = await bot.get_chat_member(
            chat_id=channel_id,
            user_id=user_id
        )

        return member.status in [
            "member",
            "administrator",
            "creator"
        ]

    except Exception:
        return False


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
            "✅ I JOINED / CHECK",
            callback_data="check_join"
        )
    ])

    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 MOVIE ရယူရန်\n\n"
        "အောက်က Channel ၆ ခုလုံးကို Join လုပ်ပေးပါ။\n\n"
        "Join ပြီးရင် ✅ I JOINED / CHECK ကိုနှိပ်ပါ။",
        reply_markup=join_keyboard()
    )


async def check_join(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    not_joined = []

    for i, channel in enumerate(CHANNELS, start=1):
        joined = await check_member(
            context.bot,
            user_id,
            channel["id"]
        )

        if not joined:
            not_joined.append(i)

    if not not_joined:

        keyboard = [[
            InlineKeyboardButton(
                "🎬 WATCH MOVIE",
                url=MOVIE_LINK
            )
        ]]

        await query.edit_message_text(
            "✅ Channel ၆ ခုလုံး Join ထားပါတယ်။\n\n"
            "🎬 Movie ကြည့်နိုင်ပါပြီ။",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    else:

        missing = ", ".join(
            [f"Channel {x}" for x in not_joined]
        )

        await query.answer(
            f"❌ မ Join ရသေးပါ: {missing}",
            show_alert=True
        )


def main():

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CallbackQueryHandler(
            check_join,
            pattern="^check_join$"
        )
    )

    app.run_polling()


if __name__ == "__main__":
    main()

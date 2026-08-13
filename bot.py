import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

# နောက်ပိုင်းမှာ Channel ID ၂ ခု ထည့်မယ်
CHANNEL_1 = os.getenv("CHANNEL_1")
CHANNEL_2 = os.getenv("CHANNEL_2")

# Join ပြီးရင် ပြမယ့် Movie Link
MOVIE_LINK = os.getenv("MOVIE_LINK")


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
    keyboard = [
        [
            InlineKeyboardButton(
                "🔽 JOIN CHANNEL 1 🔽",
                url=os.getenv("CHANNEL_1_LINK")
            )
        ],
        [
            InlineKeyboardButton(
                "🔽 JOIN CHANNEL 2 🔽",
                url=os.getenv("CHANNEL_2_LINK")
            )
        ],
        [
            InlineKeyboardButton(
                "✅ I JOINED / CHECK",
                callback_data="check_join"
            )
        ]
    ]

    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 Movie ကြည့်ရန်အတွက်\n\n"
        "အောက်က Channel ၂ ခုလုံးကို Join လုပ်ပေးပါ။\n\n"
        "Join ပြီးရင် ✅ I JOINED / CHECK ကိုနှိပ်ပါ။",
        reply_markup=join_keyboard()
    )


async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    joined_1 = await check_member(
        context.bot,
        user_id,
        CHANNEL_1
    )

    joined_2 = await check_member(
        context.bot,
        user_id,
        CHANNEL_2
    )

    if joined_1 and joined_2:
        keyboard = [
            [
                InlineKeyboardButton(
                    "🎬 WATCH MOVIE 🎬",
                    url=MOVIE_LINK
                )
            ]
        ]

        await query.edit_message_text(
            "✅ Channel ၂ ခုလုံး Join ထားပါတယ်။\n\n"
            "🎬 အခု Movie ကို ကြည့်နိုင်ပါပြီ။",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    else:
        await query.answer(
            "❌ Channel ၂ ခုလုံး Join လုပ်ထားတာ မတွေ့သေးပါဘူး။",
            show_alert=True
        )


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        CallbackQueryHandler(
            check_join,
            pattern="^check_join$"
        )
    )

    app.run_polling()


if __name__ == "__main__":
    main()

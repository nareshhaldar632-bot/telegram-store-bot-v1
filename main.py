import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

from config import BOT_TOKEN, ADMIN_ID, QR_IMAGE, CHANNEL_URL
from database import create_tables, add_user

logging.basicConfig(level=logging.INFO)


PRODUCTS = [
    "APK MC PANEL",
    "BR MOD",
    "DRIPCLIENT",
    "KOS",
    "NEO STRIKE",
    "PATO TEAM",
    "PRIME HOOK",
    "REAPER X PRO",
    "FLUORITE",
    "HIKARI MOD",
    "IOS CLOUD"
]

DURATIONS = {
    "1 Day": 60,
    "3 Days": 100,
    "7 Days": 150,
    "10 Days": 190,
    "15 Days": 300,
    "30 Days": 500
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    add_user(
        user.id,
        user.username,
        user.first_name
    )

    keyboard = [
        [InlineKeyboardButton("🛒 Products", callback_data="products")],
        [InlineKeyboardButton("📞 Contact Admin", url="https://t.me/YOUR_USERNAME")],
        [InlineKeyboardButton("📢 Join Channel", url=CHANNEL_URL)]
    ]

    await update.message.reply_text(
        "🔥 Welcome to Nandu Global Key Store 🔥\n\nSelect Option:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "products":

        buttons = []

        for p in PRODUCTS:
            buttons.append(
                [InlineKeyboardButton(p, callback_data=p)]
            )

        await query.edit_message_text(
            "Select Product:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    elif query.data in PRODUCTS:

        buttons = []

        for d, price in DURATIONS.items():
            buttons.append(
                [InlineKeyboardButton(
                    f"{d} - ₹{price}",
                    callback_data=f"{query.data}|{d}"
                )]
            )

        await query.edit_message_text(
            f"Product: {query.data}\n\nSelect Duration:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    elif "|" in query.data:

        product, duration = query.data.split("|")

        await query.message.reply_photo(
            photo=QR_IMAGE,
            caption=(
                f"Product: {product}\n"
                f"Duration: {duration}\n"
                f"Amount: ₹{DURATIONS[duration]}\n\n"
                "Payment karke UTR number bheje."
            )
        )


async def main():

    create_tables()

if __name__ == "__main__":
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    print("Bot Started")

    app.run_polling()

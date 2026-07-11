import logging
import uuid

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from config import BOT_TOKEN, ADMIN_ID, QR_IMAGE, CHANNEL_URL, UPI_ID
from database import create_tables, add_user, add_order
from products import PRODUCTS, DURATIONS


logging.basicConfig(level=logging.INFO)

user_orders = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    add_user(
        user.id,
        user.username,
        user.first_name
    )

    keyboard = [
        [InlineKeyboardButton("🛒 Products", callback_data="products")],
        [InlineKeyboardButton("📢 Join Channel", url=CHANNEL_URL)]
    ]

    await update.message.reply_text(
        "🔥 Welcome to Nandu Global Key Store 🔥",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
            
    query = update.callback_query
    await query.answer()

if query.data.startswith("approve_"):
    await query.message.reply_text("✅ Order Approved")
    return

elif query.data.startswith("reject_"):
    await query.message.reply_text("❌ Order Rejected")
    return

    if query.data == "products":

        buttons = []
        
        for product in PRODUCTS:
            buttons.append(
                [InlineKeyboardButton(
                    product["name"],
                    callback_data=f"product_{product['id']}"
                )]
            )

        await query.edit_message_text(
            "🛒 Select Product:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )


    elif query.data.startswith("product_"):

        product_id = query.data.replace("product_", "")

        user_orders[query.from_user.id] = {
            "product": product_id
        }

        buttons = []

        for duration, price in DURATIONS.items():
            buttons.append(
                [InlineKeyboardButton(
                    f"{duration} - ₹{price}",
                    callback_data=f"buy_{duration}"
                )]
            )

        await query.edit_message_text(
            "Select Duration:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )


    elif query.data.startswith("buy_"):

        duration = query.data.replace("buy_", "")

        data = user_orders.get(query.from_user.id)

        if not data:
            await query.message.reply_text("Please select product again.")
            return


        data["duration"] = duration
        data["amount"] = DURATIONS[duration]

        user_orders[query.from_user.id] = data


        await query.message.reply_photo(
            photo=QR_IMAGE,
            caption=(
                f"💳 Payment Details\n\n"
                f"Product: {data['product']}\n"
                f"Duration: {duration}\n"
                f"Amount: ₹{data['amount']}\n\n"
                f"UPI: {UPI_ID}\n\n"
                "Payment ke baad UTR number bheje."
            )
        )


async def utr_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    if user.id not in user_orders:
        return


    utr = update.message.text

    data = user_orders[user.id]

    order_id = str(uuid.uuid4())[:8]


    add_order(
        order_id,
        user.id,
        data["product"],
        data["duration"],
        data["amount"],
        utr
    )


    await update.message.reply_text(
        f"✅ Order Submitted\n\n"
        f"Order ID: {order_id}\n"
        f"Status: Pending"
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "✅ Approve",
                callback_data=f"approve_{order_id}_{user.id}"
            ),
            InlineKeyboardButton(
                "❌ Reject",
                callback_data=f"reject_{order_id}_{user.id}"
            )
        ]
    ]

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            f"🔔 New Order\n\n"
            f"Order ID: {order_id}\n"
            f"User: {user.id}\n"
            f"Product: {data['product']}\n"
            f"Duration: {data['duration']}\n"
            f"Amount: ₹{data['amount']}\n"
            f"UTR: {utr}"
        ),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


def main():

    create_tables()

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            utr_handler
        )
    )


    print("Bot Started")

    app.run_polling()


if __name__ == "__main__":
    main()

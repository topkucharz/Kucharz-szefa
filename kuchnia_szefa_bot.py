
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.environ.get("TOKEN")
ADMIN_CHAT_ID = 7667536346

produkty = {
    "Blueberry": [60, 120, 150, 200],
    "Strawberry Mohito": [60, 120, 150, 200],
    "Cherry Berry": [60, 120, 150, 200],
    "Banana Haze": [60, 120, 150, 200],
    "Cherry Kush": [60, 120, 150, 200],
    "Ghost OG": [60, 120, 150, 200]
}

ilosci = ["1g", "2g", "3g", "5g"]
platnosci = ["Gotówka", "BLIK"]
odbior = ["H2H", "Uberpaka", "Skrytka"]

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(nazwa, callback_data=nazwa)] for nazwa in produkty]
    await update.message.reply_text("Wybierz produkt:", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id

    if chat_id not in user_data:
        user_data[chat_id] = {}

    step = user_data[chat_id].get("step", "produkt")

    if step == "produkt":
        user_data[chat_id]["produkt"] = query.data
        user_data[chat_id]["step"] = "ilosc"
        keyboard = [[InlineKeyboardButton(i, callback_data=i)] for i in ilosci]
        await query.edit_message_text("Wybierz ilość:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif step == "ilosc":
        user_data[chat_id]["ilosc"] = query.data
        user_data[chat_id]["step"] = "platnosc"
        keyboard = [[InlineKeyboardButton(p, callback_data=p)] for p in platnosci]
        await query.edit_message_text("Wybierz metodę płatności:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif step == "platnosc":
        user_data[chat_id]["platnosc"] = query.data
        user_data[chat_id]["step"] = "odbior"
        keyboard = [[InlineKeyboardButton(o, callback_data=o)] for o in odbior]
        await query.edit_message_text("Wybierz metodę odbioru:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif step == "odbior":
        user_data[chat_id]["odbior"] = query.data
        dane = user_data[chat_id]
        produkt = dane["produkt"]
        ilosc_index = ilosci.index(dane["ilosc"])
        cena = produkty[produkt][ilosc_index]

        tekst = (
            f"**Nowe zamówienie**\n"
            f"Produkt: {produkt}\n"
            f"Ilość: {dane['ilosc']} – {cena} zł\n"
            f"Płatność: {dane['platnosc']}\n"
            f"Odbiór: {dane['odbior']}\n"
            f"Użytkownik: @{query.from_user.username or 'brak'}"
        )

        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=tekst)
        await query.edit_message_text("Zamówienie przyjęte! Szef się odezwie.")

        del user_data[chat_id]

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(handle_selection))

app.run_polling()

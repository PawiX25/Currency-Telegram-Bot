from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters
import re
from decimal import Decimal
import requests
from datetime import datetime, timedelta

TELEGRAM_TOKEN = "YOUR_TELEGRAM"

rates_cache = {"timestamp": None, "rates": None}

async def get_rates():
    if (rates_cache["timestamp"] and 
        datetime.now() - rates_cache["timestamp"] < timedelta(hours=1) and 
        rates_cache["rates"]):
        return rates_cache["rates"]
    
    try:
        response = requests.get("https://api.exchangerate-api.com/v4/latest/EUR")
        data = response.json()
        rates_cache["rates"] = data["rates"]
        rates_cache["timestamp"] = datetime.now()
        return rates_cache["rates"]
    except Exception as e:
        print(f"Error fetching rates: {e}")
        return None

async def convert_currency(amount: Decimal, from_currency: str, rates: dict) -> list:
    if not rates:
        return []
    
    conversions = []
    if from_currency == "EUR":
        base_amount = amount
    else:
        eur_rate = Decimal(1) / Decimal(str(rates[from_currency]))
        base_amount = amount * eur_rate
    
    if from_currency == "PLN":
        conversions.append(f"€{base_amount:.2f}")
        usd_amount = base_amount * Decimal(str(rates['USD']))
        conversions.append(f"{usd_amount:.2f} USD")
    elif from_currency == "EUR":
        pln_amount = base_amount * Decimal(str(rates['PLN']))
        conversions.append(f"{pln_amount:.2f} PLN")
        usd_amount = base_amount * Decimal(str(rates['USD']))
        conversions.append(f"{usd_amount:.2f} USD")
    elif from_currency == "USD":
        conversions.append(f"€{base_amount:.2f}")
        pln_amount = base_amount * Decimal(str(rates['PLN']))
        conversions.append(f"{pln_amount:.2f} PLN")
    
    return conversions

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi! I'll help convert currencies. Just mention an amount like '10 PLN' in the chat."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    author = update.message.from_user.first_name
    
    pattern = r'(\d+(?:\.\d+)?)\s*(PLN|EUR|USD|pln|eur|usd)'
    matches = re.finditer(pattern, text)
    
    if not matches:
        return
    
    rates = await get_rates()
    if not rates:
        await update.message.reply_text("Sorry, couldn't fetch exchange rates")
        return

    new_text = text
    replacements = []
    
    for match in re.finditer(pattern, text):
        amount_str, currency = match.groups()
        amount = Decimal(str(amount_str))
        currency = currency.upper()
        
        if currency == "PLN":
            eur_rate = Decimal(1) / Decimal(str(rates['PLN']))
            converted = amount * eur_rate
            replacements.append((match.group(), f"{converted:.2f} EUR"))
        elif currency == "EUR":
            pln_rate = Decimal(str(rates['PLN']))
            converted = amount * pln_rate
            replacements.append((match.group(), f"{converted:.2f} PLN"))
        elif currency == "USD":
            eur_rate = Decimal(1) / Decimal(str(rates['USD']))
            converted = amount * eur_rate
            replacements.append((match.group(), f"{converted:.2f} EUR"))
    
    for old, new in reversed(replacements):
        new_text = new_text.replace(old, new)
    
    if new_text != text:
        await update.message.reply_text(
            f"{author}: {new_text}",
            reply_to_message_id=update.message.message_id
        )

def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    application.run_polling()

if __name__ == "__main__":
    main()

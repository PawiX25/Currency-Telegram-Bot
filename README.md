# Currency Convert Telegram Bot

A Telegram bot that automatically detects and converts currency amounts in group chat messages. When users mention amounts in PLN, EUR, or USD, the bot replies with converted values.

## Features

- Real-time currency conversion
- Supports PLN, EUR, and USD
- Replies to original messages with conversions
- Uses free exchange rate API
- Caches exchange rates to prevent API abuse

## Setup

1. Install requirements:
```bash
pip install -r requirements.txt
```

2. Configure bot token:
- Get a bot token from [@BotFather](https://t.me/botfather)
- Replace `TELEGRAM_TOKEN` in `main.py`

3. Run the bot:
```bash
python main.py
```

## Usage

Simply add the bot to your group chat and mention currency amounts:
- "I bought a phone for 1200 PLN"
- Bot replies: "John: I bought a phone for 276.00 EUR"

## Exchange Rates

Uses the free API from exchangerate-api.com with hourly rate caching.

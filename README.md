# Currency Convert Telegram Bot

A Telegram bot that automatically detects and converts currency amounts in group chat messages. Supports over 150 world currencies and major cryptocurrencies.

## Features

- Real-time currency and cryptocurrency conversion
- Automatic detection of currency amounts in messages
- Direct conversion between any two supported currencies
- Default currency preferences for each user
- Supports 150+ fiat currencies and major cryptocurrencies (BTC, ETH, etc.)
- Uses free exchange rate APIs with hourly rate caching
- Multiple conversion formats supported

## Setup

1. Install requirements:
```bash
pip install -r requirements.txt
```

2. Configure bot token:
- Get a bot token from [@BotFather](https://t.me/botfather)
- Set environment variable: `TELEGRAM_TOKEN`

3. Run the bot:
```bash
python main.py
```

## Usage

### Basic Commands
- `/start` - Start the bot
- `/help` - Show help message
- `/currencies` - List all supported currencies
- `/rate FROM TO` - Check exchange rate between currencies
- `/setdefault FROM TO` - Set your default currencies
- `/getdefault` - View your default currencies

### Conversion Examples
- Simple conversion: "100 USD" or "50 £" or "0.5 BTC"
- Direct conversion: "100 USD to JPY" or "1 BTC in ETH"
- Multiple conversions: "I have 100 USD and 0.1 BTC"
- Using symbols: "€50" or "$100" or "£75"

### Supported Cryptocurrencies
- Bitcoin (BTC)
- Ethereum (ETH)
- Tether (USDT)
- Binance Coin (BNB)
- XRP
- Cardano (ADA)
- Dogecoin (DOGE)
- Solana (SOL)
- Polkadot (DOT)
- USD Coin (USDC)

## APIs Used
- Exchange rates: exchangerate-api.com
- Crypto rates: api.coingecko.com

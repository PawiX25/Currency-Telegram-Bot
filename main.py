import os
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters
import re
from decimal import Decimal
import aiohttp
from datetime import datetime, timedelta
import logging

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

currency_synonyms = {
    # Euro (EUR)
    "eur": "EUR", "€": "EUR", "euro": "EUR", "euros": "EUR",
    
    # United Arab Emirates Dirham (AED)
    "aed": "AED", "uae dirham": "AED", "emirati dirham": "AED",
    
    # Afghan Afghani (AFN)
    "afn": "AFN", "afghan afghani": "AFN", "afghani": "AFN",
    
    # Albanian Lek (ALL)
    "all": "ALL", "albanian lek": "ALL", "lek": "ALL",
    
    # Armenian Dram (AMD)
    "amd": "AMD", "armenian dram": "AMD", "dram": "AMD",
    
    # Netherlands Antillean Guilder (ANG)
    "ang": "ANG", "antillean guilder": "ANG", "netherlands antillean guilder": "ANG", "ƒ": "ANG",
    
    # Angolan Kwanza (AOA)
    "aoa": "AOA", "angolan kwanza": "AOA", "kwanza": "AOA",
    
    # Argentine Peso (ARS)
    "ars": "ARS", "argentine peso": "ARS", "peso argentino": "ARS",
    
    # Australian Dollar (AUD)
    "aud": "AUD", "australian dollar": "AUD", "aussie dollar": "AUD", "a$": "AUD",
    
    # Aruban Florin (AWG)
    "awg": "AWG", "aruban florin": "AWG", "ƒ": "AWG",
    
    # Azerbaijani Manat (AZN)
    "azn": "AZN", "azerbaijani manat": "AZN", "manat": "AZN",
    
    # Bosnia and Herzegovina Convertible Mark (BAM)
    "bam": "BAM", "bosnia-herzegovina convertible mark": "BAM", "convertible mark": "BAM",
    
    # Barbadian Dollar (BBD)
    "bbd": "BBD", "barbadian dollar": "BBD", "bds$": "BBD",
    
    # Bangladeshi Taka (BDT)
    "bdt": "BDT", "bangladeshi taka": "BDT", "taka": "BDT",
    
    # Bulgarian Lev (BGN)
    "bgn": "BGN", "bulgarian lev": "BGN", "lev": "BGN",
    
    # Bahraini Dinar (BHD)
    "bhd": "BHD", "bahraini dinar": "BHD",
    
    # Burundian Franc (BIF)
    "bif": "BIF", "burundian franc": "BIF",
    
    # Bermudian Dollar (BMD)
    "bmd": "BMD", "bermudian dollar": "BMD",
    
    # Brunei Dollar (BND)
    "bnd": "BND", "brunei dollar": "BND",
    
    # Bolivian Boliviano (BOB)
    "bob": "BOB", "bolivian boliviano": "BOB", "boliviano": "BOB",
    
    # Brazilian Real (BRL)
    "brl": "BRL", "brazilian real": "BRL", "real": "BRL", "reais": "BRL", "r$": "BRL",
    
    # Bahamian Dollar (BSD)
    "bsd": "BSD", "bahamian dollar": "BSD",
    
    # Bhutanese Ngultrum (BTN)
    "btn": "BTN", "bhutanese ngultrum": "BTN", "ngultrum": "BTN",
    
    # Botswanan Pula (BWP)
    "bwp": "BWP", "botswanan pula": "BWP", "pula": "BWP",
    
    # Belarusian Ruble (BYN)
    "byn": "BYN", "belarusian ruble": "BYN",
    
    # Belize Dollar (BZD)
    "bzd": "BZD", "belize dollar": "BZD",
    
    # Canadian Dollar (CAD)
    "cad": "CAD", "canadian dollar": "CAD", "c$": "CAD",
    
    # Congolese Franc (CDF)
    "cdf": "CDF", "congolese franc": "CDF",
    
    # Swiss Franc (CHF)
    "chf": "CHF", "swiss franc": "CHF",
    
    # Chilean Peso (CLP)
    "clp": "CLP", "chilean peso": "CLP",
    
    # Chinese Yuan Renminbi (CNY)
    "cny": "CNY", "chinese yuan": "CNY", "yuan": "CNY", "renminbi": "CNY", "rmb": "CNY", "¥": "CNY",
    
    # Colombian Peso (COP)
    "cop": "COP", "colombian peso": "COP",
    
    # Costa Rican Colón (CRC)
    "crc": "CRC", "costa rican colón": "CRC", "colón": "CRC",
    
    # Cuban Peso (CUP)
    "cup": "CUP", "cuban peso": "CUP",
    
    # Cape Verdean Escudo (CVE)
    "cve": "CVE", "cape verdean escudo": "CVE",
    
    # Czech Koruna (CZK)
    "czk": "CZK", "czech koruna": "CZK", "koruna": "CZK",
    
    # Djiboutian Franc (DJF)
    "djf": "DJF", "djiboutian franc": "DJF",
    
    # Danish Krone (DKK)
    "dkk": "DKK", "danish krone": "DKK",
    
    # Dominican Peso (DOP)
    "dop": "DOP", "dominican peso": "DOP",
    
    # Algerian Dinar (DZD)
    "dzd": "DZD", "algerian dinar": "DZD",
    
    # Egyptian Pound (EGP)
    "egp": "EGP", "egyptian pound": "EGP",
    
    # Eritrean Nakfa (ERN)
    "ern": "ERN", "eritrean nakfa": "ERN", "nakfa": "ERN",
    
    # Ethiopian Birr (ETB)
    "etb": "ETB", "ethiopian birr": "ETB",
    
    # Fijian Dollar (FJD)
    "fjd": "FJD", "fijian dollar": "FJD",
    
    # Falkland Islands Pound (FKP)
    "fkp": "FKP", "falkland islands pound": "FKP",
    
    # Faroese Króna (FOK)
    "fok": "FOK", "faroese króna": "FOK",
    
    # British Pound Sterling (GBP)
    "gbp": "GBP", "british pound": "GBP", "pound sterling": "GBP", "£": "GBP", "quid": "GBP",
    
    # Georgian Lari (GEL)
    "gel": "GEL", "georgian lari": "GEL", "lari": "GEL",
    
    # Guernsey Pound (GGP)
    "ggp": "GGP", "guernsey pound": "GGP",
    
    # Ghanaian Cedi (GHS)
    "ghs": "GHS", "ghanaian cedi": "GHS", "cedi": "GHS",
    
    # Gibraltar Pound (GIP)
    "gip": "GIP", "gibraltar pound": "GIP",
    
    # Gambian Dalasi (GMD)
    "gmd": "GMD", "gambian dalasi": "GMD", "dalasi": "GMD",
    
    # Guinean Franc (GNF)
    "gnf": "GNF", "guinean franc": "GNF",
    
    # Guatemalan Quetzal (GTQ)
    "gtq": "GTQ", "guatemalan quetzal": "GTQ", "quetzal": "GTQ",
    
    # Guyanese Dollar (GYD)
    "gyd": "GYD", "guyanese dollar": "GYD",
    
    # Hong Kong Dollar (HKD)
    "hkd": "HKD", "hong kong dollar": "HKD", "hk$": "HKD",
    
    # Honduran Lempira (HNL)
    "hnl": "HNL", "honduran lempira": "HNL", "lempira": "HNL",
    
    # Croatian Kuna (HRK)
    "hrk": "HRK", "croatian kuna": "HRK", "kuna": "HRK",
    
    # Haitian Gourde (HTG)
    "htg": "HTG", "haitian gourde": "HTG",
    
    # Hungarian Forint (HUF)
    "huf": "HUF", "hungarian forint": "HUF", "forint": "HUF",
    
    # Indonesian Rupiah (IDR)
    "idr": "IDR", "indonesian rupiah": "IDR", "rupiah": "IDR", "rp": "IDR",
    
    # Israeli New Shekel (ILS)
    "ils": "ILS", "israeli new shekel": "ILS", "shekel": "ILS", "₪": "ILS",
    
    # Manx Pound (IMP)
    "imp": "IMP", "manx pound": "IMP",
    
    # Indian Rupee (INR)
    "inr": "INR", "indian rupee": "INR", "rupee": "INR", "₹": "INR", "rs": "INR",
    
    # Iraqi Dinar (IQD)
    "iqd": "IQD", "iraqi dinar": "IQD",
    
    # Iranian Rial (IRR)
    "irr": "IRR", "iranian rial": "IRR",
    
    # Icelandic Króna (ISK)
    "isk": "ISK", "icelandic króna": "ISK", "króna (iceland)": "ISK",
    
    # Jersey Pound (JEP)
    "jep": "JEP", "jersey pound": "JEP",
    
    # Jamaican Dollar (JMD)
    "jmd": "JMD", "jamaican dollar": "JMD",
    
    # Jordanian Dinar (JOD)
    "jod": "JOD", "jordanian dinar": "JOD",
    
    # Japanese Yen (JPY)
    "jpy": "JPY", "japanese yen": "JPY", "yen": "JPY", "¥": "JPY",
    
    # Kenyan Shilling (KES)
    "kes": "KES", "kenyan shilling": "KES",
    
    # Kyrgyzstani Som (KGS)
    "kgs": "KGS", "kyrgyzstani som": "KGS",
    
    # Cambodian Riel (KHR)
    "khr": "KHR", "cambodian riel": "KHR", "riel": "KHR",
    
    # Kiribati Dollar (KID - same as AUD in practice)
    "kid": "KID", "kiribati dollar": "KID",
    
    # Comorian Franc (KMF)
    "kmf": "KMF", "comorian franc": "KMF",
    
    # South Korean Won (KRW)
    "krw": "KRW", "south korean won": "KRW", "won": "KRW", "₩": "KRW",
    
    # Kuwaiti Dinar (KWD)
    "kwd": "KWD", "kuwaiti dinar": "KWD",
    
    # Cayman Islands Dollar (KYD)
    "kyd": "KYD", "cayman islands dollar": "KYD",
    
    # Kazakhstani Tenge (KZT)
    "kzt": "KZT", "kazakhstani tenge": "KZT", "tenge": "KZT",
    
    # Lao Kip (LAK)
    "lak": "LAK", "lao kip": "LAK", "kip": "LAK",
    
    # Lebanese Pound (LBP)
    "lbp": "LBP", "lebanese pound": "LBP",
    
    # Sri Lankan Rupee (LKR)
    "lkr": "LKR", "sri lankan rupee": "LKR",
    
    # Liberian Dollar (LRD)
    "lrd": "LRD", "liberian dollar": "LRD",
    
    # Lesotho Loti (LSL)
    "lsl": "LSL", "lesotho loti": "LSL",
    
    # Libyan Dinar (LYD)
    "lyd": "LYD", "libyan dinar": "LYD",
    
    # Moroccan Dirham (MAD)
    "mad": "MAD", "moroccan dirham": "MAD",
    
    # Moldovan Leu (MDL)
    "mdl": "MDL", "moldovan leu": "MDL",
    
    # Malagasy Ariary (MGA)
    "mga": "MGA", "malagasy ariary": "MGA", "ariary": "MGA",
    
    # Macedonian Denar (MKD)
    "mkd": "MKD", "macedonian denar": "MKD", "denar": "MKD",
    
    # Myanma Kyat (MMK)
    "mmk": "MMK", "myanmar kyat": "MMK", "kyat": "MMK",
    
    # Mongolian Tögrög (MNT)
    "mnt": "MNT", "mongolian tögrög": "MNT", "tögrög": "MNT", "tugrik": "MNT",
    
    # Macanese Pataca (MOP)
    "mop": "MOP", "macanese pataca": "MOP", "pataca": "MOP",
    
    # Mauritanian Ouguiya (MRU)
    "mru": "MRU", "mauritanian ouguiya": "MRU",
    
    # Mauritian Rupee (MUR)
    "mur": "MUR", "mauritian rupee": "MUR",
    
    # Maldivian Rufiyaa (MVR)
    "mvr": "MVR", "maldivian rufiyaa": "MVR", "rufiyaa": "MVR",
    
    # Malawian Kwacha (MWK)
    "mwk": "MWK", "malawian kwacha": "MWK",
    
    # Mexican Peso (MXN)
    "mxn": "MXN", "mexican peso": "MXN",
    
    # Malaysian Ringgit (MYR)
    "myr": "MYR", "malaysian ringgit": "MYR", "ringgit": "MYR",
    
    # Mozambican Metical (MZN)
    "mzn": "MZN", "mozambican metical": "MZN", "metical": "MZN",
    
    # Namibian Dollar (NAD)
    "nad": "NAD", "namibian dollar": "NAD",
    
    # Nigerian Naira (NGN)
    "ngn": "NGN", "nigerian naira": "NGN", "naira": "NGN",
    
    # Nicaraguan Córdoba (NIO)
    "nio": "NIO", "nicaraguan córdoba": "NIO",
    
    # Norwegian Krone (NOK)
    "nok": "NOK", "norwegian krone": "NOK",
    
    # Nepalese Rupee (NPR)
    "npr": "NPR", "nepalese rupee": "NPR",
    
    # New Zealand Dollar (NZD)
    "nzd": "NZD", "new zealand dollar": "NZD", "kiwi dollar": "NZD",
    
    # Omani Rial (OMR)
    "omr": "OMR", "omani rial": "OMR",
    
    # Panamanian Balboa (PAB)
    "pab": "PAB", "panamanian balboa": "PAB", "balboa": "PAB",
    
    # Peruvian Sol (PEN)
    "pen": "PEN", "peruvian sol": "PEN", "sol": "PEN",
    
    # Papua New Guinean Kina (PGK)
    "pgk": "PGK", "papua new guinean kina": "PGK", "kina": "PGK",
    
    # Philippine Peso (PHP)
    "php": "PHP", "philippine peso": "PHP", "₱": "PHP",
    
    # Pakistani Rupee (PKR)
    "pkr": "PKR", "pakistani rupee": "PKR",
    
    # Polish Złoty (PLN)
    "pln": "PLN", "polish złoty": "PLN", "zł": "PLN", "zloty": "PLN", "złotych": "PLN",
    "zlotych": "PLN", "zlotys": "PLN",
    
    # Paraguayan Guarani (PYG)
    "pyg": "PYG", "paraguayan guarani": "PYG", "guarani": "PYG",
    
    # Qatari Riyal (QAR)
    "qar": "QAR", "qatari riyal": "QAR",
    
    # Romanian Leu (RON)
    "ron": "RON", "romanian leu": "RON",
    
    # Serbian Dinar (RSD)
    "rsd": "RSD", "serbian dinar": "RSD",
    
    # Russian Ruble (RUB)
    "rub": "RUB", "russian ruble": "RUB", "ruble": "RUB", "rouble": "RUB",
    
    # Rwandan Franc (RWF)
    "rwf": "RWF", "rwandan franc": "RWF",
    
    # Saudi Riyal (SAR)
    "sar": "SAR", "saudi riyal": "SAR",
    
    # Solomon Islands Dollar (SBD)
    "sbd": "SBD", "solomon islands dollar": "SBD",
    
    # Seychellois Rupee (SCR)
    "scr": "SCR", "seychellois rupee": "SCR",
    
    # Sudanese Pound (SDG)
    "sdg": "SDG", "sudanese pound": "SDG",
    
    # Swedish Krona (SEK)
    "sek": "SEK", "swedish krona": "SEK", "krona": "SEK",
    
    # Singapore Dollar (SGD)
    "sgd": "SGD", "singapore dollar": "SGD", "s$": "SGD",
    
    # Saint Helena Pound (SHP)
    "shp": "SHP", "saint helena pound": "SHP",
    
    # Sierra Leonean Leone (SLE)
    "sle": "SLE", "sierra leonean leone": "SLE",
    
    # Old Sierra Leonean Leone (SLL)
    "sll": "SLL", "old sierra leonean leone": "SLL",
    
    # Somali Shilling (SOS)
    "sos": "SOS", "somali shilling": "SOS",
    
    # Surinamese Dollar (SRD)
    "srd": "SRD", "surinamese dollar": "SRD",
    
    # South Sudanese Pound (SSP)
    "ssp": "SSP", "south sudanese pound": "SSP",
    
    # São Tomé and Príncipe Dobra (STN)
    "stn": "STN", "são tomé and príncipe dobra": "STN",
    
    # Syrian Pound (SYP)
    "syp": "SYP", "syrian pound": "SYP",
    
    # Eswatini Lilangeni (SZL)
    "szl": "SZL", "eswatini lilangeni": "SZL",
    
    # Thai Baht (THB)
    "thb": "THB", "thai baht": "THB", "baht": "THB", "฿": "THB",
    
    # Tajikistani Somoni (TJS)
    "tjs": "TJS", "tajikistani somoni": "TJS",
    
    # Turkmenistani Manat (TMT)
    "tmt": "TMT", "turkmenistani manat": "TMT",
    
    # Tunisian Dinar (TND)
    "tnd": "TND", "tunisian dinar": "TND",
    
    # Tongan Paʻanga (TOP)
    "top": "TOP", "tongan paʻanga": "TOP",
    
    # Turkish Lira (TRY)
    "try": "TRY", "turkish lira": "TRY", "₺": "TRY", "lira": "TRY",
    
    # Trinidad and Tobago Dollar (TTD)
    "ttd": "TTD", "trinidad and tobago dollar": "TTD",
    
    # Tuvaluan Dollar (TVD - often pegged to AUD)
    "tvd": "TVD", "tuvaluan dollar": "TVD",
    
    # New Taiwan Dollar (TWD)
    "twd": "TWD", "new taiwan dollar": "TWD", "nt$": "TWD",
    
    # Tanzanian Shilling (TZS)
    "tzs": "TZS", "tanzanian shilling": "TZS",
    
    # Ukrainian Hryvnia (UAH)
    "uah": "UAH", "ukrainian hryvnia": "UAH", "hryvnia": "UAH",
    
    # Ugandan Shilling (UGX)
    "ugx": "UGX", "ugandan shilling": "UGX",
    
    # US Dollar (USD)
    "usd": "USD", "us dollar": "USD", "$": "USD", "bucks": "USD", "greenbacks": "USD",
    
    # Uruguayan Peso (UYU)
    "uyu": "UYU", "uruguayan peso": "UYU",
    
    # Uzbekistani Som (UZS)
    "uzs": "UZS", "uzbekistani som": "UZS",
    
    # Venezuelan Bolívar (VES)
    "ves": "VES", "venezuelan bolívar": "VES", "bolívar": "VES",
    
    # Vietnamese Đồng (VND)
    "vnd": "VND", "vietnamese đồng": "VND", "đồng": "VND",
    
    # Vanuatu Vatu (VUV)
    "vuv": "VUV", "vanuatu vatu": "VUV", "vatu": "VUV",
    
    # Samoan Tālā (WST)
    "wst": "WST", "samoan tālā": "WST", "tālā": "WST",
    
    # Central African CFA Franc (XAF)
    "xaf": "XAF", "central african cfa franc": "XAF",
    
    # East Caribbean Dollar (XCD)
    "xcd": "XCD", "east caribbean dollar": "XCD",
    
    # Special Drawing Rights (XDR)
    "xdr": "XDR", "special drawing rights": "XDR", "imf sdr": "XDR",
    
    # West African CFA Franc (XOF)
    "xof": "XOF", "west african cfa franc": "XOF",
    
    # CFP Franc (XPF)
    "xpf": "XPF", "cfp franc": "XPF",
    
    # Yemeni Rial (YER)
    "yer": "YER", "yemeni rial": "YER",
    
    # South African Rand (ZAR)
    "zar": "ZAR", "south african rand": "ZAR", "rand": "ZAR",
    
    # Zambian Kwacha (ZMW)
    "zmw": "ZMW", "zambian kwacha": "ZMW",
    
    # Zimbabwean Dollar (ZWL)
    "zwl": "ZWL", "zimbabwean dollar": "ZWL"
}

currency_synonyms.update({
    # Cryptocurrencies
    "btc": "BTC", "bitcoin": "BTC", "₿": "BTC",
    "eth": "ETH", "ethereum": "ETH", "ether": "ETH",
    "usdt": "USDT", "tether": "USDT",
    "bnb": "BNB", "binance coin": "BNB",
    "xrp": "XRP", "ripple": "XRP",
    "ada": "ADA", "cardano": "ADA",
    "doge": "DOGE", "dogecoin": "DOGE",
    "sol": "SOL", "solana": "SOL",
    "dot": "DOT", "polkadot": "DOT",
    "usdc": "USDC", "usd coin": "USDC",
})

# Cache for exchange rates
rates_cache = {"timestamp": None, "rates": None}

user_preferences = {}

async def get_rates():
    if (rates_cache["timestamp"] and 
        datetime.now() - rates_cache["timestamp"] < timedelta(hours=1) and 
        rates_cache["rates"]):
        return rates_cache["rates"]
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.exchangerate-api.com/v4/latest/EUR") as response:
                data = await response.json()
                fiat_rates = data["rates"]
            
            async with session.get("https://api.coingecko.com/api/v3/simple/price", params={
                "ids": "bitcoin,ethereum,tether,binancecoin,ripple,cardano,dogecoin,solana,polkadot,usd-coin",
                "vs_currencies": "eur"
            }) as crypto_response:
                crypto_data = await crypto_response.json()
        
        crypto_mapping = {
            "bitcoin": "BTC",
            "ethereum": "ETH",
            "tether": "USDT",
            "binancecoin": "BNB",
            "ripple": "XRP",
            "cardano": "ADA",
            "dogecoin": "DOGE",
            "solana": "SOL",
            "polkadot": "DOT",
            "usd-coin": "USDC"
        }
        
        crypto_rates = {}
        for gecko_id, code in crypto_mapping.items():
            if gecko_id in crypto_data:
                crypto_rates[code] = 1 / crypto_data[gecko_id]["eur"]
        
        combined_rates = {**fiat_rates, **crypto_rates}
        rates_cache["rates"] = combined_rates
        rates_cache["timestamp"] = datetime.now()
        return combined_rates
        
    except Exception as e:
        logging.error(f"Error fetching rates: {e}")
        return None

async def normalize_currency(raw_cur: str):
    raw_cur = raw_cur.lower().strip()
    code = currency_synonyms.get(raw_cur)
    if not code:
        logging.warning(f"Currency not recognized: {raw_cur}")
    return code

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi! I'll help convert currencies. Just mention an amount and currency like '10 PLN' or '5 bucks' and I'll convert it to EUR."
    )

async def list_currencies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    unique_currencies = sorted(set(currency_synonyms.values()))
    message = "Supported currencies:\n\n" + ", ".join(unique_currencies)
    await update.message.reply_text(message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
Available commands:
/start - Start the bot
/help - Show this help message
/currencies - List all supported currencies
/rate FROM TO - Check exchange rate between two currencies
/setdefault FROM TO - Set default currencies for conversion
/getdefault - Get your default currencies

Usage examples:
- Simple conversion to EUR: "100 USD" or "50 £" or "0.5 BTC"
- Direct conversion: "100 USD to JPY" or "1 BTC in ETH"
- Multiple conversions in one message: "I have 100 USD and 0.1 BTC"
- Check rate: "/rate USD EUR" or "/rate BTC ETH"
- Set default currencies: "/setdefault USD EUR"
- Get default currencies: "/getdefault"

Supported cryptocurrencies: BTC, ETH, USDT, BNB, XRP, ADA, DOGE, SOL, DOT, USDC
"""
    await update.message.reply_text(help_text)

async def set_default(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 2:
        await update.message.reply_text(
            "Please use the format: /setdefault FROM TO\nExample: /setdefault USD EUR"
        )
        return
    from_cur = await normalize_currency(context.args[0])
    to_cur = await normalize_currency(context.args[1])
    if not from_cur or not to_cur:
        await update.message.reply_text(
            "Invalid currency codes. Use /currencies to see available options."
        )
        return
    user_id = update.message.from_user.id
    user_preferences[user_id] = {'from': from_cur, 'to': to_cur}
    await update.message.reply_text(
        f"Default currencies set to: {from_cur} to {to_cur}"
    )

async def get_default(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    prefs = user_preferences.get(user_id)
    if prefs:
        await update.message.reply_text(
            f"Your default currencies are: {prefs['from']} to {prefs['to']}"
        )
    else:
        await update.message.reply_text(
            "You have not set default currencies. Use /setdefault FROM TO to set them."
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    author = update.message.from_user.first_name
    
    direct_pattern = r'(\d+(?:\.\d+)?)\s*([^\s]+)\s+(?:to|in)\s+([^\s]+)'
    simple_pattern = r'(\d+(?:\.\d+)?)\s*([^\s]+)'
    
    direct_matches = list(re.finditer(direct_pattern, text))
    
    rates = await get_rates()
    if not rates:
        await update.message.reply_text("Sorry, couldn't fetch exchange rates at the moment.")
        return

    user_id = update.message.from_user.id
    prefs = user_preferences.get(user_id)
    if prefs:
        amount_pattern = r'(\d+(?:\.\d+)?)'
        matches = re.findall(amount_pattern, text)
        if matches:
            amount_str = matches[0]
            amount = Decimal(amount_str)
            from_code = prefs['from']
            to_code = prefs['to']
            if from_code != "EUR":
                amount_in_eur = amount / Decimal(str(rates[from_code]))
            else:
                amount_in_eur = amount
            if to_code != "EUR":
                final_amount = amount_in_eur * Decimal(str(rates[to_code]))
            else:
                final_amount = amount_in_eur
            await update.message.reply_text(
                f"{amount_str} {from_code} = {final_amount:.2f} {to_code}",
                reply_to_message_id=update.message.message_id
            )
            return

    if direct_matches:
        for match in direct_matches:
            try:
                amount_str, from_cur, to_cur = match.groups()
                from_code = await normalize_currency(from_cur)
                to_code = await normalize_currency(to_cur)
                
                if not from_code or not to_code:
                    continue
                
                amount = Decimal(amount_str)
                if amount <= 0:
                    continue

                if from_code != "EUR":
                    amount = amount / Decimal(str(rates[from_code]))
                
                final_amount = amount * Decimal(str(rates[to_code]))
                await update.message.reply_text(
                    f"{amount_str} {from_code} = {final_amount:.2f} {to_code}",
                    reply_to_message_id=update.message.message_id
                )
                return
                
            except (ValueError, KeyError):
                continue
    
    new_text = text
    replacements = []
    simple_matches = list(re.finditer(simple_pattern, text))
    for match in simple_matches:
        try:
            amount_str, raw_currency = match.groups()
            currency_code = await normalize_currency(raw_currency)
            
            if not currency_code or currency_code not in rates:
                continue
            
            amount = Decimal(amount_str)
            if amount <= 0:
                continue

            if currency_code == "EUR":
                converted = amount
                usd_amt = converted * Decimal(str(rates["USD"]))
                pln_amt = converted * Decimal(str(rates["PLN"]))
                new_val = f"{converted:.2f} EUR (~{usd_amt:.2f} USD, ~{pln_amt:.2f} PLN)"
            else:
                rate = Decimal(str(rates[currency_code]))
                converted = amount / rate
                usd_amt = converted * Decimal(str(rates["USD"]))
                new_val = f"{converted:.2f} EUR (~{usd_amt:.2f} USD)"
            
            replacements.append((match.group(), new_val))
            
        except (ValueError, KeyError):
            continue

    for old, new in reversed(replacements):
        new_text = new_text.replace(old, new)
    
    if new_text != text:
        await update.message.reply_text(
            f"{author}: {new_text}",
            reply_to_message_id=update.message.message_id
        )

async def rate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or len(context.args) != 2:
        await update.message.reply_text(
            "Please use the format: /rate FROM TO\nExample: /rate USD EUR"
        )
        return

    from_cur = await normalize_currency(context.args[0])
    to_cur = await normalize_currency(context.args[1])

    if not from_cur or not to_cur:
        await update.message.reply_text(
            "Invalid currency codes. Use /currencies to see available options."
        )
        return

    rates = await get_rates()
    if not rates:
        await update.message.reply_text("Sorry, couldn't fetch exchange rates at the moment.")
        return

    try:
        if from_cur == "EUR":
            rate = Decimal(str(rates[to_cur]))
        elif to_cur == "EUR":
            rate = Decimal(1) / Decimal(str(rates[from_cur]))
        else:
            eur_rate = Decimal(1) / Decimal(str(rates[from_cur]))
            rate = eur_rate * Decimal(str(rates[to_cur]))

        await update.message.reply_text(
            f"Current rate:\n1 {from_cur} = {rate:.4f} {to_cur}"
        )
    except (KeyError, ValueError):
        await update.message.reply_text("Error calculating exchange rate.")

def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("currencies", list_currencies))
    application.add_handler(CommandHandler("rate", rate_command))
    application.add_handler(CommandHandler("setdefault", set_default))
    application.add_handler(CommandHandler("getdefault", get_default))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logging.basicConfig(level=logging.INFO)
    application.run_polling()

if __name__ == "__main__":
    main()

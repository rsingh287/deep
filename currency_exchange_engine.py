import re

import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AntigravityAI-CurrencyEngine/1.0"
}

# Verified ISO 4217 Currency Codes
KNOWN_CURRENCIES = {
    "USD",
    "EUR",
    "GBP",
    "CAD",
    "AUD",
    "JPY",
    "INR",
    "CNY",
    "CHF",
    "NZD",
    "SGD",
    "HKD",
    "SEK",
    "NOK",
    "KRW",
    "MXN",
    "BRL",
    "ZAR",
    "RUB",
    "TRY",
    "AED",
    "SAR",
    "THB",
    "IDR",
    "MYR",
    "PHP",
    "PLN",
    "DKK",
    "CZK",
    "HUF",
    "ILS",
    "CLP",
    "PKR",
    "BDT",
    "NGN",
    "EGP",
    "VND",
    "BTC",
    "ETH",
    "USDT",
    "SOL",
}

CURRENCY_NAME_MAP = {
    "dollar": "USD",
    "dollars": "USD",
    "us dollar": "USD",
    "us dollars": "USD",
    "euro": "EUR",
    "euros": "EUR",
    "pound": "GBP",
    "pounds": "GBP",
    "cad": "CAD",
    "canadian dollar": "CAD",
    "canadian dollars": "CAD",
    "rupee": "INR",
    "rupees": "INR",
    "yen": "JPY",
    "yuan": "CNY",
    "aud": "AUD",
    "australian dollar": "AUD",
    "franc": "CHF",
    "francs": "CHF",
    "dirham": "AED",
    "dirhams": "AED",
    "riyal": "SAR",
    "riyals": "SAR",
    "bitcoin": "BTC",
    "ethereum": "ETH",
}


def resolve_currency_code(token: str):
    if not token:
        return None
    token = token.strip().upper()
    if token in KNOWN_CURRENCIES:
        return token
    t_low = token.lower()
    return CURRENCY_NAME_MAP.get(t_low)


def convert_currency(amount: float, base_curr: str, target_curr: str):
    base = base_curr.upper().strip()
    target = target_curr.upper().strip()

    try:
        url = f"https://open.er-api.com/v6/latest/{base}"
        res = requests.get(url, headers=HEADERS, timeout=4).json()

        if res.get("result") != "success":
            return None

        rates = res.get("rates", {})
        if target not in rates:
            return None

        rate = rates[target]
        converted = amount * rate

        return f"""### 💱 Real-Time Foreign Exchange Rates
- **Base Amount**: **{amount:,.2f} {base}**
- **Exchange Rate**: 1 {base} = `{rate:.4f}` {target}
- **Converted Value**: **{converted:,.2f} {target}**

*Rates updated live via European Central Bank & Open Exchange Feeds.*
"""
    except Exception:
        return None


def handle_currency_intent(prompt: str):
    p_low = prompt.lower().strip()

    # 1. Guard against coding, programming, temperature, unit, and media queries
    ignore_words = [
        "code",
        "coding",
        "script",
        "program",
        "function",
        "write",
        "make a code",
        "write a code",
        "create a code",
        "generate",
        "temperature",
        "celsius",
        "fahrenheit",
        "kelvin",
        "miles",
        "km",
        "meter",
        "meters",
        "kg",
        "lbs",
        "cm",
        "inches",
        "feet",
        "video",
        "audio",
        "pdf",
        "file",
        "app",
    ]
    if any(re.search(r"\b" + re.escape(w) + r"\b", p_low) for w in ignore_words):
        return None

    # 2. Currency conversion must have relevant indicators
    has_curr_context = any(
        k in p_low
        for k in [
            "exchange rate",
            "currency",
            "forex",
            "usd",
            "eur",
            "gbp",
            "cad",
            "inr",
            "jpy",
        ]
    ) or any(sym in prompt for sym in ["$", "€", "£", "₹"])
    if not has_curr_context and not re.search(r"\b(?:convert)\s+[\$€£₹]?\d+", p_low):
        return None

    # Match patterns like "100 usd to cad", "convert $500 to inr", "convert 500 eur to usd"
    m = re.search(
        r"\b(?:convert\s+)?(?:[\$€£₹]\s*)?(\d+(?:\.\d+)?)\s*([a-zA-Z]{3})\s+(?:to|in|into|=)\s+([a-zA-Z]{3})\b",
        prompt,
        re.IGNORECASE,
    )
    if m:
        try:
            amt = float(m.group(1))
            base = resolve_currency_code(m.group(2))
            target = resolve_currency_code(m.group(3))
            if base and target and base != target:
                result = convert_currency(amt, base, target)
                if result:
                    return (
                        result,
                        "autonomous_currency_engine",
                        [
                            {
                                "language": "python",
                                "code": f"convert_currency({amt}, '{base}', '{target}')",
                                "output": f"Converted {amt} {base} -> {target}",
                            }
                        ],
                    )
        except Exception:
            pass

    # Match simple rate queries like "exchange rate usd to cad" or "usd to cad"
    m2 = re.search(
        r"\b([a-zA-Z]{3})\s+(?:to|in|into)\s+([a-zA-Z]{3})\b", prompt, re.IGNORECASE
    )
    if m2:
        try:
            base = resolve_currency_code(m2.group(1))
            target = resolve_currency_code(m2.group(2))
            if base and target and base != target:
                result = convert_currency(1.0, base, target)
                if result:
                    return (
                        result,
                        "autonomous_currency_engine",
                        [
                            {
                                "language": "python",
                                "code": f"convert_currency(1.0, '{base}', '{target}')",
                                "output": f"Fetched 1 {base} -> {target}",
                            }
                        ],
                    )
        except Exception:
            pass

    return None

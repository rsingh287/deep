import ipaddress
import re
import secrets
import string
import urllib.parse

import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AntigravityAI-PublicEngine/1.0"
}


# ---------------------------------------------------------------------------------
# 1. WEATHER, AIR QUALITY & CLIMATE (OPEN-METEO)
# ---------------------------------------------------------------------------------
def get_weather(city="Toronto"):
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={urllib.parse.quote(city)}&count=1"
        geo_res = requests.get(geo_url, headers=HEADERS, timeout=4).json()
        if not geo_res.get("results"):
            return f"❌ **Weather**: City '{city}' not found."

        res = geo_res["results"][0]
        name, country, lat, lon = (
            res.get("name"),
            res.get("country", ""),
            res.get("latitude"),
            res.get("longitude"),
        )

        w_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        w_res = requests.get(w_url, headers=HEADERS, timeout=4).json()

        curr = w_res.get("current_weather", {})
        temp_c = curr.get("temperature", 0)
        temp_f = round((temp_c * 9 / 5) + 32, 1)
        wind_kmh = curr.get("windspeed", 0)
        is_day = "☀️ Day" if curr.get("is_day") == 1 else "🌙 Night"

        return f"""### 🌤️ Live Weather Telemetry: **{name}, {country}**
- **Temperature**: **{temp_c}°C** / **{temp_f}°F**
- **Wind Speed**: {wind_kmh} km/h ({is_day})
- **Coordinates**: Lat {lat:.2f}, Lon {lon:.2f}
- **Data Source**: Open-Meteo Public Satellite API
"""
    except Exception as e:
        return f"❌ **Weather API Error**: {str(e)}"


def get_air_quality(city="Toronto"):
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={urllib.parse.quote(city)}&count=1"
        geo_res = requests.get(geo_url, headers=HEADERS, timeout=4).json()
        if not geo_res.get("results"):
            return f"❌ **Air Quality**: City '{city}' not found."

        res = geo_res["results"][0]
        lat, lon, name = res["latitude"], res["longitude"], res["name"]

        aq_url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone,us_aqi"
        aq_res = requests.get(aq_url, headers=HEADERS, timeout=4).json()
        curr = aq_res.get("current", {})

        us_aqi = curr.get("us_aqi", 0)
        status = (
            "🟢 Good"
            if us_aqi <= 50
            else ("🟡 Moderate" if us_aqi <= 100 else "🔴 Unhealthy")
        )

        return f"""### 🌬️ Real-Time Air Quality Index: **{name}**
- **US AQI Score**: **{us_aqi}** ({status})
- **PM2.5**: {curr.get('pm2_5', 'N/A')} µg/m³
- **PM10**: {curr.get('pm10', 'N/A')} µg/m³
- **Ozone (O₃)**: {curr.get('ozone', 'N/A')} µg/m³
- **Nitrogen Dioxide (NO₂)**: {curr.get('nitrogen_dioxide', 'N/A')} µg/m³
- **Data Source**: European Environment Agency / Open-Meteo
"""
    except Exception as e:
        return f"❌ **Air Quality API Error**: {str(e)}"


# ---------------------------------------------------------------------------------
# 2. FOREX & CURRENCY RATES
# ---------------------------------------------------------------------------------
def get_currency_rate(amount=1.0, from_curr="USD", to_curr="INR"):
    try:
        from_curr, to_curr = from_curr.upper(), to_curr.upper()
        url = f"https://open.er-api.com/v6/latest/{from_curr}"
        res = requests.get(url, headers=HEADERS, timeout=4).json()
        if res.get("result") != "success":
            return f"❌ **Currency API**: Unable to fetch rate for {from_curr}."

        rate = res.get("rates", {}).get(to_curr)
        if not rate:
            return f"❌ **Currency API**: Code '{to_curr}' not recognized."

        converted = round(amount * rate, 2)
        return f"""### 💱 Live Forex Rate: **{amount:.2f} {from_curr} ➔ {converted:.2f} {to_curr}**
- **Exchange Rate**: 1 {from_curr} = **{rate:.4f} {to_curr}**
- **Inverse Rate**: 1 {to_curr} = **{(1/rate):.4f} {from_curr}**
- **Data Source**: Open Exchange Rates Network
"""
    except Exception as e:
        return f"❌ **Currency API Error**: {str(e)}"


# ---------------------------------------------------------------------------------
# 3. CRYPTO, BLOCKCHAIN & GAS FEES
# ---------------------------------------------------------------------------------
def get_crypto_prices():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana,cardano,dogecoin,ripple,binancecoin&vs_currencies=usd,cad,inr&include_24hr_change=true"
        res = requests.get(url, headers=HEADERS, timeout=4).json()
        coins = [
            ("Bitcoin (BTC)", "bitcoin"),
            ("Ethereum (ETH)", "ethereum"),
            ("Solana (SOL)", "solana"),
            ("Cardano (ADA)", "cardano"),
            ("Ripple (XRP)", "ripple"),
            ("Dogecoin (DOGE)", "dogecoin"),
            ("BNB", "binancecoin"),
        ]
        lines = []
        for name, key in coins:
            d = res.get(key, {})
            usd, cad, inr, chg = (
                d.get("usd", 0),
                d.get("cad", 0),
                d.get("inr", 0),
                d.get("usd_24h_change", 0),
            )
            lines.append(
                f"| **{name}** | **${usd:,.2f}** | CA${cad:,.2f} | ₹{inr:,.2f} | `{(chg):+.2f}%` |"
            )
        table_md = "\n".join(lines)
        return f"""### 🪙 Live Crypto Market Dashboard
| Asset | USD ($) | CAD (CA$) | INR (₹) | 24h Change |
| :--- | :--- | :--- | :--- | :--- |
{table_md}
*Data Source: CoinGecko Public API*
"""
    except Exception as e:
        return f"❌ **Crypto API Error**: {str(e)}"


def get_btc_gas_fees():
    try:
        res = requests.get(
            "https://mempool.space/api/v1/fees/recommended", headers=HEADERS, timeout=4
        ).json()
        return f"""### ⛽ Real-Time Bitcoin Mempool Gas Fees
- **High Priority (Fastest)**: **{res.get('fastestFee')} sat/vB**
- **Half Hour Fee**: **{res.get('halfHourFee')} sat/vB**
- **Hour Fee**: **{res.get('hourFee')} sat/vB**
- **Minimum Fee**: **{res.get('minimumFee')} sat/vB**
- **Data Source**: Mempool.space Public Node Telemetry
"""
    except Exception as e:
        return f"❌ **BTC Gas Fee API Error**: {str(e)}"


def get_crypto_fear_greed():
    try:
        res = requests.get(
            "https://api.alternative.me/fng/", headers=HEADERS, timeout=4
        ).json()
        data = res.get("data", [{}])[0]
        val = data.get("value", "50")
        class_str = data.get("value_classification", "Neutral")
        return f"""### 📊 Crypto Market Fear & Greed Index
- **Index Score**: **{val} / 100**
- **Market Sentiment**: **{class_str}**
- **Data Source**: Alternative.me Sentiment Index
"""
    except Exception as e:
        return f"❌ **Crypto Fear/Greed API Error**: {str(e)}"


def get_wikipedia_on_this_day():
    try:
        import datetime

        now = datetime.datetime.now()
        month = f"{now.month:02d}"
        day = f"{now.day:02d}"
        url = f"https://en.wikipedia.org/api/rest_v1/feed/onthisday/selected/{month}/{day}"
        res = requests.get(url, headers=HEADERS, timeout=4).json()
        events = res.get("selected", [])[:5]
        lines = [f"- **{e.get('year')}**: {e.get('text')}" for e in events]
        events_md = (
            "\n".join(lines) if lines else "No historical records found for today."
        )
        return f"""### 📅 Today in History (Wikipedia On This Day - {now.strftime('%B %d')})
{events_md}

*Data Source: Wikipedia Historical Archives*
"""
    except Exception as e:
        return f"❌ **Today in History API Error**: {str(e)}"


def lookup_zip_code(zip_code="90210", country="us"):
    try:
        url = f"http://api.zippopotam.us/{country.lower()}/{zip_code.strip()}"
        res = requests.get(url, headers=HEADERS, timeout=4).json()
        if not res.get("places"):
            return f"❌ **Zip Lookup**: Postal code '{zip_code}' not found."
        p = res["places"][0]
        place = p.get("place name")
        state = p.get("state")
        lat = p.get("latitude")
        lon = p.get("longitude")

        return f"""### 📍 Postal Code Geolocation: **{zip_code.upper()}** ({res.get('country')})
- **City / Community**: **{place}**
- **State / Province**: **{state}** ({p.get('state abbreviation')})
- **Coordinates**: Lat {lat}, Lon {lon}
"""
    except Exception as e:
        return f"❌ **Zip Lookup API Error**: {str(e)}"


def get_cocktail_recipe(drink="margarita"):
    try:
        url = f"https://www.thecocktaildb.com/api/json/v1/1/search.php?s={urllib.parse.quote(drink)}"
        res = requests.get(url, headers=HEADERS, timeout=4).json()
        drinks = res.get("drinks")
        if not drinks:
            return f"❌ **Cocktail DB**: Recipe for '{drink}' not found."
        d = drinks[0]
        name = d.get("strDrink")
        cat = d.get("strCategory")
        glass = d.get("strGlass")
        inst = d.get("strInstructions")
        thumb = d.get("strDrinkThumb")

        ingredients = []
        for i in range(1, 10):
            ing = d.get(f"strIngredient{i}")
            meas = d.get(f"strMeasure{i}")
            if ing:
                meas_str = f" ({meas.strip()})" if meas else ""
                ingredients.append(f"- **{ing.strip()}**{meas_str}")

        ing_md = "\n".join(ingredients)

        return f"""### 🍸 Mixology & Drink Recipe: **{name}**
![Cocktail]({thumb})

- **Category**: {cat} | **Glass Type**: {glass}
- **Ingredients**:
{ing_md}

- **Preparation Instructions**:
{inst}
"""
    except Exception as e:
        return f"❌ **Cocktail API Error**: {str(e)}"


def get_bacon_ipsum():
    try:
        res = requests.get(
            "https://baconipsum.com/api/?type=all-meat&paras=2",
            headers=HEADERS,
            timeout=3,
        ).json()
        paras = "\n\n".join(res)
        return f"🥓 **Developer Bacon Ipsum Text**:\n\n{paras}"
    except Exception as e:
        return f"❌ **Bacon Ipsum Error**: {str(e)}"


def get_zen_quote():
    try:
        res = requests.get(
            "https://zenquotes.io/api/random", headers=HEADERS, timeout=3
        ).json()
        q = res[0]
        return f"🧘 **Zen Thought & Wisdom**: *\"{q.get('q')}\"* — **{q.get('a')}**"
    except Exception as e:
        return f"❌ **Zen Quote API Error**: {str(e)}"


def get_food_nutrition(barcode="737628064502"):
    try:
        url = f"https://world.openfoodfacts.org/api/v0/product/{barcode.strip()}.json"
        res = requests.get(url, headers=HEADERS, timeout=4).json()
        if res.get("status") != 1:
            return f"❌ **OpenFoodFacts**: Product barcode '{barcode}' not found."
        p = res.get("product", {})
        name = p.get("product_name", "Unknown Product")
        brand = p.get("brands", "N/A")
        nutri = p.get("nutriscore_grade", "N/A").upper()
        nutr = p.get("nutriments", {})
        energy_kcal = nutr.get("energy-kcal_100g", "N/A")
        fat = nutr.get("fat_100g", "N/A")
        sugars = nutr.get("sugars_100g", "N/A")
        proteins = nutr.get("proteins_100g", "N/A")

        return f"""### 🥗 Open Food Facts Nutrition: **{name}**
- **Brand**: **{brand}**
- **Nutri-Score**: **Grade {nutri}**
- **Calories (per 100g)**: **{energy_kcal} kcal**
- **Fat (per 100g)**: {fat} g
- **Sugars (per 100g)**: {sugars} g
- **Proteins (per 100g)**: {proteins} g
"""
    except Exception as e:
        return f"❌ **Food Facts API Error**: {str(e)}"


def get_open_trivia():
    try:
        res = requests.get(
            "https://opentdb.com/api.php?amount=1&type=multiple",
            headers=HEADERS,
            timeout=4,
        ).json()
        q = res.get("results", [{}])[0]
        category = q.get("category")
        diff = q.get("difficulty", "").upper()
        question = urllib.parse.unquote(q.get("question", ""))
        correct = urllib.parse.unquote(q.get("correct_answer", ""))
        incorrects = [urllib.parse.unquote(i) for i in q.get("incorrect_answers", [])]

        return f"""### 🎯 Trivia & Quiz Challenge
- **Category**: **{category}** ({diff} Difficulty)
- **Question**: **{question}**

- **Correct Answer**: ||**{correct}**|| *(Hover/Click to reveal)*
- **Options**: {", ".join([correct] + incorrects)}
"""
    except Exception as e:
        return f"❌ **OpenTrivia API Error**: {str(e)}"


def get_kanye_quote():
    try:
        res = requests.get("https://api.kanye.rest", headers=HEADERS, timeout=3).json()
        return f"🎤 **Kanye West Quote**: *\"{res.get('quote')}\"*"
    except Exception as e:
        return f"❌ **Kanye Quote Error**: {str(e)}"


def get_hackernews_user(username="pg"):
    try:
        url = f"https://hacker-news.firebaseio.com/v0/user/{urllib.parse.quote(username)}.json"
        res = requests.get(url, headers=HEADERS, timeout=4).json()
        if not res:
            return f"❌ **HackerNews**: User '{username}' not found."

        about = re.sub(r"<[^>]*>?", "", res.get("about", "No bio provided."))
        karma = res.get("karma", 0)

        return f"""### 📰 HackerNews Profile: **@{res.get('id')}**
- **Karma Score**: **{karma:,}**
- **Bio**: {about}
- **Submissions Count**: {len(res.get('submitted', []))} items
"""
    except Exception as e:
        return f"❌ **HackerNews User Error**: {str(e)}"


def get_trending_crypto():
    try:
        res = requests.get(
            "https://api.coingecko.com/api/v3/search/trending",
            headers=HEADERS,
            timeout=4,
        ).json()
        coins = res.get("coins", [])[:5]
        lines = []
        for c in coins:
            item = c.get("item", {})
            name = item.get("name")
            sym = item.get("symbol")
            rank = item.get("market_cap_rank", "N/A")
            lines.append(f"- **{name} ({sym})**: Market Rank #{rank}")

        return "### 🔥 Top Trending Crypto Tokens (CoinGecko)\n" + "\n".join(lines)
    except Exception as e:
        return f"❌ **Trending Crypto Error**: {str(e)}"


def base64_utility(text, mode="encode"):
    import base64

    try:
        if mode == "encode":
            encoded = base64.b64encode(text.encode("utf-8")).decode("utf-8")
            return f"### 🔐 Base64 Encoded Result\n- **Original**: `{text}`\n- **Encoded**: `{encoded}`"
        else:
            decoded = base64.b64decode(text.encode("utf-8")).decode("utf-8")
            return f"### 🔓 Base64 Decoded Result\n- **Encoded**: `{text}`\n- **Decoded**: `{decoded}`"
    except Exception as e:
        return f"❌ **Base64 Error**: {str(e)}"


def generate_uuid_v4():
    import uuid

    u = str(uuid.uuid4())
    return f"### 🆔 RFC 4122 Compliant UUID v4 Generated\n- **UUID**: `{u}`"


# ---------------------------------------------------------------------------------
# 4. PUBLIC IP, NETWORK & GOOGLE PUBLIC DNS
# ---------------------------------------------------------------------------------
def get_public_ip_info():
    try:
        res = requests.get("http://ip-api.com/json", headers=HEADERS, timeout=4).json()
        return f"""### 🌐 Public IP & Network Geolocation
- **IP Address**: `{res.get('query')}`
- **ISP**: **{res.get('isp')}** ({res.get('org')})
- **Location**: **{res.get('city')}, {res.get('regionName')}, {res.get('country')}**
- **Coordinates**: Lat {res.get('lat')}, Lon {res.get('lon')}
- **Timezone**: {res.get('timezone')}
"""
    except Exception as e:
        return f"❌ **IP API Error**: {str(e)}"


def get_dns_records(domain="google.com"):
    try:
        url = f"https://dns.google/resolve?name={urllib.parse.quote(domain)}&type=A"
        res = requests.get(url, headers=HEADERS, timeout=4).json()
        answers = res.get("Answer", [])
        ips = [a.get("data") for a in answers if a.get("type") == 1]
        ip_str = ", ".join(f"`{ip}`" for ip in ips) if ips else "No A records"
        return f"""### 🔍 Google Public DNS Resolver: **{domain}**
- **Domain Name**: `{domain}`
- **Resolved A Records**: {ip_str}
- **DNS Status Code**: `{res.get('Status')}` (0 = NOERROR)
- **Data Source**: Google Public DNS (8.8.8.8)
"""
    except Exception as e:
        return f"❌ **DNS API Error**: {str(e)}"


# ---------------------------------------------------------------------------------
# 5. DEMOGRAPHICS, RANDOM USERS & NAME PREDICTOR APIS
# ---------------------------------------------------------------------------------
def predict_name_demographics(name="Michael"):
    try:
        name_clean = urllib.parse.quote(name.strip())
        agify = requests.get(
            f"https://api.agify.io/?name={name_clean}", headers=HEADERS, timeout=3
        ).json()
        genderize = requests.get(
            f"https://api.genderize.io/?name={name_clean}", headers=HEADERS, timeout=3
        ).json()
        nationalize = requests.get(
            f"https://api.nationalize.io/?name={name_clean}", headers=HEADERS, timeout=3
        ).json()

        age = agify.get("age", "N/A")
        gender = genderize.get("gender", "N/A").title()
        g_prob = round(genderize.get("probability", 0) * 100, 1)

        countries = nationalize.get("country", [])
        c_list = [
            f"{c.get('country_id')} ({c.get('probability')*100:.1f}%)"
            for c in countries[:3]
        ]
        c_str = ", ".join(c_list) if c_list else "Unknown"

        return f"""### 👤 Demographic AI Predictions: **{name.title()}**
- **Estimated Average Age**: **{age} years old**
- **Predicted Gender**: **{gender}** ({g_prob}% confidence)
- **Top Nationality Origins**: **{c_str}**
- **Data Source**: Agify / Genderize / Nationalize Demographic API Engine
"""
    except Exception as e:
        return f"❌ **Demographics API Error**: {str(e)}"


def get_random_user_profile():
    try:
        res = requests.get(
            "https://randomuser.me/api/", headers=HEADERS, timeout=4
        ).json()
        u = res.get("results", [{}])[0]
        name = f"{u.get('name', {}).get('first')} {u.get('name', {}).get('last')}"
        email = u.get("email")
        loc = f"{u.get('location', {}).get('city')}, {u.get('location', {}).get('country')}"
        pic = u.get("picture", {}).get("large")

        return f"""### 👨‍💼 Generated Mock User Profile
![User Avatar]({pic})
- **Name**: **{name}**
- **Gender**: {u.get('gender', '').title()}
- **Location**: **{loc}**
- **Email**: `{email}`
- **Username**: `{u.get('login', {}).get('username')}`
- **Phone**: `{u.get('phone')}`
"""
    except Exception as e:
        return f"❌ **Random User API Error**: {str(e)}"


# ---------------------------------------------------------------------------------
# 6. DUCKDUCKGO, JOKES, CAT/DOG & UTILITIES
# ---------------------------------------------------------------------------------
def get_duckduckgo_summary(query="Python"):
    try:
        url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(query)}&format=json&no_html=1"
        res = requests.get(url, headers=HEADERS, timeout=4).json()
        abstract = res.get("AbstractText", "")
        heading = res.get("Heading", query)
        source_url = res.get("AbstractURL", "")

        if not abstract:
            related = res.get("RelatedTopics", [])
            if related and "Text" in related[0]:
                abstract = related[0]["Text"]
                source_url = related[0].get("FirstURL", "")

        if abstract:
            return f"""### 🦆 DuckDuckGo Instant Web Answer: **{heading}**
{abstract}

🔗 [Read Source Link]({source_url})
"""
        return f"❌ **DuckDuckGo**: No instant answer found for '{query}'."
    except Exception as e:
        return f"❌ **DuckDuckGo API Error**: {str(e)}"


def get_programming_joke():
    try:
        res = requests.get(
            "https://v2.jokeapi.dev/joke/Programming?safe-mode",
            headers=HEADERS,
            timeout=3,
        ).json()
        if res.get("type") == "single":
            joke = res.get("joke")
        else:
            joke = (
                f"**Setup**: {res.get('setup')}\n\n**Punchline**: {res.get('delivery')}"
            )

        return f"💻 **Geek & Programming Joke**:\n\n{joke}"
    except Exception as e:
        return f"❌ **Joke API Error**: {str(e)}"


def get_chuck_norris_joke():
    try:
        res = requests.get(
            "https://api.chucknorris.io/jokes/random", headers=HEADERS, timeout=3
        ).json()
        return f"🤠 **Chuck Norris Fact**: *\"{res.get('value')}\"*"
    except Exception as e:
        return f"❌ **Chuck Norris API Error**: {str(e)}"


def get_cat_fact():
    try:
        res = requests.get(
            "https://catfact.ninja/fact", headers=HEADERS, timeout=3
        ).json()
        return f"🐱 **Verified Cat Fact**: *\"{res.get('fact')}\"*"
    except Exception as e:
        return f"❌ **Cat Fact API Error**: {str(e)}"


def get_dog_image():
    try:
        res = requests.get(
            "https://dog.ceo/api/breeds/image/random", headers=HEADERS, timeout=3
        ).json()
        img_url = res.get("message")
        breed = img_url.split("/")[-2].replace("-", " ").title()
        return f"""### 🐶 Random Dog & Breed Identification
![Dog Image]({img_url})

- **Detected Breed**: **{breed}**
- **Direct Image Link**: [Click to Open photo]({img_url})
"""
    except Exception as e:
        return f"❌ **Dog API Error**: {str(e)}"


def generate_secure_password(length=16):
    chars = string.ascii_letters + string.digits + "!@#$%^&*()_+-="
    pwd = "".join(secrets.choice(chars) for _ in range(length))
    return f"""### 🔑 Cryptographically Secure Random Password
- **Generated Password**: `{pwd}`
- **Length**: {length} characters
- **Entropy**: High (Upper, Lower, Digits, Special Chars)
"""


def calculate_subnet(ip_cidr="192.168.1.1/24"):
    try:
        net = ipaddress.ip_network(ip_cidr.strip(), strict=False)
        return f"""### 🧮 Network Subnet Calculator: `{ip_cidr}`
- **Network Address**: `{net.network_address}`
- **Broadcast Address**: `{net.broadcast_address}`
- **Netmask**: `{net.netmask}`
- **Wildcard Mask**: `{net.hostmask}`
- **Total Host Capacities**: **{net.num_addresses:,}** addresses (**{max(0, net.num_addresses - 2):,}** usable hosts)
- **First Usable Host**: `{net.network_address + 1}`
- **Last Usable Host**: `{net.broadcast_address - 1}`
"""
    except Exception as e:
        return f"❌ **Subnet Calculator Error**: {str(e)}"


# ---------------------------------------------------------------------------------
# 7. NASA, USGS & OTHER UTILITIES
# ---------------------------------------------------------------------------------
def get_nasa_apod():
    try:
        res = requests.get(
            "https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY",
            headers=HEADERS,
            timeout=4,
        ).json()
        return f"""### 🚀 NASA Astronomy Picture of the Day ({res.get('date')})
**Title**: {res.get('title')}

![NASA APOD]({res.get('url')})

{res.get('explanation', '')[:350]}...
"""
    except Exception as e:
        return f"❌ **NASA APOD Error**: {str(e)}"


def get_latest_earthquakes():
    try:
        res = requests.get(
            "https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&minmagnitude=4.5&limit=5",
            headers=HEADERS,
            timeout=4,
        ).json()
        lines = [
            f"- **Magnitude {f['properties']['mag']:.1f}**: {f['properties']['place']}"
            for f in res.get("features", [])
        ]
        return f"### 🌋 Real-Time USGS Earthquakes (Mag 4.5+)\n" + "\n".join(lines)
    except Exception as e:
        return f"❌ **Earthquake API Error**: {str(e)}"


def get_country_info(country="Canada"):
    try:
        res = requests.get(
            f"https://restcountries.com/v3.1/name/{urllib.parse.quote(country)}",
            headers=HEADERS,
            timeout=4,
        ).json()
        c = res[0]
        return f"""### {c.get('flag', '🏳️')} Country Intelligence: **{c.get('name', {}).get('common')}**
- **Capital**: **{", ".join(c.get('capital', ['N/A']))}**
- **Population**: **{c.get('population', 0):,}**
- **Languages**: {", ".join(c.get('languages', {}).values())}
- **Currency**: `{", ".join(c.get('currencies', {}).keys())}`
"""
    except Exception as e:
        return f"❌ **Country API Error**: {str(e)}"


def get_github_user(username="torvalds"):
    try:
        res = requests.get(
            f"https://api.github.com/users/{urllib.parse.quote(username)}",
            headers=HEADERS,
            timeout=4,
        ).json()
        return f"""### 🐙 GitHub Developer Profile: **@{res.get('login')}**
- **Name**: **{res.get('name', username)}**
- **Public Repos**: **{res.get('public_repos', 0)}**
- **Followers**: **{res.get('followers', 0):,}**
- **Bio**: {res.get('bio', 'N/A')}
"""
    except Exception as e:
        return f"❌ **GitHub API Error**: {str(e)}"


def get_sunrise_sunset(city="Toronto"):
    try:
        geo = requests.get(
            f"https://geocoding-api.open-meteo.com/v1/search?name={urllib.parse.quote(city)}&count=1",
            headers=HEADERS,
            timeout=4,
        ).json()
        res = geo["results"][0]
        s = (
            requests.get(
                f"https://api.sunrise-sunset.org/json?lat={res['latitude']}&lng={res['longitude']}&formatted=0",
                headers=HEADERS,
                timeout=4,
            )
            .json()
            .get("results", {})
        )
        return f"""### 🌅 Solar Telemetry: **{res['name']}**
- **Sunrise**: `{s.get('sunrise', '')[:19].replace('T', ' ')} UTC`
- **Sunset**: `{s.get('sunset', '')[:19].replace('T', ' ')} UTC`
"""
    except Exception as e:
        return f"❌ **Sunrise API Error**: {str(e)}"


def get_movie_info(query="Matrix"):
    try:
        res = requests.get(
            f"https://api.tvmaze.com/search/shows?q={urllib.parse.quote(query)}",
            headers=HEADERS,
            timeout=4,
        ).json()
        show = res[0].get("show", {})
        return f"### 🎬 TV/Movie DB: **{show.get('name')}**\n- **Rating**: ⭐ **{show.get('rating',{}).get('average', 'N/A')} / 10**\n- **Summary**: {re.sub(r'<[^>]*>?', '', show.get('summary', ''))[:250]}..."
    except Exception as e:
        return f"❌ **Movie API Error**: {str(e)}"


def get_anime_info(query="Naruto"):
    try:
        res = requests.get(
            f"https://api.jikan.moe/v4/anime?q={urllib.parse.quote(query)}&limit=1",
            headers=HEADERS,
            timeout=4,
        ).json()
        a = res.get("data", [])[0]
        return f"### ⛩️ MyAnimeList: **{a.get('title')}**\n- **Score**: ⭐ **{a.get('score')} / 10**\n- **Episodes**: {a.get('episodes')}"
    except Exception as e:
        return f"❌ **Anime API Error**: {str(e)}"


def get_pokemon_info(name="pikachu"):
    try:
        res = requests.get(
            f"https://pokeapi.co/api/v2/pokemon/{urllib.parse.quote(name.lower())}",
            headers=HEADERS,
            timeout=4,
        ).json()
        types = ", ".join(
            t.get("type", {}).get("name").title() for t in res.get("types", [])
        )
        return f"### ⚡ Pokédex: **{res.get('name').upper()}**\n- **Type**: **{types}**\n- **Height**: {res.get('height')/10.0} m | **Weight**: {res.get('weight')/10.0} kg"
    except Exception as e:
        return f"❌ **Pokédex API Error**: {str(e)}"


def get_book_info(title="1984"):
    try:
        res = requests.get(
            f"https://openlibrary.org/search.json?title={urllib.parse.quote(title)}&limit=1",
            headers=HEADERS,
            timeout=4,
        ).json()
        b = res.get("docs", [])[0]
        return f"### 📖 OpenLibrary: **{b.get('title')}**\n- **Author**: **{', '.join(b.get('author_name', ['Unknown']))}**\n- **First Published**: {b.get('first_publish_year')}"
    except Exception as e:
        return f"❌ **Book API Error**: {str(e)}"


def get_qr_code(text="https://google.com"):
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={urllib.parse.quote(text)}"
    return (
        f"### 📱 Dynamic QR Code Generated\n![QR Code]({qr_url})\n\n- **URL**: `{text}`"
    )


def get_public_holidays(country="CA", year=2026):
    try:
        res = requests.get(
            f"https://date.nager.at/api/v3/PublicHolidays/{year}/{country.upper()}",
            headers=HEADERS,
            timeout=4,
        ).json()
        lines = [f"- **{h.get('date')}**: {h.get('name')}" for h in res[:5]]
        return f"### 📅 Statutory Holidays ({country.upper()})\n" + "\n".join(lines)
    except Exception as e:
        return f"❌ **Holidays API Error**: {str(e)}"


def get_universities(name="Toronto", country="Canada"):
    try:
        res = requests.get(
            f"http://universities.hipolabs.com/search?name={urllib.parse.quote(name)}&country={urllib.parse.quote(country)}",
            headers=HEADERS,
            timeout=4,
        ).json()
        lines = [
            f"- **[{u.get('name')}]({u.get('web_pages', ['#'])[0]})**" for u in res[:4]
        ]
        return f"### 🎓 Universities Directory: **{name}**\n" + "\n".join(lines)
    except Exception as e:
        return f"❌ **Universities API Error**: {str(e)}"


def get_wikipedia_summary(query="Artificial intelligence"):
    try:
        clean_q = re.sub(
            r"^(who is|what is|tell me about|define|explain)\s+",
            "",
            query,
            flags=re.IGNORECASE,
        ).strip()
        res = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(clean_q.title().replace(' ', '_'))}",
            headers=HEADERS,
            timeout=4,
        )
        if res.status_code == 200:
            d = res.json()
            return f"### 📚 Wikipedia: **{d.get('title')}**\n{d.get('extract')}\n\n🔗 [Read Article]({d.get('content_urls', {}).get('desktop', {}).get('page', '')})"
        return f"❌ **Wikipedia API**: No article found for '{clean_q}'."
    except Exception as e:
        return f"❌ **Wikipedia API Error**: {str(e)}"


def get_tech_news():
    try:
        ids = requests.get(
            "https://hacker-news.firebaseio.com/v0/topstories.json",
            headers=HEADERS,
            timeout=3,
        ).json()[:5]
        items = []
        for sid in ids:
            item = requests.get(
                f"https://hacker-news.firebaseio.com/v0/item/{sid}.json",
                headers=HEADERS,
                timeout=2,
            ).json()
            if item:
                items.append(
                    f"- [{item.get('title')}]({item.get('url')}) (Points: `{item.get('score')}`)"
                )
        return f"### 📰 Top Tech News (HackerNews)\n" + "\n".join(items)
    except Exception as e:
        return f"❌ **Tech News API Error**: {str(e)}"


def get_random_advice():
    try:
        res = requests.get(
            "https://api.adviceslip.com/advice", headers=HEADERS, timeout=3
        ).json()
        return f"💡 **Advice Slip**: *\"{res.get('slip', {}).get('advice')}\"*"
    except Exception as e:
        return f"❌ **Advice API Error**: {str(e)}"


# ---------------------------------------------------------------------------------
# CENTRAL PUBLIC API INTENT ROUTER
# ---------------------------------------------------------------------------------
def handle_public_api_intent(prompt: str):
    p_low = prompt.lower().strip()

    # Trivia & Quiz
    if "trivia" in p_low or "quiz question" in p_low or "random trivia" in p_low:
        return (
            get_open_trivia(),
            "free_public_trivia_api",
            [
                {
                    "language": "python",
                    "code": "get_open_trivia()",
                    "output": "Fetched OpenTrivia Question",
                }
            ],
        )

    # Kanye Quote
    if "kanye" in p_low or "kanye quote" in p_low:
        return (
            get_kanye_quote(),
            "free_public_kanye_api",
            [
                {
                    "language": "python",
                    "code": "get_kanye_quote()",
                    "output": "Fetched Kanye West Quote",
                }
            ],
        )

    # HackerNews User
    if "hackernews user" in p_low or "hn profile" in p_low:
        u = re.search(r"(?:user|profile)\s+([a-zA-Z0-9_-]+)", prompt, re.IGNORECASE)
        user = u.group(1).strip() if u else "pg"
        return (
            get_hackernews_user(user),
            "free_public_hn_user_api",
            [
                {
                    "language": "python",
                    "code": f"get_hackernews_user('{user}')",
                    "output": "Fetched HackerNews User Profile",
                }
            ],
        )

    # Trending Crypto
    if "trending crypto" in p_low or "hot coins" in p_low or "trending coins" in p_low:
        return (
            get_trending_crypto(),
            "free_public_trending_crypto_api",
            [
                {
                    "language": "python",
                    "code": "get_trending_crypto()",
                    "output": "Fetched CoinGecko Trending Coins",
                }
            ],
        )

    # Base64 Utility
    if "base64 encode" in p_low or "base64 decode" in p_low or "base64" in p_low:
        mode = "decode" if "decode" in p_low else "encode"
        q = re.search(r"(?:encode|decode|base64)\s+(.+)", prompt, re.IGNORECASE)
        text = q.group(1).strip() if q else "Antigravity AI"
        return (
            base64_utility(text, mode),
            "free_public_base64_utility",
            [
                {
                    "language": "python",
                    "code": f"base64_utility('{text}', '{mode}')",
                    "output": "Executed Base64 Utility",
                }
            ],
        )

    # UUID Generator
    if (
        "generate uuid" in p_low
        or "random uuid" in p_low
        or "uuid v4" in p_low
        or "guid" in p_low
    ):
        return (
            generate_uuid_v4(),
            "free_public_uuid_generator",
            [
                {
                    "language": "python",
                    "code": "generate_uuid_v4()",
                    "output": "Generated RFC 4122 UUID v4",
                }
            ],
        )

    # Wikipedia On This Day / Today in History
    if any(
        k in p_low
        for k in [
            "today in history",
            "on this day",
            "this day in history",
            "historical events today",
        ]
    ):
        return (
            get_wikipedia_on_this_day(),
            "free_public_history_api",
            [
                {
                    "language": "python",
                    "code": "get_wikipedia_on_this_day()",
                    "output": "Fetched Wikipedia Historical Records",
                }
            ],
        )

    # Zip Code / Postal Code Lookup
    if "zip code" in p_low or "postal code" in p_low or "zip lookup" in p_low:
        m = re.search(r"(\d{5})", prompt)
        zip_c = m.group(1) if m else "90210"
        return (
            lookup_zip_code(zip_c),
            "free_public_zip_lookup_api",
            [
                {
                    "language": "python",
                    "code": f"lookup_zip_code('{zip_c}')",
                    "output": "Fetched Zippopotam Geolocation",
                }
            ],
        )

    # Cocktail & Drink Recipe
    if any(
        k in p_low
        for k in ["cocktail", "drink recipe", "how to make drink", "mixology"]
    ):
        m = re.search(
            r"(?:cocktail|recipe|make|for)\s+([a-zA-Z\s]+)", prompt, re.IGNORECASE
        )
        drink = m.group(1).strip() if m else "margarita"
        return (
            get_cocktail_recipe(drink),
            "free_public_cocktail_api",
            [
                {
                    "language": "python",
                    "code": f"get_cocktail_recipe('{drink}')",
                    "output": "Fetched CocktailDB Recipe",
                }
            ],
        )

    # Bacon Ipsum
    if "bacon ipsum" in p_low or "lorem ipsum" in p_low or "meat text" in p_low:
        return (
            get_bacon_ipsum(),
            "free_public_bacon_ipsum_api",
            [
                {
                    "language": "python",
                    "code": "get_bacon_ipsum()",
                    "output": "Generated Bacon Ipsum Text",
                }
            ],
        )

    # Zen Quote
    if (
        "zen quote" in p_low
        or "quote of the day" in p_low
        or "motivational quote" in p_low
        or "inspirational quote" in p_low
    ):
        return (
            get_zen_quote(),
            "free_public_zen_quote_api",
            [
                {
                    "language": "python",
                    "code": "get_zen_quote()",
                    "output": "Fetched ZenQuote Wisdom",
                }
            ],
        )

    # Food Nutrition Barcode
    if (
        "food nutrition" in p_low
        or "barcode" in p_low
        or "nutriscore" in p_low
        or "nutrition info" in p_low
    ):
        m = re.search(r"(\d{8,14})", prompt)
        code = m.group(1) if m else "737628064502"
        return (
            get_food_nutrition(code),
            "free_public_food_nutrition_api",
            [
                {
                    "language": "python",
                    "code": f"get_food_nutrition('{code}')",
                    "output": "Fetched Open Food Facts Data",
                }
            ],
        )

    # Demographics Predictor
    if any(
        k in p_low
        for k in ["predict name", "demographics for", "demographics of", "age of name"]
    ):
        m = re.search(
            r"(?:demographics for|demographics of|name demographics for|predict name for|name|for|of)\s+([a-zA-Z]+)",
            prompt,
            re.IGNORECASE,
        )
        name = m.group(1).strip() if m else "Michael"
        return (
            predict_name_demographics(name),
            "free_public_demographics_api",
            [
                {
                    "language": "python",
                    "code": f"predict_name_demographics('{name}')",
                    "output": "Fetched Agify/Genderize Data",
                }
            ],
        )

    # Random Mock User Profile
    if (
        "random user" in p_low
        or "mock user profile" in p_low
        or "generate user" in p_low
    ):
        return (
            get_random_user_profile(),
            "free_public_random_user_api",
            [
                {
                    "language": "python",
                    "code": "get_random_user_profile()",
                    "output": "Fetched RandomUser Profile",
                }
            ],
        )

    # Password Generator
    if (
        "generate password" in p_low
        or "random password" in p_low
        or "secure password" in p_low
    ):
        m = re.search(r"(\d+)", prompt)
        length = int(m.group(1)) if m else 16
        return (
            generate_secure_password(length),
            "free_public_password_generator",
            [
                {
                    "language": "python",
                    "code": f"generate_secure_password({length})",
                    "output": "Generated Crypto Secure Password",
                }
            ],
        )

    # Subnet Calculator
    if "subnet" in p_low or "cidr" in p_low or "ip range" in p_low:
        m = re.search(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2})", prompt)
        cidr = m.group(1) if m else "192.168.1.1/24"
        return (
            calculate_subnet(cidr),
            "free_public_subnet_calculator",
            [
                {
                    "language": "python",
                    "code": f"calculate_subnet('{cidr}')",
                    "output": "Calculated Network Subnet",
                }
            ],
        )

    # DuckDuckGo Answer
    if "duckduckgo" in p_low or "ddg search" in p_low or "ddg" in p_low:
        q = re.sub(
            r"^(duckduckgo search|duckduckgo|ddg search|ddg)\s+",
            "",
            prompt,
            flags=re.IGNORECASE,
        ).strip()
        return (
            get_duckduckgo_summary(q),
            "free_public_duckduckgo_api",
            [
                {
                    "language": "python",
                    "code": f"get_duckduckgo_summary('{q}')",
                    "output": "Fetched DuckDuckGo Answer",
                }
            ],
        )

    # Programming Joke
    if "code joke" in p_low or "programming joke" in p_low or "geek joke" in p_low:
        return (
            get_programming_joke(),
            "free_public_joke_api",
            [
                {
                    "language": "python",
                    "code": "get_programming_joke()",
                    "output": "Fetched JokeAPI Data",
                }
            ],
        )

    # Chuck Norris Joke
    if "chuck norris" in p_low:
        return (
            get_chuck_norris_joke(),
            "free_public_chuck_norris_api",
            [
                {
                    "language": "python",
                    "code": "get_chuck_norris_joke()",
                    "output": "Fetched Chuck Norris Joke",
                }
            ],
        )

    # Cat Fact
    if "cat fact" in p_low or "cat facts" in p_low:
        return (
            get_cat_fact(),
            "free_public_cat_fact_api",
            [
                {
                    "language": "python",
                    "code": "get_cat_fact()",
                    "output": "Fetched Cat Fact",
                }
            ],
        )

    # Dog Photo
    if (
        "dog picture" in p_low
        or "dog photo" in p_low
        or "dog image" in p_low
        or "dog breed" in p_low
    ):
        return (
            get_dog_image(),
            "free_public_dog_api",
            [
                {
                    "language": "python",
                    "code": "get_dog_image()",
                    "output": "Fetched Dog Image",
                }
            ],
        )

    # Air Quality & Weather
    if "air quality" in p_low or "aqi" in p_low or "pollution" in p_low:
        c = re.search(r"(?:in|for|at)\s+([a-zA-Z\s]+)", prompt)
        city = c.group(1).strip() if c else "Toronto"
        return (
            get_air_quality(city),
            "free_public_air_quality_api",
            [
                {
                    "language": "python",
                    "code": f"get_air_quality('{city}')",
                    "output": "Fetched Open-Meteo AQI Data",
                }
            ],
        )

    # Weather (ensure not a coding or temperature conversion request)
    is_weather = any(k in p_low for k in ["weather", "forecast", "climate"]) or (
        "temperature" in p_low
        and not any(
            w in p_low
            for w in [
                "code",
                "script",
                "convert",
                "converting",
                "celsius",
                "fahrenheit",
                "kelvin",
                "program",
                "function",
            ]
        )
    )
    if is_weather and not any(
        w in p_low
        for w in [
            "make a code",
            "write a code",
            "create code",
            "generate code",
            "python",
        ]
    ):
        c = re.search(
            r"(?:weather|temperature|forecast|climate)(?:\s+in|\s+for|\s+at)\s+([a-zA-Z\s,]+)",
            prompt,
            re.IGNORECASE,
        )
        if c:
            city = c.group(1).strip()
            if city and not any(
                w in city.lower() for w in ["from", "to", "celsius", "fahrenheit"]
            ):
                return (
                    get_weather(city),
                    "free_public_weather_api",
                    [
                        {
                            "language": "python",
                            "code": f"get_weather('{city}')",
                            "output": "Fetched Open-Meteo Data",
                        }
                    ],
                )

    # Currency Forex
    if any(
        k in p_low
        for k in [
            "currency",
            "forex",
            "exchange rate",
            "usd to",
            "cad to",
            "inr to",
            "eur to",
            "gbp to",
            "convert currency",
        ]
    ):
        amt = 1.0
        m = re.search(r"(\d+(?:\.\d+)?)", prompt)
        if m:
            try:
                amt = float(m.group(1))
            except:
                pass
        f_c, t_c = "USD", "INR"
        pairs = [
            ("usd", "inr"),
            ("usd", "cad"),
            ("cad", "inr"),
            ("cad", "usd"),
            ("eur", "usd"),
            ("gbp", "usd"),
            ("inr", "usd"),
        ]
        for f, t in pairs:
            if f in p_low and t in p_low:
                f_c, t_c = f.upper(), t.upper()
                break
        return (
            get_currency_rate(amt, f_c, t_c),
            "free_public_currency_api",
            [
                {
                    "language": "python",
                    "code": f"get_currency_rate({amt}, '{f_c}', '{t_c}')",
                    "output": "Fetched Open ExchangeRates",
                }
            ],
        )

    # Crypto & Blockchain
    if "btc gas" in p_low or "mempool" in p_low or "bitcoin fee" in p_low:
        return (
            get_btc_gas_fees(),
            "free_public_btc_gas_api",
            [
                {
                    "language": "python",
                    "code": "get_btc_gas_fees()",
                    "output": "Fetched Mempool Node Fees",
                }
            ],
        )

    if "fear and greed" in p_low or "crypto sentiment" in p_low:
        return (
            get_crypto_fear_greed(),
            "free_public_fear_greed_api",
            [
                {
                    "language": "python",
                    "code": "get_crypto_fear_greed()",
                    "output": "Fetched Alternative.me Index",
                }
            ],
        )

    if any(
        k in p_low
        for k in [
            "crypto",
            "bitcoin",
            "btc",
            "ethereum",
            "eth price",
            "solana price",
            "dogecoin",
        ]
    ):
        return (
            get_crypto_prices(),
            "free_public_crypto_api",
            [
                {
                    "language": "python",
                    "code": "get_crypto_prices()",
                    "output": "Fetched CoinGecko Crypto Prices",
                }
            ],
        )

    # NASA & USGS
    if (
        "nasa" in p_low
        or "apod" in p_low
        or "space picture" in p_low
        or "astronomy picture" in p_low
    ):
        return (
            get_nasa_apod(),
            "free_public_nasa_api",
            [
                {
                    "language": "python",
                    "code": "get_nasa_apod()",
                    "output": "Fetched NASA APOD Telemetry",
                }
            ],
        )

    if "earthquake" in p_low or "earthquakes" in p_low or "seismic" in p_low:
        return (
            get_latest_earthquakes(),
            "free_public_usgs_api",
            [
                {
                    "language": "python",
                    "code": "get_latest_earthquakes()",
                    "output": "Fetched USGS Seismic Telemetry",
                }
            ],
        )

    # Country & Holidays
    if any(
        k in p_low for k in ["country info", "country", "population of", "capital of"]
    ):
        c = re.search(
            r"(?:country info|country|info|of)\s+([a-zA-Z\s]+)", prompt, re.IGNORECASE
        )
        country = c.group(1).strip() if c else "Canada"
        return (
            get_country_info(country),
            "free_public_country_api",
            [
                {
                    "language": "python",
                    "code": f"get_country_info('{country}')",
                    "output": "Fetched REST Countries Data",
                }
            ],
        )

    if "holidays" in p_low or "public holiday" in p_low:
        return (
            get_public_holidays("CA", 2026),
            "free_public_holidays_api",
            [
                {
                    "language": "python",
                    "code": "get_public_holidays('CA', 2026)",
                    "output": "Fetched Nager.Date Public Holidays",
                }
            ],
        )

    # GitHub User
    if "github user" in p_low or "github profile" in p_low:
        u = re.search(r"(?:user|profile)\s+([a-zA-Z0-9_-]+)", prompt, re.IGNORECASE)
        user = u.group(1).strip() if u else "torvalds"
        return (
            get_github_user(user),
            "free_public_github_api",
            [
                {
                    "language": "python",
                    "code": f"get_github_user('{user}')",
                    "output": "Fetched GitHub Profile Data",
                }
            ],
        )

    # Sunrise & Sunset
    if "sunrise" in p_low or "sunset" in p_low or "solar time" in p_low:
        c = re.search(r"(?:in|for|at)\s+([a-zA-Z\s]+)", prompt, re.IGNORECASE)
        city = c.group(1).strip() if c else "Toronto"
        return (
            get_sunrise_sunset(city),
            "free_public_sunrise_api",
            [
                {
                    "language": "python",
                    "code": f"get_sunrise_sunset('{city}')",
                    "output": "Fetched Sunrise-Sunset Data",
                }
            ],
        )

    # TV, Movies & Anime
    if "movie" in p_low or "tv show" in p_low or "series" in p_low:
        m = re.search(
            r"(?:movie|show|series)\s+([a-zA-Z0-9\s]+)", prompt, re.IGNORECASE
        )
        query = m.group(1).strip() if m else "Matrix"
        return (
            get_movie_info(query),
            "free_public_tvmaze_api",
            [
                {
                    "language": "python",
                    "code": f"get_movie_info('{query}')",
                    "output": "Fetched TVMaze Show Data",
                }
            ],
        )

    if "anime" in p_low or "manga" in p_low:
        a = re.search(r"(?:anime|manga)\s+([a-zA-Z0-9\s]+)", prompt, re.IGNORECASE)
        query = a.group(1).strip() if a else "Naruto"
        return (
            get_anime_info(query),
            "free_public_jikan_anime_api",
            [
                {
                    "language": "python",
                    "code": f"get_anime_info('{query}')",
                    "output": "Fetched MyAnimeList Data",
                }
            ],
        )

    if "pokedex" in p_low or "pokemon" in p_low:
        p = re.search(r"(?:pokemon|pokedex)\s+([a-zA-Z]+)", prompt, re.IGNORECASE)
        pname = p.group(1).strip() if p else "pikachu"
        return (
            get_pokemon_info(pname),
            "free_public_pokeapi",
            [
                {
                    "language": "python",
                    "code": f"get_pokemon_info('{pname}')",
                    "output": "Fetched PokeAPI Telemetry",
                }
            ],
        )

    if "book" in p_low or "author of" in p_low:
        b = re.search(r"(?:book|of)\s+([a-zA-Z0-9\s]+)", prompt, re.IGNORECASE)
        query = b.group(1).strip() if b else "1984"
        return (
            get_book_info(query),
            "free_public_openlibrary_api",
            [
                {
                    "language": "python",
                    "code": f"get_book_info('{query}')",
                    "output": "Fetched OpenLibrary Data",
                }
            ],
        )

    # QR Code Generator
    if "qr code" in p_low or "generate qr" in p_low:
        q = re.search(r"(?:code|for)\s+(.+)", prompt, re.IGNORECASE)
        text = q.group(1).strip() if q else "https://google.com"
        return (
            get_qr_code(text),
            "free_public_qr_api",
            [
                {
                    "language": "python",
                    "code": f"get_qr_code('{text}')",
                    "output": "Generated QR Code Image",
                }
            ],
        )

    # Public IP & DNS
    if any(
        k in p_low
        for k in ["my ip", "what is my ip", "public ip", "my location", "my isp"]
    ):
        return (
            get_public_ip_info(),
            "free_public_ip_api",
            [
                {
                    "language": "python",
                    "code": "get_public_ip_info()",
                    "output": "Fetched IP-API Geolocation",
                }
            ],
        )

    if "dns lookup" in p_low or "dns resolve" in p_low:
        d = re.search(
            r"(?:lookup|resolve|for)\s+([a-zA-Z0-9\.-]+)", prompt, re.IGNORECASE
        )
        domain = d.group(1).strip() if d else "google.com"
        return (
            get_dns_records(domain),
            "free_public_google_dns_api",
            [
                {
                    "language": "python",
                    "code": f"get_dns_records('{domain}')",
                    "output": "Fetched Google Public DNS",
                }
            ],
        )

    # Tech News
    if any(
        k in p_low for k in ["tech news", "hacker news", "top news", "headline news"]
    ):
        return (
            get_tech_news(),
            "free_public_news_api",
            [
                {
                    "language": "python",
                    "code": "get_tech_news()",
                    "output": "Fetched HackerNews Top Stories",
                }
            ],
        )

    # Advice
    if "advice" in p_low or "give me advice" in p_low:
        return (
            get_random_advice(),
            "free_public_advice_api",
            [
                {
                    "language": "python",
                    "code": "get_random_advice()",
                    "output": "Fetched Advice Slip Data",
                }
            ],
        )

    # Wikipedia Instant Knowledge
    if prompt.startswith(("who is ", "what is ", "define ", "wiki ")) and not any(
        k in p_low for k in ["ip", "weather", "time", "date", "system", "status", "cpu", "ram", "pc", "battery", "hardware", "gpu", "file", "code", "commit", "port", "service", "memory"]
    ):
        return (
            get_wikipedia_summary(prompt),
            "free_public_wikipedia_api",
            [
                {
                    "language": "python",
                    "code": f"get_wikipedia_summary('{prompt}')",
                    "output": "Fetched Wikipedia REST Data",
                }
            ],
        )

    return None

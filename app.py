import os
import json
import requests
import feedparser
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import jinja2
from datetime import datetime
from dotenv import load_dotenv
from config import APP_TITLE, COLORS, APIS

load_dotenv()  # .env फाइल से API Key लोड करो

app = FastAPI()
# 🔥 FastAPI के बजाय सीधा Jinja2 Environment use करो (Python 3.14 के लिए सही)
env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))

# ----- 1. DATA LOADING (JSON Files) -----
def load_json(filename):
    try:
        with open(f"data/{filename}", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

# ----- 2. LIVE MANDI PRICES -----
def get_mandi_prices():
    try:
        r = requests.get(APIS["mandi"], timeout=5)
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list) and len(data) > 0:
                return data[:6]
    except:
        pass
    # 🛡️ Fallback (अगर API डाउन हो तो)
    return [
        {"crop": "Wheat", "variety": "Lok-1", "price": 2450, "change": "+0.8%"},
        {"crop": "Paddy", "variety": "Pusa 1121", "price": 4280, "change": "+1.2%"},
        {"crop": "Maize", "variety": "Hybrid", "price": 2180, "change": "0.0%"},
        {"crop": "Tomato", "variety": "Hybrid", "price": 2850, "change": "+7.2%"},
    ]

# ----- 3. LIVE WEATHER (OpenWeatherMap) -----
def get_weather():
    key = os.getenv("OPENWEATHER_KEY")
    if not key:
        return {"temp": "N/A", "desc": "Key Missing", "icon": "fa-cloud"}
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q=Karnal&appid={key}&units=metric"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            return {
                "temp": round(data['main']['temp']),
                "desc": data['weather'][0]['description'],
                "icon": "fa-cloud-rain" if "rain" in data['weather'][0]['description'].lower() else "fa-sun"
            }
    except:
        pass
    return {"temp": "28", "desc": "Partly Cloudy", "icon": "fa-cloud"}

# ----- 4. LIVE NEWS (Google RSS) -----
def get_news():
    try:
        feed = feedparser.parse("https://news.google.com/rss/search?q=haryana+agriculture&hl=en-IN&gl=IN&ceid=IN:en")
        items = []
        for entry in feed.entries[:4]:  # सिर्फ 4 खबरें
            items.append(entry.title)
        if items:
            return items
    except:
        pass
    # 🛡️ अगर RSS न चले तो Fallback
    fallback = load_json("news_fallback.json")
    if fallback:
        return fallback
    return ["🌾 Latest Agri News loading..."]

# ----- 5. MAIN ROUTE -----
@app.get("/", response_class=HTMLResponse)
async def home(req: Request):
    # सारा Live Data एक साथ Fetch करो
    prices = get_mandi_prices()
    weather = get_weather()
    news = get_news()
    progressive = load_json("progressive_farmers.json")
    organic = load_json("organic_farmers.json")
    institutions = load_json("institutions.json")
    today = datetime.now().strftime("%d %B %Y")

    # --- KPI CARDS के लिए Dynamic कैलकुलेशन (Mandi Data से) ---
    avg_price = "N/A"
    if prices and isinstance(prices, list):
        try:
            nums = [p['price'] for p in prices if isinstance(p.get('price'), (int, float))]
            if nums:
                avg_price = f"₹{round(sum(nums)/len(nums))}"
        except:
            pass

    kpi = {
        "farmers": "2.4M",
        "avg_price": avg_price,
        "schemes": "15",
        "fpos": "182"
    }

    # 🖼️ Template Render करो - अब WEATHER और NEWS भी पास किए हैं!
    template = env.get_template("index.html")
    html_content = template.render(
        title=APP_TITLE,
        today=today,
        colors=COLORS,
        prices=prices,
        weather=weather,          # ✅ अब Weather भेजा
        news=news,               # ✅ अब News भेजा
        kpi=kpi,
        progressive_farmers=progressive,
        organic_farmers=organic,
        institutions=institutions
    )
    return HTMLResponse(content=html_content)
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
env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))

# ----- 1. DATA LOADING (JSON Files) -----
def load_json(filename):
    try:
        with open(f"data/{filename}", "r", encoding="utf-8") as f:
            data = json.load(f)
            print(f"✅ {filename} loaded successfully! ({len(data) if isinstance(data, list) else len(data)} items)")
            return data
    except FileNotFoundError:
        print(f"❌ FILE NOT FOUND: data/{filename}")
        return [] if filename != "institutions_haryana.json" else {}  # Handle dict fallback
    except json.JSONDecodeError as e:
        print(f"❌ JSON ERROR in {filename}: {e}")
        return [] if filename != "institutions_haryana.json" else {}
    except Exception as e:
        print(f"❌ UNKNOWN ERROR in {filename}: {e}")
        return [] if filename != "institutions_haryana.json" else {}

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
        for entry in feed.entries[:4]:
            items.append(entry.title)
        if items:
            return items
    except:
        pass
    fallback = load_json("news_fallback.json")
    if fallback:
        return fallback
    return ["🌾 Latest Agri News loading..."]

# ----- 5. MAIN ROUTE (Dashboard) -----
@app.get("/", response_class=HTMLResponse)
async def home(req: Request):
    # LIVE DATA
    prices = get_mandi_prices()
    weather = get_weather()
    news = get_news()
    
    # 🔥 FARMERS DATA (Static JSONs)
    progressive_haryana = load_json("progressive_haryana.json")
    progressive_india = load_json("progressive_india.json")
    organic_farmers = load_json("organic_farmers.json")
    
    # 🏛️ HARYANA INSTITUTIONS (नई FILES)
    haryana_institutions = load_json("institutions_haryana.json")  # सभी विश्वविद्यालय, विभाग
    kvks = load_json("kvks_haryana.json")  # सभी KVKs
    fpos = load_json("fpos_haryana.json")  # सभी FPOs
    
    # 🇮🇳 INDIA INSTITUTIONS (नई FILES)
    india_institutions = load_json("institutions_india.json")  # State Agricultural Universities
    icar_institutes = load_json("icar_institutes_india.json")  # ICAR Research Institutes
    
    # 📋 CHECKLIST DATA (नई FEATURE)
    checklist = load_json("checklist.json")  # Daily/Weekly Tasks
    
    today = datetime.now().strftime("%d %B %Y")

    # KPI CALCULATION (Dynamic Avg Price)
    avg_price = "N/A"
    if prices and isinstance(prices, list):
        try:
            nums = [p['price'] for p in prices if isinstance(p.get('price'), (int, float))]
            if nums:
                avg_price = f"₹{round(sum(nums)/len(nums))}"
        except:
            pass

    # KPI Cards Data
    kpi = {
        "farmers": "2.4M",
        "avg_price": avg_price,
        "schemes": "15",
        "fpos": str(len(fpos) if fpos else "182")
    }

    # 🖼️ TEMPLATE RENDER (सारा Data Template को भेजो)
    template = env.get_template("index.html")
    html_content = template.render(
        title=APP_TITLE,
        today=today,
        colors=COLORS,
        prices=prices,
        weather=weather,
        news=news,
        kpi=kpi,
        # Farmers
        progressive_haryana=progressive_haryana,
        progressive_india=progressive_india,
        organic_farmers=organic_farmers,
        # Haryana Institutions
        haryana_institutions=haryana_institutions,
        kvks=kvks,
        fpos=fpos,
        # India Institutions
        india_institutions=india_institutions,
        icar_institutes=icar_institutes,
        # Checklist (New Feature)
        checklist=checklist
    )
    return HTMLResponse(content=html_content)
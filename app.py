from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests
from datetime import datetime
from config import APP_TITLE, COLORS, APIS

app = FastAPI()
templates = Jinja2Templates(directory="templates")

def get_prices():
    try:
        r = requests.get(APIS["mandi"], timeout=5)
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list) and len(data) > 0:
                return data[:6]
    except:
        pass
    # Fallback Data (अगर API डाउन हो तो ये दिखेगा)
    return [
        {"crop": "Wheat", "variety": "Lok-1", "price": 2450, "change": "+0.8%"},
        {"crop": "Paddy (Basmati)", "variety": "Pusa 1121", "price": 4280, "change": "+1.2%"},
        {"crop": "Maize", "variety": "Hybrid", "price": 2180, "change": "0.0%"},
        {"crop": "Mustard", "variety": "Local", "price": 5850, "change": "-0.5%"},
        {"crop": "Tomato", "variety": "Hybrid", "price": 2850, "change": "+7.2%"},
        {"crop": "Onion", "variety": "Red", "price": 3200, "change": "+2.1%"},
    ]

@app.get("/", response_class=HTMLResponse)
async def home(req: Request):
    # KPI Data (Static - आप चाहें तो इसे बदल सकते हैं)
    kpi_data = {
        "farmers": "2.4M",
        "avg_price": "₹2,450",
        "schemes": "15",
        "fpos": "182"
    }
    
    # Progressive Farmers
    progressive_farmers = [
        {"name": "Khema Ram Choudhary", "location": "Jaipur, Rajasthan", "specialty": "Hydroponics", "initials": "KC"},
        {"name": "Vinod Kumar", "location": "Karnal, Haryana", "specialty": "Dairy+Agri", "initials": "VK"},
        {"name": "Dharampal Kala", "location": "Chiri, Rohtak", "specialty": "Aquapreneur", "initials": "DK"},
        {"name": "Soniya Jain", "location": "Rajasthan", "specialty": "Integrated Farming", "initials": "SJ"},
    ]
    
    # Organic Farmers
    organic_farmers = [
        {"name": "Jitender Mann & Sarla", "location": "Haryana", "specialty": "Moringa", "initials": "JM"},
        {"name": "Omveer", "location": "Palwal, Haryana", "specialty": "Dairy+Organic", "initials": "OV"},
        {"name": "Gurdeep Singh", "location": "Nagoki, Sirsa", "specialty": "Turmeric", "initials": "GS"},
        {"name": "Radheyshyam Parihar", "location": "Agar Malwa, MP", "specialty": "Multi-crop", "initials": "RP"},
    ]
    
    # Institutions
    institutions = {
        "Research": ["HAU Hisar (Asia's biggest)", "NDRI Karnal (NIRF #2)", "Maharana Pratap Hort. Uni.", "CSSRI Karnal"],
        "KVKs": ["KVK Karnal", "KVK Hisar", "KVK Rohtak", "KVK Sirsa"],
        "FPOs": ["Satnali Organic FPC, Bhiwani", "Progressive Farmers FPC, Sonipat", "Jhorar FPC, Sirsa", "Badli FPC, Jhajjar"]
    }
    
    # News
    news_items = [
        "PM Kisan 19th Installment Released — ₹2,000 credited to 9.8cr farmers (24 July 2026)",
        "Haryana Crop Diversification Scheme 2026 — Incentives for maize & pulses",
        "Organic Certification Camp in Karnal — NPOP registration drive (26 July 2026)",
        "Micro-Irrigation Subsidy Extended — 75% subsidy for drip systems",
    ]

    return templates.TemplateResponse("index.html", {
        "request": req,
        "title": APP_TITLE,
        "today": datetime.now().strftime("%d %B %Y"),
        "colors": COLORS,
        "prices": get_prices(),
        "kpi": kpi_data,
        "progressive_farmers": progressive_farmers,
        "organic_farmers": organic_farmers,
        "institutions": institutions,
        "news": news_items
    })
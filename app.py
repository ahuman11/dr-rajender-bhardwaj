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
    return [
        {"crop": "Wheat", "variety": "Lok-1", "price": 2450, "change": "+0.8%"},
        {"crop": "Paddy", "variety": "Pusa 1121", "price": 4280, "change": "+1.2%"},
        {"crop": "Maize", "variety": "Hybrid", "price": 2180, "change": "0.0%"},
        {"crop": "Tomato", "variety": "Hybrid", "price": 2850, "change": "+7.2%"},
    ]

@app.get("/", response_class=HTMLResponse)
async def home(req: Request):
    return templates.TemplateResponse("index.html", {
        "request": req,
        "title": APP_TITLE,
        "today": datetime.now().strftime("%d %B %Y"),
        "colors": COLORS,
        "prices": get_prices()
    })
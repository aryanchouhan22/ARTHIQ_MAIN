import base64
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.session import get_db, init_db
from app.db.models import Shop, Customer, Item
from app.languages import SUPPORTED
from app.tools.ledger_tools import get_balance
from app.agent.pipeline import handle, SESSIONS
from app.voice.stt import transcribe
from app.voice.tts import speak
from app.voice.templates import say
from app.api.customers import router as customers_router

app = FastAPI(title="Arthiq")
app.include_router(customers_router)
from app.api.collect import router as collect_router
app.include_router(collect_router)
from app.api.inbox import router as inbox_router
app.include_router(inbox_router)
from app.api.insights import router as insights_router
app.include_router(insights_router)

# Customer management routes
from app.api.customers import router as customers_router
app.include_router(customers_router)

# Ensure a default shop exists for demo / testing
from app.db.models import Shop
db = next(get_db())
if not db.get(Shop, 1):
    shop = Shop(id=1, name='Demo Shop', language='hi-IN')
    db.add(shop)
    db.commit()
init_db()



@app.get("/")
def home():
    return FileResponse("web/index.html")


@app.get("/languages")
def languages():
    return [{"code": l.code, "name": l.name, "native": l.native} for l in SUPPORTED.values()]


class LanguageIn(BaseModel):
    shop_id: int = 1
    language: str


@app.post("/shop/language")
def set_language(body: LanguageIn, db: Session = Depends(get_db)):
    if body.language not in SUPPORTED:
        raise HTTPException(400, "Unsupported language")
    shop = db.get(Shop, body.shop_id)
    if not shop:
        raise HTTPException(404, "Shop not found")
    shop.language = body.language
    db.commit()
    return {"shop_id": shop.id, "language": shop.language}


@app.get("/ledger")
def ledger(shop_id: int = 1, db: Session = Depends(get_db)):
    rows = db.query(Customer).filter_by(shop_id=shop_id).all()
    return [{"id": c.id, "name": c.name, "language": c.preferred_language,
             "balance": get_balance(db, c.id), "credit_limit": c.credit_limit} for c in rows]


@app.get("/stock")
def stock(shop_id: int = 1, db: Session = Depends(get_db)):
    rows = db.query(Item).filter_by(shop_id=shop_id).all()
    return [{"id": i.id, "name": i.name, "unit": i.unit, "price": i.price,
             "stock_qty": i.stock_qty, "reorder_level": i.reorder_level} for i in rows]


def _turn(db, shop_id: int, transcript: str):
    shop = db.get(Shop, shop_id)
    if not transcript.strip():
        result = {"state": "error", "reply": say(shop.language, "err_generic")}
    else:
        result = handle(db, shop_id, transcript)
    audio = None
    try:
        audio = base64.b64encode(speak(result["reply"], shop.language)).decode()
    except Exception as e:                      # text is still shown if TTS fails
        print("TTS failed:", e)
    return {"transcript": transcript, **result, "audio_b64": audio, "language": shop.language}


@app.post("/voice/turn")
def voice_turn(audio: UploadFile = File(...), shop_id: int = Form(1),
               db: Session = Depends(get_db)):
    try:
        transcript, detected = transcribe(audio.file.read())
    except Exception as e:
        raise HTTPException(502, f"Speech-to-text failed: {e}")
    return _turn(db, shop_id, transcript) | {"detected_language": detected}


class TextIn(BaseModel):
    shop_id: int = 1
    text: str


@app.post("/text/turn")
def text_turn(body: TextIn, db: Session = Depends(get_db)):
    return _turn(db, body.shop_id, body.text)


@app.post("/session/reset")
def reset(shop_id: int = 1):
    SESSIONS.pop(shop_id, None)
    return {"ok": True}
# backend/app/main.py
from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional
import uvicorn
import os
import uuid
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
AUDIO_DIR = DATA_DIR / "audio"
DATA_DIR.mkdir(exist_ok=True)
AUDIO_DIR.mkdir(exist_ok=True)

app = FastAPI(title="KisanMitra MVP Backend")
# ensure DB initialized on startup and print DB path for debugging
@app.on_event("startup")
def startup_event():
    print("🚀 KisanMitra startup: initialising DB...")
    print("DB_PATH resolved to:", DB_PATH)
    init_db()
    # For debugging, show absolute path existence
    print("DB exists after init:", DB_PATH.exists())

DB_PATH = ROOT / "data" / "kisanmitra.db"
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS interactions (
        id TEXT PRIMARY KEY,
        language TEXT,
        crop TEXT,
        question TEXT,
        transcript TEXT,
        answer TEXT,
        sources TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id TEXT PRIMARY KEY,
        interaction_id TEXT,
        rating INTEGER,
        comment TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()

init_db()

class AskResponse(BaseModel):
    id: str
    language: str
    crop: str
    question: str
    transcript: Optional[str]
    answer: str
    sources: Optional[str]
    tts_path: Optional[str]

@app.post("/ask", response_model=AskResponse)
async def ask(
    language: str = Form(...),
    crop: str = Form("wheat"),
    question: Optional[str] = Form(None),
    audio: Optional[UploadFile] = File(None)
):
    transcript = None
    if audio is not None:
        ext = Path(audio.filename).suffix or ".wav"
        fname = f"{uuid.uuid4().hex}{ext}"
        fpath = AUDIO_DIR / fname
        with open(fpath, "wb") as f:
            data = await audio.read()
            f.write(data)
        transcript = run_asr_local(str(fpath), language=language)
        question_text = transcript
    else:
        question_text = question

    answer, sources = run_llm_answer(question_text, crop=crop, language=language)
    tts_path = produce_tts(answer, language=language)

    interaction_id = uuid.uuid4().hex
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO interactions (id, language, crop, question, transcript, answer, sources) VALUES (?,?,?,?,?,?,?)",
        (interaction_id, language, crop, question or None, transcript, answer, sources)
    )
    conn.commit()
    conn.close()

    return AskResponse(
        id=interaction_id,
        language=language,
        crop=crop,
        question=question_text,
        transcript=transcript,
        answer=answer,
        sources=sources,
        tts_path=str(tts_path) if tts_path else None
    )

@app.post("/feedback")
async def feedback(interaction_id: str = Form(...), rating: int = Form(...), comment: Optional[str] = Form(None)):
    fid = uuid.uuid4().hex
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO feedback (id, interaction_id, rating, comment) VALUES (?,?,?,?)", (fid, interaction_id, rating, comment))
    conn.commit()
    conn.close()
    return {"status": "ok", "id": fid}

# ---- Placeholder implementations ----- #
def run_asr_local(audio_path: str, language: str="hi") -> str:
    return "यहाँ ऑडियो ट्रांसक्रिप्ट दिखाई देगा" if language.startswith("hi") else "This is a stub transcript."

def run_llm_answer(question_text: str, crop:str="wheat", language:str="hi"):
    stub_answer = "संक्षेप: यह एक डेमो उत्तर है।\n\n1. कदम 1\n2. कदम 2\n\nस्रोत: राज्य कृषि विभाग।"
    sources = "state_agri_dept_url"
    return stub_answer, sources

def produce_tts(text: str, language: str="hi"):
    fname = f"{uuid.uuid4().hex}.txt"
    out = DATA_DIR / "tts"
    out.mkdir(exist_ok=True)
    fpath = out / fname
    fpath.write_text(text, encoding="utf-8")
    return fpath

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
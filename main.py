import json
import os
import secrets
import uuid
from contextlib import asynccontextmanager

import redis.asyncio as redis
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# ---------------- CONFIG ----------------
load_dotenv()

secret_key = os.getenv("GHOSTNOTE_SECRET_KEY")
if not secret_key:
    raise RuntimeError("Missing GHOSTNOTE_SECRET_KEY in .env")

cipher_suite = Fernet(secret_key.encode())

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6380")
r = redis.from_url(REDIS_URL, decode_responses=False)

RATE_LIMIT = 5
WINDOW_SECONDS = 60


# ---------------- LIFESPAN ----------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("GhostNote API started")
    yield
    await r.aclose()
    print("Redis connection closed")


app = FastAPI(title="GhostNote API", lifespan=lifespan)


# ---------------- MODELS ----------------
class NoteRequest(BaseModel):
    content: str
    ttl: int = 360


# ---------------- RATE LIMIT ----------------
async def check_rate_limit(ip: str):
    key = f"rate:{ip}"

    async with r.pipeline(transaction=True) as pipe:
        pipe.incr(key)
        pipe.ttl(key)
        current, ttl = await pipe.execute()

    if ttl == -1:
        await r.expire(key, WINDOW_SECONDS)

    if current > RATE_LIMIT:
        raise HTTPException(
            status_code=429, detail="Too many requests. Try again later."
        )


# ---------------- CREATE NOTE ----------------
@app.post("/api/notes")
async def create_note(request: NoteRequest, http_request: Request):
    client = http_request.client
    ip = client.host if client else "unknown"
    await check_rate_limit(ip)

    note_id = str(uuid.uuid4())
    access_token = secrets.token_urlsafe(16)

    payload = {"content": request.content, "token": access_token}
    encrypted_payload = cipher_suite.encrypt(json.dumps(payload).encode())

    await r.set(name=note_id, value=encrypted_payload, ex=request.ttl)

    return {
        "note_id": note_id,
        "access_token": access_token,
        "link": f"http://localhost:8000/notes/{note_id}?token={access_token}",
    }


# ---------------- READ NOTE ----------------
@app.get("/api/notes/{note_id}")
async def read_note(note_id: str, token: str = Query(...)):
    encrypted_payload = await r.execute_command("GETDEL", note_id)

    if encrypted_payload is None:
        raise HTTPException(status_code=404, detail="Note not found or already read.")

    try:
        payload = json.loads(cipher_suite.decrypt(encrypted_payload).decode())
    except Exception:
        raise HTTPException(status_code=500, detail="Decryption failed.")

    if payload["token"] != token:
        raise HTTPException(status_code=404, detail="Note not found or already read.")

    return {"note_id": note_id, "content": payload["content"], "status": "destroyed"}


# ---------------- FRONTEND ----------------
@app.get("/notes/{note_id}")
async def serve_note_page(note_id: str):
    return FileResponse("static/index.html")


app.mount("/", StaticFiles(directory="static", html=True), name="static")


from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os

app = FastAPI(title="TRI-D V39 Central")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HF_TOKEN = os.getenv("HF_TOKEN", "")
MODEL_ID = os.getenv("MODEL_ID", "black-forest-labs/FLUX.1-schnell")

@app.get("/")
async def root():
    return {"status": "TRI-D V39 Central LIVE", "owner": "asishtoppo84", "model": MODEL_ID, "mode": "free-24-7"}

@app.get("/health")
async def health():
    return {"ok": True, "service": "tri-d-v39-central"}

@app.post("/generate")
async def generate(req: Request):
    data = await req.json()
    prompt = data.get("prompt", "")
    # For now proxy info - actual HF call done by frontend fallback if token missing
    # This endpoint will be expanded to call HF Inference
    return {"status": "received", "prompt": prompt, "central": "asishtoppo84/tri-d-v39-central", "next": "Use HF_TOKEN env for direct FLUX"}

@app.get("/config")
async def config():
    return {"model": MODEL_ID, "has_token": bool(HF_TOKEN), "repo": "asishtoppo84/tri-d-v39-central"}

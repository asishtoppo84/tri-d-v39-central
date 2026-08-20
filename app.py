from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import requests
import base64

app = FastAPI(title="TRI-D V39 Central")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

HF_TOKEN = os.getenv("HF_TOKEN", "")
MODEL_ID = os.getenv("MODEL_ID", "black-forest-labs/FLUX.1-schnell")

@app.get("/")
async def root():
    return {"status": "TRI-D V39 Central LIVE", "owner": "asishtoppo84", "model": MODEL_ID, "mode": "free-24-7", "hf_token_set": bool(HF_TOKEN)}

@app.get("/health")
async def health():
    return {"ok": True, "service": "tri-d-v39-central", "hf_ready": bool(HF_TOKEN)}

@app.post("/generate")
@app.post("/generate-flux")
async def generate(req: Request):
    try:
        body = await req.json()
        prompt = body.get("prompt", "a beautiful landscape")
    except:
        prompt = "a beautiful landscape"
    if not HF_TOKEN:
        return JSONResponse({"status": "error", "message": "HF_TOKEN missing in Render", "prompt": prompt})
    API_URL = f"https://api-inference.huggingface.co/models/{MODEL_ID}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    try:
        resp = requests.post(API_URL, headers=headers, json={"inputs": prompt}, timeout=90)
        if resp.status_code == 200 and "image" in resp.headers.get("content-type", ""):
            b64 = base64.b64encode(resp.content).decode()
            return {"status": "success", "owner": "asishtoppo84", "model": MODEL_ID, "prompt": prompt, "image_base64": f"data:image/jpeg;base64,{b64}"}
        else:
            return {"status": "hf_response", "code": resp.status_code, "detail": resp.text[:800], "prompt": prompt, "note": "If 503 wait 20s retry"}
    except Exception as e:
        return JSONResponse({"status": "exception", "error": str(e), "prompt": prompt})


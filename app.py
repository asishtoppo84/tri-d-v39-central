import os, base64, requests
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="TRI-D V39 Central")

HF_TOKEN = os.getenv("HF_TOKEN")
MODEL_ID = "stabilityai/stable-diffusion-2-1"
API_URL = f"https://api-inference.huggingface.co/models/{MODEL_ID}"

class PromptRequest(BaseModel):
    prompt: str = "a beautiful Indian girl, cyberpunk city, neon lights, ultra detailed"

@app.get("/", response_class=HTMLResponse)
def root():
    return f"""
    <h2>TRI-D V39 Central LIVE 🔥 FINAL</h2>
    <p>Model: {MODEL_ID}</p>
    <p>Endpoint: api-inference.huggingface.co (WORKING)</p>
    <p>HF_TOKEN: {bool(HF_TOKEN)}</p>
    <p><a href="/docs">Go to /docs</a></p>
    """

@app.get("/status")
def status():
    return {"status": "LIVE", "model": MODEL_ID, "hf_token_set": bool(HF_TOKEN)}

@app.post("/generate")
def generate(req: PromptRequest):
    if not HF_TOKEN:
        return {"error": "HF_TOKEN missing"}

    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    try:
        # HF Inference wants {"inputs": "..."}
        resp = requests.post(API_URL, headers=headers, json={"inputs": req.prompt}, timeout=120)

        if resp.status_code == 200 and "image" in resp.headers.get("content-type",""):
            b64 = base64.b64encode(resp.content).decode()
            return {"image_base64": b64, "prompt": req.prompt}

        # If returns JSON error or waiting
        try:
            j = resp.json()
            return {"error": f"HF API {resp.status_code}", "details": str(j)[:500], "prompt": req.prompt, "note": "Wait 20s and retry if model loading"}
        except:
            return {"error": f"HF API {resp.status_code}", "details": resp.text[:500]}

    except Exception as e:
        return {"error": "Exception", "details": str(e)}

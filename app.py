import os
import base64
import requests
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="TRI-D V39 Central")

# --- CONFIG ---
HF_TOKEN = os.getenv("HF_TOKEN")
MODEL_ID = "black-forest-labs/FLUX.1-schnell"
API_URL = f"https://router.huggingface.co/fal-ai/{MODEL_ID}"

class PromptRequest(BaseModel):
    prompt: str = "a beautiful Indian girl, cyberpunk city, neon lights, ultra detailed"

@app.get("/", response_class=HTMLResponse)
def root():
    return f"""
    <h2>TRI-D V39 Central LIVE 🔥</h2>
    <p>Owner: asishtoppo84</p>
    <p>Model: {MODEL_ID}</p>
    <p>Provider: fal-ai (FIXED)</p>
    <p>Mode: free-24-7</p>
    <p>HF_TOKEN: {bool(HF_TOKEN)}</p>
    <p><a href="/docs">Go to /docs to Generate Image</a></p>
    """

@app.get("/status")
def status():
    return {
        "status": "TRI-D V39 Central LIVE",
        "owner": "asishtoppo84",
        "model": MODEL_ID,
        "provider": "fal-ai",
        "mode": "free-24-7",
        "hf_token_set": bool(HF_TOKEN)
    }

@app.post("/generate")
def generate(req: PromptRequest):
    if not HF_TOKEN:
        return {"error": "HF_TOKEN not set in Render env"}

    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        resp = requests.post(API_URL, headers=headers, json={"inputs": req.prompt}, timeout=120)

        # If direct image
        if resp.status_code == 200 and "image" in resp.headers.get("content-type",""):
            b64 = base64.b64encode(resp.content).decode()
            return {"image_base64": b64, "prompt": req.prompt, "model": MODEL_ID}

        data = resp.json() if resp.content else {}

        # fal-ai format: handle url or b64
        if isinstance(data, dict):
            if "images" in data and len(data["images"]) > 0:
                first = data["images"][0]
                if "url" in first:
                    img_resp = requests.get(first["url"], timeout=60)
                    b64 = base64.b64encode(img_resp.content).decode()
                    return {"image_base64": b64, "prompt": req.prompt, "model": MODEL_ID}
                if "b64_json" in first:
                    return {"image_base64": first["b64_json"], "prompt": req.prompt}
                if "image" in first:
                    return {"image_base64": first["image"], "prompt": req.prompt}

        if resp.status_code!= 200:
            return {"error": f"HF API {resp.status_code}", "details": str(data), "prompt": req.prompt}

        return {"result": data, "prompt": req.prompt}

    except Exception as e:
        return {"error": "Exception", "details": str(e), "prompt": req.prompt}

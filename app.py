import os
import base64
import requests
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="TRI-D V39 Central")

HF_TOKEN = os.getenv("HF_TOKEN")
MODEL_ID = "stabilityai/stable-diffusion-xl-base-1.0"
API_URL = f"https://router.huggingface.co/hf-inference/models/{MODEL_ID}"

class PromptRequest(BaseModel):
    prompt: str = "a beautiful Indian girl, cyberpunk city, neon lights"

@app.get("/")
def root():
    return {
        "status": "TRI-D V39 Central LIVE",
        "owner": "asishtoppo84",
        "model": MODEL_ID,
        "mode": "free-24-7",
        "hf_token_set": bool(HF_TOKEN)
    }

@app.post("/generate")
def generate(req: PromptRequest):
    prompt = req.prompt
    if not HF_TOKEN:
        return {"error": "HF_TOKEN not set in Render env"}

    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        # Call HF
        resp = requests.post(
            API_URL,
            headers=headers,
            json={"inputs": prompt},
            timeout=120
        )
        
        # If HF returns image directly
        if resp.status_code == 200 and "image" in resp.headers.get("content-type", ""):
            img_b64 = base64.b64encode(resp.content).decode()
            return {"image_base64": img_b64, "prompt": prompt}
        
        # If HF returns JSON with error
        data = resp.json() if resp.content else {}
        
        if resp.status_code != 200:
            return {
                "error": f"HF API {resp.status_code}",
                "details": str(data),
                "prompt": prompt
            }
        
        # Sometimes returns base64 inside JSON
        return {"result": data, "prompt": prompt, "image_base64": str(data)[:100]}

    except Exception as e:
        return {"error": "Exception", "details": str(e), "prompt": prompt}

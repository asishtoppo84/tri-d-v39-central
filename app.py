import os, base64, requests
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="TRI-D V39 Central")

HF_TOKEN = os.getenv("HF_TOKEN")
MODEL_ID = "black-forest-labs/FLUX.1-schnell"
API_URL = f"https://router.huggingface.co/fal-ai/{MODEL_ID}"

class PromptRequest(BaseModel):
    prompt: str = "a beautiful Indian girl, cyberpunk city, neon lights, ultra detailed"

@app.get("/")
def root():
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
        return {"error": "HF_TOKEN not set"}

    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        resp = requests.post(API_URL, headers=headers, json={"inputs": req.prompt}, timeout=120)

        # fal-ai returns image bytes or json
        ctype = resp.headers.get("content-type","")
        if resp.status_code == 200 and "image" in ctype:
            b64 = base64.b64encode(resp.content).decode()
            return {"image_base64": b64, "prompt": req.prompt}

        # try parse json
        try:
            data = resp.json()
        except:
            data = {"raw": resp.text[:500]}

        # If fal-ai returns {images: [{url, b64}]}
        if isinstance(data, dict) and "images" in data:
            # download first image url if needed
            img_data = data["images"][0]
            if "url" in img_data:
                img_resp = requests.get(img_data["url"])
                b64 = base64.b64encode(img_resp.content).decode()
                return {"image_base64": b64, "prompt": req.prompt}
            if "b64_json" in img_data:
                return {"image_base64": img_data["b64_json"], "prompt": req.prompt}

        if resp.status_code!= 200:
            return {"error": f"HF API {resp.status_code}", "details": str(data), "prompt": req.prompt}

        return {"result": data, "prompt": req.prompt}

    except Exception as e:
        return {"error": "Exception", "details": str(e), "prompt": req.prompt}

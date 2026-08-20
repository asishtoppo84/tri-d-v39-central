import os, base64, requests
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="TRI-D V39 Central")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

MODEL_ID = "black-forest-labs/FLUX.1-schnell"
HF_TOKEN = os.getenv("HF_TOKEN", "")

@app.get("/")
def root():
    return {"status": "TRI-D V39 Central LIVE", "owner": "asishtoppo84", "model": MODEL_ID, "mode": "free-24-7", "hf_token_set": bool(HF_TOKEN)}

@app.get("/health")
def health():
    return {"status": "ok", "hf_token_set": bool(HF_TOKEN)}

@app.get("/config")
def config():
    return {"model": MODEL_ID, "hf_token_set": bool(HF_TOKEN)}

@app.post("/generate")
async def generate(request: Request):
    try:
        try:
            body = await request.json()
            prompt = body.get("prompt", "a beautiful landscape") if isinstance(body, dict) else "a beautiful landscape"
        except:
            prompt = "a beautiful landscape"

        if not HF_TOKEN:
            return JSONResponse(status_code=500, content={"error": "HF_TOKEN missing in Render Env. Add HF_TOKEN env var."})

        
# becomes
        API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}

        resp = requests.post(API_URL, headers=headers, json={"inputs": prompt}, timeout=90)

        if resp.status_code!= 200:
            return JSONResponse(status_code=resp.status_code, content={"error": f"HF API {resp.status_code}", "details": resp.text[:500], "prompt": prompt})

        content_type = resp.headers.get("content-type", "")
        if "image" in content_type:
            b64 = base64.b64encode(resp.content).decode()
            return {"status": "success", "owner": "asishtoppo84", "model": MODEL_ID, "prompt": prompt, "image_base64": f"data:image/jpeg;base64,{b64}"}
        else:
            return {"status": "hf_returned_json", "hf_response": resp.text[:1000], "prompt": prompt}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "details": str(e)})

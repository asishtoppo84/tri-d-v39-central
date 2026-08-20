from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os, base64, requests

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class GenReq(BaseModel):
    prompt: str
    width: int = 768
    height: int = 768
    steps: int = 4

HF_TOKEN = os.getenv("HF_TOKEN", "")
MODEL = "black-forest-labs/FLUX.1-schnell"

@app.get("/")
def health():
    return {"status": "TRI-D V39 Central LIVE", "owner": "asishtoppo84", "model": MODEL}

@app.post("/generate")
@app.post("/generate-flux")
def generate(req: GenReq):
    if not HF_TOKEN:
        return {"status": "error", "error": "Set HF_TOKEN env var in Render"}
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {"inputs": req.prompt, "parameters": {"width": req.width, "height": req.height, "num_inference_steps": req.steps}}
    r = requests.post(f"https://api-inference.huggingface.co/models/{MODEL}", headers=headers, json=payload, timeout=90)
    if r.status_code != 200:
        return {"status": "error", "error": r.text[:500]}
    b64 = base64.b64encode(r.content).decode()
    return {"status": "success", "image_base64": f"data:image/jpeg;base64,{b64}", "prompt": req.prompt}

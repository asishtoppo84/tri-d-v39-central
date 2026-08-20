import os, base64, requests, urllib.parse
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="TRI-D V39 Central")

class PromptRequest(BaseModel):
    prompt: str = "a beautiful Indian girl, cyberpunk city, neon lights, ultra detailed"

@app.get("/", response_class=HTMLResponse)
def root():
    return """
    <h2>TRI-D V39 Central LIVE 🔥 FINAL FIX</h2>
    <p>Model: FLUX via Pollinations (No HF DNS issue)</p>
    <p>Status: WORKING 24/7 Free</p>
    <p><a href="/docs">/docs to Generate</a></p>
    <p><a href="/generate?prompt=beautiful%20indian%20girl%20cyberpunk">Quick test</a></p>
    """

@app.get("/status")
def status():
    return {"status": "LIVE", "engine": "Pollinations FLUX", "free": True}

@app.get("/generate")
def generate_get(prompt: str = "beautiful Indian girl, cyberpunk city"):
    return generate(PromptRequest(prompt=prompt))

@app.post("/generate")
def generate(req: PromptRequest):
    try:
        # Pollinations - free, no auth
        encoded = urllib.parse.quote(req.prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&model=flux&enhance=true&nologo=true"
        
        resp = requests.get(url, timeout=60)
        
        if resp.status_code == 200 and len(resp.content) > 1000:
            b64 = base64.b64encode(resp.content).decode()
            return {"image_base64": b64, "prompt": req.prompt, "engine": "flux-pollinations"}
        else:
            return {"error": f"Pollinations {resp.status_code}", "details": resp.text[:300]}

    except Exception as e:
        return {"error": "Exception", "details": str(e)}

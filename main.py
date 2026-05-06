import os

# [COLD START CALIBRATION] 
# Explicitly purging API keys from the environment to force Vertex AI (Onyx Prime) authentication.
os.environ.pop("GOOGLE_API_KEY", None)
os.environ.pop("GEMINI_API_KEY", None)

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import ValidationError
import time

from models import AthleteBiometrics, EngineOutput
from engine import AtlasEngine, InitializationError

app = FastAPI(title="The Archetype Atlas API")

# [DIAGNOSTIC MIDDLEWARE] 
# Monitoring request lifecycle to prevent/diagnose 499 CANCELLED errors.
@app.middleware("http")
async def diagnostic_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    print(f"Rowen: 'Request processed in {process_time:.4f}s. Path: {request.url.path}'")
    return response

# Global engine instance
try:
    engine = AtlasEngine()
except InitializationError as e:
    print(f"Rowen: 'System alert - Engine core offline.' Error: {e}")
    engine = None

@app.get("/")
async def serve_ui():
    """Serves the Onyx Liquid Glass frontend."""
    return FileResponse("index.html")

@app.post("/analyze", response_model=EngineOutput)
async def analyze_biometrics(user_data: AthleteBiometrics):
    """
    State-less biometric analysis endpoint.
    Processes user data in-memory and returns Rowen's synthesized insight.
    """
    if engine is None:
        raise HTTPException(
            status_code=503, 
            detail="Atlas Engine is not initialized. Verify GOOGLE_API_KEY in .env."
        )
    
    try:
        result = engine.generate_insight(user_data)
        return result
    except Exception as e:
        print(f"Rowen: 'Synthesis failure.' Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

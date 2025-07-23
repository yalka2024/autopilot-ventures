from fastapi import FastAPI
from fastapi.responses import JSONResponse
import os

app = FastAPI(title="AutoPilot Ventures Test", version="1.0.0")

@app.get("/")
async def root():
    return {"message": "AutoPilot Ventures Test - Deployment Successful!"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "autopilot-ventures-test"}

@app.get("/status")
async def status():
    return {
        "status": "operational",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port) 
"""
Minimal test server for Cloud Run deployment
"""

import os
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World from AutoPilot Ventures!"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting test server on port {port}")
    # Use the correct uvicorn format for Cloud Run
    uvicorn.run("test_server:app", host="0.0.0.0", port=port, log_level="info") 
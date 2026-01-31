import sys 
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from fastapi import FastAPI
from src.routers.auth import router as auth_router


app = FastAPI(title="Auth Service")

app.include_router(auth_router)

@app.get("/health")
def health():
    return {"status": "ok"}
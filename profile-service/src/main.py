from fastapi import FastAPI
from src.routers.me import router as me_router

# from api.health import router as health_router

app = FastAPI(title="Profile Service")

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(me_router)

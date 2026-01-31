from fastapi import APIRouter
from src.db.session import db_ping
from src.core.deps import redis_ping

router = APIRouter(tags=["health"])

@router.get("/health")
def health():
    return {
        "status": "ok",
        "db": "ok" if db_ping() else "down",
        "redis": "ok" if redis_ping() else "down",
    }

import sys
import os
# sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.routers.me import router as get_me

# Add /app/src to sys.path (Docker working dir is /app)
from fastapi import FastAPI
from routers import me

# from api.health import router as health_router

app = FastAPI(title="Profile Service")

app.include_router(get_me)
# app.include_router(get_me.router)

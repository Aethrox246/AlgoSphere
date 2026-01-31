from fastapi import FastAPI
from routers import me
from api.health import router as health_router

app = FastAPI(title="Profile Service")

app.include_router(health_router)
app.include_router(me.router)

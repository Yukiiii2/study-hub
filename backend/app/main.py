from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.auth import router as auth_router
from app.api.subjects import router as subjects_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(title="Study Hub API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["Content-Type", "Authorization"],
)
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(subjects_router)

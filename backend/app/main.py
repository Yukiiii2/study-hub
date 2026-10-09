from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.auth import router as auth_router
from app.api.subjects import router as subjects_router
from app.api.topics import router as topics_router
from app.api.videos import router as videos_router
from app.api.planner import router as planner_router
from app.api.dashboard import router as dashboard_router
from app.api.resources import router as resources_router
from app.api.resource_body_limit import ResourceUploadBodyLimit
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(title="Study Hub API", version="0.1.0")
app.add_middleware(ResourceUploadBodyLimit)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "PATCH", "POST", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(subjects_router)
app.include_router(topics_router)
app.include_router(videos_router)
app.include_router(planner_router)
app.include_router(dashboard_router)
app.include_router(resources_router)

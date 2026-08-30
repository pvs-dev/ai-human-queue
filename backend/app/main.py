import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.database import engine, Base, SessionLocal
from app.seeds import seed_skills, seed_demo_items
from app.scheduler import start_scheduler, shutdown_scheduler
from app.api import queue, tasks, skills, events, settings as settings_api

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_skills(db)
        seed_demo_items(db)
    finally:
        db.close()
    
    start_scheduler()
    yield
    # Shutdown
    shutdown_scheduler()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(queue.router, prefix="/api/v1/queue", tags=["Queue / Human-in-the-Loop"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["Tasks"])
app.include_router(skills.router, prefix="/api/v1/skills", tags=["Skills"])
app.include_router(settings_api.router, prefix="/api/v1/settings", tags=["Settings"])
app.include_router(events.router, prefix="/api/v1/events", tags=["Realtime Events"])

@app.get("/api/v1/health")
def health_check():
    return {"status": "ok", "app": settings.PROJECT_NAME}

# Serve static frontend build if present
frontend_dist = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static")

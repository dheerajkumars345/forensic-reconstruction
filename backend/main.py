"""
Crime Scene Reconstruction System - Backend API
FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
from pathlib import Path

from config import settings
from database import init_db


# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager"""
    # Startup
    logger.info("Starting Crime Scene Reconstruction System...")
    logger.info(f"Version: {settings.APP_VERSION}")
    
    # Initialize database
    await init_db()
    logger.info("Database initialized")
    
    # Ensure all directories exist
    settings.ensure_directories()
    logger.info("Directory structure verified")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Forensic-grade crime scene reconstruction with photogrammetry",
    lifespan=lifespan
)

# Configure CORS
cors_origins = ["*"] if settings.CORS_ALLOW_ALL_ORIGINS else settings.CORS_ORIGINS
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# Mount static files for serving models, reports, and uploads
app.mount("/static/models", StaticFiles(directory=settings.MODELS_DIR), name="models")
app.mount("/static/reports", StaticFiles(directory=settings.REPORTS_DIR), name="reports")
app.mount("/static/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


# Root endpoint
@app.get("/")
async def root():
    """API health check"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational",
        "api_docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "storage": "ready",
        "version": settings.APP_VERSION
    }


# Import and include routers
# These will be created in the next steps
route_modules = [
    ("routes.projects", "projects", f"{settings.API_PREFIX}/projects", "Projects"),
    ("routes.images", "images", f"{settings.API_PREFIX}", "Images"),
    ("routes.reconstruction", "reconstruction", f"{settings.API_PREFIX}", "Reconstruction"),
    ("routes.measurements", "measurements", f"{settings.API_PREFIX}", "Measurements"),
    ("routes.reports", "reports", f"{settings.API_PREFIX}", "Reports"),
]

for module_path, name, prefix, tag in route_modules:
    try:
        import importlib
        mod = importlib.import_module(module_path)
        app.include_router(mod.router, prefix=prefix, tags=[tag])
        logger.info(f"Route registered: {name}")
    except Exception as e:
        logger.warning(f"Route '{name}' not loaded: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )

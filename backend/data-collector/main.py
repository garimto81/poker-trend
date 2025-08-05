from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
from contextlib import asynccontextmanager
import os
from datetime import datetime

from src.config.settings import settings
from src.api.youtube_routes import router as youtube_router

# Import logger (we'll create this)
import logging
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("🚀 Starting Data Collector service...")
    yield
    # Shutdown
    logger.info("🛑 Shutting down Data Collector service...")

# Create FastAPI app with lifespan
app = FastAPI(
    title="Poker Trend Data Collector",
    description="YouTube poker trend data collection and analysis service",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(youtube_router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Poker Trend Data Collector",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "data-collector",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
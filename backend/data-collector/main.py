from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
from contextlib import asynccontextmanager
import os
from datetime import datetime

from src.config.settings import settings
from src.config.database import init_databases, close_databases
from src.collectors.trend_collector import TrendCollector
from src.utils.logger import logger

# Global trend collector instance
trend_collector = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global trend_collector
    
    # Startup
    logger.info("🚀 Starting Data Collector service...")
    
    try:
        # Initialize databases
        await init_databases()
        logger.info("✅ Databases initialized")
        
        # Initialize trend collector
        trend_collector = TrendCollector()
        await trend_collector.initialize()
        logger.info("✅ Trend collector initialized")
        
        # Start background tasks
        asyncio.create_task(trend_collector.start_monitoring())
        logger.info("✅ Background monitoring started")
        
    except Exception as e:
        logger.error(f"❌ Failed to start service: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Data Collector service...")
    
    try:
        if trend_collector:
            await trend_collector.stop_monitoring()
        await close_databases()
        logger.info("✅ Service shutdown completed")
        
    except Exception as e:
        logger.error(f"❌ Error during shutdown: {e}")

# Create FastAPI app with lifespan
app = FastAPI(
    title="Poker Trend Data Collector",
    description="Real-time poker trend data collection and analysis service",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
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

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "data-collector",
        "version": "1.0.0"
    }

@app.get("/status")
async def get_status():
    """Get collector status"""
    if not trend_collector:
        raise HTTPException(status_code=503, detail="Trend collector not initialized")
    
    return await trend_collector.get_status()

@app.post("/collect/trends")
async def trigger_trend_collection(background_tasks: BackgroundTasks):
    """Manually trigger trend collection"""
    if not trend_collector:
        raise HTTPException(status_code=503, detail="Trend collector not initialized")
    
    background_tasks.add_task(trend_collector.collect_all_trends)
    
    return {
        "message": "Trend collection triggered",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/collect/youtube")
async def trigger_youtube_collection(background_tasks: BackgroundTasks):
    """Manually trigger YouTube data collection"""
    if not trend_collector:
        raise HTTPException(status_code=503, detail="Trend collector not initialized")
    
    background_tasks.add_task(trend_collector.collect_youtube_trends)
    
    return {
        "message": "YouTube collection triggered",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/collect/twitter")
async def trigger_twitter_collection(background_tasks: BackgroundTasks):
    """Manually trigger Twitter data collection"""
    if not trend_collector:
        raise HTTPException(status_code=503, detail="Trend collector not initialized")
    
    background_tasks.add_task(trend_collector.collect_twitter_trends)
    
    return {
        "message": "Twitter collection triggered",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/collect/reddit")
async def trigger_reddit_collection(background_tasks: BackgroundTasks):
    """Manually trigger Reddit data collection"""
    if not trend_collector:
        raise HTTPException(status_code=503, detail="Trend collector not initialized")
    
    background_tasks.add_task(trend_collector.collect_reddit_trends)
    
    return {
        "message": "Reddit collection triggered",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/trends/latest")
async def get_latest_trends(limit: int = 10):
    """Get latest detected trends"""
    if not trend_collector:
        raise HTTPException(status_code=503, detail="Trend collector not initialized")
    
    return await trend_collector.get_latest_trends(limit)

@app.get("/metrics")
async def get_metrics():
    """Get collection metrics"""
    if not trend_collector:
        raise HTTPException(status_code=503, detail="Trend collector not initialized")
    
    return await trend_collector.get_metrics()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info"
    )
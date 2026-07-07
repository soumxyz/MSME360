"""FastAPI application setup for Risk Intelligence Agent.

This module initializes the FastAPI application with middleware, routes,
and startup/shutdown handlers.

**Validates Requirements**: 12.1, 12.8, 13.2, 13.6, 13.7
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import sys

from .routes import router
from agents.risk_intelligence_agent.xgboost_model import load_model
from agents.risk_intelligence_agent.cache import initialize_cache
from agents.risk_intelligence_agent.audit import get_audit_logger


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "component": "%(name)s", "message": "%(message)s"}',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


# Global resources
app_state = {
    "model": None,
    "cache": None,
    "audit_logger": None
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events.
    
    Args:
        app: FastAPI application instance
    """
    # Startup
    logger.info("Starting Risk Intelligence Agent API...")
    
    try:
        # Load ML model
        logger.info("Loading ML model...")
        app_state["model"] = load_model()
        logger.info("ML model loaded successfully")
        
        # Initialize cache
        logger.info("Initializing cache...")
        app_state["cache"] = initialize_cache()
        logger.info("Cache initialized successfully")
        
        # Initialize audit logger
        logger.info("Initializing audit logger...")
        app_state["audit_logger"] = get_audit_logger()
        logger.info("Audit logger initialized successfully")
        
        logger.info("Risk Intelligence Agent API started successfully")
        
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Risk Intelligence Agent API...")
    
    # Clean up resources
    app_state["model"] = None
    app_state["cache"] = None
    app_state["audit_logger"] = None
    
    logger.info("Risk Intelligence Agent API shut down successfully")


# Create FastAPI application
app = FastAPI(
    title="Risk Intelligence Agent",
    description="AI-assisted credit risk evaluation for MSME lending using alternate data sources",
    version="1.0.0",
    lifespan=lifespan
)


# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Mount routes
app.include_router(router, prefix="/api/v1", tags=["risk-assessment"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Risk Intelligence Agent",
        "version": "1.0.0",
        "status": "running",
        "api_docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

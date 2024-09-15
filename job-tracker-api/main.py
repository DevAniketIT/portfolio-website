"""
FastAPI application initialization and configuration.

This module sets up the main FastAPI application instance with proper
configuration, middleware, and routing.
"""

from fastapi import FastAPI
import uvicorn
import os
from dotenv import load_dotenv

# Import middleware setup functions
from middleware import (
    setup_middleware,
    add_health_endpoint,
    setup_exception_handlers
)

# Import enhanced documentation
from docs import setup_enhanced_docs

# Load environment variables
load_dotenv()

# Create FastAPI instance
app = FastAPI(
    title="Job Application Tracker API",
    description="A comprehensive API for tracking job applications with CRUD operations, filtering, and analytics",
    version="1.0.0",
    docs_url=None,  # We'll use custom docs
    redoc_url="/redoc"
)

# Set up all middleware components
setup_middleware(app)

# Add exception handlers
setup_exception_handlers(app)

# Add enhanced health check endpoint
add_health_endpoint(app)

# Import routers
from routers import applications, tracking

# Setup enhanced documentation
setup_enhanced_docs(app)

# Include routers
app.include_router(applications.router, prefix="/api")
app.include_router(tracking.router, prefix="/api")

@app.get("/")
async def root():
    """Root endpoint providing API information."""
    return {
        "message": "Job Application Tracker API",
        "version": "1.0.0",
        "status": "active",
        "docs": "/docs",
        "endpoints": {
            "applications": "/api/applications",
            "tracking": "/api/tracking",
            "health": "/health"
        }
    }

if __name__ == "__main__":
    # For development purposes
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )

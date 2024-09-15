"""
FastAPI middleware for security and monitoring.

This module provides comprehensive middleware components for:
- CORS configuration for cross-origin requests
- API key authentication (optional, configurable via environment)
- Request logging for debugging and monitoring
- Rate limiting to prevent abuse
- Exception handling for consistent error responses
- Health check functionality
"""

import time
import logging
from typing import Dict, Optional, Callable, Any
from datetime import datetime, timedelta
import json
import os
from collections import defaultdict
from threading import Lock

from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api_requests.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# API Key configuration
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Rate limiting storage (in production, use Redis or similar)
rate_limit_storage: Dict[str, list] = defaultdict(list)
rate_limit_lock = Lock()

# Configuration from environment variables
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # seconds
API_KEY_REQUIRED = os.getenv("API_KEY_REQUIRED", "false").lower() == "true"
VALID_API_KEY = os.getenv("API_KEY", None)


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    timestamp: datetime
    uptime: Optional[float] = None
    version: str = "1.0.0"


class ErrorResponse(BaseModel):
    """Standard error response model."""
    error: str
    message: str
    timestamp: datetime
    path: Optional[str] = None
    status_code: int


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware to prevent abuse."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Any:
        client_ip = request.client.host if request.client else "unknown"
        
        # Skip rate limiting for health check
        if request.url.path == "/health":
            return await call_next(request)
        
        current_time = time.time()
        
        with rate_limit_lock:
            # Clean old requests
            rate_limit_storage[client_ip] = [
                req_time for req_time in rate_limit_storage[client_ip]
                if current_time - req_time < RATE_LIMIT_WINDOW
            ]
            
            # Check rate limit
            if len(rate_limit_storage[client_ip]) >= RATE_LIMIT_REQUESTS:
                logger.warning(f"Rate limit exceeded for IP: {client_ip}")
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content=ErrorResponse(
                        error="Rate Limit Exceeded",
                        message=f"Maximum {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_WINDOW} seconds allowed",
                        timestamp=datetime.utcnow(),
                        path=str(request.url.path),
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS
                    ).dict()
                )
            
            # Add current request
            rate_limit_storage[client_ip].append(current_time)
        
        return await call_next(request)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging all incoming requests and responses."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Any:
        start_time = time.time()
        client_ip = request.client.host if request.client else "unknown"
        
        # Log request
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"from {client_ip} - Query: {dict(request.query_params)}"
        )
        
        # Process request
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log response
            logger.info(
                f"Response: {response.status_code} "
                f"for {request.method} {request.url.path} "
                f"in {process_time:.3f}s"
            )
            
            # Add processing time header
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as exc:
            process_time = time.time() - start_time
            logger.error(
                f"Error: {str(exc)} "
                f"for {request.method} {request.url.path} "
                f"in {process_time:.3f}s"
            )
            raise


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware for consistent exception handling."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Any:
        try:
            return await call_next(request)
        except HTTPException:
            # Re-raise HTTP exceptions to be handled by FastAPI
            raise
        except Exception as exc:
            logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse(
                    error="Internal Server Error",
                    message="An unexpected error occurred. Please try again later.",
                    timestamp=datetime.utcnow(),
                    path=str(request.url.path),
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                ).dict()
            )


async def get_api_key(api_key: Optional[str] = Depends(api_key_header)) -> Optional[str]:
    """
    Extract and validate API key from request headers.
    
    Args:
        api_key: API key from request header
        
    Returns:
        Validated API key or None if not required
        
    Raises:
        HTTPException: If API key is required but invalid/missing
    """
    if not API_KEY_REQUIRED:
        return api_key
    
    if not api_key or api_key != VALID_API_KEY:
        logger.warning(f"Invalid API key attempted: {api_key}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key"
        )
    
    return api_key


def configure_cors(app: FastAPI) -> None:
    """
    Configure CORS middleware with appropriate settings.
    
    Args:
        app: FastAPI application instance
    """
    # Get CORS settings from environment
    cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
    cors_methods = os.getenv("CORS_METHODS", "GET,POST,PUT,DELETE,OPTIONS").split(",")
    cors_headers = os.getenv("CORS_HEADERS", "*").split(",")
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=cors_methods,
        allow_headers=cors_headers,
    )
    
    logger.info(f"CORS configured with origins: {cors_origins}")


def setup_middleware(app: FastAPI) -> None:
    """
    Set up all middleware components for the FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    # Add exception handling middleware (first)
    app.add_middleware(ExceptionHandlerMiddleware)
    
    # Add request logging middleware
    app.add_middleware(RequestLoggingMiddleware)
    
    # Add rate limiting middleware
    app.add_middleware(RateLimitMiddleware)
    
    # Configure CORS
    configure_cors(app)
    
    logger.info("All middleware components configured successfully")


def add_health_endpoint(app: FastAPI) -> None:
    """
    Add health check endpoint to the FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    start_time = time.time()
    
    @app.get("/health", response_model=HealthResponse, tags=["Health"])
    async def health_check():
        """
        Health check endpoint for monitoring and deployment.
        
        Returns:
            HealthResponse: Current health status and system information
        """
        uptime = time.time() - start_time
        
        return HealthResponse(
            status="healthy",
            timestamp=datetime.utcnow(),
            uptime=uptime
        )
    
    logger.info("Health check endpoint configured at /health")


# Exception handlers for different HTTP exceptions
def setup_exception_handlers(app: FastAPI) -> None:
    """
    Set up custom exception handlers for specific HTTP exceptions.
    
    Args:
        app: FastAPI application instance
    """
    
    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc: HTTPException):
        """Handle 404 Not Found exceptions."""
        return JSONResponse(
            status_code=404,
            content=ErrorResponse(
                error="Not Found",
                message="The requested resource was not found",
                timestamp=datetime.utcnow(),
                path=str(request.url.path),
                status_code=404
            ).dict()
        )
    
    @app.exception_handler(422)
    async def validation_exception_handler(request: Request, exc):
        """Handle validation exceptions."""
        return JSONResponse(
            status_code=422,
            content=ErrorResponse(
                error="Validation Error",
                message="Invalid request data provided",
                timestamp=datetime.utcnow(),
                path=str(request.url.path),
                status_code=422
            ).dict()
        )
    
    @app.exception_handler(500)
    async def internal_error_handler(request: Request, exc: Exception):
        """Handle internal server errors."""
        logger.error(f"Internal server error: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error="Internal Server Error",
                message="An unexpected error occurred",
                timestamp=datetime.utcnow(),
                path=str(request.url.path),
                status_code=500
            ).dict()
        )
    
    logger.info("Exception handlers configured")


# Utility functions for monitoring
def get_rate_limit_stats() -> Dict[str, Any]:
    """
    Get current rate limiting statistics.
    
    Returns:
        Dictionary with rate limiting statistics
    """
    with rate_limit_lock:
        current_time = time.time()
        stats = {}
        
        for ip, requests in rate_limit_storage.items():
            # Clean old requests
            active_requests = [
                req_time for req_time in requests
                if current_time - req_time < RATE_LIMIT_WINDOW
            ]
            stats[ip] = {
                "active_requests": len(active_requests),
                "remaining": max(0, RATE_LIMIT_REQUESTS - len(active_requests)),
                "reset_in": RATE_LIMIT_WINDOW - (current_time - min(active_requests)) if active_requests else 0
            }
        
        return stats


def reset_rate_limits() -> None:
    """Reset all rate limiting counters (useful for testing)."""
    with rate_limit_lock:
        rate_limit_storage.clear()
    logger.info("Rate limiting counters reset")

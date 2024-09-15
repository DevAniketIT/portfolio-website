"""
Example of using API key authentication in protected routes.

This demonstrates how to use the get_api_key dependency from middleware
to protect specific endpoints with API key authentication.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional

# Import the API key dependency from middleware
from middleware import get_api_key

router = APIRouter()

@router.get("/protected")
async def protected_endpoint(api_key: Optional[str] = Depends(get_api_key)):
    """
    Example of a protected endpoint that requires API key authentication
    when API_KEY_REQUIRED=true in environment variables.
    
    Args:
        api_key: Validated API key from middleware dependency
        
    Returns:
        Protected resource data
    """
    return {
        "message": "This is a protected endpoint",
        "authenticated": api_key is not None,
        "data": "Sensitive information only for authenticated users"
    }

@router.get("/public")
async def public_endpoint():
    """
    Example of a public endpoint that doesn't require authentication.
    
    Returns:
        Public resource data
    """
    return {
        "message": "This is a public endpoint",
        "data": "Public information available to everyone"
    }

@router.get("/admin")
async def admin_endpoint(api_key: str = Depends(get_api_key)):
    """
    Example of an admin endpoint that always requires authentication.
    Note: This uses `str` instead of `Optional[str]` to always require API key,
    even when API_KEY_REQUIRED=false.
    
    Args:
        api_key: Required validated API key
        
    Returns:
        Admin resource data
        
    Raises:
        HTTPException: 401 if API key is missing or invalid
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is required for admin endpoints"
        )
    
    return {
        "message": "This is an admin endpoint",
        "authenticated": True,
        "data": "Administrative information for authenticated admins only"
    }

# How to include this in your main application:
# 
# from fastapi import FastAPI
# from auth_example import router as auth_router
# 
# app = FastAPI()
# app.include_router(auth_router, prefix="/api/auth", tags=["Authentication Examples"])

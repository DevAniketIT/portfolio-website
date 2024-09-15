"""
Custom documentation configuration for Job Application Tracker API.

This module provides enhanced OpenAPI documentation configuration including:
- Custom API information and contact details
- Authentication documentation
- Custom styling and branding
- OpenAPI schema enhancements
- Postman collection generation utilities
"""

from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Dict, Any, Optional
import json
import os
from datetime import datetime

# API Information and contact details
API_INFO = {
    "title": "Job Application Tracker API",
    "version": "1.0.0",
    "description": """
## Job Application Tracker API

A comprehensive REST API for managing and tracking job applications with powerful filtering, analytics, and history tracking capabilities.

### Key Features

🎯 **Complete Application Management**
- Full CRUD operations for job applications
- Advanced filtering and search capabilities  
- Bulk operations support
- Status tracking and updates

📊 **Analytics & Insights**
- Comprehensive application statistics
- Success rate calculations
- Response time analytics
- Status distribution analysis

📈 **Activity Tracking**
- Detailed application history
- Interaction logging
- Timeline visualization
- Follow-up reminders

⚡ **Quick Tracking**
- Simplified tracking endpoint for external integrations
- Minimal required fields for fast entry
- Auto-populated defaults

### Data Models

The API uses comprehensive Pydantic models with:
- **Validation**: Input validation with detailed error messages
- **Examples**: Complete request/response examples
- **Documentation**: Field-level descriptions and constraints
- **Type Safety**: Strong typing throughout

### Response Format

All endpoints return standardized responses:
- **Success responses** include `success`, `message`, `data`, and `timestamp`
- **Error responses** include `success`, `message`, `errors`, `error_code`, and `timestamp`
- **Paginated responses** include pagination metadata

### Getting Started

1. **Create an Application**: Use `POST /api/applications/` to create your first job application
2. **Track Applications**: Use `POST /api/tracking/track` for quick application tracking
3. **View Analytics**: Access `GET /api/tracking/stats` for comprehensive analytics
4. **Search & Filter**: Use query parameters on `GET /api/applications/` for advanced filtering

### Authentication

This API supports optional API key authentication:
- Set `API_KEY_REQUIRED=true` in environment variables to enable authentication
- Include API key in `X-API-Key` header for authenticated requests
- Some endpoints may require authentication regardless of global settings

### Rate Limiting

The API includes built-in rate limiting:
- Default: 100 requests per minute per IP
- Authenticated users may have higher limits
- Rate limit information included in response headers

### Error Handling

The API provides comprehensive error handling:
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Authentication required
- **404 Not Found**: Resource not found
- **422 Unprocessable Entity**: Validation errors
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Server errors

All error responses include detailed error messages and codes for programmatic handling.
    """,
    "contact": {
        "name": "API Support Team",
        "email": "api-support@example.com",
        "url": "https://github.com/yourusername/job-tracker-api"
    },
    "license_info": {
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    },
    "terms_of_service": "https://example.com/terms"
}

# Custom OpenAPI tags with descriptions
CUSTOM_TAGS = [
    {
        "name": "applications",
        "description": """
**Job Application Management**

Complete CRUD operations for managing job applications including:
- Create single or multiple applications
- Retrieve with advanced filtering and pagination
- Update with partial update support  
- Delete applications
- Status-specific queries
- Company-specific queries

All endpoints support comprehensive filtering, sorting, and pagination.
        """
    },
    {
        "name": "tracking", 
        "description": """
**Application Tracking & Analytics**

Specialized endpoints for application tracking and analytics:
- Quick application tracking with minimal fields
- Detailed application history and timeline
- Comprehensive analytics and statistics
- Recent activity monitoring
- Interaction logging

Perfect for dashboard integration and external tracking tools.
        """
    },
    {
        "name": "health",
        "description": """
**Health & Monitoring**

System health and monitoring endpoints:
- Basic health check
- Database connectivity status
- System metrics and status
        """
    }
]

# Authentication schemes for OpenAPI
SECURITY_SCHEMES = {
    "ApiKeyAuth": {
        "type": "apiKey",
        "in": "header",
        "name": "X-API-Key",
        "description": "API key for authentication. Include your API key in the X-API-Key header."
    }
}

def create_custom_openapi_schema(app: FastAPI) -> Dict[str, Any]:
    """
    Create custom OpenAPI schema with enhanced documentation.
    
    Args:
        app: FastAPI application instance
        
    Returns:
        Custom OpenAPI schema dictionary
    """
    if app.openapi_schema:
        return app.openapi_schema

    # Generate base OpenAPI schema
    openapi_schema = get_openapi(
        title=API_INFO["title"],
        version=API_INFO["version"],
        description=API_INFO["description"],
        routes=app.routes,
    )

    # Add custom information
    openapi_schema["info"].update({
        "contact": API_INFO["contact"],
        "license": API_INFO["license_info"],
        "termsOfService": API_INFO["terms_of_service"],
        "x-logo": {
            "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png",
            "altText": "Job Tracker API"
        }
    })

    # Add custom tags
    openapi_schema["tags"] = CUSTOM_TAGS

    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = SECURITY_SCHEMES

    # Add global security if API key is required
    if os.getenv("API_KEY_REQUIRED", "false").lower() == "true":
        openapi_schema["security"] = [{"ApiKeyAuth": []}]

    # Add custom examples for common responses
    if "components" not in openapi_schema:
        openapi_schema["components"] = {}
    
    openapi_schema["components"]["examples"] = {
        "SuccessResponse": {
            "summary": "Successful Operation",
            "value": {
                "success": True,
                "message": "Operation completed successfully",
                "data": {"id": 123},
                "timestamp": "2024-01-15T10:30:00Z"
            }
        },
        "ErrorResponse": {
            "summary": "Error Response",
            "value": {
                "success": False,
                "message": "Validation error",
                "errors": ["Company name is required"],
                "error_code": "VALIDATION_ERROR", 
                "timestamp": "2024-01-15T10:30:00Z"
            }
        },
        "PaginatedResponse": {
            "summary": "Paginated Response",
            "value": {
                "items": [],
                "total": 150,
                "page": 1,
                "limit": 20,
                "pages": 8,
                "has_next": True,
                "has_previous": False
            }
        }
    }

    # Add server information
    openapi_schema["servers"] = [
        {
            "url": "http://localhost:8000",
            "description": "Development server"
        },
        {
            "url": "https://api.example.com",
            "description": "Production server"
        }
    ]

    # Custom vendor extensions
    openapi_schema["x-api-version"] = API_INFO["version"]
    openapi_schema["x-generated-at"] = datetime.utcnow().isoformat() + "Z"

    app.openapi_schema = openapi_schema
    return app.openapi_schema

def setup_custom_docs(app: FastAPI) -> None:
    """
    Setup custom documentation for the FastAPI app.
    
    Args:
        app: FastAPI application instance
    """
    # Set custom OpenAPI schema generator
    app.openapi = lambda: create_custom_openapi_schema(app)

def generate_postman_collection(app: FastAPI) -> Dict[str, Any]:
    """
    Generate a Postman collection from the OpenAPI schema.
    
    Args:
        app: FastAPI application instance
        
    Returns:
        Postman collection dictionary
    """
    openapi_schema = app.openapi()
    
    collection = {
        "info": {
            "name": openapi_schema["info"]["title"],
            "description": openapi_schema["info"]["description"],
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
            "version": openapi_schema["info"]["version"]
        },
        "auth": {
            "type": "apikey",
            "apikey": [
                {
                    "key": "key",
                    "value": "X-API-Key",
                    "type": "string"
                },
                {
                    "key": "value",
                    "value": "{{api_key}}",
                    "type": "string"
                },
                {
                    "key": "in",
                    "value": "header",
                    "type": "string"
                }
            ]
        },
        "variable": [
            {
                "key": "base_url",
                "value": "http://localhost:8000",
                "type": "string"
            },
            {
                "key": "api_key", 
                "value": "your-api-key-here",
                "type": "string"
            }
        ],
        "item": []
    }
    
    # Process paths and create Postman requests
    for path, methods in openapi_schema.get("paths", {}).items():
        folder_name = path.split('/')[2] if len(path.split('/')) > 2 else "General"
        
        # Find or create folder
        folder = None
        for item in collection["item"]:
            if item.get("name") == folder_name:
                folder = item
                break
        
        if not folder:
            folder = {
                "name": folder_name,
                "item": []
            }
            collection["item"].append(folder)
        
        # Add requests for each method
        for method, details in methods.items():
            if method.upper() in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                request = {
                    "name": details.get("summary", f"{method.upper()} {path}"),
                    "request": {
                        "method": method.upper(),
                        "header": [
                            {
                                "key": "Content-Type",
                                "value": "application/json",
                                "type": "text"
                            }
                        ],
                        "url": {
                            "raw": "{{base_url}}" + path,
                            "host": ["{{base_url}}"],
                            "path": path.split("/")[1:]
                        },
                        "description": details.get("description", "")
                    }
                }
                
                # Add request body for POST/PUT/PATCH
                if method.upper() in ["POST", "PUT", "PATCH"]:
                    request_body = details.get("requestBody", {})
                    if request_body:
                        content = request_body.get("content", {})
                        json_content = content.get("application/json", {})
                        schema = json_content.get("schema", {})
                        
                        if "example" in json_content:
                            request["request"]["body"] = {
                                "mode": "raw",
                                "raw": json.dumps(json_content["example"], indent=2),
                                "options": {
                                    "raw": {
                                        "language": "json"
                                    }
                                }
                            }
                
                folder["item"].append(request)
    
    return collection

def get_postman_collection_endpoint(app: FastAPI):
    """
    Create endpoint that serves the Postman collection.
    
    Args:
        app: FastAPI application instance
        
    Returns:
        FastAPI route function
    """
    @app.get("/docs/postman", include_in_schema=False)
    async def download_postman_collection():
        """Download Postman collection for API testing."""
        collection = generate_postman_collection(app)
        return JSONResponse(
            content=collection,
            headers={
                "Content-Disposition": "attachment; filename=job-tracker-api.postman_collection.json"
            }
        )
    
    return download_postman_collection

def add_docs_endpoints(app: FastAPI):
    """
    Add custom documentation endpoints to the FastAPI app.
    
    Args:
        app: FastAPI application instance
    """
    @app.get("/docs/info", include_in_schema=False)
    async def api_info():
        """Get API information and documentation links."""
        return {
            "api": API_INFO,
            "documentation": {
                "swagger_ui": "/docs",
                "redoc": "/redoc",
                "openapi_schema": "/openapi.json",
                "postman_collection": "/docs/postman"
            },
            "health": {
                "status": "/health",
                "metrics": "/metrics"  
            },
            "endpoints": {
                "applications": "/api/applications",
                "tracking": "/api/tracking"
            }
        }
    
    # Add Postman collection endpoint
    get_postman_collection_endpoint(app)
    
def setup_enhanced_docs(app: FastAPI):
    """
    Complete setup for enhanced API documentation.
    
    Args:
        app: FastAPI application instance
    """
    # Setup custom OpenAPI schema
    setup_custom_docs(app)
    
    # Add custom documentation endpoints
    add_docs_endpoints(app)
    
    # Configure Swagger UI with custom settings
    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        """Custom Swagger UI with enhanced styling."""
        return get_swagger_ui_html(
            openapi_url=app.openapi_url,
            title=f"{app.title} - Interactive API Documentation",
            swagger_ui_parameters={
                "deepLinking": True,
                "displayRequestDuration": True,
                "docExpansion": "list",
                "operationsSorter": "method",
                "filter": True,
                "showExtensions": True,
                "showCommonExtensions": True,
                "tryItOutEnabled": True
            }
        )

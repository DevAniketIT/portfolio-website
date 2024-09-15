# FastAPI Middleware Documentation

This document describes the comprehensive security and monitoring middleware implemented for the Job Application Tracker API.

## Features

### 1. CORS Middleware Configuration
- **Purpose**: Enable cross-origin requests from web browsers
- **Configuration**: Environment-based CORS settings
- **Default**: Allows all origins, methods, and headers (development mode)

### 2. API Key Authentication (Optional)
- **Purpose**: Secure API endpoints with API key authentication
- **Configuration**: Configurable via environment variables
- **Default**: Disabled (set `API_KEY_REQUIRED=true` to enable)

### 3. Request Logging Middleware
- **Purpose**: Log all incoming requests and responses for debugging
- **Features**: 
  - Request method, path, IP, and query parameters
  - Response status codes and processing times
  - Error logging with stack traces
  - Adds `X-Process-Time` header to responses

### 4. Rate Limiting Middleware
- **Purpose**: Prevent API abuse by limiting requests per IP
- **Default**: 100 requests per minute per IP address
- **Features**: 
  - Configurable limits via environment variables
  - Automatic cleanup of expired request records
  - Detailed error responses when limits are exceeded

### 5. Exception Handling Middleware
- **Purpose**: Provide consistent error responses across the API
- **Features**:
  - Standardized error response format
  - Detailed logging of unhandled exceptions
  - Graceful handling of different HTTP error types

### 6. Health Check Endpoint
- **Purpose**: Monitor API health and uptime
- **Endpoint**: `GET /health`
- **Features**: Returns status, timestamp, uptime, and version information

## Configuration

All middleware components are configured via environment variables. Copy `.env.example` to `.env` and customize:

```bash
# Rate Limiting
RATE_LIMIT_REQUESTS=100          # Max requests per window
RATE_LIMIT_WINDOW=60             # Time window in seconds

# API Key Authentication
API_KEY_REQUIRED=false           # Enable/disable authentication
API_KEY=your-secret-key          # Your API key

# CORS Settings
CORS_ORIGINS=*                   # Allowed origins
CORS_METHODS=GET,POST,PUT,DELETE,OPTIONS
CORS_HEADERS=*

# Server Settings
HOST=0.0.0.0
PORT=8000
```

## Usage Examples

### Basic Setup (Already implemented in main.py)

```python
from fastapi import FastAPI
from middleware import setup_middleware, add_health_endpoint, setup_exception_handlers

app = FastAPI()

# Set up all middleware
setup_middleware(app)
setup_exception_handlers(app)
add_health_endpoint(app)
```

### Using API Key Authentication

```python
from fastapi import APIRouter, Depends
from middleware import get_api_key
from typing import Optional

router = APIRouter()

@router.get("/protected")
async def protected_route(api_key: Optional[str] = Depends(get_api_key)):
    # This endpoint respects the API_KEY_REQUIRED setting
    return {"message": "Protected data", "authenticated": api_key is not None}

@router.get("/admin")
async def admin_route(api_key: str = Depends(get_api_key)):
    # This endpoint always requires authentication
    if not api_key:
        raise HTTPException(401, "API key required")
    return {"message": "Admin data"}
```

### Making Authenticated Requests

When API key authentication is enabled, include the API key in the request header:

```bash
# With curl
curl -H "X-API-Key: your-secret-key" http://localhost:8000/api/protected

# With Python requests
import requests
headers = {"X-API-Key": "your-secret-key"}
response = requests.get("http://localhost:8000/api/protected", headers=headers)
```

## Security Best Practices

### Production Configuration

1. **CORS**: Restrict origins to your specific domains
   ```bash
   CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
   ```

2. **API Keys**: Use strong, randomly generated keys
   ```bash
   API_KEY_REQUIRED=true
   API_KEY=sk_prod_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
   ```

3. **Rate Limiting**: Adjust based on your expected traffic
   ```bash
   RATE_LIMIT_REQUESTS=50    # Stricter for production
   RATE_LIMIT_WINDOW=60
   ```

### SSL/HTTPS

Ensure your production deployment uses HTTPS to protect API keys and sensitive data in transit.

### Rate Limiting in Production

The current implementation stores rate limiting data in memory. For production with multiple server instances, consider using Redis:

```python
# Example Redis-based rate limiting (not implemented)
import redis
r = redis.Redis(host='localhost', port=6379, db=0)
```

## Monitoring and Logging

### Log Files

- **api_requests.log**: All request/response logs with timestamps
- **Console output**: Real-time logging for development

### Health Check

The `/health` endpoint provides:
- Service status
- Current timestamp
- Uptime in seconds
- API version

Use this endpoint for:
- Load balancer health checks
- Monitoring systems (Prometheus, etc.)
- Deployment verification

### Rate Limiting Stats

Monitor rate limiting with the utility function:

```python
from middleware import get_rate_limit_stats

stats = get_rate_limit_stats()
# Returns per-IP statistics: active requests, remaining, reset time
```

## Error Responses

All errors follow a consistent format:

```json
{
  "error": "Rate Limit Exceeded",
  "message": "Maximum 100 requests per 60 seconds allowed",
  "timestamp": "2024-08-24T10:30:00Z",
  "path": "/api/applications",
  "status_code": 429
}
```

### Common HTTP Status Codes

- **401**: Invalid or missing API key
- **404**: Endpoint not found
- **422**: Validation error (invalid request data)
- **429**: Rate limit exceeded
- **500**: Internal server error

## Testing

### Rate Limiting Test

```bash
# Test rate limiting by making multiple rapid requests
for i in {1..105}; do
  curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/api/applications
done
# Should return 429 after 100 requests
```

### API Key Test

```bash
# Test without API key (when required)
curl -w "%{http_code}" http://localhost:8000/api/protected
# Should return 401

# Test with valid API key
curl -H "X-API-Key: your-secret-key" -w "%{http_code}" http://localhost:8000/api/protected
# Should return 200
```

### Health Check Test

```bash
curl http://localhost:8000/health
# Should return health status with uptime
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Rate Limiting Too Strict**: Adjust `RATE_LIMIT_REQUESTS` and `RATE_LIMIT_WINDOW`
3. **CORS Issues**: Check `CORS_ORIGINS` configuration for your frontend domain
4. **API Key Problems**: Verify `API_KEY` matches between server and client

### Debug Mode

For development, enable detailed logging:

```python
import logging
logging.getLogger().setLevel(logging.DEBUG)
```

This will show detailed middleware execution and request processing information.

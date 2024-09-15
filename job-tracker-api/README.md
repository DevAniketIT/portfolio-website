# Job Application Tracker API

[![API Status](https://img.shields.io/website?down_color=red&down_message=offline&up_color=green&up_message=online&url=https%3A%2F%2Fyour-service-name.onrender.com%2Fhealth)](https://your-service-name.onrender.com/health)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-00a393.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A comprehensive, production-ready REST API for managing job applications with CRUD operations, filtering, pagination, analytics, and proper error handling.

## 🚀 Production API

**Base URL**: `https://your-service-name.onrender.com`

### 🔗 Quick Links
- 📖 **[Interactive API Documentation](https://your-service-name.onrender.com/docs)**
- 🏥 **[Health Check](https://your-service-name.onrender.com/health)**
- 📋 **[API Schema](https://your-service-name.onrender.com/openapi.json)**
- 📊 **[Analytics Dashboard](https://your-service-name.onrender.com/docs/dashboard)**

## ✨ Features

- ✅ **Production Ready** - Deployed on Render.com with PostgreSQL
- ✅ **Full CRUD Operations** - Complete job application management
- ✅ **Advanced Filtering & Search** - Multi-field search with pagination
- ✅ **Analytics & Tracking** - Application statistics and trends
- ✅ **Rate Limiting** - 1000 requests/minute protection
- ✅ **Authentication Support** - Optional API key authentication
- ✅ **Python SDK** - Complete client library with retry logic
- ✅ **Interactive Documentation** - OpenAPI/Swagger with examples
- ✅ **Postman Collection** - Ready-to-import API collection
- ✅ **Auto-scaling & Monitoring** - Built-in health checks

## 🚀 Quick Start Guide

### Option 1: Use Production API (Recommended)

**No installation required!** Start using the API immediately:

```bash
# Test the API health
curl "https://your-service-name.onrender.com/health"

# Create your first job application
curl -X POST "https://your-service-name.onrender.com/api/applications" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Google Inc.",
    "job_title": "Software Engineer",
    "location": "Mountain View, CA",
    "status": "applied"
  }'

# List all your applications
curl "https://your-service-name.onrender.com/api/applications"
```

**Explore the API**: Visit **[https://your-service-name.onrender.com/docs](https://your-service-name.onrender.com/docs)** for interactive documentation.

### Option 2: Use Python SDK

1. **Install the SDK**:
   ```bash
   pip install requests python-dateutil typing-extensions
   ```

2. **Copy the SDK file**:
   ```bash
   # Download the SDK from this repository
   curl -O https://raw.githubusercontent.com/yourusername/job-tracker-api/main/client_sdk.py
   ```

3. **Start using it**:
   ```python
   from client_sdk import JobTrackerClient
   
   # Initialize client
   client = JobTrackerClient("https://your-service-name.onrender.com")
   
   # Create an application
   app = client.create_application({
       "company_name": "Google Inc.",
       "job_title": "Software Engineer",
       "location": "Mountain View, CA",
       "status": "applied"
   })
   
   print(f"Created application with ID: {app['data']['id']}")
   
   # List applications
   applications = client.get_applications(limit=10)
   print(f"Found {len(applications['items'])} applications")
   ```

### Option 3: Local Development

1. **Clone and install**:
   ```bash
   git clone https://github.com/yourusername/job-tracker-api.git
   cd job-tracker-api
   pip install -r requirements.txt
   ```

2. **Run locally**:
   ```bash
   python main.py
   ```

3. **Access locally**:
   - API: `http://localhost:8000`
   - Docs: `http://localhost:8000/docs`
   - Health: `http://localhost:8000/health`

### Option 4: Import Postman Collection

1. **Download collection**:
   ```bash
   curl -O https://your-service-name.onrender.com/docs/postman
   ```

2. **Import to Postman**:
   - Open Postman
   - File → Import → Upload the downloaded `.json` file
   - Set environment variable: `base_url = https://your-service-name.onrender.com`

3. **Start testing**: All endpoints ready with examples!

## API Endpoints

### Core CRUD Operations

#### `GET /api/applications`
List all applications with pagination and filtering.

**Query Parameters:**
- `status`: Filter by application status(es) (multiple values allowed)
- `company_name`: Filter by company name (partial match)
- `date_from`: Filter applications from this date
- `date_to`: Filter applications up to this date
- `job_type`: Filter by job type(s)
- `remote_type`: Filter by remote work type(s)
- `priority`: Filter by priority level(s)
- `search`: Full-text search across company, title, notes
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20, max: 100)
- `sort_by`: Field to sort by (default: created_at)
- `sort_order`: Sort order - 'asc' or 'desc' (default: desc)

**Example:**
```bash
GET /api/applications?status=applied&status=reviewing&company_name=Google&page=1&limit=10
```

**Response:**
```json
{
  "items": [...],
  "total": 150,
  "page": 1,
  "limit": 10,
  "pages": 15,
  "has_next": true,
  "has_previous": false
}
```

#### `POST /api/applications`
Create a new job application.

**Request Body:**
```json
{
  "company_name": "Google Inc.",
  "job_title": "Senior Software Engineer",
  "job_url": "https://careers.google.com/jobs/results/123456789",
  "location": "Mountain View, CA, USA",
  "salary_min": 120000,
  "salary_max": 180000,
  "currency": "USD",
  "job_type": "full_time",
  "remote_type": "hybrid",
  "application_date": "2024-01-15",
  "priority": "high",
  "notes": "Applied through referral",
  "contact_email": "recruiter@google.com",
  "status": "applied"
}
```

**Response:** `201 Created` with the created application including generated ID and timestamps.

#### `GET /api/applications/{id}`
Get a specific application by ID.

**Response:** `200 OK` with application details or `404 Not Found`.

#### `PUT /api/applications/{id}`
Update an application (partial updates supported).

**Request Body:** Any subset of application fields
```json
{
  "status": "phone_screen",
  "notes": "Completed phone screen. Technical interview next week.",
  "priority": "high"
}
```

**Response:** `200 OK` with updated application or `404 Not Found`.

#### `DELETE /api/applications/{id}`
Delete an application by ID.

**Response:** `200 OK` with deletion confirmation or `404 Not Found`.

### Utility Endpoints

#### `GET /api/applications/status/{status}`
Get applications filtered by specific status.

#### `GET /api/applications/company/{company_name}`
Get applications filtered by company name.

#### `PATCH /api/applications/{id}/status`
Update only the status of an application.

**Query Parameter:**
- `status`: New application status

## Data Models

### Application Status Options
- `applied` - Application submitted
- `reviewing` - Under review
- `phone_screen` - Phone screening stage
- `technical_interview` - Technical interview stage
- `onsite_interview` - On-site interview
- `final_round` - Final round interview
- `offer` - Offer received
- `rejected` - Application rejected
- `withdrawn` - Application withdrawn
- `accepted` - Offer accepted

### Job Type Options
- `full_time` - Full-time position
- `part_time` - Part-time position
- `contract` - Contract position
- `internship` - Internship
- `freelance` - Freelance work

### Remote Type Options
- `on_site` - On-site work
- `remote` - Fully remote
- `hybrid` - Hybrid work arrangement

### Priority Levels
- `low` - Low priority
- `medium` - Medium priority
- `high` - High priority
- `urgent` - Urgent priority

## Error Handling

The API returns standardized error responses with appropriate HTTP status codes:

- `200 OK` - Successful operation
- `201 Created` - Resource created successfully
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

**Error Response Format:**
```json
{
  "success": false,
  "message": "Error description",
  "errors": ["Detailed error messages"],
  "error_code": "ERROR_CODE",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Example Usage

### Create an Application
```bash
curl -X POST "http://localhost:8000/api/applications" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Google Inc.",
    "job_title": "Software Engineer",
    "location": "Mountain View, CA",
    "status": "applied"
  }'
```

### List Applications with Filtering
```bash
curl "http://localhost:8000/api/applications?status=applied&company_name=Google&limit=5"
```

### Update Application Status
```bash
curl -X PATCH "http://localhost:8000/api/applications/1/status?status=phone_screen"
```

### Search Applications
```bash
curl "http://localhost:8000/api/applications?search=software%20engineer&remote_type=remote"
```

## Project Structure

```
api/
├── __init__.py
├── main.py                 # FastAPI application setup
├── models.py              # Pydantic data models
├── README.md              # This file
└── routers/
    ├── __init__.py
    └── applications.py    # Applications CRUD endpoints
```

## Development

### Running the API in Development Mode
```bash
python api/main.py
```

The API will start with auto-reload enabled on `http://localhost:8000`.

### Testing
Run the comprehensive test suite:
```bash
python test_applications_api.py
```

This tests all endpoints, filtering, pagination, error handling, and edge cases.

### API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

The interactive documentation provides a complete API reference with request/response examples and the ability to test endpoints directly in the browser.

## 🌐 Production Deployment

**Base URL**: `https://YOUR_SERVICE_NAME.onrender.com` (Update this with your actual service URL)

### Production Features
- ✅ PostgreSQL database with automated backups
- ✅ HTTPS/SSL encryption
- ✅ CORS configuration
- ✅ Rate limiting (1000 req/min)
- ✅ Health monitoring
- ✅ Auto-scaling and deployment

### Quick Links
- **Interactive API Docs**: https://YOUR_SERVICE_NAME.onrender.com/docs
- **Health Check**: https://YOUR_SERVICE_NAME.onrender.com/health
- **API Schema**: https://YOUR_SERVICE_NAME.onrender.com/openapi.json

### Production Usage Examples

#### Create an Application
```bash
curl -X POST "https://YOUR_SERVICE_NAME.onrender.com/api/applications" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Google Inc.",
    "job_title": "Software Engineer",
    "location": "Mountain View, CA",
    "status": "applied"
  }'
```

#### List Applications
```bash
curl "https://YOUR_SERVICE_NAME.onrender.com/api/applications?limit=10"
```

#### Health Check
```bash
curl "https://YOUR_SERVICE_NAME.onrender.com/health"
```

### Testing Production Deployment

Run the validation script to test all endpoints:
```powershell
# Update the URL in the script first
.\quick_api_test.ps1
```

### Monitoring & Maintenance
- **Render Dashboard**: Monitor logs, metrics, and deployments
- **Health Endpoint**: Automated health checks every 30 seconds
- **Database Backups**: Automated daily backups
- **SSL Certificates**: Auto-renewed Let's Encrypt certificates

## 🔧 Python SDK

### Installation

```bash
# Install dependencies
pip install requests python-dateutil typing-extensions

# Download SDK
curl -O https://raw.githubusercontent.com/yourusername/job-tracker-api/main/client_sdk.py
```

### Basic Usage

```python
from client_sdk import JobTrackerClient

# Initialize client
client = JobTrackerClient("https://your-service-name.onrender.com")

# Create application
app = client.create_application({
    "company_name": "Google Inc.",
    "job_title": "Senior Software Engineer",
    "location": "Mountain View, CA",
    "status": "applied",
    "priority": "high"
})

# List applications with filtering
apps = client.get_applications(
    status=["applied", "reviewing"],
    company_name="Google",
    limit=10
)

# Update application
client.update_application(app['data']['id'], {
    "status": "phone_screen",
    "notes": "Completed initial screening"
})

# Get analytics
stats = client.get_analytics_stats()
print(f"Total applications: {stats['total_applications']}")
print(f"Success rate: {stats['success_rate']}%")
```

### Advanced Features

```python
# Bulk operations
apps_data = [
    {"company_name": "Company A", "job_title": "Engineer"},
    {"company_name": "Company B", "job_title": "Developer"}
]
results = client.bulk_create_applications(apps_data, batch_size=5)

# Quick tracking for external tools/browser extensions
quick_app = client.quick_track(
    company="StartupXYZ",
    title="Full Stack Developer",
    url="https://startup.com/jobs/123"
)

# Error handling
try:
    app = client.get_application(999999)
except client_sdk.NotFoundError:
    print("Application not found")
except client_sdk.RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
```

**Complete SDK Documentation**: See [`CLIENT_SDK_README.md`](CLIENT_SDK_README.md) for full documentation.

---

## 🔐 Authentication & Rate Limiting

### Authentication (Optional)

Authentication is **disabled by default** for ease of use. To enable API key authentication:

#### Enable Authentication
```bash
# Set environment variables
export API_KEY_REQUIRED=true
export API_KEY=your-secure-api-key-here
```

#### Using API Key
```bash
# With curl
curl -H "X-API-Key: your-api-key" \
  "https://your-service-name.onrender.com/api/applications"

# With Python SDK
client = JobTrackerClient(
    "https://your-service-name.onrender.com",
    api_key="your-api-key"
)

# With JavaScript/fetch
fetch('https://your-service-name.onrender.com/api/applications', {
    headers: {
        'X-API-Key': 'your-api-key',
        'Content-Type': 'application/json'
    }
});
```

### Rate Limiting

- **Default Limit**: 1000 requests per minute per IP
- **Authenticated Users**: May have higher limits
- **Rate Limit Headers**: Included in all responses
  - `X-RateLimit-Limit`: Request limit
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Reset timestamp

#### Rate Limit Response
```json
{
  "success": false,
  "message": "Rate limit exceeded",
  "error_code": "RATE_LIMIT_EXCEEDED",
  "retry_after": 60
}
```

#### Handling Rate Limits
```python
# Python SDK handles retries automatically
from client_sdk import JobTrackerClient, RetryConfig

retry_config = RetryConfig(
    max_attempts=5,
    base_delay=2.0,
    exponential_base=2.0
)

client = JobTrackerClient(
    base_url="https://your-service-name.onrender.com",
    retry_config=retry_config
)
```

---

## 📚 API Documentation

### Interactive Documentation
- **Swagger UI**: [https://your-service-name.onrender.com/docs](https://your-service-name.onrender.com/docs)
  - Interactive API explorer
  - Test endpoints directly in browser
  - Auto-generated from OpenAPI spec

- **ReDoc**: [https://your-service-name.onrender.com/redoc](https://your-service-name.onrender.com/redoc)
  - Beautiful, responsive documentation
  - Better for reading and reference

### API Schema & Collections
- **OpenAPI Schema**: [https://your-service-name.onrender.com/openapi.json](https://your-service-name.onrender.com/openapi.json)
- **Postman Collection**: [Download](https://your-service-name.onrender.com/docs/postman)
- **Comprehensive API Docs**: [`API_DOCUMENTATION.md`](API_DOCUMENTATION.md)

### Additional Resources
- **SDK Documentation**: [`CLIENT_SDK_README.md`](CLIENT_SDK_README.md)
- **Deployment Guide**: [`DEPLOYMENT.md`](DEPLOYMENT.md)
- **Postman Guide**: [`POSTMAN_COLLECTION_GUIDE.md`](POSTMAN_COLLECTION_GUIDE.md)
- **Demo Script**: [`DEMO_SCRIPT.md`](DEMO_SCRIPT.md)

### Health & Monitoring
```bash
# Health check
curl "https://your-service-name.onrender.com/health"
# Response: {"status": "healthy", "database": "connected", "timestamp": "..."}

# API info
curl "https://your-service-name.onrender.com/"
# Response: API version, endpoints, status
```

---

## 🛠️ Development & Testing

### Local Development
```bash
git clone https://github.com/yourusername/job-tracker-api.git
cd job-tracker-api
pip install -r requirements.txt
python main.py
```

### Testing
```bash
# Run API tests
python test_applications_api.py

# Test SDK
python test_sdk.py

# Test with PowerShell script
.\test_api.ps1 -ApiUrl "https://your-service-name.onrender.com"
```

### Example Implementations
- **Python Client**: [`examples/python_client_example.py`](examples/python_client_example.py)
- **JavaScript Client**: [`examples/javascript_client_example.js`](examples/javascript_client_example.js)
- **Node.js Client**: [`examples/node_client_example.js`](examples/node_client_example.js)

---

## 📋 Notes & Best Practices

### Production Ready Features
- ✅ **PostgreSQL Database** - Reliable, scalable data storage
- ✅ **Auto-scaling** - Handles traffic spikes automatically
- ✅ **HTTPS/SSL** - Secure connections with auto-renewed certificates
- ✅ **CORS Support** - Cross-origin requests enabled
- ✅ **Error Handling** - Comprehensive error responses
- ✅ **Input Validation** - Pydantic models prevent invalid data
- ✅ **Logging & Monitoring** - Built-in health checks and metrics

### Integration Tips
- Use the **Python SDK** for Python applications
- Import **Postman Collection** for API testing
- Check **health endpoint** for monitoring
- Enable **authentication** for production use
- Use **bulk operations** for multiple items
- Implement **retry logic** for rate limiting

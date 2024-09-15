# Job Application Tracker API Documentation

A comprehensive REST API for managing and tracking job applications with powerful filtering, analytics, and history tracking capabilities.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://api.example.com`

## Table of Contents

1. [Authentication](#authentication)
2. [Response Format](#response-format)
3. [Error Handling](#error-handling)
4. [Applications API](#applications-api)
5. [Tracking API](#tracking-api)
6. [Rate Limiting](#rate-limiting)
7. [Postman Collection](#postman-collection)

## Authentication

The API supports optional API key authentication through the `X-API-Key` header.

### Setup Authentication

To enable authentication, set the environment variable:
```bash
export API_KEY_REQUIRED=true
export API_KEY=your-secret-api-key
```

### Using Authentication

Include your API key in the request header:
```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/api/applications/
```

## Response Format

### Success Response
```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": { "id": 123 },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Error Response
```json
{
  "success": false,
  "message": "Validation error",
  "errors": ["Company name is required"],
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Paginated Response
```json
{
  "items": [...],
  "total": 150,
  "page": 1,
  "limit": 20,
  "pages": 8,
  "has_next": true,
  "has_previous": false
}
```

## Error Handling

| Status Code | Description | Example |
|-------------|-------------|---------|
| 200 | Success | Request completed successfully |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Missing or invalid API key |
| 404 | Not Found | Resource not found |
| 422 | Validation Error | Request validation failed |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error occurred |

---

## Applications API

### List All Applications

Get a paginated list of job applications with filtering and sorting options.

**Endpoint:** `GET /api/applications/`

**Query Parameters:**
- `status` (array): Filter by application status
- `company_name` (string): Filter by company name (partial match)
- `date_from` (date): Filter applications from this date
- `date_to` (date): Filter applications up to this date
- `job_type` (array): Filter by job type
- `remote_type` (array): Filter by remote work type
- `priority` (array): Filter by priority level
- `search` (string): Search across multiple fields
- `page` (integer): Page number (default: 1)
- `limit` (integer): Items per page (max: 100, default: 20)
- `sort_by` (string): Sort field (default: created_at)
- `sort_order` (string): Sort order (asc/desc, default: desc)

**Examples:**

```bash
# Get all applications (first page)
curl "http://localhost:8000/api/applications/"

# Get applications with filtering
curl "http://localhost:8000/api/applications/?status=applied&status=reviewing&limit=10"

# Search for Python roles
curl "http://localhost:8000/api/applications/?search=python&job_type=full_time"

# Get applications by date range
curl "http://localhost:8000/api/applications/?date_from=2024-01-01&date_to=2024-03-31"

# Sort by application date (most recent first)
curl "http://localhost:8000/api/applications/?sort_by=application_date&sort_order=desc"

# Pagination
curl "http://localhost:8000/api/applications/?page=2&limit=50"
```

**Response Example:**
```json
{
  "items": [
    {
      "id": 123,
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
      "status": "applied",
      "priority": "high",
      "notes": "Applied through referral",
      "contact_email": "recruiter@google.com",
      "days_since_applied": 15,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 150,
  "page": 1,
  "limit": 20,
  "pages": 8,
  "has_next": true,
  "has_previous": false
}
```

### Create Application

Create a new job application.

**Endpoint:** `POST /api/applications/`

**Required Fields:**
- `company_name` (string): Company name
- `job_title` (string): Job title

**Optional Fields:**
- `job_url` (string): Job posting URL
- `job_description` (string): Job description
- `location` (string): Job location
- `salary_min` (integer): Minimum salary
- `salary_max` (integer): Maximum salary
- `currency` (string): Currency code (default: USD)
- `job_type` (string): Job type (default: full_time)
- `remote_type` (string): Remote work type (default: on_site)
- `application_date` (date): Application date
- `deadline` (date): Application deadline
- `status` (string): Application status (default: applied)
- `priority` (string): Priority level (default: medium)
- `notes` (string): Personal notes
- `referral_name` (string): Referral person name
- `contact_email` (string): Contact email
- `contact_person` (string): Contact person name

**Examples:**

```bash
# Minimal application
curl -X POST "http://localhost:8000/api/applications/" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Google Inc.",
    "job_title": "Senior Software Engineer"
  }'

# Complete application
curl -X POST "http://localhost:8000/api/applications/" \
  -H "Content-Type: application/json" \
  -d '{
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
    "notes": "Applied through referral from John",
    "contact_email": "recruiter@google.com",
    "status": "applied"
  }'

# With authentication
curl -X POST "http://localhost:8000/api/applications/" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "company_name": "Microsoft",
    "job_title": "Software Engineer II",
    "location": "Seattle, WA"
  }'
```

### Get Specific Application

Retrieve a specific job application by ID.

**Endpoint:** `GET /api/applications/{application_id}`

**Examples:**

```bash
# Get application by ID
curl "http://localhost:8000/api/applications/123"

# With authentication
curl -H "X-API-Key: your-api-key" \
  "http://localhost:8000/api/applications/123"
```

### Update Application

Update a job application with partial update support.

**Endpoint:** `PUT /api/applications/{application_id}`

**Examples:**

```bash
# Update status only
curl -X PUT "http://localhost:8000/api/applications/123" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "phone_screen",
    "notes": "Completed phone screen successfully"
  }'

# Update multiple fields
curl -X PUT "http://localhost:8000/api/applications/123" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "technical_interview",
    "priority": "high",
    "notes": "Technical interview scheduled for next week",
    "contact_person": "Jane Smith"
  }'

# Update salary information
curl -X PUT "http://localhost:8000/api/applications/123" \
  -H "Content-Type: application/json" \
  -d '{
    "salary_min": 130000,
    "salary_max": 190000,
    "notes": "Salary range updated after initial discussion"
  }'
```

### Delete Application

Delete a job application by ID.

**Endpoint:** `DELETE /api/applications/{application_id}`

**Examples:**

```bash
# Delete application
curl -X DELETE "http://localhost:8000/api/applications/123"

# With authentication
curl -X DELETE "http://localhost:8000/api/applications/123" \
  -H "X-API-Key: your-api-key"
```

### Get Applications by Status

Get applications filtered by a specific status.

**Endpoint:** `GET /api/applications/status/{status_name}`

**Examples:**

```bash
# Get all applications with 'applied' status
curl "http://localhost:8000/api/applications/status/applied"

# Get 'phone_screen' applications with pagination
curl "http://localhost:8000/api/applications/status/phone_screen?page=1&limit=10"

# Get offers
curl "http://localhost:8000/api/applications/status/offer"
```

### Get Applications by Company

Get applications filtered by company name.

**Endpoint:** `GET /api/applications/company/{company_name}`

**Examples:**

```bash
# Get all Google applications
curl "http://localhost:8000/api/applications/company/Google"

# Get Microsoft applications with pagination
curl "http://localhost:8000/api/applications/company/Microsoft?page=1&limit=5"
```

### Update Application Status

Update only the status of a specific application.

**Endpoint:** `PATCH /api/applications/{application_id}/status`

**Examples:**

```bash
# Update status to reviewing
curl -X PATCH "http://localhost:8000/api/applications/123/status?status=reviewing"

# Update status to offer
curl -X PATCH "http://localhost:8000/api/applications/123/status?status=offer"

# Update status to rejected
curl -X PATCH "http://localhost:8000/api/applications/123/status?status=rejected"
```

---

## Tracking API

### Quick Application Tracking

Simplified endpoint for external job tracking with minimal required fields.

**Endpoint:** `POST /api/tracking/track`

**Required Fields:**
- `company` (string): Company name
- `title` (string): Job title

**Optional Fields:**
- `url` (string): Job posting URL
- `notes` (string): Optional notes

**Examples:**

```bash
# Minimal tracking
curl -X POST "http://localhost:8000/api/tracking/track" \
  -H "Content-Type: application/json" \
  -d '{
    "company": "Tech Corp Inc.",
    "title": "Senior Software Engineer"
  }'

# With URL and notes
curl -X POST "http://localhost:8000/api/tracking/track" \
  -H "Content-Type: application/json" \
  -d '{
    "company": "StartupXYZ",
    "title": "Full Stack Developer",
    "url": "https://startupxyz.com/careers/fullstack",
    "notes": "Found through AngelList, exciting startup"
  }'

# Browser extension usage
curl -X POST "http://localhost:8000/api/tracking/track" \
  -H "Content-Type: application/json" \
  -d '{
    "company": "Netflix",
    "title": "Backend Engineer",
    "url": "https://jobs.netflix.com/jobs/123456",
    "notes": "Applied via company website"
  }'
```

**Response Example:**
```json
{
  "tracking_id": 12345,
  "company": "Tech Corp Inc.",
  "title": "Senior Software Engineer",
  "status": "applied",
  "created_at": "2024-08-24T10:30:00Z"
}
```

### Get Application History

Get comprehensive history for a specific application including status changes, interactions, and timeline.

**Endpoint:** `GET /api/tracking/application-history/{application_id}`

**Examples:**

```bash
# Get complete history
curl "http://localhost:8000/api/tracking/application-history/123"

# With authentication
curl -H "X-API-Key: your-api-key" \
  "http://localhost:8000/api/tracking/application-history/123"
```

**Response Example:**
```json
{
  "application": {
    "id": 123,
    "company_name": "Google Inc.",
    "job_title": "Senior Software Engineer",
    "status": "technical_interview",
    "created_at": "2024-01-15T10:30:00Z"
  },
  "status_changes": [
    {
      "from_status": "applied",
      "to_status": "phone_screen",
      "changed_at": "2024-01-22T14:00:00Z",
      "description": "Moved to phone screen stage"
    }
  ],
  "interactions": [...],
  "interview_stages": [
    {
      "stage": "Technical Interview - Round 1",
      "date": "2024-01-25",
      "outcome": "Positive feedback",
      "description": "1-hour technical interview"
    }
  ],
  "timeline": [...]
}
```

### Get Analytics Stats

Get comprehensive analytics data for dashboard visualization.

**Endpoint:** `GET /api/tracking/stats`

**Examples:**

```bash
# Get analytics data
curl "http://localhost:8000/api/tracking/stats"

# With authentication
curl -H "X-API-Key: your-api-key" \
  "http://localhost:8000/api/tracking/stats"
```

**Response Example:**
```json
{
  "total_applications": 50,
  "applications_by_status": {
    "applied": 20,
    "reviewing": 10,
    "phone_screen": 8,
    "technical_interview": 5,
    "offer": 2,
    "rejected": 5
  },
  "applications_by_month": {
    "2024-01": 15,
    "2024-02": 20,
    "2024-03": 15
  },
  "success_rate": 4.0,
  "average_response_time": 7.5,
  "top_companies": [
    {"company_name": "Google Inc.", "count": 3},
    {"company_name": "Microsoft", "count": 2}
  ],
  "salary_range": {
    "min": 80000,
    "max": 200000,
    "avg": 140000
  },
  "active_applications": 25
}
```

### Add Interaction to History

Add a new interaction or note to an application's history.

**Endpoint:** `POST /api/tracking/application-history/{application_id}/interaction`

**Query Parameters:**
- `interaction_type` (string, required): Type of interaction
- `title` (string, required): Interaction title
- `description` (string, optional): Detailed description
- `outcome` (string, optional): Outcome or result

**Examples:**

```bash
# Add phone call interaction
curl -X POST "http://localhost:8000/api/tracking/application-history/123/interaction" \
  -H "Content-Type: application/json" \
  -d "interaction_type=phone_call&title=Follow-up Call&description=Called to check on status&outcome=Will hear back next week"

# Add interview interaction
curl -X POST "http://localhost:8000/api/tracking/application-history/123/interaction" \
  -H "Content-Type: application/json" \
  -d "interaction_type=interview&title=Technical Interview&description=90-minute technical interview&outcome=Positive feedback, moving to final round"

# Add email interaction
curl -X POST "http://localhost:8000/api/tracking/application-history/123/interaction" \
  -H "Content-Type: application/json" \
  -d "interaction_type=email&title=Thank You Email&description=Sent thank you email after interview"
```

### Get Recent Activity

Get recent applications and interactions for dashboard overview.

**Endpoint:** `GET /api/tracking/recent-activity`

**Query Parameters:**
- `days` (integer): Number of days to look back (1-30, default: 7)
- `limit` (integer): Maximum items to return (1-50, default: 10)

**Examples:**

```bash
# Get last 7 days of activity
curl "http://localhost:8000/api/tracking/recent-activity"

# Get last 14 days, limit to 20 items
curl "http://localhost:8000/api/tracking/recent-activity?days=14&limit=20"

# Get recent activity for last 30 days
curl "http://localhost:8000/api/tracking/recent-activity?days=30&limit=50"
```

**Response Example:**
```json
{
  "recent_activity": [
    {
      "id": 125,
      "company_name": "Netflix",
      "job_title": "Backend Engineer",
      "status": "applied",
      "application_date": "2024-01-30",
      "type": "application"
    },
    {
      "id": 15,
      "application_id": 123,
      "company_name": "Google Inc.",
      "title": "Phone Screen Completed",
      "interaction_type": "interview",
      "interaction_date": "2024-01-29",
      "type": "interaction"
    }
  ],
  "total_found": 15,
  "days_back": 7,
  "generated_at": "2024-01-30T10:30:00Z"
}
```

---

## Rate Limiting

The API implements rate limiting to ensure fair usage:

- **Default**: 100 requests per minute per IP address
- **Authenticated users**: May have higher limits
- **Rate limit headers** are included in responses:
  - `X-RateLimit-Limit`: Request limit
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Reset timestamp

**Example Response Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

**Rate Limit Exceeded Response:**
```json
{
  "success": false,
  "message": "Rate limit exceeded",
  "errors": ["Too many requests. Please try again later."],
  "error_code": "RATE_LIMIT_EXCEEDED",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## Postman Collection

Download the complete Postman collection for easy API testing:

**Collection URL:** `http://localhost:8000/docs/postman`

```bash
# Download Postman collection
curl "http://localhost:8000/docs/postman" -o job-tracker-api.postman_collection.json
```

The collection includes:
- Pre-configured requests for all endpoints
- Environment variables for base URL and API key
- Example request bodies and responses
- Authentication setup

### Environment Variables

Set these variables in your Postman environment:
- `base_url`: `http://localhost:8000` (or your API URL)
- `api_key`: Your API key (if authentication is enabled)

---

## Additional Resources

- **Interactive Documentation**: `http://localhost:8000/docs`
- **ReDoc Documentation**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`
- **API Information**: `http://localhost:8000/docs/info`
- **Health Check**: `http://localhost:8000/health`

### Example Scripts

**Bash script for bulk application creation:**
```bash
#!/bin/bash

# Array of companies and roles
companies=(
  "Google Inc.:Senior Software Engineer"
  "Microsoft:Software Engineer II"
  "Amazon:SDE II"
  "Netflix:Backend Engineer"
  "Apple:iOS Engineer"
)

for company_role in "${companies[@]}"
do
  IFS=':' read -ra ADDR <<< "$company_role"
  company="${ADDR[0]}"
  role="${ADDR[1]}"
  
  curl -X POST "http://localhost:8000/api/applications/" \
    -H "Content-Type: application/json" \
    -d "{
      \"company_name\": \"$company\",
      \"job_title\": \"$role\",
      \"application_date\": \"$(date +%Y-%m-%d)\",
      \"status\": \"applied\",
      \"priority\": \"medium\"
    }"
  
  echo "Created application for $company - $role"
  sleep 1
done
```

**Python script for analytics:**
```python
import requests

# Get analytics data
response = requests.get("http://localhost:8000/api/tracking/stats")
stats = response.json()

print(f"Total Applications: {stats['total_applications']}")
print(f"Success Rate: {stats['success_rate']}%")
print(f"Active Applications: {stats['active_applications']}")
print("\nTop Companies:")
for company in stats['top_companies']:
    print(f"  - {company['company_name']}: {company['count']} applications")
```

---

## Support

For API support and questions:
- **Email**: api-support@example.com
- **GitHub**: [Job Tracker API Repository](https://github.com/yourusername/job-tracker-api)
- **Documentation**: Available at `/docs` endpoint

---

*Last updated: January 30, 2024*

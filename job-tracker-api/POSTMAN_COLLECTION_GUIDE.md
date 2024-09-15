# 🚀 Job Application Tracker API - Postman Collection Guide

## 📋 Overview

This comprehensive Postman collection provides complete testing and integration capabilities for the Job Application Tracker API. The collection includes all endpoints, extensive test scripts, environment configurations, and detailed documentation.

## 📁 Files Included

### 🎯 Main Collection
- **`job-tracker-api-enhanced.postman_collection.json`** - Enhanced collection with full features
- **`job-tracker-api.postman_collection.json`** - Original collection (backup)

### 🌍 Environment Configurations
- **`postman-environments.json`** - Complete environment configurations
  - 🛠️ Local Development (`http://localhost:8000`)
  - 🚀 Production (`https://your-production-api.com`)
  - 🧪 Staging (`https://staging-api.your-domain.com`)

## 🚀 Quick Start

### 1. Import Collection & Environment
1. Open Postman
2. Click **Import** → **Upload Files**
3. Import `job-tracker-api-enhanced.postman_collection.json`
4. Import `postman-environments.json`
5. Select **🛠️ Local Development** environment

### 2. Configure Environment
- Set `base_url` to your API server
- Set `api_key` if authentication is required
- Verify `environment_name` is set correctly

### 3. Test Connection
- Run **📊 Health Check** to verify connectivity
- Check **🏠 Root Endpoint** for API information
- Verify **📖 OpenAPI Schema** is accessible

## 📁 Collection Structure

### 📋 Applications Module
Complete CRUD operations for job applications:

- **📄 List Applications** - Paginated listing with filters
- **➕ Create Application** - Create new applications
- **🔍 Get Application by ID** - Retrieve specific applications
- **✏️ Update Application** - Full and partial updates
- **🗑️ Delete Application** - Remove applications
- **📊 Get by Status** - Filter by application status
- **🏢 Get by Company** - Filter by company name
- **🔄 Update Status** - Quick status updates

### 📊 Tracking & Analytics Module
Advanced tracking and analytics features:

- **📤 Quick Track Application** - Simplified application entry
- **📜 Get Application History** - Comprehensive history tracking
- **📊 Get Analytics Stats** - Dashboard statistics
- **💬 Add Interaction** - Add notes and interactions
- **⏰ Get Recent Activity** - Recent applications and updates

### ⚙️ General Module
System and documentation endpoints:

- **🏠 Root Endpoint** - API information and status
- **📊 Health Check** - System health monitoring
- **📖 API Documentation Info** - Documentation links
- **🔗 OpenAPI Schema** - Complete API specification

## 🧪 Advanced Testing Features

### 🔄 Pre-request Scripts
Automatically executed before each request:

- **🆔 Request ID Generation** - Unique tracking IDs
- **⏰ Timestamp Setting** - Current timestamps
- **🏷️ Header Injection** - Common headers and metadata
- **🔐 Authentication Handling** - API key management
- **📊 Environment Detection** - Environment-specific logic

### ✅ Response Tests
Comprehensive validation for all endpoints:

- **⚡ Performance Testing** - Response time validation
- **📊 Status Code Validation** - HTTP status verification
- **📄 Content Type Checking** - JSON response validation
- **🏗️ Structure Validation** - Response schema verification
- **🔗 Variable Chaining** - Auto-store IDs for subsequent requests

### 📊 Collection Variables
Dynamic variables for seamless testing:

- `application_id` - Sample application ID
- `created_application_id` - Auto-set from creation tests
- `sample_company` - Test company name
- `sample_job_title` - Test job title

## 🔍 Filtering & Search Examples

### 📊 Basic Pagination
```
GET /api/applications/?page=1&limit=20
```

### 🔍 Status Filtering
```
GET /api/applications/?status=applied&status=reviewing
```

### 🏢 Company Search
```
GET /api/applications/?company_name=Google
```

### 🔤 Full-text Search
```
GET /api/applications/?search=python engineer
```

### 📅 Date Range Filtering
```
GET /api/applications/?date_from=2024-01-01&date_to=2024-03-31
```

### 🔄 Sorting
```
GET /api/applications/?sort_by=created_at&sort_order=desc
```

### 🎯 Combined Filters
```
GET /api/applications/?status=applied&company_name=tech&sort_by=priority&sort_order=desc&limit=10
```

## 🔐 Authentication Setup

### API Key Authentication
1. Set `api_key` in your environment variables
2. The collection automatically adds `X-API-Key` header
3. Supports both environment and collection-level auth

### Bearer Token (Future)
```javascript
// Pre-request script for bearer token
if (pm.environment.get('access_token')) {
    pm.request.headers.add({
        key: 'Authorization',
        value: 'Bearer ' + pm.environment.get('access_token')
    });
}
```

## 💡 Common Use Cases

### 🚀 Quick Application Entry Workflow
1. **📤 Quick Track Application** - Minimal data entry
2. **✏️ Update Application** - Add detailed information
3. **💬 Add Interaction** - Track follow-ups

### 📊 Analytics Dashboard Workflow
1. **📊 Get Analytics Stats** - Overall statistics
2. **⏰ Get Recent Activity** - Recent changes
3. **📜 Get Application History** - Detailed tracking

### 🔍 Search & Filter Workflow
1. **📄 List Applications** - Basic listing
2. Apply filters: status, company, dates
3. **🔍 Get Application by ID** - Detailed view

### 🔄 Bulk Management Workflow
1. **📄 List Applications** with pagination
2. **✏️ Update Application** in bulk
3. **📊 Get Analytics Stats** to verify changes

## 🧰 Integration Examples

### 🌐 Browser Extension Integration
```javascript
// Quick track from job posting page
fetch('{{base_url}}/api/tracking/track', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'your-api-key'
  },
  body: JSON.stringify({
    company: document.querySelector('.company-name').textContent,
    title: document.querySelector('.job-title').textContent,
    url: window.location.href,
    notes: 'Applied via browser extension'
  })
})
.then(response => response.json())
.then(data => {
  console.log('Application tracked:', data.tracking_id);
});
```

### 📱 Mobile App Integration
```javascript
// React Native example
const trackApplication = async (jobData) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/tracking/track`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY
      },
      body: JSON.stringify(jobData)
    });
    
    const result = await response.json();
    return result.tracking_id;
  } catch (error) {
    console.error('Failed to track application:', error);
  }
};
```

### 📊 Dashboard Analytics
```javascript
// Fetch analytics for dashboard
const getDashboardData = async () => {
  const [stats, recentActivity] = await Promise.all([
    fetch(`${API_BASE_URL}/api/tracking/stats`).then(r => r.json()),
    fetch(`${API_BASE_URL}/api/tracking/recent-activity?days=7`).then(r => r.json())
  ]);
  
  return {
    totalApplications: stats.total_applications,
    successRate: stats.success_rate,
    recentActivity: recentActivity.recent_activity
  };
};
```

## 🔧 Custom Scripts

### 📊 Collection Runner Scripts
For automated testing workflows:

```javascript
// Collection pre-request script for test data generation
pm.globals.set('test_company', 'Test Company ' + Date.now());
pm.globals.set('test_job_title', 'Test Job ' + Math.random().toString(36).substring(7));
pm.globals.set('test_date', new Date().toISOString().split('T')[0]);
```

### 🧪 Test Data Generation
```javascript
// Generate random test application
const generateTestApplication = () => {
  const companies = ['Google', 'Microsoft', 'Apple', 'Amazon', 'Meta'];
  const titles = ['Software Engineer', 'Product Manager', 'Data Scientist'];
  const locations = ['San Francisco', 'Seattle', 'New York', 'Austin'];
  
  return {
    company_name: companies[Math.floor(Math.random() * companies.length)],
    job_title: titles[Math.floor(Math.random() * titles.length)],
    location: locations[Math.floor(Math.random() * locations.length)],
    salary_min: Math.floor(Math.random() * 50000) + 80000,
    salary_max: Math.floor(Math.random() * 80000) + 120000
  };
};
```

## 🚨 Error Handling

### Common Response Formats
```json
// Success Response
{
  "success": true,
  "message": "Operation completed successfully",
  "data": { /* response payload */ },
  "timestamp": "2024-01-15T10:30:00Z"
}

// Error Response
{
  "success": false,
  "message": "Validation error",
  "errors": ["Company name is required"],
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2024-01-15T10:30:00Z"
}

// FastAPI Validation Error
{
  "detail": [
    {
      "loc": ["body", "company_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### Error Test Scripts
```javascript
// Test error responses
if (pm.response.code >= 400) {
    pm.test('Error response has proper structure', function () {
        const jsonData = pm.response.json();
        if (jsonData.detail) {
            // FastAPI format
            pm.expect(jsonData).to.have.property('detail');
        } else {
            // Custom format
            pm.expect(jsonData).to.have.property('success').that.equals(false);
            pm.expect(jsonData).to.have.property('message');
        }
    });
}
```

## 📊 Performance Monitoring

### Response Time Testing
```javascript
// Test response time with environment-specific thresholds
const maxResponseTime = parseInt(pm.environment.get('request_timeout')) || 5000;
pm.test(`Response time < ${maxResponseTime}ms`, function () {
    pm.expect(pm.response.responseTime).to.be.below(maxResponseTime);
});

// Log slow responses
if (pm.response.responseTime > 3000) {
    console.warn(`Slow response: ${pm.response.responseTime}ms`);
}
```

### Load Testing Preparation
```javascript
// Collection runner preparation
const runnerData = [];
for (let i = 0; i < 100; i++) {
    runnerData.push({
        company_name: `Test Company ${i}`,
        job_title: `Test Position ${i}`,
        application_date: new Date().toISOString().split('T')[0]
    });
}
```

## 🔄 Continuous Integration

### Newman CLI Usage
```bash
# Install Newman
npm install -g newman

# Run collection with environment
newman run job-tracker-api-enhanced.postman_collection.json \
  -e postman-environments.json \
  --env-var "base_url=http://localhost:8000" \
  --reporters cli,json \
  --reporter-json-export results.json

# Run with specific folder
newman run job-tracker-api-enhanced.postman_collection.json \
  -e postman-environments.json \
  --folder "Applications" \
  --bail
```

### GitHub Actions Integration
```yaml
# .github/workflows/api-tests.yml
name: API Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
        with:
          node-version: '16'
      - run: npm install -g newman
      - name: Start API Server
        run: python main.py &
      - name: Wait for API
        run: sleep 10
      - name: Run Postman Tests
        run: |
          newman run job-tracker-api-enhanced.postman_collection.json \
            -e postman-environments.json \
            --env-var "base_url=http://localhost:8000" \
            --reporters cli,junit \
            --reporter-junit-export results.xml
```

## 📖 Documentation Links

Once the API is deployed, the collection automatically provides access to:

- **Interactive Documentation**: `{{base_url}}/docs`
- **ReDoc Documentation**: `{{base_url}}/redoc`
- **OpenAPI JSON**: `{{base_url}}/openapi.json`

## 🤝 Contributing

To enhance the collection:

1. Fork the repository
2. Import the collection into Postman
3. Make your changes
4. Export the updated collection
5. Submit a pull request with your improvements

## 📞 Support

For questions about the Postman collection:

- Check the built-in documentation in each request
- Review test scripts for usage examples
- Consult the API documentation at `/docs`
- Open an issue in the repository

## 📝 Changelog

### Version 2.0.0 - Enhanced Collection
- ✅ Comprehensive pre-request and test scripts
- 🌍 Multiple environment configurations
- 📊 Advanced filtering and search examples
- 🔐 Authentication handling
- 📱 Integration examples
- 🧪 Performance monitoring
- 📖 Extensive documentation

### Version 1.0.0 - Basic Collection
- ✅ Basic CRUD operations
- 📊 Simple test scripts
- 🌍 Single environment setup
- 📄 Basic documentation

## 🏆 Best Practices

### 🔧 Collection Organization
- Use descriptive names with emojis
- Group related endpoints in folders
- Include comprehensive descriptions
- Provide multiple response examples

### 🧪 Testing Strategy
- Test both success and error scenarios
- Validate response structure and data
- Chain requests using variables
- Monitor performance metrics

### 🌍 Environment Management
- Use environment variables for all configurable values
- Separate development, staging, and production
- Include debug flags for detailed logging
- Set appropriate timeout values

### 📊 Documentation
- Document each endpoint thoroughly
- Provide usage examples
- Include common error scenarios
- Maintain up-to-date response samples

---

**🎯 Happy Testing!** This collection provides everything you need to effectively test and integrate with the Job Application Tracker API.

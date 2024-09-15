# 🚀 Job Application Tracker API - Postman Collection

## 📋 Quick Import Guide

### 🎯 1. Import the Collection

**Option A: Import Files**
1. Download these files from the repository:
   - `job-tracker-api-enhanced.postman_collection.json`
   - `postman-environments.json`
2. Open Postman
3. Click **Import** → **Upload Files**
4. Select both files and import

**Option B: Import URL (if published)**
1. Open Postman
2. Click **Import** → **Link**
3. Paste the collection URL
4. Click **Continue** → **Import**

### 🌍 2. Set Up Environment
1. Select **🛠️ Local Development** environment
2. Set variables:
   - `base_url`: `http://localhost:8000` (or your server URL)
   - `api_key`: Your API key (if authentication required)
3. Save the environment

### 🔬 3. Test the Setup
1. Run **📊 Health Check** to verify connectivity
2. Check **🏠 Root Endpoint** for API information
3. Try **📄 List Applications** to test the main functionality

## 🎯 Postman Documentation Link

Once you've imported the collection, you can generate a public documentation link:

### 📖 Generate Documentation
1. Right-click on the collection in Postman
2. Select **View Documentation**
3. Click **Publish** in the top-right corner
4. Choose your settings:
   - **Environment**: Select the appropriate environment
   - **Logo**: Add your API logo (optional)
   - **Custom Domain**: Use custom domain if available
5. Click **Publish Collection**
6. Copy the generated documentation URL

### 🔗 Documentation URL Format
```
https://documenter.getpostman.com/view/[user-id]/[collection-id]/[version-id]
```

### 📊 Documentation Features
The published documentation includes:
- Complete endpoint documentation
- Request/response examples
- Parameter descriptions
- Authentication setup
- Code samples in multiple languages
- Try-it-now functionality

## 📁 Collection Overview

### 🗂️ Folder Structure
```
🚀 Job Application Tracker API - Enhanced/
├── 📁 Applications
│   ├── 📄 List Applications
│   ├── ➕ Create Application
│   ├── 🔍 Get Application by ID
│   ├── ✏️ Update Application
│   ├── 🗑️ Delete Application
│   ├── 📊 Get by Status
│   ├── 🏢 Get by Company
│   └── 🔄 Update Status
├── 📁 Tracking & Analytics
│   ├── 📤 Quick Track Application
│   ├── 📜 Get Application History
│   ├── 📊 Get Analytics Stats
│   ├── 💬 Add Interaction
│   └── ⏰ Get Recent Activity
└── 📁 General
    ├── 🏠 Root Endpoint
    ├── 📊 Health Check
    ├── 📖 API Documentation Info
    └── 🔗 OpenAPI Schema
```

## 🌍 Environment Configurations

### 🛠️ Local Development
```json
{
  "base_url": "http://localhost:8000",
  "environment_name": "development",
  "debug_mode": "true",
  "request_timeout": "10000"
}
```

### 🚀 Production
```json
{
  "base_url": "https://your-production-api.com",
  "environment_name": "production", 
  "debug_mode": "false",
  "request_timeout": "5000"
}
```

### 🧪 Staging
```json
{
  "base_url": "https://staging-api.your-domain.com",
  "environment_name": "staging",
  "debug_mode": "true", 
  "request_timeout": "7500"
}
```

## 🚀 Quick Start Workflows

### 📝 Basic Testing Workflow
1. **📊 Health Check** - Verify API is running
2. **📄 List Applications** - See existing data
3. **➕ Create Application** - Add test data
4. **🔍 Get Application by ID** - Retrieve specific record
5. **📊 Get Analytics Stats** - View statistics

### 🔍 Search & Filter Workflow
1. **📄 List Applications** (basic)
2. Enable query parameters:
   - `company_name`: "Google" 
   - `status`: "applied"
   - `search`: "engineer"
3. Test different filter combinations

### 📊 Analytics Workflow
1. **📊 Get Analytics Stats** - Overall metrics
2. **⏰ Get Recent Activity** - Recent changes
3. **📜 Get Application History** - Detailed tracking (use existing ID)

## 🔧 Advanced Usage

### 🧪 Collection Runner
1. Select collection or folder
2. Click **Run** button
3. Configure:
   - **Environment**: Choose target environment
   - **Iterations**: Number of runs
   - **Delay**: Between requests
   - **Data File**: CSV for bulk testing (optional)
4. Click **Start Run**

### 📊 Newman CLI
```bash
# Install Newman
npm install -g newman

# Basic run
newman run job-tracker-api-enhanced.postman_collection.json \
  -e postman-environments.json

# With custom environment variables
newman run job-tracker-api-enhanced.postman_collection.json \
  -e postman-environments.json \
  --env-var "base_url=http://localhost:8000" \
  --env-var "api_key=your-key-here"

# Generate reports
newman run job-tracker-api-enhanced.postman_collection.json \
  -e postman-environments.json \
  --reporters cli,json,html \
  --reporter-html-export report.html
```

## 🔐 Authentication Setup

### API Key Authentication
If your API requires authentication:

1. **Set Environment Variable**:
   - Variable: `api_key`
   - Value: Your actual API key
   - Type: `secret` (to hide value)

2. **Verify Headers**:
   - The collection automatically adds `X-API-Key` header
   - Check in request preview before sending

### Custom Authentication
To modify authentication:

1. **Collection Level**: 
   - Right-click collection → **Edit**
   - Go to **Authorization** tab
   - Choose auth type and configure

2. **Request Level**:
   - Select individual request
   - Go to **Authorization** tab
   - Override collection auth if needed

## 🧪 Testing Features

### ✅ Automatic Tests
Every request includes tests for:
- Response time validation
- Status code verification
- JSON structure validation
- Business logic verification
- Error handling validation

### 📊 Test Results
View test results in:
- **Test Results** tab after running requests
- **Collection Runner** for batch testing
- **Newman** CLI output for automation

### 🔗 Variable Chaining
Tests automatically store values for reuse:
- `application_id` - From list requests
- `created_application_id` - From create requests
- Use `{{variable_name}}` in subsequent requests

## 🚨 Troubleshooting

### Common Issues

**❌ Connection Refused**
- Check if API server is running
- Verify `base_url` in environment
- Test with simple curl command

**❌ 401 Unauthorized** 
- Verify API key is set correctly
- Check authentication method
- Ensure key has proper permissions

**❌ 404 Not Found**
- Check endpoint URLs are correct
- Verify API version compatibility
- Check if endpoints exist in your API

**❌ Timeout Errors**
- Increase `request_timeout` in environment
- Check server performance
- Verify network connectivity

### Getting Help

1. **Check Console**: View detailed logs in Postman Console
2. **Test Scripts**: Review test failures for specific errors  
3. **Documentation**: Refer to endpoint descriptions
4. **API Logs**: Check your API server logs

## 📱 Integration Examples

### JavaScript/Node.js
```javascript
const baseUrl = 'http://localhost:8000';

// Create application
const createApp = async (appData) => {
  const response = await fetch(`${baseUrl}/api/applications/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': 'your-api-key'
    },
    body: JSON.stringify(appData)
  });
  return response.json();
};
```

### Python
```python
import requests

base_url = 'http://localhost:8000'
headers = {
    'Content-Type': 'application/json',
    'X-API-Key': 'your-api-key'
}

# List applications
response = requests.get(f'{base_url}/api/applications/', headers=headers)
applications = response.json()
```

### cURL
```bash
# List applications
curl -X GET "http://localhost:8000/api/applications/" \
  -H "X-API-Key: your-api-key"

# Create application
curl -X POST "http://localhost:8000/api/applications/" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"company_name":"Test Corp","job_title":"Developer"}'
```

## 🎯 Best Practices

### 🔧 Collection Management
- Keep environments synchronized
- Use meaningful variable names
- Document custom variables
- Version control collection files

### 🧪 Testing
- Run health checks first
- Test error scenarios
- Validate response structure
- Monitor performance metrics

### 🔐 Security
- Use secret variables for sensitive data
- Don't commit API keys to version control
- Use different keys per environment
- Rotate keys regularly

### 📊 Documentation  
- Keep descriptions up to date
- Add examples for complex requests
- Document parameter requirements
- Include error response examples

## 📞 Support

For help with the Postman collection:

1. **Documentation**: Check request descriptions and examples
2. **Tests**: Review test script outputs for detailed error information
3. **API Docs**: Visit `{{base_url}}/docs` for interactive documentation
4. **Issues**: Report problems in the project repository

## 🎉 You're Ready!

With the collection imported and configured, you can now:

- ✅ Test all API endpoints
- 🔍 Explore filtering and search capabilities  
- 📊 Generate analytics reports
- 🧪 Run automated tests
- 📱 Develop integrations
- 📖 Share documentation with your team

**Happy API testing!** 🚀

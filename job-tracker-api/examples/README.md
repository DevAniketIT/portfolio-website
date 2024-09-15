# JavaScript/Node.js Client Examples

This directory contains comprehensive JavaScript and Node.js client examples for the Job Application Tracker API.

## 📁 Files

- **`javascript_client_example.js`** - Browser-compatible JavaScript client using Fetch API
- **`node_client_example.js`** - Node.js client with advanced features using axios
- **`package.json`** - Dependencies and scripts for running the examples
- **`README.md`** - This documentation file

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd examples
npm install
```

### 2. Set Environment Variables

```bash
# For local development
export API_BASE_URL=http://localhost:8000

# For production API
export API_BASE_URL=https://your-service-name.onrender.com

# If your API requires authentication
export API_KEY=your-api-key
```

### 3. Run Examples

```bash
# Run Node.js example (recommended)
npm run demo

# Run against local API
npm run test:local

# Run against production API
npm run test:production

# Run with API key
npm run demo:with-key
```

## 📊 Features Demonstrated

### ✅ CRUD Operations
- ✅ Create applications
- ✅ Read/fetch applications by ID
- ✅ Update applications (full and partial)
- ✅ Delete applications
- ✅ List applications with filtering

### ✅ Tracking Features
- ✅ Quick tracking for external tools
- ✅ Analytics and statistics
- ✅ Application history and interactions
- ✅ Recent activity monitoring

### ✅ Advanced Features
- ✅ Bulk operations with batching
- ✅ File-based data import
- ✅ Progress reporting
- ✅ Comprehensive error handling
- ✅ Retry logic with exponential backoff
- ✅ Environment variable configuration

### ✅ Error Handling
- ✅ Network error handling
- ✅ API validation errors
- ✅ Server error handling
- ✅ Timeout handling
- ✅ Rate limiting handling

## 🔧 Configuration Options

### Environment Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `API_BASE_URL` | API server base URL | `https://your-service-name.onrender.com` | `https://api.example.com` |
| `API_KEY` | API key for authentication | `null` | `your-secret-key` |
| `REQUEST_TIMEOUT` | Request timeout in milliseconds | `30000` | `60000` |
| `RETRY_ATTEMPTS` | Number of retry attempts | `3` | `5` |
| `RETRY_DELAY_MS` | Base retry delay in milliseconds | `1000` | `2000` |

### Configuration Examples

```bash
# Local development
API_BASE_URL=http://localhost:8000 node node_client_example.js

# Production with authentication
API_BASE_URL=https://your-api.onrender.com API_KEY=your-key node node_client_example.js

# With custom timeout and retry settings
API_BASE_URL=https://api.example.com REQUEST_TIMEOUT=60000 RETRY_ATTEMPTS=5 node node_client_example.js
```

## 📖 Usage Examples

### Browser Usage (JavaScript)

```html
<!DOCTYPE html>
<html>
<head>
    <title>Job Tracker API Example</title>
</head>
<body>
    <script type="module">
        // Set API configuration
        window.API_BASE_URL = 'https://your-api.onrender.com';
        window.API_KEY = 'your-api-key'; // optional
        
        // Import functions
        import { listApplications, createApplication, runAsyncDemo } from './javascript_client_example.js';
        
        // Run demo
        runAsyncDemo();
    </script>
</body>
</html>
```

### Node.js Usage

```javascript
import { createApplication, listApplications } from './node_client_example.js';

// Create a new application
const newApp = await createApplication({
  company_name: 'Example Corp',
  job_title: 'Software Engineer',
  status: 'applied'
});

// List applications with filtering
const apps = await listApplications({
  status: ['applied', 'reviewing'],
  limit: 10
});

console.log('Applications:', apps.items);
```

## 🧪 Testing Against Production API

The examples are designed to work with both local development and production APIs. Here's how to test against your deployed API:

### Step 1: Identify Your Production URL

Your production API URL will typically be in the format:
- Render: `https://your-service-name.onrender.com`
- Heroku: `https://your-app-name.herokuapp.com`
- Custom domain: `https://api.yourdomain.com`

### Step 2: Test Health Check

```bash
# Test API health
curl https://your-api.onrender.com/health

# Expected response:
# {"status":"healthy","database_status":"connected"}
```

### Step 3: Run Client Examples

```bash
# Test with your production URL
API_BASE_URL=https://your-api.onrender.com node node_client_example.js
```

### Step 4: Verify All Operations

The Node.js example will automatically test:
1. ✅ Health check
2. ✅ Create application
3. ✅ Read application
4. ✅ Update application
5. ✅ Status updates
6. ✅ List applications
7. ✅ Quick tracking
8. ✅ Analytics
9. ✅ File import
10. ✅ Bulk operations
11. ✅ Cleanup

## 🚨 Troubleshooting

### Common Issues

#### 1. Connection Errors
```
❌ Health check failed
Network Error: getaddrinfo ENOTFOUND your-service-name.onrender.com
```

**Solution:** Check your API URL and ensure the server is running.

#### 2. CORS Errors (Browser)
```
Access to fetch at 'https://api.example.com' from origin 'http://localhost:3000' has been blocked by CORS policy
```

**Solution:** Configure CORS in your API server to allow your frontend domain.

#### 3. Authentication Errors
```
❌ Create application failed:
Status: 401
Message: Missing or invalid API key
```

**Solution:** Set the `API_KEY` environment variable or disable authentication.

#### 4. Validation Errors
```
❌ Create application failed:
Status: 422
Message: Validation error
Errors: Company name is required, Job title is required
```

**Solution:** Ensure required fields are provided in your request data.

### Debug Mode

Enable verbose logging by setting debug environment variables:

```bash
DEBUG=axios:* API_BASE_URL=https://your-api.com node node_client_example.js
```

## 📚 API Endpoints Reference

### Applications API
- `GET /api/applications/` - List applications
- `POST /api/applications/` - Create application
- `GET /api/applications/{id}` - Get specific application
- `PUT /api/applications/{id}` - Update application
- `DELETE /api/applications/{id}` - Delete application
- `PATCH /api/applications/{id}/status` - Update status only

### Tracking API
- `POST /api/tracking/track` - Quick track application
- `GET /api/tracking/stats` - Get analytics stats
- `GET /api/tracking/application-history/{id}` - Get application history
- `POST /api/tracking/application-history/{id}/interaction` - Add interaction
- `GET /api/tracking/recent-activity` - Get recent activity

### Utility Endpoints
- `GET /health` - Health check
- `GET /docs` - API documentation
- `GET /` - API information

## 🔐 Security Considerations

### API Keys
- Never commit API keys to version control
- Use environment variables for sensitive data
- Rotate API keys regularly

### HTTPS
- Always use HTTPS in production
- Validate SSL certificates

### Error Handling
- Don't expose sensitive information in error messages
- Log errors appropriately for debugging

## 🤝 Contributing

To improve these examples:

1. Fork the repository
2. Create a feature branch
3. Add your improvements
4. Test thoroughly
5. Submit a pull request

### Adding New Features

When adding new API endpoints, follow this pattern:

```javascript
export async function newEndpoint(params) {
  try {
    const response = await api.post('/api/new-endpoint', params);
    return response.data;
  } catch (error) {
    handleError(error, 'New endpoint operation');
    throw error;
  }
}
```

## 📄 License

MIT License - feel free to use these examples in your projects.

---

## 🆘 Need Help?

- **API Documentation**: Visit your API's `/docs` endpoint
- **Issues**: Check the repository issues page
- **Support**: Contact the API maintainers

**Happy coding! 🚀**

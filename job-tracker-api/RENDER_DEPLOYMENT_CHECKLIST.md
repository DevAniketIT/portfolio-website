# Render.com Deployment Checklist

## 📋 Pre-Deployment Checklist

### ✅ Prerequisites
- [ ] GitHub account created
- [ ] Render.com account created (go to [render.com](https://render.com) and sign up)
- [ ] All project files are ready in your local directory
- [ ] Git is installed on your system

### ✅ Project Structure Verification
Your project should have these files:
- [ ] `main.py` - FastAPI application
- [ ] `requirements.txt` - Python dependencies
- [ ] `Procfile` - Process definition
- [ ] `render.yaml` - Render configuration
- [ ] `start.sh` - Startup script
- [ ] `.env.production` - Environment variables template
- [ ] `routers/` - API route definitions
- [ ] `postgresql_db.py` - Database initialization
- [ ] All other Python modules

## 🚀 Step-by-Step Deployment Process

### Step 1: Create GitHub Repository
If you haven't already created a GitHub repository:

```bash
# Initialize git repository (if not already done)
git init

# Create .gitignore file
echo "__pycache__/
*.pyc
*.pyo
*.pyd
.env
.venv/
venv/
.DS_Store
*.log" > .gitignore

# Add all files
git add .

# Commit files
git commit -m "Initial commit: Job Application Tracker API"

# Create repository on GitHub and push
# Follow GitHub instructions to push to your new repository
```

### Step 2: Set Up Render.com Account
1. [ ] Go to [render.com](https://render.com)
2. [ ] Sign up with GitHub account (recommended)
3. [ ] Verify your email address
4. [ ] Complete account setup

### Step 3: Deploy with render.yaml (Recommended)
1. [ ] In Render Dashboard, click "New" → "Blueprint"
2. [ ] Connect your GitHub repository
3. [ ] Select the repository containing your code
4. [ ] Render will automatically detect `render.yaml`
5. [ ] Review the configuration:
   - [ ] Web Service: `job-tracker-api`
   - [ ] Database: `job-tracker-db` (PostgreSQL)
   - [ ] Environment variables are configured
6. [ ] Click "Apply" to start deployment

### Step 4: Monitor Deployment
1. [ ] Watch the build logs for any errors
2. [ ] Verify database creation completes
3. [ ] Check that web service starts successfully
4. [ ] Wait for health check to pass

### Step 5: Configure Environment Variables (if needed)
If you need to add custom environment variables:
1. [ ] Go to your web service in Render Dashboard
2. [ ] Click "Environment" tab
3. [ ] Add these required variables:

```bash
# Core Settings
DATABASE_TYPE=postgresql
ENVIRONMENT=production
DEBUG=false

# Server Settings (auto-configured by Render)
# HOST=0.0.0.0
# PORT=10000

# Security Settings
API_KEY_REQUIRED=false
API_KEY=your-secure-api-key-here

# CORS Settings (update for production)
CORS_ORIGINS=*
CORS_METHODS=GET,POST,PUT,DELETE,OPTIONS
CORS_HEADERS=*

# Rate Limiting
RATE_LIMIT_REQUESTS=1000
RATE_LIMIT_WINDOW=60
```

## 🔍 Verification Steps

### Step 6: Test API Endpoints
Once deployed, test these endpoints:

1. [ ] **Root Endpoint**
   ```bash
   curl https://your-service-name.onrender.com/
   ```

2. [ ] **Health Check**
   ```bash
   curl https://your-service-name.onrender.com/health
   ```

3. [ ] **API Documentation**
   - [ ] Visit: `https://your-service-name.onrender.com/docs`
   - [ ] Verify interactive docs load correctly

4. [ ] **Applications Endpoints**
   ```bash
   # Get all applications
   curl https://your-service-name.onrender.com/api/applications

   # Create test application
   curl -X POST https://your-service-name.onrender.com/api/applications \
     -H "Content-Type: application/json" \
     -d '{
       "company": "Test Company",
       "position": "Software Engineer",
       "status": "applied",
       "applied_date": "2024-12-19",
       "job_url": "https://example.com/job"
     }'
   ```

5. [ ] **Tracking Endpoints**
   ```bash
   # Get tracking data
   curl https://your-service-name.onrender.com/api/tracking/status-summary
   ```

### Step 7: Database Verification
1. [ ] Check database connection in Render Dashboard
2. [ ] Verify tables were created correctly
3. [ ] Test CRUD operations work properly

## 📊 Production Configuration

### Step 8: Production Security (Important!)
1. [ ] **Update CORS Origins**
   ```bash
   CORS_ORIGINS=https://your-frontend.com,https://your-domain.com
   ```

2. [ ] **Enable API Authentication (if needed)**
   ```bash
   API_KEY_REQUIRED=true
   API_KEY=your-secure-random-api-key
   ```

3. [ ] **Configure Rate Limiting**
   ```bash
   RATE_LIMIT_REQUESTS=100  # Adjust based on needs
   RATE_LIMIT_WINDOW=60
   ```

### Step 9: Monitoring Setup
1. [ ] Set up uptime monitoring in Render Dashboard
2. [ ] Configure email alerts for downtime
3. [ ] Monitor logs for errors
4. [ ] Set up performance alerts

### Step 10: Custom Domain (Optional)
1. [ ] Purchase domain name
2. [ ] In Render Dashboard, go to your service
3. [ ] Click "Settings" → "Custom Domains"
4. [ ] Add your domain
5. [ ] Configure DNS records as instructed
6. [ ] Wait for SSL certificate provisioning

## 🧪 Testing Checklist

### Step 11: Comprehensive API Testing

Use this curl script to test all endpoints:

```bash
#!/bin/bash
API_URL="https://your-service-name.onrender.com"

echo "🧪 Testing Job Application Tracker API"
echo "API URL: $API_URL"

# Test 1: Health Check
echo "1. Testing health check..."
curl -s "$API_URL/health" | jq '.' || echo "❌ Health check failed"

# Test 2: Root endpoint
echo "2. Testing root endpoint..."
curl -s "$API_URL/" | jq '.' || echo "❌ Root endpoint failed"

# Test 3: Create application
echo "3. Creating test application..."
APP_RESPONSE=$(curl -s -X POST "$API_URL/api/applications" \
  -H "Content-Type: application/json" \
  -d '{
    "company": "Test Company",
    "position": "Software Engineer",
    "status": "applied",
    "applied_date": "2024-12-19",
    "job_url": "https://example.com/job"
  }')
echo "$APP_RESPONSE" | jq '.' || echo "❌ Create application failed"

# Extract application ID for further tests
APP_ID=$(echo "$APP_RESPONSE" | jq -r '.id')

# Test 4: Get all applications
echo "4. Getting all applications..."
curl -s "$API_URL/api/applications" | jq '.' || echo "❌ Get applications failed"

# Test 5: Get specific application
echo "5. Getting specific application..."
curl -s "$API_URL/api/applications/$APP_ID" | jq '.' || echo "❌ Get specific application failed"

# Test 6: Update application
echo "6. Updating application..."
curl -s -X PUT "$API_URL/api/applications/$APP_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "company": "Updated Company",
    "position": "Senior Software Engineer",
    "status": "interviewing"
  }' | jq '.' || echo "❌ Update application failed"

# Test 7: Tracking endpoints
echo "7. Testing tracking endpoints..."
curl -s "$API_URL/api/tracking/status-summary" | jq '.' || echo "❌ Status summary failed"

echo "✅ API testing completed!"
```

## 🎯 Success Criteria

### Your deployment is successful when:
- [ ] All API endpoints return expected responses
- [ ] Database operations work correctly
- [ ] Health check returns healthy status
- [ ] API documentation is accessible
- [ ] No errors in application logs
- [ ] Response times are acceptable (< 2 seconds)

## 📝 Post-Deployment Tasks

### Step 12: Documentation Update
1. [ ] Update API documentation with production URL
2. [ ] Create client integration guide
3. [ ] Document any custom configuration

### Step 13: Performance Monitoring
1. [ ] Monitor response times
2. [ ] Check database performance
3. [ ] Monitor error rates
4. [ ] Set up log aggregation if needed

### Step 14: Backup Verification
1. [ ] Verify automatic database backups are enabled
2. [ ] Test database restore process
3. [ ] Document disaster recovery procedures

## 🆘 Troubleshooting

### Common Issues and Solutions

1. **Build Failures**
   - Check `requirements.txt` for typos
   - Verify Python version compatibility
   - Check for missing dependencies

2. **Database Connection Errors**
   - Verify DATABASE_URL is correctly set
   - Check database service is running
   - Ensure database and web service are in same region

3. **Module Import Errors**
   - Check file structure
   - Verify all Python files are present
   - Check for circular imports

4. **Port Binding Issues**
   - Don't override PORT in production (Render sets it to 10000)
   - Use HOST=0.0.0.0

5. **Performance Issues**
   - Monitor resource usage
   - Consider upgrading plan
   - Optimize database queries

## 📞 Support Resources

- Render Documentation: https://render.com/docs
- Community Forum: https://community.render.com
- Support Email: support@render.com

## 🎉 Deployment Complete!

Once all checkboxes are completed, your API will be:
- ✅ Deployed and running on Render.com
- ✅ Connected to PostgreSQL database
- ✅ Accessible via HTTPS
- ✅ Ready for production use

**Your API URLs:**
- API Base: `https://your-service-name.onrender.com`
- Documentation: `https://your-service-name.onrender.com/docs`
- Health Check: `https://your-service-name.onrender.com/health`

Remember to replace `your-service-name` with your actual Render service name!

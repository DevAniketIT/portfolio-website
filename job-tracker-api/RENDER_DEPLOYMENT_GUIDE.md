# 🚀 Job Tracker API - Render.com Deployment Guide

## Prerequisites Checklist

✅ Your FastAPI application is ready and tested locally
✅ All required files are present (main.py, requirements.txt, Procfile, start.sh)
✅ Environment variables are configured (.env.example provided)
✅ Git repository is initialized

## Step 1: Push to GitHub Repository

Since Render.com deploys from GitHub, you need to push your code first:

### 1.1 Create GitHub Repository
1. Go to https://github.com and sign in with your account
2. Click "New" to create a new repository
3. Name it: `job-tracker-api`
4. Make it public (or private if you have a paid GitHub account)
5. Don't initialize with README (you already have files)

### 1.2 Connect Local Repository to GitHub
```bash
# Add GitHub remote (replace YOUR_GITHUB_USERNAME)
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/job-tracker-api.git

# Push your code
git add .
git commit -m "Initial commit - Job Tracker API ready for deployment"
git branch -M main
git push -u origin main
```

## Step 2: Create Render.com Account

### 2.1 Account Setup
1. **Go to**: https://render.com
2. **Sign up with**: aniket.kumar.devpro@gmail.com
3. **Choose**: "Sign up with GitHub" for easy integration
4. **Authorize**: Render to access your GitHub repositories
5. **Verify**: Your email address when prompted

## Step 3: Deploy Your API

### 3.1 Create Web Service
1. **Click**: "New +" button in Render dashboard
2. **Select**: "Web Service"
3. **Connect Repository**: Choose your `job-tracker-api` repository
4. **Configure Settings**:

#### Basic Configuration
- **Name**: `job-tracker-api-aniket`
- **Region**: Oregon (or closest to your location)
- **Branch**: `main`
- **Runtime**: Python 3
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

#### Environment Variables (Add these in Render dashboard)
```
ENVIRONMENT=production
DEBUG=false
API_KEY_REQUIRED=false
RATE_LIMIT_REQUESTS=1000
RATE_LIMIT_WINDOW=60
CORS_ORIGINS=*
CORS_METHODS=GET,POST,PUT,DELETE,OPTIONS
CORS_HEADERS=*
LOG_LEVEL=INFO
HEALTH_CHECK_PATH=/health
```

### 3.2 Add PostgreSQL Database
1. **In Render dashboard**: Click "New +" → "PostgreSQL"
2. **Configure**:
   - **Name**: `job-tracker-db`
   - **Database Name**: `job_tracker_production`
   - **User**: `job_tracker_user`
   - **Plan**: Free tier
   - **Region**: Same as web service (Oregon)
3. **Create Database**

### 3.3 Connect Database to Web Service
1. **Go to**: Your web service settings
2. **Environment Variables section**
3. **Add**: `DATABASE_URL`
4. **Value**: Copy from your PostgreSQL service connection string
   - Format: `postgresql://username:password@hostname:port/database_name`

## Step 4: Deploy and Verify

### 4.1 Initial Deployment
1. **Click**: "Create Web Service"
2. **Monitor**: Build logs for any errors
3. **Wait**: For deployment to complete (usually 2-5 minutes)

### 4.2 Verify Deployment
Your API will be available at: `https://job-tracker-api-aniket.onrender.com`

**Test Endpoints**:
- **Root**: `https://job-tracker-api-aniket.onrender.com/`
- **Health Check**: `https://job-tracker-api-aniket.onrender.com/health`
- **API Docs**: `https://job-tracker-api-aniket.onrender.com/docs`
- **Applications**: `https://job-tracker-api-aniket.onrender.com/api/applications`

## Step 5: Post-Deployment Configuration

### 5.1 Custom Domain (Optional)
1. **Purchase domain** or use existing
2. **In Render**: Go to web service → Settings → Custom Domains
3. **Add domain** and follow DNS configuration instructions

### 5.2 Monitoring Setup
1. **Enable auto-deploy**: Automatic deployment on git push
2. **Set up alerts**: For service health monitoring
3. **Configure logging**: Check logs in Render dashboard

## Troubleshooting Common Issues

### Build Failures
- **Check**: requirements.txt for correct package versions
- **Verify**: Python version compatibility
- **Review**: Build logs for specific error messages

### Database Connection Issues
- **Verify**: DATABASE_URL format is correct
- **Check**: Database service is running
- **Ensure**: Web service and database are in same region

### Application Startup Issues
- **Review**: start.sh script permissions and syntax
- **Check**: Environment variables are set correctly
- **Verify**: Port configuration matches Render requirements

## Important Notes

⚠️ **Free Tier Limitations**:
- Service spins down after 15 minutes of inactivity
- 750 hours per month limit
- Database storage limit: 1GB

🔒 **Security Considerations**:
- Update CORS_ORIGINS in production with actual frontend domains
- Set strong API_KEY if enabling authentication
- Use environment variables for all secrets

📊 **Performance Optimization**:
- Monitor response times in Render dashboard
- Upgrade to paid tier for better performance
- Use connection pooling for database

## Next Steps After Deployment

1. **Test all endpoints** using Postman or API client
2. **Update frontend** to use production API URL
3. **Set up monitoring** and alerting
4. **Configure backup** strategy for database
5. **Plan scaling** strategy for increased traffic

## Support Resources

- **Render Docs**: https://render.com/docs
- **API Documentation**: Available at `/docs` endpoint
- **GitHub Issues**: Use for bug reports and feature requests

---

🎉 **Congratulations!** Your Job Tracker API is now live in production!

**Your API URL**: `https://job-tracker-api-aniket.onrender.com`

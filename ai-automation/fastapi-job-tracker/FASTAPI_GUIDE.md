# FastAPI Job Tracker - Complete Learning Guide

## Week 4: FastAPI + Modern Web Development

This guide demonstrates how to build a complete REST API for job application tracking using FastAPI. You've successfully learned:

### ✅ What You've Built

1. **Modern REST API**: Complete CRUD operations for job applications
2. **Authentication System**: JWT-based authentication with password hashing
3. **Database Integration**: SQLAlchemy ORM with PostgreSQL/SQLite support
4. **Data Validation**: Pydantic models for request/response validation
5. **Production-Ready Deployment**: Docker containerization and Render.com deployment
6. **API Documentation**: Auto-generated interactive docs with Swagger UI

## 🏗️ Project Architecture

```
fastapi-job-tracker/
├── main.py                 # FastAPI app entry point
├── config.py              # Application configuration
├── models.py              # SQLAlchemy database models
├── schemas.py             # Pydantic validation models
├── database.py            # Database connection setup
├── auth.py                # Authentication & JWT handling
├── crud.py                # Database CRUD operations
├── routers/               # API route modules
│   ├── __init__.py
│   ├── auth.py           # Authentication endpoints
│   └── jobs.py           # Job application endpoints
├── requirements.txt       # Development dependencies
├── requirements-prod.txt  # Production dependencies
├── Dockerfile            # Container configuration
├── render.yaml           # Render.com deployment config
└── README.md             # Complete documentation
```

## 🔑 Key FastAPI Concepts Learned

### 1. FastAPI Application Structure
```python
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Job Tracker API",
    version="1.0.0",
    description="Modern job application tracking API"
)

# Add CORS middleware for frontend integration
app.add_middleware(CORSMiddleware, allow_origins=["*"])
```

### 2. Pydantic Data Models
```python
from pydantic import BaseModel, EmailStr, Field

class JobApplicationCreate(BaseModel):
    title: str = Field(..., max_length=255)
    company: str = Field(..., max_length=255)
    description: Optional[str] = None
    status: ApplicationStatus = ApplicationStatus.APPLIED
```

### 3. Database Integration with SQLAlchemy
```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class JobApplication(Base):
    __tablename__ = "job_applications"
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
```

### 4. Authentication & Security
```python
from passlib.context import CryptContext
from jose import jwt

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"])

def create_access_token(data: dict):
    encoded_jwt = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

### 5. API Routes with Dependencies
```python
@router.post("/jobs/", response_model=JobApplication)
async def create_application(
    application: JobApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return create_job_application(db, application, current_user.id)
```

## 🛠️ API Endpoints Built

### Authentication Endpoints
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user info
- `POST /api/v1/auth/verify-token` - Verify JWT token

### Job Application Endpoints
- `POST /api/v1/jobs/` - Create job application
- `GET /api/v1/jobs/` - List applications (with filtering & pagination)
- `GET /api/v1/jobs/{id}` - Get specific application
- `PUT /api/v1/jobs/{id}` - Update application
- `DELETE /api/v1/jobs/{id}` - Delete application
- `PATCH /api/v1/jobs/{id}/status` - Update application status
- `GET /api/v1/jobs/stats/summary` - Get application statistics

### System Endpoints
- `GET /` - API information
- `GET /health` - Health check

## 📝 Example API Usage

### 1. Register a User
```bash
curl -X POST "https://your-api.render.com/api/v1/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "developer@example.com",
       "full_name": "Jane Developer", 
       "password": "securepassword123"
     }'
```

### 2. Login and Get Token
```bash
curl -X POST "https://your-api.render.com/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "developer@example.com",
       "password": "securepassword123"
     }'
```

### 3. Create Job Application
```bash
curl -X POST "https://your-api.render.com/api/v1/jobs/" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -d '{
       "title": "Senior Python Developer",
       "company": "Tech Startup Inc",
       "description": "Backend development with FastAPI",
       "location": "Remote",
       "salary_range": "$90k - $130k",
       "job_url": "https://company.com/careers/python-dev"
     }'
```

### 4. Get All Applications with Filtering
```bash
# Get all applications
curl -X GET "https://your-api.render.com/api/v1/jobs/" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Filter by status
curl -X GET "https://your-api.render.com/api/v1/jobs/?status=interviewing" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Filter by company
curl -X GET "https://your-api.render.com/api/v1/jobs/?company=Google" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 🚀 Deployment Process

### 1. Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python main.py

# Visit http://localhost:8000/docs for interactive API documentation
```

### 2. Production Deployment on Render.com
1. **Create Database**: PostgreSQL database on Render
2. **Deploy Web Service**: Connect GitHub repo, set environment variables
3. **Environment Variables**:
   - `DATABASE_URL`: PostgreSQL connection string
   - `SECRET_KEY`: JWT secret key
   - `DEBUG`: False for production

### 3. Container Deployment
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements-prod.txt .
RUN pip install -r requirements-prod.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 💡 Key Features Implemented

### 1. Data Validation
- Email format validation
- Password strength requirements
- Field length constraints
- Enum validation for application status

### 2. Security Features
- Password hashing with bcrypt
- JWT token authentication
- CORS middleware
- SQL injection protection
- Input sanitization

### 3. Database Operations
- User management
- Job application CRUD
- Filtering and pagination
- Statistics and reporting
- Foreign key relationships

### 4. API Best Practices
- RESTful URL structure
- HTTP status codes
- Error handling
- Response models
- API versioning

## 🎯 Freelance-Ready Skills

You now have the skills to build APIs for:

### 1. Mobile App Backends
```python
# Mobile apps can consume your REST API
# iOS/Android apps → FastAPI → Database
@app.get("/api/v1/jobs/")
async def get_jobs_for_mobile():
    # Returns JSON that mobile apps can consume
    pass
```

### 2. Web Application Backends  
```python
# React/Vue/Angular frontends can use your API
# SPA Frontend → FastAPI → Database
@app.post("/api/v1/jobs/")
async def create_job_for_web():
    # CORS enabled for browser requests
    pass
```

### 3. Microservices Architecture
```python
# Your API can be part of larger systems
# Service A → Your FastAPI → Service B
@app.get("/api/v1/integrations/external")
async def integrate_with_external_service():
    pass
```

## 📚 What You've Mastered

1. **FastAPI Framework**: Modern Python web framework
2. **RESTful API Design**: Industry-standard API patterns  
3. **Database Design**: Relational models and relationships
4. **Authentication**: JWT tokens and security best practices
5. **Data Validation**: Input validation and error handling
6. **Deployment**: Production deployment on cloud platforms
7. **Documentation**: Auto-generated API docs
8. **Testing**: API testing strategies
9. **Docker**: Containerization for deployment
10. **Cloud Deployment**: Platform-as-a-Service deployment

## 🔥 Next Steps for Freelancing

### Immediate Opportunities
1. **Build client APIs**: Restaurants, gyms, small businesses
2. **Create mobile app backends**: iOS/Android app APIs
3. **Develop web dashboards**: Admin panels and analytics
4. **Integrate systems**: Connect different business tools

### Advanced Extensions
1. **Add real-time features**: WebSocket support
2. **Implement caching**: Redis for performance
3. **Add file uploads**: Resume/document storage
4. **Create notifications**: Email/SMS integration
5. **Build analytics**: Data visualization APIs

## 🎉 Congratulations!

You've successfully completed Week 4 and built a production-ready REST API with FastAPI! You now have:

- ✅ Modern web development skills
- ✅ Database integration knowledge  
- ✅ Authentication implementation experience
- ✅ Cloud deployment capabilities
- ✅ API design best practices
- ✅ Freelance-ready backend development skills

**You're now equipped to build APIs for mobile apps, websites, and business systems!**

## 📁 Project Files Summary

All the code you've learned is organized in these files:

- **`main.py`** - FastAPI application entry point
- **`models.py`** - Database models (User, JobApplication)  
- **`schemas.py`** - Pydantic validation models
- **`auth.py`** - JWT authentication system
- **`crud.py`** - Database operations
- **`routers/`** - API endpoint organization
- **`requirements.txt`** - Project dependencies
- **`Dockerfile`** - Container configuration
- **`render.yaml`** - Deployment configuration
- **`README.md`** - Complete project documentation

This project serves as a template for any REST API you'll build in your freelance career!

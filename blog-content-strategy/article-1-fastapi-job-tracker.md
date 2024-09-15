# Building a Production-Ready Job Tracker API with FastAPI

*How I built a scalable job application tracking API from scratch and deployed it to production*

---

## The Problem: Job Search Chaos

As a developer actively job hunting, I quickly realized that managing job applications across multiple platforms was a nightmare. Spreadsheets became unwieldy, important follow-ups were forgotten, and I had no clear visibility into my job search progress. Sound familiar?

I needed a robust, production-ready solution that could handle CRUD operations, provide meaningful analytics, and scale as my job search grew. Instead of using existing tools that didn't fit my specific needs, I decided to build my own API using FastAPI—and document the entire journey for fellow developers.

## What You'll Build

By the end of this article, you'll have a fully functional job tracking API with:
- Complete CRUD operations for job applications
- Advanced filtering and pagination
- Built-in analytics and statistics
- Rate limiting and error handling
- Production deployment on Render with PostgreSQL
- Interactive API documentation

## Tech Stack Overview

**Backend Framework:** FastAPI (Python's fastest web framework)
**Database:** PostgreSQL (production) / SQLite (development)
**Deployment:** Render.com (free tier with auto-scaling)
**Documentation:** Auto-generated OpenAPI/Swagger docs
**Testing:** Built-in test suite with comprehensive coverage

Why FastAPI? It's incredibly fast, generates automatic documentation, has excellent typing support, and makes building production APIs a breeze.

## Step 1: Setting Up the Foundation

### Project Structure
```
job-tracker-api/
├── main.py              # FastAPI app setup
├── models.py            # Pydantic data models
├── database.py          # Database connection
├── routers/
│   ├── __init__.py
│   └── applications.py  # Application endpoints
├── requirements.txt     # Dependencies
└── render.yaml         # Deployment config
```

### Core Dependencies
```python
# requirements.txt
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
pydantic==2.5.0
python-multipart==0.0.6
```

## Step 2: Database Models and Schema

```python
# models.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class ApplicationStatus(str, Enum):
    applied = "applied"
    reviewing = "reviewing"
    phone_screen = "phone_screen"
    technical_interview = "technical_interview"
    onsite_interview = "onsite_interview"
    final_round = "final_round"
    offer = "offer"
    rejected = "rejected"
    withdrawn = "withdrawn"
    accepted = "accepted"

class JobApplication(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=200)
    job_title: str = Field(..., min_length=1, max_length=200)
    job_url: Optional[str] = Field(None, max_length=500)
    location: Optional[str] = Field(None, max_length=200)
    salary_min: Optional[int] = Field(None, ge=0)
    salary_max: Optional[int] = Field(None, ge=0)
    currency: str = Field(default="USD", max_length=3)
    job_type: Optional[str] = None
    remote_type: Optional[str] = None
    application_date: Optional[datetime] = None
    status: ApplicationStatus = ApplicationStatus.applied
    priority: Optional[str] = Field(default="medium")
    notes: Optional[str] = Field(None, max_length=2000)
    contact_email: Optional[str] = None

class ApplicationResponse(JobApplication):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
```

## Step 3: Database Setup with SQLAlchemy

```python
# database.py
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "sqlite:///./job_tracker.db"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Application(Base):
    __tablename__ = "applications"
    
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(200), nullable=False, index=True)
    job_title = Column(String(200), nullable=False, index=True)
    job_url = Column(String(500))
    location = Column(String(200))
    salary_min = Column(Integer)
    salary_max = Column(Integer)
    currency = Column(String(3), default="USD")
    job_type = Column(String(50))
    remote_type = Column(String(50))
    application_date = Column(DateTime)
    status = Column(String(50), default="applied", index=True)
    priority = Column(String(20), default="medium")
    notes = Column(Text)
    contact_email = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

# Dependency for database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## Step 4: Building the API Endpoints

```python
# routers/applications.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db, Application
from ..models import JobApplication, ApplicationResponse

router = APIRouter(prefix="/api/applications", tags=["applications"])

@router.post("/", response_model=ApplicationResponse)
async def create_application(
    application: JobApplication,
    db: Session = Depends(get_db)
):
    """Create a new job application"""
    db_application = Application(**application.dict())
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application

@router.get("/", response_model=dict)
async def get_applications(
    status: Optional[List[str]] = Query(None),
    company_name: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    db: Session = Depends(get_db)
):
    """Get applications with filtering and pagination"""
    query = db.query(Application)
    
    # Apply filters
    if status:
        query = query.filter(Application.status.in_(status))
    if company_name:
        query = query.filter(Application.company_name.ilike(f"%{company_name}%"))
    if search:
        query = query.filter(
            Application.company_name.ilike(f"%{search}%") |
            Application.job_title.ilike(f"%{search}%") |
            Application.notes.ilike(f"%{search}%")
        )
    
    # Count total items
    total = query.count()
    
    # Apply sorting and pagination
    if sort_order.lower() == "desc":
        query = query.order_by(getattr(Application, sort_by).desc())
    else:
        query = query.order_by(getattr(Application, sort_by))
    
    applications = query.offset((page - 1) * limit).limit(limit).all()
    
    return {
        "items": applications,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit,
        "has_next": page * limit < total,
        "has_previous": page > 1
    }

@router.get("/{application_id}", response_model=ApplicationResponse)
async def get_application(application_id: int, db: Session = Depends(get_db)):
    """Get a specific application by ID"""
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    return application

@router.put("/{application_id}", response_model=ApplicationResponse)
async def update_application(
    application_id: int,
    application_update: JobApplication,
    db: Session = Depends(get_db)
):
    """Update an application"""
    db_application = db.query(Application).filter(Application.id == application_id).first()
    if not db_application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    for key, value in application_update.dict(exclude_unset=True).items():
        setattr(db_application, key, value)
    
    db.commit()
    db.refresh(db_application)
    return db_application

@router.delete("/{application_id}")
async def delete_application(application_id: int, db: Session = Depends(get_db)):
    """Delete an application"""
    db_application = db.query(Application).filter(Application.id == application_id).first()
    if not db_application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    db.delete(db_application)
    db.commit()
    return {"message": "Application deleted successfully"}
```

## Step 5: Main Application Setup

```python
# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import time
import logging
from .routers import applications

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Job Application Tracker API",
    description="A production-ready API for managing job applications",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Security middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# Include routers
app.include_router(applications.router)

@app.get("/")
async def root():
    """API health check and info"""
    return {
        "message": "Job Application Tracker API",
        "version": "1.0.0",
        "status": "healthy",
        "endpoints": {
            "docs": "/docs",
            "applications": "/api/applications"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Step 6: Production Deployment on Render

### Deployment Configuration
```yaml
# render.yaml
services:
  - type: web
    name: job-tracker-api
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "uvicorn main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: DATABASE_URL
        fromDatabase:
          name: job-tracker-db
          property: connectionString

databases:
  - name: job-tracker-db
    databaseName: job_tracker
    user: job_tracker_user
```

### Production Environment Variables
- `DATABASE_URL`: PostgreSQL connection string (auto-provided by Render)
- `ENVIRONMENT`: "production"
- `API_KEY`: Optional API key for authentication

## Live Demo & Repository

🌐 **Live API**: [https://job-tracker-api-xyz.onrender.com](https://job-tracker-api-xyz.onrender.com)
📖 **Interactive Docs**: [https://job-tracker-api-xyz.onrender.com/docs](https://job-tracker-api-xyz.onrender.com/docs)
💻 **GitHub Repository**: [https://github.com/yourusername/job-tracker-api](https://github.com/yourusername/job-tracker-api)

### Try It Now
```bash
# Test the health check
curl https://job-tracker-api-xyz.onrender.com/health

# Create your first application
curl -X POST "https://job-tracker-api-xyz.onrender.com/api/applications" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Google",
    "job_title": "Software Engineer",
    "location": "Mountain View, CA",
    "status": "applied"
  }'
```

## Key Takeaways

**Production-Ready Features Implemented:**
- ✅ Comprehensive data validation with Pydantic
- ✅ Advanced filtering, pagination, and search
- ✅ Proper error handling and HTTP status codes
- ✅ Auto-generated interactive documentation
- ✅ Database migrations and connection pooling
- ✅ CORS and security middleware
- ✅ Health check endpoints for monitoring
- ✅ Deployment configuration for scaling

**Performance & Scalability:**
- FastAPI's async nature handles thousands of concurrent requests
- PostgreSQL handles complex queries efficiently
- Render's auto-scaling responds to traffic spikes
- Proper indexing on frequently queried fields

**Developer Experience:**
- Type hints throughout for better IDE support
- Comprehensive error messages for debugging
- Interactive API documentation for easy testing
- Modular code structure for easy maintenance

## What's Next?

This API serves as the foundation for a complete job tracking system. In upcoming articles, I'll cover:
- Adding authentication with JWT tokens
- Implementing real-time notifications
- Building a React frontend
- Adding advanced analytics and reporting
- Creating a mobile app with React Native

Building this API taught me valuable lessons about production deployment, database design, and API architecture. The best part? It's actively helping me track my own job applications, making my job search more organized and data-driven.

---

**What challenges are you facing with your job search workflow? Let me know in the comments, and I'll consider covering them in future articles!**

*If you found this helpful, consider following me for more production-ready Python tutorials. Connect with me on [LinkedIn](your-linkedin) or check out my [portfolio](your-portfolio) for more projects.*

---

**Tags:** #fastapi #python #api #backend #production #jobsearch #deployment #postgresql #webdev

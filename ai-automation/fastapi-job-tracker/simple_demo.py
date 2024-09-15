"""
Simple FastAPI Job Tracker Demo
This demonstrates the key concepts of building a REST API with FastAPI
"""

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import sqlite3
import hashlib
import json
from datetime import datetime

# Simple in-memory database simulation
fake_users_db = {}
fake_jobs_db = {}
user_counter = 1
job_counter = 1

app = FastAPI(
    title="Job Tracker API Demo",
    description="A simple demonstration of FastAPI for job application tracking",
    version="1.0.0"
)

# Pydantic models
class UserCreate(BaseModel):
    email: str
    full_name: str
    password: str

class User(BaseModel):
    id: int
    email: str
    full_name: str

class JobApplicationCreate(BaseModel):
    title: str
    company: str
    description: Optional[str] = None
    location: Optional[str] = None
    salary_range: Optional[str] = None
    status: str = "applied"

class JobApplication(BaseModel):
    id: int
    title: str
    company: str
    description: Optional[str] = None
    location: Optional[str] = None
    salary_range: Optional[str] = None
    status: str
    owner_id: int
    created_at: str

# Helper functions
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def get_current_user() -> User:
    # Simplified auth - in reality, you'd use JWT tokens
    if fake_users_db:
        user_id = list(fake_users_db.keys())[0]  # Use first user for demo
        return User(**fake_users_db[user_id])
    raise HTTPException(status_code=401, detail="No users registered")

# API Routes
@app.get("/")
async def root():
    return {
        "message": "Welcome to the Job Tracker API Demo!",
        "endpoints": {
            "register": "POST /register",
            "jobs": "GET/POST /jobs",
            "health": "GET /health"
        }
    }

@app.post("/register", response_model=User)
async def register_user(user: UserCreate):
    """Register a new user"""
    global user_counter
    
    # Check if email exists
    for existing_user in fake_users_db.values():
        if existing_user["email"] == user.email:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    user_id = user_counter
    user_counter += 1
    
    new_user = {
        "id": user_id,
        "email": user.email,
        "full_name": user.full_name,
        "password_hash": hash_password(user.password)
    }
    
    fake_users_db[user_id] = new_user
    
    # Return user without password
    return User(id=user_id, email=user.email, full_name=user.full_name)

@app.post("/jobs", response_model=JobApplication)
async def create_job_application(job: JobApplicationCreate):
    """Create a new job application"""
    global job_counter
    
    # Get current user (simplified)
    current_user = get_current_user()
    
    # Create new job application
    job_id = job_counter
    job_counter += 1
    
    new_job = {
        "id": job_id,
        "title": job.title,
        "company": job.company,
        "description": job.description,
        "location": job.location,
        "salary_range": job.salary_range,
        "status": job.status,
        "owner_id": current_user.id,
        "created_at": datetime.now().isoformat()
    }
    
    fake_jobs_db[job_id] = new_job
    
    return JobApplication(**new_job)

@app.get("/jobs", response_model=List[JobApplication])
async def get_job_applications():
    """Get all job applications for current user"""
    current_user = get_current_user()
    
    user_jobs = [
        JobApplication(**job) 
        for job in fake_jobs_db.values() 
        if job["owner_id"] == current_user.id
    ]
    
    return user_jobs

@app.get("/jobs/{job_id}", response_model=JobApplication)
async def get_job_application(job_id: int):
    """Get a specific job application"""
    current_user = get_current_user()
    
    if job_id not in fake_jobs_db:
        raise HTTPException(status_code=404, detail="Job application not found")
    
    job = fake_jobs_db[job_id]
    if job["owner_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this job")
    
    return JobApplication(**job)

@app.put("/jobs/{job_id}", response_model=JobApplication)
async def update_job_application(job_id: int, job_update: JobApplicationCreate):
    """Update a job application"""
    current_user = get_current_user()
    
    if job_id not in fake_jobs_db:
        raise HTTPException(status_code=404, detail="Job application not found")
    
    job = fake_jobs_db[job_id]
    if job["owner_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this job")
    
    # Update job
    job.update({
        "title": job_update.title,
        "company": job_update.company,
        "description": job_update.description,
        "location": job_update.location,
        "salary_range": job_update.salary_range,
        "status": job_update.status,
    })
    
    return JobApplication(**job)

@app.delete("/jobs/{job_id}")
async def delete_job_application(job_id: int):
    """Delete a job application"""
    current_user = get_current_user()
    
    if job_id not in fake_jobs_db:
        raise HTTPException(status_code=404, detail="Job application not found")
    
    job = fake_jobs_db[job_id]
    if job["owner_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this job")
    
    del fake_jobs_db[job_id]
    return {"message": "Job application deleted successfully"}

@app.get("/stats")
async def get_application_stats():
    """Get application statistics"""
    current_user = get_current_user()
    
    user_jobs = [job for job in fake_jobs_db.values() if job["owner_id"] == current_user.id]
    
    stats = {
        "total": len(user_jobs),
        "by_status": {}
    }
    
    for job in user_jobs:
        status = job["status"]
        stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
    
    return stats

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "users_registered": len(fake_users_db),
        "jobs_tracked": len(fake_jobs_db),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    print("Starting Job Tracker API Demo...")
    print("Visit http://127.0.0.1:8000/docs to see the interactive API documentation")
    uvicorn.run(app, host="127.0.0.1", port=8000)

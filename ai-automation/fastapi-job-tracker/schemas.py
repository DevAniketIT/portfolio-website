from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from models import ApplicationStatus


# User schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None


class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True


# Job Application schemas
class JobApplicationBase(BaseModel):
    title: str = Field(..., max_length=255)
    company: str = Field(..., max_length=255)
    description: Optional[str] = None
    location: Optional[str] = Field(None, max_length=255)
    salary_range: Optional[str] = Field(None, max_length=100)
    job_url: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = None
    contact_person: Optional[str] = Field(None, max_length=255)
    contact_email: Optional[EmailStr] = None


class JobApplicationCreate(JobApplicationBase):
    status: Optional[ApplicationStatus] = ApplicationStatus.APPLIED


class JobApplicationUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    company: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    location: Optional[str] = Field(None, max_length=255)
    salary_range: Optional[str] = Field(None, max_length=100)
    job_url: Optional[str] = Field(None, max_length=500)
    status: Optional[ApplicationStatus] = None
    notes: Optional[str] = None
    contact_person: Optional[str] = Field(None, max_length=255)
    contact_email: Optional[EmailStr] = None


class JobApplication(JobApplicationBase):
    id: int
    status: ApplicationStatus
    applied_date: datetime
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True


class JobApplicationWithOwner(JobApplication):
    owner: User


# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# API Response schemas
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None


class JobApplicationList(BaseModel):
    applications: List[JobApplication]
    total: int
    page: int
    per_page: int

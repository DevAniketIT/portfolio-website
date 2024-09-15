"""
Pydantic models for job application tracking API.

This module contains all the data models used throughout the API for
request/response validation, database schemas, and data transfer objects.
"""

from pydantic import BaseModel, HttpUrl, Field, validator, EmailStr
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date
from enum import Enum
import re

# Enums for job application status and types
class ApplicationStatus(str, Enum):
    """Job application status options."""
    APPLIED = "applied"
    REVIEWING = "reviewing"
    PHONE_SCREEN = "phone_screen"
    TECHNICAL_INTERVIEW = "technical_interview"
    ONSITE_INTERVIEW = "onsite_interview"
    FINAL_ROUND = "final_round"
    OFFER = "offer"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"
    ACCEPTED = "accepted"

class JobType(str, Enum):
    """Job type options."""
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    FREELANCE = "freelance"

class RemoteType(str, Enum):
    """Remote work options."""
    ON_SITE = "on_site"
    REMOTE = "remote"
    HYBRID = "hybrid"

class Priority(str, Enum):
    """Application priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class InteractionType(str, Enum):
    """Types of interactions with companies."""
    APPLICATION = "application"
    EMAIL = "email"
    PHONE_CALL = "phone_call"
    INTERVIEW = "interview"
    FOLLOW_UP = "follow_up"
    NETWORKING = "networking"
    OTHER = "other"

# Base models with timestamp functionality
class TimestampMixin(BaseModel):
    """Mixin for timestamp fields."""
    created_at: Optional[datetime] = Field(
        None,
        description="Timestamp when the record was created",
        example="2024-01-15T10:30:00Z"
    )
    updated_at: Optional[datetime] = Field(
        None,
        description="Timestamp when the record was last updated",
        example="2024-01-15T14:30:00Z"
    )

# Core application models
class ApplicationBase(BaseModel):
    """Base model for job applications with core fields."""
    company_name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Name of the company",
        example="Google Inc."
    )
    job_title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Title of the job position",
        example="Senior Software Engineer"
    )
    job_url: Optional[HttpUrl] = Field(
        None,
        description="URL to the job posting",
        example="https://careers.google.com/jobs/results/123456789"
    )
    job_description: Optional[str] = Field(
        None,
        max_length=5000,
        description="Description of the job role and requirements",
        example="We are looking for a Senior Software Engineer to join our team..."
    )
    location: Optional[str] = Field(
        None,
        max_length=200,
        description="Job location (city, state, country)",
        example="Mountain View, CA, USA"
    )
    salary_min: Optional[int] = Field(
        None,
        ge=0,
        description="Minimum salary range",
        example=120000
    )
    salary_max: Optional[int] = Field(
        None,
        ge=0,
        description="Maximum salary range",
        example=180000
    )
    currency: str = Field(
        default="USD",
        max_length=3,
        description="Currency code for salary",
        example="USD"
    )
    job_type: Optional[JobType] = Field(
        None,
        description="Type of employment",
        example=JobType.FULL_TIME
    )
    remote_type: Optional[RemoteType] = Field(
        None,
        description="Remote work arrangement",
        example=RemoteType.HYBRID
    )
    application_date: Optional[date] = Field(
        None,
        description="Date when the application was submitted",
        example="2024-01-15"
    )
    deadline: Optional[date] = Field(
        None,
        description="Application deadline",
        example="2024-02-15"
    )
    priority: Priority = Field(
        default=Priority.MEDIUM,
        description="Priority level of this application",
        example=Priority.HIGH
    )
    notes: Optional[str] = Field(
        None,
        max_length=2000,
        description="Personal notes about the application",
        example="Applied through referral from John. Great company culture."
    )
    referral_name: Optional[str] = Field(
        None,
        max_length=100,
        description="Name of the person who referred you",
        example="John Smith"
    )
    contact_email: Optional[EmailStr] = Field(
        None,
        description="Contact email for the application",
        example="recruiter@google.com"
    )
    contact_person: Optional[str] = Field(
        None,
        max_length=100,
        description="Name of the contact person",
        example="Jane Recruiter"
    )

    @validator('company_name', 'job_title')
    def validate_required_fields(cls, v):
        if not v or not v.strip():
            raise ValueError('Field cannot be empty or just whitespace')
        return v.strip()

    @validator('currency')
    def validate_currency(cls, v):
        if not re.match(r'^[A-Z]{3}$', v.upper()):
            raise ValueError('Currency must be a 3-letter code (e.g., USD, EUR)')
        return v.upper()

    @validator('salary_max')
    def validate_salary_range(cls, v, values):
        salary_min = values.get('salary_min')
        if salary_min is not None and v is not None and v <= salary_min:
            raise ValueError('Maximum salary must be greater than minimum salary')
        return v

    @validator('deadline')
    def validate_deadline(cls, v, values):
        application_date = values.get('application_date')
        if application_date and v and v < application_date:
            raise ValueError('Deadline cannot be before application date')
        return v

class ApplicationCreate(ApplicationBase):
    """Model for creating new job applications (POST requests)."""
    status: ApplicationStatus = Field(
        default=ApplicationStatus.APPLIED,
        description="Current status of the application",
        example=ApplicationStatus.APPLIED
    )
    
    class Config:
        schema_extra = {
            "example": {
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
                "notes": "Applied through referral. Exciting AI/ML role.",
                "contact_email": "recruiter@google.com",
                "status": "applied"
            }
        }

class ApplicationUpdate(BaseModel):
    """Model for updating job applications (PUT requests) with optional fields."""
    company_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=200,
        description="Name of the company"
    )
    job_title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=200,
        description="Title of the job position"
    )
    job_url: Optional[HttpUrl] = Field(
        None,
        description="URL to the job posting"
    )
    job_description: Optional[str] = Field(
        None,
        max_length=5000,
        description="Description of the job role and requirements"
    )
    location: Optional[str] = Field(
        None,
        max_length=200,
        description="Job location"
    )
    salary_min: Optional[int] = Field(
        None,
        ge=0,
        description="Minimum salary range"
    )
    salary_max: Optional[int] = Field(
        None,
        ge=0,
        description="Maximum salary range"
    )
    currency: Optional[str] = Field(
        None,
        max_length=3,
        description="Currency code for salary"
    )
    job_type: Optional[JobType] = Field(
        None,
        description="Type of employment"
    )
    remote_type: Optional[RemoteType] = Field(
        None,
        description="Remote work arrangement"
    )
    application_date: Optional[date] = Field(
        None,
        description="Date when the application was submitted"
    )
    deadline: Optional[date] = Field(
        None,
        description="Application deadline"
    )
    status: Optional[ApplicationStatus] = Field(
        None,
        description="Current status of the application"
    )
    priority: Optional[Priority] = Field(
        None,
        description="Priority level of this application"
    )
    notes: Optional[str] = Field(
        None,
        max_length=2000,
        description="Personal notes about the application"
    )
    referral_name: Optional[str] = Field(
        None,
        max_length=100,
        description="Name of the person who referred you"
    )
    contact_email: Optional[EmailStr] = Field(
        None,
        description="Contact email for the application"
    )
    contact_person: Optional[str] = Field(
        None,
        max_length=100,
        description="Name of the contact person"
    )

    @validator('company_name', 'job_title')
    def validate_required_fields(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('Field cannot be empty or just whitespace')
        return v.strip() if v else v

    @validator('currency')
    def validate_currency(cls, v):
        if v is not None and not re.match(r'^[A-Z]{3}$', v.upper()):
            raise ValueError('Currency must be a 3-letter code (e.g., USD, EUR)')
        return v.upper() if v else v

    class Config:
        schema_extra = {
            "example": {
                "status": "phone_screen",
                "notes": "Completed phone screen. Technical interview scheduled for next week.",
                "priority": "high"
            }
        }

class ApplicationResponse(ApplicationBase, TimestampMixin):
    """Model for job application API responses with ID and timestamps."""
    id: int = Field(
        ...,
        description="Unique identifier for the application",
        example=123
    )
    status: ApplicationStatus = Field(
        ...,
        description="Current status of the application",
        example=ApplicationStatus.APPLIED
    )
    days_since_applied: Optional[int] = Field(
        None,
        description="Number of days since the application was submitted",
        example=15
    )
    last_interaction_date: Optional[date] = Field(
        None,
        description="Date of the last interaction with the company",
        example="2024-01-20"
    )
    
    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
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
                "status": "phone_screen",
                "priority": "high",
                "notes": "Phone screen completed successfully",
                "contact_email": "recruiter@google.com",
                "days_since_applied": 15,
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-30T14:20:00Z"
            }
        }

# Analytics and statistics models
class ApplicationStats(BaseModel):
    """Model for application analytics and statistics data."""
    total_applications: int = Field(
        ...,
        ge=0,
        description="Total number of applications",
        example=50
    )
    applications_by_status: Dict[str, int] = Field(
        ...,
        description="Count of applications grouped by status",
        example={
            "applied": 20,
            "reviewing": 10,
            "phone_screen": 8,
            "technical_interview": 5,
            "offer": 2,
            "rejected": 5
        }
    )
    applications_by_month: Dict[str, int] = Field(
        ...,
        description="Count of applications by month",
        example={
            "2024-01": 15,
            "2024-02": 20,
            "2024-03": 15
        }
    )
    success_rate: float = Field(
        ...,
        ge=0,
        le=100,
        description="Success rate percentage (offers/total applications * 100)",
        example=4.0
    )
    average_response_time: Optional[float] = Field(
        None,
        ge=0,
        description="Average response time in days",
        example=7.5
    )
    top_companies: List[Dict[str, Union[str, int]]] = Field(
        default=[],
        description="Most applied to companies with counts",
        example=[
            {"company_name": "Google Inc.", "count": 3},
            {"company_name": "Microsoft", "count": 2}
        ]
    )
    salary_range: Dict[str, Optional[int]] = Field(
        default={"min": None, "max": None, "avg": None},
        description="Salary statistics",
        example={"min": 80000, "max": 200000, "avg": 140000}
    )
    active_applications: int = Field(
        ...,
        ge=0,
        description="Number of applications still in progress",
        example=25
    )
    
    class Config:
        schema_extra = {
            "example": {
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
                "active_applications": 25
            }
        }

class ApplicationHistory(BaseModel):
    """Model for tracking changes and interactions over time."""
    id: int = Field(
        ...,
        description="Unique identifier for the history record",
        example=1
    )
    application_id: int = Field(
        ...,
        description="ID of the related application",
        example=123
    )
    interaction_type: InteractionType = Field(
        ...,
        description="Type of interaction or change",
        example=InteractionType.INTERVIEW
    )
    title: str = Field(
        ...,
        max_length=200,
        description="Title or summary of the interaction",
        example="Technical Interview - Round 1"
    )
    description: Optional[str] = Field(
        None,
        max_length=2000,
        description="Detailed description of the interaction",
        example="Completed 1-hour technical interview focusing on algorithms and system design"
    )
    interaction_date: date = Field(
        ...,
        description="Date when the interaction occurred",
        example="2024-01-25"
    )
    old_status: Optional[ApplicationStatus] = Field(
        None,
        description="Previous application status (if status changed)",
        example=ApplicationStatus.PHONE_SCREEN
    )
    new_status: Optional[ApplicationStatus] = Field(
        None,
        description="New application status (if status changed)",
        example=ApplicationStatus.TECHNICAL_INTERVIEW
    )
    outcome: Optional[str] = Field(
        None,
        max_length=500,
        description="Outcome or result of the interaction",
        example="Positive feedback. Moving to final round."
    )
    follow_up_needed: bool = Field(
        default=False,
        description="Whether follow-up action is needed",
        example=True
    )
    follow_up_date: Optional[date] = Field(
        None,
        description="Date for follow-up action",
        example="2024-02-01"
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when the record was created",
        example="2024-01-25T15:30:00Z"
    )
    
    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "application_id": 123,
                "interaction_type": "interview",
                "title": "Technical Interview - Round 1",
                "description": "1-hour technical interview with the engineering team",
                "interaction_date": "2024-01-25",
                "old_status": "phone_screen",
                "new_status": "technical_interview",
                "outcome": "Positive feedback, moving to next round",
                "follow_up_needed": true,
                "follow_up_date": "2024-02-01",
                "created_at": "2024-01-25T15:30:00Z"
            }
        }

# Pagination and response models
class PaginationParams(BaseModel):
    """Model for pagination parameters."""
    page: int = Field(
        1,
        ge=1,
        description="Page number (1-indexed)",
        example=1
    )
    limit: int = Field(
        20,
        ge=1,
        le=100,
        description="Number of items per page (max 100)",
        example=20
    )
    sort_by: Optional[str] = Field(
        None,
        description="Field to sort by",
        example="created_at"
    )
    sort_order: Optional[str] = Field(
        "desc",
        regex="^(asc|desc)$",
        description="Sort order: 'asc' or 'desc'",
        example="desc"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "page": 1,
                "limit": 20,
                "sort_by": "created_at",
                "sort_order": "desc"
            }
        }

class PaginatedResponse(BaseModel):
    """Generic paginated response model."""
    items: List[Any] = Field(
        ...,
        description="List of items for the current page"
    )
    total: int = Field(
        ...,
        ge=0,
        description="Total number of items",
        example=150
    )
    page: int = Field(
        ...,
        ge=1,
        description="Current page number",
        example=1
    )
    limit: int = Field(
        ...,
        ge=1,
        description="Number of items per page",
        example=20
    )
    pages: int = Field(
        ...,
        ge=0,
        description="Total number of pages",
        example=8
    )
    has_next: bool = Field(
        ...,
        description="Whether there is a next page",
        example=True
    )
    has_previous: bool = Field(
        ...,
        description="Whether there is a previous page",
        example=False
    )
    
    @validator('pages', pre=True, always=True)
    def calculate_pages(cls, v, values):
        total = values.get('total', 0)
        limit = values.get('limit', 20)
        return (total + limit - 1) // limit if total > 0 else 0
    
    @validator('has_next', pre=True, always=True)
    def calculate_has_next(cls, v, values):
        page = values.get('page', 1)
        pages = values.get('pages', 0)
        return page < pages
    
    @validator('has_previous', pre=True, always=True)
    def calculate_has_previous(cls, v, values):
        page = values.get('page', 1)
        return page > 1

    class Config:
        schema_extra = {
            "example": {
                "items": [],
                "total": 150,
                "page": 1,
                "limit": 20,
                "pages": 8,
                "has_next": True,
                "has_previous": False
            }
        }

# Generic API response models
class APIResponse(BaseModel):
    """Generic API response model."""
    success: bool = Field(
        True,
        description="Whether the operation was successful",
        example=True
    )
    message: str = Field(
        "Operation completed successfully",
        description="Response message",
        example="Application created successfully"
    )
    data: Optional[Union[Dict[str, Any], List[Any], Any]] = Field(
        None,
        description="Response data"
    )
    errors: Optional[List[str]] = Field(
        None,
        description="List of error messages"
    )
    timestamp: Optional[datetime] = Field(
        None,
        description="Response timestamp",
        example="2024-01-15T10:30:00Z"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Operation completed successfully",
                "data": {"id": 123},
                "errors": None,
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }

class ErrorResponse(BaseModel):
    """Error response model."""
    success: bool = Field(
        False,
        description="Always false for error responses"
    )
    message: str = Field(
        ...,
        description="Error message",
        example="Validation error"
    )
    errors: List[str] = Field(
        ...,
        description="List of specific error messages",
        example=["Company name is required", "Invalid email format"]
    )
    error_code: Optional[str] = Field(
        None,
        description="Specific error code for programmatic handling",
        example="VALIDATION_ERROR"
    )
    timestamp: datetime = Field(
        ...,
        description="Error timestamp",
        example="2024-01-15T10:30:00Z"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "success": False,
                "message": "Validation error",
                "errors": ["Company name is required"],
                "error_code": "VALIDATION_ERROR",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }

# Filtering and search models
class ApplicationFilter(BaseModel):
    """Model for filtering job applications."""
    status: Optional[List[ApplicationStatus]] = Field(
        None,
        description="Filter by application statuses",
        example=[ApplicationStatus.APPLIED, ApplicationStatus.REVIEWING]
    )
    company_name: Optional[str] = Field(
        None,
        max_length=200,
        description="Filter by company name (partial match)",
        example="Google"
    )
    job_title: Optional[str] = Field(
        None,
        max_length=200,
        description="Filter by job title (partial match)",
        example="Software Engineer"
    )
    location: Optional[str] = Field(
        None,
        max_length=200,
        description="Filter by location (partial match)",
        example="San Francisco"
    )
    job_type: Optional[List[JobType]] = Field(
        None,
        description="Filter by job types",
        example=[JobType.FULL_TIME, JobType.CONTRACT]
    )
    remote_type: Optional[List[RemoteType]] = Field(
        None,
        description="Filter by remote work arrangements",
        example=[RemoteType.REMOTE, RemoteType.HYBRID]
    )
    priority: Optional[List[Priority]] = Field(
        None,
        description="Filter by priority levels",
        example=[Priority.HIGH, Priority.URGENT]
    )
    salary_min: Optional[int] = Field(
        None,
        ge=0,
        description="Minimum salary filter",
        example=100000
    )
    salary_max: Optional[int] = Field(
        None,
        ge=0,
        description="Maximum salary filter",
        example=200000
    )
    application_date_from: Optional[date] = Field(
        None,
        description="Filter applications from this date onwards",
        example="2024-01-01"
    )
    application_date_to: Optional[date] = Field(
        None,
        description="Filter applications up to this date",
        example="2024-03-31"
    )
    deadline_from: Optional[date] = Field(
        None,
        description="Filter by deadline from this date onwards",
        example="2024-02-01"
    )
    deadline_to: Optional[date] = Field(
        None,
        description="Filter by deadline up to this date",
        example="2024-04-30"
    )
    has_referral: Optional[bool] = Field(
        None,
        description="Filter applications with/without referrals",
        example=True
    )
    search: Optional[str] = Field(
        None,
        max_length=200,
        description="Global search across company, title, notes, and description",
        example="machine learning python"
    )
    
    @validator('salary_max')
    def validate_salary_range(cls, v, values):
        salary_min = values.get('salary_min')
        if salary_min is not None and v is not None and v <= salary_min:
            raise ValueError('Maximum salary must be greater than minimum salary')
        return v
    
    @validator('application_date_to')
    def validate_application_date_range(cls, v, values):
        date_from = values.get('application_date_from')
        if date_from and v and v < date_from:
            raise ValueError('Application date "to" must be after "from" date')
        return v
    
    @validator('deadline_to')
    def validate_deadline_range(cls, v, values):
        deadline_from = values.get('deadline_from')
        if deadline_from and v and v < deadline_from:
            raise ValueError('Deadline "to" must be after "from" date')
        return v

    class Config:
        schema_extra = {
            "example": {
                "status": ["applied", "reviewing"],
                "job_type": ["full_time"],
                "remote_type": ["remote", "hybrid"],
                "priority": ["high"],
                "salary_min": 100000,
                "application_date_from": "2024-01-01",
                "search": "software engineer python"
            }
        }

# Bulk operation models
class BulkApplicationCreate(BaseModel):
    """Model for creating multiple applications in bulk."""
    applications: List[ApplicationCreate] = Field(
        ...,
        min_items=1,
        max_items=50,
        description="List of applications to create (max 50)"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "applications": [
                    {
                        "company_name": "Google Inc.",
                        "job_title": "Senior Software Engineer",
                        "location": "Mountain View, CA",
                        "status": "applied"
                    },
                    {
                        "company_name": "Microsoft",
                        "job_title": "Software Engineer II",
                        "location": "Seattle, WA",
                        "status": "applied"
                    }
                ]
            }
        }

class BulkOperationResponse(BaseModel):
    """Response model for bulk operations."""
    total_processed: int = Field(
        ...,
        ge=0,
        description="Total number of items processed",
        example=10
    )
    successful: int = Field(
        ...,
        ge=0,
        description="Number of successful operations",
        example=8
    )
    failed: int = Field(
        ...,
        ge=0,
        description="Number of failed operations",
        example=2
    )
    created_ids: List[int] = Field(
        default=[],
        description="IDs of successfully created items",
        example=[123, 124, 125]
    )
    errors: List[Dict[str, Union[str, int]]] = Field(
        default=[],
        description="Detailed error information for failed operations",
        example=[
            {"index": 3, "error": "Company name is required"},
            {"index": 7, "error": "Invalid email format"}
        ]
    )
    
    class Config:
        schema_extra = {
            "example": {
                "total_processed": 10,
                "successful": 8,
                "failed": 2,
                "created_ids": [123, 124, 125, 126, 127, 128, 129, 130],
                "errors": [
                    {"index": 3, "error": "Company name is required"},
                    {"index": 7, "error": "Invalid email format"}
                ]
            }
        }

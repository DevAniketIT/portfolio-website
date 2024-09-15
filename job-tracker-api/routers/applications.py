"""
Job application REST API router with CRUD operations.

This module provides comprehensive REST endpoints for managing job applications,
including pagination, filtering, and proper error handling.
"""

from fastapi import APIRouter, HTTPException, Query, Depends, status
from fastapi.responses import JSONResponse
from typing import List, Optional, Union
from datetime import datetime, date
import logging
from contextlib import contextmanager
import math

from ..models import (
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationResponse,
    ApplicationStatus,
    JobType,
    RemoteType,
    Priority,
    PaginatedResponse,
    APIResponse,
    ErrorResponse,
    ApplicationFilter
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router instance
router = APIRouter(
    prefix="/applications",
    tags=["applications"],
    responses={
        404: {"model": ErrorResponse, "description": "Application not found"},
        422: {"model": ErrorResponse, "description": "Validation error"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)

# In-memory storage for demonstration (replace with actual database)
applications_db: List[dict] = []
next_id: int = 1

def get_current_timestamp() -> datetime:
    """Get current UTC timestamp."""
    return datetime.utcnow()

def create_error_response(message: str, errors: List[str] = None, error_code: str = None) -> dict:
    """Create standardized error response."""
    return {
        "success": False,
        "message": message,
        "errors": errors or [message],
        "error_code": error_code,
        "timestamp": get_current_timestamp()
    }

def create_success_response(message: str, data: any = None) -> dict:
    """Create standardized success response."""
    return {
        "success": True,
        "message": message,
        "data": data,
        "timestamp": get_current_timestamp()
    }

def calculate_days_since_applied(application_date: Optional[date]) -> Optional[int]:
    """Calculate days since application was submitted."""
    if not application_date:
        return None
    delta = date.today() - application_date
    return delta.days

def find_application_by_id(app_id: int) -> Optional[dict]:
    """Find application by ID."""
    return next((app for app in applications_db if app["id"] == app_id), None)

def apply_filters(applications: List[dict], filters: dict) -> List[dict]:
    """Apply filters to applications list."""
    filtered = applications.copy()
    
    # Status filter
    if filters.get("status"):
        status_values = filters["status"] if isinstance(filters["status"], list) else [filters["status"]]
        filtered = [app for app in filtered if app.get("status") in status_values]
    
    # Company name filter (partial match, case insensitive)
    if filters.get("company_name"):
        company_filter = filters["company_name"].lower()
        filtered = [app for app in filtered if company_filter in app.get("company_name", "").lower()]
    
    # Date range filters
    if filters.get("date_from"):
        date_from = filters["date_from"]
        if isinstance(date_from, str):
            date_from = datetime.strptime(date_from, "%Y-%m-%d").date()
        filtered = [app for app in filtered if app.get("application_date") and app["application_date"] >= date_from]
    
    if filters.get("date_to"):
        date_to = filters["date_to"]
        if isinstance(date_to, str):
            date_to = datetime.strptime(date_to, "%Y-%m-%d").date()
        filtered = [app for app in filtered if app.get("application_date") and app["application_date"] <= date_to]
    
    # Job type filter
    if filters.get("job_type"):
        job_types = filters["job_type"] if isinstance(filters["job_type"], list) else [filters["job_type"]]
        filtered = [app for app in filtered if app.get("job_type") in job_types]
    
    # Remote type filter
    if filters.get("remote_type"):
        remote_types = filters["remote_type"] if isinstance(filters["remote_type"], list) else [filters["remote_type"]]
        filtered = [app for app in filtered if app.get("remote_type") in remote_types]
    
    # Priority filter
    if filters.get("priority"):
        priorities = filters["priority"] if isinstance(filters["priority"], list) else [filters["priority"]]
        filtered = [app for app in filtered if app.get("priority") in priorities]
    
    # Search filter (across multiple fields)
    if filters.get("search"):
        search_term = filters["search"].lower()
        filtered = [
            app for app in filtered
            if search_term in app.get("company_name", "").lower() or
               search_term in app.get("job_title", "").lower() or
               search_term in app.get("notes", "").lower() or
               search_term in app.get("job_description", "").lower()
        ]
    
    return filtered

def paginate_results(items: List[dict], page: int, limit: int) -> dict:
    """Paginate results and return pagination metadata."""
    total = len(items)
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    
    paginated_items = items[start_idx:end_idx]
    total_pages = math.ceil(total / limit) if total > 0 else 0
    
    return {
        "items": paginated_items,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1
    }

@router.get(
    "/",
    response_model=PaginatedResponse,
    summary="List all job applications",
    description="""Retrieve a paginated list of job applications with comprehensive filtering and sorting options.
    
    **Features:**
    - **Pagination**: Control page size and navigation
    - **Filtering**: Filter by status, company, dates, job type, remote type, priority
    - **Search**: Full-text search across company name, job title, notes, and description
    - **Sorting**: Sort by any field in ascending or descending order
    - **Calculated Fields**: Includes days since applied and other derived fields
    
    **Query Parameters:**
    - Use multiple status values: `?status=applied&status=reviewing`
    - Date ranges: `?date_from=2024-01-01&date_to=2024-03-31`
    - Text search: `?search=python engineer` (searches across multiple fields)
    - Pagination: `?page=1&limit=20`
    - Sorting: `?sort_by=created_at&sort_order=desc`
    
    **Examples:**
    - Get recent applications: `GET /api/applications/?sort_by=application_date&sort_order=desc&limit=10`
    - Search for Python roles: `GET /api/applications/?search=python&job_type=full_time`
    - Filter by status: `GET /api/applications/?status=applied&status=reviewing`
    """,
    responses={
        200: {
            "description": "Successfully retrieved paginated applications",
            "content": {
                "application/json": {
                    "example": {
                        "items": [
                            {
                                "id": 123,
                                "company_name": "Google Inc.",
                                "job_title": "Senior Software Engineer",
                                "status": "applied",
                                "application_date": "2024-01-15",
                                "days_since_applied": 15,
                                "priority": "high",
                                "created_at": "2024-01-15T10:30:00Z"
                            }
                        ],
                        "total": 150,
                        "page": 1,
                        "limit": 20,
                        "pages": 8,
                        "has_next": True,
                        "has_previous": False
                    }
                }
            }
        }
    }
)
async def list_applications(
    status: Optional[List[ApplicationStatus]] = Query(None, description="Filter by application status"),
    company_name: Optional[str] = Query(None, description="Filter by company name (partial match)"),
    date_from: Optional[date] = Query(None, description="Filter applications from this date"),
    date_to: Optional[date] = Query(None, description="Filter applications up to this date"),
    job_type: Optional[List[JobType]] = Query(None, description="Filter by job type"),
    remote_type: Optional[List[RemoteType]] = Query(None, description="Filter by remote work type"),
    priority: Optional[List[Priority]] = Query(None, description="Filter by priority level"),
    search: Optional[str] = Query(None, description="Search across company name, job title, and notes"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(20, ge=1, le=100, description="Number of items per page (max 100)"),
    sort_by: Optional[str] = Query("created_at", description="Field to sort by"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order")
):
    """
    Get a paginated list of job applications with optional filtering.
    
    Supports filtering by:
    - Application status
    - Company name (partial match)
    - Date range
    - Job type and remote work type
    - Priority level
    - Full-text search
    
    Returns paginated results with metadata.
    """
    try:
        # Build filters dictionary
        filters = {}
        if status:
            filters["status"] = [s.value for s in status]
        if company_name:
            filters["company_name"] = company_name
        if date_from:
            filters["date_from"] = date_from
        if date_to:
            filters["date_to"] = date_to
        if job_type:
            filters["job_type"] = [jt.value for jt in job_type]
        if remote_type:
            filters["remote_type"] = [rt.value for rt in remote_type]
        if priority:
            filters["priority"] = [p.value for p in priority]
        if search:
            filters["search"] = search
        
        # Apply filters
        filtered_applications = apply_filters(applications_db, filters)
        
        # Apply sorting
        reverse_order = sort_order == "desc"
        if sort_by and sort_by in ["created_at", "updated_at", "application_date", "company_name", "job_title"]:
            filtered_applications.sort(
                key=lambda x: x.get(sort_by, ""),
                reverse=reverse_order
            )
        
        # Add calculated fields
        for app in filtered_applications:
            app["days_since_applied"] = calculate_days_since_applied(app.get("application_date"))
        
        # Paginate results
        paginated = paginate_results(filtered_applications, page, limit)
        
        logger.info(f"Retrieved {len(paginated['items'])} applications (page {page}/{paginated['pages']})")
        return paginated
        
    except Exception as e:
        logger.error(f"Error listing applications: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response("Failed to retrieve applications", [str(e)], "RETRIEVAL_ERROR")
        )

@router.post(
    "/",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new job application",
    description="""Create a new job application with comprehensive validation.
    
    **Features:**
    - **Automatic ID Generation**: System generates unique ID for each application
    - **Timestamp Management**: Automatically sets created_at and updated_at timestamps
    - **Data Validation**: Validates all fields using Pydantic models
    - **Calculated Fields**: Automatically computes days since applied
    
    **Required Fields:**
    - `company_name`: Name of the company (1-200 characters)
    - `job_title`: Title of the position (1-200 characters)
    
    **Optional Fields:**
    - All other fields are optional with sensible defaults
    - `status` defaults to "applied"
    - `priority` defaults to "medium"
    - `currency` defaults to "USD"
    
    **Validation Rules:**
    - Company name and job title cannot be empty or whitespace
    - Currency must be 3-letter code (e.g., USD, EUR)
    - Salary max must be greater than salary min
    - Deadline cannot be before application date
    - Email must be valid format if provided
    """,
    responses={
        201: {
            "description": "Application successfully created",
            "content": {
                "application/json": {
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
                        "status": "applied",
                        "priority": "high",
                        "notes": "Applied through referral",
                        "contact_email": "recruiter@google.com",
                        "days_since_applied": 0,
                        "created_at": "2024-01-15T10:30:00Z",
                        "updated_at": "2024-01-15T10:30:00Z"
                    }
                }
            }
        },
        422: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "Validation error",
                        "errors": [
                            "Company name is required",
                            "Invalid email format"
                        ],
                        "error_code": "VALIDATION_ERROR",
                        "timestamp": "2024-01-15T10:30:00Z"
                    }
                }
            }
        }
    }
)
async def create_application(application: ApplicationCreate):
    """
    Create a new job application.
    
    Validates input data using Pydantic models and returns the created application
    with a generated ID and timestamps.
    """
    global next_id
    
    try:
        # Create new application dictionary
        now = get_current_timestamp()
        new_app = application.dict()
        new_app.update({
            "id": next_id,
            "created_at": now,
            "updated_at": now
        })
        
        # Add calculated fields
        new_app["days_since_applied"] = calculate_days_since_applied(new_app.get("application_date"))
        
        # Add to database
        applications_db.append(new_app)
        next_id += 1
        
        logger.info(f"Created new application with ID {new_app['id']} for {new_app['company_name']}")
        
        return ApplicationResponse(**new_app)
        
    except ValueError as e:
        logger.error(f"Validation error creating application: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=create_error_response("Validation error", [str(e)], "VALIDATION_ERROR")
        )
    except Exception as e:
        logger.error(f"Error creating application: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response("Failed to create application", [str(e)], "CREATION_ERROR")
        )

@router.get(
    "/{application_id}",
    response_model=ApplicationResponse,
    summary="Get a specific job application",
    description="Retrieve a specific job application by its ID with all details."
)
async def get_application(application_id: int):
    """
    Get a specific job application by ID.
    
    Returns the complete application data including calculated fields.
    """
    try:
        application = find_application_by_id(application_id)
        
        if not application:
            logger.warning(f"Application with ID {application_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=create_error_response(
                    f"Application with ID {application_id} not found",
                    [f"No application found with ID {application_id}"],
                    "NOT_FOUND"
                )
            )
        
        # Add calculated fields
        app_copy = application.copy()
        app_copy["days_since_applied"] = calculate_days_since_applied(app_copy.get("application_date"))
        
        logger.info(f"Retrieved application {application_id}")
        return ApplicationResponse(**app_copy)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving application {application_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response("Failed to retrieve application", [str(e)], "RETRIEVAL_ERROR")
        )

@router.put(
    "/{application_id}",
    response_model=ApplicationResponse,
    summary="Update a job application",
    description="Update a job application with support for partial updates. Only provided fields will be updated."
)
async def update_application(application_id: int, application_update: ApplicationUpdate):
    """
    Update a job application with partial update support.
    
    Only the fields provided in the request will be updated.
    Returns the updated application data.
    """
    try:
        application = find_application_by_id(application_id)
        
        if not application:
            logger.warning(f"Application with ID {application_id} not found for update")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=create_error_response(
                    f"Application with ID {application_id} not found",
                    [f"No application found with ID {application_id}"],
                    "NOT_FOUND"
                )
            )
        
        # Get only non-None values for partial update
        update_data = application_update.dict(exclude_unset=True)
        
        if not update_data:
            logger.warning(f"No update data provided for application {application_id}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=create_error_response("No update data provided", ["At least one field must be provided for update"], "NO_UPDATE_DATA")
            )
        
        # Update fields
        for field, value in update_data.items():
            application[field] = value
        
        # Update timestamp
        application["updated_at"] = get_current_timestamp()
        
        # Add calculated fields
        application["days_since_applied"] = calculate_days_since_applied(application.get("application_date"))
        
        logger.info(f"Updated application {application_id} with fields: {list(update_data.keys())}")
        
        return ApplicationResponse(**application)
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error updating application {application_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=create_error_response("Validation error", [str(e)], "VALIDATION_ERROR")
        )
    except Exception as e:
        logger.error(f"Error updating application {application_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response("Failed to update application", [str(e)], "UPDATE_ERROR")
        )

@router.delete(
    "/{application_id}",
    response_model=APIResponse,
    summary="Delete a job application",
    description="Delete a job application by ID and return confirmation."
)
async def delete_application(application_id: int):
    """
    Delete a job application by ID.
    
    Returns a success confirmation with the deleted application ID.
    """
    try:
        application = find_application_by_id(application_id)
        
        if not application:
            logger.warning(f"Application with ID {application_id} not found for deletion")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=create_error_response(
                    f"Application with ID {application_id} not found",
                    [f"No application found with ID {application_id}"],
                    "NOT_FOUND"
                )
            )
        
        # Remove from database
        applications_db.remove(application)
        
        logger.info(f"Deleted application {application_id}")
        
        return APIResponse(
            success=True,
            message=f"Application {application_id} deleted successfully",
            data={"deleted_id": application_id},
            timestamp=get_current_timestamp()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting application {application_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response("Failed to delete application", [str(e)], "DELETION_ERROR")
        )

# Additional utility endpoints

@router.get(
    "/status/{status_name}",
    response_model=PaginatedResponse,
    summary="Get applications by status",
    description="Retrieve applications filtered by a specific status with pagination."
)
async def get_applications_by_status(
    status_name: ApplicationStatus,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """Get applications filtered by specific status."""
    return await list_applications(
        status=[status_name],
        page=page,
        limit=limit
    )

@router.get(
    "/company/{company_name}",
    response_model=PaginatedResponse,
    summary="Get applications by company",
    description="Retrieve applications filtered by company name with pagination."
)
async def get_applications_by_company(
    company_name: str,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """Get applications filtered by company name."""
    return await list_applications(
        company_name=company_name,
        page=page,
        limit=limit
    )

@router.patch(
    "/{application_id}/status",
    response_model=ApplicationResponse,
    summary="Update application status",
    description="Update only the status of a specific application."
)
async def update_application_status(application_id: int, status: ApplicationStatus):
    """Update only the status of an application."""
    update_data = ApplicationUpdate(status=status)
    return await update_application(application_id, update_data)

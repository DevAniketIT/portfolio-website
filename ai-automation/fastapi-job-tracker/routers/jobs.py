from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from database import get_db
from schemas import (
    JobApplicationCreate, JobApplication, JobApplicationUpdate, 
    JobApplicationList, APIResponse, User
)
from models import ApplicationStatus
from crud import (
    create_job_application, get_job_application, get_job_applications,
    update_job_application, delete_job_application, count_job_applications,
    get_application_stats
)
from auth import get_current_active_user


router = APIRouter(
    prefix="/jobs",
    tags=["job applications"],
    dependencies=[Depends(get_current_active_user)]
)


@router.post("/", response_model=JobApplication, status_code=status.HTTP_201_CREATED)
async def create_application(
    application: JobApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new job application."""
    return create_job_application(db=db, application=application, user_id=current_user.id)


@router.get("/", response_model=JobApplicationList)
async def read_applications(
    status_filter: Optional[ApplicationStatus] = Query(None, alias="status"),
    company: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get job applications with optional filtering and pagination."""
    skip = (page - 1) * per_page
    
    applications = get_job_applications(
        db=db,
        user_id=current_user.id,
        status=status_filter,
        company=company,
        skip=skip,
        limit=per_page
    )
    
    total = count_job_applications(
        db=db,
        user_id=current_user.id,
        status=status_filter,
        company=company
    )
    
    return JobApplicationList(
        applications=applications,
        total=total,
        page=page,
        per_page=per_page
    )


@router.get("/{application_id}", response_model=JobApplication)
async def read_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific job application."""
    application = get_job_application(db=db, application_id=application_id, user_id=current_user.id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job application not found"
        )
    return application


@router.put("/{application_id}", response_model=JobApplication)
async def update_application(
    application_id: int,
    application_update: JobApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a job application."""
    application = update_job_application(
        db=db,
        application_id=application_id,
        application_update=application_update,
        user_id=current_user.id
    )
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job application not found"
        )
    return application


@router.delete("/{application_id}", response_model=APIResponse)
async def delete_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a job application."""
    success = delete_job_application(db=db, application_id=application_id, user_id=current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job application not found"
        )
    return APIResponse(
        success=True,
        message="Job application deleted successfully"
    )


@router.get("/stats/summary")
async def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get application statistics summary."""
    stats = get_application_stats(db=db, user_id=current_user.id)
    return APIResponse(
        success=True,
        message="Statistics retrieved successfully",
        data=stats
    )


@router.patch("/{application_id}/status", response_model=JobApplication)
async def update_application_status(
    application_id: int,
    new_status: ApplicationStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update only the status of a job application."""
    application_update = JobApplicationUpdate(status=new_status)
    application = update_job_application(
        db=db,
        application_id=application_id,
        application_update=application_update,
        user_id=current_user.id
    )
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job application not found"
        )
    return application

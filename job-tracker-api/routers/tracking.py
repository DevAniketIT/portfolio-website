"""
Specialized tracking and analytics router for job applications.

This module provides specialized endpoints for:
- Simplified external job tracking
- Detailed application history
- Analytics and dashboard data
"""

from fastapi import APIRouter, HTTPException, Query, Depends, status
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from collections import defaultdict, Counter
import logging
from pydantic import BaseModel, Field, HttpUrl

from ..models import (
    ApplicationCreate,
    ApplicationResponse,
    ApplicationStatus,
    ApplicationHistory,
    ApplicationStats,
    JobType,
    RemoteType,
    Priority,
    APIResponse,
    ErrorResponse
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router instance
router = APIRouter(
    prefix="/tracking",
    tags=["tracking"],
    responses={
        404: {"model": ErrorResponse, "description": "Resource not found"},
        422: {"model": ErrorResponse, "description": "Validation error"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)

# Import applications database from the applications router
# In a real implementation, this would be a proper database connection
from ..routers.applications import applications_db, get_current_timestamp
from ..routers import applications

# In-memory storage for application history
application_history_db: List[dict] = []
next_history_id: int = 1

# Specialized models for tracking endpoints
class QuickTrackRequest(BaseModel):
    """Simplified model for external job tracking with minimal required fields."""
    company: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Company name",
        example="Tech Corp Inc."
    )
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Job title",
        example="Senior Software Engineer"
    )
    url: Optional[HttpUrl] = Field(
        None,
        description="Job posting URL",
        example="https://techcorp.com/careers/senior-engineer"
    )
    notes: Optional[str] = Field(
        None,
        max_length=500,
        description="Optional notes",
        example="Found through LinkedIn, looks promising"
    )

    class Config:
        schema_extra = {
            "example": {
                "company": "Tech Corp Inc.",
                "title": "Senior Software Engineer",
                "url": "https://techcorp.com/careers/senior-engineer",
                "notes": "Applied through company website"
            }
        }

class TrackingResponse(BaseModel):
    """Response model for tracking operations."""
    tracking_id: int = Field(
        ...,
        description="Unique tracking ID for reference",
        example=12345
    )
    company: str = Field(
        ...,
        description="Company name",
        example="Tech Corp Inc."
    )
    title: str = Field(
        ...,
        description="Job title",
        example="Senior Software Engineer"
    )
    status: ApplicationStatus = Field(
        ...,
        description="Application status",
        example=ApplicationStatus.APPLIED
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when created",
        example="2024-08-24T10:30:00Z"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "tracking_id": 12345,
                "company": "Tech Corp Inc.",
                "title": "Senior Software Engineer",
                "status": "applied",
                "created_at": "2024-08-24T10:30:00Z"
            }
        }

class DetailedHistory(BaseModel):
    """Detailed application history with status changes and interactions."""
    application: ApplicationResponse = Field(
        ...,
        description="Complete application details"
    )
    status_changes: List[Dict[str, Any]] = Field(
        default=[],
        description="History of status changes with timestamps"
    )
    interactions: List[ApplicationHistory] = Field(
        default=[],
        description="All interactions and follow-ups"
    )
    interview_stages: List[Dict[str, Any]] = Field(
        default=[],
        description="Interview stages if available"
    )
    timeline: List[Dict[str, Any]] = Field(
        default=[],
        description="Complete timeline of all events"
    )

def create_error_response(message: str, errors: List[str] = None, error_code: str = None) -> dict:
    """Create standardized error response."""
    return {
        "success": False,
        "message": message,
        "errors": errors or [message],
        "error_code": error_code,
        "timestamp": get_current_timestamp()
    }

def create_success_response(message: str, data: Any = None) -> dict:
    """Create standardized success response."""
    return {
        "success": True,
        "message": message,
        "data": data,
        "timestamp": get_current_timestamp()
    }

def find_application_by_id(app_id: int) -> Optional[dict]:
    """Find application by ID."""
    return next((app for app in applications_db if app["id"] == app_id), None)

def add_history_entry(application_id: int, interaction_type: str, title: str, 
                     description: str = None, old_status: str = None, 
                     new_status: str = None, outcome: str = None) -> int:
    """Add a new history entry."""
    global next_history_id
    
    history_entry = {
        "id": next_history_id,
        "application_id": application_id,
        "interaction_type": interaction_type,
        "title": title,
        "description": description,
        "interaction_date": date.today(),
        "old_status": old_status,
        "new_status": new_status,
        "outcome": outcome,
        "follow_up_needed": False,
        "follow_up_date": None,
        "created_at": get_current_timestamp()
    }
    
    application_history_db.append(history_entry)
    next_history_id += 1
    return history_entry["id"]

def calculate_response_rate() -> float:
    """Calculate response rate based on applications that moved beyond 'applied' status."""
    if not applications_db:
        return 0.0
    
    total_apps = len(applications_db)
    responded_apps = len([app for app in applications_db 
                         if app.get("status") not in ["applied", "rejected"]])
    
    return (responded_apps / total_apps) * 100 if total_apps > 0 else 0.0

def calculate_average_response_time() -> Optional[float]:
    """Calculate average response time in days."""
    response_times = []
    
    for app in applications_db:
        app_date = app.get("application_date")
        status = app.get("status")
        
        if app_date and status not in ["applied"]:
            # For demo purposes, simulate response times
            # In real implementation, this would use actual status change dates
            if status in ["reviewing", "phone_screen"]:
                response_times.append(7)  # Average 7 days to first response
            elif status in ["technical_interview", "onsite_interview"]:
                response_times.append(14)  # Average 14 days to interview
            elif status in ["offer", "rejected"]:
                response_times.append(21)  # Average 21 days to final decision
    
    return sum(response_times) / len(response_times) if response_times else None

@router.post(
    "/track",
    response_model=TrackingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Quick application tracking",
    description="""Simplified endpoint for external job tracking with minimal required fields.
    
    **Perfect for:**
    - Browser extensions and bookmarklets
    - Mobile app quick entry
    - External integrations
    - Rapid application logging
    
    **Features:**
    - **Minimal Input**: Only company and job title required
    - **Auto-defaults**: Automatically populates sensible defaults
    - **Quick Response**: Returns tracking ID for future reference
    - **History Tracking**: Automatically creates initial history entry
    
    **Required Fields:**
    - `company`: Company name (1-200 characters)
    - `title`: Job title (1-200 characters)
    
    **Auto-populated Defaults:**
    - `status`: "applied"
    - `priority`: "medium"
    - `job_type`: "full_time"
    - `remote_type`: "on_site"
    - `application_date`: Today's date
    - `currency`: "USD"
    
    **Usage Examples:**
    ```javascript
    // Browser extension
    fetch('/api/tracking/track', {
      method: 'POST',
      body: JSON.stringify({
        company: 'Google Inc.',
        title: 'Software Engineer',
        url: window.location.href,
        notes: 'Applied via company website'
      })
    })
    ```
    """,
    responses={
        201: {
            "description": "Application successfully tracked",
            "content": {
                "application/json": {
                    "example": {
                        "tracking_id": 12345,
                        "company": "Tech Corp Inc.",
                        "title": "Senior Software Engineer",
                        "status": "applied",
                        "created_at": "2024-08-24T10:30:00Z"
                    }
                }
            }
        }
    }
)
async def track_application(track_request: QuickTrackRequest):
    """
    Simplified endpoint for external job tracking.
    
    Accepts minimal required fields (company, title, url) and auto-populates
    defaults for other fields. Returns tracking ID for reference.
    """
    # Use the next_id from the applications module
    current_next_id = applications.next_id
    
    try:
        # Create application with defaults
        now = get_current_timestamp()
        today = date.today()
        
        new_app = {
            "id": current_next_id,
            "company_name": track_request.company,
            "job_title": track_request.title,
            "job_url": str(track_request.url) if track_request.url else None,
            "job_description": None,
            "location": None,
            "salary_min": None,
            "salary_max": None,
            "currency": "USD",
            "job_type": JobType.FULL_TIME.value,
            "remote_type": RemoteType.ON_SITE.value,
            "application_date": today,
            "deadline": None,
            "status": ApplicationStatus.APPLIED.value,
            "priority": Priority.MEDIUM.value,
            "notes": track_request.notes or "Tracked via quick tracking endpoint",
            "referral_name": None,
            "contact_email": None,
            "contact_person": None,
            "created_at": now,
            "updated_at": now,
            "days_since_applied": 0,
            "last_interaction_date": today
        }
        
        # Add to database
        applications_db.append(new_app)
        
        # Add initial history entry
        add_history_entry(
            application_id=current_next_id,
            interaction_type="application",
            title="Application submitted",
            description=f"Applied to {track_request.company} for {track_request.title} position",
            new_status=ApplicationStatus.APPLIED.value
        )
        
        tracking_id = current_next_id
        applications.next_id += 1
        
        logger.info(f"Quick tracked application {tracking_id} for {track_request.company}")
        
        return TrackingResponse(
            tracking_id=tracking_id,
            company=track_request.company,
            title=track_request.title,
            status=ApplicationStatus.APPLIED,
            created_at=now
        )
        
    except ValueError as e:
        logger.error(f"Validation error in quick tracking: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=create_error_response("Validation error", [str(e)], "VALIDATION_ERROR")
        )
    except Exception as e:
        logger.error(f"Error in quick tracking: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response("Failed to track application", [str(e)], "TRACKING_ERROR")
        )

@router.get(
    "/application-history/{application_id}",
    response_model=DetailedHistory,
    summary="Get detailed application history",
    description="Get comprehensive history including status changes, interactions, and interview stages"
)
async def get_application_history(application_id: int):
    """
    Get detailed history for a specific application.
    
    Includes:
    - All status changes with timestamps
    - Follow-up history
    - Interview stages if available
    - Complete timeline
    """
    try:
        # Find the application
        application = find_application_by_id(application_id)
        
        if not application:
            logger.warning(f"Application {application_id} not found for history")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=create_error_response(
                    f"Application {application_id} not found",
                    [f"No application found with ID {application_id}"],
                    "NOT_FOUND"
                )
            )
        
        # Get application history
        app_history = [h for h in application_history_db if h["application_id"] == application_id]
        
        # Extract status changes
        status_changes = []
        for h in app_history:
            if h.get("old_status") and h.get("new_status"):
                status_changes.append({
                    "from_status": h["old_status"],
                    "to_status": h["new_status"],
                    "changed_at": h["created_at"],
                    "description": h.get("description")
                })
        
        # Extract interview stages
        interview_stages = []
        for h in app_history:
            if h.get("interaction_type") == "interview":
                interview_stages.append({
                    "stage": h["title"],
                    "date": h["interaction_date"],
                    "outcome": h.get("outcome"),
                    "description": h.get("description")
                })
        
        # Build complete timeline
        timeline = []
        for h in sorted(app_history, key=lambda x: x["created_at"]):
            timeline.append({
                "date": h["interaction_date"],
                "type": h["interaction_type"],
                "title": h["title"],
                "description": h.get("description"),
                "outcome": h.get("outcome")
            })
        
        # Add application created event to timeline
        timeline.insert(0, {
            "date": application["application_date"],
            "type": "application",
            "title": "Application created",
            "description": f"Applied to {application['company_name']} for {application['job_title']}",
            "outcome": None
        })
        
        # Create response
        app_copy = application.copy()
        app_copy["days_since_applied"] = (date.today() - app_copy.get("application_date", date.today())).days
        
        detailed_history = DetailedHistory(
            application=ApplicationResponse(**app_copy),
            status_changes=status_changes,
            interactions=[ApplicationHistory(**h) for h in app_history],
            interview_stages=interview_stages,
            timeline=timeline
        )
        
        logger.info(f"Retrieved detailed history for application {application_id}")
        return detailed_history
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving application history {application_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response("Failed to retrieve application history", [str(e)], "HISTORY_ERROR")
        )

@router.get(
    "/stats",
    response_model=ApplicationStats,
    summary="Analytics dashboard data",
    description="Comprehensive analytics data for dashboard visualization"
)
async def get_analytics_stats():
    """
    Get analytics dashboard data.
    
    Provides:
    - Total applications count
    - Status distribution (pie chart data)
    - Applications by month (line chart data)
    - Response rate calculations
    - Average time to response
    """
    try:
        if not applications_db:
            # Return empty stats if no applications
            return ApplicationStats(
                total_applications=0,
                applications_by_status={},
                applications_by_month={},
                success_rate=0.0,
                average_response_time=None,
                top_companies=[],
                salary_range={"min": None, "max": None, "avg": None},
                active_applications=0
            )
        
        # Total applications
        total_applications = len(applications_db)
        
        # Status distribution
        status_counter = Counter(app.get("status", "unknown") for app in applications_db)
        applications_by_status = dict(status_counter)
        
        # Applications by month
        applications_by_month = defaultdict(int)
        for app in applications_db:
            app_date = app.get("application_date")
            if app_date:
                if isinstance(app_date, str):
                    app_date = datetime.strptime(app_date, "%Y-%m-%d").date()
                month_key = app_date.strftime("%Y-%m")
                applications_by_month[month_key] += 1
        
        applications_by_month = dict(applications_by_month)
        
        # Success rate (offers / total applications * 100)
        offers = sum(1 for app in applications_db if app.get("status") in ["offer", "accepted"])
        success_rate = (offers / total_applications * 100) if total_applications > 0 else 0.0
        
        # Average response time
        avg_response_time = calculate_average_response_time()
        
        # Top companies
        company_counter = Counter(app.get("company_name", "Unknown") for app in applications_db)
        top_companies = [
            {"company_name": company, "count": count}
            for company, count in company_counter.most_common(5)
        ]
        
        # Salary range
        salaries = []
        for app in applications_db:
            if app.get("salary_min"):
                salaries.append(app["salary_min"])
            if app.get("salary_max"):
                salaries.append(app["salary_max"])
        
        salary_range = {
            "min": min(salaries) if salaries else None,
            "max": max(salaries) if salaries else None,
            "avg": int(sum(salaries) / len(salaries)) if salaries else None
        }
        
        # Active applications (not rejected, withdrawn, or accepted)
        active_statuses = ["applied", "reviewing", "phone_screen", "technical_interview", 
                          "onsite_interview", "final_round", "offer"]
        active_applications = sum(1 for app in applications_db 
                                if app.get("status") in active_statuses)
        
        stats = ApplicationStats(
            total_applications=total_applications,
            applications_by_status=applications_by_status,
            applications_by_month=applications_by_month,
            success_rate=round(success_rate, 1),
            average_response_time=avg_response_time,
            top_companies=top_companies,
            salary_range=salary_range,
            active_applications=active_applications
        )
        
        logger.info(f"Generated analytics stats: {total_applications} total applications")
        return stats
        
    except Exception as e:
        logger.error(f"Error generating analytics stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response("Failed to generate analytics", [str(e)], "ANALYTICS_ERROR")
        )

# Additional utility endpoints for tracking

@router.post(
    "/application-history/{application_id}/interaction",
    response_model=APIResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add interaction to application history",
    description="Add a new interaction or note to an application's history"
)
async def add_interaction(
    application_id: int,
    interaction_type: str = Query(..., description="Type of interaction"),
    title: str = Query(..., description="Interaction title"),
    description: Optional[str] = Query(None, description="Detailed description"),
    outcome: Optional[str] = Query(None, description="Outcome or result")
):
    """Add a new interaction to application history."""
    try:
        # Verify application exists
        application = find_application_by_id(application_id)
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=create_error_response(
                    f"Application {application_id} not found",
                    [f"No application found with ID {application_id}"],
                    "NOT_FOUND"
                )
            )
        
        # Add history entry
        history_id = add_history_entry(
            application_id=application_id,
            interaction_type=interaction_type,
            title=title,
            description=description,
            outcome=outcome
        )
        
        logger.info(f"Added interaction {history_id} to application {application_id}")
        
        return APIResponse(
            success=True,
            message=f"Interaction added to application {application_id}",
            data={"history_id": history_id, "application_id": application_id},
            timestamp=get_current_timestamp()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding interaction to application {application_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response("Failed to add interaction", [str(e)], "INTERACTION_ERROR")
        )

@router.get(
    "/recent-activity",
    summary="Get recent tracking activity",
    description="Get recent applications and interactions for dashboard overview"
)
async def get_recent_activity(
    days: int = Query(7, ge=1, le=30, description="Number of days to look back"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of items to return")
):
    """Get recent applications and activity for dashboard overview."""
    try:
        cutoff_date = date.today() - timedelta(days=days)
        
        # Recent applications
        recent_apps = []
        for app in applications_db:
            app_date = app.get("application_date")
            if app_date:
                if isinstance(app_date, str):
                    app_date = datetime.strptime(app_date, "%Y-%m-%d").date()
                if app_date >= cutoff_date:
                    recent_apps.append({
                        "id": app["id"],
                        "company_name": app["company_name"],
                        "job_title": app["job_title"],
                        "status": app["status"],
                        "application_date": app_date.isoformat(),
                        "type": "application"
                    })
        
        # Recent interactions
        recent_interactions = []
        for history in application_history_db:
            interaction_date = history.get("interaction_date")
            if interaction_date:
                if isinstance(interaction_date, str):
                    interaction_date = datetime.strptime(interaction_date, "%Y-%m-%d").date()
                if interaction_date >= cutoff_date:
                    app = find_application_by_id(history["application_id"])
                    if app:
                        recent_interactions.append({
                            "id": history["id"],
                            "application_id": history["application_id"],
                            "company_name": app["company_name"],
                            "title": history["title"],
                            "interaction_type": history["interaction_type"],
                            "interaction_date": interaction_date.isoformat(),
                            "type": "interaction"
                        })
        
        # Combine and sort by date
        all_activity = recent_apps + recent_interactions
        all_activity.sort(key=lambda x: x.get("application_date") or x.get("interaction_date"), reverse=True)
        
        # Apply limit
        limited_activity = all_activity[:limit]
        
        return {
            "recent_activity": limited_activity,
            "total_found": len(all_activity),
            "days_back": days,
            "generated_at": get_current_timestamp()
        }
        
    except Exception as e:
        logger.error(f"Error retrieving recent activity: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response("Failed to retrieve recent activity", [str(e)], "ACTIVITY_ERROR")
        )

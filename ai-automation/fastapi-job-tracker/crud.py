from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from typing import List, Optional
from models import User, JobApplication, ApplicationStatus
from schemas import UserCreate, UserUpdate, JobApplicationCreate, JobApplicationUpdate
from auth import get_password_hash


# User CRUD operations
def get_user(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email."""
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, user: UserCreate) -> User:
    """Create a new user."""
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
    """Update user information."""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return None
    
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user


# Job Application CRUD operations
def get_job_application(db: Session, application_id: int, user_id: int) -> Optional[JobApplication]:
    """Get job application by ID for a specific user."""
    return db.query(JobApplication).filter(
        and_(JobApplication.id == application_id, JobApplication.owner_id == user_id)
    ).first()


def get_job_applications(
    db: Session, 
    user_id: int, 
    status: Optional[ApplicationStatus] = None,
    company: Optional[str] = None,
    skip: int = 0, 
    limit: int = 20
) -> List[JobApplication]:
    """Get job applications for a user with optional filtering."""
    query = db.query(JobApplication).filter(JobApplication.owner_id == user_id)
    
    if status:
        query = query.filter(JobApplication.status == status)
    
    if company:
        query = query.filter(JobApplication.company.ilike(f"%{company}%"))
    
    return query.order_by(desc(JobApplication.created_at)).offset(skip).limit(limit).all()


def count_job_applications(
    db: Session, 
    user_id: int,
    status: Optional[ApplicationStatus] = None,
    company: Optional[str] = None
) -> int:
    """Count job applications for a user with optional filtering."""
    query = db.query(JobApplication).filter(JobApplication.owner_id == user_id)
    
    if status:
        query = query.filter(JobApplication.status == status)
    
    if company:
        query = query.filter(JobApplication.company.ilike(f"%{company}%"))
    
    return query.count()


def create_job_application(db: Session, application: JobApplicationCreate, user_id: int) -> JobApplication:
    """Create a new job application."""
    db_application = JobApplication(
        **application.dict(),
        owner_id=user_id
    )
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application


def update_job_application(
    db: Session, 
    application_id: int, 
    application_update: JobApplicationUpdate,
    user_id: int
) -> Optional[JobApplication]:
    """Update job application."""
    db_application = db.query(JobApplication).filter(
        and_(JobApplication.id == application_id, JobApplication.owner_id == user_id)
    ).first()
    
    if not db_application:
        return None
    
    update_data = application_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_application, field, value)
    
    db.commit()
    db.refresh(db_application)
    return db_application


def delete_job_application(db: Session, application_id: int, user_id: int) -> bool:
    """Delete job application."""
    db_application = db.query(JobApplication).filter(
        and_(JobApplication.id == application_id, JobApplication.owner_id == user_id)
    ).first()
    
    if not db_application:
        return False
    
    db.delete(db_application)
    db.commit()
    return True


def get_application_stats(db: Session, user_id: int) -> dict:
    """Get application statistics for a user."""
    total = db.query(JobApplication).filter(JobApplication.owner_id == user_id).count()
    
    stats = {}
    for status in ApplicationStatus:
        count = db.query(JobApplication).filter(
            and_(JobApplication.owner_id == user_id, JobApplication.status == status)
        ).count()
        stats[status.value] = count
    
    stats["total"] = total
    return stats

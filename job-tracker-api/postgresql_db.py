"""
PostgreSQL database implementation using SQLAlchemy ORM.

This module provides SQLAlchemy models and database operations for the job application
tracking system with PostgreSQL as the backend database.
"""

import os
import logging
from datetime import datetime, date
from typing import List, Optional, Dict, Any, Union
from contextlib import asynccontextmanager

# SQLAlchemy imports
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, DateTime, Boolean, 
    Text, ForeignKey, Date, Enum as SQLEnum, JSON
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.pool import StaticPool
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func

# Async SQLAlchemy support
try:
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
    ASYNC_SQLALCHEMY_AVAILABLE = True
except ImportError:
    ASYNC_SQLALCHEMY_AVAILABLE = False

# Import models for enum definitions
from models import ApplicationStatus, JobType, RemoteType, Priority, InteractionType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create base class
Base = declarative_base()


class Application(Base):
    """SQLAlchemy model for job applications."""
    __tablename__ = 'applications'

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_name = Column(String(200), nullable=False, index=True)
    job_title = Column(String(200), nullable=False, index=True)
    job_url = Column(Text, nullable=True)
    job_description = Column(Text, nullable=True)
    location = Column(String(200), nullable=True, index=True)
    
    # Salary information
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    currency = Column(String(3), nullable=False, default='USD')
    
    # Job details
    job_type = Column(SQLEnum(JobType), nullable=True, index=True)
    remote_type = Column(SQLEnum(RemoteType), nullable=True, index=True)
    
    # Application details
    application_date = Column(Date, nullable=True, index=True)
    deadline = Column(Date, nullable=True)
    status = Column(SQLEnum(ApplicationStatus), nullable=False, default=ApplicationStatus.APPLIED, index=True)
    priority = Column(SQLEnum(Priority), nullable=False, default=Priority.MEDIUM, index=True)
    
    # Notes and contacts
    notes = Column(Text, nullable=True)
    referral_name = Column(String(100), nullable=True)
    contact_email = Column(String(255), nullable=True)
    contact_person = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    
    # Relationships
    followups = relationship("Followup", back_populates="application", cascade="all, delete-orphan")
    interviews = relationship("Interview", back_populates="application", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary."""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, (datetime, date)):
                result[column.name] = value.isoformat() if value else None
            elif hasattr(value, 'value'):  # Enum values
                result[column.name] = value.value
            else:
                result[column.name] = value
        return result

    def __repr__(self):
        return f"<Application(id={self.id}, company='{self.company_name}', title='{self.job_title}', status='{self.status}')>"


class Followup(Base):
    """SQLAlchemy model for application follow-ups and general interactions."""
    __tablename__ = 'followups'

    id = Column(Integer, primary_key=True, autoincrement=True)
    application_id = Column(Integer, ForeignKey('applications.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Interaction details
    interaction_type = Column(SQLEnum(InteractionType), nullable=False, default=InteractionType.FOLLOW_UP)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    interaction_date = Column(Date, nullable=False, index=True)
    
    # Status tracking
    old_status = Column(SQLEnum(ApplicationStatus), nullable=True)
    new_status = Column(SQLEnum(ApplicationStatus), nullable=True)
    outcome = Column(String(500), nullable=True)
    
    # Follow-up management
    follow_up_needed = Column(Boolean, nullable=False, default=False)
    follow_up_date = Column(Date, nullable=True)
    
    # Additional data
    notes = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)  # For storing additional structured data
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    
    # Relationships
    application = relationship("Application", back_populates="followups")

    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary."""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, (datetime, date)):
                result[column.name] = value.isoformat() if value else None
            elif hasattr(value, 'value'):  # Enum values
                result[column.name] = value.value
            else:
                result[column.name] = value
        return result

    def __repr__(self):
        return f"<Followup(id={self.id}, app_id={self.application_id}, type='{self.interaction_type}', title='{self.title}')>"


class Interview(Base):
    """SQLAlchemy model for interview-specific interactions."""
    __tablename__ = 'interviews'

    id = Column(Integer, primary_key=True, autoincrement=True)
    application_id = Column(Integer, ForeignKey('applications.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Interview details
    interview_type = Column(String(100), nullable=False)  # phone_screen, technical, onsite, etc.
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    interview_date = Column(Date, nullable=False, index=True)
    interview_time = Column(String(50), nullable=True)  # Time as string for flexibility
    
    # Location/format
    location = Column(String(200), nullable=True)
    is_virtual = Column(Boolean, nullable=False, default=False)
    meeting_link = Column(Text, nullable=True)
    
    # Participants
    interviewer_names = Column(Text, nullable=True)  # Comma-separated or JSON
    interviewer_roles = Column(Text, nullable=True)
    
    # Interview process
    round_number = Column(Integer, nullable=True)
    total_rounds = Column(Integer, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    
    # Results and feedback
    outcome = Column(String(500), nullable=True)
    feedback = Column(Text, nullable=True)
    technical_topics = Column(Text, nullable=True)  # JSON or comma-separated
    questions_asked = Column(Text, nullable=True)
    
    # Status and follow-up
    status = Column(String(50), nullable=False, default='scheduled')  # scheduled, completed, cancelled, rescheduled
    follow_up_needed = Column(Boolean, nullable=False, default=False)
    follow_up_date = Column(Date, nullable=True)
    
    # Additional data
    notes = Column(Text, nullable=True)
    preparation_notes = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)  # For storing additional structured data
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    
    # Relationships
    application = relationship("Application", back_populates="interviews")

    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary."""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, (datetime, date)):
                result[column.name] = value.isoformat() if value else None
            elif hasattr(value, 'value'):  # Enum values
                result[column.name] = value.value
            else:
                result[column.name] = value
        return result

    def __repr__(self):
        return f"<Interview(id={self.id}, app_id={self.application_id}, type='{self.interview_type}', date='{self.interview_date}')>"


class JobApplicationDB:
    """Database operations class for job applications using SQLAlchemy ORM."""
    
    def __init__(self, database_url: str, echo: bool = False):
        """
        Initialize the database connection.
        
        Args:
            database_url: PostgreSQL connection string
            echo: Whether to echo SQL statements (for debugging)
        """
        self.database_url = database_url
        self.echo = echo
        self.engine = None
        self.SessionLocal = None
        self._setup_database()
    
    def _setup_database(self):
        """Setup database engine and session factory."""
        try:
            self.engine = create_engine(
                self.database_url,
                echo=self.echo,
                pool_size=10,
                max_overflow=20,
                pool_timeout=30,
                pool_recycle=3600,
                pool_pre_ping=True
            )
            
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            logger.info("Database connection established successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup database: {e}")
            raise
    
    def init_db(self):
        """Initialize database tables."""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            raise
    
    def get_session(self) -> Session:
        """Get a database session."""
        return self.SessionLocal()
    
    @asynccontextmanager
    async def get_db_session(self):
        """Async context manager for database sessions."""
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()
    
    # Application CRUD operations
    
    def create_application(self, application_data: Dict[str, Any]) -> Optional[int]:
        """
        Create a new application.
        
        Args:
            application_data: Dictionary containing application data
            
        Returns:
            Application ID if successful, None otherwise
        """
        session = self.get_session()
        try:
            # Create new application instance
            app = Application(**application_data)
            session.add(app)
            session.commit()
            session.refresh(app)
            
            logger.info(f"Created application {app.id} for {app.company_name}")
            return app.id
            
        except IntegrityError as e:
            session.rollback()
            logger.error(f"Integrity error creating application: {e}")
            return None
        except Exception as e:
            session.rollback()
            logger.error(f"Error creating application: {e}")
            raise
        finally:
            session.close()
    
    def get_application(self, application_id: int) -> Optional[Dict[str, Any]]:
        """
        Get application by ID.
        
        Args:
            application_id: Application ID
            
        Returns:
            Application data dictionary or None if not found
        """
        session = self.get_session()
        try:
            app = session.query(Application).filter(Application.id == application_id).first()
            if app:
                result = app.to_dict()
                # Add calculated fields
                if app.application_date:
                    days_since = (date.today() - app.application_date).days
                    result['days_since_applied'] = days_since
                return result
            return None
        except Exception as e:
            logger.error(f"Error retrieving application {application_id}: {e}")
            raise
        finally:
            session.close()
    
    def get_applications(
        self, 
        filters: Optional[Dict[str, Any]] = None, 
        page: int = 1, 
        limit: int = 20,
        sort_by: str = 'created_at',
        sort_order: str = 'desc'
    ) -> Dict[str, Any]:
        """
        Get paginated list of applications with optional filtering.
        
        Args:
            filters: Dictionary of filter criteria
            page: Page number (1-indexed)
            limit: Number of items per page
            sort_by: Field to sort by
            sort_order: Sort order ('asc' or 'desc')
            
        Returns:
            Dictionary with items, total, pagination metadata
        """
        session = self.get_session()
        try:
            query = session.query(Application)
            
            # Apply filters
            if filters:
                if 'status' in filters and filters['status']:
                    if isinstance(filters['status'], list):
                        query = query.filter(Application.status.in_(filters['status']))
                    else:
                        query = query.filter(Application.status == filters['status'])
                
                if 'company_name' in filters and filters['company_name']:
                    query = query.filter(Application.company_name.ilike(f"%{filters['company_name']}%"))
                
                if 'job_type' in filters and filters['job_type']:
                    if isinstance(filters['job_type'], list):
                        query = query.filter(Application.job_type.in_(filters['job_type']))
                    else:
                        query = query.filter(Application.job_type == filters['job_type'])
                
                if 'remote_type' in filters and filters['remote_type']:
                    if isinstance(filters['remote_type'], list):
                        query = query.filter(Application.remote_type.in_(filters['remote_type']))
                    else:
                        query = query.filter(Application.remote_type == filters['remote_type'])
                
                if 'priority' in filters and filters['priority']:
                    if isinstance(filters['priority'], list):
                        query = query.filter(Application.priority.in_(filters['priority']))
                    else:
                        query = query.filter(Application.priority == filters['priority'])
                
                if 'date_from' in filters and filters['date_from']:
                    query = query.filter(Application.application_date >= filters['date_from'])
                
                if 'date_to' in filters and filters['date_to']:
                    query = query.filter(Application.application_date <= filters['date_to'])
                
                if 'search' in filters and filters['search']:
                    search_term = f"%{filters['search']}%"
                    query = query.filter(
                        Application.company_name.ilike(search_term) |
                        Application.job_title.ilike(search_term) |
                        Application.notes.ilike(search_term) |
                        Application.job_description.ilike(search_term)
                    )
            
            # Get total count
            total = query.count()
            
            # Apply sorting
            if hasattr(Application, sort_by):
                sort_column = getattr(Application, sort_by)
                if sort_order.lower() == 'desc':
                    query = query.order_by(sort_column.desc())
                else:
                    query = query.order_by(sort_column.asc())
            
            # Apply pagination
            offset = (page - 1) * limit
            applications = query.offset(offset).limit(limit).all()
            
            # Convert to dictionaries
            items = []
            for app in applications:
                app_dict = app.to_dict()
                # Add calculated fields
                if app.application_date:
                    days_since = (date.today() - app.application_date).days
                    app_dict['days_since_applied'] = days_since
                items.append(app_dict)
            
            # Calculate pagination metadata
            total_pages = (total + limit - 1) // limit if total > 0 else 0
            
            return {
                'items': items,
                'total': total,
                'page': page,
                'limit': limit,
                'pages': total_pages,
                'has_next': page < total_pages,
                'has_previous': page > 1
            }
            
        except Exception as e:
            logger.error(f"Error retrieving applications: {e}")
            raise
        finally:
            session.close()
    
    def update_application(self, application_id: int, update_data: Dict[str, Any]) -> bool:
        """
        Update an application.
        
        Args:
            application_id: Application ID
            update_data: Dictionary of fields to update
            
        Returns:
            True if successful, False otherwise
        """
        session = self.get_session()
        try:
            app = session.query(Application).filter(Application.id == application_id).first()
            if not app:
                return False
            
            # Update fields
            for field, value in update_data.items():
                if hasattr(app, field):
                    setattr(app, field, value)
            
            session.commit()
            logger.info(f"Updated application {application_id}")
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating application {application_id}: {e}")
            raise
        finally:
            session.close()
    
    def delete_application(self, application_id: int) -> bool:
        """
        Delete an application.
        
        Args:
            application_id: Application ID
            
        Returns:
            True if successful, False if not found
        """
        session = self.get_session()
        try:
            app = session.query(Application).filter(Application.id == application_id).first()
            if not app:
                return False
            
            session.delete(app)
            session.commit()
            logger.info(f"Deleted application {application_id}")
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error deleting application {application_id}: {e}")
            raise
        finally:
            session.close()
    
    # Followup operations
    
    def create_followup(self, followup_data: Dict[str, Any]) -> Optional[int]:
        """Create a new followup record."""
        session = self.get_session()
        try:
            followup = Followup(**followup_data)
            session.add(followup)
            session.commit()
            session.refresh(followup)
            
            logger.info(f"Created followup {followup.id} for application {followup.application_id}")
            return followup.id
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error creating followup: {e}")
            raise
        finally:
            session.close()
    
    def get_followups(self, application_id: int) -> List[Dict[str, Any]]:
        """Get all followups for an application."""
        session = self.get_session()
        try:
            followups = session.query(Followup).filter(
                Followup.application_id == application_id
            ).order_by(Followup.interaction_date.desc()).all()
            
            return [followup.to_dict() for followup in followups]
            
        except Exception as e:
            logger.error(f"Error retrieving followups for application {application_id}: {e}")
            raise
        finally:
            session.close()
    
    # Interview operations
    
    def create_interview(self, interview_data: Dict[str, Any]) -> Optional[int]:
        """Create a new interview record."""
        session = self.get_session()
        try:
            interview = Interview(**interview_data)
            session.add(interview)
            session.commit()
            session.refresh(interview)
            
            logger.info(f"Created interview {interview.id} for application {interview.application_id}")
            return interview.id
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error creating interview: {e}")
            raise
        finally:
            session.close()
    
    def get_interviews(self, application_id: int) -> List[Dict[str, Any]]:
        """Get all interviews for an application."""
        session = self.get_session()
        try:
            interviews = session.query(Interview).filter(
                Interview.application_id == application_id
            ).order_by(Interview.interview_date.desc()).all()
            
            return [interview.to_dict() for interview in interviews]
            
        except Exception as e:
            logger.error(f"Error retrieving interviews for application {application_id}: {e}")
            raise
        finally:
            session.close()
    
    # Analytics and statistics
    
    def get_application_statistics(self) -> Dict[str, Any]:
        """Get application statistics for analytics."""
        session = self.get_session()
        try:
            total_applications = session.query(Application).count()
            
            # Status distribution
            status_query = session.query(
                Application.status, 
                func.count(Application.id)
            ).group_by(Application.status).all()
            
            applications_by_status = {status.value: count for status, count in status_query}
            
            # Applications by month
            month_query = session.query(
                func.date_trunc('month', Application.application_date).label('month'),
                func.count(Application.id)
            ).filter(Application.application_date.isnot(None)).group_by('month').all()
            
            applications_by_month = {
                month.strftime('%Y-%m'): count for month, count in month_query
            }
            
            # Success rate (offers + accepted / total)
            offers = session.query(Application).filter(
                Application.status.in_([ApplicationStatus.OFFER, ApplicationStatus.ACCEPTED])
            ).count()
            
            success_rate = (offers / total_applications * 100) if total_applications > 0 else 0.0
            
            # Active applications
            active_statuses = [
                ApplicationStatus.APPLIED, ApplicationStatus.REVIEWING, 
                ApplicationStatus.PHONE_SCREEN, ApplicationStatus.TECHNICAL_INTERVIEW,
                ApplicationStatus.ONSITE_INTERVIEW, ApplicationStatus.FINAL_ROUND, 
                ApplicationStatus.OFFER
            ]
            
            active_applications = session.query(Application).filter(
                Application.status.in_(active_statuses)
            ).count()
            
            # Top companies
            company_query = session.query(
                Application.company_name,
                func.count(Application.id)
            ).group_by(Application.company_name).order_by(
                func.count(Application.id).desc()
            ).limit(5).all()
            
            top_companies = [
                {"company_name": company, "count": count}
                for company, count in company_query
            ]
            
            # Salary statistics
            salary_query = session.query(
                func.min(Application.salary_min),
                func.max(Application.salary_max),
                func.avg(Application.salary_min),
                func.avg(Application.salary_max)
            ).filter(
                (Application.salary_min.isnot(None)) | (Application.salary_max.isnot(None))
            ).first()
            
            salary_range = {
                "min": int(salary_query[0]) if salary_query[0] else None,
                "max": int(salary_query[1]) if salary_query[1] else None,
                "avg": int((salary_query[2] + salary_query[3]) / 2) if salary_query[2] and salary_query[3] else None
            }
            
            return {
                "total_applications": total_applications,
                "applications_by_status": applications_by_status,
                "applications_by_month": applications_by_month,
                "success_rate": round(success_rate, 1),
                "active_applications": active_applications,
                "top_companies": top_companies,
                "salary_range": salary_range
            }
            
        except Exception as e:
            logger.error(f"Error generating statistics: {e}")
            raise
        finally:
            session.close()


def create_database_instance(database_url: str = None, echo: bool = False) -> JobApplicationDB:
    """
    Factory function to create a JobApplicationDB instance.
    
    Args:
        database_url: PostgreSQL connection string. If None, will try to get from env
        echo: Whether to echo SQL statements
        
    Returns:
        JobApplicationDB instance
    """
    if not database_url:
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            raise ValueError("DATABASE_URL environment variable not set")
    
    return JobApplicationDB(database_url, echo)


def initialize_postgresql_database(database_url: str = None):
    """
    Initialize PostgreSQL database with tables.
    
    Args:
        database_url: PostgreSQL connection string
    """
    db = create_database_instance(database_url)
    db.init_db()
    logger.info("PostgreSQL database initialized successfully")
    return db

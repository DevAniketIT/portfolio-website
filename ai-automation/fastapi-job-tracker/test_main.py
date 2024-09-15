import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import tempfile

from main import app
from database import get_db
from models import Base


# Create a temporary database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


class TestJobTrackerAPI:
    """Test suite for Job Tracker API."""
    
    def setup_method(self):
        """Set up test data before each test."""
        self.test_user = {
            "email": "test@example.com",
            "full_name": "Test User",
            "password": "testpassword123"
        }
        
        self.test_job_application = {
            "title": "Software Engineer",
            "company": "Tech Corp",
            "description": "Full-stack development position",
            "location": "San Francisco, CA",
            "salary_range": "$100k - $150k",
            "job_url": "https://example.com/job/123"
        }
    
    def test_root_endpoint(self):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        assert "Welcome to" in response.json()["message"]
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_user_registration(self):
        """Test user registration."""
        response = client.post("/api/v1/auth/register", json=self.test_user)
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == self.test_user["email"]
        assert data["full_name"] == self.test_user["full_name"]
        assert "id" in data
    
    def test_user_login(self):
        """Test user login."""
        # First register a user
        client.post("/api/v1/auth/register", json=self.test_user)
        
        # Then try to login
        login_data = {
            "email": self.test_user["email"],
            "password": self.test_user["password"]
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_create_job_application(self):
        """Test creating a job application."""
        # Register and login user
        client.post("/api/v1/auth/register", json=self.test_user)
        login_response = client.post("/api/v1/auth/login", json={
            "email": self.test_user["email"],
            "password": self.test_user["password"]
        })
        token = login_response.json()["access_token"]
        
        # Create job application
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post("/api/v1/jobs/", json=self.test_job_application, headers=headers)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == self.test_job_application["title"]
        assert data["company"] == self.test_job_application["company"]
        assert "id" in data
    
    def test_get_job_applications(self):
        """Test getting job applications."""
        # Register and login user
        client.post("/api/v1/auth/register", json=self.test_user)
        login_response = client.post("/api/v1/auth/login", json={
            "email": self.test_user["email"],
            "password": self.test_user["password"]
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create a job application
        client.post("/api/v1/jobs/", json=self.test_job_application, headers=headers)
        
        # Get job applications
        response = client.get("/api/v1/jobs/", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert len(data["applications"]) >= 1
    
    def test_unauthorized_access(self):
        """Test that endpoints require authentication."""
        response = client.get("/api/v1/jobs/")
        assert response.status_code == 403
        
        response = client.post("/api/v1/jobs/", json=self.test_job_application)
        assert response.status_code == 403


if __name__ == "__main__":
    pytest.main([__file__])

"""
Test script to verify the tracking endpoints functionality.
This script tests the key functionality of the tracking router without starting the full server.
"""

import sys
import os

# Add parent directory to path to access the api module
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from datetime import date, datetime
from api.routers.tracking import (
    QuickTrackRequest, 
    TrackingResponse,
    calculate_response_rate,
    calculate_average_response_time,
    add_history_entry,
    find_application_by_id,
    application_history_db,
    next_history_id
)
from api.routers.applications import applications_db, get_current_timestamp
from api.models import ApplicationStatus, JobType, RemoteType, Priority

def test_quick_track_request():
    """Test the QuickTrackRequest model validation."""
    print("Testing QuickTrackRequest model...")
    
    # Valid request
    request = QuickTrackRequest(
        company="Test Company",
        title="Software Engineer",
        url="https://example.com/job",
        notes="Test notes"
    )
    print(f"✓ Valid request created: {request.company} - {request.title}")
    
    # Minimal request (without URL and notes)
    minimal_request = QuickTrackRequest(
        company="Minimal Company",
        title="Developer"
    )
    print(f"✓ Minimal request created: {minimal_request.company} - {minimal_request.title}")
    
    print("QuickTrackRequest tests passed!\n")

def test_tracking_response():
    """Test the TrackingResponse model."""
    print("Testing TrackingResponse model...")
    
    response = TrackingResponse(
        tracking_id=123,
        company="Test Company",
        title="Software Engineer",
        status=ApplicationStatus.APPLIED,
        created_at=datetime.now()
    )
    print(f"✓ TrackingResponse created: ID {response.tracking_id} - {response.company}")
    print("TrackingResponse tests passed!\n")

def test_utility_functions():
    """Test utility functions."""
    print("Testing utility functions...")
    
    # Clear any existing data
    applications_db.clear()
    application_history_db.clear()
    
    # Add sample application to database
    sample_app = {
        "id": 1,
        "company_name": "Test Corp",
        "job_title": "Engineer",
        "job_url": None,
        "job_description": None,
        "location": "San Francisco",
        "salary_min": 100000,
        "salary_max": 150000,
        "currency": "USD",
        "job_type": JobType.FULL_TIME.value,
        "remote_type": RemoteType.HYBRID.value,
        "application_date": date.today(),
        "deadline": None,
        "status": ApplicationStatus.APPLIED.value,
        "priority": Priority.HIGH.value,
        "notes": "Test application",
        "referral_name": None,
        "contact_email": "test@company.com",
        "contact_person": "John Doe",
        "created_at": get_current_timestamp(),
        "updated_at": get_current_timestamp(),
        "days_since_applied": 0,
        "last_interaction_date": date.today()
    }
    applications_db.append(sample_app)
    
    # Test find_application_by_id
    found_app = find_application_by_id(1)
    assert found_app is not None, "Should find application by ID"
    print("✓ find_application_by_id works correctly")
    
    # Test add_history_entry
    history_id = add_history_entry(
        application_id=1,
        interaction_type="application",
        title="Application submitted",
        description="Initial application",
        new_status=ApplicationStatus.APPLIED.value
    )
    assert history_id == 1, "Should return correct history ID"
    assert len(application_history_db) == 1, "Should add history entry to database"
    print("✓ add_history_entry works correctly")
    
    # Test calculate_response_rate with no responses
    rate = calculate_response_rate()
    assert rate == 0.0, "Should return 0% response rate for applied status only"
    print("✓ calculate_response_rate works for no responses")
    
    # Update application status to simulate response
    applications_db[0]["status"] = ApplicationStatus.PHONE_SCREEN.value
    rate = calculate_response_rate()
    assert rate == 100.0, "Should return 100% response rate when app advances"
    print("✓ calculate_response_rate works for responses")
    
    # Test calculate_average_response_time
    avg_time = calculate_average_response_time()
    assert avg_time == 7.0, "Should return 7 days for phone screen status"
    print("✓ calculate_average_response_time works correctly")
    
    print("Utility function tests passed!\n")

def test_data_structures():
    """Test that our data structures work correctly."""
    print("Testing data structures...")
    
    # Test that we can create applications with all required fields
    print(f"Applications DB has {len(applications_db)} entries")
    print(f"History DB has {len(application_history_db)} entries")
    
    if applications_db:
        app = applications_db[0]
        required_fields = [
            "id", "company_name", "job_title", "status", "created_at", "updated_at"
        ]
        for field in required_fields:
            assert field in app, f"Application should have {field} field"
        print("✓ Application has all required fields")
    
    if application_history_db:
        history = application_history_db[0]
        required_history_fields = [
            "id", "application_id", "interaction_type", "title", "created_at"
        ]
        for field in required_history_fields:
            assert field in history, f"History should have {field} field"
        print("✓ History entry has all required fields")
    
    print("Data structure tests passed!\n")

def test_analytics_calculations():
    """Test analytics calculation functions."""
    print("Testing analytics calculations...")
    
    # Clear and set up test data
    applications_db.clear()
    
    # Add multiple applications with different statuses
    test_apps = [
        {"id": 1, "company_name": "Company A", "status": "applied", "application_date": date.today(), "salary_min": 80000, "salary_max": 100000},
        {"id": 2, "company_name": "Company B", "status": "reviewing", "application_date": date.today(), "salary_min": 90000, "salary_max": 120000},
        {"id": 3, "company_name": "Company A", "status": "offer", "application_date": date.today(), "salary_min": 100000, "salary_max": 140000},
        {"id": 4, "company_name": "Company C", "status": "rejected", "application_date": date.today(), "salary_min": 70000, "salary_max": 90000},
    ]
    
    for app in test_apps:
        # Fill in other required fields
        app.update({
            "job_title": "Software Engineer",
            "job_url": None,
            "job_description": None,
            "location": None,
            "currency": "USD",
            "job_type": JobType.FULL_TIME.value,
            "remote_type": RemoteType.ON_SITE.value,
            "deadline": None,
            "priority": Priority.MEDIUM.value,
            "notes": None,
            "referral_name": None,
            "contact_email": None,
            "contact_person": None,
            "created_at": get_current_timestamp(),
            "updated_at": get_current_timestamp(),
            "days_since_applied": 0,
            "last_interaction_date": date.today()
        })
        applications_db.append(app)
    
    # Test response rate calculation
    # Should be 2/4 = 50% (reviewing and offer are responses, applied and rejected are not)
    rate = calculate_response_rate()
    print(f"Response rate: {rate}%")
    assert rate == 50.0, f"Expected 50% response rate, got {rate}%"
    print("✓ Response rate calculation works correctly")
    
    print("Analytics calculation tests passed!\n")

def main():
    """Run all tests."""
    print("=" * 50)
    print("TESTING TRACKING ENDPOINTS")
    print("=" * 50)
    print()
    
    try:
        test_quick_track_request()
        test_tracking_response()
        test_utility_functions()
        test_data_structures()
        test_analytics_calculations()
        
        print("=" * 50)
        print("ALL TESTS PASSED! ✓")
        print("The tracking endpoints are ready to use.")
        print("=" * 50)
        
        # Print endpoint summary
        print("\nAvailable endpoints:")
        print("- POST /api/tracking/track - Quick application tracking")
        print("- GET /api/tracking/application-history/{id} - Detailed history")
        print("- GET /api/tracking/stats - Analytics dashboard data")
        print("- POST /api/tracking/application-history/{id}/interaction - Add interaction")
        print("- GET /api/tracking/recent-activity - Recent activity overview")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

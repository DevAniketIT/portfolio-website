#!/usr/bin/env python3
"""
Job Tracker API - Python Client Example

A comprehensive example demonstrating how to integrate with the Job Application Tracker API
using the client SDK. This example covers all major endpoints and use cases, including error
handling and bulk operations.

Usage:
    python python_client_example.py

Requirements:
    pip install requests python-dateutil
"""

import sys
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time
import random

# Add the parent directory to the path so we can import the client_sdk module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the client SDK
from client_sdk import (
    JobTrackerClient, 
    JobTrackerError, 
    ValidationError, 
    NotFoundError, 
    AuthenticationError,
    RateLimitError,
    ServerError,
    ConnectionError,
    RetryConfig,
    ClientConfig
)


# Helper functions and utilities for the examples
def print_header(title):
    """Print a formatted section header"""
    print("\n" + "="*60)
    print(title.upper())
    print("="*60)

def print_success(message):
    """Print a success message"""
    print(f"✅ {message}")
    
def print_error(message):
    """Print an error message"""
    print(f"❌ {message}")

def print_info(message):
    """Print an info message"""
    print(f"ℹ️ {message}")


def demonstrate_basic_operations():
    """Demonstrate basic CRUD operations using the SDK"""
    print_header("BASIC APPLICATION MANAGEMENT EXAMPLES")
    
    # Initialize client with retry configuration
    retry_config = RetryConfig(max_attempts=3, base_delay=1.0, jitter=True)
    client = JobTrackerClient(
        base_url="http://localhost:8000", 
        retry_config=retry_config
    )
    
    # 1. Create a new application
    print("\n1. Creating a new application...")
    application_data = {
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
        "notes": "Applied through referral from John",
        "contact_email": "recruiter@google.com",
        "status": "applied"
    }
    
    try:
        result = client.create_application(application_data)
        app_id = result['data']['id']
        print_success(f"Created application with ID: {app_id}")
        
        # 2. Get the created application
        print(f"\n2. Retrieving application {app_id}...")
        app = client.get_application(app_id)
        print_success(f"Found application: {app['data']['company_name']} - {app['data']['job_title']}")
        
        # 3. Update application status
        print(f"\n3. Updating application status...")
        client.update_application_status(app_id, "phone_screen")
        print_success("Updated status to 'phone_screen'")
        
        # 4. Add partial update
        print(f"\n4. Adding notes and updating priority...")
        update_data = {
            "notes": "Phone screen scheduled for next week. Recruiter was very positive!",
            "priority": "urgent"
        }
        client.update_application(app_id, update_data)
        print_success("Updated application with additional notes")
        
        # 5. Demonstrate the health check endpoint
        print(f"\n5. Testing API health check...")
        health = client.health_check()
        print_success(f"API health status: {health.get('status', 'OK')}")
        
        return app_id
        
    except ValidationError as e:
        print_error(f"Validation error: {e}")
        if hasattr(e, 'errors') and e.errors:
            for error in e.errors:
                print_error(f"  - {error}")
        return None
    except NotFoundError as e:
        print_error(f"Resource not found: {e}")
        return None
    except Exception as e:
        print_error(f"Error in basic operations: {e}")
        return None


def demonstrate_filtering_and_search():
    """Demonstrate filtering and search capabilities using the SDK"""
    print_header("FILTERING AND SEARCH EXAMPLES")
    
    client = JobTrackerClient(base_url="http://localhost:8000")
    
    try:
        # 1. Get all applications with pagination
        print("\n1. Getting all applications (first page)...")
        all_apps = client.get_applications(page=1, limit=10)
        print_success(f"Found {all_apps.get('total', 0)} total applications")
        print_info(f"Showing page {all_apps.get('page', 1)} of {all_apps.get('pages', 1)}")
        
        # 2. Filter by status
        print("\n2. Filtering by status...")
        applied_apps = client.get_applications(status=["applied", "reviewing"])
        items = applied_apps.get('items', [])
        print_success(f"Found {len(items)} applications with status 'applied' or 'reviewing'")
        
        # 3. Search by company
        print("\n3. Searching for Google applications...")
        google_apps = client.get_applications(company_name="Google")
        print_success(f"Found {len(google_apps.get('items', []))} applications at Google")
        
        # 4. Date range filtering
        print("\n4. Getting applications from last month...")
        last_month = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        recent_apps = client.get_applications(date_from=last_month)
        print_success(f"Found {len(recent_apps.get('items', []))} applications from the last 30 days")
        
        # 5. Full-text search
        print("\n5. Searching for 'engineer' across all fields...")
        search_results = client.get_applications(search="engineer", limit=5)
        print_success(f"Found {len(search_results.get('items', []))} applications matching 'engineer'")
        
        # 6. Advanced filtering
        print("\n6. Advanced filtering (remote, high priority)...")
        filtered = client.get_applications(
            remote_type=["remote", "hybrid"],
            priority="high",
            sort_by="application_date",
            sort_order="desc"
        )
        print_success(f"Found {len(filtered.get('items', []))} high-priority remote/hybrid applications")
        
    except ValidationError as e:
        print_error(f"Validation error: {e}")
    except Exception as e:
        print_error(f"Error in filtering examples: {e}")


def demonstrate_tracking_features():
    """Demonstrate tracking and analytics features using the SDK"""
    print_header("TRACKING AND ANALYTICS EXAMPLES")
    
    client = JobTrackerClient(base_url="http://localhost:8000")
    
    try:
        # 1. Quick tracking (minimal fields)
        print("\n1. Quick application tracking...")
        quick_result = client.quick_track(
            company="StartupXYZ",
            title="Full Stack Developer",
            url="https://startupxyz.com/careers/fullstack",
            notes="Found through AngelList, exciting startup"
        )
        print_success(f"Quickly tracked application: {quick_result.get('company', 'Unknown')} - {quick_result.get('title', 'Unknown')}")
        
        # 2. Get analytics stats
        print("\n2. Getting analytics data...")
        stats = client.get_analytics_stats()
        print_success(f"Analytics Summary:")
        print_info(f"Total Applications: {stats.get('total_applications', 0)}")
        print_info(f"Success Rate: {stats.get('success_rate', 0)}%")
        print_info(f"Active Applications: {stats.get('active_applications', 0)}")
        print_info(f"Average Response Time: {stats.get('average_response_time', 0)} days")
        
        top_companies = stats.get('top_companies', [])
        if top_companies:
            print_info(f"Top Companies:")
            for company in top_companies[:3]:
                print_info(f"  - {company.get('company_name', 'Unknown')}: {company.get('count', 0)} applications")
        
        # 3. Get recent activity
        print("\n3. Getting recent activity...")
        activity = client.get_recent_activity(days=14, limit=5)
        recent_activity = activity.get('recent_activity', [])
        print_success(f"Found {len(recent_activity)} recent activities:")
        
        for item in recent_activity[:3]:
            if item.get('type') == 'application':
                print_info(f"📝 Applied to {item.get('company_name')} for {item.get('job_title')}")
            else:
                print_info(f"🔄 {item.get('title')} at {item.get('company_name')}")
        
        # 4. Add interaction (if we have an application)
        print("\n4. Adding interaction to application history...")
        # Get first application from recent activity
        apps = client.get_applications(limit=1)
        items = apps.get('items', [])
        
        if items:
            app_id = items[0]['id']
            interaction = client.add_interaction(
                app_id,
                interaction_type="phone_call",
                title="Follow-up Call",
                description="Called recruiter to check on application status",
                outcome="Will hear back by end of week"
            )
            print_success(f"Added interaction to application {app_id}")
            
            # Get application history
            print_info(f"Getting application history...")
            history = client.get_application_history(app_id)
            print_info(f"Application has {len(history.get('status_changes', []))} status changes")
            print_info(f"Application has {len(history.get('interactions', []))} interactions")
        
    except ValidationError as e:
        print_error(f"Validation error: {e}")
    except NotFoundError as e:
        print_error(f"Not found: {e}")
    except Exception as e:
        print_error(f"Error in tracking examples: {e}")


def demonstrate_utility_endpoints():
    """Demonstrate utility endpoints using the SDK"""
    print_header("UTILITY ENDPOINTS EXAMPLES")
    
    client = JobTrackerClient(base_url="http://localhost:8000")
    
    try:
        # 1. Get applications by specific status
        print("\n1. Getting applications by status...")
        statuses = ["applied", "phone_screen", "offer"]
        
        for status in statuses:
            apps = client.get_applications_by_status(status, limit=5)
            items = apps.get('items', [])
            print_success(f"{status.replace('_', ' ').title()}: {len(items)} applications")
        
        # 2. Get applications by company
        print("\n2. Getting applications by company...")
        companies = ["Google", "Microsoft", "Amazon"]
        
        for company in companies:
            try:
                apps = client.get_applications_by_company(company, limit=5)
                items = apps.get('items', [])
                print_success(f"{company}: {len(items)} applications")
            except NotFoundError:
                print_info(f"{company}: No applications found")
            except Exception as e:
                print_error(f"Error fetching {company} applications: {e}")
        
        # 3. Bulk status updates using the bulk operation feature
        print("\n3. Demonstrating bulk operations...")
        # Get a few applications to update
        recent_apps = client.get_applications(limit=5)
        items = recent_apps.get('items', [])
        
        if items:
            # Extract IDs of applications with 'applied' status
            app_ids = [app['id'] for app in items if app.get('status') == 'applied']
            
            if app_ids:
                print_info(f"Updating {len(app_ids)} applications to 'reviewing' status")
                
                # Use the bulk update method
                results = client.bulk_update_status(
                    application_ids=app_ids,
                    status='reviewing',
                    batch_size=2,  # Small batch size for demonstration
                    delay_between_batches=0.5
                )
                
                # Count successful updates
                successful = sum(1 for r in results if r.get('success', False))
                print_success(f"Bulk updated {successful} of {len(app_ids)} applications")
                
                # Show any errors
                errors = [r for r in results if not r.get('success', False)]
                if errors:
                    print_info(f"Failed to update {len(errors)} applications:")
                    for error in errors[:3]:  # Show first 3 errors
                        print_error(f"  App ID {error.get('application_id')}: {error.get('error')}")
            else:
                print_info("No 'applied' applications found to update")
        else:
            print_info("No applications found for bulk update demonstration")
        
    except Exception as e:
        print_error(f"Error in utility examples: {e}")


def demonstrate_error_handling():
    """Demonstrate proper error handling using the SDK exceptions"""
    print_header("ERROR HANDLING EXAMPLES")
    
    client = JobTrackerClient(base_url="http://localhost:8000")
    
    # 1. Invalid application ID
    print("\n1. Testing invalid application ID...")
    try:
        client.get_application(999999)
        print_error("This should have failed!")
    except NotFoundError as e:
        print_success(f"Properly handled NotFoundError: {e}")
    except Exception as e:
        print_error(f"Unexpected error: {e}")
    
    # 2. Invalid data validation
    print("\n2. Testing validation errors...")
    try:
        invalid_data = {
            "company_name": "",  # Empty company name should fail
            "job_title": "Test Role",
            "salary_min": -1000,  # Invalid salary
        }
        client.create_application(invalid_data)
        print_error("This should have failed!")
    except ValidationError as e:
        print_success(f"Properly handled ValidationError: {e}")
        if hasattr(e, 'errors') and e.errors:
            print_info("Validation errors:")
            for error in e.errors:
                print_info(f"  - {error}")
    except Exception as e:
        print_error(f"Unexpected error: {e}")
    
    # 3. Invalid status update
    print("\n3. Testing invalid status...")
    try:
        # Get first application
        apps = client.get_applications(limit=1)
        items = apps.get('items', [])
        if items:
            client.update_application_status(items[0]['id'], 'invalid_status')
            print_error("This should have failed!")
        else:
            print_info("No applications found to test invalid status update")
    except ValidationError as e:
        print_success(f"Properly handled ValidationError: {e}")
    except Exception as e:
        print_error(f"Unexpected error: {e}")
    
    # 4. Demonstrate retry logic (simulated)
    print("\n4. Demonstrating retry logic (simulation)...")
    print_info("The SDK automatically retries on server errors and rate limits.")
    print_info("Here's how a retry would look during rate limiting:")
    
    # Create a retry example
    retry_attempts = 3
    for attempt in range(retry_attempts):
        print_info(f"Attempt {attempt+1}/{retry_attempts}: Making request...")
        if attempt < retry_attempts - 1:
            delay = 2 ** attempt  # Exponential backoff
            print_info(f"Rate limit exceeded. Retrying in {delay}s...")
            time.sleep(0.5)  # Just for demonstration, don't actually wait full time
        else:
            print_success("Request succeeded after retries")
    
    print_success("Error handling demonstration complete!")


def demonstrate_bulk_operations():
    """Demonstrate bulk operations using the SDK"""
    print_header("BULK OPERATIONS EXAMPLES")
    
    client = JobTrackerClient(base_url="http://localhost:8000")
    
    try:
        # Generate sample applications for bulk creation
        print("\n1. Bulk creating multiple applications...")
        
        companies = ["TechCorp", "DevInc", "CodeLabs", "ByteWorks", "AlgoCo"]
        positions = ["Frontend Developer", "Backend Engineer", "DevOps Specialist", "Data Scientist", "Product Manager"]
        locations = ["San Francisco, CA", "New York, NY", "Austin, TX", "Seattle, WA", "Boston, MA"]
        
        # Generate 5 sample applications with different data
        applications = []
        for i in range(5):
            company_idx = i % len(companies)
            position_idx = i % len(positions)
            location_idx = i % len(locations)
            
            applications.append({
                "company_name": f"{companies[company_idx]} {random.randint(1, 100)}",
                "job_title": positions[position_idx],
                "location": locations[location_idx],
                "job_type": "full_time",
                "remote_type": random.choice(["remote", "hybrid", "on_site"]),
                "priority": random.choice(["low", "medium", "high"]),
                "notes": f"Bulk created application #{i+1}",
                "status": "applied"
            })
        
        # Perform bulk creation with small batch size for demonstration
        results = client.bulk_create_applications(
            applications=applications,
            batch_size=2,  # Small batch size for demonstration
            delay_between_batches=0.5
        )
        
        # Analyze results
        successful = sum(1 for r in results if r.get('success', False))
        print_success(f"Successfully created {successful} of {len(applications)} applications")
        
        # Get IDs of created applications for later cleanup
        created_ids = [r.get('data', {}).get('data', {}).get('id') 
                      for r in results if r.get('success', False)]
        
        # Show error details if any
        errors = [r for r in results if not r.get('success', False)]
        if errors:
            print_info(f"Failed to create {len(errors)} applications:")
            for error in errors:
                print_error(f"  Error: {error.get('error')}")
        
        # 2. Demonstrate bulk status update if we have any created applications
        if created_ids:
            print("\n2. Bulk updating application statuses...")
            update_results = client.bulk_update_status(
                application_ids=created_ids,
                status="reviewing",
                batch_size=2,
                delay_between_batches=0.5
            )
            
            successful_updates = sum(1 for r in update_results if r.get('success', False))
            print_success(f"Successfully updated {successful_updates} of {len(created_ids)} applications")
            
            # Clean up the applications we created
            print("\n3. Cleaning up bulk created applications...")
            for app_id in created_ids:
                try:
                    client.delete_application(app_id)
                    print_info(f"Deleted application {app_id}")
                except Exception as e:
                    print_error(f"Failed to delete application {app_id}: {e}")
            
            print_success(f"Cleaned up all {len(created_ids)} bulk-created applications")
        
    except Exception as e:
        print_error(f"Error in bulk operations: {e}")


def main():
    """Main demonstration function using the JobTrackerClient SDK"""
    print("🚀 Job Application Tracker API - Python Client SDK Demo")
    print("=" * 60)
    print("This demo showcases the comprehensive SDK capabilities including:")
    print("- Automatic retry logic with exponential backoff")
    print("- Comprehensive error handling with custom exceptions")
    print("- Type hints and input validation")
    print("- Bulk operations with batching")
    print("\nMake sure the API server is running on http://localhost:8000")
    print("=" * 60)
    
    try:
        # Test API connection using the health check method
        client = JobTrackerClient(base_url="http://localhost:8000")
        
        try:
            health = client.health_check()
            print_success("API server is running and accessible")
        except ConnectionError:
            print_error("API server is not responding. Please start the server first.")
            return
        
        # Run all demonstrations
        app_id = demonstrate_basic_operations()
        demonstrate_filtering_and_search()
        demonstrate_tracking_features()
        demonstrate_utility_endpoints()
        demonstrate_error_handling()
        demonstrate_bulk_operations()
        
        print_header("DEMONSTRATION COMPLETE!")
        print("This example covered:")
        print_success("Basic CRUD operations with robust error handling")
        print_success("Advanced filtering and search capabilities")
        print_success("Tracking and analytics features")
        print_success("Utility endpoints and convenience methods")
        print_success("Proper error handling with custom exceptions")
        print_success("Bulk operations with batching and rate limiting")
        print_success("Automatic retry logic with exponential backoff")
        
        print("\nFor API documentation, visit: http://localhost:8000/docs")
        
        # Clean up the demo application if created
        if app_id:
            try:
                client.delete_application(app_id)
                print_info(f"Cleaned up demo application {app_id}")
            except Exception:
                pass  # Ignore cleanup errors
                
    except Exception as e:
        print_error(f"Demo failed: {e}")
        print_info("Please ensure the API server is running and accessible.")


if __name__ == "__main__":
    main()

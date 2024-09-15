#!/usr/bin/env python3
"""
Script to generate a Postman collection for the Job Application Tracker API.

This script creates a complete Postman collection that can be imported 
directly into Postman for API testing.
"""

import json
from datetime import datetime

def generate_postman_collection():
    """Generate a complete Postman collection for the API."""
    
    collection = {
        "info": {
            "name": "Job Application Tracker API",
            "description": "A comprehensive REST API for managing and tracking job applications with powerful filtering, analytics, and history tracking capabilities.",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
            "version": "1.0.0",
            "_postman_id": "12345678-1234-5678-9abc-123456789abc"
        },
        "auth": {
            "type": "apikey",
            "apikey": [
                {
                    "key": "key",
                    "value": "X-API-Key",
                    "type": "string"
                },
                {
                    "key": "value",
                    "value": "{{api_key}}",
                    "type": "string"
                },
                {
                    "key": "in",
                    "value": "header",
                    "type": "string"
                }
            ]
        },
        "variable": [
            {
                "key": "base_url",
                "value": "http://localhost:8000",
                "type": "string",
                "description": "Base URL for the API"
            },
            {
                "key": "api_key",
                "value": "your-api-key-here",
                "type": "string",
                "description": "API key for authentication (if required)"
            }
        ],
        "item": []
    }

    # Applications folder
    applications_folder = {
        "name": "Applications",
        "description": "Complete CRUD operations for managing job applications",
        "item": [
            {
                "name": "List Applications",
                "request": {
                    "method": "GET",
                    "header": [],
                    "url": {
                        "raw": "{{base_url}}/api/applications/?page=1&limit=20",
                        "host": ["{{base_url}}"],
                        "path": ["api", "applications", ""],
                        "query": [
                            {"key": "page", "value": "1"},
                            {"key": "limit", "value": "20"},
                            {"key": "status", "value": "applied", "disabled": True},
                            {"key": "company_name", "value": "Google", "disabled": True},
                            {"key": "search", "value": "python", "disabled": True},
                            {"key": "sort_by", "value": "created_at", "disabled": True},
                            {"key": "sort_order", "value": "desc", "disabled": True}
                        ]
                    },
                    "description": "Get a paginated list of job applications with optional filtering and sorting"
                },
                "response": []
            },
            {
                "name": "Create Application",
                "request": {
                    "method": "POST",
                    "header": [
                        {"key": "Content-Type", "value": "application/json"}
                    ],
                    "url": {
                        "raw": "{{base_url}}/api/applications/",
                        "host": ["{{base_url}}"],
                        "path": ["api", "applications", ""]
                    },
                    "body": {
                        "mode": "raw",
                        "raw": json.dumps({
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
                        }, indent=2)
                    },
                    "description": "Create a new job application"
                },
                "response": []
            },
            {
                "name": "Get Application by ID",
                "request": {
                    "method": "GET",
                    "header": [],
                    "url": {
                        "raw": "{{base_url}}/api/applications/123",
                        "host": ["{{base_url}}"],
                        "path": ["api", "applications", "123"]
                    },
                    "description": "Retrieve a specific job application by ID"
                },
                "response": []
            },
            {
                "name": "Update Application",
                "request": {
                    "method": "PUT",
                    "header": [
                        {"key": "Content-Type", "value": "application/json"}
                    ],
                    "url": {
                        "raw": "{{base_url}}/api/applications/123",
                        "host": ["{{base_url}}"],
                        "path": ["api", "applications", "123"]
                    },
                    "body": {
                        "mode": "raw",
                        "raw": json.dumps({
                            "status": "phone_screen",
                            "notes": "Completed phone screen successfully",
                            "priority": "high"
                        }, indent=2)
                    },
                    "description": "Update a job application (partial update supported)"
                },
                "response": []
            },
            {
                "name": "Delete Application",
                "request": {
                    "method": "DELETE",
                    "header": [],
                    "url": {
                        "raw": "{{base_url}}/api/applications/123",
                        "host": ["{{base_url}}"],
                        "path": ["api", "applications", "123"]
                    },
                    "description": "Delete a job application by ID"
                },
                "response": []
            },
            {
                "name": "Get Applications by Status",
                "request": {
                    "method": "GET",
                    "header": [],
                    "url": {
                        "raw": "{{base_url}}/api/applications/status/applied?page=1&limit=10",
                        "host": ["{{base_url}}"],
                        "path": ["api", "applications", "status", "applied"],
                        "query": [
                            {"key": "page", "value": "1"},
                            {"key": "limit", "value": "10"}
                        ]
                    },
                    "description": "Get applications filtered by a specific status"
                },
                "response": []
            },
            {
                "name": "Get Applications by Company",
                "request": {
                    "method": "GET",
                    "header": [],
                    "url": {
                        "raw": "{{base_url}}/api/applications/company/Google?page=1&limit=10",
                        "host": ["{{base_url}}"],
                        "path": ["api", "applications", "company", "Google"],
                        "query": [
                            {"key": "page", "value": "1"},
                            {"key": "limit", "value": "10"}
                        ]
                    },
                    "description": "Get applications filtered by company name"
                },
                "response": []
            },
            {
                "name": "Update Application Status",
                "request": {
                    "method": "PATCH",
                    "header": [],
                    "url": {
                        "raw": "{{base_url}}/api/applications/123/status?status=reviewing",
                        "host": ["{{base_url}}"],
                        "path": ["api", "applications", "123", "status"],
                        "query": [
                            {"key": "status", "value": "reviewing"}
                        ]
                    },
                    "description": "Update only the status of a specific application"
                },
                "response": []
            }
        ]
    }

    # Tracking folder
    tracking_folder = {
        "name": "Tracking & Analytics",
        "description": "Application tracking and analytics endpoints",
        "item": [
            {
                "name": "Quick Track Application",
                "request": {
                    "method": "POST",
                    "header": [
                        {"key": "Content-Type", "value": "application/json"}
                    ],
                    "url": {
                        "raw": "{{base_url}}/api/tracking/track",
                        "host": ["{{base_url}}"],
                        "path": ["api", "tracking", "track"]
                    },
                    "body": {
                        "mode": "raw",
                        "raw": json.dumps({
                            "company": "Tech Corp Inc.",
                            "title": "Senior Software Engineer",
                            "url": "https://techcorp.com/careers/senior-engineer",
                            "notes": "Found through LinkedIn, looks promising"
                        }, indent=2)
                    },
                    "description": "Simplified endpoint for external job tracking with minimal required fields"
                },
                "response": []
            },
            {
                "name": "Get Application History",
                "request": {
                    "method": "GET",
                    "header": [],
                    "url": {
                        "raw": "{{base_url}}/api/tracking/application-history/123",
                        "host": ["{{base_url}}"],
                        "path": ["api", "tracking", "application-history", "123"]
                    },
                    "description": "Get comprehensive history for a specific application"
                },
                "response": []
            },
            {
                "name": "Get Analytics Stats",
                "request": {
                    "method": "GET",
                    "header": [],
                    "url": {
                        "raw": "{{base_url}}/api/tracking/stats",
                        "host": ["{{base_url}}"],
                        "path": ["api", "tracking", "stats"]
                    },
                    "description": "Get comprehensive analytics data for dashboard visualization"
                },
                "response": []
            },
            {
                "name": "Add Interaction to History",
                "request": {
                    "method": "POST",
                    "header": [],
                    "url": {
                        "raw": "{{base_url}}/api/tracking/application-history/123/interaction?interaction_type=phone_call&title=Follow-up Call&description=Called to check on status&outcome=Will hear back next week",
                        "host": ["{{base_url}}"],
                        "path": ["api", "tracking", "application-history", "123", "interaction"],
                        "query": [
                            {"key": "interaction_type", "value": "phone_call"},
                            {"key": "title", "value": "Follow-up Call"},
                            {"key": "description", "value": "Called to check on status"},
                            {"key": "outcome", "value": "Will hear back next week"}
                        ]
                    },
                    "description": "Add a new interaction or note to an application's history"
                },
                "response": []
            },
            {
                "name": "Get Recent Activity",
                "request": {
                    "method": "GET",
                    "header": [],
                    "url": {
                        "raw": "{{base_url}}/api/tracking/recent-activity?days=7&limit=10",
                        "host": ["{{base_url}}"],
                        "path": ["api", "tracking", "recent-activity"],
                        "query": [
                            {"key": "days", "value": "7"},
                            {"key": "limit", "value": "10"}
                        ]
                    },
                    "description": "Get recent applications and interactions for dashboard overview"
                },
                "response": []
            }
        ]
    }

    # General endpoints folder
    general_folder = {
        "name": "General",
        "description": "General API endpoints",
        "item": [
            {
                "name": "Root Endpoint",
                "request": {
                    "method": "GET",
                    "header": [],
                    "url": {
                        "raw": "{{base_url}}/",
                        "host": ["{{base_url}}"],
                        "path": [""]
                    },
                    "description": "Root endpoint providing API information"
                },
                "response": []
            },
            {
                "name": "Health Check",
                "request": {
                    "method": "GET",
                    "header": [],
                    "url": {
                        "raw": "{{base_url}}/health",
                        "host": ["{{base_url}}"],
                        "path": ["health"]
                    },
                    "description": "API health check endpoint"
                },
                "response": []
            },
            {
                "name": "API Documentation Info",
                "request": {
                    "method": "GET",
                    "header": [],
                    "url": {
                        "raw": "{{base_url}}/docs/info",
                        "host": ["{{base_url}}"],
                        "path": ["docs", "info"]
                    },
                    "description": "Get API information and documentation links"
                },
                "response": []
            },
            {
                "name": "OpenAPI Schema",
                "request": {
                    "method": "GET",
                    "header": [],
                    "url": {
                        "raw": "{{base_url}}/openapi.json",
                        "host": ["{{base_url}}"],
                        "path": ["openapi.json"]
                    },
                    "description": "Get the OpenAPI schema definition"
                },
                "response": []
            }
        ]
    }

    # Add folders to collection
    collection["item"] = [applications_folder, tracking_folder, general_folder]

    return collection

def main():
    """Generate and save the Postman collection."""
    print("Generating Job Application Tracker API Postman Collection...")
    
    collection = generate_postman_collection()
    
    # Save to file
    filename = "job-tracker-api.postman_collection.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(collection, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Postman collection saved as '{filename}'")
    print(f"📁 Total endpoints: {sum(len(folder['item']) for folder in collection['item'])}")
    print("\nTo use this collection:")
    print("1. Import the JSON file into Postman")
    print("2. Set up environment variables:")
    print("   - base_url: http://localhost:8000 (or your API URL)")
    print("   - api_key: your-api-key (if authentication is enabled)")
    print("3. Start testing the API endpoints!")
    print("\n🔗 Collection includes:")
    for folder in collection["item"]:
        print(f"   • {folder['name']}: {len(folder['item'])} endpoints")

if __name__ == "__main__":
    main()

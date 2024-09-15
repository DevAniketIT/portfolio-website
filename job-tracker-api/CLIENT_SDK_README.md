# JobTracker Python Client SDK

A comprehensive, production-ready Python SDK for the Job Application Tracker API. This SDK provides a complete interface with automatic retry logic, comprehensive error handling, response validation, and type hints.

## Features

- **Complete CRUD Operations**: Full support for job application management
- **Automatic Retry Logic**: Exponential backoff for handling rate limits and server errors
- **Comprehensive Error Handling**: Custom exceptions with detailed error information
- **Response Validation**: Automatic validation and parsing of API responses
- **Type Hints**: Full type annotations for better IDE support and code quality
- **Session Management**: Connection pooling and optimized HTTP sessions
- **Bulk Operations**: Efficient batch processing with rate limiting
- **Analytics and Tracking**: Built-in support for tracking and analytics features
- **Context Manager Support**: Proper resource management with `with` statements

## Installation

```bash
pip install requests python-dateutil typing-extensions
```

## Quick Start

```python
from client_sdk import JobTrackerClient

# Initialize client
client = JobTrackerClient("https://your-api-server.com")

# Create an application
application = client.create_application({
    "company_name": "Google Inc.",
    "job_title": "Software Engineer",
    "location": "Mountain View, CA",
    "status": "applied"
})

print(f"Created application with ID: {application['data']['id']}")
```

## Configuration

### Retry Configuration

```python
from client_sdk import JobTrackerClient, RetryConfig

retry_config = RetryConfig(
    max_attempts=5,
    base_delay=2.0,
    max_delay=120.0,
    exponential_base=2.0,
    jitter=True
)

client = JobTrackerClient(
    "https://api.example.com", 
    retry_config=retry_config
)
```

### Client Configuration

```python
from client_sdk import JobTrackerClient, ClientConfig

client_config = ClientConfig(
    timeout=60.0,
    max_connections=20,
    max_connections_per_host=10,
    verify_ssl=True,
    user_agent="MyApp/1.0"
)

client = JobTrackerClient(
    "https://api.example.com",
    client_config=client_config
)
```

## Authentication

```python
# With API key
client = JobTrackerClient(
    "https://api.example.com",
    api_key="your-api-key"
)

# Update API key later
client.set_api_key("new-api-key")
```

## Usage Examples

### Basic CRUD Operations

```python
from client_sdk import JobTrackerClient, ValidationError, NotFoundError

client = JobTrackerClient("https://api.example.com")

try:
    # Create application
    app_data = {
        "company_name": "TechCorp",
        "job_title": "Senior Developer",
        "job_url": "https://techcorp.com/jobs/123",
        "location": "San Francisco, CA",
        "salary_min": 100000,
        "salary_max": 150000,
        "remote_type": "hybrid",
        "priority": "high"
    }
    
    app = client.create_application(app_data)
    app_id = app['data']['id']
    
    # Retrieve application
    application = client.get_application(app_id)
    
    # Update application
    client.update_application(app_id, {
        "notes": "Had a great phone interview!",
        "status": "phone_screen"
    })
    
    # Update just the status
    client.update_application_status(app_id, "technical_interview")
    
    # Delete application
    client.delete_application(app_id)
    
except ValidationError as e:
    print(f"Validation error: {e}")
    for error in e.errors:
        print(f"  - {error}")
except NotFoundError:
    print("Application not found")
```

### Filtering and Search

```python
# Get all applications with pagination
apps = client.get_applications(page=1, limit=20)

# Filter by status
applied_apps = client.get_applications(status=["applied", "reviewing"])

# Filter by multiple criteria
filtered_apps = client.get_applications(
    company_name="Google",
    remote_type=["remote", "hybrid"],
    priority="high",
    date_from="2024-01-01",
    sort_by="application_date",
    sort_order="desc"
)

# Full-text search
search_results = client.get_applications(search="software engineer")

# Get applications by status
phone_screens = client.get_applications_by_status("phone_screen")

# Get applications by company
google_apps = client.get_applications_by_company("Google")
```

### Tracking and Analytics

```python
# Quick application tracking
quick_app = client.quick_track(
    company="StartupXYZ",
    title="Full Stack Developer",
    url="https://startup.com/jobs/123",
    notes="Exciting opportunity in AI/ML"
)

# Get analytics
stats = client.get_analytics_stats()
print(f"Total applications: {stats['total_applications']}")
print(f"Success rate: {stats['success_rate']}%")

# Get recent activity
activity = client.get_recent_activity(days=7, limit=10)

# Add interaction
client.add_interaction(
    app_id,
    interaction_type="phone_call",
    title="Follow-up Call",
    description="Discussed role requirements",
    outcome="Technical interview scheduled"
)

# Get application history
history = client.get_application_history(app_id)
```

### Bulk Operations

```python
# Bulk create applications
applications_data = [
    {
        "company_name": f"Company {i}",
        "job_title": "Software Engineer",
        "status": "applied"
    }
    for i in range(10)
]

results = client.bulk_create_applications(
    applications=applications_data,
    batch_size=5,
    delay_between_batches=1.0
)

# Check results
successful = [r for r in results if r['success']]
failed = [r for r in results if not r['success']]

print(f"Created {len(successful)} applications successfully")
print(f"Failed to create {len(failed)} applications")

# Bulk update status
app_ids = [r['data']['data']['id'] for r in successful]
update_results = client.bulk_update_status(
    application_ids=app_ids,
    status="reviewing",
    batch_size=3
)
```

### Context Manager

```python
# Automatic resource cleanup
with JobTrackerClient("https://api.example.com") as client:
    apps = client.get_applications()
    # Client is automatically closed when exiting the context
```

## Error Handling

The SDK provides custom exceptions for different types of errors:

```python
from client_sdk import (
    JobTrackerError,          # Base exception
    ValidationError,          # Invalid request data
    NotFoundError,           # Resource not found
    AuthenticationError,     # Authentication failed
    RateLimitError,         # Rate limit exceeded
    ServerError,            # Server error (5xx)
    ConnectionError         # Network/connection issues
)

try:
    client.get_application(999999)
except NotFoundError:
    print("Application not found")
except AuthenticationError:
    print("Authentication failed - check your API key")
except RateLimitError as e:
    print(f"Rate limited - retry after {e.retry_after} seconds")
except ValidationError as e:
    print("Validation errors:")
    for error in e.errors:
        print(f"  - {error}")
except ServerError:
    print("Server error - please try again later")
except ConnectionError:
    print("Network connection failed")
except JobTrackerError as e:
    print(f"General API error: {e}")
```

## Advanced Configuration

### Custom Retry Logic

```python
from client_sdk import RetryConfig

# Custom retry configuration
retry_config = RetryConfig(
    max_attempts=3,
    base_delay=1.0,
    max_delay=60.0,
    exponential_base=2.0,
    jitter=True,
    retry_on_status=[429, 500, 502, 503, 504]
)

client = JobTrackerClient(
    base_url="https://api.example.com",
    retry_config=retry_config
)

# Update retry config later
client.configure_retries(retry_config)
```

### Connection Pooling

```python
from client_sdk import ClientConfig

# Optimize for high-throughput scenarios
client_config = ClientConfig(
    timeout=30.0,
    max_connections=50,
    max_connections_per_host=20,
    verify_ssl=True
)

client = JobTrackerClient(
    base_url="https://api.example.com",
    client_config=client_config
)
```

### Session Information

```python
# Get current session configuration
session_info = client.get_session_info()
print(f"Base URL: {session_info['base_url']}")
print(f"Has API Key: {session_info['has_api_key']}")
print(f"Timeout: {session_info['timeout']}")
print(f"SSL Verification: {session_info['verify_ssl']}")
```

## Testing

The SDK includes a comprehensive test suite:

```bash
# Run SDK validation tests
python test_sdk.py
```

## Examples

Complete examples are available in the `examples/` directory:

- `python_client_example.py` - Comprehensive demonstration of all SDK features
- Run the example: `python examples/python_client_example.py`

## API Compatibility

This SDK is compatible with JobTracker API v1.0.0 and supports all endpoints:

- **Applications**: CRUD operations, filtering, search
- **Tracking**: Quick tracking, analytics, interactions
- **Utility**: Health checks, status updates, bulk operations

## Best Practices

### 1. Use Context Managers

```python
with JobTrackerClient("https://api.example.com") as client:
    # Your code here
    pass  # Client is automatically cleaned up
```

### 2. Handle Specific Exceptions

```python
try:
    app = client.get_application(app_id)
except NotFoundError:
    # Handle missing resource specifically
    pass
except ValidationError as e:
    # Handle validation errors with details
    for error in e.errors:
        print(f"Validation error: {error}")
```

### 3. Use Bulk Operations for Multiple Items

```python
# Instead of individual requests
for app_id in app_ids:
    client.update_application_status(app_id, "reviewing")  # Don't do this

# Use bulk operations
client.bulk_update_status(app_ids, "reviewing")  # Much better
```

### 4. Configure Retries Appropriately

```python
# For production environments
retry_config = RetryConfig(
    max_attempts=5,
    base_delay=1.0,
    max_delay=300.0,  # 5 minutes max
    jitter=True  # Avoid thundering herd
)
```

### 5. Monitor Rate Limits

```python
try:
    result = client.create_application(data)
except RateLimitError as e:
    if e.retry_after:
        print(f"Rate limited. Retry after {e.retry_after} seconds")
        time.sleep(e.retry_after)
        # Retry the operation
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
   ```bash
   pip install requests python-dateutil typing-extensions
   ```

2. **Connection Errors**: Check your base URL and network connectivity
   ```python
   # Test connection
   try:
       health = client.health_check()
       print("API is accessible")
   except ConnectionError:
       print("Cannot connect to API server")
   ```

3. **Authentication Errors**: Verify your API key
   ```python
   client.set_api_key("your-correct-api-key")
   ```

4. **Validation Errors**: Check your request data format
   ```python
   try:
       client.create_application(data)
   except ValidationError as e:
       print("Validation errors:")
       for error in e.errors:
           print(f"  - {error}")
   ```

### Debug Information

Enable debug logging to see detailed request/response information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

When contributing to the SDK:

1. Follow the existing code style and patterns
2. Add comprehensive error handling
3. Include type hints for all public methods
4. Write tests for new functionality
5. Update documentation for any API changes

## License

This SDK is part of the JobTracker project and follows the same licensing terms.

---

For more information, visit the [API documentation](http://localhost:8000/docs) or check the examples in the `examples/` directory.

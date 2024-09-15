#!/usr/bin/env python3
"""
Job Tracker API - Python Client SDK

A comprehensive, production-ready Python SDK for the Job Application Tracker API.
This SDK provides a complete interface with automatic retry logic, comprehensive
error handling, response validation, and type hints.

Features:
- Complete CRUD operations for job applications
- Automatic retry logic with exponential backoff
- Comprehensive error handling and custom exceptions
- Response validation and type hints
- Session management and connection pooling
- Rate limiting and request throttling
- Bulk operations support
- Analytics and tracking features

Usage:
    from client_sdk import JobTrackerClient, JobTrackerError
    
    client = JobTrackerClient(base_url="https://api.example.com", api_key="your-key")
    
    # Create application
    app = client.create_application({
        "company_name": "Google",
        "job_title": "Software Engineer"
    })

Requirements:
    pip install requests python-dateutil typing-extensions
"""

import requests
import json
import time
import random
from datetime import datetime, date
from typing import Dict, List, Optional, Union, Any, Callable
from urllib.parse import urljoin
import logging
from functools import wraps
from dataclasses import dataclass
from enum import Enum


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Custom Exceptions
class JobTrackerError(Exception):
    """Base exception for Job Tracker API errors."""
    pass


class AuthenticationError(JobTrackerError):
    """Raised when authentication fails."""
    pass


class ValidationError(JobTrackerError):
    """Raised when request data validation fails."""
    
    def __init__(self, message: str, errors: List[str] = None):
        super().__init__(message)
        self.errors = errors or []


class NotFoundError(JobTrackerError):
    """Raised when a resource is not found."""
    pass


class RateLimitError(JobTrackerError):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str, retry_after: Optional[int] = None):
        super().__init__(message)
        self.retry_after = retry_after


class ServerError(JobTrackerError):
    """Raised when server encounters an error."""
    pass


class ConnectionError(JobTrackerError):
    """Raised when connection fails."""
    pass


# Configuration classes
@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    retry_on_status: List[int] = None
    
    def __post_init__(self):
        if self.retry_on_status is None:
            self.retry_on_status = [429, 500, 502, 503, 504]


@dataclass
class ClientConfig:
    """Configuration for the client."""
    timeout: float = 30.0
    max_connections: int = 10
    max_connections_per_host: int = 5
    user_agent: str = "JobTracker-Python-SDK/1.0.0"
    verify_ssl: bool = True


# Response validation and parsing
class ResponseValidator:
    """Validates and parses API responses."""
    
    @staticmethod
    def validate_response(response: requests.Response) -> Dict[str, Any]:
        """Validate and parse response with comprehensive error handling."""
        try:
            # Check for successful status codes
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 201:
                return response.json()
            elif response.status_code == 204:
                return {"success": True, "message": "Operation completed successfully"}
            
            # Handle error status codes
            elif response.status_code == 400:
                error_data = response.json() if response.content else {}
                raise ValidationError(
                    error_data.get("message", "Invalid request data"),
                    error_data.get("errors", [])
                )
            elif response.status_code == 401:
                raise AuthenticationError("Authentication failed. Check your API key.")
            elif response.status_code == 403:
                raise AuthenticationError("Access forbidden. Insufficient permissions.")
            elif response.status_code == 404:
                raise NotFoundError("Resource not found")
            elif response.status_code == 422:
                error_data = response.json() if response.content else {}
                raise ValidationError(
                    error_data.get("message", "Validation failed"),
                    error_data.get("errors", [])
                )
            elif response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                raise RateLimitError(
                    "Rate limit exceeded",
                    int(retry_after) if retry_after else None
                )
            elif 500 <= response.status_code < 600:
                raise ServerError(f"Server error: {response.status_code}")
            else:
                raise JobTrackerError(f"Unexpected status code: {response.status_code}")
                
        except (ValueError, json.JSONDecodeError) as e:
            if response.status_code < 400:
                # Successful response but invalid JSON
                return {"success": True, "raw_response": response.text}
            else:
                raise JobTrackerError(f"Invalid response format: {e}")
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Request failed: {e}")


# Retry decorator
def with_retry(retry_config: RetryConfig = None):
    """Decorator to add retry logic to methods."""
    if retry_config is None:
        retry_config = RetryConfig()
    
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            last_exception = None
            
            for attempt in range(retry_config.max_attempts):
                try:
                    return func(self, *args, **kwargs)
                except RateLimitError as e:
                    last_exception = e
                    if e.retry_after:
                        delay = e.retry_after
                    else:
                        delay = min(
                            retry_config.base_delay * (retry_config.exponential_base ** attempt),
                            retry_config.max_delay
                        )
                    
                    if retry_config.jitter:
                        delay += random.uniform(0, delay * 0.1)
                    
                    if attempt < retry_config.max_attempts - 1:
                        logger.warning(f"Rate limited. Retrying in {delay:.2f}s (attempt {attempt + 1}/{retry_config.max_attempts})")
                        time.sleep(delay)
                    continue
                    
                except (ConnectionError, ServerError) as e:
                    last_exception = e
                    if attempt < retry_config.max_attempts - 1:
                        delay = min(
                            retry_config.base_delay * (retry_config.exponential_base ** attempt),
                            retry_config.max_delay
                        )
                        if retry_config.jitter:
                            delay += random.uniform(0, delay * 0.1)
                        
                        logger.warning(f"Request failed. Retrying in {delay:.2f}s (attempt {attempt + 1}/{retry_config.max_attempts}): {e}")
                        time.sleep(delay)
                        continue
                    
                except (AuthenticationError, ValidationError, NotFoundError):
                    # Don't retry these errors
                    raise
                    
                except Exception as e:
                    last_exception = JobTrackerError(f"Unexpected error: {e}")
                    break
            
            # If we get here, all retries failed
            raise last_exception or JobTrackerError("Max retries exceeded")
        
        return wrapper
    return decorator


# Main client class
class JobTrackerClient:
    """
    Production-ready Python client for Job Application Tracker API.
    
    This client provides a complete interface to the Job Tracker API with
    automatic retry logic, comprehensive error handling, and type hints.
    
    Args:
        base_url: Base URL of the API (e.g., "https://api.example.com")
        api_key: Optional API key for authentication
        retry_config: Configuration for retry behavior
        client_config: Configuration for HTTP client
        
    Example:
        >>> client = JobTrackerClient("https://api.example.com", api_key="your-key")
        >>> application = client.create_application({
        ...     "company_name": "Google",
        ...     "job_title": "Software Engineer"
        ... })
        >>> print(f"Created application {application['id']}")
    """
    
    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        retry_config: Optional[RetryConfig] = None,
        client_config: Optional[ClientConfig] = None
    ):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.retry_config = retry_config or RetryConfig()
        self.client_config = client_config or ClientConfig()
        
        # Setup HTTP session with optimized configuration
        self.session = requests.Session()
        
        # Configure adapter for connection pooling
        adapter = requests.adapters.HTTPAdapter(
            max_retries=0,  # We handle retries ourselves
            pool_connections=self.client_config.max_connections,
            pool_maxsize=self.client_config.max_connections_per_host
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': self.client_config.user_agent,
            'Accept': 'application/json'
        })
        
        # Add API key if provided
        if self.api_key:
            self.session.headers.update({'X-API-Key': self.api_key})
        
        # Configure SSL verification
        self.session.verify = self.client_config.verify_ssl
        
        # Response validator
        self.validator = ResponseValidator()
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Make HTTP request with error handling and validation."""
        url = urljoin(self.base_url, endpoint.lstrip('/'))
        
        # Prepare request data
        request_kwargs = {
            'timeout': self.client_config.timeout,
            'params': params,
            **kwargs
        }
        
        if data is not None:
            request_kwargs['data'] = json.dumps(data) if isinstance(data, dict) else data
        
        try:
            response = self.session.request(method, url, **request_kwargs)
            return self.validator.validate_response(response)
        except requests.exceptions.Timeout:
            raise ConnectionError(f"Request timeout after {self.client_config.timeout}s")
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(f"Connection failed: {e}")
        except requests.exceptions.RequestException as e:
            raise JobTrackerError(f"Request failed: {e}")
    
    # Health check and utility methods
    @with_retry()
    def health_check(self) -> Dict[str, Any]:
        """Check API health and connectivity."""
        return self._make_request('GET', '/health')
    
    @with_retry()
    def get_api_info(self) -> Dict[str, Any]:
        """Get API information and available endpoints."""
        return self._make_request('GET', '/')
    
    # ==================== Application CRUD Operations ====================
    
    @with_retry()
    def create_application(self, application_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new job application.
        
        Args:
            application_data: Dictionary containing application data
            
        Returns:
            Created application data with ID
            
        Raises:
            ValidationError: If the provided data is invalid
            AuthenticationError: If authentication fails
            JobTrackerError: For other API errors
        """
        return self._make_request('POST', '/api/applications/', data=application_data)
    
    @with_retry()
    def get_application(self, application_id: int) -> Dict[str, Any]:
        """
        Get a specific application by ID.
        
        Args:
            application_id: ID of the application
            
        Returns:
            Application data
            
        Raises:
            NotFoundError: If application doesn't exist
            AuthenticationError: If authentication fails
        """
        return self._make_request('GET', f'/api/applications/{application_id}')
    
    @with_retry()
    def update_application(
        self, 
        application_id: int, 
        update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update an existing application (partial updates supported).
        
        Args:
            application_id: ID of the application to update
            update_data: Dictionary containing fields to update
            
        Returns:
            Updated application data
            
        Raises:
            NotFoundError: If application doesn't exist
            ValidationError: If the provided data is invalid
        """
        return self._make_request('PUT', f'/api/applications/{application_id}', data=update_data)
    
    @with_retry()
    def delete_application(self, application_id: int) -> Dict[str, Any]:
        """
        Delete an application by ID.
        
        Args:
            application_id: ID of the application to delete
            
        Returns:
            Deletion confirmation
            
        Raises:
            NotFoundError: If application doesn't exist
        """
        return self._make_request('DELETE', f'/api/applications/{application_id}')
    
    @with_retry()
    def get_applications(
        self,
        page: int = 1,
        limit: int = 20,
        status: Union[str, List[str], None] = None,
        company_name: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        **filters
    ) -> Dict[str, Any]:
        """
        Get applications with filtering and pagination.
        
        Args:
            page: Page number (default: 1)
            limit: Items per page (default: 20, max: 100)
            status: Filter by status (can be list or single value)
            company_name: Filter by company name (partial match)
            date_from: Filter applications from date (YYYY-MM-DD)
            date_to: Filter applications to date (YYYY-MM-DD)
            search: Search across multiple fields
            sort_by: Sort field (default: created_at)
            sort_order: Sort order 'asc' or 'desc' (default: desc)
            **filters: Additional filter parameters
            
        Returns:
            Paginated list of applications with metadata
        """
        params = {
            'page': page,
            'limit': limit,
            'sort_by': sort_by,
            'sort_order': sort_order
        }
        
        # Handle status filter (can be list or string)
        if status:
            if isinstance(status, list):
                for s in status:
                    params.setdefault('status', []).append(s) if isinstance(params.get('status'), list) else params.update({'status': [params.get('status', s)] if params.get('status') else [s]})
            else:
                params['status'] = status
        
        # Add other filters
        filter_mapping = {
            'company_name': company_name,
            'date_from': date_from,
            'date_to': date_to,
            'search': search
        }
        
        for key, value in filter_mapping.items():
            if value is not None:
                params[key] = value
        
        # Add any additional filters
        for key, value in filters.items():
            if value is not None:
                params[key] = value
        
        return self._make_request('GET', '/api/applications/', params=params)
    
    @with_retry()
    def update_application_status(self, application_id: int, status: str) -> Dict[str, Any]:
        """
        Update only the status of an application.
        
        Args:
            application_id: ID of the application
            status: New status value
            
        Returns:
            Updated application data
        """
        return self._make_request(
            'PATCH', 
            f'/api/applications/{application_id}/status',
            params={'status': status}
        )
    
    @with_retry()
    def get_applications_by_status(
        self, 
        status: str, 
        page: int = 1, 
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Get applications filtered by specific status.
        
        Args:
            status: Status to filter by
            page: Page number
            limit: Items per page
            
        Returns:
            Filtered applications
        """
        return self._make_request(
            'GET',
            f'/api/applications/status/{status}',
            params={'page': page, 'limit': limit}
        )
    
    @with_retry()
    def get_applications_by_company(
        self, 
        company_name: str, 
        page: int = 1, 
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Get applications filtered by company name.
        
        Args:
            company_name: Company name to filter by
            page: Page number
            limit: Items per page
            
        Returns:
            Filtered applications
        """
        return self._make_request(
            'GET',
            f'/api/applications/company/{company_name}',
            params={'page': page, 'limit': limit}
        )
    
    # ==================== Tracking & Analytics ====================
    
    @with_retry()
    def quick_track(
        self, 
        company: str, 
        title: str, 
        url: Optional[str] = None, 
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Quick application tracking with minimal fields.
        
        Args:
            company: Company name
            title: Job title
            url: Optional job URL
            notes: Optional notes
            
        Returns:
            Created application data
        """
        data = {
            'company': company,
            'title': title
        }
        if url:
            data['url'] = url
        if notes:
            data['notes'] = notes
        
        return self._make_request('POST', '/api/tracking/track', data=data)
    
    @with_retry()
    def get_application_history(self, application_id: int) -> Dict[str, Any]:
        """
        Get comprehensive application history including status changes and interactions.
        
        Args:
            application_id: ID of the application
            
        Returns:
            Application history data
        """
        return self._make_request('GET', f'/api/tracking/application-history/{application_id}')
    
    @with_retry()
    def get_analytics_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive analytics data.
        
        Returns:
            Analytics statistics including totals, success rates, and trends
        """
        return self._make_request('GET', '/api/tracking/stats')
    
    @with_retry()
    def add_interaction(
        self,
        application_id: int,
        interaction_type: str,
        title: str,
        description: Optional[str] = None,
        outcome: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add an interaction to application history.
        
        Args:
            application_id: ID of the application
            interaction_type: Type of interaction (email, phone_call, interview, etc.)
            title: Title of the interaction
            description: Optional description
            outcome: Optional outcome
            
        Returns:
            Created interaction data
        """
        params = {
            'interaction_type': interaction_type,
            'title': title
        }
        if description:
            params['description'] = description
        if outcome:
            params['outcome'] = outcome
        
        return self._make_request(
            'POST',
            f'/api/tracking/application-history/{application_id}/interaction',
            params=params
        )
    
    @with_retry()
    def get_recent_activity(self, days: int = 7, limit: int = 10) -> Dict[str, Any]:
        """
        Get recent applications and interactions.
        
        Args:
            days: Number of days to look back (default: 7)
            limit: Maximum number of activities to return (default: 10)
            
        Returns:
            Recent activity data
        """
        return self._make_request(
            'GET',
            '/api/tracking/recent-activity',
            params={'days': days, 'limit': limit}
        )
    
    # ==================== Bulk Operations ====================
    
    def bulk_create_applications(
        self, 
        applications: List[Dict[str, Any]],
        batch_size: int = 10,
        delay_between_batches: float = 1.0
    ) -> List[Dict[str, Any]]:
        """
        Create multiple applications in batches.
        
        Args:
            applications: List of application data dictionaries
            batch_size: Number of applications to create per batch
            delay_between_batches: Delay in seconds between batches
            
        Returns:
            List of created applications with results and errors
        """
        results = []
        
        for i in range(0, len(applications), batch_size):
            batch = applications[i:i + batch_size]
            batch_results = []
            
            for app_data in batch:
                try:
                    result = self.create_application(app_data)
                    batch_results.append({
                        'success': True,
                        'data': result,
                        'error': None
                    })
                except Exception as e:
                    batch_results.append({
                        'success': False,
                        'data': None,
                        'error': str(e),
                        'input_data': app_data
                    })
            
            results.extend(batch_results)
            
            # Delay between batches to avoid rate limiting
            if i + batch_size < len(applications):
                time.sleep(delay_between_batches)
        
        return results
    
    def bulk_update_status(
        self,
        application_ids: List[int],
        status: str,
        batch_size: int = 10,
        delay_between_batches: float = 1.0
    ) -> List[Dict[str, Any]]:
        """
        Update status for multiple applications in batches.
        
        Args:
            application_ids: List of application IDs to update
            status: New status for all applications
            batch_size: Number of updates per batch
            delay_between_batches: Delay in seconds between batches
            
        Returns:
            List of update results
        """
        results = []
        
        for i in range(0, len(application_ids), batch_size):
            batch = application_ids[i:i + batch_size]
            batch_results = []
            
            for app_id in batch:
                try:
                    result = self.update_application_status(app_id, status)
                    batch_results.append({
                        'success': True,
                        'application_id': app_id,
                        'data': result,
                        'error': None
                    })
                except Exception as e:
                    batch_results.append({
                        'success': False,
                        'application_id': app_id,
                        'data': None,
                        'error': str(e)
                    })
            
            results.extend(batch_results)
            
            # Delay between batches
            if i + batch_size < len(application_ids):
                time.sleep(delay_between_batches)
        
        return results
    
    # ==================== Utility Methods ====================
    
    def close(self):
        """Close the HTTP session."""
        if self.session:
            self.session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def set_api_key(self, api_key: str):
        """Update the API key."""
        self.api_key = api_key
        if api_key:
            self.session.headers.update({'X-API-Key': api_key})
        else:
            self.session.headers.pop('X-API-Key', None)
    
    def configure_retries(self, retry_config: RetryConfig):
        """Update retry configuration."""
        self.retry_config = retry_config
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get information about the current session."""
        return {
            'base_url': self.base_url,
            'has_api_key': bool(self.api_key),
            'user_agent': self.session.headers.get('User-Agent'),
            'timeout': self.client_config.timeout,
            'verify_ssl': self.session.verify,
            'retry_config': {
                'max_attempts': self.retry_config.max_attempts,
                'base_delay': self.retry_config.base_delay,
                'max_delay': self.retry_config.max_delay
            }
        }


# Convenience factory function
def create_client(
    base_url: str,
    api_key: Optional[str] = None,
    **kwargs
) -> JobTrackerClient:
    """
    Factory function to create a JobTrackerClient instance.
    
    Args:
        base_url: Base URL of the API
        api_key: Optional API key
        **kwargs: Additional configuration options
        
    Returns:
        Configured JobTrackerClient instance
    """
    return JobTrackerClient(base_url=base_url, api_key=api_key, **kwargs)


# Version info
__version__ = "1.0.0"
__all__ = [
    'JobTrackerClient',
    'JobTrackerError',
    'AuthenticationError',
    'ValidationError',
    'NotFoundError',
    'RateLimitError',
    'ServerError',
    'ConnectionError',
    'RetryConfig',
    'ClientConfig',
    'create_client'
]

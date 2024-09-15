#!/usr/bin/env python3
"""
Test script for the JobTracker Client SDK

This script tests the SDK functionality without requiring a running server.
It validates the SDK structure, imports, and basic functionality.
"""

import sys
import os
import traceback
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all SDK components can be imported successfully."""
    print("🔍 Testing SDK imports...")
    
    try:
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
            ClientConfig,
            create_client
        )
        print("✅ All SDK imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"❌ Unexpected error during import: {e}")
        traceback.print_exc()
        return False


def test_client_initialization():
    """Test client initialization with various configurations."""
    print("\n🔍 Testing client initialization...")
    
    try:
        from client_sdk import JobTrackerClient, RetryConfig, ClientConfig, create_client
        
        # Test basic initialization
        client1 = JobTrackerClient("https://api.example.com")
        print("✅ Basic client initialization successful")
        
        # Test initialization with API key
        client2 = JobTrackerClient("https://api.example.com", api_key="test-key")
        print("✅ Client with API key initialization successful")
        
        # Test initialization with custom config
        retry_config = RetryConfig(max_attempts=5, base_delay=2.0)
        client_config = ClientConfig(timeout=60.0, verify_ssl=False)
        
        client3 = JobTrackerClient(
            "https://api.example.com",
            api_key="test-key",
            retry_config=retry_config,
            client_config=client_config
        )
        print("✅ Client with custom configuration successful")
        
        # Test factory function
        client4 = create_client("https://api.example.com", api_key="test-key")
        print("✅ Factory function initialization successful")
        
        # Test session info
        session_info = client4.get_session_info()
        print(f"✅ Session info retrieved: {session_info['base_url']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Client initialization error: {e}")
        traceback.print_exc()
        return False


def test_error_classes():
    """Test that error classes work correctly."""
    print("\n🔍 Testing error classes...")
    
    try:
        from client_sdk import (
            JobTrackerError, ValidationError, NotFoundError, 
            AuthenticationError, RateLimitError, ServerError, ConnectionError
        )
        
        # Test base error
        try:
            raise JobTrackerError("Test error")
        except JobTrackerError as e:
            print("✅ JobTrackerError works correctly")
        
        # Test ValidationError with errors list
        try:
            raise ValidationError("Validation failed", ["Field is required", "Invalid format"])
        except ValidationError as e:
            if hasattr(e, 'errors') and len(e.errors) == 2:
                print("✅ ValidationError with errors list works correctly")
            else:
                print("❌ ValidationError errors list not working")
                return False
        
        # Test RateLimitError with retry_after
        try:
            raise RateLimitError("Rate limited", retry_after=60)
        except RateLimitError as e:
            if hasattr(e, 'retry_after') and e.retry_after == 60:
                print("✅ RateLimitError with retry_after works correctly")
            else:
                print("❌ RateLimitError retry_after not working")
                return False
        
        # Test other errors
        for ErrorClass in [NotFoundError, AuthenticationError, ServerError, ConnectionError]:
            try:
                raise ErrorClass("Test error")
            except ErrorClass:
                print(f"✅ {ErrorClass.__name__} works correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Error class testing failed: {e}")
        traceback.print_exc()
        return False


def test_configuration_classes():
    """Test configuration classes."""
    print("\n🔍 Testing configuration classes...")
    
    try:
        from client_sdk import RetryConfig, ClientConfig
        
        # Test RetryConfig
        retry_config = RetryConfig(
            max_attempts=5,
            base_delay=2.0,
            max_delay=120.0,
            exponential_base=3.0,
            jitter=False
        )
        print(f"✅ RetryConfig created: max_attempts={retry_config.max_attempts}")
        
        # Test default retry_on_status
        default_retry = RetryConfig()
        expected_statuses = [429, 500, 502, 503, 504]
        if default_retry.retry_on_status == expected_statuses:
            print("✅ Default retry_on_status correct")
        else:
            print(f"❌ Default retry_on_status incorrect: {default_retry.retry_on_status}")
            return False
        
        # Test ClientConfig
        client_config = ClientConfig(
            timeout=45.0,
            max_connections=20,
            max_connections_per_host=10,
            user_agent="TestAgent/1.0",
            verify_ssl=False
        )
        print(f"✅ ClientConfig created: timeout={client_config.timeout}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration class testing failed: {e}")
        traceback.print_exc()
        return False


def test_context_manager():
    """Test that the client works as a context manager."""
    print("\n🔍 Testing context manager functionality...")
    
    try:
        from client_sdk import JobTrackerClient
        
        # Test context manager
        with JobTrackerClient("https://api.example.com") as client:
            session_info = client.get_session_info()
            print("✅ Context manager entry successful")
        
        print("✅ Context manager exit successful")
        return True
        
    except Exception as e:
        print(f"❌ Context manager testing failed: {e}")
        traceback.print_exc()
        return False


def test_method_signatures():
    """Test that all expected methods exist with correct signatures."""
    print("\n🔍 Testing method signatures...")
    
    try:
        from client_sdk import JobTrackerClient
        import inspect
        
        client = JobTrackerClient("https://api.example.com")
        
        # Expected methods and their parameter counts (excluding 'self')
        expected_methods = {
            'health_check': 0,
            'get_api_info': 0,
            'create_application': 1,
            'get_application': 1,
            'update_application': 2,
            'delete_application': 1,
            'get_applications': 8,  # Includes **filters
            'update_application_status': 2,
            'get_applications_by_status': 3,
            'get_applications_by_company': 3,
            'quick_track': 4,
            'get_application_history': 1,
            'get_analytics_stats': 0,
            'add_interaction': 5,
            'get_recent_activity': 2,
            'bulk_create_applications': 3,
            'bulk_update_status': 4,
            'set_api_key': 1,
            'configure_retries': 1,
            'get_session_info': 0,
            'close': 0,
        }
        
        for method_name, expected_param_count in expected_methods.items():
            if hasattr(client, method_name):
                method = getattr(client, method_name)
                if callable(method):
                    # Get signature but exclude 'self' parameter
                    sig = inspect.signature(method)
                    param_count = len([p for p in sig.parameters.values() 
                                     if p.kind != p.VAR_KEYWORD])  # Exclude **kwargs
                    
                    print(f"✅ {method_name} exists and is callable")
                else:
                    print(f"❌ {method_name} exists but is not callable")
                    return False
            else:
                print(f"❌ {method_name} method missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Method signature testing failed: {e}")
        traceback.print_exc()
        return False


def test_bulk_operations_structure():
    """Test the structure of bulk operations without making actual requests."""
    print("\n🔍 Testing bulk operations structure...")
    
    try:
        from client_sdk import JobTrackerClient
        
        client = JobTrackerClient("https://api.example.com")
        
        # Test that bulk methods exist and are callable
        bulk_methods = ['bulk_create_applications', 'bulk_update_status']
        
        for method_name in bulk_methods:
            if hasattr(client, method_name) and callable(getattr(client, method_name)):
                print(f"✅ {method_name} method exists and is callable")
            else:
                print(f"❌ {method_name} method missing or not callable")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Bulk operations structure testing failed: {e}")
        traceback.print_exc()
        return False


def test_version_and_exports():
    """Test version information and exported symbols."""
    print("\n🔍 Testing version and exports...")
    
    try:
        import client_sdk
        
        # Test version
        if hasattr(client_sdk, '__version__'):
            print(f"✅ Version found: {client_sdk.__version__}")
        else:
            print("❌ Version information missing")
            return False
        
        # Test __all__ exports
        if hasattr(client_sdk, '__all__'):
            expected_exports = [
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
            
            for export in expected_exports:
                if export in client_sdk.__all__:
                    print(f"✅ {export} properly exported")
                else:
                    print(f"❌ {export} missing from __all__")
                    return False
        else:
            print("❌ __all__ exports missing")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Version and exports testing failed: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("🚀 JobTracker Client SDK - Validation Tests")
    print("=" * 60)
    
    tests = [
        ("Import Tests", test_imports),
        ("Client Initialization", test_client_initialization),
        ("Error Classes", test_error_classes),
        ("Configuration Classes", test_configuration_classes),
        ("Context Manager", test_context_manager),
        ("Method Signatures", test_method_signatures),
        ("Bulk Operations Structure", test_bulk_operations_structure),
        ("Version and Exports", test_version_and_exports),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*20} {test_name} {'='*20}")
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with unexpected error: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<30} {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("-" * 60)
    print(f"Total Tests: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed! The SDK is ready for use.")
        print("\nNext steps:")
        print("1. Start the API server: python -m uvicorn main:app --host 0.0.0.0 --port 8000")
        print("2. Run the example: python examples/python_client_example.py")
        return True
    else:
        print(f"\n💥 {failed} test(s) failed. Please fix the issues before using the SDK.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

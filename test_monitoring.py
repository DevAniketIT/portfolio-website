<<<<<<< HEAD
#!/usr/bin/env python3
"""
Monitoring Test Script

Tests all monitoring endpoints and validates the setup for:
- FastAPI health check
- Metrics endpoint
- Google Analytics integration
- Status badges functionality

Usage:
    python test_monitoring.py
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional


class MonitoringTester:
    """Test suite for monitoring and analytics setup."""
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url.rstrip('/')
        self.results = {}
        
    def test_health_endpoint(self) -> Dict[str, Any]:
        """Test the /health endpoint."""
        try:
            response = requests.get(f"{self.api_base_url}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "✅ PASS",
                    "response_code": response.status_code,
                    "response_time": response.elapsed.total_seconds(),
                    "data": data,
                    "checks": {
                        "has_status": "status" in data,
                        "has_timestamp": "timestamp" in data, 
                        "has_uptime": "uptime" in data,
                        "status_healthy": data.get("status") == "healthy"
                    }
                }
            else:
                return {
                    "status": "❌ FAIL",
                    "response_code": response.status_code,
                    "error": f"Expected 200, got {response.status_code}"
                }
                
        except requests.exceptions.ConnectionError:
            return {
                "status": "❌ FAIL", 
                "error": "Connection refused - is the API running?"
            }
        except Exception as e:
            return {
                "status": "❌ FAIL",
                "error": str(e)
            }
    
    def test_metrics_endpoint(self) -> Dict[str, Any]:
        """Test the /metrics endpoint."""
        try:
            response = requests.get(f"{self.api_base_url}/metrics", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "✅ PASS",
                    "response_code": response.status_code,
                    "response_time": response.elapsed.total_seconds(),
                    "data": data,
                    "checks": {
                        "has_total_requests": "total_requests" in data,
                        "has_last_request_ts": "last_request_ts" in data,
                        "has_endpoints": "endpoints" in data,
                        "endpoints_is_dict": isinstance(data.get("endpoints"), dict)
                    }
                }
            else:
                return {
                    "status": "❌ FAIL",
                    "response_code": response.status_code,
                    "error": f"Expected 200, got {response.status_code}"
                }
                
        except requests.exceptions.ConnectionError:
            return {
                "status": "❌ FAIL",
                "error": "Connection refused - is the API running?"
            }
        except Exception as e:
            return {
                "status": "❌ FAIL",
                "error": str(e)
            }
    
    def test_api_endpoints(self) -> Dict[str, Any]:
        """Test some API endpoints to generate metrics."""
        endpoints_to_test = [
            "/",
            "/api/applications",
            "/docs",
        ]
        
        results = {}
        
        for endpoint in endpoints_to_test:
            try:
                response = requests.get(f"{self.api_base_url}{endpoint}", timeout=10)
                results[endpoint] = {
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds(),
                    "success": response.status_code < 500
                }
            except Exception as e:
                results[endpoint] = {
                    "error": str(e),
                    "success": False
                }
        
        return results
    
    def test_status_badges(self) -> Dict[str, Any]:
        """Test status badge URLs (these should be accessible)."""
        badge_tests = {
            "shields.io": "https://img.shields.io/badge/test-working-green",
            "website_status": f"https://img.shields.io/website?url={self.api_base_url}/health"
        }
        
        results = {}
        
        for name, url in badge_tests.items():
            try:
                response = requests.get(url, timeout=10)
                results[name] = {
                    "status": "✅ PASS" if response.status_code == 200 else "❌ FAIL",
                    "response_code": response.status_code,
                    "content_type": response.headers.get("content-type", "")
                }
            except Exception as e:
                results[name] = {
                    "status": "❌ FAIL",
                    "error": str(e)
                }
        
        return results
    
    def run_load_test(self, requests_count: int = 10) -> Dict[str, Any]:
        """Run a simple load test to generate metrics data."""
        print(f"Running load test with {requests_count} requests...")
        
        start_time = time.time()
        successful_requests = 0
        failed_requests = 0
        response_times = []
        
        for i in range(requests_count):
            try:
                response = requests.get(f"{self.api_base_url}/health", timeout=10)
                if response.status_code == 200:
                    successful_requests += 1
                else:
                    failed_requests += 1
                response_times.append(response.elapsed.total_seconds())
            except Exception:
                failed_requests += 1
            
            # Small delay between requests
            time.sleep(0.1)
        
        total_time = time.time() - start_time
        
        return {
            "total_requests": requests_count,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "total_time": total_time,
            "avg_response_time": sum(response_times) / len(response_times) if response_times else 0,
            "min_response_time": min(response_times) if response_times else 0,
            "max_response_time": max(response_times) if response_times else 0,
            "requests_per_second": requests_count / total_time if total_time > 0 else 0
        }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all monitoring tests."""
        print("🧪 Starting Monitoring Tests...")
        print("=" * 50)
        
        # Test health endpoint
        print("Testing health endpoint...")
        self.results["health"] = self.test_health_endpoint()
        
        # Test some API endpoints to generate data
        print("Testing API endpoints...")
        api_results = self.test_api_endpoints()
        
        # Test metrics endpoint
        print("Testing metrics endpoint...")
        self.results["metrics"] = self.test_metrics_endpoint()
        
        # Test status badges
        print("Testing status badges...")
        self.results["badges"] = self.test_status_badges()
        
        # Run load test
        load_test_results = self.run_load_test()
        self.results["load_test"] = load_test_results
        
        # Test metrics again after load test
        print("Testing metrics after load test...")
        self.results["metrics_after_load"] = self.test_metrics_endpoint()
        
        return self.results
    
    def print_results(self):
        """Print formatted test results."""
        print("\n" + "="*50)
        print("🏥 MONITORING TEST RESULTS")
        print("="*50)
        
        # Health endpoint results
        health = self.results.get("health", {})
        print(f"\n🏥 Health Endpoint: {health.get('status', 'Unknown')}")
        if health.get('data'):
            print(f"   Response Time: {health.get('response_time', 0):.3f}s")
            print(f"   Status: {health['data'].get('status', 'unknown')}")
            print(f"   Uptime: {health['data'].get('uptime', 0):.1f}s")
        
        # Metrics endpoint results
        metrics = self.results.get("metrics", {})
        print(f"\n📊 Metrics Endpoint: {metrics.get('status', 'Unknown')}")
        if metrics.get('data'):
            print(f"   Response Time: {metrics.get('response_time', 0):.3f}s")
            print(f"   Total Requests: {metrics['data'].get('total_requests', 0)}")
            endpoints = metrics['data'].get('endpoints', {})
            print(f"   Tracked Endpoints: {len(endpoints)}")
        
        # Load test results
        load_test = self.results.get("load_test", {})
        if load_test:
            print(f"\n⚡ Load Test Results:")
            print(f"   Total Requests: {load_test.get('total_requests', 0)}")
            print(f"   Successful: {load_test.get('successful_requests', 0)}")
            print(f"   Failed: {load_test.get('failed_requests', 0)}")
            print(f"   Avg Response Time: {load_test.get('avg_response_time', 0):.3f}s")
            print(f"   Requests/Second: {load_test.get('requests_per_second', 0):.2f}")
        
        # Badge tests
        badges = self.results.get("badges", {})
        print(f"\n🏷️ Status Badges:")
        for name, result in badges.items():
            print(f"   {name}: {result.get('status', 'Unknown')}")
        
        # Metrics comparison (before/after load test)
        metrics_before = self.results.get("metrics", {}).get("data", {})
        metrics_after = self.results.get("metrics_after_load", {}).get("data", {})
        
        if metrics_before and metrics_after:
            requests_before = metrics_before.get("total_requests", 0)
            requests_after = metrics_after.get("total_requests", 0)
            print(f"\n📈 Metrics Change:")
            print(f"   Requests Before: {requests_before}")
            print(f"   Requests After: {requests_after}")
            print(f"   New Requests: {requests_after - requests_before}")
        
        print("\n" + "="*50)
        print("✅ Test completed!")
        print("="*50)


def main():
    """Main test runner."""
    import sys
    
    # Allow custom API URL via command line
    api_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    print(f"🔍 Testing monitoring setup for: {api_url}")
    
    tester = MonitoringTester(api_url)
    
    try:
        results = tester.run_all_tests()
        tester.print_results()
        
        # Save results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"monitoring_test_results_{timestamp}.json"
        
        with open(filename, "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to: {filename}")
        
    except KeyboardInterrupt:
        print("\n❌ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")


if __name__ == "__main__":
    main()
=======
#!/usr/bin/env python3
"""
Monitoring Test Script

Tests all monitoring endpoints and validates the setup for:
- FastAPI health check
- Metrics endpoint
- Google Analytics integration
- Status badges functionality

Usage:
    python test_monitoring.py
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional


class MonitoringTester:
    """Test suite for monitoring and analytics setup."""
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url.rstrip('/')
        self.results = {}
        
    def test_health_endpoint(self) -> Dict[str, Any]:
        """Test the /health endpoint."""
        try:
            response = requests.get(f"{self.api_base_url}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "✅ PASS",
                    "response_code": response.status_code,
                    "response_time": response.elapsed.total_seconds(),
                    "data": data,
                    "checks": {
                        "has_status": "status" in data,
                        "has_timestamp": "timestamp" in data, 
                        "has_uptime": "uptime" in data,
                        "status_healthy": data.get("status") == "healthy"
                    }
                }
            else:
                return {
                    "status": "❌ FAIL",
                    "response_code": response.status_code,
                    "error": f"Expected 200, got {response.status_code}"
                }
                
        except requests.exceptions.ConnectionError:
            return {
                "status": "❌ FAIL", 
                "error": "Connection refused - is the API running?"
            }
        except Exception as e:
            return {
                "status": "❌ FAIL",
                "error": str(e)
            }
    
    def test_metrics_endpoint(self) -> Dict[str, Any]:
        """Test the /metrics endpoint."""
        try:
            response = requests.get(f"{self.api_base_url}/metrics", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "✅ PASS",
                    "response_code": response.status_code,
                    "response_time": response.elapsed.total_seconds(),
                    "data": data,
                    "checks": {
                        "has_total_requests": "total_requests" in data,
                        "has_last_request_ts": "last_request_ts" in data,
                        "has_endpoints": "endpoints" in data,
                        "endpoints_is_dict": isinstance(data.get("endpoints"), dict)
                    }
                }
            else:
                return {
                    "status": "❌ FAIL",
                    "response_code": response.status_code,
                    "error": f"Expected 200, got {response.status_code}"
                }
                
        except requests.exceptions.ConnectionError:
            return {
                "status": "❌ FAIL",
                "error": "Connection refused - is the API running?"
            }
        except Exception as e:
            return {
                "status": "❌ FAIL",
                "error": str(e)
            }
    
    def test_api_endpoints(self) -> Dict[str, Any]:
        """Test some API endpoints to generate metrics."""
        endpoints_to_test = [
            "/",
            "/api/applications",
            "/docs",
        ]
        
        results = {}
        
        for endpoint in endpoints_to_test:
            try:
                response = requests.get(f"{self.api_base_url}{endpoint}", timeout=10)
                results[endpoint] = {
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds(),
                    "success": response.status_code < 500
                }
            except Exception as e:
                results[endpoint] = {
                    "error": str(e),
                    "success": False
                }
        
        return results
    
    def test_status_badges(self) -> Dict[str, Any]:
        """Test status badge URLs (these should be accessible)."""
        badge_tests = {
            "shields.io": "https://img.shields.io/badge/test-working-green",
            "website_status": f"https://img.shields.io/website?url={self.api_base_url}/health"
        }
        
        results = {}
        
        for name, url in badge_tests.items():
            try:
                response = requests.get(url, timeout=10)
                results[name] = {
                    "status": "✅ PASS" if response.status_code == 200 else "❌ FAIL",
                    "response_code": response.status_code,
                    "content_type": response.headers.get("content-type", "")
                }
            except Exception as e:
                results[name] = {
                    "status": "❌ FAIL",
                    "error": str(e)
                }
        
        return results
    
    def run_load_test(self, requests_count: int = 10) -> Dict[str, Any]:
        """Run a simple load test to generate metrics data."""
        print(f"Running load test with {requests_count} requests...")
        
        start_time = time.time()
        successful_requests = 0
        failed_requests = 0
        response_times = []
        
        for i in range(requests_count):
            try:
                response = requests.get(f"{self.api_base_url}/health", timeout=10)
                if response.status_code == 200:
                    successful_requests += 1
                else:
                    failed_requests += 1
                response_times.append(response.elapsed.total_seconds())
            except Exception:
                failed_requests += 1
            
            # Small delay between requests
            time.sleep(0.1)
        
        total_time = time.time() - start_time
        
        return {
            "total_requests": requests_count,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "total_time": total_time,
            "avg_response_time": sum(response_times) / len(response_times) if response_times else 0,
            "min_response_time": min(response_times) if response_times else 0,
            "max_response_time": max(response_times) if response_times else 0,
            "requests_per_second": requests_count / total_time if total_time > 0 else 0
        }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all monitoring tests."""
        print("🧪 Starting Monitoring Tests...")
        print("=" * 50)
        
        # Test health endpoint
        print("Testing health endpoint...")
        self.results["health"] = self.test_health_endpoint()
        
        # Test some API endpoints to generate data
        print("Testing API endpoints...")
        api_results = self.test_api_endpoints()
        
        # Test metrics endpoint
        print("Testing metrics endpoint...")
        self.results["metrics"] = self.test_metrics_endpoint()
        
        # Test status badges
        print("Testing status badges...")
        self.results["badges"] = self.test_status_badges()
        
        # Run load test
        load_test_results = self.run_load_test()
        self.results["load_test"] = load_test_results
        
        # Test metrics again after load test
        print("Testing metrics after load test...")
        self.results["metrics_after_load"] = self.test_metrics_endpoint()
        
        return self.results
    
    def print_results(self):
        """Print formatted test results."""
        print("\n" + "="*50)
        print("🏥 MONITORING TEST RESULTS")
        print("="*50)
        
        # Health endpoint results
        health = self.results.get("health", {})
        print(f"\n🏥 Health Endpoint: {health.get('status', 'Unknown')}")
        if health.get('data'):
            print(f"   Response Time: {health.get('response_time', 0):.3f}s")
            print(f"   Status: {health['data'].get('status', 'unknown')}")
            print(f"   Uptime: {health['data'].get('uptime', 0):.1f}s")
        
        # Metrics endpoint results
        metrics = self.results.get("metrics", {})
        print(f"\n📊 Metrics Endpoint: {metrics.get('status', 'Unknown')}")
        if metrics.get('data'):
            print(f"   Response Time: {metrics.get('response_time', 0):.3f}s")
            print(f"   Total Requests: {metrics['data'].get('total_requests', 0)}")
            endpoints = metrics['data'].get('endpoints', {})
            print(f"   Tracked Endpoints: {len(endpoints)}")
        
        # Load test results
        load_test = self.results.get("load_test", {})
        if load_test:
            print(f"\n⚡ Load Test Results:")
            print(f"   Total Requests: {load_test.get('total_requests', 0)}")
            print(f"   Successful: {load_test.get('successful_requests', 0)}")
            print(f"   Failed: {load_test.get('failed_requests', 0)}")
            print(f"   Avg Response Time: {load_test.get('avg_response_time', 0):.3f}s")
            print(f"   Requests/Second: {load_test.get('requests_per_second', 0):.2f}")
        
        # Badge tests
        badges = self.results.get("badges", {})
        print(f"\n🏷️ Status Badges:")
        for name, result in badges.items():
            print(f"   {name}: {result.get('status', 'Unknown')}")
        
        # Metrics comparison (before/after load test)
        metrics_before = self.results.get("metrics", {}).get("data", {})
        metrics_after = self.results.get("metrics_after_load", {}).get("data", {})
        
        if metrics_before and metrics_after:
            requests_before = metrics_before.get("total_requests", 0)
            requests_after = metrics_after.get("total_requests", 0)
            print(f"\n📈 Metrics Change:")
            print(f"   Requests Before: {requests_before}")
            print(f"   Requests After: {requests_after}")
            print(f"   New Requests: {requests_after - requests_before}")
        
        print("\n" + "="*50)
        print("✅ Test completed!")
        print("="*50)


def main():
    """Main test runner."""
    import sys
    
    # Allow custom API URL via command line
    api_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    print(f"🔍 Testing monitoring setup for: {api_url}")
    
    tester = MonitoringTester(api_url)
    
    try:
        results = tester.run_all_tests()
        tester.print_results()
        
        # Save results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"monitoring_test_results_{timestamp}.json"
        
        with open(filename, "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to: {filename}")
        
    except KeyboardInterrupt:
        print("\n❌ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")


if __name__ == "__main__":
    main()
>>>>>>> 409cb991133140d112bd4125da7948b5dacb035f

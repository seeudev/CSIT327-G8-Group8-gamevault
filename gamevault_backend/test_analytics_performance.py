"""
Performance and Load Testing for Analytics Module - Module 15
Tests API response times and concurrent request handling
"""

import time
import requests
import threading
from statistics import mean, median
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"
API_ENDPOINTS = [
    "/store/api/analytics/overview/?days=30",
    "/store/api/analytics/sales-trend/?days=30&period=daily",
    "/store/api/analytics/user-engagement/?days=30",
    "/store/api/analytics/top-games/?days=30&limit=10",
    "/store/api/analytics/category-performance/?days=30",
]

# Store results
results = {
    'response_times': [],
    'errors': [],
    'success_count': 0,
    'error_count': 0
}

def test_single_request(endpoint, session):
    """Test a single API request and measure response time"""
    start_time = time.time()
    try:
        response = session.get(BASE_URL + endpoint)
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            results['success_count'] += 1
            results['response_times'].append(elapsed)
            return True, elapsed
        else:
            results['error_count'] += 1
            results['errors'].append(f"{endpoint}: HTTP {response.status_code}")
            return False, elapsed
    except Exception as e:
        elapsed = time.time() - start_time
        results['error_count'] += 1
        results['errors'].append(f"{endpoint}: {str(e)}")
        return False, elapsed

def test_concurrent_requests(num_threads=10):
    """Test concurrent requests to analytics endpoints"""
    print(f"\nTesting with {num_threads} concurrent requests...")
    
    threads = []
    session = requests.Session()
    
    # Login first (if needed)
    # session.post(BASE_URL + '/auth/login/', data={'username': 'admin', 'password': 'admin123'})
    
    def worker():
        for endpoint in API_ENDPOINTS:
            test_single_request(endpoint, session)
    
    start_time = time.time()
    
    for _ in range(num_threads):
        thread = threading.Thread(target=worker)
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    total_time = time.time() - start_time
    return total_time

def run_performance_tests():
    """Run comprehensive performance tests"""
    
    print("=" * 70)
    print("ANALYTICS MODULE PERFORMANCE TEST - MODULE 15")
    print("=" * 70)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test 1: Single Request Performance
    print("Test 1: Single Request Response Times")
    print("-" * 70)
    
    session = requests.Session()
    
    for endpoint in API_ENDPOINTS:
        success, elapsed = test_single_request(endpoint, session)
        status = "✓" if success else "✗"
        print(f"{status} {endpoint}")
        print(f"   Response time: {elapsed*1000:.2f}ms")
    
    print()
    
    # Clear results for concurrent test
    results['response_times'].clear()
    results['errors'].clear()
    results['success_count'] = 0
    results['error_count'] = 0
    
    # Test 2: Concurrent Load (Low)
    print("Test 2: Concurrent Load Test (Low - 5 threads)")
    print("-" * 70)
    
    total_time = test_concurrent_requests(num_threads=5)
    
    if results['response_times']:
        avg_time = mean(results['response_times'])
        med_time = median(results['response_times'])
        max_time = max(results['response_times'])
        min_time = min(results['response_times'])
        
        print(f"Total requests: {results['success_count'] + results['error_count']}")
        print(f"Successful: {results['success_count']}")
        print(f"Failed: {results['error_count']}")
        print(f"Total time: {total_time:.2f}s")
        print(f"Average response time: {avg_time*1000:.2f}ms")
        print(f"Median response time: {med_time*1000:.2f}ms")
        print(f"Min response time: {min_time*1000:.2f}ms")
        print(f"Max response time: {max_time*1000:.2f}ms")
        print(f"Requests per second: {(results['success_count'] + results['error_count']) / total_time:.2f}")
        
        # Performance benchmarks
        if avg_time < 0.5:
            print("✓ EXCELLENT: Average response time < 500ms")
        elif avg_time < 1.0:
            print("✓ GOOD: Average response time < 1s")
        elif avg_time < 2.0:
            print("⚠ ACCEPTABLE: Average response time < 2s")
        else:
            print("✗ POOR: Average response time > 2s - optimization needed")
    
    print()
    
    # Clear results
    results['response_times'].clear()
    results['errors'].clear()
    results['success_count'] = 0
    results['error_count'] = 0
    
    # Test 3: Concurrent Load (Medium)
    print("Test 3: Concurrent Load Test (Medium - 10 threads)")
    print("-" * 70)
    
    total_time = test_concurrent_requests(num_threads=10)
    
    if results['response_times']:
        avg_time = mean(results['response_times'])
        med_time = median(results['response_times'])
        
        print(f"Total requests: {results['success_count'] + results['error_count']}")
        print(f"Successful: {results['success_count']}")
        print(f"Failed: {results['error_count']}")
        print(f"Total time: {total_time:.2f}s")
        print(f"Average response time: {avg_time*1000:.2f}ms")
        print(f"Median response time: {med_time*1000:.2f}ms")
        print(f"Requests per second: {(results['success_count'] + results['error_count']) / total_time:.2f}")
    
    print()
    
    # Test 4: Export Performance
    print("Test 4: Export Functionality Performance")
    print("-" * 70)
    
    export_endpoints = [
        "/store/api/analytics/export/csv/?type=sales&days=30",
        "/store/api/analytics/export/csv/?type=games&days=30",
        "/store/api/analytics/export/json/?type=overview&days=30",
    ]
    
    for endpoint in export_endpoints:
        start_time = time.time()
        try:
            response = session.get(BASE_URL + endpoint)
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                size_kb = len(response.content) / 1024
                print(f"✓ {endpoint}")
                print(f"   Response time: {elapsed*1000:.2f}ms")
                print(f"   File size: {size_kb:.2f}KB")
            else:
                print(f"✗ {endpoint}: HTTP {response.status_code}")
        except Exception as e:
            print(f"✗ {endpoint}: {str(e)}")
    
    print()
    
    # Summary
    print("=" * 70)
    print("PERFORMANCE TEST SUMMARY")
    print("=" * 70)
    
    if results['errors']:
        print(f"⚠ {len(results['errors'])} errors encountered:")
        for error in results['errors'][:5]:  # Show first 5 errors
            print(f"  - {error}")
    else:
        print("✓ All tests passed without errors")
    
    print()
    print("Recommendations:")
    print("1. Monitor response times under production load")
    print("2. Consider caching for frequently accessed analytics data")
    print("3. Implement database query optimization for large datasets")
    print("4. Use pagination for large result sets")
    print("=" * 70)

if __name__ == '__main__':
    try:
        # Check if server is running
        response = requests.get(BASE_URL, timeout=5)
        run_performance_tests()
    except requests.exceptions.ConnectionError:
        print("ERROR: Django development server is not running!")
        print(f"Please start the server first: python manage.py runserver")
    except Exception as e:
        print(f"ERROR: {str(e)}")

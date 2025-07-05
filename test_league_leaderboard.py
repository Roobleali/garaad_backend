#!/usr/bin/env python
"""
Test script to verify league leaderboard endpoint is working correctly.
"""

import requests
import json

# Production API URL
BASE_URL = "https://api.garaad.org"

def test_api_endpoints():
    """Test various API endpoints to check deployment status."""
    
    endpoints = [
        "/api/health/",
        "/api/",
        "/api/leagues/",
        "/api/leagues/leaderboard/",
        "/api/leagues/status/",
        "/api/auth/login/",
    ]
    
    print("=== Testing API Endpoints ===")
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            print(f"{endpoint}: {response.status_code}")
            
            if response.status_code == 200:
                print(f"  ✅ {endpoint} is working")
            elif response.status_code == 401:
                print(f"  🔐 {endpoint} requires authentication")
            elif response.status_code == 404:
                print(f"  ❌ {endpoint} not found")
            else:
                print(f"  ⚠️ {endpoint} returned {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"  ❌ {endpoint}: Connection error - {e}")

def test_league_leaderboard():
    """Test the league leaderboard endpoint."""
    
    print("\n=== Testing League Leaderboard ===")
    
    try:
        response = requests.get(f"{BASE_URL}/api/leagues/leaderboard/")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ Endpoint is accessible (requires authentication)")
        elif response.status_code == 404:
            print("❌ Endpoint not found - check URL configuration")
        else:
            print(f"Response: {response.text[:200]}...")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error connecting to endpoint: {e}")
        return False
    
    return True

def test_league_status():
    """Test the league status endpoint."""
    
    print("\n=== Testing League Status ===")
    
    try:
        response = requests.get(f"{BASE_URL}/api/leagues/status/")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ Status endpoint is accessible (requires authentication)")
        elif response.status_code == 404:
            print("❌ Status endpoint not found - check URL configuration")
        else:
            print(f"Response: {response.text[:200]}...")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error connecting to status endpoint: {e}")
        return False
    
    return True

def check_deployment_status():
    """Check if the deployment is working."""
    
    print("\n=== Checking Deployment Status ===")
    
    try:
        response = requests.get(f"{BASE_URL}/api/health/")
        print(f"Health check status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ API is running and accessible")
        else:
            print(f"⚠️ API returned status {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error connecting to API: {e}")
        return False
    
    return True

def provide_testing_instructions():
    """Provide detailed testing instructions."""
    
    print("\n=== Testing Instructions ===")
    print("1. **Deploy Changes**:")
    print("   - Check Railway dashboard for deployment status")
    print("   - Wait for deployment to complete")
    print("   - Verify no errors in deployment logs")
    
    print("\n2. **Run Data Fix Command**:")
    print("   - Access Railway console")
    print("   - Run: python manage.py fix_league_points")
    print("   - Verify the command completes successfully")
    
    print("\n3. **Test with Authentication**:")
    print("   # Get JWT token:")
    print("   curl -X POST https://api.garaad.org/api/auth/login/ \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{\"username\":\"your_username\",\"password\":\"your_password\"}'")
    
    print("\n   # Test leaderboard:")
    print("   curl -H 'Authorization: Bearer YOUR_JWT_TOKEN' \\")
    print("     https://api.garaad.org/api/leagues/leaderboard/")
    
    print("\n   # Test status:")
    print("   curl -H 'Authorization: Bearer YOUR_JWT_TOKEN' \\")
    print("     https://api.garaad.org/api/leagues/status/")
    
    print("\n4. **Verify Points Are Not 0**:")
    print("   - Check that 'points' field in response is > 0")
    print("   - Verify weekly_xp, monthly_xp, total_xp are correct")
    print("   - Test with different users to ensure consistency")

if __name__ == "__main__":
    print("=== League Leaderboard Test ===")
    
    # Check deployment status
    check_deployment_status()
    
    # Test all API endpoints
    test_api_endpoints()
    
    # Test specific endpoints
    test_league_leaderboard()
    test_league_status()
    
    # Provide instructions
    provide_testing_instructions() 
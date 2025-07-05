#!/usr/bin/env python3
"""
Test the generate-referral-code endpoint on production
"""
import requests
import json

def test_production_endpoint():
    """Test the generate-referral-code endpoint on production"""
    print("🔍 Testing Generate Referral Code Endpoint on Production...")
    
    base_url = "https://api.garaad.org"
    
    # Test 1: Check if endpoint exists
    print("\n1. Testing endpoint availability...")
    try:
        response = requests.post(f"{base_url}/api/auth/generate-referral-code/")
        print(f"✅ Endpoint exists (status: {response.status_code})")
        
        if response.status_code == 401:
            print("✅ Authentication required (expected)")
        elif response.status_code == 404:
            print("❌ Endpoint not found - may need to deploy")
        else:
            print(f"⚠️  Unexpected status code: {response.status_code}")
            print(f"⚠️  Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    
    # Test 2: Test with authentication (if you have a test user)
    print("\n2. Testing with authentication...")
    print("⚠️  This requires a valid JWT token")
    print("⚠️  You can test this manually with:")
    print(f"   curl -X POST {base_url}/api/auth/generate-referral-code/ \\")
    print("        -H 'Authorization: Bearer YOUR_JWT_TOKEN' \\")
    print("        -H 'Content-Type: application/json'")
    
    print("\n🎉 Production endpoint test completed!")
    print("\n📋 Next Steps:")
    print("1. Wait for deployment to complete (usually 2-5 minutes)")
    print("2. Test the endpoint with a valid JWT token")
    print("3. Verify that users without referral codes can generate them")

if __name__ == "__main__":
    test_production_endpoint() 
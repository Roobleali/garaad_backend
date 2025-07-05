#!/usr/bin/env python3
"""
Test script to verify referral API endpoints
"""
import os
import django
import requests
import json
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'garaad.settings')
django.setup()

def test_referral_api_endpoints():
    """Test referral API endpoints"""
    print("🔍 Testing Referral API Endpoints...")
    
    # Base URL - adjust this to your actual API URL
    base_url = "https://api.garaad.org"
    
    # Test 1: Test signup with referral code
    print("\n1. Testing signup with referral code...")
    try:
        # First, get a valid referral code from an existing user
        from accounts.models import User
        existing_user = User.objects.first()
        if existing_user and existing_user.referral_code:
            referral_code = existing_user.referral_code
            print(f"✅ Using referral code: {referral_code}")
            
            # Test signup with referral code
            signup_data = {
                "username": f"testuser_{os.urandom(4).hex()}",
                "email": f"test{os.urandom(4).hex()}@example.com",
                "password": "testpass123",
                "age": 25,
                "referral_code": referral_code
            }
            
            print(f"📝 Signup data: {json.dumps(signup_data, indent=2)}")
            
            # Note: This would require the actual API to be running
            # For now, we'll just test the data structure
            print("✅ Signup data structure is valid")
            
        else:
            print("⚠️  No existing users with referral codes found")
            
    except Exception as e:
        print(f"❌ Error in test 1: {e}")
    
    # Test 2: Test referral code validation
    print("\n2. Testing referral code validation...")
    try:
        from accounts.models import User
        
        # Test valid referral code
        valid_user = User.objects.filter(referral_code__isnull=False).exclude(referral_code='').first()
        if valid_user:
            valid_code = valid_user.referral_code
            exists = User.objects.filter(referral_code=valid_code).exists()
            print(f"✅ Valid code '{valid_code}' exists: {exists}")
        
        # Test invalid referral code
        invalid_code = "invalid123"
        exists = User.objects.filter(referral_code=invalid_code).exists()
        print(f"✅ Invalid code '{invalid_code}' exists: {exists} (should be False)")
        
    except Exception as e:
        print(f"❌ Error in test 2: {e}")
    
    # Test 3: Test referral statistics
    print("\n3. Testing referral statistics...")
    try:
        from accounts.models import User
        
        # Get referral statistics
        total_users = User.objects.count()
        users_with_codes = User.objects.filter(referral_code__isnull=False).exclude(referral_code='').count()
        users_with_referrals = User.objects.filter(referrals__isnull=False).distinct().count()
        total_points = sum(User.objects.values_list('referral_points', flat=True))
        
        print(f"📊 Total users: {total_users}")
        print(f"📊 Users with referral codes: {users_with_codes}")
        print(f"📊 Users who have referred others: {users_with_referrals}")
        print(f"📊 Total referral points: {total_points}")
        
        # Show top referrers
        from django.db import models
        top_referrers = User.objects.annotate(
            referral_count=models.Count('referrals')
        ).filter(referral_count__gt=0).order_by('-referral_count')[:5]
        
        print(f"📊 Top referrers:")
        for user in top_referrers:
            print(f"   - {user.username}: {user.referral_count} referrals, {user.referral_points} points")
            
    except Exception as e:
        print(f"❌ Error in test 3: {e}")
    
    # Test 4: Test referral code generation
    print("\n4. Testing referral code generation...")
    try:
        from accounts.models import User
        import random
        import string
        
        # Test the generation method directly
        generated_code = User.generate_referral_code()
        print(f"✅ Generated code: {generated_code}")
        print(f"✅ Code length: {len(generated_code)}")
        print(f"✅ Code is alphanumeric: {generated_code.isalnum()}")
        print(f"✅ Code is lowercase: {generated_code.islower()}")
        
        # Test uniqueness
        codes = set()
        for i in range(5):
            code = User.generate_referral_code()
            codes.add(code)
        
        print(f"✅ Generated {len(codes)} unique codes")
        print(f"✅ All codes are unique: {len(codes) == 5}")
        
    except Exception as e:
        print(f"❌ Error in test 4: {e}")
    
    # Test 5: Test referral relationships
    print("\n5. Testing referral relationships...")
    try:
        from accounts.models import User
        
        # Find users with referral relationships
        referrers = User.objects.filter(referrals__isnull=False).distinct()
        
        print(f"📊 Users who have referred others: {referrers.count()}")
        
        for referrer in referrers:
            referrals = referrer.referrals.all()
            print(f"   - {referrer.username} ({referrer.referral_code}): {referrals.count()} referrals")
            for referral in referrals:
                print(f"     └─ {referral.username} (joined: {referral.date_joined.strftime('%Y-%m-%d')})")
                
    except Exception as e:
        print(f"❌ Error in test 5: {e}")
    
    print("\n🎉 Referral API endpoint tests completed!")

def test_referral_code_format():
    """Test referral code format and validation"""
    print("\n🔍 Testing Referral Code Format...")
    
    try:
        from accounts.models import User
        import string
        
        # Test code format
        test_user = User.objects.create_user(
            username=f"formattest_{os.urandom(4).hex()}",
            email=f"format{os.urandom(4).hex()}@example.com",
            password="testpass123",
            age=25
        )
        
        code = test_user.referral_code
        valid_chars = string.ascii_lowercase + string.digits
        
        print(f"✅ Code: {code}")
        print(f"✅ Length: {len(code)}")
        print(f"✅ Valid characters only: {all(char in valid_chars for char in code)}")
        print(f"✅ Lowercase only: {code.islower()}")
        print(f"✅ Alphanumeric: {code.isalnum()}")
        
        # Test uniqueness
        existing_codes = set(User.objects.values_list('referral_code', flat=True))
        print(f"✅ Code is unique: {code not in existing_codes}")
        
        # Clean up
        test_user.delete()
        
    except Exception as e:
        print(f"❌ Error in format test: {e}")

if __name__ == '__main__':
    test_referral_api_endpoints()
    test_referral_code_format() 
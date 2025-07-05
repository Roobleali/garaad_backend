#!/usr/bin/env python3
"""
Test script to verify referral code generation functionality
"""
import os
import django
import random
import string
from django.conf import settings
from django.test import TestCase
from django.contrib.auth import get_user_model

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'garaad.settings')
django.setup()

User = get_user_model()

def test_referral_code_generation():
    """Test referral code generation functionality"""
    print("🔍 Testing Referral Code Generation...")
    
    # Test 1: Generate referral code for new user
    print("\n1. Testing referral code generation for new user...")
    try:
        # Create a test user
        test_user = User.objects.create_user(
            username=f'testuser_{random.randint(1000, 9999)}',
            email=f'test{random.randint(1000, 9999)}@example.com',
            password='testpass123',
            age=25
        )
        
        print(f"✅ User created: {test_user.username}")
        print(f"✅ Referral code generated: {test_user.referral_code}")
        print(f"✅ Referral code length: {len(test_user.referral_code)}")
        print(f"✅ Referral code is alphanumeric: {test_user.referral_code.isalnum()}")
        print(f"✅ Referral code is lowercase: {test_user.referral_code.islower()}")
        
        # Clean up
        test_user.delete()
        print("✅ Test user cleaned up")
        
    except Exception as e:
        print(f"❌ Error in test 1: {e}")
    
    # Test 2: Verify uniqueness
    print("\n2. Testing referral code uniqueness...")
    try:
        codes = set()
        for i in range(10):
            user = User.objects.create_user(
                username=f'uniquetest_{i}_{random.randint(1000, 9999)}',
                email=f'unique{i}_{random.randint(1000, 9999)}@example.com',
                password='testpass123',
                age=25
            )
            codes.add(user.referral_code)
            user.delete()
        
        print(f"✅ Generated {len(codes)} unique codes")
        print(f"✅ All codes are unique: {len(codes) == 10}")
        
    except Exception as e:
        print(f"❌ Error in test 2: {e}")
    
    # Test 3: Test referral code format
    print("\n3. Testing referral code format...")
    try:
        test_user = User.objects.create_user(
            username=f'formattest_{random.randint(1000, 9999)}',
            email=f'format{random.randint(1000, 9999)}@example.com',
            password='testpass123',
            age=25
        )
        
        code = test_user.referral_code
        valid_chars = string.ascii_lowercase + string.digits
        
        is_valid = all(char in valid_chars for char in code)
        print(f"✅ Code contains only valid characters: {is_valid}")
        print(f"✅ Code length is 8: {len(code) == 8}")
        print(f"✅ Code: {code}")
        
        test_user.delete()
        
    except Exception as e:
        print(f"❌ Error in test 3: {e}")
    
    # Test 4: Test referral system methods
    print("\n4. Testing referral system methods...")
    try:
        # Create referrer
        referrer = User.objects.create_user(
            username=f'referrer_{random.randint(1000, 9999)}',
            email=f'referrer{random.randint(1000, 9999)}@example.com',
            password='testpass123',
            age=30
        )
        
        # Create referred user
        referred = User.objects.create_user(
            username=f'referred_{random.randint(1000, 9999)}',
            email=f'referred{random.randint(1000, 9999)}@example.com',
            password='testpass123',
            age=25,
            referred_by=referrer
        )
        
        print(f"✅ Referrer: {referrer.username} (code: {referrer.referral_code})")
        print(f"✅ Referred: {referred.username} (referred by: {referred.referred_by.username})")
        
        # Test referral count
        referral_count = referrer.get_referral_count()
        print(f"✅ Referral count: {referral_count}")
        
        # Test referral list
        referral_list = referrer.get_referral_list()
        print(f"✅ Referral list length: {len(referral_list)}")
        
        # Test awarding points
        initial_points = referrer.referral_points
        referrer.award_referral_points(10)
        print(f"✅ Points before: {initial_points}, after: {referrer.referral_points}")
        
        # Clean up
        referred.delete()
        referrer.delete()
        
    except Exception as e:
        print(f"❌ Error in test 4: {e}")
    
    # Test 5: Test existing users without referral codes
    print("\n5. Testing existing users without referral codes...")
    try:
        # Find a user without referral code (if any)
        users_without_code = User.objects.filter(referral_code='')
        if users_without_code.exists():
            user = users_without_code.first()
            print(f"✅ Found user without referral code: {user.username}")
            
            # Generate code for existing user
            user.referral_code = User.generate_referral_code()
            user.save()
            print(f"✅ Generated referral code: {user.referral_code}")
        else:
            print("✅ All users have referral codes")
            
    except Exception as e:
        print(f"❌ Error in test 5: {e}")
    
    # Test 6: Test referral code validation
    print("\n6. Testing referral code validation...")
    try:
        # Create a user with a known referral code
        test_user = User.objects.create_user(
            username=f'validationtest_{random.randint(1000, 9999)}',
            email=f'validation{random.randint(1000, 9999)}@example.com',
            password='testpass123',
            age=25
        )
        
        valid_code = test_user.referral_code
        
        # Test if code exists
        exists = User.objects.filter(referral_code=valid_code).exists()
        print(f"✅ Valid code exists: {exists}")
        
        # Test non-existent code
        fake_code = 'fake1234'
        exists = User.objects.filter(referral_code=fake_code).exists()
        print(f"✅ Fake code exists: {exists} (should be False)")
        
        test_user.delete()
        
    except Exception as e:
        print(f"❌ Error in test 6: {e}")
    
    print("\n🎉 Referral code generation tests completed!")

def test_referral_code_statistics():
    """Test referral system statistics"""
    print("\n📊 Testing Referral System Statistics...")
    
    try:
        # Get total users
        total_users = User.objects.count()
        users_with_codes = User.objects.filter(referral_code__isnull=False).exclude(referral_code='').count()
        users_without_codes = User.objects.filter(referral_code__isnull=True).count() + User.objects.filter(referral_code='').count()
        
        print(f"📊 Total users: {total_users}")
        print(f"📊 Users with referral codes: {users_with_codes}")
        print(f"📊 Users without referral codes: {users_without_codes}")
        
        # Get referral statistics
        users_with_referrals = User.objects.filter(referrals__isnull=False).distinct().count()
        total_referral_points = sum(User.objects.values_list('referral_points', flat=True))
        
        print(f"📊 Users who have referred others: {users_with_referrals}")
        print(f"📊 Total referral points awarded: {total_referral_points}")
        
        # Show some example referral codes
        sample_users = User.objects.filter(referral_code__isnull=False).exclude(referral_code='')[:5]
        print(f"📊 Sample referral codes:")
        for user in sample_users:
            print(f"   - {user.username}: {user.referral_code}")
            
    except Exception as e:
        print(f"❌ Error in statistics test: {e}")

if __name__ == '__main__':
    test_referral_code_generation()
    test_referral_code_statistics() 
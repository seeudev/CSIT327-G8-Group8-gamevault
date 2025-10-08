#!/usr/bin/env python
"""
Test script for User Profile Management API endpoints (Module 4).
This script tests the profile editing and account deletion functionality.
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamevault_backend.settings')
django.setup()

from django.test import Client
from users.models import User
from django.contrib.auth import get_user_model

def test_profile_management():
    """Test profile editing and account deletion endpoints."""
    
    print("=" * 60)
    print("Testing User Profile Management (Module 4)")
    print("=" * 60)
    
    # Create a test client
    client = Client()
    
    # Create a test user
    User = get_user_model()
    
    # Clean up any existing test user
    User.objects.filter(username='testuser').delete()
    User.objects.filter(username='updateduser').delete()
    User.objects.filter(email='test@example.com').delete()
    User.objects.filter(email='updated@example.com').delete()
    
    test_user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )
    print(f"\n✓ Created test user: {test_user.username}")
    
    # Test 1: Login
    print("\n" + "-" * 60)
    print("Test 1: User Login")
    print("-" * 60)
    login_success = client.login(username='testuser', password='testpass123')
    print(f"Login result: {'✓ Success' if login_success else '✗ Failed'}")
    
    # Test 2: Update username and email
    print("\n" + "-" * 60)
    print("Test 2: Update Username and Email")
    print("-" * 60)
    
    response = client.put(
        f'/auth/api/users/{test_user.id}/',
        data={
            'username': 'updateduser',
            'email': 'updated@example.com'
        },
        content_type='application/json'
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200 and response.json().get('success'):
        print("✓ Profile update successful")
        # Refresh user from database
        test_user.refresh_from_db()
        print(f"  New username: {test_user.username}")
        print(f"  New email: {test_user.email}")
    else:
        print("✗ Profile update failed")
    
    # Test 3: Update password
    print("\n" + "-" * 60)
    print("Test 3: Update Password")
    print("-" * 60)
    
    response = client.put(
        f'/auth/api/users/{test_user.id}/',
        data={
            'current_password': 'testpass123',
            'new_password': 'newpass123456'
        },
        content_type='application/json'
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200 and response.json().get('success'):
        print("✓ Password update successful")
        # Test login with new password
        client.logout()
        login_success = client.login(username='updateduser', password='newpass123456')
        print(f"  Login with new password: {'✓ Success' if login_success else '✗ Failed'}")
    else:
        print("✗ Password update failed")
    
    # Test 4: Attempt to update another user's profile (should fail)
    print("\n" + "-" * 60)
    print("Test 4: Authorization Check (Update Another User's Profile)")
    print("-" * 60)
    
    # Create another user
    other_user = User.objects.create_user(
        username='otheruser',
        email='other@example.com',
        password='otherpass123'
    )
    
    response = client.put(
        f'/auth/api/users/{other_user.id}/',
        data={
            'username': 'hackeduser',
            'email': 'hacked@example.com'
        },
        content_type='application/json'
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 403:
        print("✓ Authorization check working - unauthorized update blocked")
    else:
        print("✗ Authorization check failed - should have blocked update")
    
    # Test 5: Validation - duplicate username
    print("\n" + "-" * 60)
    print("Test 5: Validation - Duplicate Username")
    print("-" * 60)
    
    response = client.put(
        f'/auth/api/users/{test_user.id}/',
        data={
            'username': 'otheruser',  # Already exists
            'email': 'updated@example.com'
        },
        content_type='application/json'
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 400 and 'errors' in response.json():
        print("✓ Duplicate username validation working")
    else:
        print("✗ Duplicate username validation failed")
    
    # Test 6: Delete account
    print("\n" + "-" * 60)
    print("Test 6: Delete Account")
    print("-" * 60)
    
    user_count_before = User.objects.count()
    print(f"User count before deletion: {user_count_before}")
    
    response = client.delete(
        f'/auth/api/users/{test_user.id}/delete/',
        content_type='application/json'
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    user_count_after = User.objects.count()
    print(f"User count after deletion: {user_count_after}")
    
    if response.status_code == 200 and response.json().get('success'):
        print("✓ Account deletion successful")
        if user_count_after == user_count_before - 1:
            print("✓ User removed from database")
    else:
        print("✗ Account deletion failed")
    
    # Test 7: Authorization check for deletion
    print("\n" + "-" * 60)
    print("Test 7: Authorization Check (Delete Another User's Account)")
    print("-" * 60)
    
    # Create new user and login
    new_user = User.objects.create_user(
        username='newuser',
        email='new@example.com',
        password='newpass123'
    )
    client.login(username='newuser', password='newpass123')
    
    response = client.delete(
        f'/auth/api/users/{other_user.id}/delete/',
        content_type='application/json'
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 403:
        print("✓ Authorization check working - unauthorized deletion blocked")
    else:
        print("✗ Authorization check failed - should have blocked deletion")
    
    # Cleanup
    print("\n" + "-" * 60)
    print("Cleanup")
    print("-" * 60)
    User.objects.filter(username__in=['testuser', 'updateduser', 'otheruser', 'newuser']).delete()
    User.objects.filter(email__in=['test@example.com', 'updated@example.com', 'other@example.com', 'new@example.com']).delete()
    print("✓ Test users cleaned up")
    
    print("\n" + "=" * 60)
    print("All Tests Completed!")
    print("=" * 60)

if __name__ == '__main__':
    test_profile_management()

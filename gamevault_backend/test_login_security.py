#!/usr/bin/env python
"""
Test script for Module 12: Invalid Login Handling & Security

Tests:
1. Failed login attempt tracking
2. Lockout after 4 failed attempts
3. Clear password field on failed login
4. Countdown timer display
5. Re-enable after lockout period
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamevault_backend.settings')
django.setup()

from users.models import LoginAttempt, User
from django.utils import timezone
from datetime import timedelta


def test_login_attempt_tracking():
    """Test that login attempts are properly tracked"""
    print("\n=== Test 1: Login Attempt Tracking ===")
    
    # Clean up any existing attempts
    LoginAttempt.objects.all().delete()
    
    # Record failed attempts
    test_username = "testuser_security"
    for i in range(3):
        LoginAttempt.record_attempt(test_username, "127.0.0.1", successful=False)
    
    # Check count
    failed_count = LoginAttempt.get_failed_attempts(test_username)
    print(f"✓ Recorded 3 failed attempts, retrieved: {failed_count}")
    assert failed_count == 3, f"Expected 3 failed attempts, got {failed_count}"
    
    # Record successful attempt
    LoginAttempt.record_attempt(test_username, "127.0.0.1", successful=True)
    
    # Clear attempts
    LoginAttempt.clear_attempts(test_username)
    failed_count = LoginAttempt.get_failed_attempts(test_username)
    print(f"✓ Cleared failed attempts, count now: {failed_count}")
    assert failed_count == 0, f"Expected 0 failed attempts after clearing, got {failed_count}"
    
    print("✅ Test 1 PASSED: Login attempt tracking works correctly\n")


def test_lockout_mechanism():
    """Test that lockout is triggered after 4 failed attempts"""
    print("=== Test 2: Lockout Mechanism ===")
    
    # Clean up
    LoginAttempt.objects.all().delete()
    
    test_username = "lockout_test"
    
    # Record 3 failed attempts - should NOT be locked
    for i in range(3):
        LoginAttempt.record_attempt(test_username, "127.0.0.1", successful=False)
    
    is_locked, remaining = LoginAttempt.is_locked_out(test_username)
    print(f"✓ After 3 attempts - Locked: {is_locked}, Remaining: {remaining}s")
    assert not is_locked, "Should not be locked after 3 attempts"
    
    # Record 4th failed attempt - should NOW be locked
    LoginAttempt.record_attempt(test_username, "127.0.0.1", successful=False)
    
    is_locked, remaining = LoginAttempt.is_locked_out(test_username)
    print(f"✓ After 4 attempts - Locked: {is_locked}, Remaining: {remaining}s")
    assert is_locked, "Should be locked after 4 attempts"
    assert remaining > 0, f"Remaining time should be > 0, got {remaining}"
    assert remaining <= 900, f"Remaining time should be <= 900s (15 min), got {remaining}"
    
    print("✅ Test 2 PASSED: Lockout mechanism works correctly\n")


def test_lockout_expiration():
    """Test that lockout expires after 15 minutes"""
    print("=== Test 3: Lockout Expiration ===")
    
    # Clean up
    LoginAttempt.objects.all().delete()
    
    test_username = "expiration_test"
    
    # Create 4 failed attempts manually with old timestamp (16 minutes ago)
    old_time = timezone.now() - timedelta(minutes=16)
    for i in range(4):
        attempt = LoginAttempt(
            username=test_username,
            ip_address="127.0.0.1",
            successful=False
        )
        # Save first, then update timestamp to bypass auto_now_add
        attempt.save()
        LoginAttempt.objects.filter(id=attempt.id).update(timestamp=old_time)
    
    # Should not be locked (attempts are old)
    is_locked, remaining = LoginAttempt.is_locked_out(test_username)
    print(f"✓ With 16-minute-old attempts - Locked: {is_locked}, Remaining: {remaining}s")
    assert not is_locked, "Should not be locked with old attempts (>15 min)"
    
    print("✅ Test 3 PASSED: Lockout expiration works correctly\n")


def test_cleanup_old_attempts():
    """Test cleanup of old login attempts"""
    print("=== Test 4: Cleanup Old Attempts ===")
    
    # Clean up
    LoginAttempt.objects.all().delete()
    
    test_username = "cleanup_test"
    
    # Create recent attempt
    LoginAttempt.record_attempt(test_username, "127.0.0.1", successful=False)
    
    # Create old attempt (31 days ago)
    old_time = timezone.now() - timedelta(days=31)
    old_attempt = LoginAttempt(
        username=f"{test_username}_old",
        ip_address="127.0.0.1",
        successful=False
    )
    old_attempt.save()
    # Update timestamp to bypass auto_now_add
    LoginAttempt.objects.filter(id=old_attempt.id).update(timestamp=old_time)
    
    total_before = LoginAttempt.objects.count()
    print(f"✓ Total attempts before cleanup: {total_before}")
    
    # Cleanup attempts older than 30 days
    deleted_count, _ = LoginAttempt.cleanup_old_attempts(days=30)
    
    total_after = LoginAttempt.objects.count()
    print(f"✓ Deleted {deleted_count} old attempt(s)")
    print(f"✓ Total attempts after cleanup: {total_after}")
    
    assert deleted_count == 1, f"Expected to delete 1 old attempt, deleted {deleted_count}"
    assert total_after == total_before - 1, "Recent attempts should remain"
    
    print("✅ Test 4 PASSED: Cleanup mechanism works correctly\n")


def test_remaining_attempts_message():
    """Test calculation of remaining attempts for user feedback"""
    print("=== Test 5: Remaining Attempts Calculation ===")
    
    # Clean up
    LoginAttempt.objects.all().delete()
    
    test_username = "remaining_test"
    max_attempts = 4
    
    for i in range(1, max_attempts + 1):
        LoginAttempt.record_attempt(test_username, "127.0.0.1", successful=False)
        failed_count = LoginAttempt.get_failed_attempts(test_username)
        remaining = max_attempts - failed_count
        
        print(f"✓ After {i} attempt(s): {remaining} remaining")
        
        if i < max_attempts:
            assert remaining > 0, f"Should have remaining attempts before lockout"
        else:
            assert remaining == 0, f"Should have 0 remaining at lockout"
    
    print("✅ Test 5 PASSED: Remaining attempts calculation works correctly\n")


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("MODULE 12: Invalid Login Handling & Security - Test Suite")
    print("=" * 60)
    
    try:
        test_login_attempt_tracking()
        test_lockout_mechanism()
        test_lockout_expiration()
        test_cleanup_old_attempts()
        test_remaining_attempts_message()
        
        print("=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nModule 12 Security Features:")
        print("✓ Failed login attempt tracking")
        print("✓ 4-attempt lockout mechanism")
        print("✓ 15-minute lockout duration")
        print("✓ Automatic lockout expiration")
        print("✓ Old attempt cleanup (30 days)")
        print("✓ Remaining attempts calculation")
        print("\nFrontend Features (manual testing required):")
        print("- Clear password field on failed login")
        print("- Display error messages with attempt count")
        print("- Show lockout timer countdown")
        print("- Disable form during lockout")
        print("- Re-enable form after lockout expires")
        print("=" * 60 + "\n")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())

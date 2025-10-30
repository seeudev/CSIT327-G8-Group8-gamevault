"""
Test script for password reset functionality (Module 9)
Run this to verify the password reset system works correctly.
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamevault_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from users.models import PasswordResetToken
from users.email_service import send_password_reset_email

User = get_user_model()

def test_password_reset():
    """Test password reset functionality"""
    print("=" * 60)
    print("Testing Password Reset System (Module 9)")
    print("=" * 60)
    
    # Step 1: Create or get test user
    print("\n[1] Creating test user...")
    test_email = "test@gamevault.com"
    test_username = "testuser"
    
    user, created = User.objects.get_or_create(
        username=test_username,
        defaults={'email': test_email}
    )
    
    if created:
        user.set_password('oldpassword123')
        user.save()
        print(f"✓ Created new test user: {test_username} ({test_email})")
    else:
        print(f"✓ Using existing test user: {test_username} ({test_email})")
    
    # Step 2: Generate password reset token
    print("\n[2] Generating password reset token...")
    token = PasswordResetToken.create_token(user)
    print(f"✓ Token created: {token.token[:20]}...")
    print(f"  - Expires at: {token.expires_at}")
    print(f"  - Is valid: {token.is_valid()}")
    
    # Step 3: Send password reset email
    print("\n[3] Sending password reset email...")
    success, message = send_password_reset_email(user, token)
    if success:
        print(f"✓ {message}")
        print("  - Check the terminal for the email output (console backend)")
    else:
        print(f"✗ {message}")
    
    # Step 4: Display reset URL
    from django.conf import settings
    reset_url = f"{settings.SITE_URL}/auth/password-reset/confirm/{token.token}/"
    print(f"\n[4] Password reset URL:")
    print(f"  {reset_url}")
    
    # Step 5: Test token validation
    print("\n[5] Testing token validation...")
    print(f"  - Token is valid: {token.is_valid()}")
    print(f"  - Token is used: {token.is_used}")
    
    # Step 6: Simulate password reset
    print("\n[6] Simulating password reset...")
    new_password = "newpassword456"
    user.set_password(new_password)
    user.save()
    token.is_used = True
    token.save()
    print(f"✓ Password updated for user: {user.username}")
    print(f"✓ Token marked as used")
    print(f"  - Token is valid: {token.is_valid()}")
    
    # Step 7: Verify password change
    print("\n[7] Verifying password change...")
    if user.check_password(new_password):
        print(f"✓ New password is correct")
    else:
        print(f"✗ Password verification failed")
    
    # Step 8: Show statistics
    print("\n[8] Password Reset Token Statistics:")
    total_tokens = PasswordResetToken.objects.filter(user=user).count()
    used_tokens = PasswordResetToken.objects.filter(user=user, is_used=True).count()
    active_tokens = PasswordResetToken.objects.filter(user=user, is_used=False).count()
    print(f"  - Total tokens: {total_tokens}")
    print(f"  - Used tokens: {used_tokens}")
    print(f"  - Active tokens: {active_tokens}")
    
    print("\n" + "=" * 60)
    print("Password Reset System Test Complete!")
    print("=" * 60)
    print("\nManual Testing Steps:")
    print("1. Visit: http://localhost:8000/auth/login/")
    print("2. Click 'Forgot Password?' link")
    print("3. Enter email: test@gamevault.com")
    print("4. Check terminal for reset link")
    print("5. Visit the reset link and set new password")
    print("6. Login with new password")
    print("=" * 60)

if __name__ == '__main__':
    test_password_reset()

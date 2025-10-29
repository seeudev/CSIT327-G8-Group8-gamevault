"""
Email service for password reset functionality.
Sends password reset links to users via email.
"""

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags


def send_password_reset_email(user, token):
    """
    Send password reset email to user with reset link.
    
    Args:
        user: User object
        token: PasswordResetToken object
        
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # Build reset URL
        reset_url = f"{settings.SITE_URL}/auth/password-reset/confirm/{token.token}/"
        
        # Render email template
        context = {
            'user': user,
            'reset_url': reset_url,
            'site_url': settings.SITE_URL,
            'expiry_hours': 1,
        }
        
        html_message = render_to_string('users/emails/password_reset.html', context)
        plain_message = strip_tags(html_message)
        
        # Send email
        send_mail(
            subject='Password Reset Request - GameVault',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return True, 'Password reset email sent successfully'
        
    except Exception as e:
        return False, f'Failed to send email: {str(e)}'

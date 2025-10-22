"""
Email service for sending game keys to customers.
Module 5: Secure Game Delivery
"""
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from .models import EmailLog


def send_game_key_email(transaction_item):
    """
    Send game key email to customer.
    
    Args:
        transaction_item: TransactionItem object containing the game purchase
        
    Returns:
        tuple: (success: bool, message: str)
    """
    user = transaction_item.transaction.user
    game = transaction_item.game
    
    # Generate key if not exists
    game_key = transaction_item.generate_game_key()
    
    # Prepare email content
    subject = f'Your Game Key for {game.title} - GameVault'
    
    # Get site URL from settings, fallback to localhost
    site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
    
    # HTML email template
    html_message = render_to_string('store/emails/game_key_email.html', {
        'user': user,
        'game': game,
        'game_key': game_key,
        'transaction_id': transaction_item.transaction.id,
        'site_url': site_url,
    })
    
    # Plain text fallback
    plain_message = f"""
Hi {user.username},

Thank you for your purchase!

Game: {game.title}
Your Game Key: {game_key}

You can download your game from: {site_url}/store/transactions/{transaction_item.transaction.id}/

Important: Keep this key safe. You'll need it to activate your game.

Best regards,
GameVault Team
    """
    
    try:
        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@gamevault.com'),
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False
        )
        
        # Update transaction item
        transaction_item.key_sent_at = timezone.now()
        transaction_item.save()
        
        # Log email
        EmailLog.objects.create(
            user=user,
            game=game,
            game_key=game_key,
            email_to=user.email,
            status='sent'
        )
        
        return True, 'Game key sent successfully!'
        
    except Exception as e:
        # Log failed email
        EmailLog.objects.create(
            user=user,
            game=game,
            game_key=game_key,
            email_to=user.email,
            status='failed'
        )
        return False, f'Failed to send email: {str(e)}'

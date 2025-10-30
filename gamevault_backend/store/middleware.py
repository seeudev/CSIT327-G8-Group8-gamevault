"""
Middleware for purchase validation and game access control.
Module 5: Secure Game Delivery
"""
from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib import messages
from django.db import connection
from django.utils.deprecation import MiddlewareMixin
from .models import Transaction


class PurchaseValidationMiddleware:
    """
    Middleware to verify user owns a game before allowing access to game-related resources.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    @staticmethod
    def verify_game_ownership(user, game_id):
        """
        Verify that a user has purchased a specific game.
        
        Args:
            user: User object
            game_id: ID of the game to verify
            
        Returns:
            tuple: (bool, Transaction or None) - ownership status and transaction if found
        """
        if not user.is_authenticated:
            return False, None
        
        # Check if user has a completed transaction containing this game
        transactions = Transaction.objects.filter(
            user=user,
            payment_status='completed'
        ).prefetch_related('items__game')
        
        for transaction in transactions:
            if transaction.items.filter(game_id=game_id).exists():
                return True, transaction
        
        return False, None


class CloseDBConnectionMiddleware(MiddlewareMixin):
    """
    Middleware to force-close database connections after each request.
    Critical for Supabase Session Pooler to prevent MaxClientsInSessionMode errors.
    
    Solution for: django.db.utils.OperationalError: MaxClientsInSessionMode
    Context: Free tier Supabase Session Pooler has limited connections (~15-30)
    """
    
    def process_response(self, request, response):
        """Close DB connection after successful response."""
        connection.close()
        return response
    
    def process_exception(self, request, exception):
        """Close DB connection even if exception occurs."""
        connection.close()
        return None

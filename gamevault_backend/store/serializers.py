"""Lightweight serializers/helpers for GameVault store.

This module intentionally avoids Django REST Framework to keep the
project aligned with the simplicity-first philosophy. Complex
serialization is done inline in views when necessary.
"""
from .models import Wishlist


def wishlist_to_dict(wishlist_item):
    """Convert a Wishlist model instance to a plain dict for JSON responses."""
    game = wishlist_item.game
    return {
        'id': wishlist_item.id,
        'game_id': game.id,
        'game_title': game.title,
        'game_thumbnail': getattr(game, 'screenshot_url', None) or None,
        'game_price': float(game.price) if game.price is not None else None,
        'added_at': wishlist_item.added_at.isoformat() if wishlist_item.added_at else None,
    }
 


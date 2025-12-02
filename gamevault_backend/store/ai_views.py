"""
Module 17: AI Market Analysis API Views
Provides endpoints for hybrid consensus analysis.
"""
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
import logging

from .models import Game
from .ai_market_analysis import get_game_consensus, refresh_game_analysis

logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
def api_game_consensus(request, game_id):
    """
    5.3 Frontend & Attribution UI
    Get AI hybrid consensus analysis for a game.
    
    Response: {
        'success': bool,
        'data': {
            'local_sentiment': float,
            'global_sentiment': float,
            'divergence': float,
            'verdict': str,
            'sources': [{source_name, url, sentiment, excerpt}],
            'local_review_count': int,
            'local_avg_rating': float,
            'exists_externally': bool
        }
    }
    """
    try:
        game = get_object_or_404(Game, id=game_id)
        
        # Get force_refresh parameter
        force_refresh = request.GET.get('refresh', 'false').lower() == 'true'
        
        # Get consensus analysis
        consensus = get_game_consensus(game, force_refresh=force_refresh)
        
        return JsonResponse({
            'success': True,
            'data': {
                'game_title': game.title,
                'local_sentiment': consensus['local_sentiment'],
                'global_sentiment': consensus['global_sentiment'],
                'divergence': consensus['divergence'],
                'verdict': consensus['verdict'],
                'sources': consensus['sources'],
                'local_review_count': consensus['local_review_count'],
                'local_avg_rating': consensus.get('local_avg_rating', 0),
                'exists_externally': consensus.get('exists_externally', True),
                'last_updated': game.last_external_sync.isoformat() if game.last_external_sync else None
            }
        })
        
    except Exception as e:
        logger.error(f"Error fetching game consensus: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def api_refresh_consensus(request, game_id):
    """
    Admin/user action to force refresh consensus analysis.
    Only admins can force external refresh (costs API credits).
    """
    try:
        game = get_object_or_404(Game, id=game_id)
        
        # Only admins can force external refresh
        if not request.user.is_admin:
            return JsonResponse({
                'success': False,
                'error': 'Only administrators can force refresh external data'
            }, status=403)
        
        # Force refresh
        consensus = refresh_game_analysis(game_id)
        
        if consensus:
            return JsonResponse({
                'success': True,
                'message': 'Consensus analysis refreshed successfully',
                'data': {
                    'local_sentiment': consensus['local_sentiment'],
                    'global_sentiment': consensus['global_sentiment'],
                    'divergence': consensus['divergence'],
                    'verdict': consensus['verdict']
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Failed to refresh analysis'
            }, status=500)
            
    except Exception as e:
        logger.error(f"Error refreshing consensus: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

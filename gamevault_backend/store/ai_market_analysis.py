"""
Module 17: AI Hybrid Market Analysis Service
Uses Gemini API with Search Grounding to analyze game sentiment from external sources.
"""
import os
import json
import logging
import requests
from datetime import datetime, timedelta
from django.utils import timezone
from decimal import Decimal
from typing import Optional, Dict, List, Tuple

logger = logging.getLogger(__name__)

# Configure Gemini API
# Note: Using REST API directly for better compatibility
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY', '')
# Using gemini-2.5-flash for fast, efficient responses
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

# Mock mode for development/testing (set USE_MOCK_AI=true to enable)
USE_MOCK_AI = os.getenv('USE_MOCK_AI', '').lower() in ('true', '1', 'yes')

# Cache durations
EXTERNAL_CACHE_DAYS = 7  # External data refreshes weekly
LOCAL_CACHE_DAYS = 1     # Local analysis refreshes daily


class AIMarketAnalyzer:
    """
    AI-powered market analysis using Gemini API with search grounding.
    Synthesizes local reviews with external web data.
    """
    
    def __init__(self):
        self.api_key = GOOGLE_API_KEY
        if self.api_key:
            logger.info("Gemini API key configured (using REST API)")
        else:
            logger.warning("No Gemini API key found")
    
    def _call_gemini_api(self, prompt: str, temperature: float = 0.7) -> Optional[str]:
        """
        Call Gemini API directly using REST endpoint for better compatibility.
        """
        # Mock mode for development/testing
        if USE_MOCK_AI:
            if "Does the game" in prompt and "exist" in prompt:
                return '{"exists": true, "sources_found": ["https://en.wikipedia.org/wiki/Game", "https://www.ign.com/games"]}'
            elif "sentiment" in prompt.lower():
                return '{"sentiment_score": 78, "sources": [{"url": "https://www.ign.com/review", "title": "IGN Review", "sentiment": 80}, {"url": "https://www.gamespot.com/review", "title": "GameSpot Review", "sentiment": 76}], "summary": "Generally positive reception from critics and players"}'
            elif "verdict" in prompt.lower() or "analysis" in prompt.lower():
                return "Based on comprehensive analysis of both local user reviews and external gaming sources, this title demonstrates strong overall sentiment. The game has received positive feedback across multiple platforms."
        
        if not self.api_key:
            logger.warning("No API key found, returning None")
            return None
        
        try:
            url = f"{GEMINI_API_URL}?key={self.api_key}"
            headers = {"Content-Type": "application/json"}
            data = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": temperature,
                    "topP": 0.8,
                    "topK": 40
                },
                # Enable Google Search for real-time web data
                "tools": [{
                    "google_search": {}
                }]
            }
            
            # Increase timeout to 25 seconds for sentiment analysis (more complex queries)
            response = requests.post(url, headers=headers, json=data, timeout=25)
            
            # Check status code
            if response.status_code != 200:
                logger.error(f"API returned status {response.status_code}: {response.text}")
                return None
            
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                text = result['candidates'][0]['content']['parts'][0]['text']
                # Remove markdown code block markers if present
                if text.startswith('```json'):
                    text = text.replace('```json', '').replace('```', '').strip()
                elif text.startswith('```'):
                    text = text.replace('```', '').strip()
                
                # Validate we got something back
                if not text or len(text) < 5:
                    logger.warning(f"API returned empty/invalid response: '{text}'")
                    return None
                    
                return text
            else:
                logger.error(f"Unexpected API response structure: {result}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error(f"Gemini API request timed out after 25 seconds")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Gemini API request failed: {e}")
            return None
        except (KeyError, IndexError) as e:
            logger.error(f"Failed to parse Gemini API response: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error calling Gemini API: {e}")
            return None
    
    def check_game_existence(self, game_title):
        """
        5.1.3 Existence Verification: Check if game exists in external sources.
        Returns: (exists: bool, sources: list)
        """
        if not self.api_key and not USE_MOCK_AI:
            return True, []  # Assume exists if API unavailable
        
        try:
            # Escape game title for JSON safety
            safe_title = game_title.replace('"', '\\"')
            prompt = f"""Check if this video game exists on IGN, Metacritic, or Steam: {safe_title}

Respond ONLY with JSON: {{"exists": true, "sources_found": ["IGN", "Metacritic"]}}"""
            
            response_text = self._call_gemini_api(prompt, temperature=0.1)
            if not response_text:
                return True, []
            
            result = json.loads(response_text)
            return result.get('exists', False), result.get('sources_found', [])
            
        except Exception as e:
            logger.error(f"Existence verification failed for {game_title}: {e}")
            return True, []  # Fail open - assume exists
    
    def fetch_external_sentiment(self, game_title):
        """
        5.1.1 & 5.1.2: Fetch real-time external reviews with source URIs.
        Uses Gemini API to retrieve actual web data.
        
        Returns: {
            'sentiment_score': float (0-100),
            'sources': [{source_name, url, sentiment, excerpt}],
            'exists': bool
        }
        """
        if not self.api_key and not USE_MOCK_AI:
            logger.warning("Gemini API not configured or unavailable")
            return {
                'sentiment_score': None,
                'sources': [],
                'exists': False,
                'verdict': 'AI analysis unavailable. Please configure a valid GOOGLE_API_KEY.'
            }
        
        # First check if game exists
        exists, found_sources = self.check_game_existence(game_title)
        
        if not exists:
            logger.info(f"Game '{game_title}' does not exist externally")
            return {
                'sentiment_score': None,
                'sources': [],
                'exists': False,
                'verdict': f"No external information found for '{game_title}'. This game may be exclusive to this platform."
            }
        
        try:
            # Escape the game title for JSON safety
            safe_title = game_title.replace('"', '\\"')
            
            prompt = f"""Search the web NOW for reviews of: {safe_title}

Check these sites for CURRENT reviews (game may have released recently):
- IGN.com
- Metacritic.com  
- store.steampowered.com

Return ONLY this JSON format (no other text):
{{"overall_sentiment_score": 85, "sources": [{{"source_name": "IGN", "url": "https://ign.com/reviews/...", "sentiment": "Positive", "score": 90}}], "summary": "Brief summary"}}

If absolutely no reviews found:
{{"overall_sentiment_score": null, "sources": [], "summary": "No reviews"}}"""
            
            response_text = self._call_gemini_api(prompt, temperature=0.3)
            if not response_text:
                logger.warning(f"No response from API for {game_title}")
                return None
            
            # Parse JSON response
            try:
                result = json.loads(response_text)
            except json.JSONDecodeError as e:
                logger.error(f"JSON parse error for {game_title}: API returned text instead of JSON.")
                # API returned text instead of JSON - treat as no data available
                return {
                    'sentiment_score': None,
                    'sources': [],
                    'exists': False,
                    'web_summary': 'External review data not yet available for this game.'
                }
            
            # Validate sources have URLs
            validated_sources = []
            for source in result.get('sources', []):
                if source.get('url') and source['url'].startswith('http'):
                    validated_sources.append({
                        'source_name': source.get('source_name', 'Unknown'),
                        'url': source.get('url'),
                        'sentiment': source.get('sentiment', 'Mixed'),
                        'excerpt': source.get('excerpt', ''),
                        'score': source.get('score', 50)
                    })
            
            # Check if game actually has review data
            sentiment_score = result.get('overall_sentiment_score')
            has_data = sentiment_score is not None or len(validated_sources) > 0
            
            return {
                'sentiment_score': sentiment_score,  # Keep None if no reviews
                'sources': validated_sources,
                'exists': has_data,  # Only True if we have real data
                'web_summary': result.get('summary', '')
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch external sentiment for {game_title}: {e}")
            return None
    
    def calculate_local_sentiment(self, game):
        """
        Calculate local sentiment from internal reviews.
        Returns: (local_score: float 0-100, review_count: int, avg_rating: float)
        """
        from .models import Review
        
        reviews = Review.objects.filter(game=game)
        review_count = reviews.count()
        
        if review_count == 0:
            return None, 0, 0
        
        # Calculate average rating (1-5 stars)
        avg_rating = sum(r.rating for r in reviews) / review_count
        
        # Convert to 0-100 scale
        local_score = (avg_rating / 5.0) * 100
        
        return local_score, review_count, avg_rating
    
    def generate_hybrid_consensus(self, game, force_refresh=False):
        """
        5.1.2: Synthesize local data vs. web data to generate consensus.
        
        Returns: {
            'local_sentiment': float,
            'global_sentiment': float,
            'divergence': float,
            'verdict': str,
            'sources': list,
            'local_review_count': int,
            'needs_update': bool
        }
        """
        from .models import Review
        
        now = timezone.now()
        
        # Check cache freshness
        needs_external_update = (
            force_refresh or
            not game.last_external_sync or
            now - game.last_external_sync > timedelta(days=EXTERNAL_CACHE_DAYS)
        )
        
        needs_local_update = (
            force_refresh or
            not game.last_local_sync or
            now - game.last_local_sync > timedelta(days=LOCAL_CACHE_DAYS)
        )
        
        # Calculate local sentiment
        if needs_local_update:
            local_score, local_count, avg_rating = self.calculate_local_sentiment(game)
            if local_score is not None:
                game.local_rating = local_score
                game.last_local_sync = now
        else:
            local_score = game.local_rating
            local_count = Review.objects.filter(game=game).count()
            avg_rating = (local_score / 100 * 5) if local_score else 0
        
        # Fetch external sentiment
        if needs_external_update:
            external_data = self.fetch_external_sentiment(game.title)
            
            if external_data and external_data['exists']:
                game.global_sentiment_score = external_data['sentiment_score']
                game.external_sources = external_data['sources']
                game.game_exists_externally = True
                game.last_external_sync = now
            elif external_data and not external_data['exists']:
                game.global_sentiment_score = None
                game.external_sources = []
                game.game_exists_externally = False
                game.last_external_sync = now
            elif external_data is None:
                # API timeout or error - don't make up data
                logger.warning(f"External API unavailable for {game.title}, no external data")
                # Don't update last_external_sync so we retry later
                # Keep values as None/empty (don't fabricate sentiment scores)
                if game.global_sentiment_score is None:
                    game.global_sentiment_score = None  # Keep None, no fake data
                if game.external_sources is None:
                    game.external_sources = []
                if game.game_exists_externally is None:
                    game.game_exists_externally = False
        
        global_score = game.global_sentiment_score
        
        # Generate AI verdict
        verdict = self._generate_verdict_text(
            game.title,
            local_score,
            global_score,
            local_count,
            game.external_sources,
            game.game_exists_externally
        )
        
        game.ai_verdict = verdict
        game.save()
        
        # Calculate divergence
        divergence = None
        if local_score is not None and global_score is not None:
            divergence = abs(local_score - global_score)
        
        return {
            'local_sentiment': local_score,
            'global_sentiment': global_score,
            'divergence': divergence,
            'verdict': verdict,
            'sources': game.external_sources or [],
            'local_review_count': local_count,
            'local_avg_rating': avg_rating,
            'exists_externally': game.game_exists_externally,
            'needs_update': False
        }
    
    def _generate_verdict_text(self, game_title, local_score, global_score, 
                                 local_count, sources, exists_externally):
        """
        Generate human-readable AI verdict explaining sentiment divergence.
        """
        if not exists_externally:
            return (
                f"{game_title} is not found in major external gaming databases. "
                f"This appears to be an exclusive or indie title available only on this platform. "
                f"{'Local buyers have rated it ' + f'{local_score:.1f}/100 based on {local_count} reviews.' if local_score else 'No local reviews yet.'}"
            )
        
        if local_score is None and global_score is None:
            return f"Insufficient data to generate consensus for {game_title}."
        
        if local_score is None:
            return (
                f"Based on {len(sources)} external sources, {game_title} has a web sentiment score of {global_score:.1f}/100. "
                f"No local reviews yet - be the first to share your experience!"
            )
        
        if global_score is None:
            return (
                f"Local buyers rate {game_title} at {local_score:.1f}/100 ({local_count} reviews). "
                f"External data unavailable for comparison."
            )
        
        # Both scores available - analyze divergence
        divergence = abs(local_score - global_score)
        
        if divergence < 10:
            alignment = "strong consensus"
            explanation = "Local and global opinions align closely."
        elif divergence < 20:
            alignment = "general agreement"
            explanation = "Minor variance between local buyers and web critics."
        elif divergence < 30:
            alignment = "moderate divergence"
            explanation = "Notable difference in opinions between local buyers and web critics."
        else:
            alignment = "significant divergence"
            explanation = "Local buyers have a markedly different opinion than web critics."
        
        # Determine which is higher
        if local_score > global_score:
            sentiment_diff = "Local buyers rate this game MORE FAVORABLY than web critics"
        elif local_score < global_score:
            sentiment_diff = "Web critics rate this game MORE FAVORABLY than local buyers"
        else:
            sentiment_diff = "Local and web sentiments are perfectly aligned"
        
        verdict = (
            f"**{alignment.upper()}**: {game_title} scores {local_score:.1f}/100 locally "
            f"({local_count} reviews) vs. {global_score:.1f}/100 globally "
            f"({len(sources)} sources). {sentiment_diff}. {explanation}"
        )
        
        return verdict


# Singleton instance
analyzer = AIMarketAnalyzer()


def get_game_consensus(game, force_refresh=False):
    """
    Public API: Get hybrid consensus analysis for a game.
    """
    return analyzer.generate_hybrid_consensus(game, force_refresh)


def refresh_game_analysis(game_id):
    """
    Force refresh analysis for a specific game.
    Useful for admin actions or scheduled tasks.
    """
    from .models import Game
    
    try:
        game = Game.objects.get(id=game_id)
        return analyzer.generate_hybrid_consensus(game, force_refresh=True)
    except Game.DoesNotExist:
        return None

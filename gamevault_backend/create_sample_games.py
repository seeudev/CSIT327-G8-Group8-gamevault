"""
Script to create sample games for testing.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamevault_backend.settings')
django.setup()

from store.models import Game
from decimal import Decimal

# Sample games data
sample_games = [
    {
        'title': 'Space Adventure',
        'description': 'An exciting space exploration game where you travel across galaxies, discover new planets, and encounter alien civilizations.',
        'category': 'Action',
        'price': Decimal('29.99'),
        'screenshot_url': 'https://via.placeholder.com/400x300/0088cc/ffffff?text=Space+Adventure',
        'file_url': 'https://example.com/downloads/space-adventure.zip'
    },
    {
        'title': 'Fantasy Quest',
        'description': 'Embark on an epic fantasy adventure filled with magic, dragons, and legendary heroes in this immersive RPG experience.',
        'category': 'RPG',
        'price': Decimal('39.99'),
        'screenshot_url': 'https://via.placeholder.com/400x300/cc0088/ffffff?text=Fantasy+Quest',
        'file_url': 'https://example.com/downloads/fantasy-quest.zip'
    },
    {
        'title': 'Racing Rivals',
        'description': 'High-speed racing action with realistic physics and stunning graphics. Compete against players worldwide.',
        'category': 'Racing',
        'price': Decimal('24.99'),
        'screenshot_url': 'https://via.placeholder.com/400x300/cc8800/ffffff?text=Racing+Rivals',
        'file_url': 'https://example.com/downloads/racing-rivals.zip'
    },
    {
        'title': 'Puzzle Master',
        'description': 'Challenge your mind with hundreds of unique puzzles. Perfect for casual gamers who love a good brain teaser.',
        'category': 'Puzzle',
        'price': Decimal('9.99'),
        'screenshot_url': 'https://via.placeholder.com/400x300/00cc88/ffffff?text=Puzzle+Master',
        'file_url': 'https://example.com/downloads/puzzle-master.zip'
    },
    {
        'title': 'Strategy Empire',
        'description': 'Build your empire from scratch, manage resources, command armies, and conquer the world in this deep strategy game.',
        'category': 'Strategy',
        'price': Decimal('44.99'),
        'screenshot_url': 'https://via.placeholder.com/400x300/8800cc/ffffff?text=Strategy+Empire',
        'file_url': 'https://example.com/downloads/strategy-empire.zip'
    },
]

# Create games if they don't exist
created_count = 0
for game_data in sample_games:
    if not Game.objects.filter(title=game_data['title']).exists():
        Game.objects.create(**game_data)
        created_count += 1
        print(f"Created: {game_data['title']}")
    else:
        print(f"Already exists: {game_data['title']}")

print(f"\n{created_count} new games created!")
print(f"Total games in database: {Game.objects.count()}")

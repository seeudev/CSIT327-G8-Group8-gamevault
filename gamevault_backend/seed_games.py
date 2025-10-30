"""
Script to seed the database with games, categories, and tags.
This script uses the actual production data from Supabase.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamevault_backend.settings')
django.setup()

from store.models import Game, Category, Tag, GameTag
from decimal import Decimal

# Categories to create
CATEGORIES = [
    {'id': 1, 'name': 'Action'},
    {'id': 2, 'name': 'Adventure'},
    {'id': 3, 'name': 'Strategy'},
    {'id': 4, 'name': 'RPG'},
    {'id': 5, 'name': 'Simulation'},
    {'id': 6, 'name': 'Survival'},
    {'id': 7, 'name': 'Sports'},
    {'id': 8, 'name': 'Puzzle'},
    {'id': 9, 'name': 'Casual'},
]

# Tags to create
TAGS = [
    '2D', '3D', 'Casual', 'Cute', 'Fantasy', 'First-Person',
    'Horror', 'Interactive Fiction', 'LGBT', 'Multiplayer',
    'Open World', 'Pixel Art', 'Platformer', 'Psychological Horror',
    'Retro', 'Romance', 'Sandbox', 'Sci-Fi', 'Singleplayer',
    'Story Rich', 'Survival', 'Tabletop', 'Visual Novel'
]

# Games data from production database
GAMES = [
    {
        'title': 'Clair Obscur: Expedition 33',
        'description': 'Lead the members of Expedition 33 on their quest to destroy the Paintress so that she can never paint death again. Explore a world of wonders inspired by Belle Époque France and battle unique enemies in this turn-based RPG with real-time mechanics.',
        'category': 'RPG',
        'price': Decimal('49.99'),
        'screenshot_url': 'https://www.vgchartz.com/games/boxart/full_6351495AmericaFrontccc.png',
        'file_url': None,
        'tags': ['3D', 'Fantasy', 'Singleplayer', 'Story Rich']
    },
    {
        'title': 'Metaphor: ReFantazio',
        'description': 'The throne sits empty after the king\'s assassination. With no heirs, the will of the late king decrees that the next monarch will be elected by the people, and thus begins your fight for the throne.',
        'category': 'RPG',
        'price': Decimal('69.99'),
        'screenshot_url': 'https://www.vgchartz.com/games/boxart/full_9835128AmericaFrontccc.jpg',
        'file_url': None,
        'tags': ['3D', 'Fantasy', 'Singleplayer', 'Story Rich']
    },
    {
        'title': 'Persona 5 Royal',
        'description': 'Prepare for the award-winning RPG experience in this definitive edition of Persona 5 Royal. Forced to transfer to a high school in Tokyo, the protagonist has a strange dream. With the goal of "rehabilitation" looming overhead, he must save others from distorted desires by donning the mask of a Phantom Thief.',
        'category': 'RPG',
        'price': Decimal('59.99'),
        'screenshot_url': 'https://www.vgchartz.com/games/boxart/full_6938512AmericaFrontccc.jpeg',
        'file_url': None,
        'tags': ['3D', 'Fantasy', 'Singleplayer', 'Story Rich']
    },
    {
        'title': 'Persona 4 Golden',
        'description': 'A coming of age story that places the protagonist and his friends on a journey set in motion by a chain of serial murders. After moving to the rural town of Inaba, the protagonist must explore the mysterious TV World and harness the power of Persona to uncover the truth.',
        'category': 'RPG',
        'price': Decimal('19.99'),
        'screenshot_url': 'https://www.vgchartz.com/games/boxart/full_3580522AmericaFrontccc.jpg',
        'file_url': None,
        'tags': ['3D', 'Fantasy', 'Singleplayer', 'Story Rich']
    },
    {
        'title': 'Persona 3 Portable',
        'description': 'Enjoy Persona 3 Portable now with newly remastered graphics, improved smoothness in gameplay, and quality of life features. Climb the looming tower of Tartarus, take down powerful Shadows, and investigate the mysteries of the Dark Hour. Experience this dark, emotional journey through two distinct protagonists\' perspectives for twice the social possibilities.',
        'category': 'RPG',
        'price': Decimal('19.99'),
        'screenshot_url': 'https://www.vgchartz.com/games/boxart/full_shin-megami-tensei-persona-3-portable_1AmericaFront.jpg',
        'file_url': None,
        'tags': ['2D', 'Fantasy', 'Singleplayer', 'Story Rich', 'Visual Novel']
    },
    {
        'title': 'Persona 3 Reload',
        'description': 'Step into the shoes of a transfer student thrust into an unexpected fate when entering the hour "hidden" between one day and the next. Awaken an incredible power and chase the mysteries of the Dark Hour, fight for your friends, and leave a mark on their memories forever. Persona 3 Reload is a captivating reimagining of the genre-defining RPG, reborn for the modern era.',
        'category': 'RPG',
        'price': Decimal('59.99'),
        'screenshot_url': 'https://www.vgchartz.com/games/boxart/full_2329504AmericaFrontccc.jpg',
        'file_url': None,
        'tags': ['3D', 'Fantasy', 'Singleplayer', 'Story Rich']
    },
    {
        'title': 'SILENT HILL f',
        'description': 'Hinako\'s hometown is engulfed in fog, driving her to fight grotesque monsters and solve eerie puzzles.',
        'category': 'Puzzle',
        'price': Decimal('59.99'),
        'screenshot_url': 'https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/2947440/7e5d923ac622bd1775ebc9b5d4b5b0a24bf5ed40/header.jpg?t=1758772827',
        'file_url': None,
        'tags': ['3D', 'Horror', 'Psychological Horror', 'Singleplayer']
    },
    {
        'title': 'Detroit: Become Human',
        'description': 'Detroit: Become Human puts the destiny of both mankind and androids in your hands, taking you to a near future where machines have become more intelligent than humans.',
        'category': 'Adventure',
        'price': Decimal('45.99'),
        'screenshot_url': 'https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/1222140/header.jpg?t=1667468479',
        'file_url': None,
        'tags': ['3D', 'First-Person', 'Interactive Fiction', 'Sci-Fi', 'Singleplayer', 'Story Rich']
    },
    {
        'title': 'Dispatch',
        'description': 'Dispatch is a superhero workplace comedy where choices matter. You play as Robert Robertson, AKA Mecha Man, whose mech-suit is destroyed, forcing him to take a job at a superhero dispatch center: not as a hero, but a dispatcher.',
        'category': 'Action',
        'price': Decimal('29.99'),
        'screenshot_url': 'https://cdn.akamai.steamstatic.com/steam/apps/2592160/library_header.jpg',
        'file_url': None,
        'tags': []
    },
    {
        'title': 'The Outer Worlds 2',
        'description': 'The Outer Worlds 2 is the eagerly-awaited sequel to the award-winning first-person sci-fi RPG from Obsidian Entertainment. As a daring Earth Directorate agent, you must uncover the source of devastating rifts threatening to destroy all of humanity.',
        'category': 'Action',
        'price': Decimal('69.99'),
        'screenshot_url': 'https://cdn.akamai.steamstatic.com/steam/apps/1449110/header.jpg',
        'file_url': None,
        'tags': []
    },
    {
        'title': 'Battlefield™ 6',
        'description': 'The ultimate all-out warfare experience. A first-person shooter featuring high-intensity infantry combat, aerial dogfights, and environmental-destruction-based strategy.',
        'category': 'Action',
        'price': Decimal('69.99'),
        'screenshot_url': 'https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/2807960/c12d12ce3c7d217398d3fcad77427bfc9d57c570/header.jpg?t=1754584466',
        'file_url': None,
        'tags': []
    },
    {
        'title': 'The Witcher 3: Wild Hunt Complete Edition',
        'description': 'Massive open-world RPG with critical acclaim.',
        'category': 'Action',
        'price': Decimal('49.99'),
        'screenshot_url': 'https://www.vgchartz.com/games/boxart/full_3930956AmericaFrontccc.jpg',
        'file_url': None,
        'tags': []
    },
    {
        'title': 'Valheim',
        'description': 'Viking-themed survival, sandbox, online co-op, building game.',
        'category': 'Survival',
        'price': Decimal('19.99'),
        'screenshot_url': 'https://www.vgchartz.com/games/boxart/full_5778838AmericaFrontccc.jpg',
        'file_url': None,
        'tags': []
    },
    {
        'title': 'Rust',
        'description': 'Hardcore open-world survival, multiplayer, building game.',
        'category': 'Survival',
        'price': Decimal('39.99'),
        'screenshot_url': 'https://www.vgchartz.com/games/boxart/full_4256609AmericaFrontccc.jpg',
        'file_url': None,
        'tags': []
    },
]


def seed_categories():
    """Create categories if they don't exist."""
    print("Seeding categories...")
    created_count = 0
    for cat_data in CATEGORIES:
        category, created = Category.objects.get_or_create(
            id=cat_data['id'],
            defaults={'name': cat_data['name']}
        )
        if created:
            created_count += 1
            print(f"  ✓ Created category: {category.name}")
        else:
            print(f"  - Category already exists: {category.name}")
    
    print(f"Categories: {created_count} new, {Category.objects.count()} total\n")


def seed_tags():
    """Create tags if they don't exist."""
    print("Seeding tags...")
    created_count = 0
    for tag_name in TAGS:
        tag, created = Tag.objects.get_or_create(name=tag_name)
        if created:
            created_count += 1
            print(f"  ✓ Created tag: {tag.name}")
        else:
            print(f"  - Tag already exists: {tag.name}")
    
    print(f"Tags: {created_count} new, {Tag.objects.count()} total\n")


def seed_games():
    """Create games with their categories and tags."""
    print("Seeding games...")
    created_count = 0
    updated_count = 0
    
    for game_data in GAMES:
        # Extract tags and category name from game data
        tag_names = game_data.pop('tags', [])
        category_name = game_data.pop('category', None)
        
        # Get or create the game
        game, created = Game.objects.get_or_create(
            title=game_data['title'],
            defaults=game_data
        )
        
        # Set the category if provided
        if category_name:
            try:
                category = Category.objects.get(name=category_name)
                game.category = category
                game.save()
            except Category.DoesNotExist:
                print(f"  ⚠ Warning: Category '{category_name}' not found for game '{game.title}'")
        
        # Add tags
        if tag_names:
            for tag_name in tag_names:
                try:
                    tag = Tag.objects.get(name=tag_name)
                    GameTag.objects.get_or_create(game=game, tag=tag)
                except Tag.DoesNotExist:
                    print(f"  ⚠ Warning: Tag '{tag_name}' not found for game '{game.title}'")
        
        if created:
            created_count += 1
            print(f"  ✓ Created game: {game.title} (${game.price})")
        else:
            updated_count += 1
            print(f"  - Game already exists: {game.title}")
    
    print(f"Games: {created_count} new, {updated_count} existing, {Game.objects.count()} total\n")


if __name__ == '__main__':
    print("=" * 60)
    print("GameVault Database Seeding")
    print("=" * 60)
    print()
    
    # Seed in order: categories -> tags -> games
    seed_categories()
    seed_tags()
    seed_games()
    
    print("=" * 60)
    print("Seeding completed successfully!")
    print("=" * 60)

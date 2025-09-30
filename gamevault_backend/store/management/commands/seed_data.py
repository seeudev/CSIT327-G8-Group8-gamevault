from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from store.models import Game, GameKey
from datetime import date
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with sample games and game keys for testing'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')

        # Sample games data
        games_data = [
            {
                'title': 'Cyberpunk 2077',
                'description': 'An open-world action-adventure RPG set in Night City.',
                'price': 59.99,
                'platform': 'PC',
                'genre': 'RPG',
                'publisher': 'CD Projekt Red',
                'release_date': date(2020, 12, 10),
                'cover_image_url': 'https://example.com/cyberpunk.jpg',
                'stock_count': 5
            },
            {
                'title': 'The Witcher 3: Wild Hunt',
                'description': 'An epic fantasy RPG with a rich story and vast open world.',
                'price': 39.99,
                'platform': 'PC',
                'genre': 'RPG',
                'publisher': 'CD Projekt Red',
                'release_date': date(2015, 5, 19),
                'cover_image_url': 'https://example.com/witcher3.jpg',
                'stock_count': 10
            },
            {
                'title': 'God of War',
                'description': 'Follow Kratos and Atreus on their journey through Norse mythology.',
                'price': 49.99,
                'platform': 'PS5',
                'genre': 'Action',
                'publisher': 'Sony Interactive Entertainment',
                'release_date': date(2018, 4, 20),
                'cover_image_url': 'https://example.com/gow.jpg',
                'stock_count': 8
            },
            {
                'title': 'Halo Infinite',
                'description': 'The legendary Halo series continues with Master Chief.',
                'price': 59.99,
                'platform': 'XBOX',
                'genre': 'FPS',
                'publisher': 'Xbox Game Studios',
                'release_date': date(2021, 12, 8),
                'cover_image_url': 'https://example.com/halo.jpg',
                'stock_count': 15
            },
            {
                'title': 'The Legend of Zelda: Breath of the Wild',
                'description': 'Explore Hyrule in this revolutionary open-world adventure.',
                'price': 59.99,
                'platform': 'SWITCH',
                'genre': 'Adventure',
                'publisher': 'Nintendo',
                'release_date': date(2017, 3, 3),
                'cover_image_url': 'https://example.com/zelda.jpg',
                'stock_count': 12
            },
            {
                'title': 'Red Dead Redemption 2',
                'description': 'An epic tale of life in America at the dawn of the modern age.',
                'price': 54.99,
                'platform': 'PC',
                'genre': 'Action',
                'publisher': 'Rockstar Games',
                'release_date': date(2018, 10, 26),
                'cover_image_url': 'https://example.com/rdr2.jpg',
                'stock_count': 7
            },
            {
                'title': 'Elden Ring',
                'description': 'A dark fantasy action RPG from FromSoftware and George R.R. Martin.',
                'price': 59.99,
                'platform': 'PC',
                'genre': 'RPG',
                'publisher': 'Bandai Namco',
                'release_date': date(2022, 2, 25),
                'cover_image_url': 'https://example.com/eldenring.jpg',
                'stock_count': 20
            },
            {
                'title': 'FIFA 24',
                'description': 'The latest entry in the world-famous football game series.',
                'price': 69.99,
                'platform': 'PS5',
                'genre': 'Sports',
                'publisher': 'EA Sports',
                'release_date': date(2023, 9, 29),
                'cover_image_url': 'https://example.com/fifa24.jpg',
                'stock_count': 25
            },
        ]

        # Create games
        created_games = []
        for game_data in games_data:
            game, created = Game.objects.get_or_create(
                title=game_data['title'],
                platform=game_data['platform'],
                defaults=game_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created game: {game.title}'))
                created_games.append(game)
            else:
                self.stdout.write(self.style.WARNING(f'Game already exists: {game.title}'))

        # Generate game keys for each game
        for game in created_games:
            keys_count = game.stock_count
            for i in range(keys_count):
                key_code = f'{game.platform}-{game.title[:4].upper()}-{"".join([str(random.randint(0, 9)) for _ in range(4)])}-{"".join([str(random.randint(0, 9)) for _ in range(4)])}'
                game_key, created = GameKey.objects.get_or_create(
                    key_code=key_code,
                    defaults={
                        'game': game,
                        'status': 'AVAILABLE'
                    }
                )
                if created:
                    self.stdout.write(f'  Created key for {game.title}')

        self.stdout.write(self.style.SUCCESS('\nDatabase seeded successfully!'))
        self.stdout.write(f'Total games: {Game.objects.count()}')
        self.stdout.write(f'Total keys: {GameKey.objects.count()}')

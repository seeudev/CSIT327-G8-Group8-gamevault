"""
Script to verify Supabase connection and show database info.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamevault_backend.settings')
django.setup()

from django.conf import settings
from django.db import connection
from users.models import User
from store.models import Game, Cart, Transaction

print("=" * 60)
print("DATABASE CONNECTION VERIFICATION")
print("=" * 60)

# Show database info
db = settings.DATABASES['default']
print(f"\n✅ Connected to: {db['ENGINE']}")
print(f"📍 Host: {db['HOST']}")
print(f"📊 Database: {db['NAME']}")
print(f"👤 User: {db['USER']}")

# Show database statistics
print("\n" + "=" * 60)
print("DATABASE STATISTICS")
print("=" * 60)

user_count = User.objects.count()
game_count = Game.objects.count()
cart_count = Cart.objects.count()
transaction_count = Transaction.objects.count()

print(f"\n👥 Total Users: {user_count}")
print(f"🎮 Total Games: {game_count}")
print(f"🛒 Total Carts: {cart_count}")
print(f"💰 Total Transactions: {transaction_count}")

# Show sample data
if user_count > 0:
    print("\n📋 Users:")
    for user in User.objects.all()[:5]:
        admin_badge = " [ADMIN]" if user.is_admin else ""
        print(f"  - {user.username}{admin_badge} ({user.email})")

if game_count > 0:
    print("\n🎮 Games:")
    for game in Game.objects.all()[:5]:
        print(f"  - {game.title} - ${game.price} ({game.category})")

print("\n" + "=" * 60)
print("✨ You are now using Supabase PostgreSQL! ✨")
print("=" * 60)

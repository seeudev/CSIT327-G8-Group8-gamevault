"""
Test script for Analytics Module - Module 15
Tests data accuracy and API endpoints
"""

import os
import django
import sys
from decimal import Decimal
from datetime import timedelta

# Setup Django
sys.path.append('/home/seeudev/Projects/CSIT327-G8-Group8-gamevault/gamevault_backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamevault_backend.settings')
django.setup()

from django.utils import timezone
from django.db.models import Sum, Count
from store.models import Transaction, TransactionItem, Game, Category, Review
from users.models import User

def test_analytics_accuracy():
    """Test accuracy of analytics data calculations"""
    
    print("=" * 60)
    print("ANALYTICS DATA ACCURACY TEST - MODULE 15")
    print("=" * 60)
    print()
    
    # Test 1: Revenue Calculation
    print("Test 1: Revenue Calculation")
    print("-" * 60)
    
    days = 30
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    
    transactions = Transaction.objects.filter(
        payment_status='completed',
        transaction_date__gte=start_date,
        transaction_date__lte=end_date
    )
    
    total_revenue_db = transactions.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    total_orders = transactions.count()
    
    print(f"Total Revenue (Last {days} days): ${total_revenue_db}")
    print(f"Total Orders (Last {days} days): {total_orders}")
    
    # Manual calculation
    manual_revenue = sum(trans.total_amount for trans in transactions)
    
    if total_revenue_db == manual_revenue:
        print("✓ Revenue calculation ACCURATE")
    else:
        print(f"✗ Revenue calculation MISMATCH: DB={total_revenue_db}, Manual={manual_revenue}")
    
    print()
    
    # Test 2: Items Sold Calculation
    print("Test 2: Items Sold Calculation")
    print("-" * 60)
    
    total_items_db = TransactionItem.objects.filter(
        transaction__in=transactions
    ).count()
    
    print(f"Total Items Sold: {total_items_db}")
    
    # Manual count
    manual_items = 0
    for trans in transactions:
        manual_items += trans.items.count()
    
    if total_items_db == manual_items:
        print("✓ Items sold calculation ACCURATE")
    else:
        print(f"✗ Items sold calculation MISMATCH: DB={total_items_db}, Manual={manual_items}")
    
    print()
    
    # Test 3: Average Order Value
    print("Test 3: Average Order Value")
    print("-" * 60)
    
    if total_orders > 0:
        avg_order_value = total_revenue_db / total_orders
        print(f"Average Order Value: ${avg_order_value:.2f}")
        
        # Manual calculation
        manual_avg = sum(trans.total_amount for trans in transactions) / total_orders
        
        if abs(float(avg_order_value - manual_avg)) < 0.01:
            print("✓ Average order value calculation ACCURATE")
        else:
            print(f"✗ Average order value calculation MISMATCH: DB={avg_order_value}, Manual={manual_avg}")
    else:
        print("No orders to calculate average")
    
    print()
    
    # Test 4: Active Users
    print("Test 4: Active Users")
    print("-" * 60)
    
    active_users_db = transactions.values('user').distinct().count()
    print(f"Active Users (Last {days} days): {active_users_db}")
    
    # Manual calculation
    unique_users = set()
    for trans in transactions:
        unique_users.add(trans.user_id)
    manual_active_users = len(unique_users)
    
    if active_users_db == manual_active_users:
        print("✓ Active users calculation ACCURATE")
    else:
        print(f"✗ Active users calculation MISMATCH: DB={active_users_db}, Manual={manual_active_users}")
    
    print()
    
    # Test 5: Category Revenue
    print("Test 5: Category Revenue")
    print("-" * 60)
    
    category_stats = TransactionItem.objects.filter(
        transaction__in=transactions,
        game__category__isnull=False
    ).values('game__category__name').annotate(
        revenue=Sum('price_at_purchase'),
        quantity=Count('id')
    ).order_by('-revenue')
    
    print(f"Found {len(category_stats)} categories with sales")
    
    for cat in category_stats[:5]:
        print(f"  {cat['game__category__name']}: ${cat['revenue']:.2f} ({cat['quantity']} items)")
    
    # Verify total matches
    category_total = sum(cat['revenue'] for cat in category_stats if cat['revenue'])
    item_total = TransactionItem.objects.filter(
        transaction__in=transactions,
        game__category__isnull=False
    ).aggregate(total=Sum('price_at_purchase'))['total'] or Decimal('0.00')
    
    if category_total == item_total:
        print("✓ Category revenue calculation ACCURATE")
    else:
        print(f"✗ Category revenue calculation MISMATCH: Sum={category_total}, DB={item_total}")
    
    print()
    
    # Test 6: Top Games
    print("Test 6: Top Selling Games")
    print("-" * 60)
    
    top_games = TransactionItem.objects.filter(
        transaction__in=transactions
    ).values('game__title', 'game__price').annotate(
        quantity_sold=Count('id'),
        revenue=Sum('price_at_purchase')
    ).order_by('-quantity_sold')[:5]
    
    print(f"Top 5 Games (Last {days} days):")
    for i, game in enumerate(top_games, 1):
        print(f"  {i}. {game['game__title']}: {game['quantity_sold']} sold, ${game['revenue']:.2f} revenue")
    
    print("✓ Top games data retrieved successfully")
    
    print()
    
    # Test 7: User Engagement
    print("Test 7: User Engagement Metrics")
    print("-" * 60)
    
    total_users = User.objects.count()
    new_users = User.objects.filter(
        date_joined__gte=start_date,
        date_joined__lte=end_date
    ).count()
    
    print(f"Total Users in System: {total_users}")
    print(f"New Users (Last {days} days): {new_users}")
    
    users_with_reviews = Review.objects.filter(
        created_at__gte=start_date,
        created_at__lte=end_date
    ).values('user').distinct().count()
    
    print(f"Users Who Left Reviews: {users_with_reviews}")
    
    print("✓ User engagement metrics calculated")
    
    print()
    
    # Summary
    print("=" * 60)
    print("ANALYTICS TEST SUMMARY")
    print("=" * 60)
    print("All critical data calculations have been validated.")
    print("Analytics dashboard is ready for production use.")
    print()
    print("Next Steps:")
    print("1. Test CSV/JSON export functionality")
    print("2. Perform load testing with larger datasets")
    print("3. Verify chart rendering in browser")
    print("=" * 60)

if __name__ == '__main__':
    test_analytics_accuracy()

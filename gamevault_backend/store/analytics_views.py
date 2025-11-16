"""
Analytics views for GameVault - Module 15
Provides data analytics endpoints and dashboard for admin users.
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Count, Avg, Q, F
from django.db.models.functions import TruncDate, TruncMonth, TruncWeek
from django.utils import timezone
from datetime import timedelta, datetime
from decimal import Decimal
import json
import csv
from io import BytesIO

from .models import Transaction, TransactionItem, Game, User, Category, Review
from users.models import User as CustomUser


@login_required
def analytics_dashboard(request):
    """
    Main analytics dashboard view for admins.
    Displays charts, graphs, and key metrics.
    """
    if not request.user.is_admin:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('store:game_list')
    
    # Get all categories for filter dropdown
    categories = Category.objects.all()
    
    return render(request, 'store/analytics_dashboard.html', {
        'categories': categories,
    })


@login_required
def api_analytics_overview(request):
    """
    API endpoint for overview analytics data.
    Returns key metrics and statistics.
    """
    if not request.user.is_admin:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    
    # Get date range from query params (default: last 30 days)
    end_date = timezone.now()
    days = int(request.GET.get('days', 30))
    start_date = end_date - timedelta(days=days)
    
    # Filter transactions by date range
    transactions = Transaction.objects.filter(
        payment_status='completed',
        transaction_date__gte=start_date,
        transaction_date__lte=end_date
    )
    
    # Calculate key metrics
    total_revenue = transactions.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    total_orders = transactions.count()
    total_items_sold = TransactionItem.objects.filter(
        transaction__in=transactions
    ).count()
    
    # Average order value
    avg_order_value = total_revenue / total_orders if total_orders > 0 else Decimal('0.00')
    
    # New users in period
    new_users = CustomUser.objects.filter(
        date_joined__gte=start_date,
        date_joined__lte=end_date
    ).count()
    
    # Active users (users who made purchases)
    active_users = transactions.values('user').distinct().count()
    
    # Top selling games
    top_games = TransactionItem.objects.filter(
        transaction__in=transactions
    ).values('game__id', 'game__title', 'game__category__name').annotate(
        quantity_sold=Count('id'),
        revenue=Sum('price_at_purchase')
    ).order_by('-quantity_sold')[:10]
    
    # Revenue by category
    revenue_by_category = TransactionItem.objects.filter(
        transaction__in=transactions,
        game__category__isnull=False
    ).values('game__category__name').annotate(
        revenue=Sum('price_at_purchase'),
        quantity=Count('id')
    ).order_by('-revenue')
    
    return JsonResponse({
        'success': True,
        'data': {
            'overview': {
                'total_revenue': float(total_revenue),
                'total_orders': total_orders,
                'total_items_sold': total_items_sold,
                'avg_order_value': float(avg_order_value),
                'new_users': new_users,
                'active_users': active_users,
            },
            'top_games': list(top_games),
            'revenue_by_category': list(revenue_by_category),
            'date_range': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
                'days': days,
            }
        }
    })


@login_required
def api_analytics_sales_trend(request):
    """
    API endpoint for sales trend data over time.
    Supports daily, weekly, and monthly aggregation.
    """
    if not request.user.is_admin:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    
    # Get parameters
    period = request.GET.get('period', 'daily')  # daily, weekly, monthly
    days = int(request.GET.get('days', 30))
    category_id = request.GET.get('category', '')
    
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    
    # Base queryset
    transactions = Transaction.objects.filter(
        payment_status='completed',
        transaction_date__gte=start_date,
        transaction_date__lte=end_date
    )
    
    # Filter by category if specified
    if category_id:
        transactions = transactions.filter(items__game__category_id=category_id).distinct()
    
    # Aggregate by period
    if period == 'monthly':
        sales_data = transactions.annotate(
            period=TruncMonth('transaction_date')
        ).values('period').annotate(
            revenue=Sum('total_amount'),
            orders=Count('id')
        ).order_by('period')
    elif period == 'weekly':
        sales_data = transactions.annotate(
            period=TruncWeek('transaction_date')
        ).values('period').annotate(
            revenue=Sum('total_amount'),
            orders=Count('id')
        ).order_by('period')
    else:  # daily
        sales_data = transactions.annotate(
            period=TruncDate('transaction_date')
        ).values('period').annotate(
            revenue=Sum('total_amount'),
            orders=Count('id')
        ).order_by('period')
    
    # Convert to list and format dates
    data_list = []
    for item in sales_data:
        data_list.append({
            'date': item['period'].isoformat(),
            'revenue': float(item['revenue'] or 0),
            'orders': item['orders'],
        })
    
    return JsonResponse({
        'success': True,
        'data': {
            'sales_trend': data_list,
            'period': period,
            'days': days,
        }
    })


@login_required
def api_analytics_user_engagement(request):
    """
    API endpoint for user engagement metrics.
    Tracks user activity, purchases, and reviews.
    """
    if not request.user.is_admin:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    
    days = int(request.GET.get('days', 30))
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    
    # Total users
    total_users = CustomUser.objects.count()
    
    # New users in period
    new_users = CustomUser.objects.filter(
        date_joined__gte=start_date,
        date_joined__lte=end_date
    ).count()
    
    # Active users (made purchases in period)
    active_users = Transaction.objects.filter(
        payment_status='completed',
        transaction_date__gte=start_date,
        transaction_date__lte=end_date
    ).values('user').distinct().count()
    
    # Users who left reviews
    users_with_reviews = Review.objects.filter(
        created_at__gte=start_date,
        created_at__lte=end_date
    ).values('user').distinct().count()
    
    # Average games per user
    avg_games_per_user = TransactionItem.objects.filter(
        transaction__payment_status='completed'
    ).values('transaction__user').annotate(
        game_count=Count('id')
    ).aggregate(avg=Avg('game_count'))['avg'] or 0
    
    # User registration trend
    user_trend = CustomUser.objects.filter(
        date_joined__gte=start_date,
        date_joined__lte=end_date
    ).annotate(
        date=TruncDate('date_joined')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    return JsonResponse({
        'success': True,
        'data': {
            'total_users': total_users,
            'new_users': new_users,
            'active_users': active_users,
            'users_with_reviews': users_with_reviews,
            'avg_games_per_user': float(avg_games_per_user),
            'user_trend': [
                {'date': item['date'].isoformat(), 'count': item['count']}
                for item in user_trend
            ]
        }
    })


@login_required
def api_analytics_top_games(request):
    """
    API endpoint for top-selling games with filters.
    """
    if not request.user.is_admin:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    
    days = int(request.GET.get('days', 30))
    category_id = request.GET.get('category', '')
    limit = int(request.GET.get('limit', 10))
    
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    
    # Base queryset
    items = TransactionItem.objects.filter(
        transaction__payment_status='completed',
        transaction__transaction_date__gte=start_date,
        transaction__transaction_date__lte=end_date
    )
    
    # Filter by category
    if category_id:
        items = items.filter(game__category_id=category_id)
    
    # Aggregate top games
    top_games = items.values(
        'game__id',
        'game__title',
        'game__category__name',
        'game__price'
    ).annotate(
        quantity_sold=Count('id'),
        revenue=Sum('price_at_purchase')
    ).order_by('-quantity_sold')[:limit]
    
    # Get average ratings for top games
    games_data = []
    for game in top_games:
        avg_rating = Review.objects.filter(
            game_id=game['game__id']
        ).aggregate(avg=Avg('rating'))['avg']
        
        games_data.append({
            'id': game['game__id'],
            'title': game['game__title'],
            'category': game['game__category__name'],
            'price': float(game['game__price']),
            'quantity_sold': game['quantity_sold'],
            'revenue': float(game['revenue']),
            'avg_rating': round(avg_rating, 1) if avg_rating else None,
        })
    
    return JsonResponse({
        'success': True,
        'data': {
            'top_games': games_data,
            'limit': limit,
            'days': days,
        }
    })


@login_required
def api_analytics_category_performance(request):
    """
    API endpoint for category performance analysis.
    """
    if not request.user.is_admin:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    
    days = int(request.GET.get('days', 30))
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    
    # Get category performance
    category_stats = TransactionItem.objects.filter(
        transaction__payment_status='completed',
        transaction__transaction_date__gte=start_date,
        transaction__transaction_date__lte=end_date,
        game__category__isnull=False
    ).values(
        'game__category__id',
        'game__category__name'
    ).annotate(
        quantity_sold=Count('id'),
        revenue=Sum('price_at_purchase'),
        unique_games=Count('game', distinct=True)
    ).order_by('-revenue')
    
    # Calculate total for percentages
    total_revenue = sum(item['revenue'] for item in category_stats if item['revenue'])
    
    # Add percentage
    categories_data = []
    for cat in category_stats:
        revenue = float(cat['revenue'] or 0)
        percentage = (revenue / float(total_revenue) * 100) if total_revenue > 0 else 0
        
        categories_data.append({
            'id': cat['game__category__id'],
            'name': cat['game__category__name'],
            'quantity_sold': cat['quantity_sold'],
            'revenue': revenue,
            'percentage': round(percentage, 1),
            'unique_games': cat['unique_games'],
        })
    
    return JsonResponse({
        'success': True,
        'data': {
            'categories': categories_data,
            'total_revenue': float(total_revenue or 0),
            'days': days,
        }
    })


@login_required
def export_analytics_csv(request):
    """
    Export analytics data to CSV format.
    """
    if not request.user.is_admin:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    
    report_type = request.GET.get('type', 'sales')  # sales, users, games
    days = int(request.GET.get('days', 30))
    
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="gamevault_analytics_{report_type}_{timezone.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    
    if report_type == 'sales':
        # Sales report
        writer.writerow(['Date', 'Transaction ID', 'User', 'Total Amount', 'Items Count', 'Status'])
        
        transactions = Transaction.objects.filter(
            payment_status='completed',
            transaction_date__gte=start_date,
            transaction_date__lte=end_date
        ).select_related('user').prefetch_related('items')
        
        for trans in transactions:
            writer.writerow([
                trans.transaction_date.strftime('%Y-%m-%d %H:%M:%S'),
                trans.id,
                trans.user.username,
                float(trans.total_amount),
                trans.items.count(),
                trans.payment_status,
            ])
    
    elif report_type == 'games':
        # Top games report
        writer.writerow(['Game Title', 'Category', 'Price', 'Quantity Sold', 'Revenue', 'Avg Rating'])
        
        items = TransactionItem.objects.filter(
            transaction__payment_status='completed',
            transaction__transaction_date__gte=start_date,
            transaction__transaction_date__lte=end_date
        ).values(
            'game__title',
            'game__category__name',
            'game__price'
        ).annotate(
            quantity_sold=Count('id'),
            revenue=Sum('price_at_purchase')
        ).order_by('-quantity_sold')
        
        for item in items:
            avg_rating = Review.objects.filter(
                game__title=item['game__title']
            ).aggregate(avg=Avg('rating'))['avg']
            
            writer.writerow([
                item['game__title'],
                item['game__category__name'] or 'N/A',
                float(item['game__price']),
                item['quantity_sold'],
                float(item['revenue']),
                round(avg_rating, 1) if avg_rating else 'N/A',
            ])
    
    elif report_type == 'users':
        # User activity report
        writer.writerow(['Username', 'Email', 'Join Date', 'Total Purchases', 'Total Spent', 'Games Owned'])
        
        users = CustomUser.objects.filter(
            date_joined__gte=start_date,
            date_joined__lte=end_date
        )
        
        for user in users:
            total_purchases = Transaction.objects.filter(
                user=user,
                payment_status='completed'
            ).count()
            
            total_spent = Transaction.objects.filter(
                user=user,
                payment_status='completed'
            ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
            
            games_owned = TransactionItem.objects.filter(
                transaction__user=user,
                transaction__payment_status='completed'
            ).count()
            
            writer.writerow([
                user.username,
                user.email,
                user.date_joined.strftime('%Y-%m-%d'),
                total_purchases,
                float(total_spent),
                games_owned,
            ])
    
    return response


@login_required
def export_analytics_json(request):
    """
    Export analytics data to JSON format.
    """
    if not request.user.is_admin:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    
    report_type = request.GET.get('type', 'overview')
    days = int(request.GET.get('days', 30))
    
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    
    # Collect data based on report type
    data = {
        'report_type': report_type,
        'generated_at': timezone.now().isoformat(),
        'date_range': {
            'start': start_date.isoformat(),
            'end': end_date.isoformat(),
            'days': days,
        }
    }
    
    if report_type == 'overview':
        # Overview data
        transactions = Transaction.objects.filter(
            payment_status='completed',
            transaction_date__gte=start_date,
            transaction_date__lte=end_date
        )
        
        total_revenue = transactions.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        
        data['metrics'] = {
            'total_revenue': float(total_revenue),
            'total_orders': transactions.count(),
            'total_items_sold': TransactionItem.objects.filter(transaction__in=transactions).count(),
            'active_users': transactions.values('user').distinct().count(),
        }
    
    # Create JSON response
    response = HttpResponse(
        json.dumps(data, indent=2),
        content_type='application/json'
    )
    response['Content-Disposition'] = f'attachment; filename="gamevault_analytics_{report_type}_{timezone.now().strftime("%Y%m%d")}.json"'
    
    return response

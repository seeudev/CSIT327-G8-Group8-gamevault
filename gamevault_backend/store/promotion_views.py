"""
Promotion views for GameVault - Module 16.
Handles promotion management, display, and reporting.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods, require_POST
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Count, F, Q
from django.utils import timezone
from decimal import Decimal
import json
import csv
from datetime import datetime, timedelta

from .models import Promotion, PromotionUsage, Game, Category, Transaction, TransactionItem
from users.models import User


@login_required
def promotion_list(request):
    """
    Admin view: List all promotions with filtering options.
    GET /store/admin/promotions/
    """
    if not request.user.is_admin:
        messages.error(request, 'You must be an admin to access this page.')
        return redirect('store:game_list')
    
    promotions = Promotion.objects.all()
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter == 'active':
        now = timezone.now()
        promotions = promotions.filter(
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        )
    elif status_filter == 'upcoming':
        promotions = promotions.filter(start_date__gt=timezone.now())
    elif status_filter == 'expired':
        promotions = promotions.filter(end_date__lt=timezone.now())
    elif status_filter == 'inactive':
        promotions = promotions.filter(is_active=False)
    
    # Search by name
    search = request.GET.get('search', '')
    if search:
        promotions = promotions.filter(name__icontains=search)
    
    # Add usage statistics
    for promotion in promotions:
        usage_stats = promotion.usages.aggregate(
            total_uses=Count('id'),
            total_savings=Sum('discount_amount')
        )
        promotion.total_uses = usage_stats['total_uses'] or 0
        promotion.total_savings = usage_stats['total_savings'] or Decimal('0.00')
        promotion.currently_active = promotion.is_currently_active()
    
    context = {
        'promotions': promotions,
        'status_filter': status_filter,
        'search': search,
    }
    return render(request, 'store/admin/promotions_list.html', context)


@login_required
def promotion_create(request):
    """
    Admin view: Create a new promotion.
    GET/POST /store/admin/promotions/create/
    """
    if not request.user.is_admin:
        messages.error(request, 'You must be an admin to access this page.')
        return redirect('store:game_list')
    
    if request.method == 'POST':
        try:
            # Extract form data
            name = request.POST.get('name')
            description = request.POST.get('description', '')
            discount_type = request.POST.get('discount_type')
            discount_value = Decimal(request.POST.get('discount_value'))
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            is_active = request.POST.get('is_active') == 'on'
            
            # Validation
            if not name or not discount_type or not start_date or not end_date:
                messages.error(request, 'Please fill in all required fields.')
                return redirect('store:promotion_create')
            
            if discount_value <= 0:
                messages.error(request, 'Discount value must be greater than 0.')
                return redirect('store:promotion_create')
            
            if discount_type == 'percentage' and discount_value > 100:
                messages.error(request, 'Percentage discount cannot exceed 100%.')
                return redirect('store:promotion_create')
            
            # Create promotion
            promotion = Promotion.objects.create(
                name=name,
                description=description,
                discount_type=discount_type,
                discount_value=discount_value,
                start_date=start_date,
                end_date=end_date,
                is_active=is_active,
                created_by=request.user
            )
            
            # Add games
            game_ids = request.POST.getlist('games')
            if game_ids:
                promotion.games.set(Game.objects.filter(id__in=game_ids))
            
            # Add categories
            category_ids = request.POST.getlist('categories')
            if category_ids:
                promotion.categories.set(Category.objects.filter(id__in=category_ids))
            
            messages.success(request, f'Promotion "{name}" created successfully!')
            return redirect('store:promotion_detail', promotion_id=promotion.id)
            
        except Exception as e:
            messages.error(request, f'Error creating promotion: {str(e)}')
            return redirect('store:promotion_create')
    
    # GET request - show form
    games = Game.objects.all().order_by('title')
    categories = Category.objects.all().order_by('name')
    
    context = {
        'games': games,
        'categories': categories,
    }
    return render(request, 'store/admin/promotion_form.html', context)


@login_required
def promotion_edit(request, promotion_id):
    """
    Admin view: Edit an existing promotion.
    GET/POST /store/admin/promotions/<id>/edit/
    """
    if not request.user.is_admin:
        messages.error(request, 'You must be an admin to access this page.')
        return redirect('store:game_list')
    
    promotion = get_object_or_404(Promotion, id=promotion_id)
    
    if request.method == 'POST':
        try:
            # Update fields
            promotion.name = request.POST.get('name')
            promotion.description = request.POST.get('description', '')
            promotion.discount_type = request.POST.get('discount_type')
            promotion.discount_value = Decimal(request.POST.get('discount_value'))
            promotion.start_date = request.POST.get('start_date')
            promotion.end_date = request.POST.get('end_date')
            promotion.is_active = request.POST.get('is_active') == 'on'
            
            # Validation
            if promotion.discount_value <= 0:
                messages.error(request, 'Discount value must be greater than 0.')
                return redirect('store:promotion_edit', promotion_id=promotion_id)
            
            if promotion.discount_type == 'percentage' and promotion.discount_value > 100:
                messages.error(request, 'Percentage discount cannot exceed 100%.')
                return redirect('store:promotion_edit', promotion_id=promotion_id)
            
            promotion.save()
            
            # Update games
            game_ids = request.POST.getlist('games')
            promotion.games.set(Game.objects.filter(id__in=game_ids))
            
            # Update categories
            category_ids = request.POST.getlist('categories')
            promotion.categories.set(Category.objects.filter(id__in=category_ids))
            
            messages.success(request, f'Promotion "{promotion.name}" updated successfully!')
            return redirect('store:promotion_detail', promotion_id=promotion.id)
            
        except Exception as e:
            messages.error(request, f'Error updating promotion: {str(e)}')
            return redirect('store:promotion_edit', promotion_id=promotion_id)
    
    # GET request - show form with current values
    games = Game.objects.all().order_by('title')
    categories = Category.objects.all().order_by('name')
    
    # Get selected games and categories
    selected_game_ids = list(promotion.games.values_list('id', flat=True))
    selected_category_ids = list(promotion.categories.values_list('id', flat=True))
    
    context = {
        'promotion': promotion,
        'games': games,
        'categories': categories,
        'selected_game_ids': selected_game_ids,
        'selected_category_ids': selected_category_ids,
        'is_edit': True,
    }
    return render(request, 'store/admin/promotion_form.html', context)


@login_required
def promotion_detail(request, promotion_id):
    """
    Admin view: View promotion details and performance statistics.
    GET /store/admin/promotions/<id>/
    """
    if not request.user.is_admin:
        messages.error(request, 'You must be an admin to access this page.')
        return redirect('store:game_list')
    
    promotion = get_object_or_404(Promotion, id=promotion_id)
    
    # Get usage statistics
    usages = promotion.usages.all()
    total_uses = usages.count()
    total_savings = usages.aggregate(total=Sum('discount_amount'))['total'] or Decimal('0.00')
    total_revenue = usages.aggregate(total=Sum('discounted_price'))['total'] or Decimal('0.00')
    
    # Get top games sold with this promotion
    top_games = usages.values('game__title', 'game__id').annotate(
        quantity=Count('id'),
        revenue=Sum('discounted_price'),
        savings=Sum('discount_amount')
    ).order_by('-quantity')[:10]
    
    # Daily usage trend (last 30 days or since creation)
    start_date = max(
        promotion.created_at,
        timezone.now() - timedelta(days=30)
    ).date()
    
    daily_usage = usages.filter(
        used_at__date__gte=start_date
    ).values('used_at__date').annotate(
        uses=Count('id'),
        revenue=Sum('discounted_price'),
        savings=Sum('discount_amount')
    ).order_by('used_at__date')
    
    context = {
        'promotion': promotion,
        'total_uses': total_uses,
        'total_savings': total_savings,
        'total_revenue': total_revenue,
        'top_games': top_games,
        'daily_usage': daily_usage,
        'is_currently_active': promotion.is_currently_active(),
        'applicable_games_count': promotion.get_applicable_games().count(),
    }
    return render(request, 'store/admin/promotion_detail.html', context)


@login_required
@require_POST
def promotion_delete(request, promotion_id):
    """
    Admin view: Delete a promotion.
    POST /store/admin/promotions/<id>/delete/
    """
    if not request.user.is_admin:
        return JsonResponse({
            'success': False,
            'error': 'Admin access required'
        }, status=403)
    
    try:
        promotion = get_object_or_404(Promotion, id=promotion_id)
        name = promotion.name
        promotion.delete()
        
        messages.success(request, f'Promotion "{name}" deleted successfully!')
        return JsonResponse({
            'success': True,
            'message': f'Promotion deleted successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_POST
def promotion_toggle(request, promotion_id):
    """
    Admin API: Toggle promotion active status.
    POST /store/admin/promotions/<id>/toggle/
    """
    if not request.user.is_admin:
        return JsonResponse({
            'success': False,
            'error': 'Admin access required'
        }, status=403)
    
    try:
        promotion = get_object_or_404(Promotion, id=promotion_id)
        promotion.is_active = not promotion.is_active
        promotion.save()
        
        status = 'activated' if promotion.is_active else 'deactivated'
        return JsonResponse({
            'success': True,
            'is_active': promotion.is_active,
            'message': f'Promotion {status} successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def promotion_report(request, promotion_id):
    """
    Admin view: Generate and export promotion performance report as CSV.
    GET /store/admin/promotions/<id>/report/
    """
    if not request.user.is_admin:
        messages.error(request, 'You must be an admin to access this page.')
        return redirect('store:game_list')
    
    promotion = get_object_or_404(Promotion, id=promotion_id)
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="promotion_{promotion.id}_{datetime.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    
    # Write header
    writer.writerow([
        'Promotion Report',
        promotion.name,
        f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}'
    ])
    writer.writerow([])
    
    # Write summary
    writer.writerow(['Summary'])
    writer.writerow(['Total Uses', promotion.usages.count()])
    writer.writerow(['Total Savings', f'${promotion.usages.aggregate(total=Sum("discount_amount"))["total"] or 0:.2f}'])
    writer.writerow(['Total Revenue', f'${promotion.usages.aggregate(total=Sum("discounted_price"))["total"] or 0:.2f}'])
    writer.writerow([])
    
    # Write detailed usage
    writer.writerow(['Detailed Usage'])
    writer.writerow(['Date', 'Game', 'Original Price', 'Discounted Price', 'Savings', 'Transaction ID'])
    
    usages = promotion.usages.select_related('game', 'transaction').order_by('-used_at')
    for usage in usages:
        writer.writerow([
            usage.used_at.strftime('%Y-%m-%d %H:%M'),
            usage.game.title,
            f'${usage.original_price:.2f}',
            f'${usage.discounted_price:.2f}',
            f'${usage.discount_amount:.2f}',
            usage.transaction.id
        ])
    
    return response


def get_active_promotions_for_game(game):
    """
    Helper function: Get all active promotions applicable to a game.
    Returns list of Promotion objects.
    """
    now = timezone.now()
    
    # Promotions that include this game specifically
    game_promotions = Promotion.objects.filter(
        games=game,
        is_active=True,
        start_date__lte=now,
        end_date__gte=now
    )
    
    # Promotions that include this game's category
    category_promotions = Promotion.objects.none()
    if game.category:
        category_promotions = Promotion.objects.filter(
            categories=game.category,
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        )
    
    # Combine and remove duplicates
    promotions = (game_promotions | category_promotions).distinct()
    
    return list(promotions)


def calculate_best_price(game, promotions=None):
    """
    Helper function: Calculate the best discounted price for a game.
    Returns (discounted_price, applied_promotion) or (original_price, None).
    """
    if promotions is None:
        promotions = get_active_promotions_for_game(game)
    
    if not promotions:
        return game.price, None
    
    # Find the promotion that gives the best discount
    best_price = game.price
    best_promotion = None
    
    for promotion in promotions:
        discounted_price = promotion.calculate_discounted_price(game.price)
        if discounted_price < best_price:
            best_price = discounted_price
            best_promotion = promotion
    
    return best_price, best_promotion

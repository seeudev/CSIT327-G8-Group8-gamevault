"""
Admin views for template rendering
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Sum, Q
from store.models import Game
from users.models import User


def is_admin(user):
    """Check if user is admin"""
    return user.is_authenticated and user.is_admin


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Admin dashboard view"""
    # Get stats
    stats = {
        'total_games': Game.objects.count(),
        'total_users': User.objects.count(),
        'total_orders': 0,  # Placeholder
        'total_revenue': 0,  # Placeholder
    }
    
    context = {
        'stats': stats
    }
    return render(request, 'admin/dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def game_list(request):
    """Game list view for admin"""
    games = Game.objects.all().order_by('-created_at')
    
    context = {
        'games': games
    }
    return render(request, 'admin/game_list.html', context)


@login_required
@user_passes_test(is_admin)
def game_create(request):
    """Game creation view for admin"""
    if request.method == 'POST':
        # Handle game creation
        # This would typically use a form or serializer
        messages.success(request, 'Game created successfully!')
        return redirect('admin:game_list')
    
    return render(request, 'admin/game_form.html')


@login_required
@user_passes_test(is_admin)
def game_edit(request, slug):
    """Game edit view for admin"""
    game = get_object_or_404(Game, slug=slug)
    
    if request.method == 'POST':
        # Handle game update
        messages.success(request, 'Game updated successfully!')
        return redirect('admin:game_list')
    
    context = {
        'game': game,
        'is_edit': True
    }
    return render(request, 'admin/game_form.html', context)


@login_required
@user_passes_test(is_admin)
def user_list(request):
    """User list view for admin"""
    users = User.objects.all().order_by('-date_joined')
    
    context = {
        'users': users
    }
    return render(request, 'admin/user_list.html', context)


@login_required
@user_passes_test(is_admin)
def order_list(request):
    """Order list view for admin"""
    # Placeholder - orders functionality to be implemented
    context = {
        'orders': []
    }
    return render(request, 'admin/order_list.html', context)


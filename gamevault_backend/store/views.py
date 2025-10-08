"""
Simple store views for GameVault.
Handles game listing, cart management, checkout, and transactions.
"""
from django.contrib.auth.models import update_last_login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from decimal import Decimal

from .models import Game, Cart, CartItem, Transaction, TransactionItem, AdminActionLog
from users.models import User


def game_list(request):
    """
    Display list of all games with optional filtering.
    Public view - no login required.
    """
    games = Game.objects.all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        games = games.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Filter by category
    category = request.GET.get('category', '')
    if category:
        games = games.filter(category__iexact=category)

    # Filter by price range
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        games = games.filter(price__gte=min_price)
    if max_price:
        games = games.filter(price__lte=max_price)

    # Filter release date range
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date:
        games = games.filter(upload_date__date__gte=start_date)
    if end_date:
        games = games.filter(upload_date__date__lte=end_date)

    # Sorting
    sort_by = request.GET.get('sort', '')
    if sort_by == 'price_low':
        games = games.order_by('price')
    elif sort_by == 'price_high':
        games = games.order_by('-price')
    elif sort_by == 'newest':
        games = games.order_by('-upload_date')
    elif sort_by == 'oldest':
        games = games.order_by('upload_date')
    # Popularity
    elif sort_by == 'popular' and hasattr(Game, 'popularity'):
        games = games.order_by('-popularity')

    # Get all unique categories for filter
    categories = Game.objects.values_list('category', flat=True).distinct()
    
    return render(request, 'store/game_list.html', {
        'games': games,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category,
        'selected_sort': sort_by,
        'min_price': min_price,
        'max_price': max_price,
        'start_date': start_date,
        'end_date': end_date,
    })


def game_detail(request, game_id):
    """
    Display details of a single game.
    """
    game = get_object_or_404(Game, id=game_id)
    return render(request, 'store/game_detail.html', {
        'game': game
    })


@login_required
def cart_view(request):
    """
    Display user's shopping cart.
    """
    # Get or create active cart for user
    cart, created = Cart.objects.get_or_create(
        user=request.user,
        status='active'
    )
    
    cart_items = cart.items.all()
    total = cart.get_total()
    
    return render(request, 'store/cart.html', {
        'cart': cart,
        'cart_items': cart_items,
        'total': total,
    })


@login_required
@require_http_methods(["POST"])
def add_to_cart(request, game_id):
    """
    Add a game to the user's cart.
    """
    game = get_object_or_404(Game, id=game_id)
    
    # Get or create active cart
    cart, created = Cart.objects.get_or_create(
        user=request.user,
        status='active'
    )
    
    # Check if game is already in cart
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        game=game,
        defaults={'price_at_addition': game.price, 'quantity': 1}
    )
    
    if not created:
        # Item already exists, increase quantity
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, f'Increased {game.title} quantity in cart.')
    else:
        messages.success(request, f'Added {game.title} to cart.')
    
    return redirect('store:cart')


@login_required
@require_http_methods(["POST"])
def remove_from_cart(request, item_id):
    """
    Remove an item from the cart.
    """
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    game_title = cart_item.game.title
    cart_item.delete()
    messages.success(request, f'Removed {game_title} from cart.')
    return redirect('store:cart')


@login_required
@require_http_methods(["POST"])
def update_cart_quantity(request, item_id):
    """
    Update quantity of an item in the cart.
    """
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, 'Cart updated.')
    else:
        cart_item.delete()
        messages.success(request, 'Item removed from cart.')
    
    return redirect('store:cart')


@login_required
def checkout(request):
    """
    Process checkout - convert cart to transaction.
    """
    # Get user's active cart
    try:
        cart = Cart.objects.get(user=request.user, status='active')
    except Cart.DoesNotExist:
        messages.error(request, 'Your cart is empty.')
        return redirect('store:cart')
    
    cart_items = cart.items.all()
    if not cart_items.exists():
        messages.error(request, 'Your cart is empty.')
        return redirect('store:cart')
    
    if request.method == 'POST':
        # Calculate total
        total = cart.get_total()
        
        # Create transaction
        transaction = Transaction.objects.create(
            user=request.user,
            total_amount=total,
            payment_status='completed'  # In a real app, this would be 'pending' until payment
        )
        
        # Create transaction items from cart items
        for cart_item in cart_items:
            TransactionItem.objects.create(
                transaction=transaction,
                game=cart_item.game,
                price_at_purchase=cart_item.price_at_addition
            )
        
        # Mark cart as checked out
        cart.status = 'checked_out'
        cart.save()
        
        messages.success(request, 'Purchase completed successfully!')
        return redirect('store:transaction_detail', transaction_id=transaction.id)
    
    # GET request - show checkout confirmation
    total = cart.get_total()
    return render(request, 'store/checkout.html', {
        'cart': cart,
        'cart_items': cart_items,
        'total': total,
    })


@login_required
def transaction_history(request):
    """
    Display user's transaction history.
    """
    transactions = Transaction.objects.filter(user=request.user).order_by('-transaction_date')
    
    return render(request, 'store/transaction_history.html', {
        'transactions': transactions
    })


@login_required
def transaction_detail(request, transaction_id):
    """
    Display details of a specific transaction.
    """
    transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)
    transaction_items = transaction.items.all()
    
    return render(request, 'store/transaction_detail.html', {
        'transaction': transaction,
        'transaction_items': transaction_items,
    })


@login_required
def download_game(request, transaction_id, game_id):
    """
    Allow user to download a game from their purchase.
    Verify they own the game before allowing download.
    """
    transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)
    game = get_object_or_404(Game, id=game_id)
    
    # Verify the game is in this transaction
    if not transaction.items.filter(game=game).exists():
        messages.error(request, 'You do not own this game.')
        return redirect('store:transaction_history')
    
    # In a real app, this would redirect to a secure download URL or serve the file
    # For now, just redirect to the file_url if it exists
    if game.file_url:
        messages.success(request, f'Starting download for {game.title}')
        return redirect(game.file_url)
    else:
        messages.error(request, 'Download not available for this game.')
        return redirect('store:transaction_detail', transaction_id=transaction.id)


# Admin views
@login_required
def admin_dashboard(request):
    """
    Admin dashboard view.
    Only accessible to admin users.
    """
    if not request.user.is_admin:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('store:game_list')
    
    # Get stats
    total_games = Game.objects.count()
    total_users = User.objects.count()
    total_transactions = Transaction.objects.count()
    recent_actions = AdminActionLog.objects.all()[:10]
    
    return render(request, 'store/admin_dashboard.html', {
        'total_games': total_games,
        'total_users': total_users,
        'total_transactions': total_transactions,
        'recent_actions': recent_actions,
    })


@login_required
def admin_game_list(request):
    """
    Admin view to list all games for management.
    """
    if not request.user.is_admin:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('store:game_list')
    
    games = Game.objects.all().order_by('-upload_date')
    return render(request, 'store/admin_game_list.html', {
        'games': games
    })


@login_required
@require_http_methods(["GET", "POST"])
def admin_game_create(request):
    """
    Admin view to create a new game.
    """
    if not request.user.is_admin:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('store:game_list')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        category = request.POST.get('category')
        price = request.POST.get('price')
        screenshot_url = request.POST.get('screenshot_url')
        file_url = request.POST.get('file_url')
        
        # Simple validation
        if not all([title, description, category, price]):
            messages.error(request, 'All required fields must be filled.')
            return render(request, 'store/admin_game_form.html')
        
        try:
            game = Game.objects.create(
                title=title,
                description=description,
                category=category,
                price=Decimal(price),
                screenshot_url=screenshot_url if screenshot_url else None,
                file_url=file_url if file_url else None,
            )
            
            # Log the action
            AdminActionLog.objects.create(
                admin=request.user,
                action_type='create',
                target_game=game,
                notes=f'Created game: {title}'
            )
            
            messages.success(request, f'Game "{title}" created successfully.')
            return redirect('store:admin_game_list')
        except Exception as e:
            messages.error(request, f'Error creating game: {str(e)}')
            return render(request, 'store/admin_game_form.html')
    
    return render(request, 'store/admin_game_form.html')


@login_required
@require_http_methods(["GET", "POST"])
def admin_game_edit(request, game_id):
    """
    Admin view to edit an existing game.
    """
    if not request.user.is_admin:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('store:game_list')
    
    game = get_object_or_404(Game, id=game_id)
    
    if request.method == 'POST':
        game.title = request.POST.get('title')
        game.description = request.POST.get('description')
        game.category = request.POST.get('category')
        game.price = Decimal(request.POST.get('price'))
        screenshot_url = request.POST.get('screenshot_url')
        file_url = request.POST.get('file_url')
        
        if screenshot_url:
            game.screenshot_url = screenshot_url
        if file_url:
            game.file_url = file_url
        
        try:
            game.save()
            
            # Log the action
            AdminActionLog.objects.create(
                admin=request.user,
                action_type='update',
                target_game=game,
                notes=f'Updated game: {game.title}'
            )
            
            messages.success(request, f'Game "{game.title}" updated successfully.')
            return redirect('store:admin_game_list')
        except Exception as e:
            messages.error(request, f'Error updating game: {str(e)}')
    
    return render(request, 'store/admin_game_form.html', {
        'game': game,
        'is_edit': True
    })


@login_required
@require_http_methods(["POST"])
def admin_game_delete(request, game_id):
    """
    Admin view to delete a game.
    """
    if not request.user.is_admin:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('store:game_list')
    
    game = get_object_or_404(Game, id=game_id)
    game_title = game.title
    
    # Log the action before deletion
    AdminActionLog.objects.create(
        admin=request.user,
        action_type='delete',
        target_game=None,  # Game will be deleted
        notes=f'Deleted game: {game_title} (ID: {game_id})'
    )
    
    game.delete()
    messages.success(request, f'Game "{game_title}" deleted successfully.')
    return redirect('store:admin_game_list')

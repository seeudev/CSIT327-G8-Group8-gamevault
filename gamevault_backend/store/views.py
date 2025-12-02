"""
Simple store views for GameVault.
Handles game listing, cart management, checkout, and transactions.
"""
from django.contrib.auth.models import update_last_login
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods, require_POST
from django.db.models import Q, Sum, Count
from django.http import JsonResponse
from decimal import Decimal
import json

from .models import Game, Cart, CartItem, Transaction, TransactionItem, AdminActionLog, GameTag, Tag, Category, Review
from .middleware import PurchaseValidationMiddleware
from .email_service import send_game_key_email
from users.models import User

from .models import Wishlist
from .serializers import wishlist_to_dict


def game_list(request):
    """
    Display list of all games with optional filtering.
    Public view - no login required.

    Display list of all games with optional filtering by category, tag, search, price, and date.
    Supports:
    Public view - no login required.
      /store/games/?category=Action
      /store/games/?tag=Singleplayer
      /store/games/?category=Action&tag=Singleplayer
    """

    games = Game.objects.all()

    # Wishlist functionality
    wishlist_game_ids = []
    if request.user.is_authenticated:
        wishlist_game_ids = list(
            Wishlist.objects.filter(user=request.user).values_list('game_id', flat=True)
        )

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
        games = games.filter(category__name__iexact=category)

    # Filter by tag
    selected_tags = request.GET.getlist('tags')
    if selected_tags:
        games = games.filter(tags__id__in=selected_tags).distinct()


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
    categories = Category.objects.all()
    tags = Tag.objects.all()

    # Get featured games with screenshots for hero slideshow (limit to 8)
    featured_games = Game.objects.filter(screenshot_url__isnull=False).exclude(screenshot_url='')[:8]

    # Add promotion information to games
    from .promotion_views import get_active_promotions_for_game, calculate_best_price
    for game in games:
        discounted_price, promotion = calculate_best_price(game)
        game.discounted_price = discounted_price
        game.has_promotion = promotion is not None
        game.active_promotion = promotion
        if promotion:
            if promotion.discount_type == 'percentage':
                game.discount_label = f'{int(promotion.discount_value)}% OFF'
            else:
                game.discount_label = f'${promotion.discount_value} OFF'

    # Filter display info
    filter_type = ''
    filter_value = ''
    if selected_tags:
        filter_type = 'tag'
        filter_value = ','.join(Tag.objects.filter(id__in=selected_tags).values_list('name',flat=True))
    elif category:
        filter_type = 'category'
        filter_value = category


    # Check if the request wants JSON output
    if request.GET.get('format') == 'json':
        game_list_json = [
            {
                "id": g.id,
                "title": g.title,
                "description": g.description,
                "category": g.category,
                "price": str(g.price),
                "screenshot_url": g.screenshot_url,
                "file_url": g.file_url,
                "upload_date": g.upload_date.isoformat(),
                "tags": [gt.tag.name for gt in g.gametag_set.all()],
                "games": games,
                "wishlist_game_ids": wishlist_game_ids,
            }
            for g in games
        ]
        return JsonResponse(game_list_json,safe=False)

    return render(request, 'store/game_list.html', {
        'games': games,
        'categories': categories,
        'tags': tags,
        'search_query': search_query,
        'selected_category': category,
        'selected_tags': selected_tags,
        'selected_sort': sort_by,
        'min_price': min_price,
        'max_price': max_price,
        'start_date': start_date,
        'end_date': end_date,
        'featured_games': featured_games,
        'filter_type': filter_type,
        'filter_value': filter_value,
        'wishlist_game_ids': wishlist_game_ids,
    })


@login_required
def wishlist(request):
    """
    Display all games the user has added to their wishlist.
    """

    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('game')

    games = [item.game for item in wishlist_items]

    return render(request, 'store/wishlist.html', {
        'wishlist_items': wishlist_items,
        'games': games,
    })

@login_required
@require_POST
def wishlist_remove(request, game_id):
    wishlist_item = get_object_or_404(Wishlist, user=request.user, game_id=game_id)
    wishlist_item.delete()
    return redirect('store:wishlist')


def game_search(request):
    """
    GET /api/games/search/?q=
    Searches games by title, description, category, or tag name.
    Returns JSON list of matching games.
    """

    query = request.GET.get('q','').strip()
    if not query:
        return JsonResponse({"results": [], "message": "No search query provided."}, status=200)

    games = Game.objects.filter(
        Q(title__icontains=query) |
        Q(description__icontains=query) |
        Q(category__name__icontains=query) |
        Q(gametag__tag__name__icontains=query)
    ).distinct()

    results = [
        {
            "id": g.id,
            "title": g.title,
            "description": g.description,
            "category": g.category,
            "price": str(g.price),
            "screenshot_url": g.screenshot_url,
            # "file_url": g.file_url,
            "upload_date": g.upload_date.isoformat(),
            "tags": [gt.tag.name for gt in g.gametag_set.all()],
        }
        for g in games
    ]

    if not results:
        return JsonResponse({"results": [], "message": "No games found for your search"}, status=200)

    return JsonResponse({"results": results}, status=200)


def games_by_tag(request, tag_id):
    """
    Display a list of games that have the selected tag.
    """
    tag = get_object_or_404(Tag, id=tag_id)
    games = tag.games.all()  # uses the related_name from Game.tags

    return render(request, 'store/game_list.html', {
        'games': games,
        'filter_type': 'tag',
        'filter_value': tag.name,
        'categories': Category.objects.all()
    })


def game_detail(request, game_id):
    """
    Display details of a single game.
    """
    game = get_object_or_404(Game, id=game_id)
    
    # Add promotion information
    from .promotion_views import get_active_promotions_for_game, calculate_best_price
    discounted_price, promotion = calculate_best_price(game)
    game.discounted_price = discounted_price
    game.has_promotion = promotion is not None
    game.active_promotion = promotion
    if promotion:
        if promotion.discount_type == 'percentage':
            game.discount_label = f'{int(promotion.discount_value)}% OFF'
            game.savings_amount = game.price - discounted_price
            game.savings_percentage = promotion.discount_value
        else:
            game.discount_label = f'${promotion.discount_value} OFF'
            game.savings_amount = promotion.discount_value
            game.savings_percentage = (promotion.discount_value / game.price * 100) if game.price > 0 else 0
    
    return render(request, 'store/game_detail.html', {
        'game': game
    })


@login_required
def cart_view(request):
    """
    Display user's shopping cart with promotional pricing.
    """
    # Get or create active cart for user
    cart, created = Cart.objects.get_or_create(
        user=request.user,
        status='active'
    )
    
    cart_items = cart.items.all()
    
    # Add promotion information to cart items
    from .promotion_views import calculate_best_price
    total = Decimal('0.00')
    original_total = Decimal('0.00')
    total_savings = Decimal('0.00')
    
    for item in cart_items:
        discounted_price, promotion = calculate_best_price(item.game)
        item.discounted_price = discounted_price
        item.has_promotion = promotion is not None
        item.active_promotion = promotion
        item.item_total = discounted_price * item.quantity
        item.original_item_total = item.price_at_addition * item.quantity
        item.item_savings = item.original_item_total - item.item_total
        
        total += item.item_total
        original_total += item.original_item_total
        total_savings += item.item_savings
    
    return render(request, 'store/cart.html', {
        'cart': cart,
        'cart_items': cart_items,
        'total': total,
        'original_total': original_total,
        'total_savings': total_savings,
        'has_discounts': total_savings > 0,
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
    Auto-generates game keys for each purchased item.
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
        # Import promotion helpers
        from .promotion_views import calculate_best_price
        from .models import PromotionUsage
        
        # Calculate total with promotions applied
        total = Decimal('0.00')
        items_with_prices = []
        
        for cart_item in cart_items:
            # Check for active promotions
            discounted_price, promotion = calculate_best_price(cart_item.game)
            final_price = discounted_price * cart_item.quantity
            total += final_price
            
            items_with_prices.append({
                'cart_item': cart_item,
                'final_price': discounted_price,
                'promotion': promotion,
                'original_price': cart_item.price_at_addition
            })
        
        # Create transaction
        transaction = Transaction.objects.create(
            user=request.user,
            total_amount=total,
            payment_status='completed'  # In a real app, this would be 'pending' until payment
        )
        
        # Create transaction items from cart items and track promotion usage
        for item_data in items_with_prices:
            cart_item = item_data['cart_item']
            transaction_item = TransactionItem.objects.create(
                transaction=transaction,
                game=cart_item.game,
                price_at_purchase=item_data['final_price']  # Store discounted price
            )
            # Auto-generate game key for each purchased item
            transaction_item.generate_game_key()
            
            # Track promotion usage if applicable
            if item_data['promotion']:
                PromotionUsage.objects.create(
                    promotion=item_data['promotion'],
                    transaction=transaction,
                    game=cart_item.game,
                    original_price=item_data['original_price'],
                    discounted_price=item_data['final_price'],
                    discount_amount=item_data['original_price'] - item_data['final_price']
                )
        
        # Mark cart as checked out
        cart.status = 'checked_out'
        cart.save()
        
        messages.success(request, 'Purchase completed successfully! Check your transaction details for game keys.')
        return redirect('store:transaction_detail', transaction_id=transaction.id)
    
    # GET request - show checkout confirmation with promotional pricing
    from .promotion_views import calculate_best_price
    
    total = Decimal('0.00')
    original_total = Decimal('0.00')
    total_savings = Decimal('0.00')
    
    # Calculate promotional prices for each item
    for item in cart_items:
        discounted_price, promotion = calculate_best_price(item.game)
        item.discounted_price = discounted_price
        item.has_promotion = promotion is not None
        item.active_promotion = promotion
        item.item_total = discounted_price * item.quantity
        item.original_item_total = item.price_at_addition * item.quantity
        item.item_savings = item.original_item_total - item.item_total
        
        total += item.item_total
        original_total += item.original_item_total
        total_savings += item.item_savings
    
    return render(request, 'store/checkout.html', {
        'cart': cart,
        'cart_items': cart_items,
        'total': total,
        'original_total': original_total,
        'total_savings': total_savings,
        'has_discounts': total_savings > 0,
    })


@login_required
def transaction_history(request):
    """
    Display user's transaction history with filtering and search.
    Module 13: Purchase History and Viewing for Users
    
    Supports:
    - Search by game title: ?search=game_name
    - Filter by status: ?status=completed
    - Filter by date range: ?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
    - Sort by: ?sort=date_desc (default), date_asc, amount_desc, amount_asc
    """
    transactions = Transaction.objects.filter(user=request.user)
    
    # Search by game title in transaction items
    search_query = request.GET.get('search', '').strip()
    if search_query:
        transactions = transactions.filter(
            items__game__title__icontains=search_query
        ).distinct()
    
    # Filter by payment status
    status = request.GET.get('status', '')
    if status and status in ['pending', 'completed', 'failed', 'refunded']:
        transactions = transactions.filter(payment_status=status)
    
    # Filter by date range
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    if start_date:
        transactions = transactions.filter(transaction_date__date__gte=start_date)
    if end_date:
        transactions = transactions.filter(transaction_date__date__lte=end_date)
    
    # Sorting
    sort_by = request.GET.get('sort', 'date_desc')
    if sort_by == 'date_asc':
        transactions = transactions.order_by('transaction_date')
    elif sort_by == 'amount_desc':
        transactions = transactions.order_by('-total_amount')
    elif sort_by == 'amount_asc':
        transactions = transactions.order_by('total_amount')
    else:  # date_desc (default)
        transactions = transactions.order_by('-transaction_date')
    
    # Calculate summary statistics
    total_spent = transactions.filter(payment_status='completed').aggregate(
        total=Sum('total_amount')
    )['total'] or Decimal('0.00')
    
    total_games = TransactionItem.objects.filter(
        transaction__user=request.user,
        transaction__payment_status='completed'
    ).count()
    
    return render(request, 'store/transaction_history.html', {
        'transactions': transactions,
        'search_query': search_query,
        'selected_status': status,
        'start_date': start_date,
        'end_date': end_date,
        'sort_by': sort_by,
        'total_spent': total_spent,
        'total_games': total_games,
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
    Verify they own the game before allowing download using middleware.
    """
    # Use middleware for purchase validation
    has_access, transaction = PurchaseValidationMiddleware.verify_game_ownership(
        request.user, game_id
    )
    
    if not has_access:
        messages.error(request, 'You do not own this game.')
        return redirect('store:transaction_history')
    
    game = get_object_or_404(Game, id=game_id)
    
    # In a real app, this would redirect to a secure download URL or serve the file
    # For now, just redirect to the file_url if it exists
    if game.file_url:
        messages.success(request, f'Starting download for {game.title}')
        return redirect(game.file_url)
    else:
        messages.error(request, 'Download not available for this game.')
        return redirect('store:transaction_detail', transaction_id=transaction_id)


@login_required
@require_http_methods(["POST"])
def send_game_key(request, transaction_id, item_id):
    """
    API endpoint to send game key email to user.
    POST /store/transactions/:transaction_id/items/:item_id/send-key/
    
    Module 5: Secure Game Delivery
    """
    # Verify ownership - user must own this transaction
    transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)
    transaction_item = get_object_or_404(TransactionItem, id=item_id, transaction=transaction)
    
    # Send email using email service
    success, message = send_game_key_email(transaction_item)
    
    if success:
        messages.success(request, message)
        return JsonResponse({
            'success': True,
            'message': message,
            'game_key': transaction_item.game_key,
            'sent_at': transaction_item.key_sent_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    else:
        return JsonResponse({
            'success': False,
            'error': message
        }, status=500)


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
    total_transactions = Transaction.objects.filter(payment_status='completed').count()
    total_sales = Transaction.objects.filter(payment_status='completed').aggregate(
        total=Sum('total_amount')
    )['total'] or Decimal('0.00')
    
    # Get most downloaded games
    most_downloaded = TransactionItem.objects.values('game__title', 'game__id').annotate(
        download_count=Count('id')
    ).order_by('-download_count')[:5]
    
    recent_actions = AdminActionLog.objects.all()[:10]
    
    return render(request, 'store/admin_dashboard.html', {
        'total_games': total_games,
        'total_users': total_users,
        'total_transactions': total_transactions,
        'total_sales': total_sales,
        'most_downloaded': most_downloaded,
        'recent_actions': recent_actions,
    })


@login_required
def admin_users_page(request):
    """
    Admin view to manage users.
    Only accessible to admin users.
    """
    if not request.user.is_admin:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('store:game_list')
    
    return render(request, 'store/admin_users.html')


@login_required
def admin_transactions_page(request):
    """
    Admin view to view all transactions.
    Only accessible to admin users.
    """
    if not request.user.is_admin:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('store:game_list')
    
    return render(request, 'store/admin_transactions.html')


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

    categories = Category.objects.all()  # fetch all categories
    tags = Tag.objects.all()

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        category_id = request.POST.get('category')
        price = request.POST.get('price')
        screenshot_url = request.POST.get('screenshot_url')
        file_url = request.POST.get('file_url')
        tag_ids = request.POST.getlist('tags')

        # Simple validation
        if not all([title, description, category_id, price]):
            messages.error(request, 'All required fields must be filled.')
            return render(request, 'store/admin_game_form.html', {
                "categories": categories,
                "tags": tags
            })

        try:
            # Fetch the actual Category instance
            category_instance = Category.objects.get(id=int(category_id))

            game = Game.objects.create(
                title=title,
                description=description,
                category=category_instance,
                price=Decimal(price),
                screenshot_url=screenshot_url if screenshot_url else None,
                file_url=file_url if file_url else None,
            )

            # Add tags
            if tag_ids:
                game.tags.set(Tag.objects.filter(id__in=tag_ids))

            # Log admin action
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
    
    return render(request, 'store/admin_game_form.html', {
        "categories": categories,
        "tags": tags
    })


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
    categories = Category.objects.all()
    tags = Tag.objects.all()

    if request.method == 'POST':
        game.title = request.POST.get('title')
        game.description = request.POST.get('description')
        game.category_id = request.POST.get('category')
        game.price = Decimal(request.POST.get('price'))
        screenshot_url = request.POST.get('screenshot_url')
        file_url = request.POST.get('file_url')
        game.tag_ids = request.POST.getlist('tags')

        if game.category_id:
            game.category = Category.objects.get(id=int(game.category_id))
        if screenshot_url:
            game.screenshot_url = screenshot_url
        if file_url:
            game.file_url = file_url
        
        try:
            game.save()
            game.tags.set(Tag.objects.filter(id__in=game.tag_ids))

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
        'categories': categories,
        'tags': tags,
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


# Admin API Endpoints for Module 7
@login_required
def api_admin_dashboard_stats(request):
    """
    API endpoint to get dashboard statistics.
    Returns: total users, total sales (revenue), total transactions, most downloaded games
    """
    if not request.user.is_admin:
        return JsonResponse({
            'success': False,
            'error': 'Unauthorized: Admin access required'
        }, status=403)
    
    try:
        # Calculate statistics
        total_users = User.objects.count()
        total_transactions = Transaction.objects.filter(payment_status='completed').count()
        total_sales = Transaction.objects.filter(payment_status='completed').aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0.00')
        
        # Get most downloaded/purchased games
        most_downloaded = TransactionItem.objects.values('game__title', 'game__id').annotate(
            download_count=Count('id')
        ).order_by('-download_count')[:5]
        
        most_downloaded_games = [
            {
                'id': item['game__id'],
                'title': item['game__title'],
                'downloads': item['download_count']
            }
            for item in most_downloaded
        ]
        
        return JsonResponse({
            'success': True,
            'stats': {
                'total_users': total_users,
                'total_transactions': total_transactions,
                'total_sales': float(total_sales),
                'most_downloaded_games': most_downloaded_games
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def api_admin_users(request):
    """
    API endpoint to get list of all users (admin only).
    GET /api/users
    Returns: list of users with id, username, email, is_admin, registration_date
    """
    if not request.user.is_admin:
        return JsonResponse({
            'success': False,
            'error': 'Unauthorized: Admin access required'
        }, status=403)
    
    try:
        # Get query parameters for filtering/search
        search = request.GET.get('search', '')
        role = request.GET.get('role', '')
        
        # Build query
        users = User.objects.all()
        
        if search:
            users = users.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search)
            )
        
        if role == 'admin':
            users = users.filter(is_admin=True)
        elif role == 'user':
            users = users.filter(is_admin=False)
        
        # Order by registration date (newest first)
        users = users.order_by('-registration_date')
        
        # Serialize user data
        users_data = [
            {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_admin': user.is_admin,
                'registration_date': user.registration_date.strftime('%Y-%m-%d %H:%M:%S'),
                'last_login': user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else None,
                'is_active': user.is_active
            }
            for user in users
        ]
        
        return JsonResponse({
            'success': True,
            'users': users_data,
            'total': len(users_data)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def api_admin_transactions(request):
    """
    API endpoint to get list of all transactions (admin only).
    GET /api/transactions
    Returns: list of transactions with details, user info, items, amounts
    """
    if not request.user.is_admin:
        return JsonResponse({
            'success': False,
            'error': 'Unauthorized: Admin access required'
        }, status=403)
    
    try:
        # Get query parameters for filtering
        status = request.GET.get('status', '')
        user_id = request.GET.get('user_id', '')
        start_date = request.GET.get('start_date', '')
        end_date = request.GET.get('end_date', '')
        
        # Build query
        transactions = Transaction.objects.all()
        
        if status:
            transactions = transactions.filter(payment_status=status)
        
        if user_id:
            transactions = transactions.filter(user_id=user_id)
        
        if start_date:
            transactions = transactions.filter(transaction_date__date__gte=start_date)
        
        if end_date:
            transactions = transactions.filter(transaction_date__date__lte=end_date)
        
        # Order by transaction date (newest first)
        transactions = transactions.order_by('-transaction_date')
        
        # Serialize transaction data
        transactions_data = []
        for transaction in transactions:
            items = []
            for item in transaction.items.all():
                items.append({
                    'game_id': item.game.id,
                    'game_title': item.game.title,
                    'price': float(item.price_at_purchase)
                })
            
            transactions_data.append({
                'id': transaction.id,
                'user_id': transaction.user.id,
                'username': transaction.user.username,
                'user_email': transaction.user.email,
                'transaction_date': transaction.transaction_date.strftime('%Y-%m-%d %H:%M:%S'),
                'total_amount': float(transaction.total_amount),
                'payment_status': transaction.payment_status,
                'items': items,
                'items_count': len(items)
            })
        
        return JsonResponse({
            'success': True,
            'transactions': transactions_data,
            'total': len(transactions_data)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ========================================
# Review API Endpoints (Module 11)
# ========================================

def api_get_game_reviews(request, game_id):
    """
    Get all reviews for a specific game.
    Public endpoint - no login required.
    GET /api/reviews/<game_id>/
    """
    try:
        game = get_object_or_404(Game, id=game_id)
        reviews = Review.objects.filter(game=game).select_related('user')
        
        reviews_data = []
        for review in reviews:
            reviews_data.append({
                'id': review.id,
                'user_id': review.user.id,
                'username': review.user.username,
                'rating': review.rating,
                'review_text': review.review_text,
                'created_at': review.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': review.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                'is_owner': request.user.is_authenticated and review.user == request.user
            })
        
        # Get rating statistics
        rating_stats = Review.get_rating_stats(game)
        
        return JsonResponse({
            'success': True,
            'reviews': reviews_data,
            'stats': {
                'average_rating': rating_stats['avg_rating'],
                'total_reviews': rating_stats['total_reviews'],
                'rating_breakdown': {
                    '5': rating_stats['five_star'],
                    '4': rating_stats['four_star'],
                    '3': rating_stats['three_star'],
                    '2': rating_stats['two_star'],
                    '1': rating_stats['one_star']
                }
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def api_create_review(request, game_id):
    """
    Create a new review for a game.
    Requires login. User can only have one review per game.
    POST /api/reviews/<game_id>/
    Body: { "rating": 1-5, "review_text": "optional text" }
    """
    try:
        game = get_object_or_404(Game, id=game_id)
        
        # Parse JSON body
        data = json.loads(request.body)
        rating = data.get('rating')
        review_text = data.get('review_text', '').strip()
        
        # Validate rating
        if not rating or rating not in [1, 2, 3, 4, 5]:
            return JsonResponse({
                'success': False,
                'error': 'Rating must be between 1 and 5'
            }, status=400)
        
        # Check if user already reviewed this game
        existing_review = Review.objects.filter(user=request.user, game=game).first()
        if existing_review:
            return JsonResponse({
                'success': False,
                'error': 'You have already reviewed this game. Use the edit endpoint to update your review.'
            }, status=400)
        
        # Create review
        review = Review.objects.create(
            user=request.user,
            game=game,
            rating=rating,
            review_text=review_text
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Review created successfully',
            'review': {
                'id': review.id,
                'username': review.user.username,
                'rating': review.rating,
                'review_text': review.review_text,
                'created_at': review.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        })
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["PUT"])
def api_update_review(request, review_id):
    """
    Update user's own review.
    PUT /api/reviews/<review_id>/
    Body: { "rating": 1-5, "review_text": "optional text" }
    """
    try:
        review = get_object_or_404(Review, id=review_id)
        
        # Check ownership
        if review.user != request.user:
            return JsonResponse({
                'success': False,
                'error': 'You can only edit your own reviews'
            }, status=403)
        
        # Parse JSON body
        data = json.loads(request.body)
        rating = data.get('rating')
        review_text = data.get('review_text', '').strip()
        
        # Validate rating
        if rating and rating not in [1, 2, 3, 4, 5]:
            return JsonResponse({
                'success': False,
                'error': 'Rating must be between 1 and 5'
            }, status=400)
        
        # Update review
        if rating:
            review.rating = rating
        if 'review_text' in data:  # Allow empty string
            review.review_text = review_text
        review.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Review updated successfully',
            'review': {
                'id': review.id,
                'rating': review.rating,
                'review_text': review.review_text,
                'updated_at': review.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        })
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["DELETE"])
def api_delete_review(request, review_id):
    """
    Delete user's own review.
    DELETE /api/reviews/<review_id>/
    """
    try:
        review = get_object_or_404(Review, id=review_id)
        
        # Check ownership
        if review.user != request.user:
            return JsonResponse({
                'success': False,
                'error': 'You can only delete your own reviews'
            }, status=403)
        
        game_title = review.game.title
        review.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Review for {game_title} deleted successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def api_get_game_rating_stats(request, game_id):
    """
    Get rating statistics for a game.
    Public endpoint.
    GET /api/reviews/<game_id>/stats/
    """
    try:
        game = get_object_or_404(Game, id=game_id)
        stats = Review.get_rating_stats(game)
        
        return JsonResponse({
            'success': True,
            'stats': {
                'average_rating': stats['avg_rating'],
                'total_reviews': stats['total_reviews'],
                'rating_breakdown': {
                    '5': stats['five_star'],
                    '4': stats['four_star'],
                    '3': stats['three_star'],
                    '2': stats['two_star'],
                    '1': stats['one_star']
                }
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET", "POST"])
def api_wishlist(request):
    """
    GET /store/api/wishlist/ -> list wishlist items for current user
    POST /store/api/wishlist/ -> add a game to wishlist (JSON body: {"game_id": int})
    """
    try:
        if request.method == 'GET':
            items = Wishlist.objects.filter(user=request.user).select_related('game')
            data = [wishlist_to_dict(it) for it in items]
            return JsonResponse({'success': True, 'data': data})

        # POST
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

        game_id = payload.get('game_id') or payload.get('game')
        if not game_id:
            return JsonResponse({'success': False, 'error': 'Missing game_id'}, status=400)

        game = get_object_or_404(Game, id=game_id)

        # Prevent duplicates
        if Wishlist.objects.filter(user=request.user, game=game).exists():
            return JsonResponse({'success': False, 'error': 'Game already in wishlist'}, status=400)

        item = Wishlist.objects.create(user=request.user, game=game)
        return JsonResponse({'success': True, 'message': f'{game.title} added to wishlist', 'data': wishlist_to_dict(item)}, status=201)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["DELETE", "POST"])  # allow POST for forms that can't send DELETE
def api_wishlist_delete(request, game_id):
    """
    DELETE /store/api/wishlist/<game_id>/ -> remove game from wishlist for current user
    Also accepts POST to support form-based removal.
    """
    try:
        wishlist_item = Wishlist.objects.filter(user=request.user, game_id=game_id).first()
        if not wishlist_item:
            return JsonResponse({'success': False, 'error': 'Not found'}, status=404)
        game_title = wishlist_item.game.title
        wishlist_item.delete()
        return JsonResponse({'success': True, 'message': f'{game_title} removed from wishlist'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def api_users_list(request):
    """
    GET /store/api/users/ -> list all users (admin only)
    Supports search and role filtering
    """
    if not request.user.is_admin:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    
    try:
        users = User.objects.all().order_by('-registration_date')
        
        # Search filter
        search = request.GET.get('search', '').strip()
        if search:
            users = users.filter(
                Q(username__icontains=search) | Q(email__icontains=search)
            )
        
        # Role filter
        role = request.GET.get('role', '').strip()
        if role == 'admin':
            users = users.filter(is_admin=True)
        elif role == 'user':
            users = users.filter(is_admin=False)
        
        users_data = [{
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_admin': user.is_admin,
            'is_active': user.is_active,
            'registration_date': user.registration_date.isoformat() if user.registration_date else None,
            'last_login': user.last_login.isoformat() if user.last_login else None,
        } for user in users]
        
        return JsonResponse({
            'success': True,
            'users': users_data,
            'total': len(users_data)
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def api_grant_admin(request, user_id):
    """
    POST /store/api/users/<user_id>/grant-admin/ -> grant admin privileges to user
    Admin only
    """
    if not request.user.is_admin:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    
    try:
        target_user = get_object_or_404(User, id=user_id)
        
        if target_user.is_admin:
            return JsonResponse({'success': False, 'error': 'User is already an admin'}, status=400)
        
        target_user.is_admin = True
        target_user.save()
        
        # Log the action
        AdminActionLog.objects.create(
            admin=request.user,
            action_type='other',
            notes=f'Granted admin privileges to user: {target_user.username}'
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Successfully granted admin privileges to {target_user.username}'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

"""
Simple authentication views for GameVault.
Uses Django's built-in session-based authentication.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .models import User


@require_http_methods(["GET", "POST"])
def register_view(request):
    """
    User registration view.
    GET: Display registration form
    POST: Process registration
    """
    if request.user.is_authenticated:
        return redirect('store:game_list')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        # Simple validation
        if not all([username, email, password, password_confirm]):
            messages.error(request, 'All fields are required.')
            return render(request, 'users/register.html')
        
        if password != password_confirm:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'users/register.html')
        
        # Check if username or email already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'users/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'users/register.html')
        
        # Create user
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            user.save()
            
            # Log the user in
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('store:game_list')
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            return render(request, 'users/register.html')
    
    return render(request, 'users/register.html')


@require_http_methods(["GET", "POST"])
def login_view(request):
    """
    User login view.
    GET: Display login form
    POST: Process login
    """
    if request.user.is_authenticated:
        return redirect('store:game_list')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            messages.error(request, 'Username and password are required.')
            return render(request, 'users/login.html')
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful!')
            # Redirect to next page if specified, otherwise to game list
            next_url = request.GET.get('next', 'store:game_list')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
            return render(request, 'users/login.html')
    
    return render(request, 'users/login.html')


@login_required
def logout_view(request):
    """
    User logout view.
    Logs out the user and redirects to login page.
    """
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('users:login')


@login_required
def profile_view(request):
    """
    User profile view.
    Display user information and transaction history.
    """
    return render(request, 'users/profile.html', {
        'user': request.user
    })

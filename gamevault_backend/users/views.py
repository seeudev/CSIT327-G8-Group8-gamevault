"""
Simple authentication views for GameVault.
Uses Django's built-in session-based authentication.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import json
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


@login_required
@require_http_methods(["PUT"])
def update_profile_api(request, user_id):
    """
    API endpoint to update user profile.
    PUT /api/users/:id
    Requires authentication and authorization (users can only update their own profile).
    """
    # Authorization check - users can only update their own profile
    if request.user.id != user_id:
        return JsonResponse({
            'success': False,
            'error': 'Unauthorized: You can only update your own profile'
        }, status=403)
    
    try:
        # Parse JSON data from request body
        data = json.loads(request.body)
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        
        user = request.user
        
        # Validation
        errors = {}
        
        # Validate username
        if username:
            if username != user.username:
                if User.objects.filter(username=username).exists():
                    errors['username'] = 'Username already exists'
                else:
                    user.username = username
        
        # Validate email
        if email:
            if email != user.email:
                if User.objects.filter(email=email).exists():
                    errors['email'] = 'Email already exists'
                else:
                    user.email = email
        
        # Validate password change
        if new_password:
            if not current_password:
                errors['current_password'] = 'Current password is required to set a new password'
            elif not user.check_password(current_password):
                errors['current_password'] = 'Current password is incorrect'
            else:
                # Validate new password strength
                try:
                    validate_password(new_password, user)
                    user.set_password(new_password)
                    # Update session to prevent logout after password change
                    update_session_auth_hash(request, user)
                except ValidationError as e:
                    errors['new_password'] = list(e.messages)
        
        # If there are validation errors, return them
        if errors:
            return JsonResponse({
                'success': False,
                'errors': errors
            }, status=400)
        
        # Save user changes
        user.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Profile updated successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
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
def delete_account_api(request, user_id):
    """
    API endpoint to delete user account.
    DELETE /api/users/:id
    Requires authentication and authorization (users can only delete their own account).
    """
    # Authorization check - users can only delete their own account
    if request.user.id != user_id:
        return JsonResponse({
            'success': False,
            'error': 'Unauthorized: You can only delete your own account'
        }, status=403)
    
    try:
        user = request.user
        
        # Log the user out before deleting
        logout(request)
        
        # Delete the user account
        user.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Account deleted successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

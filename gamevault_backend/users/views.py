"""
Simple authentication views for GameVault.
Uses Django's built-in session-based authentication.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import json
from .models import User, PasswordResetToken, LoginAttempt
from .email_service import send_password_reset_email
from store.models import Game


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@require_http_methods(["GET", "POST"])
def register_view(request):
    """
    User registration view.
    GET: Display registration form
    POST: Process registration
    """
    if request.user.is_authenticated:
        return redirect('store:game_list')
    
    # Get featured games with screenshots for background grid
    # (moved to top so it's available for both GET and POST error responses)
    featured_games = list(Game.objects.filter(screenshot_url__isnull=False).exclude(screenshot_url='')[:5])

    # Build a grid_images list of screenshot URLs, repeating the available
    # screenshots until we have at least 9 tiles (3x3 mosaic). This keeps
    # the grid looking full on wider screens even when the DB has few games.
    grid_images = []
    if featured_games:
        urls = [g.screenshot_url for g in featured_games]
        while len(grid_images) < 9:
            grid_images.extend(urls)
        grid_images = grid_images[:9]
    else:
        grid_images = []

    context = {
        'featured_games': featured_games,
        'grid_images': grid_images,
    }
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        # Simple validation
        if not all([username, email, password, password_confirm]):
            messages.error(request, 'All fields are required.')
            return render(request, 'users/register.html', context)
        
        if password != password_confirm:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'users/register.html', context)
        
        # Check if username or email already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'users/register.html', context)
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'users/register.html', context)
        
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
            return render(request, 'users/register.html', context)

    return render(request, 'users/register.html', context)


@require_http_methods(["GET", "POST"])
def login_view(request):
    """
    User login view with failed attempt tracking and lockout.
    GET: Display login form
    POST: Process login
    - Tracks failed login attempts
    - Implements 15-minute lockout after 4 failed attempts
    - Clears password field on failed login (frontend)
    """
    if request.user.is_authenticated:
        return redirect('store:game_list')
    
    # Get featured games with screenshots for background grid
    featured_games = list(Game.objects.filter(screenshot_url__isnull=False).exclude(screenshot_url='')[:5])

    # Build grid_images (repeat to at least 9 tiles)
    grid_images = []
    if featured_games:
        urls = [g.screenshot_url for g in featured_games]
        while len(grid_images) < 9:
            grid_images.extend(urls)
        grid_images = grid_images[:9]
    else:
        grid_images = []

    context = {
        'featured_games': featured_games,
        'grid_images': grid_images,
    }
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password')
        
        if not username or not password:
            messages.error(request, 'Username and password are required.')
            return render(request, 'users/login.html', context)
        
        # Check if user is locked out
        is_locked, remaining_seconds = LoginAttempt.is_locked_out(username)
        if is_locked:
            remaining_minutes = (remaining_seconds // 60) + 1
            messages.error(
                request, 
                f'Too many failed login attempts. Please try again in {remaining_minutes} minute(s).'
            )
            context['locked_out'] = True
            context['remaining_seconds'] = remaining_seconds
            return render(request, 'users/login.html', context)
        
        # Get client IP for logging
        ip_address = get_client_ip(request)
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Successful login
            LoginAttempt.record_attempt(username, ip_address, successful=True)
            LoginAttempt.clear_attempts(username)  # Clear failed attempts
            login(request, user)
            messages.success(request, 'Login successful!')
            # Redirect to next page if specified, otherwise to game list
            next_url = request.GET.get('next', 'store:game_list')
            return redirect(next_url)
        else:
            # Failed login - record attempt
            LoginAttempt.record_attempt(username, ip_address, successful=False)
            
            # Get updated failed attempt count
            failed_count = LoginAttempt.get_failed_attempts(username)
            max_attempts = 4
            remaining_attempts = max_attempts - failed_count
            
            if remaining_attempts > 0:
                messages.error(
                    request, 
                    f'Invalid username or password. {remaining_attempts} attempt(s) remaining before lockout.'
                )
            else:
                messages.error(
                    request, 
                    'Invalid username or password. Account temporarily locked due to too many failed attempts.'
                )
                context['locked_out'] = True
                context['remaining_seconds'] = 15 * 60  # 15 minutes in seconds
            
            context['clear_password'] = True  # Signal to clear password field
            return render(request, 'users/login.html', context)

    return render(request, 'users/login.html', context)


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


@require_http_methods(["GET", "POST"])
def password_reset_request(request):
    """
    Password reset request view.
    GET: Display password reset request form
    POST: Generate reset token and send email (API endpoint)
    """
    if request.method == 'POST':
        try:
            # Handle both form data and JSON
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                email = data.get('email', '').strip()
            else:
                email = request.POST.get('email', '').strip()
            
            if not email:
                if request.content_type == 'application/json':
                    return JsonResponse({
                        'success': False,
                        'error': 'Email is required'
                    }, status=400)
                messages.error(request, 'Email is required.')
                return render(request, 'users/forgot_password.html')
            
            # Check if user exists
            try:
                user = User.objects.get(email=email)
                
                # Create password reset token
                token = PasswordResetToken.create_token(user)
                
                # Send password reset email
                success, message = send_password_reset_email(user, token)
                
                if not success:
                    if request.content_type == 'application/json':
                        return JsonResponse({
                            'success': False,
                            'error': message
                        }, status=500)
                    messages.error(request, message)
                    return render(request, 'users/forgot_password.html')
                
            except User.DoesNotExist:
                # Don't reveal if user exists or not for security
                pass
            
            # Always show success message to prevent email enumeration
            if request.content_type == 'application/json':
                return JsonResponse({
                    'success': True,
                    'message': 'If an account exists with this email, a password reset link has been sent.'
                })
            
            messages.success(request, 'If an account exists with this email, a password reset link has been sent.')
            return redirect('users:login')
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            if request.content_type == 'application/json':
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                }, status=500)
            messages.error(request, f'An error occurred: {str(e)}')
            return render(request, 'users/forgot_password.html')
    
    return render(request, 'users/forgot_password.html')


@require_http_methods(["GET", "POST"])
def password_reset_confirm(request, token):
    """
    Password reset confirmation view.
    GET: Display password reset form
    POST: Validate token and update password (API endpoint)
    """
    # Get token object
    reset_token = get_object_or_404(PasswordResetToken, token=token)
    
    # Check if token is valid
    if not reset_token.is_valid():
        if request.method == 'POST' and request.content_type == 'application/json':
            return JsonResponse({
                'success': False,
                'error': 'This password reset link has expired or has already been used.'
            }, status=400)
        messages.error(request, 'This password reset link has expired or has already been used.')
        return redirect('users:password_reset_request')
    
    if request.method == 'POST':
        try:
            # Handle both form data and JSON
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                new_password = data.get('new_password', '')
                confirm_password = data.get('confirm_password', '')
            else:
                new_password = request.POST.get('new_password', '')
                confirm_password = request.POST.get('confirm_password', '')
            
            # Validate passwords
            if not new_password or not confirm_password:
                error_msg = 'Both password fields are required.'
                if request.content_type == 'application/json':
                    return JsonResponse({
                        'success': False,
                        'error': error_msg
                    }, status=400)
                messages.error(request, error_msg)
                return render(request, 'users/reset_password.html', {'token': token})
            
            if new_password != confirm_password:
                error_msg = 'Passwords do not match.'
                if request.content_type == 'application/json':
                    return JsonResponse({
                        'success': False,
                        'error': error_msg
                    }, status=400)
                messages.error(request, error_msg)
                return render(request, 'users/reset_password.html', {'token': token})
            
            # Validate password strength
            try:
                validate_password(new_password, reset_token.user)
            except ValidationError as e:
                error_msg = ' '.join(e.messages)
                if request.content_type == 'application/json':
                    return JsonResponse({
                        'success': False,
                        'error': error_msg
                    }, status=400)
                messages.error(request, error_msg)
                return render(request, 'users/reset_password.html', {'token': token})
            
            # Update user password
            user = reset_token.user
            user.set_password(new_password)
            user.save()
            
            # Mark token as used
            reset_token.is_used = True
            reset_token.save()
            
            # Success response
            if request.content_type == 'application/json':
                return JsonResponse({
                    'success': True,
                    'message': 'Password has been reset successfully. You can now login with your new password.'
                })
            
            messages.success(request, 'Password has been reset successfully. You can now login with your new password.')
            return redirect('users:login')
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            if request.content_type == 'application/json':
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                }, status=500)
            messages.error(request, f'An error occurred: {str(e)}')
            return render(request, 'users/reset_password.html', {'token': token})
    
    return render(request, 'users/reset_password.html', {'token': token})


from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import login
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction

from .models import User, Role
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    UserListSerializer,
    ChangePasswordSerializer,
    RoleSerializer
)


class UserRegistrationView(APIView):
    """
    User registration endpoint.
    Creates a new user account with role assignment.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """
        Register a new user.
        
        Expected payload:
        {
            "username": "string",
            "email": "string",
            "password": "string",
            "password_confirm": "string",
            "first_name": "string (optional)",
            "last_name": "string (optional)",
            "role_name": "string (optional, defaults to 'buyer')",
            "phone_number": "string (optional)",
            "date_of_birth": "YYYY-MM-DD (optional)",
            "bio": "string (optional)"
        }
        """
        serializer = UserRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    user = serializer.save()
                    
                    # Generate JWT tokens
                    refresh = RefreshToken.for_user(user)
                    access_token = refresh.access_token
                    
                    # Return user data with tokens
                    user_data = UserProfileSerializer(user).data
                    
                    return Response({
                        'message': 'User registered successfully',
                        'user': user_data,
                        'tokens': {
                            'access': str(access_token),
                            'refresh': str(refresh)
                        }
                    }, status=status.HTTP_201_CREATED)
                    
            except Exception as e:
                return Response({
                    'error': 'Registration failed',
                    'details': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'error': 'Invalid data',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    """
    User login endpoint.
    Authenticates user and returns JWT tokens.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """
        Login user with username/email and password.
        
        Expected payload:
        {
            "username": "string (username or email)",
            "password": "string"
        }
        """
        serializer = UserLoginSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            
            # Update last login IP
            user.last_login_ip = self.get_client_ip(request)
            user.save(update_fields=['last_login_ip'])
            
            # Return user data with tokens
            user_data = UserProfileSerializer(user).data
            
            return Response({
                'message': 'Login successful',
                'user': user_data,
                'tokens': {
                    'access': str(access_token),
                    'refresh': str(refresh)
                }
            }, status=status.HTTP_200_OK)
        
        return Response({
            'error': 'Invalid credentials',
            'details': serializer.errors
        }, status=status.HTTP_401_UNAUTHORIZED)

    def get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    User profile endpoint.
    Allows authenticated users to view and update their profile.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Return the current user's profile"""
        return self.request.user


class UserListView(generics.ListAPIView):
    """
    User list endpoint (admin only).
    Lists all users in the system.
    """
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all().select_related('role')

    def get_queryset(self):
        """Filter users based on permissions"""
        user = self.request.user
        
        # Only admins can view all users
        if not user.is_admin:
            return User.objects.none()
        
        return super().get_queryset()


class ChangePasswordView(APIView):
    """
    Change password endpoint.
    Allows authenticated users to change their password.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        Change user password.
        
        Expected payload:
        {
            "old_password": "string",
            "new_password": "string",
            "new_password_confirm": "string"
        }
        """
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Password changed successfully'
            }, status=status.HTTP_200_OK)
        
        return Response({
            'error': 'Invalid data',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """
    User logout endpoint.
    Blacklists the refresh token.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        Logout user by blacklisting refresh token.
        
        Expected payload:
        {
            "refresh": "string (refresh token)"
        }
        """
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
                
                return Response({
                    'message': 'Logout successful'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Refresh token is required'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'error': 'Invalid token',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class RoleListView(generics.ListAPIView):
    """
    Role list endpoint.
    Lists all available roles in the system.
    """
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Role.objects.all()


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_permissions(request):
    """
    Get current user's permissions.
    Returns the user's role and associated permissions.
    """
    user = request.user
    
    if not user.role:
        return Response({
            'role': None,
            'permissions': {},
            'is_admin': False,
            'is_buyer': False
        })
    
    return Response({
        'role': RoleSerializer(user.role).data,
        'permissions': user.role.permissions,
        'is_admin': user.is_admin,
        'is_buyer': user.is_buyer
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def verify_token(request):
    """
    Verify if the current JWT token is valid.
    Returns user information if token is valid.
    """
    user = request.user
    user_data = UserProfileSerializer(user).data
    
    return Response({
        'valid': True,
        'user': user_data
    })

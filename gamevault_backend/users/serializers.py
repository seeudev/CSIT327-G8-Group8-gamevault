from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User, Role


class RoleSerializer(serializers.ModelSerializer):
    """
    Serializer for Role model.
    Used for displaying role information in API responses.
    """
    class Meta:
        model = Role
        fields = ['id', 'name', 'display_name', 'description', 'permissions']
        read_only_fields = ['id']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Handles user creation with password validation and role assignment.
    """
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'},
        help_text="Password must be at least 8 characters long"
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text="Confirm your password"
    )
    role_name = serializers.CharField(
        write_only=True,
        required=False,
        help_text="Role name (defaults to 'buyer' if not provided)"
    )

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'password', 'password_confirm', 'role_name', 'phone_number',
            'date_of_birth', 'bio'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
        }

    def validate_email(self, value):
        """Validate email uniqueness"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_username(self, value):
        """Validate username uniqueness"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def validate_password(self, value):
        """Validate password using Django's password validators"""
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate(self, attrs):
        """Validate password confirmation and role assignment"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': "Passwords don't match."
            })

        # Set default role to 'buyer' if not provided
        role_name = attrs.get('role_name', 'buyer')
        try:
            role = Role.objects.get(name=role_name)
            attrs['role'] = role
        except Role.DoesNotExist:
            raise serializers.ValidationError({
                'role_name': f"Role '{role_name}' does not exist."
            })

        # Remove fields that shouldn't be saved to the model
        attrs.pop('password_confirm', None)
        attrs.pop('role_name', None)

        return attrs

    def create(self, validated_data):
        """Create a new user with hashed password"""
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    Handles authentication and returns user data with tokens.
    """
    username = serializers.CharField(
        help_text="Username or email address"
    )
    password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True
    )

    def validate(self, attrs):
        """Validate user credentials"""
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            # Try to authenticate with username first, then email
            user = authenticate(username=username, password=password)
            
            if not user:
                # Try with email if username authentication failed
                try:
                    user_obj = User.objects.get(email=username)
                    user = authenticate(username=user_obj.username, password=password)
                except User.DoesNotExist:
                    pass

            if user:
                if not user.is_active:
                    raise serializers.ValidationError(
                        "User account is disabled."
                    )
                attrs['user'] = user
                return attrs
            else:
                raise serializers.ValidationError(
                    "Unable to log in with provided credentials."
                )
        else:
            raise serializers.ValidationError(
                "Must include 'username' and 'password'."
            )


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile information.
    Used for displaying and updating user profile data.
    """
    role = RoleSerializer(read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    is_admin = serializers.BooleanField(read_only=True)
    is_buyer = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'role', 'phone_number', 'date_of_birth',
            'bio', 'avatar', 'is_verified', 'is_admin', 'is_buyer',
            'created_at', 'updated_at', 'last_login'
        ]
        read_only_fields = [
            'id', 'username', 'email', 'is_verified', 'created_at',
            'updated_at', 'last_login'
        ]

    def validate_email(self, value):
        """Validate email uniqueness (excluding current user)"""
        if self.instance and self.instance.email == value:
            return value
        
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value


class UserListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing users (admin view).
    Shows limited user information for admin panels.
    """
    role = RoleSerializer(read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'full_name', 'role',
            'is_active', 'is_verified', 'created_at', 'last_login'
        ]


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing user password.
    """
    old_password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True
    )
    new_password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True,
        min_length=8
    )
    new_password_confirm = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True
    )

    def validate_old_password(self, value):
        """Validate old password"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def validate_new_password(self, value):
        """Validate new password using Django's password validators"""
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate(self, attrs):
        """Validate password confirmation"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': "New passwords don't match."
            })
        return attrs

    def save(self):
        """Update user password"""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user

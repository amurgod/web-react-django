"""
Custom Keycloak authentication backend for Django
"""
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from keycloak_config import keycloak_openid, ROLES, PERMISSIONS
import logging

logger = logging.getLogger(__name__)

class KeycloakBackend(BaseBackend):
    """
    Custom authentication backend using Keycloak
    """
    
    def authenticate(self, request, token=None):
        """
        Authenticate user using Keycloak token
        """
        if not token:
            return None
            
        try:
            # Decode and verify the token
            token_info = keycloak_openid.decode_token(
                token,
                key=keycloak_openid.public_key(),
                options={
                    "verify_signature": True,
                    "verify_aud": False,
                    "verify_exp": True
                }
            )
            
            # Extract user information from token
            username = token_info.get('preferred_username')
            email = token_info.get('email')
            first_name = token_info.get('given_name', '')
            last_name = token_info.get('family_name', '')
            
            if not username:
                return None
                
            # Get or create Django user
            User = get_user_model()
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email or '',
                    'first_name': first_name,
                    'last_name': last_name,
                    'is_staff': self._has_role(token_info, ROLES['ADMIN']),
                    'is_superuser': self._has_role(token_info, ROLES['ADMIN'])
                }
            )
            
            # Update user information if not created
            if not created:
                user.email = email or user.email
                user.first_name = first_name or user.first_name
                user.last_name = last_name or user.last_name
                user.is_staff = self._has_role(token_info, ROLES['ADMIN'])
                user.is_superuser = self._has_role(token_info, ROLES['ADMIN'])
                user.save()
            
            # Store token info in user session (safely)
            if request and hasattr(request, 'session'):
                request.session['keycloak_token_info'] = token_info
                request.session['keycloak_token'] = token
                
            return user
            
        except Exception as e:
            logger.error(f"Keycloak authentication error: {e}")
            return None
    
    def get_user(self, user_id):
        """
        Get user by ID
        """
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
    
    def _has_role(self, token_info, role):
        """
        Check if user has specific role
        """
        realm_access = token_info.get('realm_access', {})
        roles = realm_access.get('roles', [])
        return role in roles
    
    def _get_user_roles(self, token_info):
        """
        Get all roles for user
        """
        realm_access = token_info.get('realm_access', {})
        return realm_access.get('roles', [])
    
    def has_permission(self, user, resource, action):
        """
        Check if user has permission for specific resource and action
        """
        # This method would need access to the request object to get session data
        # For now, we'll return False as this is handled by decorators
        return False 
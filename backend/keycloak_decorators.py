"""
Decorators for Keycloak role-based access control
"""
from functools import wraps
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from keycloak_config import ROLES, PERMISSIONS
import logging

logger = logging.getLogger(__name__)

def require_role(role):
    """
    Decorator to require specific role
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({'error': 'Authentication required'}, status=401)
            
            # Get user roles from session (safely)
            token_info = {}
            if hasattr(request, 'session'):
                token_info = request.session.get('keycloak_token_info', {})
            
            realm_access = token_info.get('realm_access', {})
            user_roles = realm_access.get('roles', [])
            
            if role not in user_roles:
                return JsonResponse({'error': 'Insufficient permissions'}, status=403)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def require_permission(resource, action):
    """
    Decorator to require specific permission
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({'error': 'Authentication required'}, status=401)
            
            # Get user roles from session (safely)
            token_info = {}
            if hasattr(request, 'session'):
                token_info = request.session.get('keycloak_token_info', {})
            
            realm_access = token_info.get('realm_access', {})
            user_roles = realm_access.get('roles', [])
            
            # Check if user has required permission
            required_roles = PERMISSIONS.get(resource, {}).get(action, [])
            has_permission = any(role in user_roles for role in required_roles)
            
            if not has_permission:
                return JsonResponse({'error': 'Insufficient permissions'}, status=403)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def require_any_role(*roles):
    """
    Decorator to require any of the specified roles
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({'error': 'Authentication required'}, status=401)
            
            # Get user roles from session (safely)
            token_info = {}
            if hasattr(request, 'session'):
                token_info = request.session.get('keycloak_token_info', {})
            
            realm_access = token_info.get('realm_access', {})
            user_roles = realm_access.get('roles', [])
            
            has_role = any(role in user_roles for role in roles)
            if not has_role:
                return JsonResponse({'error': 'Insufficient permissions'}, status=403)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

# DRF-specific decorators
def drf_require_role(role):
    """
    DRF decorator to require specific role
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
            
            # Get user roles from session (safely)
            token_info = {}
            if hasattr(request, 'session'):
                token_info = request.session.get('keycloak_token_info', {})
            
            realm_access = token_info.get('realm_access', {})
            user_roles = realm_access.get('roles', [])
            
            if role not in user_roles:
                return Response({'error': 'Insufficient permissions'}, status=status.HTTP_403_FORBIDDEN)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def drf_require_permission(resource, action):
    """
    DRF decorator to require specific permission
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
            
            # Get user roles from session (safely)
            token_info = {}
            if hasattr(request, 'session'):
                token_info = request.session.get('keycloak_token_info', {})
            
            realm_access = token_info.get('realm_access', {})
            user_roles = realm_access.get('roles', [])
            
            # Check if user has required permission
            required_roles = PERMISSIONS.get(resource, {}).get(action, [])
            has_permission = any(role in user_roles for role in required_roles)
            
            if not has_permission:
                return Response({'error': 'Insufficient permissions'}, status=status.HTTP_403_FORBIDDEN)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator 
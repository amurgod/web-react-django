"""
Custom permissions for role-based access control
"""
from rest_framework import permissions

class HasRolePermission(permissions.BasePermission):
    """
    Permission class that checks if user has required role
    """
    
    def has_permission(self, request, view):
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return False
            
        # Get required role from view
        required_role = getattr(view, 'required_role', None)
        if not required_role:
            return True  # No role requirement, allow access
            
        # Get user roles from token payload
        token_payload = getattr(request, 'token_payload', {})
        user_roles = token_payload.get('realm_access', {}).get('roles', [])
        
        # Check if user has required role
        return required_role in user_roles

class HasResourcePermission(permissions.BasePermission):
    """
    Permission class that checks if user has permission for specific resource and action
    """
    
    def has_permission(self, request, view):
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return False
            
        # Get required permission from view
        required_permission = getattr(view, 'required_permission', None)
        if not required_permission:
            return True  # No permission requirement, allow access
            
        # Parse required permission (format: "resource:action")
        try:
            resource, action = required_permission.split(':')
        except ValueError:
            return False
            
        # Get user roles from token payload
        token_payload = getattr(request, 'token_payload', {})
        user_roles = token_payload.get('realm_access', {}).get('roles', [])
        
        # Define permission mappings
        permissions = {
            'patient': {
                'view': ['admin', 'doctor', 'nurse', 'receptionist', 'viewer'],
                'create': ['admin', 'doctor', 'nurse', 'receptionist'],
                'update': ['admin', 'doctor', 'nurse'],
                'delete': ['admin', 'doctor']
            },
            'hospital': {
                'view': ['admin', 'doctor', 'nurse', 'receptionist', 'viewer'],
                'create': ['admin'],
                'update': ['admin'],
                'delete': ['admin']
            }
        }
        
        # Check if user has required permission
        required_roles = permissions.get(resource, {}).get(action, [])
        return any(role in user_roles for role in required_roles) 
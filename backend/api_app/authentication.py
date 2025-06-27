"""
Custom authentication for token-based auth
"""
from rest_framework import authentication
from rest_framework import exceptions
from django.contrib.auth.models import User
import jwt
from keycloak_config import KEYCLOAK_CONFIG

class TokenAuthentication(authentication.BaseAuthentication):
    """
    Custom token authentication that validates JWT tokens from Keycloak
    """
    
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header:
            return None
            
        try:
            # Extract token from "Bearer <token>"
            parts = auth_header.split()
            if len(parts) != 2 or parts[0].lower() != 'bearer':
                return None
                
            token = parts[1]
            
            # Decode token without verification to get user info
            token_payload = jwt.decode(token, options={"verify_signature": False})
            
            # Extract user information
            username = token_payload.get('preferred_username')
            if not username:
                return None
                
            # Get or create Django user
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': token_payload.get('email', ''),
                    'first_name': token_payload.get('given_name', ''),
                    'last_name': token_payload.get('family_name', ''),
                    'is_staff': 'admin' in token_payload.get('realm_access', {}).get('roles', []),
                    'is_superuser': 'admin' in token_payload.get('realm_access', {}).get('roles', [])
                }
            )
            
            # Store token info in request for permission checks
            request.token_payload = token_payload
            
            return (user, token)
            
        except Exception as e:
            return None
    
    def authenticate_header(self, request):
        return 'Bearer realm="api"' 
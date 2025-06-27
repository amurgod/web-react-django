"""
Keycloak authentication middleware for Django
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from keycloak_auth import KeycloakBackend
import logging

logger = logging.getLogger(__name__)

class KeycloakMiddleware:
    """
    Middleware to handle Keycloak authentication
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.auth_backend = KeycloakBackend()
    
    def __call__(self, request):
        # Process request
        self.process_request(request)
        
        # Get response
        response = self.get_response(request)
        
        # Process response
        return self.process_response(request, response)
    
    def process_request(self, request):
        """
        Process incoming request and authenticate user
        """
        # Skip authentication for certain paths
        if self._should_skip_auth(request.path):
            return
        
        # Get token from Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            
            try:
                # Authenticate user with token
                user = self.auth_backend.authenticate(request, token=token)
                if user:
                    request.user = user
                else:
                    request.user = AnonymousUser()
                    
            except Exception as e:
                logger.error(f"Keycloak middleware error: {e}")
                request.user = AnonymousUser()
        else:
            # Check for token in session (only if session is available)
            if hasattr(request, 'session'):
                token = request.session.get('keycloak_token')
                if token:
                    try:
                        user = self.auth_backend.authenticate(request, token=token)
                        if user:
                            request.user = user
                        else:
                            request.user = AnonymousUser()
                    except Exception as e:
                        logger.error(f"Keycloak session authentication error: {e}")
                        request.user = AnonymousUser()
                else:
                    request.user = AnonymousUser()
            else:
                # Session not available, set anonymous user
                request.user = AnonymousUser()
    
    def process_response(self, request, response):
        """
        Process outgoing response
        """
        # Add CORS headers for Keycloak
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        
        return response
    
    def _should_skip_auth(self, path):
        """
        Check if authentication should be skipped for this path
        """
        skip_paths = [
            '/admin/login/',
            '/admin/logout/',
            '/api/auth/',
            '/health/',
            '/static/',
            '/media/',
        ]
        
        return any(path.startswith(skip_path) for skip_path in skip_paths) 
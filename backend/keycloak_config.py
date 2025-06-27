"""
Keycloak configuration for Django backend
"""
from keycloak import KeycloakOpenID

# Keycloak server configuration
KEYCLOAK_CONFIG = {
    'server_url': 'http://localhost:8080',  # Keycloak server URL
    'client_id': 'hospital-management',     # Client ID
    'client_secret_key': 'xFkvXigFGoq6PewX0tv32Zn5rRrrgymI',  # Client secret
    'admin_username': 'admin',              # Admin username
    'admin_password': 'admin',              # Admin password
    'realm_name': 'hospital-realm',         # Realm name
    'verify': True,                         # Verify SSL certificates
}

# Initialize Keycloak OpenID client
keycloak_openid = KeycloakOpenID(
    server_url=KEYCLOAK_CONFIG['server_url'],
    client_id=KEYCLOAK_CONFIG['client_id'],
    realm_name=KEYCLOAK_CONFIG['realm_name'],
    client_secret_key=KEYCLOAK_CONFIG['client_secret_key'],
    verify=KEYCLOAK_CONFIG['verify']
)

# Role definitions
ROLES = {
    'ADMIN': 'admin',
    'DOCTOR': 'doctor',
    'NURSE': 'nurse',
    'RECEPTIONIST': 'receptionist',
    'VIEWER': 'viewer'
}

# Permission mappings
PERMISSIONS = {
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
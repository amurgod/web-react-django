from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from api_app.models import Patient, Hospital
from api_app.serializers import PatientSerializer, HospitalSerializer
from api_app.authentication import TokenAuthentication
from api_app.permissions import HasResourcePermission
from keycloak_config import KEYCLOAK_CONFIG
import requests
import json
import jwt

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [HasResourcePermission]
    
    def get_permissions(self):
        """
        Set required permission based on action
        """
        if self.action == 'list' or self.action == 'retrieve':
            self.required_permission = 'patient:view'
        elif self.action == 'create':
            self.required_permission = 'patient:create'
        elif self.action in ['update', 'partial_update']:
            self.required_permission = 'patient:update'
        elif self.action == 'destroy':
            self.required_permission = 'patient:delete'
        return super().get_permissions()

class HospitalViewSet(viewsets.ModelViewSet):
    queryset = Hospital.objects.all()
    serializer_class = HospitalSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [HasResourcePermission]
    
    def get_permissions(self):
        """
        Set required permission based on action
        """
        if self.action == 'list' or self.action == 'retrieve':
            self.required_permission = 'hospital:view'
        elif self.action == 'create':
            self.required_permission = 'hospital:create'
        elif self.action in ['update', 'partial_update']:
            self.required_permission = 'hospital:update'
        elif self.action == 'destroy':
            self.required_permission = 'hospital:delete'
        return super().get_permissions()

@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """
    Handle user login with username/password and return Keycloak token
    """
    try:
        username = request.data.get('username')
        password = request.data.get('password')
        
        print(f"🔐 Login attempt for username: {username}")
        
        if not username or not password:
            return Response({
                'error': 'Username and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Keycloak configuration
        keycloak_url = KEYCLOAK_CONFIG['server_url']
        realm = KEYCLOAK_CONFIG['realm_name']
        client_id = KEYCLOAK_CONFIG['client_id']
        client_secret = KEYCLOAK_CONFIG['client_secret_key']
        
        print(f"🔐 Keycloak config - URL: {keycloak_url}, Realm: {realm}, Client: {client_id}")
        
        # Get token from Keycloak
        token_url = f"{keycloak_url}/realms/{realm}/protocol/openid-connect/token"
        
        payload = {
            'grant_type': 'password',
            'client_id': client_id,
            'client_secret': client_secret,
            'username': username,
            'password': password
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        print(f"🔐 Making request to: {token_url}")
        print(f"🔐 Payload: {payload}")
        
        response = requests.post(token_url, data=payload, headers=headers)
        
        print(f"🔐 Response status: {response.status_code}")
        print(f"🔐 Response content: {response.text}")
        
        if response.status_code == 200:
            token_data = response.json()
            
            # Get user info from Keycloak
            userinfo_url = f"{keycloak_url}/realms/{realm}/protocol/openid-connect/userinfo"
            userinfo_headers = {
                'Authorization': f"Bearer {token_data['access_token']}"
            }
            
            print(f"🔐 Getting user info from: {userinfo_url}")
            print(f"🔐 Userinfo headers: {userinfo_headers}")
            
            userinfo_response = requests.get(userinfo_url, headers=userinfo_headers)
            
            print(f"🔐 Userinfo response status: {userinfo_response.status_code}")
            print(f"🔐 Userinfo response content: {userinfo_response.text}")
            
            if userinfo_response.status_code == 200:
                user_info = userinfo_response.json()
                
                return Response({
                    'success': True,
                    'access_token': token_data['access_token'],
                    'refresh_token': token_data.get('refresh_token'),
                    'user': {
                        'username': user_info.get('preferred_username'),
                        'email': user_info.get('email'),
                        'name': user_info.get('name'),
                        'roles': user_info.get('realm_access', {}).get('roles', [])
                    }
                })
            else:
                # If userinfo fails, try to extract user info from the token itself
                print("🔐 Userinfo failed, extracting from token...")
                try:
                    # Decode the token without verification to get user info
                    token_payload = jwt.decode(token_data['access_token'], options={"verify_signature": False})
                    print(f"🔐 Token payload: {token_payload}")
                    
                    return Response({
                        'success': True,
                        'access_token': token_data['access_token'],
                        'refresh_token': token_data.get('refresh_token'),
                        'user': {
                            'username': token_payload.get('preferred_username'),
                            'email': token_payload.get('email'),
                            'name': token_payload.get('name'),
                            'roles': token_payload.get('realm_access', {}).get('roles', [])
                        }
                    })
                except Exception as e:
                    print(f"❌ Token decode failed: {e}")
                    return Response({
                        'error': 'Failed to get user information'
                    }, status=status.HTTP_401_UNAUTHORIZED)
        else:
            error_detail = response.text
            try:
                error_json = response.json()
                error_detail = error_json.get('error_description', error_json.get('error', error_detail))
            except:
                pass
                
            return Response({
                'error': f'Invalid username or password: {error_detail}'
            }, status=status.HTTP_401_UNAUTHORIZED)
            
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return Response({
            'error': f'Login failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    """
    Refresh access token using refresh token
    """
    try:
        refresh_token = request.data.get('refresh_token')
        
        if not refresh_token:
            return Response({
                'error': 'Refresh token is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Keycloak configuration
        keycloak_url = KEYCLOAK_CONFIG['server_url']
        realm = KEYCLOAK_CONFIG['realm_name']
        client_id = KEYCLOAK_CONFIG['client_id']
        client_secret = KEYCLOAK_CONFIG['client_secret_key']
        
        # Refresh token with Keycloak
        token_url = f"{keycloak_url}/realms/{realm}/protocol/openid-connect/token"
        
        payload = {
            'grant_type': 'refresh_token',
            'client_id': client_id,
            'client_secret': client_secret,
            'refresh_token': refresh_token
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        response = requests.post(token_url, data=payload, headers=headers)
        
        if response.status_code == 200:
            token_data = response.json()
            
            return Response({
                'success': True,
                'access_token': token_data['access_token'],
                'refresh_token': token_data.get('refresh_token')
            })
        else:
            return Response({
                'error': 'Invalid refresh token'
            }, status=status.HTTP_401_UNAUTHORIZED)
            
    except Exception as e:
        return Response({
            'error': f'Token refresh failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
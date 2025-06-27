#!/usr/bin/env python3
"""
Test script to verify Keycloak connection and authentication
"""
import requests
import json
from keycloak_config import KEYCLOAK_CONFIG

def test_keycloak_connection():
    """Test basic Keycloak connection"""
    try:
        # Test Keycloak health endpoint
        health_url = f"{KEYCLOAK_CONFIG['server_url']}/health"
        print(f"🔍 Testing Keycloak health: {health_url}")
        
        response = requests.get(health_url)
        print(f"Health status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Keycloak server is running")
        else:
            print("❌ Keycloak server health check failed")
            return False
            
    except Exception as e:
        print(f"❌ Keycloak connection failed: {e}")
        return False
    
    return True

def test_client_config():
    """Test client configuration"""
    try:
        # Get client info
        realm = KEYCLOAK_CONFIG['realm_name']
        client_id = KEYCLOAK_CONFIG['client_id']
        
        client_url = f"{KEYCLOAK_CONFIG['server_url']}/realms/{realm}/clients"
        print(f"🔍 Testing client config: {client_url}")
        
        # This would require admin authentication, so let's just test the token endpoint
        token_url = f"{KEYCLOAK_CONFIG['server_url']}/realms/{realm}/protocol/openid-connect/token"
        
        # Test with invalid credentials first
        payload = {
            'grant_type': 'password',
            'client_id': client_id,
            'client_secret': KEYCLOAK_CONFIG['client_secret_key'],
            'username': 'invalid_user',
            'password': 'invalid_password'
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        print(f"🔍 Testing token endpoint: {token_url}")
        response = requests.post(token_url, data=payload, headers=headers)
        
        print(f"Token endpoint status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 400:
            print("✅ Token endpoint is working (expected error for invalid credentials)")
            return True
        elif response.status_code == 401:
            print("❌ Client authentication failed - check client secret")
            return False
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Client config test failed: {e}")
        return False

def test_user_authentication():
    """Test user authentication"""
    try:
        realm = KEYCLOAK_CONFIG['realm_name']
        client_id = KEYCLOAK_CONFIG['client_id']
        token_url = f"{KEYCLOAK_CONFIG['server_url']}/realms/{realm}/protocol/openid-connect/token"
        
        # Test with valid credentials
        payload = {
            'grant_type': 'password',
            'client_id': client_id,
            'client_secret': KEYCLOAK_CONFIG['client_secret_key'],
            'username': 'admin',
            'password': 'admin123'
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        print(f"🔍 Testing admin authentication...")
        response = requests.post(token_url, data=payload, headers=headers)
        
        print(f"Auth status: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            print("✅ Admin authentication successful!")
            print(f"Access token: {token_data.get('access_token', '')[:50]}...")
            print(f"Token type: {token_data.get('token_type', 'N/A')}")
            print(f"Expires in: {token_data.get('expires_in', 'N/A')} seconds")
            return True
        else:
            print(f"❌ Authentication failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Keycloak Configuration")
    print("=" * 50)
    
    # Test 1: Basic connection
    if not test_keycloak_connection():
        print("❌ Keycloak connection failed. Make sure Keycloak is running on port 8080")
        exit(1)
    
    print()
    
    # Test 2: Client configuration
    if not test_client_config():
        print("❌ Client configuration test failed")
        exit(1)
    
    print()
    
    # Test 3: User authentication
    if not test_user_authentication():
        print("❌ User authentication test failed")
        exit(1)
    
    print()
    print("✅ All tests passed! Keycloak is properly configured.") 
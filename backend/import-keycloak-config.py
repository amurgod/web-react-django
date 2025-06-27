#!/usr/bin/env python3
"""
Script to import Keycloak realm configuration
"""
import json
import requests
import sys
import time

def get_admin_token(keycloak_url, admin_username, admin_password):
    """Get admin access token"""
    token_url = f"{keycloak_url}/realms/master/protocol/openid-connect/token"
    data = {
        'grant_type': 'password',
        'client_id': 'admin-cli',
        'username': admin_username,
        'password': admin_password
    }
    
    try:
        response = requests.post(token_url, data=data)
        response.raise_for_status()
        return response.json()['access_token']
    except requests.exceptions.RequestException as e:
        print(f"Error getting admin token: {e}")
        return None

def check_keycloak_health(keycloak_url):
    """Check if Keycloak is ready using multiple endpoints"""
    health_endpoints = [
        f"{keycloak_url}/health",
        f"{keycloak_url}/health/ready",
        f"{keycloak_url}/realms/master",
        f"{keycloak_url}/"
    ]
    
    for endpoint in health_endpoints:
        try:
            response = requests.get(endpoint, timeout=5)
            if response.status_code in [200, 302, 404]:  # 404 is OK for some endpoints
                print(f"✅ Keycloak is ready! (Endpoint: {endpoint})")
                return True
        except requests.exceptions.RequestException:
            continue
    
    return False

def import_realm(keycloak_url, admin_token, realm_config):
    """Import realm configuration"""
    import_url = f"{keycloak_url}/admin/realms"
    headers = {
        'Authorization': f'Bearer {admin_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(import_url, json=realm_config, headers=headers)
        if response.status_code == 201:
            print("✅ Realm imported successfully!")
            return True
        elif response.status_code == 409:
            print("⚠️  Realm already exists. Updating...")
            return update_realm(keycloak_url, admin_token, realm_config)
        else:
            print(f"❌ Error importing realm: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error importing realm: {e}")
        return False

def update_realm(keycloak_url, admin_token, realm_config):
    """Update existing realm"""
    realm_name = realm_config['realm']
    update_url = f"{keycloak_url}/admin/realms/{realm_name}"
    headers = {
        'Authorization': f'Bearer {admin_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.put(update_url, json=realm_config, headers=headers)
        if response.status_code == 204:
            print("✅ Realm updated successfully!")
            return True
        else:
            print(f"❌ Error updating realm: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error updating realm: {e}")
        return False

def get_client_secret(keycloak_url, admin_token, realm_name, client_id):
    """Get client secret"""
    client_url = f"{keycloak_url}/admin/realms/{realm_name}/clients"
    headers = {
        'Authorization': f'Bearer {admin_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(client_url, headers=headers)
        response.raise_for_status()
        clients = response.json()
        
        for client in clients:
            if client['clientId'] == client_id:
                client_id_uuid = client['id']
                secret_url = f"{keycloak_url}/admin/realms/{realm_name}/clients/{client_id_uuid}/client-secret"
                secret_response = requests.get(secret_url, headers=headers)
                if secret_response.status_code == 200:
                    secret_data = secret_response.json()
                    return secret_data['value']
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error getting client secret: {e}")
        return None

def main():
    # Configuration
    keycloak_url = "http://localhost:8080"
    admin_username = "admin"
    admin_password = "admin"
    config_file = "keycloak-realm-config.json"
    
    print("🚀 Starting Keycloak configuration import...")
    print(f"📁 Loading configuration from: {config_file}")
    
    # Load configuration
    try:
        with open(config_file, 'r') as f:
            realm_config = json.load(f)
    except FileNotFoundError:
        print(f"❌ Configuration file not found: {config_file}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in configuration file: {e}")
        sys.exit(1)
    
    # Wait for Keycloak to be ready
    print("⏳ Waiting for Keycloak to be ready...")
    max_retries = 30
    for i in range(max_retries):
        if check_keycloak_health(keycloak_url):
            break
        
        if i == max_retries - 1:
            print("❌ Keycloak is not responding. Please make sure it's running on http://localhost:8080")
            print("💡 Try: docker run -p 8080:8080 -e KEYCLOAK_ADMIN=admin -e KEYCLOAK_ADMIN_PASSWORD=admin quay.io/keycloak/keycloak:latest start-dev")
            sys.exit(1)
        
        print(f"⏳ Retrying... ({i+1}/{max_retries})")
        time.sleep(2)
    
    # Get admin token
    print("🔑 Getting admin token...")
    admin_token = get_admin_token(keycloak_url, admin_username, admin_password)
    if not admin_token:
        print("❌ Failed to get admin token")
        print("💡 Make sure Keycloak is running and admin credentials are correct")
        sys.exit(1)
    
    # Import realm
    print("📦 Importing realm configuration...")
    realm_name = realm_config['realm']
    if import_realm(keycloak_url, admin_token, realm_config):
        print(f"✅ Realm '{realm_name}' configured successfully!")
        
        # Get client secret
        print("🔐 Getting client secret...")
        client_secret = get_client_secret(keycloak_url, admin_token, realm_name, "hospital-management")
        if client_secret:
            print("✅ Client secret retrieved!")
            print(f"🔑 Client Secret: {client_secret}")
            print("\n📝 Update your backend/keycloak_config.py with this secret:")
            print(f"   'client_secret_key': '{client_secret}'")
        else:
            print("⚠️  Could not retrieve client secret. You'll need to get it manually from the Keycloak admin console.")
        
        print("\n🎉 Configuration complete!")
        print("\n📋 Test Users:")
        print("   Admin: admin / admin123")
        print("   Doctor: doctor / doctor123")
        print("   Nurse: nurse / nurse123")
        print("   Receptionist: receptionist / receptionist123")
        print("   Viewer: viewer / viewer123")
        
    else:
        print("❌ Failed to import realm configuration")
        sys.exit(1)

if __name__ == "__main__":
    main() 
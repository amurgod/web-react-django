# Keycloak Integration Setup Guide

This guide will help you set up Keycloak for authentication and RBAC (Role-Based Access Control) in your Hospital Management System.

## Prerequisites

1. **Java 11 or higher** installed on your system
2. **Docker** (optional, for easier setup)

## 1. Install and Start Keycloak

### Option A: Using Docker (Recommended)

```bash
# Pull and run Keycloak
docker run -p 8080:8080 \
  -e KEYCLOAK_ADMIN=admin \
  -e KEYCLOAK_ADMIN_PASSWORD=admin \
  quay.io/keycloak/keycloak:latest \
  start-dev
```

### Option B: Manual Installation

1. Download Keycloak from https://www.keycloak.org/downloads
2. Extract the archive
3. Navigate to the bin directory
4. Run: `./kc.sh start-dev`

## 2. Access Keycloak Admin Console

1. Open your browser and go to: `http://localhost:8080`
2. Click on "Administration Console"
3. Login with:
   - Username: `admin`
   - Password: `admin`

## 3. Create a New Realm

1. In the top-left dropdown, click "Create Realm"
2. Enter "hospital-realm" as the realm name
3. Click "Create"

## 4. Create Roles

1. Go to "Realm Roles" in the left sidebar
2. Click "Create Role"
3. Create the following roles:
   - `admin`
   - `doctor`
   - `nurse`
   - `receptionist`
   - `viewer`

## 5. Create a Client

1. Go to "Clients" in the left sidebar
2. Click "Create"
3. Configure the client:
   - **Client ID**: `hospital-management`
   - **Client Protocol**: `openid-connect`
   - Click "Save"

4. Configure client settings:
   - **Access Type**: `confidential`
   - **Valid Redirect URIs**: `http://localhost:3000/*`
   - **Web Origins**: `http://localhost:3000`
   - Click "Save"

5. Get the client secret:
   - Go to the "Credentials" tab
   - Copy the "Secret" value
   - Update `backend/keycloak_config.py` with this secret

## 6. Create Users

1. Go to "Users" in the left sidebar
2. Click "Add User"
3. Create test users with different roles:

### Admin User
- **Username**: `admin`
- **Email**: `admin@hospital.com`
- **First Name**: `Admin`
- **Last Name**: `User`
- **Email Verified**: ON
- **Enabled**: ON

### Doctor User
- **Username**: `doctor`
- **Email**: `doctor@hospital.com`
- **First Name**: `John`
- **Last Name**: `Doctor`
- **Email Verified**: ON
- **Enabled**: ON

### Nurse User
- **Username**: `nurse`
- **Email**: `nurse@hospital.com`
- **First Name**: `Jane`
- **Last Name**: `Nurse`
- **Email Verified**: ON
- **Enabled**: ON

## 7. Assign Roles to Users

For each user:

1. Click on the user
2. Go to the "Role Mappings" tab
3. In "Realm Roles", assign appropriate roles:
   - **admin**: assign `admin` role
   - **doctor**: assign `doctor` role
   - **nurse**: assign `nurse` role

## 8. Set User Passwords

For each user:

1. Go to the "Credentials" tab
2. Set a password (e.g., "password123")
3. Turn OFF "Temporary Password"

## 9. Update Configuration

Update `backend/keycloak_config.py` with your client secret:

```python
KEYCLOAK_CONFIG = {
    'server_url': 'http://localhost:8080',
    'client_id': 'hospital-management',
    'client_secret_key': 'YOUR_CLIENT_SECRET_HERE',  # Replace with actual secret
    'admin_username': 'admin',
    'admin_password': 'admin',
    'realm_name': 'hospital-realm',
    'verify': True,
}
```

## 10. Run Django Migrations

```bash
cd backend
source venv/bin/activate
python manage.py makemigrations
python manage.py migrate
```

## 11. Start the Applications

### Start Django Backend
```bash
cd backend
source venv/bin/activate
python manage.py runserver
```

### Start React Frontend
```bash
npm start
```

## 12. Test the Integration

1. Open `http://localhost:3000`
2. Click "Login with Keycloak"
3. Login with one of the test users
4. Verify that permissions are working correctly

## Role-Based Permissions

The system implements the following permissions:

### Patient Management
- **View**: admin, doctor, nurse, receptionist, viewer
- **Create**: admin, doctor, nurse, receptionist
- **Update**: admin, doctor, nurse
- **Delete**: admin, doctor

### Hospital Management
- **View**: admin, doctor, nurse, receptionist, viewer
- **Create**: admin
- **Update**: admin
- **Delete**: admin

## Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure CORS is properly configured in Keycloak client settings
2. **Token Validation Errors**: Check that the client secret is correct
3. **Permission Denied**: Verify that users have the correct roles assigned

### Debug Mode

Enable debug logging in Django settings:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'keycloak_auth': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## Security Considerations

1. **Production Setup**: Use HTTPS in production
2. **Client Secret**: Keep the client secret secure
3. **Token Expiration**: Configure appropriate token lifetimes
4. **Session Management**: Implement proper session handling

## Next Steps

1. Configure SSL/TLS for production
2. Set up user registration flows
3. Implement password policies
4. Add multi-factor authentication
5. Configure audit logging 
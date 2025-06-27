# Keycloak Quick Setup Guide

This guide will help you set up Keycloak with your Hospital Management System using a configuration file.

## Prerequisites

1. **Java 11 or higher** installed on your system
2. **Docker** (recommended for easier setup)

## Step 1: Start Keycloak

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

## Step 2: Install Python Dependencies

```bash
cd backend
source venv/bin/activate
pip install requests
```

## Step 3: Import Configuration

Run the import script to automatically configure Keycloak:

```bash
cd backend
python import-keycloak-config.py
```

This script will:
- ✅ Create the `hospital-realm` realm
- ✅ Create all roles (admin, doctor, nurse, receptionist, viewer)
- ✅ Create the `hospital-management` client
- ✅ Create test users with appropriate roles
- ✅ Retrieve the client secret automatically

## Step 4: Update Configuration

The script will output the client secret. Update `backend/keycloak_config.py`:

```python
KEYCLOAK_CONFIG = {
    'server_url': 'http://localhost:8080',
    'client_id': 'hospital-management',
    'client_secret_key': 'YOUR_CLIENT_SECRET_HERE',  # Replace with the output from the script
    'admin_username': 'admin',
    'admin_password': 'admin',
    'realm_name': 'hospital-realm',
    'verify': True,
}
```

## Step 5: Run Django Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

## Step 6: Start Applications

### Start Django Backend
```bash
python manage.py runserver
```

### Start React Frontend
```bash
cd ..
npm start
```

## Step 7: Test the Application

1. Open `http://localhost:3000`
2. Click "Login with Keycloak"
3. Use one of the test users:

| Username | Password | Role | Permissions |
|----------|----------|------|-------------|
| admin | admin123 | Admin | Full access |
| doctor | doctor123 | Doctor | Patient management + view hospitals |
| nurse | nurse123 | Nurse | Patient management (no delete) + view hospitals |
| receptionist | receptionist123 | Receptionist | Patient view/create + view hospitals |
| viewer | viewer123 | Viewer | Read-only access |

## What's Included in the Configuration

### 🏥 **Realm**: hospital-realm
- Custom display name and branding
- Configured for your React app

### 👥 **Roles**
- `admin` - Full administrative access
- `doctor` - Patient management + hospital view
- `nurse` - Limited patient management
- `receptionist` - Patient view/create access
- `viewer` - Read-only access

### 🔧 **Client**: hospital-management
- OpenID Connect configuration
- Proper redirect URIs for React app
- Role mapping for tokens

### 👤 **Test Users**
- 5 pre-configured users with different roles
- Realistic attributes (department, employee ID, etc.)
- Secure passwords

### 📁 **Groups**
- Medical Staff (Doctors, Nurses)
- Administrative Staff (Admins, Receptionists)
- Support Staff (Viewers)

## Troubleshooting

### Common Issues

1. **Keycloak not responding**: Make sure Keycloak is running on port 8080
2. **Import script fails**: Check that Keycloak admin credentials are correct
3. **Client secret not found**: The script will tell you how to get it manually

### Manual Client Secret Retrieval

If the script can't get the client secret automatically:

1. Go to `http://localhost:8080`
2. Login as admin
3. Select `hospital-realm`
4. Go to Clients → `hospital-management`
5. Go to Credentials tab
6. Copy the Secret value

## Security Notes

- **Change default passwords** in production
- **Use HTTPS** in production
- **Secure client secrets** properly
- **Configure proper token lifetimes**

## Next Steps

1. **Customize the configuration** in `keycloak-realm-config.json`
2. **Add more users** through the admin console
3. **Configure password policies**
4. **Set up email verification**
5. **Add multi-factor authentication**

That's it! Your Keycloak integration is now ready to use. 🎉 
import axios from 'axios';

// Create axios instance for auth API
const authClient = axios.create({
    baseURL: 'http://127.0.0.1:8000',
    timeout: 10000,
});

class AuthService {
    constructor() {
        this.token = localStorage.getItem('access_token');
        this.refreshToken = localStorage.getItem('refresh_token');
        this.user = JSON.parse(localStorage.getItem('user') || 'null');
        this.authenticated = !!this.token;
    }

    // Login with username and password
    async login(username, password) {
        try {
            console.log('🔐 Logging in with backend...');
            
            const response = await authClient.post('/login/', {
                username: username,
                password: password
            });

            if (response.data.success) {
                this.token = response.data.access_token;
                this.refreshToken = response.data.refresh_token;
                this.user = response.data.user;
                this.authenticated = true;

                // Store in localStorage
                localStorage.setItem('access_token', this.token);
                localStorage.setItem('refresh_token', this.refreshToken);
                localStorage.setItem('user', JSON.stringify(this.user));

                console.log('✅ Login successful:', this.user.username);
                return {
                    success: true,
                    user: this.user
                };
            } else {
                throw new Error(response.data.error || 'Login failed');
            }
        } catch (error) {
            console.error('❌ Login failed:', error.response?.data?.error || error.message);
            throw new Error(error.response?.data?.error || 'Login failed');
        }
    }

    // Logout
    logout() {
        console.log('🚪 Logging out...');
        
        this.token = null;
        this.refreshToken = null;
        this.user = null;
        this.authenticated = false;

        // Clear localStorage
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');

        console.log('✅ Logout successful');
    }

    // Refresh token
    async refreshAccessToken() {
        try {
            if (!this.refreshToken) {
                throw new Error('No refresh token available');
            }

            console.log('🔄 Refreshing token...');
            
            const response = await authClient.post('/refresh-token/', {
                refresh_token: this.refreshToken
            });

            if (response.data.success) {
                this.token = response.data.access_token;
                this.refreshToken = response.data.refresh_token;

                // Update localStorage
                localStorage.setItem('access_token', this.token);
                localStorage.setItem('refresh_token', this.refreshToken);

                console.log('✅ Token refreshed');
                return true;
            } else {
                throw new Error('Token refresh failed');
            }
        } catch (error) {
            console.error('❌ Token refresh failed:', error);
            this.logout();
            return false;
        }
    }

    // Get current token
    getToken() {
        return this.token;
    }

    // Get user info
    getUser() {
        return this.user;
    }

    // Get user roles
    getRoles() {
        return this.user?.roles || [];
    }

    // Check if user has specific role
    hasRole(role) {
        return this.getRoles().includes(role);
    }

    // Check if user has any of the specified roles
    hasAnyRole(roles) {
        return roles.some(role => this.hasRole(role));
    }

    // Check if user has permission for resource and action
    hasPermission(resource, action) {
        const permissions = {
            patient: {
                view: ['admin', 'doctor', 'nurse', 'receptionist', 'viewer'],
                create: ['admin', 'doctor', 'nurse', 'receptionist'],
                update: ['admin', 'doctor', 'nurse'],
                delete: ['admin', 'doctor']
            },
            hospital: {
                view: ['admin', 'doctor', 'nurse', 'receptionist', 'viewer'],
                create: ['admin'],
                update: ['admin'],
                delete: ['admin']
            }
        };

        const requiredRoles = permissions[resource]?.[action] || [];
        return this.hasAnyRole(requiredRoles);
    }

    // Check if user is authenticated
    isAuthenticated() {
        return this.authenticated && !!this.token;
    }

    // Get authorization header for API calls
    getAuthHeader() {
        return {
            'Authorization': `Bearer ${this.getToken()}`
        };
    }

    // Check if token is expired (simple check)
    isTokenExpired() {
        if (!this.token) return true;
        
        try {
            const payload = JSON.parse(atob(this.token.split('.')[1]));
            const currentTime = Math.floor(Date.now() / 1000);
            return payload.exp < currentTime;
        } catch (error) {
            console.error('Error parsing token:', error);
            return true;
        }
    }

    // Auto-refresh token if needed
    async ensureValidToken() {
        if (this.isTokenExpired()) {
            return await this.refreshAccessToken();
        }
        return true;
    }
}

// Create singleton instance
const authService = new AuthService();

export default authService; 
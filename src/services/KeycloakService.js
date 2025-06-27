import Keycloak from 'keycloak-js';

// Keycloak configuration
const keycloakConfig = {
    url: 'http://localhost:8080',
    realm: 'hospital-realm',
    clientId: 'hospital-management'
};

// Initialize Keycloak
const keycloak = new Keycloak(keycloakConfig);

class KeycloakService {
    constructor() {
        this.keycloak = keycloak;
        this.authenticated = false;
        this.user = null;
        this.roles = [];
        this.initPromise = null; // Cache initialization promise
    }

    // Initialize Keycloak with performance optimizations
    async init() {
        // Return cached promise if already initializing
        if (this.initPromise) {
            return this.initPromise;
        }

        this.initPromise = this._performInit();
        return this.initPromise;
    }

    async _performInit() {
        try {
            console.log('🚀 Initializing Keycloak...');
            const startTime = Date.now();
            
            const authenticated = await this.keycloak.init({
                onLoad: 'check-sso',
                silentCheckSsoRedirectUri: window.location.origin + '/silent-check-sso.html',
                checkLoginIframe: false,
                enableLogging: false, // Disable logging for better performance
                pkceMethod: 'S256', // Use PKCE for better security
                timeout: 10000, // 10 second timeout
            });

            const initTime = Date.now() - startTime;
            console.log(`✅ Keycloak initialized in ${initTime}ms`);

            this.authenticated = authenticated;
            
            if (authenticated) {
                this.user = this.keycloak.tokenParsed;
                this.roles = this.keycloak.tokenParsed.realm_access?.roles || [];
                this._setupTokenRefresh();
                console.log('👤 User authenticated:', this.user?.preferred_username);
            } else {
                console.log('👤 User not authenticated');
            }

            return authenticated;
        } catch (error) {
            console.error('❌ Keycloak initialization failed:', error);
            // Reset promise on error so it can be retried
            this.initPromise = null;
            return false;
        }
    }

    // Login
    async login() {
        try {
            console.log('🔐 Initiating login...');
            console.log('🔐 Current location:', window.location.href);
            console.log('🔐 Redirect URI:', window.location.origin);
            
            await this.keycloak.login({
                redirectUri: 'http://localhost:3000/'
            });
        } catch (error) {
            console.error('❌ Login failed:', error);
            throw error;
        }
    }

    // Logout
    async logout() {
        try {
            console.log('🚪 Logging out...');
            await this.keycloak.logout({
                redirectUri: window.location.origin
            });
        } catch (error) {
            console.error('❌ Logout failed:', error);
            throw error;
        }
    }

    // Get current token
    getToken() {
        return this.keycloak.token;
    }

    // Get user info
    getUser() {
        return this.user;
    }

    // Get user roles
    getRoles() {
        return this.roles;
    }

    // Check if user has specific role
    hasRole(role) {
        return this.roles.includes(role);
    }

    // Check if user has any of the specified roles
    hasAnyRole(roles) {
        return roles.some(role => this.roles.includes(role));
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
        return this.authenticated;
    }

    // Setup token refresh
    _setupTokenRefresh() {
        this.keycloak.onTokenExpired = () => {
            console.log('🔄 Token expired, refreshing...');
            this.keycloak.updateToken(70).then((refreshed) => {
                if (refreshed) {
                    console.log('✅ Token refreshed');
                    this.user = this.keycloak.tokenParsed;
                    this.roles = this.keycloak.tokenParsed.realm_access?.roles || [];
                }
            }).catch(() => {
                console.error('❌ Token refresh failed');
                this.logout();
            });
        };
    }

    // Get authorization header for API calls
    getAuthHeader() {
        return {
            'Authorization': `Bearer ${this.getToken()}`
        };
    }

    // Update token
    async updateToken() {
        try {
            const refreshed = await this.keycloak.updateToken(70);
            if (refreshed) {
                this.user = this.keycloak.tokenParsed;
                this.roles = this.keycloak.tokenParsed.realm_access?.roles || [];
            }
            return refreshed;
        } catch (error) {
            console.error('❌ Token update failed:', error);
            return false;
        }
    }

    // Clear cached initialization
    clearCache() {
        this.initPromise = null;
    }
}

// Create singleton instance
const keycloakService = new KeycloakService();

export default keycloakService; 
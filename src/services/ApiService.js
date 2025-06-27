import axios from "axios";
import authService from "./AuthService";

// Cache for API responses
const cache = new Map();
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

// Create axios instance with base configuration
const apiClient = axios.create({
    baseURL: 'http://127.0.0.1:8000',
    timeout: 8000, // Reduced timeout for faster failure detection
});

// Add request interceptor to include auth token
apiClient.interceptors.request.use(
    async (config) => {
        // Add cache busting for GET requests
        if (config.method === 'get' && !config.params) {
            config.params = { _t: Date.now() };
        }
        
        // Ensure token is valid before making request
        if (authService.isAuthenticated()) {
            await authService.ensureValidToken();
            config.headers.Authorization = `Bearer ${authService.getToken()}`;
        }
        
        // Add performance headers
        config.headers['Cache-Control'] = 'no-cache';
        config.headers['Pragma'] = 'no-cache';
        
        return config;
    },
    (error) => {
        console.error('❌ Request interceptor error:', error);
        return Promise.reject(error);
    }
);

// Add response interceptor to handle token refresh
apiClient.interceptors.response.use(
    (response) => {
        return response;
    },
    async (error) => {
        const originalRequest = error.config;
        
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;
            
            try {
                console.log('🔄 Token expired, attempting refresh...');
                const refreshed = await authService.refreshAccessToken();
                if (refreshed) {
                    originalRequest.headers.Authorization = `Bearer ${authService.getToken()}`;
                    return apiClient(originalRequest);
                }
            } catch (refreshError) {
                console.error('❌ Token refresh failed:', refreshError);
                // Redirect to login
                authService.logout();
                window.location.href = '/';
                return Promise.reject(refreshError);
            }
        }
        
        return Promise.reject(error);
    }
);

// Cache utility functions
const getCacheKey = (url, params) => {
    return `${url}?${JSON.stringify(params || {})}`;
};

const getFromCache = (key) => {
    const cached = cache.get(key);
    if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
        return cached.data;
    }
    cache.delete(key);
    return null;
};

const setCache = (key, data) => {
    cache.set(key, {
        data,
        timestamp: Date.now()
    });
};

const clearCache = () => {
    cache.clear();
};

// Patient API endpoints
export function getpatient() {
    const cacheKey = getCacheKey('/patient/');
    const cached = getFromCache(cacheKey);
    
    if (cached) {
        console.log('📦 Returning cached patient data');
        return Promise.resolve(cached);
    }
    
    console.log('🌐 Fetching patient data from API...');
    return apiClient.get('/patient/')
        .then(res => {
            setCache(cacheKey, res.data);
            return res.data;
        })
        .catch(error => {
            console.error('❌ Failed to fetch patients:', error);
            throw error;
        });
}

export function deletepatient(id) {
    // Clear cache when deleting
    clearCache();
    
    return apiClient.delete('/patient/' + id + '/')
        .then(res => res.data)
        .catch(error => {
            console.error('❌ Failed to delete patient:', error);
            throw error;
        });
}

export function addpatient(patient) {
    // Clear cache when adding
    clearCache();
    
    return apiClient.post('/patient/', patient)
        .then(res => res.data)
        .catch(error => {
            console.error('❌ Failed to add patient:', error);
            throw error;
        });
}

// Hospital API endpoints
export function getHospitals() {
    const cacheKey = getCacheKey('/hospital/');
    const cached = getFromCache(cacheKey);
    
    if (cached) {
        console.log('📦 Returning cached hospital data');
        return Promise.resolve(cached);
    }
    
    console.log('🌐 Fetching hospital data from API...');
    return apiClient.get('/hospital/')
        .then(res => {
            setCache(cacheKey, res.data);
            return res.data;
        })
        .catch(error => {
            console.error('❌ Failed to fetch hospitals:', error);
            throw error;
        });
}

export function deleteHospital(id) {
    // Clear cache when deleting
    clearCache();
    
    return apiClient.delete('/hospital/' + id + '/')
        .then(res => res.data)
        .catch(error => {
            console.error('❌ Failed to delete hospital:', error);
            throw error;
        });
}

export function addHospital(hospital) {
    // Clear cache when adding
    clearCache();
    
    return apiClient.post('/hospital/', hospital)
        .then(res => res.data)
        .catch(error => {
            console.error('❌ Failed to add hospital:', error);
            throw error;
        });
}

// Export cache utilities for manual cache management
export { clearCache, getFromCache, setCache };

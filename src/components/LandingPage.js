import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import authService from '../services/AuthService';
import './LandingPage.css';

const LandingPage = () => {
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [isLoading, setIsLoading] = useState(true);
    const [loadingMessage, setLoadingMessage] = useState('Initializing...');
    const [user, setUser] = useState(null);
    const [roles, setRoles] = useState([]);
    
    // Login form state
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [loginError, setLoginError] = useState('');
    const [isLoggingIn, setIsLoggingIn] = useState(false);
    
    const navigate = useNavigate();

    useEffect(() => {
        initializeAuth();
    }, []);

    const initializeAuth = async () => {
        try {
            setIsLoading(true);
            setLoadingMessage('Checking authentication...');
            
            // Check if user is already logged in
            if (authService.isAuthenticated()) {
                setLoadingMessage('Loading user data...');
                setIsLoggedIn(true);
                setUser(authService.getUser());
                setRoles(authService.getRoles());
            }
        } catch (error) {
            console.error('Authentication check failed:', error);
            setLoadingMessage('Authentication check failed');
        } finally {
            setIsLoading(false);
        }
    };

    const handleLogin = async (e) => {
        e.preventDefault();
        
        if (!username || !password) {
            setLoginError('Please enter both username and password');
            return;
        }

        try {
            setIsLoggingIn(true);
            setLoginError('');
            
            const result = await authService.login(username, password);
            
            if (result.success) {
                setIsLoggedIn(true);
                setUser(authService.getUser());
                setRoles(authService.getRoles());
                setUsername('');
                setPassword('');
            }
        } catch (error) {
            console.error('Login failed:', error);
            setLoginError(error.message || 'Login failed. Please check your credentials.');
        } finally {
            setIsLoggingIn(false);
        }
    };

    const handleLogout = async () => {
        try {
            setIsLoading(true);
            setLoadingMessage('Logging out...');
            authService.logout();
            setIsLoggedIn(false);
            setUser(null);
            setRoles([]);
        } catch (error) {
            console.error('Logout failed:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const handlePatientManagement = () => {
        if (authService.hasPermission('patient', 'view')) {
            navigate('/patients');
        } else {
            alert('You do not have permission to access Patient Management');
        }
    };

    const handleHospitalManagement = () => {
        if (authService.hasPermission('hospital', 'view')) {
            navigate('/hospitals');
        } else {
            alert('You do not have permission to access Hospital Management');
        }
    };

    if (isLoading) {
        return (
            <div className="landing-container">
                <div className="loading-spinner">
                    <div className="spinner"></div>
                    <p>{loadingMessage}</p>
                    <div className="loading-dots">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="landing-container">
            <div className="landing-header">
                <h1 className="landing-title">HMS</h1>
                <p className="landing-subtitle">Comprehensive Healthcare Management Solution</p>
            </div>

            <div className="landing-content">
                {!isLoggedIn ? (
                    <div className="welcome-section">
                        <h2>Welcome to HMS</h2>
                        <p>Please login to access the management system</p>
                        
                        <form onSubmit={handleLogin} className="login-form">
                            <div className="form-group">
                                <label htmlFor="username">Username:</label>
                                <input
                                    type="text"
                                    id="username"
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                    placeholder="Enter username"
                                    required
                                    disabled={isLoggingIn}
                                />
                            </div>
                            
                            <div className="form-group">
                                <label htmlFor="password">Password:</label>
                                <input
                                    type="password"
                                    id="password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    placeholder="Enter password"
                                    required
                                    disabled={isLoggingIn}
                                />
                            </div>
                            
                            {loginError && (
                                <div className="error-message">
                                    {loginError}
                                </div>
                            )}
                            
                            <button 
                                type="submit"
                                className="login-btn"
                                disabled={isLoggingIn}
                            >
                                {isLoggingIn ? 'Logging in...' : 'Login'}
                            </button>
                        </form>
                        
                        <div className="demo-credentials">
                            <h4>Demo Credentials:</h4>
                            <div className="credential-list">
                                <div><strong>Admin:</strong> admin / admin123</div>
                                <div><strong>Doctor:</strong> doctor / doctor123</div>
                                <div><strong>Nurse:</strong> nurse / nurse123</div>
                                <div><strong>Receptionist:</strong> receptionist / receptionist123</div>
                                <div><strong>Viewer:</strong> viewer / viewer123</div>
                            </div>
                        </div>
                    </div>
                ) : (
                    <div className="dashboard-section">
                        <div className="user-info">
                            <div className="user-details">
                                <h3>Welcome, {user?.username || user?.name || 'User'}!</h3>
                                <p className="user-email">{user?.email || ''}</p>
                                <div className="user-roles">
                                    <strong>Roles:</strong> {roles.join(', ')}
                                </div>
                            </div>
                            <button className="logout-btn" onClick={handleLogout}>
                                Logout
                            </button>
                        </div>
                        
                        <div className="management-options">
                            <h3>Management Options</h3>
                            <div className="option-buttons">
                                <button 
                                    className={`option-btn patient-btn ${!authService.hasPermission('patient', 'view') ? 'disabled' : ''}`}
                                    onClick={handlePatientManagement}
                                    disabled={!authService.hasPermission('patient', 'view')}
                                >
                                    <span className="btn-icon">👥</span>
                                    Patient Management
                                    {!authService.hasPermission('patient', 'view') && (
                                        <span className="permission-note">(No access)</span>
                                    )}
                                </button>
                                <button 
                                    className={`option-btn hospital-btn ${!authService.hasPermission('hospital', 'view') ? 'disabled' : ''}`}
                                    onClick={handleHospitalManagement}
                                    disabled={!authService.hasPermission('hospital', 'view')}
                                >
                                    <span className="btn-icon">🏥</span>
                                    Hospital Management
                                    {!authService.hasPermission('hospital', 'view') && (
                                        <span className="permission-note">(No access)</span>
                                    )}
                                </button>
                            </div>
                        </div>

                        <div className="permissions-info">
                            <h4>Your Permissions:</h4>
                            <div className="permissions-grid">
                                <div className="permission-item">
                                    <strong>Patients:</strong>
                                    <ul>
                                        <li>View: {authService.hasPermission('patient', 'view') ? '✅' : '❌'}</li>
                                        <li>Create: {authService.hasPermission('patient', 'create') ? '✅' : '❌'}</li>
                                        <li>Update: {authService.hasPermission('patient', 'update') ? '✅' : '❌'}</li>
                                        <li>Delete: {authService.hasPermission('patient', 'delete') ? '✅' : '❌'}</li>
                                    </ul>
                                </div>
                                <div className="permission-item">
                                    <strong>Hospitals:</strong>
                                    <ul>
                                        <li>View: {authService.hasPermission('hospital', 'view') ? '✅' : '❌'}</li>
                                        <li>Create: {authService.hasPermission('hospital', 'create') ? '✅' : '❌'}</li>
                                        <li>Update: {authService.hasPermission('hospital', 'update') ? '✅' : '❌'}</li>
                                        <li>Delete: {authService.hasPermission('hospital', 'delete') ? '✅' : '❌'}</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default LandingPage; 
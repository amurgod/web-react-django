import React from 'react';
import { useNavigate } from 'react-router-dom';
import './Navigation.css';

const Navigation = ({ currentPage }) => {
    const navigate = useNavigate();

    const handleLogout = () => {
        localStorage.removeItem('isLoggedIn');
        localStorage.removeItem('username');
        navigate('/');
    };

    const handleHome = () => {
        navigate('/');
    };

    return (
        <nav className="navbar navbar-expand-lg navbar-dark bg-primary">
            <div className="container">
                <a className="navbar-brand" href="#" onClick={handleHome}>
                    🏥 Hospital Management System
                </a>
                
                <div className="navbar-nav ms-auto">
                    <span className="navbar-text me-3">
                        Welcome, {localStorage.getItem('username') || 'User'}!
                    </span>
                    <button 
                        className="btn btn-outline-light btn-sm"
                        onClick={handleHome}
                    >
                        Home
                    </button>
                    <button 
                        className="btn btn-outline-light btn-sm ms-2"
                        onClick={handleLogout}
                    >
                        Logout
                    </button>
                </div>
            </div>
        </nav>
    );
};

export default Navigation; 
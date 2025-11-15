import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../utils/AuthContext';
import './Navbar.css';

const Navbar = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-brand">
          <span className="brand-icon">⚗️</span>
          <span className="brand-text">Equipment Visualizer</span>
        </Link>

        {isAuthenticated && (
          <div className="navbar-menu">
            <Link to="/dashboard" className="nav-link">Dashboard</Link>
            <Link to="/upload" className="nav-link">Upload</Link>
            <Link to="/history" className="nav-link">History</Link>
          </div>
        )}

        <div className="navbar-actions">
          {isAuthenticated ? (
            <>
              <span className="user-greeting">Hello, {user?.username}</span>
              <button onClick={handleLogout} className="btn btn-secondary">
                Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="btn btn-secondary">Login</Link>
              <Link to="/register" className="btn btn-primary">Register</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;

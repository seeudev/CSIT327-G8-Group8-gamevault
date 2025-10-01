import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { getBrandName } from '../../config/brand';
import CartIcon from './CartIcon';
import './StoreNavigation.css';

/**
 * StoreNavigation Component
 * Navigation bar for the storefront
 */
const StoreNavigation = () => {
  const { user, logout } = useAuth();
  const location = useLocation();

  const handleLogout = () => {
    logout();
  };

  const isActive = (path) => {
    return location.pathname === path;
  };

  return (
    <nav className="store-navigation">
      <div className="nav-container">
        <div className="nav-brand">
          <Link to="/store" className="brand-link">
            <h1>{getBrandName()}</h1>
          </Link>
        </div>

        <div className="nav-links">
          <Link
            to="/store"
            className={`nav-link ${isActive('/store') ? 'active' : ''}`}
          >
            Store
          </Link>
          
          {user && (
            <Link
              to="/library"
              className={`nav-link ${isActive('/library') ? 'active' : ''}`}
            >
              My Library
            </Link>
          )}
        </div>

        <div className="nav-actions">
          <CartIcon />
          
          {user ? (
            <div className="user-menu">
              <span className="user-name">Welcome, {user.username}</span>
              <div className="user-dropdown">
                <Link to="/profile" className="dropdown-item">
                  Profile
                </Link>
                {user.is_admin && (
                  <Link to="/admin" className="dropdown-item">
                    Admin Panel
                  </Link>
                )}
                <button onClick={handleLogout} className="dropdown-item logout">
                  Logout
                </button>
              </div>
            </div>
          ) : (
            <div className="auth-links">
              <Link to="/login" className="auth-link">
                Login
              </Link>
              <Link to="/register" className="auth-link register">
                Sign Up
              </Link>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};

export default StoreNavigation;

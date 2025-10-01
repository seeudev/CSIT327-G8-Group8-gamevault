import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import './Home.css';

/**
 * Home Component
 * Landing page for authenticated users
 */
const Home = () => {
  const { user, logout, isAdmin } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className="home-container">
      <div className="home-header">
        <h1>Welcome to GameVault</h1>
        <button onClick={handleLogout} className="btn-logout">
          Logout
        </button>
      </div>

      <div className="user-info-card">
        <h2>User Profile</h2>
        <div className="user-details">
          <div className="detail-row">
            <span className="label">Username:</span>
            <span className="value">{user?.username}</span>
          </div>
          <div className="detail-row">
            <span className="label">Email:</span>
            <span className="value">{user?.email}</span>
          </div>
          <div className="detail-row">
            <span className="label">Full Name:</span>
            <span className="value">{user?.full_name || 'Not set'}</span>
          </div>
          <div className="detail-row">
            <span className="label">Role:</span>
            <span className={`badge ${isAdmin ? 'admin' : 'buyer'}`}>
              {user?.role?.display_name || 'Buyer'}
            </span>
          </div>
          <div className="detail-row">
            <span className="label">Account Status:</span>
            <span className={`badge ${user?.is_verified ? 'verified' : 'unverified'}`}>
              {user?.is_verified ? 'Verified' : 'Unverified'}
            </span>
          </div>
        </div>
      </div>

      <div className="features-section">
        <h2>Module 1: Authentication & Authorization ✅</h2>
        <div className="features-grid">
          <div className="feature-card">
            <h3>✓ User Registration</h3>
            <p>Complete registration system with validation</p>
          </div>
          <div className="feature-card">
            <h3>✓ User Login</h3>
            <p>JWT-based authentication with token refresh</p>
          </div>
          <div className="feature-card">
            <h3>✓ Role-Based Access</h3>
            <p>Admin and Buyer roles with permissions</p>
          </div>
          <div className="feature-card">
            <h3>✓ Protected Routes</h3>
            <p>Route protection based on authentication</p>
          </div>
        </div>
      </div>

      <div className="info-section">
        <h3>🎮 What's Next?</h3>
        <ul>
          <li>Module 2: Admin Core - Game management system ✅</li>
          <li>Module 3: Storefront Core - Public game catalog</li>
          <li>Module 4: Foundation & DevOps - Deployment setup</li>
        </ul>
        
        {isAdmin && (
          <div className="admin-access">
            <h4>🔧 Admin Access</h4>
            <p>You have admin privileges! Access the admin dashboard to manage games and users.</p>
            <button 
              onClick={() => navigate('/admin')}
              className="btn-admin"
            >
              🎮 Go to Admin Dashboard
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Home;

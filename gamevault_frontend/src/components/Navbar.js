import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function Navbar() {
  const { user, logout } = useAuth();

  return (
    <nav className="navbar">
      <div className="nav-container">
        <Link to="/" className="nav-logo">
          GameVault
        </Link>
        <div className="nav-menu">
          <Link to="/" className="nav-link">Games</Link>
          {user ? (
            <>
              <Link to="/orders" className="nav-link">My Orders</Link>
              <span className="nav-user">
                {user.username} (${user.wallet_balance})
              </span>
              <button onClick={logout} className="nav-link logout-btn">
                Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="nav-link">Login</Link>
              <Link to="/register" className="nav-link">Register</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}

export default Navbar;

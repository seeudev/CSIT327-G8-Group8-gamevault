import React, { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import './AdminLayout.css';

/**
 * AdminLayout Component
 * Main layout for admin dashboard with sidebar navigation
 */
const AdminLayout = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const navigationItems = [
    {
      name: 'Dashboard',
      path: '/admin',
      icon: '📊',
      exact: true
    },
    {
      name: 'Games',
      path: '/admin/games',
      icon: '🎮',
      children: [
        { name: 'All Games', path: '/admin/games' },
        { name: 'Add Game', path: '/admin/games/new' },
        { name: 'Categories', path: '/admin/games/categories' }
      ]
    },
    {
      name: 'Orders',
      path: '/admin/orders',
      icon: '📦',
      children: [
        { name: 'All Orders', path: '/admin/orders' },
        { name: 'Pending', path: '/admin/orders/pending' },
        { name: 'Completed', path: '/admin/orders/completed' }
      ]
    },
    {
      name: 'Users',
      path: '/admin/users',
      icon: '👥',
      children: [
        { name: 'All Users', path: '/admin/users' },
        { name: 'Admins', path: '/admin/users/admins' },
        { name: 'Buyers', path: '/admin/users/buyers' }
      ]
    },
    {
      name: 'Analytics',
      path: '/admin/analytics',
      icon: '📈'
    },
    {
      name: 'Settings',
      path: '/admin/settings',
      icon: '⚙️'
    }
  ];

  const isActivePath = (path, exact = false) => {
    if (exact) {
      return location.pathname === path;
    }
    return location.pathname.startsWith(path);
  };

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  return (
    <div className="admin-layout">
      {/* Sidebar */}
      <div className={`admin-sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
        <div className="sidebar-header">
          <div className="logo">
            <span className="logo-icon">🎮</span>
            {sidebarOpen && <span className="logo-text">GameVault Admin</span>}
          </div>
          <button 
            className="sidebar-toggle"
            onClick={toggleSidebar}
            title={sidebarOpen ? 'Collapse sidebar' : 'Expand sidebar'}
          >
            {sidebarOpen ? '◀' : '▶'}
          </button>
        </div>

        <nav className="sidebar-nav">
          {navigationItems.map((item) => (
            <div key={item.name} className="nav-item">
              <div 
                className={`nav-link ${isActivePath(item.path, item.exact) ? 'active' : ''}`}
                onClick={() => navigate(item.path)}
              >
                <span className="nav-icon">{item.icon}</span>
                {sidebarOpen && <span className="nav-text">{item.name}</span>}
                {sidebarOpen && item.children && (
                  <span className="nav-arrow">▼</span>
                )}
              </div>
              
              {sidebarOpen && item.children && (
                <div className="nav-children">
                  {item.children.map((child) => (
                    <div
                      key={child.name}
                      className={`nav-child ${isActivePath(child.path) ? 'active' : ''}`}
                      onClick={() => navigate(child.path)}
                    >
                      {child.name}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="user-info">
            <div className="user-avatar">
              {user?.username?.charAt(0).toUpperCase()}
            </div>
            {sidebarOpen && (
              <div className="user-details">
                <div className="user-name">{user?.username}</div>
                <div className="user-role">{user?.role?.display_name}</div>
              </div>
            )}
          </div>
          <button 
            className="logout-btn"
            onClick={handleLogout}
            title="Logout"
          >
            {sidebarOpen ? 'Logout' : '🚪'}
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="admin-main">
        {/* Top Header */}
        <header className="admin-header">
          <div className="header-left">
            <button 
              className="mobile-menu-btn"
              onClick={toggleSidebar}
            >
              ☰
            </button>
            <h1 className="page-title">
              {navigationItems.find(item => 
                isActivePath(item.path, item.exact) || 
                (item.children && item.children.some(child => isActivePath(child.path)))
              )?.name || 'Admin Dashboard'}
            </h1>
          </div>
          
          <div className="header-right">
            <div className="header-actions">
              <button className="action-btn" title="Notifications">
                🔔
              </button>
              <button className="action-btn" title="Settings">
                ⚙️
              </button>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="admin-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default AdminLayout;

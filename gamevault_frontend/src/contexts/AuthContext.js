import React, { createContext, useState, useContext, useEffect } from 'react';
import { authAPI } from '../services/api';

/**
 * AuthContext - Manages authentication state throughout the application
 * Provides user data, login/logout functions, and loading states
 */

const AuthContext = createContext(null);

/**
 * Custom hook to use auth context
 * @throws {Error} If used outside of AuthProvider
 */
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

/**
 * AuthProvider Component
 * Wraps the app and provides authentication state and methods
 */
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  /**
   * Load user from localStorage on mount
   */
  useEffect(() => {
    const loadUser = async () => {
      try {
        const storedUser = localStorage.getItem('user');
        const accessToken = localStorage.getItem('accessToken');

        if (storedUser && accessToken) {
          setUser(JSON.parse(storedUser));
          
          // Verify token is still valid
          try {
            await authAPI.verifyToken();
          } catch (err) {
            // Token is invalid, clear auth data
            logout();
          }
        }
      } catch (err) {
        console.error('Error loading user:', err);
      } finally {
        setLoading(false);
      }
    };

    loadUser();
  }, []);

  /**
   * Register a new user
   * @param {Object} userData - Registration data
   * @returns {Promise<Object>} User data and tokens
   */
  const register = async (userData) => {
    try {
      setError(null);
      setLoading(true);

      const response = await authAPI.register(userData);
      const { user: newUser, tokens } = response.data;

      // Save tokens and user data
      localStorage.setItem('accessToken', tokens.access);
      localStorage.setItem('refreshToken', tokens.refresh);
      localStorage.setItem('user', JSON.stringify(newUser));

      setUser(newUser);
      return response.data;
    } catch (err) {
      const errorMessage = err.response?.data?.details || 
                          err.response?.data?.error || 
                          'Registration failed';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  /**
   * Login user
   * @param {string} username - Username or email
   * @param {string} password - Password
   * @returns {Promise<Object>} User data and tokens
   */
  const login = async (username, password) => {
    try {
      setError(null);
      setLoading(true);

      const response = await authAPI.login({ username, password });
      const { user: loggedInUser, tokens } = response.data;

      // Save tokens and user data
      localStorage.setItem('accessToken', tokens.access);
      localStorage.setItem('refreshToken', tokens.refresh);
      localStorage.setItem('user', JSON.stringify(loggedInUser));

      setUser(loggedInUser);
      return response.data;
    } catch (err) {
      const errorMessage = err.response?.data?.details || 
                          err.response?.data?.error || 
                          'Login failed';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  /**
   * Logout user
   */
  const logout = async () => {
    try {
      const refreshToken = localStorage.getItem('refreshToken');
      
      if (refreshToken) {
        // Call logout endpoint to blacklist token
        await authAPI.logout(refreshToken);
      }
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      // Clear local storage and state regardless of API call result
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      localStorage.removeItem('user');
      setUser(null);
      setError(null);
    }
  };

  /**
   * Update user profile
   * @param {Object} profileData - Updated profile data
   * @returns {Promise<Object>} Updated user data
   */
  const updateProfile = async (profileData) => {
    try {
      setError(null);
      setLoading(true);

      const response = await authAPI.updateProfile(profileData);
      const updatedUser = response.data;

      // Update stored user data
      localStorage.setItem('user', JSON.stringify(updatedUser));
      setUser(updatedUser);

      return updatedUser;
    } catch (err) {
      const errorMessage = err.response?.data?.details || 
                          err.response?.data?.error || 
                          'Profile update failed';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  /**
   * Change user password
   * @param {string} oldPassword - Current password
   * @param {string} newPassword - New password
   * @param {string} newPasswordConfirm - Password confirmation
   * @returns {Promise<Object>} Success message
   */
  const changePassword = async (oldPassword, newPassword, newPasswordConfirm) => {
    try {
      setError(null);
      setLoading(true);

      const response = await authAPI.changePassword({
        old_password: oldPassword,
        new_password: newPassword,
        new_password_confirm: newPasswordConfirm,
      });

      return response.data;
    } catch (err) {
      const errorMessage = err.response?.data?.details || 
                          err.response?.data?.error || 
                          'Password change failed';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  /**
   * Check if user is authenticated
   */
  const isAuthenticated = !!user;

  /**
   * Check if user is admin
   */
  const isAdmin = user?.is_admin || false;

  /**
   * Check if user is buyer
   */
  const isBuyer = user?.is_buyer || false;

  const value = {
    user,
    loading,
    error,
    isAuthenticated,
    isAdmin,
    isBuyer,
    register,
    login,
    logout,
    updateProfile,
    changePassword,
    setError,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

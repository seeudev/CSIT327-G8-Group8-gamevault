import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { CartProvider } from './contexts/CartContext';
import Login from './components/auth/Login';
import Register from './components/auth/Register';
import Home from './components/Home';
import ProtectedRoute from './components/auth/ProtectedRoute';
import AdminLayout from './components/admin/AdminLayout';
import AdminDashboard from './components/admin/AdminDashboard';
import GameList from './components/admin/GameList';
import GameForm from './components/admin/GameForm';
import GameLibrary from './components/store/GameLibrary';
import CartPage from './components/store/CartPage';
import CheckoutSuccess from './components/store/CheckoutSuccess';
import './App.css';

/**
 * Main App Component
 * Sets up routing and authentication context
 */
function App() {
  return (
    <Router>
      <AuthProvider>
        <CartProvider>
          <div className="App">
            <Routes>
              {/* Public routes */}
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />

              {/* Store routes (public) */}
              <Route path="/store" element={<GameLibrary />} />
              <Route path="/store/cart" element={<CartPage />} />
              <Route path="/store/checkout/success" element={<CheckoutSuccess />} />

              {/* Protected routes */}
              <Route
                path="/"
                element={
                  <ProtectedRoute>
                    <Home />
                  </ProtectedRoute>
                }
              />

              {/* Admin routes */}
              <Route
                path="/admin/*"
                element={
                  <ProtectedRoute requireAdmin={true}>
                    <AdminLayout />
                  </ProtectedRoute>
                }
              >
                <Route index element={<AdminDashboard />} />
                <Route path="games" element={<GameList />} />
                <Route path="games/new" element={<GameForm />} />
                <Route path="games/:slug/edit" element={<GameForm />} />
              </Route>

              {/* Redirect to store by default */}
              <Route path="*" element={<Navigate to="/store" replace />} />
            </Routes>
          </div>
        </CartProvider>
      </AuthProvider>
    </Router>
  );
}

export default App;

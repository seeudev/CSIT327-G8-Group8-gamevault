import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useCart } from '../../contexts/CartContext';
import { useAuth } from '../../contexts/AuthContext';
import { storeAPI } from '../../services/api';
import { formatCurrency, formatDate } from '../../utils/helpers';
import Button from '../common/Button';
import Card from '../common/Card';
import Input from '../common/Input';
import StoreNavigation from './StoreNavigation';
import './CartPage.css';

/**
 * CartPage Component
 * Displays cart items and handles checkout
 */
const CartPage = () => {
  const { items, totalItems, totalPrice, updateQuantity, removeFromCart, clearCart, loading, error } = useCart();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [checkoutLoading, setCheckoutLoading] = useState(false);
  const [checkoutError, setCheckoutError] = useState(null);

  const handleQuantityChange = (gameId, newQuantity) => {
    if (newQuantity < 1) {
      removeFromCart(gameId);
    } else {
      updateQuantity(gameId, newQuantity);
    }
  };

  const handleRemoveItem = (gameId) => {
    if (window.confirm('Are you sure you want to remove this item from your cart?')) {
      removeFromCart(gameId);
    }
  };

  const handleCheckout = async () => {
    if (!user) {
      navigate('/login');
      return;
    }

    if (items.length === 0) {
      setCheckoutError('Your cart is empty');
      return;
    }

    setCheckoutLoading(true);
    setCheckoutError(null);

    try {
      // Create order data
      const orderData = {
        items: items.map(item => ({
          game_id: item.id,
          quantity: item.quantity,
          price: item.price
        })),
        total_amount: totalPrice,
        total_items: totalItems
      };

      // Simulate order creation (since we don't have a real payment system)
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // In a real app, you would call the API here:
      // const response = await storeAPI.createOrder(orderData);
      
      // Clear cart and redirect to success page
      clearCart();
      navigate('/store/checkout/success');
    } catch (err) {
      setCheckoutError('Checkout failed. Please try again.');
      console.error('Checkout error:', err);
    } finally {
      setCheckoutLoading(false);
    }
  };

  const handleClearCart = () => {
    if (window.confirm('Are you sure you want to clear your cart?')) {
      clearCart();
    }
  };

  if (items.length === 0) {
  return (
    <div className="cart-page">
      <StoreNavigation />
      
      <div className="cart-header">
        <h1>Shopping Cart</h1>
      </div>
        
        <div className="empty-cart">
          <div className="empty-cart-icon">🛒</div>
          <h2>Your cart is empty</h2>
          <p>Add some games to get started!</p>
          <Link to="/store" className="continue-shopping-btn">
            Continue Shopping
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="cart-page">
      <div className="cart-header">
        <h1>Shopping Cart</h1>
        <p>{totalItems} item{totalItems !== 1 ? 's' : ''} in your cart</p>
      </div>

      <div className="cart-content">
        <div className="cart-items">
          {items.map(item => (
            <div key={item.id} className="cart-item">
              <div className="item-image">
                {item.cover_image_url ? (
                  <img
                    src={item.cover_image_url}
                    alt={item.title}
                    onError={(e) => {
                      e.target.src = '/api/placeholder/100/150';
                    }}
                  />
                ) : (
                  <div className="image-placeholder">
                    <span>No Image</span>
                  </div>
                )}
              </div>

              <div className="item-details">
                <h3 className="item-title">
                  <Link to={`/store/game/${item.slug}`}>
                    {item.title}
                  </Link>
                </h3>
                <p className="item-developer">{item.developer}</p>
                <p className="item-genre">{item.genre}</p>
                <p className="item-price">{formatCurrency(item.price)}</p>
              </div>

              <div className="item-quantity">
                <label htmlFor={`quantity-${item.id}`}>Quantity:</label>
                <div className="quantity-controls">
                  <button
                    onClick={() => handleQuantityChange(item.id, item.quantity - 1)}
                    className="quantity-btn"
                    disabled={item.quantity <= 1}
                  >
                    -
                  </button>
                  <input
                    id={`quantity-${item.id}`}
                    type="number"
                    min="1"
                    value={item.quantity}
                    onChange={(e) => handleQuantityChange(item.id, parseInt(e.target.value) || 1)}
                    className="quantity-input"
                  />
                  <button
                    onClick={() => handleQuantityChange(item.id, item.quantity + 1)}
                    className="quantity-btn"
                  >
                    +
                  </button>
                </div>
              </div>

              <div className="item-total">
                <p className="item-total-price">
                  {formatCurrency(item.price * item.quantity)}
                </p>
                <button
                  onClick={() => handleRemoveItem(item.id)}
                  className="remove-item-btn"
                  title="Remove item"
                >
                  ×
                </button>
              </div>
            </div>
          ))}
        </div>

        <div className="cart-summary">
          <div className="summary-card">
            <h3>Order Summary</h3>
            
            <div className="summary-row">
              <span>Subtotal ({totalItems} items):</span>
              <span>{formatCurrency(totalPrice)}</span>
            </div>
            
            <div className="summary-row">
              <span>Tax:</span>
              <span>Calculated at checkout</span>
            </div>
            
            <div className="summary-row total">
              <span>Total:</span>
              <span>{formatCurrency(totalPrice)}</span>
            </div>

            {checkoutError && (
              <div className="checkout-error">
                {checkoutError}
              </div>
            )}

            <div className="checkout-actions">
              <Button
                onClick={handleCheckout}
                variant="success"
                size="large"
                fullWidth
                loading={checkoutLoading}
                disabled={checkoutLoading || loading}
              >
                {checkoutLoading ? 'Processing...' : 'Proceed to Checkout'}
              </Button>
              
              <Button
                onClick={handleClearCart}
                variant="danger"
                size="medium"
                fullWidth
                disabled={checkoutLoading || loading}
              >
                Clear Cart
              </Button>
            </div>

            <div className="continue-shopping">
              <Link to="/store">Continue Shopping</Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CartPage;

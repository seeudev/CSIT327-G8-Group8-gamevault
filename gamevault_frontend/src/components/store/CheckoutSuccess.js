import React from 'react';
import { Link } from 'react-router-dom';
import { useCart } from '../../contexts/CartContext';
import StoreNavigation from './StoreNavigation';
import './CheckoutSuccess.css';

/**
 * CheckoutSuccess Component
 * Displays purchase confirmation page
 */
const CheckoutSuccess = () => {
  const { formatPrice } = useCart();

  return (
    <div className="checkout-success">
      <StoreNavigation />
      
      <div className="success-container">
        <div className="success-icon">
          <div className="checkmark">
            <div className="checkmark-stem"></div>
            <div className="checkmark-kick"></div>
          </div>
        </div>

        <div className="success-content">
          <h1>Purchase Complete!</h1>
          <p className="success-message">
            Thank you for your purchase! Your order has been successfully processed.
          </p>
          
          <div className="success-details">
            <div className="detail-item">
              <span className="detail-label">Order Status:</span>
              <span className="detail-value success">Completed</span>
            </div>
            
            <div className="detail-item">
              <span className="detail-label">Payment Method:</span>
              <span className="detail-value">Simulated Payment</span>
            </div>
            
            <div className="detail-item">
              <span className="detail-label">Order Date:</span>
              <span className="detail-value">
                {new Date().toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </span>
            </div>
          </div>

          <div className="next-steps">
            <h3>What's Next?</h3>
            <ul>
              <li>You will receive a confirmation email shortly</li>
              <li>Game keys will be delivered to your account</li>
              <li>You can access your games from your library</li>
              <li>Contact support if you have any questions</li>
            </ul>
          </div>

          <div className="success-actions">
            <Link to="/store" className="continue-shopping-btn">
              Continue Shopping
            </Link>
            
            <Link to="/library" className="view-library-btn">
              View My Library
            </Link>
          </div>

          <div className="support-info">
            <p>
              Need help? Contact our support team at{' '}
              <a href="mailto:support@gamevault.com">support@gamevault.com</a>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CheckoutSuccess;

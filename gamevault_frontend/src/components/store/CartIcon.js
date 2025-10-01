import React from 'react';
import { Link } from 'react-router-dom';
import { useCart } from '../../contexts/CartContext';
import './CartIcon.css';

/**
 * CartIcon Component
 * Displays cart icon with item count
 */
const CartIcon = () => {
  const { totalItems } = useCart();

  return (
    <Link to="/store/cart" className="cart-icon">
      <div className="cart-icon-container">
        <svg
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="cart-svg"
        >
          <path
            d="M7 4V2C7 1.45 7.45 1 8 1H16C16.55 1 17 1.45 17 2V4H20C20.55 4 21 4.45 21 5S20.55 6 20 6H19V19C19 20.1 18.1 21 17 21H7C5.9 21 5 20.1 5 19V6H4C3.45 6 3 5.55 3 5S3.45 4 4 4H7ZM9 3V4H15V3H9ZM7 6V19H17V6H7Z"
            fill="currentColor"
          />
          <path
            d="M9 8V17H11V8H9ZM13 8V17H15V8H13Z"
            fill="currentColor"
          />
        </svg>
        
        {totalItems > 0 && (
          <span className="cart-count">
            {totalItems > 99 ? '99+' : totalItems}
          </span>
        )}
      </div>
    </Link>
  );
};

export default CartIcon;

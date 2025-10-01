import React from 'react';
import { theme } from '../../config/theme';
import './Button.css';

/**
 * Button Component
 * Reusable button component with consistent styling
 */
const Button = ({
  children,
  variant = 'primary',
  size = 'medium',
  disabled = false,
  loading = false,
  fullWidth = false,
  icon = null,
  iconPosition = 'left',
  onClick,
  type = 'button',
  className = '',
  ...props
}) => {
  const baseClasses = 'btn';
  const variantClasses = `btn-${variant}`;
  const sizeClasses = `btn-${size}`;
  const stateClasses = [
    disabled && 'btn-disabled',
    loading && 'btn-loading',
    fullWidth && 'btn-full-width'
  ].filter(Boolean).join(' ');
  
  const classes = [
    baseClasses,
    variantClasses,
    sizeClasses,
    stateClasses,
    className
  ].filter(Boolean).join(' ');

  const handleClick = (e) => {
    if (disabled || loading) {
      e.preventDefault();
      return;
    }
    onClick?.(e);
  };

  const renderIcon = () => {
    if (!icon) return null;
    
    const iconElement = typeof icon === 'string' ? (
      <span className="btn-icon-text">{icon}</span>
    ) : (
      icon
    );
    
    return (
      <span className={`btn-icon btn-icon-${iconPosition}`}>
        {iconElement}
      </span>
    );
  };

  const renderContent = () => {
    if (loading) {
      return (
        <>
          <span className="btn-spinner" />
          <span className="btn-text">Loading...</span>
        </>
      );
    }

    if (icon) {
      return (
        <>
          {iconPosition === 'left' && renderIcon()}
          <span className="btn-text">{children}</span>
          {iconPosition === 'right' && renderIcon()}
        </>
      );
    }

    return <span className="btn-text">{children}</span>;
  };

  return (
    <button
      type={type}
      className={classes}
      onClick={handleClick}
      disabled={disabled || loading}
      {...props}
    >
      {renderContent()}
    </button>
  );
};

export default Button;

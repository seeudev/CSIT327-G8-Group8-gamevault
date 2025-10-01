import React, { forwardRef } from 'react';
import './Input.css';

/**
 * Input Component
 * Reusable input component with consistent styling
 */
const Input = forwardRef(({
  type = 'text',
  label,
  placeholder,
  value,
  onChange,
  onBlur,
  onFocus,
  error,
  helperText,
  disabled = false,
  required = false,
  fullWidth = false,
  size = 'medium',
  variant = 'outlined',
  icon = null,
  iconPosition = 'left',
  className = '',
  ...props
}, ref) => {
  const baseClasses = 'input-wrapper';
  const sizeClasses = `input-${size}`;
  const variantClasses = `input-${variant}`;
  const stateClasses = [
    error && 'input-error',
    disabled && 'input-disabled',
    fullWidth && 'input-full-width',
    icon && `input-with-icon input-icon-${iconPosition}`
  ].filter(Boolean).join(' ');
  
  const classes = [
    baseClasses,
    sizeClasses,
    variantClasses,
    stateClasses,
    className
  ].filter(Boolean).join(' ');

  const inputClasses = [
    'input-field',
    error && 'input-field-error',
    disabled && 'input-field-disabled'
  ].filter(Boolean).join(' ');

  const renderIcon = () => {
    if (!icon) return null;
    
    const iconElement = typeof icon === 'string' ? (
      <span className="input-icon-text">{icon}</span>
    ) : (
      icon
    );
    
    return (
      <span className="input-icon">
        {iconElement}
      </span>
    );
  };

  return (
    <div className={classes}>
      {label && (
        <label className="input-label">
          {label}
          {required && <span className="input-required">*</span>}
        </label>
      )}
      
      <div className="input-container">
        {icon && iconPosition === 'left' && renderIcon()}
        
        <input
          ref={ref}
          type={type}
          className={inputClasses}
          placeholder={placeholder}
          value={value}
          onChange={onChange}
          onBlur={onBlur}
          onFocus={onFocus}
          disabled={disabled}
          required={required}
          {...props}
        />
        
        {icon && iconPosition === 'right' && renderIcon()}
      </div>
      
      {(error || helperText) && (
        <div className="input-message">
          {error && <span className="input-error-text">{error}</span>}
          {helperText && !error && <span className="input-helper-text">{helperText}</span>}
        </div>
      )}
    </div>
  );
});

Input.displayName = 'Input';

export default Input;

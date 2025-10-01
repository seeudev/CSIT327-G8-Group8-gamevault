import React from 'react';
import './Card.css';

/**
 * Card Component
 * Reusable card component with consistent styling
 */
const Card = ({
  children,
  title,
  subtitle,
  header,
  footer,
  padding = 'medium',
  shadow = 'medium',
  hover = false,
  clickable = false,
  onClick,
  className = '',
  ...props
}) => {
  const baseClasses = 'card';
  const paddingClasses = `card-padding-${padding}`;
  const shadowClasses = `card-shadow-${shadow}`;
  const stateClasses = [
    hover && 'card-hover',
    clickable && 'card-clickable'
  ].filter(Boolean).join(' ');
  
  const classes = [
    baseClasses,
    paddingClasses,
    shadowClasses,
    stateClasses,
    className
  ].filter(Boolean).join(' ');

  const handleClick = (e) => {
    if (clickable && onClick) {
      onClick(e);
    }
  };

  const handleKeyDown = (e) => {
    if (clickable && (e.key === 'Enter' || e.key === ' ')) {
      e.preventDefault();
      onClick?.(e);
    }
  };

  return (
    <div
      className={classes}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      tabIndex={clickable ? 0 : undefined}
      role={clickable ? 'button' : undefined}
      {...props}
    >
      {(header || title || subtitle) && (
        <div className="card-header">
          {header || (
            <>
              {title && <h3 className="card-title">{title}</h3>}
              {subtitle && <p className="card-subtitle">{subtitle}</p>}
            </>
          )}
        </div>
      )}
      
      <div className="card-content">
        {children}
      </div>
      
      {footer && (
        <div className="card-footer">
          {footer}
        </div>
      )}
    </div>
  );
};

export default Card;

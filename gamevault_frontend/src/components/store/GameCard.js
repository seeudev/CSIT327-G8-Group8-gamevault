import React from 'react';
import { Link } from 'react-router-dom';
import { useCart } from '../../contexts/CartContext';
import { formatCurrency } from '../../utils/helpers';
import Button from '../common/Button';
import Card from '../common/Card';
import './GameCard.css';

/**
 * GameCard Component
 * Displays individual game information in a card format
 */
const GameCard = ({ game }) => {
  const { addToCart, isInCart } = useCart();

  const handleAddToCart = (e) => {
    e.preventDefault();
    e.stopPropagation();
    addToCart(game);
  };


  const renderRating = (rating, totalReviews) => {
    if (!rating || totalReviews === 0) {
      return <span className="no-rating">No ratings yet</span>;
    }

    const stars = Math.round(rating);
    return (
      <div className="rating">
        <div className="stars">
          {[...Array(5)].map((_, i) => (
            <span
              key={i}
              className={`star ${i < stars ? 'filled' : 'empty'}`}
            >
              ★
            </span>
          ))}
        </div>
        <span className="rating-text">
          {rating.toFixed(1)} ({totalReviews} review{totalReviews !== 1 ? 's' : ''})
        </span>
      </div>
    );
  };

  const renderSaleBadge = () => {
    if (game.is_on_sale && game.discount_percentage > 0) {
      return (
        <div className="sale-badge">
          -{game.discount_percentage}%
        </div>
      );
    }
    return null;
  };

  const renderFeaturedBadge = () => {
    if (game.featured) {
      return (
        <div className="featured-badge">
          Featured
        </div>
      );
    }
    return null;
  };

  return (
    <Card className="game-card" hover clickable>
      <Link to={`/store/game/${game.slug}`} className="game-link">
        <div className="game-image-container">
          {game.cover_image_url ? (
            <img
              src={game.cover_image_url}
              alt={game.title}
              className="game-image"
              onError={(e) => {
                e.target.src = '/api/placeholder/300/400';
              }}
            />
          ) : (
            <div className="game-image-placeholder">
              <span>No Image</span>
            </div>
          )}
          
          {renderSaleBadge()}
          {renderFeaturedBadge()}
          
          {!game.is_in_stock && (
            <div className="out-of-stock-overlay">
              <span>Out of Stock</span>
            </div>
          )}
        </div>

        <div className="game-info">
          <h3 className="game-title">{game.title}</h3>
          
          <div className="game-meta">
            <span className="game-developer">{game.developer}</span>
            <span className="game-genre">{game.genre}</span>
          </div>

          {game.short_description && (
            <p className="game-description">
              {game.short_description.length > 100
                ? `${game.short_description.substring(0, 100)}...`
                : game.short_description
              }
            </p>
          )}

          <div className="game-rating">
            {renderRating(game.average_rating, game.total_reviews)}
          </div>

          <div className="game-platforms">
            {game.platforms && game.platforms.length > 0 && (
              <div className="platforms">
                {game.platforms.slice(0, 3).map(platform => (
                  <span key={platform} className="platform-tag">
                    {platform}
                  </span>
                ))}
                {game.platforms.length > 3 && (
                  <span className="platform-more">
                    +{game.platforms.length - 3} more
                  </span>
                )}
              </div>
            )}
          </div>

          <div className="game-pricing">
            <div className="price-container">
              {game.is_on_sale && game.original_price ? (
                <>
                  <span className="current-price">
                    {formatCurrency(game.price)}
                  </span>
                  <span className="original-price">
                    {formatCurrency(game.original_price)}
                  </span>
                </>
              ) : (
                <span className="current-price">
                  {formatCurrency(game.price)}
                </span>
              )}
            </div>
          </div>
        </div>
      </Link>

      <div className="game-actions">
        {game.is_in_stock ? (
          <Button
            onClick={handleAddToCart}
            variant={isInCart(game.id) ? 'success' : 'primary'}
            size="medium"
            fullWidth
            disabled={isInCart(game.id)}
          >
            {isInCart(game.id) ? 'In Cart' : 'Add to Cart'}
          </Button>
        ) : (
          <Button
            variant="secondary"
            size="medium"
            fullWidth
            disabled
          >
            Out of Stock
          </Button>
        )}
      </div>
    </Card>
  );
};

export default GameCard;

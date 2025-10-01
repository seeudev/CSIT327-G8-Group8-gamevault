import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import api from '../../services/api';
import './GameForm.css';

/**
 * GameForm Component
 * Form for creating and editing games
 */
const GameForm = () => {
  const navigate = useNavigate();
  const { slug } = useParams();
  const isEditing = !!slug;

  const [formData, setFormData] = useState({
    title: '',
    description: '',
    short_description: '',
    price: '',
    original_price: '',
    developer: '',
    publisher: '',
    release_date: '',
    genre: '',
    tags: [],
    minimum_requirements: '',
    recommended_requirements: '',
    platforms: [],
    status: 'active',
    stock_quantity: 0,
    meta_description: '',
    featured: false
  });

  const [coverImage, setCoverImage] = useState(null);
  const [screenshots, setScreenshots] = useState([]);
  const [trailerUrl, setTrailerUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [validationErrors, setValidationErrors] = useState({});

  const genreOptions = [
    'Action', 'Adventure', 'RPG', 'Strategy', 'Simulation', 
    'Sports', 'Racing', 'Puzzle', 'Horror', 'Fighting', 
    'Platformer', 'Shooter', 'Stealth', 'Survival', 'Other'
  ];

  const platformOptions = [
    'Windows', 'Mac', 'Linux', 'PlayStation', 'Xbox', 'Nintendo Switch'
  ];

  const statusOptions = [
    { value: 'active', label: 'Active' },
    { value: 'inactive', label: 'Inactive' },
    { value: 'coming_soon', label: 'Coming Soon' },
    { value: 'discontinued', label: 'Discontinued' }
  ];

  useEffect(() => {
    if (isEditing) {
      fetchGame();
    }
  }, [slug, isEditing]);

  const fetchGame = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/games/${slug}/`);
      const game = response.data;
      
      setFormData({
        title: game.title || '',
        description: game.description || '',
        short_description: game.short_description || '',
        price: game.price || '',
        original_price: game.original_price || '',
        developer: game.developer || '',
        publisher: game.publisher || '',
        release_date: game.release_date || '',
        genre: game.genre || '',
        tags: game.tags || [],
        minimum_requirements: game.minimum_requirements || '',
        recommended_requirements: game.recommended_requirements || '',
        platforms: game.platforms || [],
        status: game.status || 'active',
        stock_quantity: game.stock_quantity || 0,
        meta_description: game.meta_description || '',
        featured: game.featured || false
      });
      
      setTrailerUrl(game.trailer_url || '');
      setScreenshots(game.screenshots || []);
    } catch (err) {
      setError('Failed to fetch game details');
      console.error('Game fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
    
    // Clear validation error for this field
    if (validationErrors[name]) {
      setValidationErrors(prev => ({
        ...prev,
        [name]: null
      }));
    }
  };

  const handleTagsChange = (e) => {
    const tagsString = e.target.value;
    const tagsArray = tagsString.split(',').map(tag => tag.trim()).filter(tag => tag);
    setFormData(prev => ({
      ...prev,
      tags: tagsArray
    }));
  };

  const handlePlatformsChange = (platform) => {
    setFormData(prev => ({
      ...prev,
      platforms: prev.platforms.includes(platform)
        ? prev.platforms.filter(p => p !== platform)
        : [...prev.platforms, platform]
    }));
  };

  const handleCoverImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setCoverImage(file);
    }
  };

  const handleScreenshotsChange = (e) => {
    const files = Array.from(e.target.files);
    setScreenshots(files);
  };

  const validateForm = () => {
    const errors = {};

    if (!formData.title.trim()) {
      errors.title = 'Title is required';
    }

    if (!formData.description.trim()) {
      errors.description = 'Description is required';
    }

    if (!formData.price || formData.price <= 0) {
      errors.price = 'Price must be greater than 0';
    }

    if (!formData.developer.trim()) {
      errors.developer = 'Developer is required';
    }

    if (!formData.publisher.trim()) {
      errors.publisher = 'Publisher is required';
    }

    if (!formData.release_date) {
      errors.release_date = 'Release date is required';
    }

    if (!formData.genre) {
      errors.genre = 'Genre is required';
    }

    if (formData.platforms.length === 0) {
      errors.platforms = 'At least one platform is required';
    }

    if (formData.stock_quantity < 0) {
      errors.stock_quantity = 'Stock quantity cannot be negative';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const submitData = new FormData();
      
      // Add form fields
      Object.keys(formData).forEach(key => {
        if (key === 'tags' || key === 'platforms') {
          submitData.append(key, JSON.stringify(formData[key]));
        } else {
          submitData.append(key, formData[key]);
        }
      });

      // Add files
      if (coverImage) {
        submitData.append('cover_image', coverImage);
      }

      screenshots.forEach((file, index) => {
        submitData.append('screenshots', file);
      });

      if (trailerUrl) {
        submitData.append('trailer_url', trailerUrl);
      }

      let response;
      if (isEditing) {
        response = await api.patch(`/games/${slug}/`, submitData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
      } else {
        response = await api.post('/games/', submitData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
      }

      navigate('/admin/games');
    } catch (err) {
      if (err.response?.data?.details) {
        setValidationErrors(err.response.data.details);
      } else {
        setError('Failed to save game');
      }
      console.error('Game save error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading && isEditing) {
    return (
      <div className="game-form-loading">
        <div className="loading-spinner"></div>
        <p>Loading game details...</p>
      </div>
    );
  }

  return (
    <div className="game-form">
      <div className="form-header">
        <h1>{isEditing ? 'Edit Game' : 'Add New Game'}</h1>
        <p>{isEditing ? 'Update game information' : 'Create a new game for your store'}</p>
      </div>

      {error && (
        <div className="form-error">
          <span>⚠️ {error}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="game-form-content">
        <div className="form-section">
          <h2>Basic Information</h2>
          
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="title">Title *</label>
              <input
                type="text"
                id="title"
                name="title"
                value={formData.title}
                onChange={handleInputChange}
                className={validationErrors.title ? 'error' : ''}
                placeholder="Enter game title"
                required
              />
              {validationErrors.title && (
                <span className="field-error">{validationErrors.title}</span>
              )}
            </div>

            <div className="form-group">
              <label htmlFor="genre">Genre *</label>
              <select
                id="genre"
                name="genre"
                value={formData.genre}
                onChange={handleInputChange}
                className={validationErrors.genre ? 'error' : ''}
                required
              >
                <option value="">Select Genre</option>
                {genreOptions.map(genre => (
                  <option key={genre} value={genre}>{genre}</option>
                ))}
              </select>
              {validationErrors.genre && (
                <span className="field-error">{validationErrors.genre}</span>
              )}
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="description">Description *</label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleInputChange}
              className={validationErrors.description ? 'error' : ''}
              placeholder="Enter detailed game description"
              rows="6"
              required
            />
            {validationErrors.description && (
              <span className="field-error">{validationErrors.description}</span>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="short_description">Short Description</label>
            <textarea
              id="short_description"
              name="short_description"
              value={formData.short_description}
              onChange={handleInputChange}
              placeholder="Brief description for cards and previews"
              rows="3"
            />
          </div>
        </div>

        <div className="form-section">
          <h2>Pricing & Inventory</h2>
          
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="price">Price *</label>
              <input
                type="number"
                id="price"
                name="price"
                value={formData.price}
                onChange={handleInputChange}
                className={validationErrors.price ? 'error' : ''}
                placeholder="0.00"
                step="0.01"
                min="0.01"
                required
              />
              {validationErrors.price && (
                <span className="field-error">{validationErrors.price}</span>
              )}
            </div>

            <div className="form-group">
              <label htmlFor="original_price">Original Price</label>
              <input
                type="number"
                id="original_price"
                name="original_price"
                value={formData.original_price}
                onChange={handleInputChange}
                placeholder="0.00"
                step="0.01"
                min="0.01"
              />
              <small>For sale items (must be higher than current price)</small>
            </div>

            <div className="form-group">
              <label htmlFor="stock_quantity">Stock Quantity</label>
              <input
                type="number"
                id="stock_quantity"
                name="stock_quantity"
                value={formData.stock_quantity}
                onChange={handleInputChange}
                className={validationErrors.stock_quantity ? 'error' : ''}
                placeholder="0"
                min="0"
              />
              {validationErrors.stock_quantity && (
                <span className="field-error">{validationErrors.stock_quantity}</span>
              )}
            </div>
          </div>
        </div>

        <div className="form-section">
          <h2>Game Details</h2>
          
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="developer">Developer *</label>
              <input
                type="text"
                id="developer"
                name="developer"
                value={formData.developer}
                onChange={handleInputChange}
                className={validationErrors.developer ? 'error' : ''}
                placeholder="Game developer"
                required
              />
              {validationErrors.developer && (
                <span className="field-error">{validationErrors.developer}</span>
              )}
            </div>

            <div className="form-group">
              <label htmlFor="publisher">Publisher *</label>
              <input
                type="text"
                id="publisher"
                name="publisher"
                value={formData.publisher}
                onChange={handleInputChange}
                className={validationErrors.publisher ? 'error' : ''}
                placeholder="Game publisher"
                required
              />
              {validationErrors.publisher && (
                <span className="field-error">{validationErrors.publisher}</span>
              )}
            </div>

            <div className="form-group">
              <label htmlFor="release_date">Release Date *</label>
              <input
                type="date"
                id="release_date"
                name="release_date"
                value={formData.release_date}
                onChange={handleInputChange}
                className={validationErrors.release_date ? 'error' : ''}
                required
              />
              {validationErrors.release_date && (
                <span className="field-error">{validationErrors.release_date}</span>
              )}
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="tags">Tags</label>
            <input
              type="text"
              id="tags"
              value={formData.tags.join(', ')}
              onChange={handleTagsChange}
              placeholder="Enter tags separated by commas"
            />
            <small>e.g., multiplayer, single-player, co-op, online</small>
          </div>

          <div className="form-group">
            <label>Platforms *</label>
            <div className="platform-checkboxes">
              {platformOptions.map(platform => (
                <label key={platform} className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={formData.platforms.includes(platform)}
                    onChange={() => handlePlatformsChange(platform)}
                  />
                  <span>{platform}</span>
                </label>
              ))}
            </div>
            {validationErrors.platforms && (
              <span className="field-error">{validationErrors.platforms}</span>
            )}
          </div>
        </div>

        <div className="form-section">
          <h2>Media</h2>
          
          <div className="form-group">
            <label htmlFor="cover_image">Cover Image *</label>
            <input
              type="file"
              id="cover_image"
              accept="image/*"
              onChange={handleCoverImageChange}
            />
            <small>Upload the main cover image for the game</small>
          </div>

          <div className="form-group">
            <label htmlFor="screenshots">Screenshots</label>
            <input
              type="file"
              id="screenshots"
              accept="image/*"
              multiple
              onChange={handleScreenshotsChange}
            />
            <small>Upload multiple screenshots (max 10)</small>
          </div>

          <div className="form-group">
            <label htmlFor="trailer_url">Trailer URL</label>
            <input
              type="url"
              id="trailer_url"
              value={trailerUrl}
              onChange={(e) => setTrailerUrl(e.target.value)}
              placeholder="https://youtube.com/watch?v=..."
            />
            <small>YouTube or other video trailer URL</small>
          </div>
        </div>

        <div className="form-section">
          <h2>System Requirements</h2>
          
          <div className="form-group">
            <label htmlFor="minimum_requirements">Minimum Requirements</label>
            <textarea
              id="minimum_requirements"
              name="minimum_requirements"
              value={formData.minimum_requirements}
              onChange={handleInputChange}
              placeholder="Minimum system requirements"
              rows="4"
            />
          </div>

          <div className="form-group">
            <label htmlFor="recommended_requirements">Recommended Requirements</label>
            <textarea
              id="recommended_requirements"
              name="recommended_requirements"
              value={formData.recommended_requirements}
              onChange={handleInputChange}
              placeholder="Recommended system requirements"
              rows="4"
            />
          </div>
        </div>

        <div className="form-section">
          <h2>Settings</h2>
          
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="status">Status</label>
              <select
                id="status"
                name="status"
                value={formData.status}
                onChange={handleInputChange}
              >
                {statusOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="meta_description">Meta Description</label>
              <input
                type="text"
                id="meta_description"
                name="meta_description"
                value={formData.meta_description}
                onChange={handleInputChange}
                placeholder="SEO meta description"
                maxLength="160"
              />
              <small>{formData.meta_description.length}/160 characters</small>
            </div>
          </div>

          <div className="form-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                name="featured"
                checked={formData.featured}
                onChange={handleInputChange}
              />
              <span>Featured Game</span>
            </label>
            <small>Featured games appear prominently on the homepage</small>
          </div>
        </div>

        <div className="form-actions">
          <button
            type="button"
            onClick={() => navigate('/admin/games')}
            className="btn-secondary"
          >
            Cancel
          </button>
          <button
            type="submit"
            className="btn-primary"
            disabled={loading}
          >
            {loading ? 'Saving...' : (isEditing ? 'Update Game' : 'Create Game')}
          </button>
        </div>
      </form>
    </div>
  );
};

export default GameForm;

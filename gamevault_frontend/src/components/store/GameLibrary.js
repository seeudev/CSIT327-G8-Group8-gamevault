import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { storeAPI } from '../../services/api';
import GameCard from './GameCard';
import StoreNavigation from './StoreNavigation';
import './GameLibrary.css';

/**
 * GameLibrary Component
 * Public storefront page displaying all available games
 */
const GameLibrary = () => {
  const [games, setGames] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedGenre, setSelectedGenre] = useState('');
  const [sortBy, setSortBy] = useState('featured');
  const [genres, setGenres] = useState([]);

  useEffect(() => {
    fetchGames();
  }, [searchTerm, selectedGenre, sortBy]);

  const fetchGames = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params = new URLSearchParams();
      if (searchTerm) params.append('search', searchTerm);
      if (selectedGenre) params.append('genre', selectedGenre);
      if (sortBy) params.append('ordering', sortBy === 'featured' ? '-featured,-created_at' : sortBy);
      
      const response = await storeAPI.getGames(params.toString());
      setGames(response.data.results || response.data);
      
      // Extract unique genres for filter
      const uniqueGenres = [...new Set(response.data.results?.map(game => game.genre) || response.data.map(game => game.genre))];
      setGenres(uniqueGenres);
    } catch (err) {
      setError('Failed to load games. Please try again.');
      console.error('Error fetching games:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
  };

  const handleGenreFilter = (e) => {
    setSelectedGenre(e.target.value);
  };

  const handleSortChange = (e) => {
    setSortBy(e.target.value);
  };

  const clearFilters = () => {
    setSearchTerm('');
    setSelectedGenre('');
    setSortBy('featured');
  };

  if (loading) {
    return (
      <div className="game-library">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading games...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="game-library">
        <div className="error-container">
          <h2>Error Loading Games</h2>
          <p>{error}</p>
          <button onClick={fetchGames} className="retry-button">
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="game-library">
      <StoreNavigation />
      
      <div className="library-header">
        <h1>Game Library</h1>
        <p>Discover and purchase your favorite games</p>
      </div>

      <div className="library-filters">
        <div className="search-section">
          <input
            type="text"
            placeholder="Search games..."
            value={searchTerm}
            onChange={handleSearch}
            className="search-input"
          />
        </div>

        <div className="filter-section">
          <select
            value={selectedGenre}
            onChange={handleGenreFilter}
            className="genre-filter"
          >
            <option value="">All Genres</option>
            {genres.map(genre => (
              <option key={genre} value={genre}>{genre}</option>
            ))}
          </select>

          <select
            value={sortBy}
            onChange={handleSortChange}
            className="sort-filter"
          >
            <option value="featured">Featured First</option>
            <option value="title">Title A-Z</option>
            <option value="-title">Title Z-A</option>
            <option value="price">Price: Low to High</option>
            <option value="-price">Price: High to Low</option>
            <option value="-average_rating">Highest Rated</option>
            <option value="-release_date">Newest First</option>
          </select>

          <button onClick={clearFilters} className="clear-filters">
            Clear Filters
          </button>
        </div>
      </div>

      <div className="games-grid">
        {games.length === 0 ? (
          <div className="no-games">
            <h3>No games found</h3>
            <p>Try adjusting your search or filters</p>
          </div>
        ) : (
          games.map(game => (
            <GameCard key={game.id} game={game} />
          ))
        )}
      </div>

      {games.length > 0 && (
        <div className="library-footer">
          <p>Showing {games.length} game{games.length !== 1 ? 's' : ''}</p>
        </div>
      )}
    </div>
  );
};

export default GameLibrary;

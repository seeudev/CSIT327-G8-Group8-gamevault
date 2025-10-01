import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../services/api';
import './GameList.css';

/**
 * GameList Component
 * Admin interface for managing games with CRUD operations
 */
const GameList = () => {
  const navigate = useNavigate();
  const [games, setGames] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [genreFilter, setGenreFilter] = useState('');
  const [sortBy, setSortBy] = useState('-created_at');
  const [selectedGames, setSelectedGames] = useState([]);
  const [bulkAction, setBulkAction] = useState('');

  useEffect(() => {
    fetchGames();
  }, [searchTerm, statusFilter, genreFilter, sortBy]);

  const fetchGames = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      
      if (searchTerm) params.append('search', searchTerm);
      if (statusFilter) params.append('status', statusFilter);
      if (genreFilter) params.append('genre', genreFilter);
      if (sortBy) params.append('ordering', sortBy);

      const response = await api.get(`/games/?${params.toString()}`);
      setGames(response.data.results || response.data);
    } catch (err) {
      setError('Failed to fetch games');
      console.error('Games fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (gameId) => {
    if (!window.confirm('Are you sure you want to delete this game?')) {
      return;
    }

    try {
      // Find the game to get its slug
      const game = games.find(g => g.id === gameId);
      if (game) {
        await api.delete(`/games/${game.slug}/`);
        setGames(games.filter(g => g.id !== gameId));
      }
    } catch (err) {
      alert('Failed to delete game');
      console.error('Delete error:', err);
    }
  };

  const handleBulkAction = async () => {
    if (!bulkAction || selectedGames.length === 0) {
      alert('Please select games and an action');
      return;
    }

    try {
      if (bulkAction === 'delete') {
        if (!window.confirm(`Are you sure you want to delete ${selectedGames.length} games?`)) {
          return;
        }
        
        for (const gameId of selectedGames) {
          const game = games.find(g => g.id === gameId);
          if (game) {
            await api.delete(`/games/${game.slug}/`);
          }
        }
        setGames(games.filter(g => !selectedGames.includes(g.id)));
      } else {
        await api.post('/games/bulk-update-status/', {
          game_ids: selectedGames,
          status: bulkAction
        });
        
        // Update local state
        setGames(games.map(game => 
          selectedGames.includes(game.id) 
            ? { ...game, status: bulkAction }
            : game
        ));
      }
      
      setSelectedGames([]);
      setBulkAction('');
    } catch (err) {
      alert('Failed to perform bulk action');
      console.error('Bulk action error:', err);
    }
  };

  const handleSelectAll = () => {
    if (selectedGames.length === games.length) {
      setSelectedGames([]);
    } else {
      setSelectedGames(games.map(game => game.id));
    }
  };

  const handleSelectGame = (gameId) => {
    setSelectedGames(prev => 
      prev.includes(gameId) 
        ? prev.filter(id => id !== gameId)
        : [...prev, gameId]
    );
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      active: { class: 'active', text: 'Active' },
      inactive: { class: 'inactive', text: 'Inactive' },
      coming_soon: { class: 'coming-soon', text: 'Coming Soon' },
      discontinued: { class: 'discontinued', text: 'Discontinued' }
    };
    
    const config = statusConfig[status] || { class: 'unknown', text: status };
    return <span className={`status-badge ${config.class}`}>{config.text}</span>;
  };

  if (loading) {
    return (
      <div className="game-list-loading">
        <div className="loading-spinner"></div>
        <p>Loading games...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="game-list-error">
        <div className="error-icon">⚠️</div>
        <h3>Error Loading Games</h3>
        <p>{error}</p>
        <button onClick={fetchGames} className="retry-btn">
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="game-list">
      {/* Header */}
      <div className="game-list-header">
        <div className="header-left">
          <h1>Game Management</h1>
          <p>Manage your game catalog</p>
        </div>
        <div className="header-right">
          <button 
            className="btn-primary"
            onClick={() => navigate('/admin/games/new')}
          >
            ➕ Add New Game
          </button>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="game-filters">
        <div className="filter-group">
          <input
            type="text"
            placeholder="Search games..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>

        <div className="filter-group">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="filter-select"
          >
            <option value="">All Status</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="coming_soon">Coming Soon</option>
            <option value="discontinued">Discontinued</option>
          </select>
        </div>

        <div className="filter-group">
          <select
            value={genreFilter}
            onChange={(e) => setGenreFilter(e.target.value)}
            className="filter-select"
          >
            <option value="">All Genres</option>
            <option value="Action">Action</option>
            <option value="RPG">RPG</option>
            <option value="Strategy">Strategy</option>
            <option value="Adventure">Adventure</option>
            <option value="Simulation">Simulation</option>
            <option value="Sports">Sports</option>
            <option value="Racing">Racing</option>
            <option value="Puzzle">Puzzle</option>
          </select>
        </div>

        <div className="filter-group">
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="filter-select"
          >
            <option value="-created_at">Newest First</option>
            <option value="created_at">Oldest First</option>
            <option value="title">Title A-Z</option>
            <option value="-title">Title Z-A</option>
            <option value="price">Price Low-High</option>
            <option value="-price">Price High-Low</option>
            <option value="-average_rating">Highest Rated</option>
          </select>
        </div>
      </div>

      {/* Bulk Actions */}
      {selectedGames.length > 0 && (
        <div className="bulk-actions">
          <div className="bulk-info">
            <span>{selectedGames.length} game(s) selected</span>
          </div>
          <div className="bulk-controls">
            <select
              value={bulkAction}
              onChange={(e) => setBulkAction(e.target.value)}
              className="bulk-select"
            >
              <option value="">Select Action</option>
              <option value="active">Set Active</option>
              <option value="inactive">Set Inactive</option>
              <option value="coming_soon">Set Coming Soon</option>
              <option value="discontinued">Set Discontinued</option>
              <option value="delete">Delete Games</option>
            </select>
            <button 
              onClick={handleBulkAction}
              className="bulk-action-btn"
              disabled={!bulkAction}
            >
              Apply
            </button>
            <button 
              onClick={() => setSelectedGames([])}
              className="bulk-cancel-btn"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Games Table */}
      <div className="games-table-container">
        <table className="games-table">
          <thead>
            <tr>
              <th>
                <input
                  type="checkbox"
                  checked={selectedGames.length === games.length && games.length > 0}
                  onChange={handleSelectAll}
                  className="select-checkbox"
                />
              </th>
              <th>Game</th>
              <th>Price</th>
              <th>Status</th>
              <th>Stock</th>
              <th>Rating</th>
              <th>Created</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {games.length === 0 ? (
              <tr>
                <td colSpan="8" className="no-games">
                  <div className="no-games-content">
                    <div className="no-games-icon">🎮</div>
                    <h3>No games found</h3>
                    <p>Start by adding your first game to the store</p>
                    <button 
                      className="btn-primary"
                      onClick={() => navigate('/admin/games/new')}
                    >
                      Add Your First Game
                    </button>
                  </div>
                </td>
              </tr>
            ) : (
              games.map((game) => (
                <tr key={game.id} className={selectedGames.includes(game.id) ? 'selected' : ''}>
                  <td>
                    <input
                      type="checkbox"
                      checked={selectedGames.includes(game.id)}
                      onChange={() => handleSelectGame(game.id)}
                      className="select-checkbox"
                    />
                  </td>
                  <td>
                    <div className="game-info">
                      <div className="game-cover">
                        {game.cover_image_url ? (
                          <img src={game.cover_image_url} alt={game.title} />
                        ) : (
                          <div className="no-cover">🎮</div>
                        )}
                      </div>
                      <div className="game-details">
                        <h4>{game.title}</h4>
                        <p>{game.developer}</p>
                        <span className="genre-tag">{game.genre}</span>
                      </div>
                    </div>
                  </td>
                  <td>
                    <div className="price-info">
                      <span className="current-price">${game.price}</span>
                      {game.is_on_sale && (
                        <span className="original-price">${game.original_price}</span>
                      )}
                    </div>
                  </td>
                  <td>{getStatusBadge(game.status)}</td>
                  <td>
                    <span className={`stock-count ${game.is_in_stock ? 'in-stock' : 'out-of-stock'}`}>
                      {game.stock_quantity}
                    </span>
                  </td>
                  <td>
                    <div className="rating-info">
                      <span className="rating">⭐ {game.average_rating || 'N/A'}</span>
                      <span className="review-count">({game.total_reviews})</span>
                    </div>
                  </td>
                  <td>
                    <span className="created-date">
                      {new Date(game.created_at).toLocaleDateString()}
                    </span>
                  </td>
                  <td>
                    <div className="action-buttons">
                      <button 
                        className="action-btn edit"
                        onClick={() => navigate(`/admin/games/${game.slug}/edit`)}
                        title="Edit Game"
                      >
                        ✏️
                      </button>
                      <button 
                        className="action-btn view"
                        onClick={() => navigate(`/admin/games/${game.slug}`)}
                        title="View Details"
                      >
                        👁️
                      </button>
                      <button 
                        className="action-btn delete"
                        onClick={() => handleDelete(game.id)}
                        title="Delete Game"
                      >
                        🗑️
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Results Summary */}
      <div className="results-summary">
        <p>Showing {games.length} game(s)</p>
      </div>
    </div>
  );
};

export default GameList;

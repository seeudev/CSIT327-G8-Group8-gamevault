import React, { useState, useEffect } from 'react';
import { gamesAPI } from '../services/api';

function GameList() {
  const [games, setGames] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadGames();
  }, []);

  const loadGames = async () => {
    try {
      setLoading(true);
      const response = await gamesAPI.getGames();
      setGames(response.data.results);
    } catch (err) {
      setError('Failed to load games');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="loading">Loading games...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="game-list">
      <h1>Game Vault - Browse Games</h1>
      <div className="games-grid">
        {games.map((game) => (
          <div key={game.id} className="game-card">
            <h3>{game.title}</h3>
            <p className="platform">{game.platform}</p>
            <p className="genre">{game.genre}</p>
            <p className="price">${game.price}</p>
            <p className="stock">Stock: {game.stock_count}</p>
            <button disabled={game.stock_count === 0}>
              {game.stock_count > 0 ? 'Add to Cart' : 'Out of Stock'}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

export default GameList;

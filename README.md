# GameVault

GameVault is a web application for selling digital video game keys and applications.

## Tech Stack
- **Frontend:** ReactJS (to be implemented)
- **Backend:** Django REST Framework
- **Database:** PostgreSQL (Supabase)
- **Authentication:** JWT (JSON Web Tokens)

## Features
- User registration and authentication
- Game catalog browsing with filters
- Digital game key inventory management
- Order processing and purchase system
- User wallet for payments
- Admin panel for game and inventory management

## Setup Instructions

### Backend Setup

1. **Clone the repository:**
```bash
git clone https://github.com/seeudev/gamevault.git
cd gamevault
```

2. **Create a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables:**
```bash
cp .env.example .env
# Edit .env with your database credentials and settings
```

5. **Run migrations:**
```bash
cd gamevault_backend
python manage.py migrate
```

6. **Create a superuser (admin):**
```bash
python manage.py createsuperuser
```

7. **Run the development server:**
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`

### Supabase PostgreSQL Connection

To connect to Supabase PostgreSQL, add your connection string to the `.env` file:

```
DATABASE_URL=postgresql://user:password@db.xxxxx.supabase.co:5432/postgres
```

You can find your connection details in your Supabase project settings.

## API Endpoints

### Authentication
- `POST /api/auth/token/` - Obtain JWT access and refresh tokens
- `POST /api/auth/token/refresh/` - Refresh access token

### Users
- `POST /api/users/` - Register a new user
- `GET /api/users/me/` - Get current user profile
- `PUT /api/users/me/` - Update current user profile

### Games
- `GET /api/games/` - List all games (supports `?platform=` and `?genre=` filters)
- `GET /api/games/{id}/` - Get specific game details
- `POST /api/games/` - Create a new game (admin only)
- `PUT /api/games/{id}/` - Update game (admin only)
- `DELETE /api/games/{id}/` - Delete game (admin only)

### Orders
- `GET /api/orders/` - List current user's orders
- `POST /api/orders/` - Create a new order (purchase games)
- `GET /api/orders/{id}/` - Get order details
- `GET /api/orders/{id}/keys/` - Get game keys for completed order

## API Usage Examples

### Register a User
```bash
curl -X POST http://localhost:8000/api/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "gamer123",
    "email": "gamer@example.com",
    "password": "securepass123",
    "password2": "securepass123",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

### Login (Get Token)
```bash
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "gamer123",
    "password": "securepass123"
  }'
```

### Get Games List
```bash
curl http://localhost:8000/api/games/
```

### Create an Order
```bash
curl -X POST http://localhost:8000/api/orders/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "game_ids": [1, 2]
  }'
```

## Database Models

### User Model
- Extended Django User with additional fields:
  - `email` (unique)
  - `phone_number`
  - `date_of_birth`
  - `wallet_balance`
  - Related `UserProfile` with bio, avatar, and verification status

### Game Model
- `title`, `description`, `price`
- `platform` (PC, PS5, PS4, Xbox, Switch)
- `genre`, `publisher`, `release_date`
- `cover_image_url`
- `stock_count`, `is_active`

### GameKey Model
- Links to `Game`
- `key_code` (encrypted game activation key)
- `status` (Available, Sold, Reserved)
- Timestamps for tracking

### Order Model
- Links to `User`
- `total_amount`, `status`
- Related `OrderItem` entries

### OrderItem Model
- Links to `Order`, `Game`, and `GameKey`
- Captures price at time of purchase

## Admin Panel

Access the Django admin panel at `http://localhost:8000/admin/` to:
- Manage users and profiles
- Add/edit games and game keys
- View and manage orders
- Monitor system activity

## Development Roadmap

### Backend (Completed)
- ✅ User authentication with JWT
- ✅ Game catalog CRUD operations
- ✅ Order processing system
- ✅ Game key inventory management
- ✅ API endpoints with filtering

### Frontend (To Do)
- [ ] Set up React application
- [ ] User authentication UI
- [ ] Game catalog browsing
- [ ] Shopping cart functionality
- [ ] Order history and key viewing
- [ ] User profile management
- [ ] Responsive design

## License
This project is private and proprietary.

## Contributors
- seeudev

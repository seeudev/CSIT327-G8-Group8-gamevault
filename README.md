# GameVault

A simple, functional game store selling digital keys web application built with Django, PostgreSQL (Supabase), and vanilla HTML/CSS/JavaScript.

## Technology Stack

- **Backend**: Django 5.2.6
- **Database**: PostgreSQL (Supabase) 
- **Frontend**: Vanilla HTML, CSS, and JavaScript (no frameworks)
- **Dependencies**: Minimal - only essential packages

## Setup & Run Instructions

### 1. Set up Virtual Environment

```bash
python -m venv env
source env/bin/activate  # On Linux/Mac
# or
env/Scripts/activate     # On Windows
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Database

Edit the `.env` file in the root directory:

For SQLite (development):
```
# Leave DATABASE_URL commented out to use SQLite
#DATABASE_URL=postgresql://...
```

For Supabase PostgreSQL (production):
```
Session Pooler
DATABASE_URL=postgresql://user:password@host:port/database
```

### 4. Run Migrations

```bash
cd gamevault_backend
python manage.py migrate
```

### 5. Create Admin User (If SQLite)

```bash
python create_admin.py
```

Default credentials:
- Username: `admin`
- Password: `admin123`

### 6. (Optional) Seed Sample Games

```bash
python seed_games.py
```

This will populate the database with:
- 9 game categories (Action, Adventure, RPG, etc.)
- 23 game tags (3D, Fantasy, Singleplayer, etc.)
- 14 sample games with real data

The script is safe to run multiple times - it only creates missing records and won't modify existing data.

### 7. Run Development Server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` in your browser.

## Team Members

| Name | Role | Email |
|------|------|-------|
| Christian Harry R. Pancito | Developer | christianharry.pancito@cit.edu |
| Kelvin Chad L. Obejero | Developer | kelvinchad.obejero@cit.edu |
| Khryzia A. Ortega | Developer | khryzia.ortega@cit.edu |

## Deployed Link

main Branch is deployed on Railway (Link down in-between sprints)

(https://csit327-g8-group8-gamevault-production.up.railway.app/store/)

---

## Additional Project Details

## Database Schema

The application uses the following models:

### User
- user_id (Primary Key)
- username, email, password_hash
- registration_date
- is_admin (Boolean)

### Category (Module 8)
- id (Integer Primary Key)
- name (Unique)

### Tag (Module 8)
- tag_id (Primary Key)
- name (Unique)

### GameTag (Module 8)
- game_tag_id (Primary Key)
- game_id (Foreign Key to Game)
- tag_id (Foreign Key to Tag)
- Unique constraint on (game_id, tag_id)

### Game
- game_id (Primary Key)
- title, description
- category_id (Foreign Key to Category, nullable)
- price
- screenshot_url, file_url
- upload_date
- tags (Many-to-Many through GameTag)

### Cart
- cart_id (Primary Key)
- user_id (Foreign Key)
- created_at, status

### CartItem
- cart_item_id (Primary Key)
- cart_id, game_id (Foreign Keys)
- quantity, price_at_addition

### Transaction
- transaction_id (Primary Key)
- user_id (Foreign Key)
- transaction_date, total_amount, payment_status
- download_token

### TransactionItem
- transaction_item_id (Primary Key)
- transaction_id, game_id (Foreign Keys)
- price_at_purchase
- game_key (Unique, Module 5)
- key_sent_at (Module 5)

### EmailLog (Module 5)
- log_id (Primary Key)
- user_id, game_id (Foreign Keys)
- game_key, sent_at, email_to, status

### PasswordResetToken (Module 9)
- token_id (Primary Key)
- user_id (Foreign Key)
- token (Unique)
- created_at, expires_at, is_used

### Review (Module 11)
- review_id (Primary Key)
- user_id, game_id (Foreign Keys)
- rating (1-5 stars)
- review_text (Optional)
- created_at, updated_at
- Unique constraint on (user_id, game_id)

### AdminActionLog
- log_id (Primary Key)
- admin_id (Foreign Key)
- action_type, target_game_id (Foreign Key)
- timestamp, notes



## Features

### Public Features
- Browse games (no login required)
- Search and filter games by category and tags (Module 8)
- View game details
- View game ratings and reviews (Module 11)

### User Features (requires login)
- Register and login
- Add games to shopping cart
- Update cart quantities
- Checkout and complete purchase
- View transaction history
- Download purchased games
- Receive game keys via email (Module 5)
- **Edit profile** (username, email, password) (Module 4)
- **Delete account** with confirmation (Module 4)
- **Reset password** via email token (Module 9)
- **Rate and review games** (1-5 stars with optional text) (Module 11)
- **Edit and delete own reviews** (Module 11)

### Admin Features (requires is_admin=True)
- Access admin dashboard
- Create, edit, and delete games
- Manage categories and tags (Module 8)
- View admin action logs
- View statistics

## API Endpoints

### User Profile Management (Module 4)

#### Update User Profile
**PUT** `/auth/api/users/:id/`
- **Authentication**: Required (session-based)
- **Authorization**: Users can only update their own profile
- **Request Body**:
  ```json
  {
    "username": "newusername",
    "email": "newemail@example.com",
    "current_password": "currentpass123",  // Required only if changing password
    "new_password": "newpass123"           // Optional
  }
  ```
- **Response (Success)**:
  ```json
  {
    "success": true,
    "message": "Profile updated successfully",
    "user": {
      "id": 1,
      "username": "newusername",
      "email": "newemail@example.com"
    }
  }
  ```
- **Response (Error)**:
  ```json
  {
    "success": false,
    "errors": {
      "username": "Username already exists",
      "email": "Email already exists",
      "current_password": "Current password is incorrect",
      "new_password": ["Password must be at least 8 characters long"]
    }
  }
  ```
- **Validation**:
  - Username uniqueness check
  - Email uniqueness check
  - Password strength validation (Django's built-in validators)
  - Current password verification for password changes

#### Delete User Account
**DELETE** `/auth/api/users/:id/delete/`
- **Authentication**: Required (session-based)
- **Authorization**: Users can only delete their own account
- **Response (Success)**:
  ```json
  {
    "success": true,
    "message": "Account deleted successfully"
  }
  ```
- **Response (Error)**:
  ```json
  {
    "success": false,
    "error": "Unauthorized: You can only delete your own account"
  }
  ```
- **Side Effects**:
  - User is logged out immediately
  - All user data is permanently deleted

### Password Reset (Module 9)

#### Request Password Reset
**POST** `/auth/api/password-reset/request/`
- **Authentication**: Not required
- **Request Body**:
  ```json
  {
    "email": "user@example.com"
  }
  ```
- **Response**: Always returns success (prevents email enumeration)
  ```json
  {
    "success": true,
    "message": "If an account exists with this email, a password reset link has been sent."
  }
  ```

  ### Wishlist / Favorites (Module 10)

  The wishlist feature allows authenticated users to save games for later using simple, function-based JSON endpoints.

  - List wishlist items:
    - GET `/store/api/wishlist/` (requires login)
    - Response: `{ "success": true, "data": [ { id, game_id, game_title, game_thumbnail, game_price, added_at }, ... ] }`

  - Add a game to wishlist:
    - POST `/store/api/wishlist/` (requires login)
    - JSON body: `{ "game_id": <int> }` or `{ "game": <int> }`
    - Response: `201 Created` with created item data

  - Remove a game from wishlist:
    - DELETE `/store/api/wishlist/<game_id>/` (requires login)
    - Also accepts POST for form-based removals

  Frontend:
  - Game cards include a heart button with class `.btn-wishlist` that calls these endpoints via `fetch()` and toggles an `active` class and SVG fill. CSRF token should be sent with `X-CSRFToken` header.


#### Confirm Password Reset
**POST** `/auth/api/password-reset/confirm/<token>/`
- **Authentication**: Not required
- **Request Body**:
  ```json
  {
    "new_password": "newpassword123"
  }
  ```
- **Response (Success)**:
  ```json
  {
    "success": true,
    "message": "Password has been reset successfully"
  }
  ```
- **Response (Error)**:
  ```json
  {
    "success": false,
    "error": "Invalid or expired token"
  }
  ```

### Game Reviews (Module 11)

#### Get Game Reviews
**GET** `/store/api/reviews/<game_id>/`
- **Authentication**: Not required (public endpoint)
- **Response**:
  ```json
  {
    "success": true,
    "reviews": [
      {
        "id": 1,
        "user_id": 2,
        "username": "john_doe",
        "rating": 5,
        "review_text": "Great game!",
        "created_at": "2025-10-30 12:00:00",
        "updated_at": "2025-10-30 12:00:00",
        "is_owner": false
      }
    ],
    "stats": {
      "average_rating": 4.5,
      "total_reviews": 10,
      "rating_breakdown": {
        "5": 6,
        "4": 2,
        "3": 1,
        "2": 1,
        "1": 0
      }
    }
  }
  ```

#### Create Review
**POST** `/store/api/reviews/<game_id>/create/`
- **Authentication**: Required
- **Request Body**:
  ```json
  {
    "rating": 5,
    "review_text": "Amazing game!"
  }
  ```
- **Response (Success)**:
  ```json
  {
    "success": true,
    "message": "Review created successfully",
    "review": {
      "id": 15,
      "username": "john_doe",
      "rating": 5,
      "review_text": "Amazing game!",
      "created_at": "2025-10-30 14:30:00"
    }
  }
  ```
- **Response (Error)**:
  ```json
  {
    "success": false,
    "error": "You have already reviewed this game. Use the edit endpoint to update your review."
  }
  ```

#### Update Review
**PUT** `/store/api/reviews/<review_id>/update/`
- **Authentication**: Required
- **Authorization**: Users can only update their own reviews
- **Request Body**:
  ```json
  {
    "rating": 4,
    "review_text": "Updated review text"
  }
  ```
- **Response (Success)**:
  ```json
  {
    "success": true,
    "message": "Review updated successfully",
    "review": {
      "id": 15,
      "rating": 4,
      "review_text": "Updated review text",
      "updated_at": "2025-10-30 15:00:00"
    }
  }
  ```

#### Delete Review
**DELETE** `/store/api/reviews/<review_id>/delete/`
- **Authentication**: Required
- **Authorization**: Users can only delete their own reviews
- **Response (Success)**:
  ```json
  {
    "success": true,
    "message": "Review for Game Title deleted successfully"
  }
  ```

#### Get Rating Statistics
**GET** `/store/api/reviews/<game_id>/stats/`
- **Authentication**: Not required
- **Response**:
  ```json
  {
    "success": true,
    "stats": {
      "average_rating": 4.5,
      "total_reviews": 10,
      "rating_breakdown": {
        "5": 6,
        "4": 2,
        "3": 1,
        "2": 1,
        "1": 0
      }
    }
  }
  ```


## Project Structure

```
gamevault_backend/
├── manage.py
├── create_admin.py
├── gamevault_backend/
│   ├── settings.py          # Simple Django settings
│   ├── urls.py              # Main URL configuration
│   ├── static/
│   │   └── css/
│   │       └── style.css    # Minimal CSS styling
│   └── templates/
│       ├── base.html        # Base template
│       ├── users/           # Authentication templates
│       └── store/           # Store templates
├── users/
│   ├── models.py            # User model
│   ├── views.py             # Simple auth views
│   ├── urls.py              # Auth URLs
│   └── admin.py             # Django admin config
└── store/
    ├── models.py            # Game, Cart, Transaction models
    ├── views.py             # All store functionality
    ├── urls.py              # Store URLs
    └── admin.py             # Django admin config
```

## Key Design Decisions in System Design

1. **Simplicity First**: 
2. **Function-Based Views**: All views are simple functions, no class-based views
3. **Session-Based Auth**: Standard Django sessions
4. **Minimal JavaScript**: Only essential client-side interactions
5. **No Frontend Framework**: Pure HTML, CSS, and JavaScript

## Development Workflow

1. Models are simple Django ORM classes
2. Views are straightforward functions that:
   - Get data from models
   - Process forms/requests
   - Render templates
3. Templates extend from `base.html`
4. URLs are mapped directly to view functions
5. Static files are served from `static/` directory

## Testing

To test the application:

1. Register a new user account
2. Browse games and add to cart
3. Complete checkout
4. View transaction history
5. Login as admin to manage games

## Switching to Supabase PostgreSQL

To use Supabase instead of SQLite:

1. Get your Supabase connection string from the Supabase dashboard
2. Update `.env` file:
   ```
   DATABASE_URL=postgresql://postgres.kdosumxcrhtvjrunnawe:[YOUR-PASSWORD]@aws-1-ap-southeast-1.pooler.supabase.com:5432/postgres
   ```
3. Run migrations again:
   ```bash
   python manage.py migrate
   python create_admin.py
   ```

## Security Notes

- Change `SECRET_KEY` in production
- Set `DEBUG=False` in production
- Use environment variables for sensitive data
- Add proper ALLOWED_HOSTS for production
- Implement proper file upload validation
- Add payment gateway for real transactions

## License

This project is for educational purposes.

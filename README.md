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
DATABASE_URL=postgresql://user:password@host:port/database
```

### 4. Run Migrations

```bash
cd gamevault_backend
python manage.py migrate
```

### 5. Create Admin User

```bash
python create_admin.py
```

Default credentials:
- Username: `admin`
- Password: `admin123`

### 6. Run Development Server

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

TBA

---

## Additional Project Details

## Database Schema

The application uses the following simple models:

### User
- user_id (Primary Key)
- username, email, password_hash
- registration_date
- is_admin (Boolean)

### Game
- game_id (Primary Key)
- title, description, category, price
- screenshot_url, file_url
- upload_date

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

### AdminActionLog
- log_id (Primary Key)
- admin_id (Foreign Key)
- action_type, target_game_id (Foreign Key)
- timestamp, notes



## Features

### Public Features
- Browse games (no login required)
- Search and filter games by category
- View game details

### User Features (requires login)
- Register and login
- Add games to shopping cart
- Update cart quantities
- Checkout and complete purchase
- View transaction history
- Download purchased games

### Admin Features (requires is_admin=True)
- Access admin dashboard
- Create, edit, and delete games
- View admin action logs
- View statistics

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

## Key Design Decisions

1. **Simplicity First**: No complex design patterns, decorators, or abstractions unless absolutely necessary
2. **Function-Based Views**: All views are simple functions, no class-based views
3. **Session-Based Auth**: Standard Django sessions, no JWT or token authentication
4. **Minimal JavaScript**: Only essential client-side interactions
5. **No Frontend Framework**: Pure HTML, CSS, and JavaScript
6. **Clear Comments**: Code is commented to explain purpose and logic

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
   DATABASE_URL=postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres
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

## Future Enhancements

- Add user profile editing
- Implement game reviews and ratings
- Add wishlist functionality
- Implement actual payment processing
- Add email notifications
- Improve admin dashboard with charts
- Add game categorization and tagging
- Implement search optimization

## License

This project is for educational purposes.

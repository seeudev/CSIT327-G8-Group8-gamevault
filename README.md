# GameVault

GameVault is a modern web application for purchasing and managing digital game keys. Built with Django (backend + templates), vanilla JavaScript (frontend interactivity), and PostgreSQL database (Supabase).

## 🎯 Project Overview

GameVault is structured in modular phases:
- **Module 1**: Authentication & Authorization ✅ **COMPLETE**
- **Module 2**: Admin Core (Game Management) ✅ **COMPLETE**
- **Module 3**: Storefront Core (Public Catalog) ✅ **COMPLETE**
- **Module 4**: Foundation & DevOps ⚠️ **PARTIAL** (Docs ✅, Deployment ❌)

---

## ✨ Implemented Modules

### Module 1: Authentication & Authorization ✅

**1.1 User Roles & Database Schema**
- Custom User model with role-based access control (Admin, Buyer, Moderator)
- Role model with JSON-based permissions
- Database seeding: `python manage.py seed_database` (creates admin/admin123)

**1.2 Registration & Login System**
- Session-based authentication with Django
- JWT API endpoints for programmatic access
- Login/registration forms with validation
- User profile management

### Module 2: Admin Core ✅

**2.1 Basic Admin Panel**
- Admin dashboard at `/admin/` with statistics
- Role-based access (admin-only)
- Navigation to game management, users, orders

**2.2 CRUD Operations for Games**
- Create, read, update, delete games
- Game model with: title, description, price, images, developer, publisher, genres, platforms
- Game key inventory management
- Bulk operations and statistics

### Module 3: Storefront Core ✅

**3.1 Public Game Library & Catalog**
- Public game listing at `/store/`
- Game cards with images, pricing, and details
- Search and filter by genre
- Sort by featured, price, rating, title

**3.2 Shopping Cart & Checkout**
- Add to cart functionality
- Cart management (view, adjust quantities, remove items)
- Checkout process (clears cart, shows confirmation)
- Cart persisted in localStorage

---

## 🛠️ Tech Stack

### Backend
- **Django 5.2.6** - Web framework with template engine
- **Django REST Framework 3.16.1** - REST API endpoints
- **Simple JWT 5.5.1** - JWT authentication for API
- **PostgreSQL** - Database (via Supabase)
- **Pillow 10.4.0** - Image processing
- **psycopg2-binary 2.9.10** - PostgreSQL adapter

### Frontend
- **Django Templates** - Server-side rendering
- **Vanilla JavaScript** - Client-side interactivity
- **CSS3** - Styling with custom properties
- **localStorage** - Client-side cart storage

### Why No React?
In a previous decision, we simplified the tech stack by removing React to reduce complexity. The application now uses Django's built-in template system with vanilla JavaScript for dynamic features, making it easier to develop and deploy as a single Django application.

---

## 📦 Quick Start

### Prerequisites
- Python 3.12+
- PostgreSQL database (or Supabase account)

### Setup & Run

1. **Clone the repository**
   ```bash
   git clone https://github.com/seeudev/gamevault.git
   cd gamevault
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv env
   # Windows
   .\env\Scripts\activate
   # macOS/Linux
   source env/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   
   Create a `.env` file in the project root:
   ```env
   DATABASE_URL=postgresql://user:password@host:port/database
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ```

5. **Navigate to backend and run migrations**
   ```bash
   cd gamevault_backend
   python manage.py migrate
   ```

6. **Seed the database**
   ```bash
   python manage.py seed_database
   ```
   
   This creates:
   - **Default Admin**: username `admin`, password `admin123`
   - **Default Roles**: Admin, Buyer, Moderator

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - **Home/Store**: http://localhost:8000/
   - **Login**: http://localhost:8000/login/
   - **Register**: http://localhost:8000/register/
   - **Admin Dashboard**: http://localhost:8000/admin/ (login as admin)
   - **Django Admin**: http://localhost:8000/django-admin/

---

## 🏗️ Project Structure

```
gamevault/
├── gamevault_backend/          # Django application
│   ├── manage.py
│   ├── gamevault_backend/      # Main project settings
│   │   ├── settings.py         # Configuration
│   │   ├── urls.py             # URL routing
│   │   ├── admin_urls.py       # Admin panel routes
│   │   ├── admin_views.py      # Admin panel views
│   │   ├── templates/          # Django templates
│   │   │   ├── base/           # Base templates
│   │   │   ├── auth/           # Login/register pages
│   │   │   ├── users/          # User pages
│   │   │   ├── store/          # Store pages
│   │   │   └── admin/          # Admin dashboard
│   │   └── static/             # Static files
│   │       ├── css/            # Stylesheets
│   │       ├── js/             # JavaScript files
│   │       └── images/         # Images
│   ├── users/                  # Users app
│   │   ├── models.py           # User & Role models
│   │   ├── serializers.py      # DRF serializers
│   │   ├── views.py            # Views & API endpoints
│   │   ├── urls.py             # URL routing
│   │   └── management/         # Management commands
│   │       └── commands/
│   │           └── seed_database.py
│   └── store/                  # Store app
│       ├── models.py           # Game, GameKey, Category models
│       ├── serializers.py      # DRF serializers
│       ├── views.py            # Views & API endpoints
│       └── urls.py             # URL routing
├── env/                        # Virtual environment
├── requirements.txt            # Python dependencies
├── README.md                   # This file
└── QUICKSTART.md              # Quick start guide
```

---

## � Key Features

### Authentication & User Management
- ✅ Role-based access control (Admin, Buyer, Moderator)
- ✅ Session-based authentication
- ✅ JWT API for programmatic access
- ✅ User registration and login
- ✅ Profile management with avatar uploads
- ✅ Password change functionality

### Admin Features
- ✅ Admin dashboard with statistics
- ✅ Full CRUD for games
- ✅ Game key inventory management
- ✅ Bulk operations
- ✅ User management
- ✅ Image uploads for game covers

### Storefront Features
- ✅ Public game catalog
- ✅ Search and filtering
- ✅ Shopping cart (localStorage)
- ✅ Checkout simulation
- ✅ Responsive design

---

## 📊 Database Schema

### Core Tables

**users**
- Custom user model with role relationship
- Profile fields: phone, date of birth, bio, avatar
- Authentication fields: email (unique), password (hashed)
- Audit fields: created_at, updated_at, last_login_ip

**roles**
- name, display_name, description
- permissions (JSON) - flexible permission system

**games**
- Game information: title, description, price, images
- Metadata: developer, publisher, release_date, genre
- Inventory: stock_quantity, total_sold
- SEO: slug, meta_description, featured
- Audit: created_by, updated_by, timestamps

**game_keys**
- Individual product keys for games
- Status: available, sold, reserved, invalid
- Tracking: sold_to, sold_at

**game_categories**
- Structured categorization
- Icon and color customization

---

## 🌐 API Endpoints

### Authentication (`/api/auth/`)
- `POST /register/` - Register new user
- `POST /login/` - Login user (returns JWT)
- `POST /logout/` - Logout user
- `GET /profile/` - Get current user profile
- `PATCH /profile/` - Update user profile
- `POST /change-password/` - Change password
- `POST /verify-token/` - Verify JWT token
- `GET /permissions/` - Get user permissions
- `GET /roles/` - List all roles

### Games - Admin (`/api/games/`)
- `GET /` - List all games (admin only)
- `POST /` - Create game (admin only)
- `GET /<slug>/` - Get game details (admin only)
- `PUT/PATCH /<slug>/` - Update game (admin only)
- `DELETE /<slug>/` - Delete game (admin only)

### Games - Public (`/api/public/games/`)
- `GET /` - List active games (public)
- `GET /<slug>/` - Get game details (public)

### Game Keys (`/api/games/<slug>/keys/`)
- `GET /` - List game keys (admin only)
- `POST /` - Create game key (admin only)
- `POST /bulk/` - Bulk create keys (admin only)

### Categories (`/api/categories/`)
- `GET /` - List categories (admin only)
- `POST /` - Create category (admin only)

---

## 🧪 Testing

### Manual Testing

1. **Register a new user**
   - Go to http://localhost:8000/register/
   - Fill in the form and submit

2. **Login as admin**
   - Go to http://localhost:8000/login/
   - Username: `admin`, Password: `admin123`
   - Access admin dashboard at http://localhost:8000/admin/

3. **Browse the store**
   - Go to http://localhost:8000/store/
   - Search and filter games
   - Add items to cart

### API Testing with cURL

**Register:**
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePass123",
    "password_confirm": "SecurePass123"
  }'
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

---

## 🔒 Security Features

- Password hashing with Django's PBKDF2 algorithm
- JWT tokens with rotation and blacklisting
- CSRF protection on forms
- SQL injection protection via Django ORM
- XSS protection via template escaping
- Role-based access control
- Secure session management

---

## 🐛 Troubleshooting

### Common Issues

**"No module named 'xyz'"**
```bash
# Activate virtual environment first
.\env\Scripts\activate  # Windows
source env/bin/activate  # macOS/Linux

# Then install dependencies
pip install -r requirements.txt
```

**Database connection errors**
- Check your `.env` file has correct `DATABASE_URL`
- Ensure PostgreSQL/Supabase is running
- Verify connection credentials

**Migration errors**
```bash
cd gamevault_backend
python manage.py migrate
```

**Static files not loading**
```bash
python manage.py collectstatic
```

---

## 🚀 Deployment (To-Do)

The application is currently configured for local development. For production deployment:

1. Set `DEBUG=False` in settings
2. Configure allowed hosts
3. Set up a production database
4. Configure static file serving
5. Use a production WSGI server (Gunicorn)
6. Set up HTTPS
7. Configure environment variables securely

Deployment platforms to consider:
- **Backend**: Railway, Heroku, PythonAnywhere, DigitalOcean
- **Database**: Supabase, ElephantSQL, Railway PostgreSQL

---

## 📝 Default Accounts

After running `python manage.py seed_database`:

**Admin Account**
- Username: `admin`
- Email: `admin@gamevault.com`
- Password: `admin123`
- Role: Administrator

⚠️ **Important**: Change the admin password after first login!

---

## � Development Team

**Group 8 - CSIT327 (Information Management 2)**
- Full-stack development
- Module 1-3 implementation
- Database design and implementation

---

## 📄 License

This project is part of a university assignment for CSIT327.

---

## 🙏 Acknowledgments

- Django Documentation
- Django REST Framework
- SimpleJWT Documentation
- PostgreSQL & Supabase

---

**Project Status**: Modules 1-3 Complete ✅ | Ready for Deployment 🚀
# GameVault

GameVault is a modern web application for purchasing and managing digital game keys. Built with a React frontend, Django REST backend, and PostgreSQL database (Supabase).

## 🎯 Project Overview

GameVault is structured in modular phases:
- **Module 1**: Authentication & Authorization ✅ (Completed)
- **Module 2**: Admin Core (Game Management)
- **Module 3**: Storefront Core (Public Catalog)
- **Module 4**: Foundation & DevOps (Deployment)

---

## ✨ Module 1: Authentication & Authorization (Completed)

### Features Implemented

#### 1.1 User Roles & Database Schema ✅
- **Custom User Model**: Extended Django's AbstractUser with additional fields
  - Email (unique, required)
  - Role (ForeignKey to Role model)
  - Phone number, date of birth, bio, avatar
  - Account verification status
  - Last login IP tracking
  - Timestamps (created_at, updated_at)

- **Role Model**: Flexible role-based access control
  - Built-in roles: Admin, Buyer, Moderator
  - JSON-based permissions system
  - Easy to extend with new roles

- **Database Seeding**
  - Management command: `python manage.py seed_database`
  - Creates default roles and admin user
  - Default admin credentials: `admin / admin123`

#### 1.2 Registration & Login System ✅
- **Backend API Endpoints**
  - `POST /api/auth/register/` - User registration
  - `POST /api/auth/login/` - User login
  - `POST /api/auth/logout/` - User logout with token blacklisting
  - `GET /api/auth/profile/` - Get current user profile
  - `PATCH /api/auth/profile/` - Update user profile
  - `POST /api/auth/change-password/` - Change password
  - `POST /api/auth/verify-token/` - Verify JWT token validity
  - `GET /api/auth/permissions/` - Get user permissions
  - `GET /api/auth/roles/` - List all roles

- **JWT Authentication**
  - Access token lifetime: 60 minutes
  - Refresh token lifetime: 7 days
  - Automatic token rotation and blacklisting
  - Secure token-based authentication

- **Frontend Components**
  - Login page with username/email support
  - Registration page with validation
  - Protected routes for authenticated users
  - Automatic token refresh on expiry
  - Auth context for global state management

---

## 🛠️ Tech Stack

### Backend
- **Django 5.2.6** - Web framework
- **Django REST Framework 3.16.1** - REST API
- **Simple JWT 5.5.1** - JWT authentication
- **PostgreSQL** - Database (Supabase)
- **Django CORS Headers** - CORS support
- **Pillow** - Image handling

### Frontend
- **React 18** - UI framework
- **React Router DOM** - Routing
- **Axios** - HTTP client
- **CSS3** - Styling

---

## 📦 Installation & Setup

### Prerequisites
- Python 3.12+
- Node.js 16+
- PostgreSQL database (or Supabase account)

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd gamevault_backend
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
   pip install -r ../requirements.txt
   ```

4. **Configure environment variables**
   Create a `.env` file in the project root:
   ```
   DATABASE_URL=postgresql://user:password@host:port/database
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Seed the database**
   ```bash
   python manage.py seed_database
   ```
   Default admin credentials:
   - Username: `admin`
   - Email: `admin@gamevault.com`
   - Password: `admin123`

7. **Run development server**
   ```bash
   python manage.py runserver
   ```
   Backend will run at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd gamevault_frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment variables**
   The `.env` file is already created:
   ```
   REACT_APP_API_URL=http://localhost:8000/api
   ```

4. **Run development server**
   ```bash
   npm start
   ```
   Frontend will run at `http://localhost:3000`

---

## 🎮 Usage

### Testing the Application

1. **Start Backend Server**
   ```bash
   cd gamevault_backend
   python manage.py runserver
   ```

2. **Start Frontend Server** (in another terminal)
   ```bash
   cd gamevault_frontend
   npm start
   ```

3. **Access the Application**
   - Open browser to `http://localhost:3000`
   - Register a new user or login with admin credentials
   - Explore the authenticated home page

### API Testing with cURL

**Register a new user:**
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
    "username": "testuser",
    "password": "SecurePass123"
  }'
```

**Get Profile (requires token):**
```bash
curl -X GET http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 📁 Project Structure

```
gamevault/
├── gamevault_backend/          # Django backend
│   ├── gamevault_backend/      # Project settings
│   │   ├── settings.py         # Django configuration
│   │   ├── urls.py             # Main URL routing
│   │   └── ...
│   ├── users/                  # Users app
│   │   ├── models.py           # User and Role models
│   │   ├── serializers.py      # DRF serializers
│   │   ├── views.py            # API views
│   │   ├── urls.py             # Users URL routing
│   │   ├── admin.py            # Admin configuration
│   │   └── management/         # Management commands
│   │       └── commands/
│   │           └── seed_database.py
│   ├── store/                  # Store app (for future modules)
│   └── manage.py
├── gamevault_frontend/         # React frontend
│   ├── public/
│   └── src/
│       ├── components/
│       │   ├── auth/           # Auth components
│       │   │   ├── Login.js
│       │   │   ├── Register.js
│       │   │   ├── ProtectedRoute.js
│       │   │   └── Auth.css
│       │   ├── Home.js         # Home page
│       │   └── Home.css
│       ├── contexts/
│       │   └── AuthContext.js  # Auth state management
│       ├── services/
│       │   └── api.js          # API client
│       ├── App.js              # Main app component
│       └── index.js
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

---

## 🔒 Security Features

- **Password Hashing**: Django's PBKDF2 algorithm
- **JWT Tokens**: Secure token-based authentication
- **Token Refresh**: Automatic token rotation
- **Token Blacklisting**: Logout invalidates tokens
- **CORS Protection**: Configured for localhost:3000
- **Password Validation**: Django's built-in validators
- **SQL Injection Protection**: Django ORM
- **XSS Protection**: React's built-in escaping

---

## 🧪 Database Schema

### Users Table
```sql
- id (Primary Key)
- username (Unique)
- email (Unique)
- password (Hashed)
- first_name
- last_name
- phone_number
- date_of_birth
- bio
- avatar
- role_id (Foreign Key -> Roles)
- is_verified
- is_active
- is_staff
- is_superuser
- created_at
- updated_at
- last_login
- last_login_ip
```

### Roles Table
```sql
- id (Primary Key)
- name (Unique)
- display_name
- description
- permissions (JSON)
- created_at
- updated_at
```

---

## 🚀 Next Steps (Upcoming Modules)

### Module 2: Admin Core
- [ ] Admin dashboard
- [ ] CRUD operations for games
- [ ] Game image uploads
- [ ] Admin-only routes

### Module 3: Storefront Core
- [ ] Public game catalog
- [ ] Shopping cart functionality
- [ ] Checkout process
- [ ] Order management

### Module 4: Foundation & DevOps
- [ ] Production deployment (Heroku/Railway)
- [ ] Frontend deployment (Vercel/Netlify)
- [ ] Environment configuration
- [ ] CI/CD pipeline

---

## 👥 Default User Accounts

After running `python manage.py seed_database`:

**Admin User**
- Username: `admin`
- Email: `admin@gamevault.com`
- Password: `admin123`
- Role: Administrator

**Note**: Change the admin password after first login!

---

## 📝 API Documentation

Full API documentation is available at `/api/docs/` when the backend server is running (in development mode).

Key endpoints:
- `/api/auth/register/` - Register new user
- `/api/auth/login/` - Login user
- `/api/auth/logout/` - Logout user
- `/api/auth/profile/` - Get/Update profile
- `/api/auth/token/refresh/` - Refresh access token

---

## 🐛 Troubleshooting

### Backend Issues

**ModuleNotFoundError: No module named 'xyz'**
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`

**Database connection error**
- Check `DATABASE_URL` in environment variables
- Ensure PostgreSQL/Supabase is running
- Verify connection credentials

**Migration errors**
- Delete migration files (keep `__init__.py`)
- Run `python manage.py makemigrations`
- Run `python manage.py migrate`

### Frontend Issues

**Module not found errors**
- Run `npm install` in gamevault_frontend directory
- Clear cache: `npm cache clean --force`

**CORS errors**
- Ensure backend CORS_ALLOWED_ORIGINS includes http://localhost:3000
- Check that backend server is running

**API connection failed**
- Verify REACT_APP_API_URL in .env file
- Ensure backend is running on correct port

---

## 📄 License

This project is part of a university assignment for CSIT327 (Information Management 2).

---

## 👨‍💻 Authors

**Group 8**
- System Design & Implementation
- Module 1: Authentication & Authorization

---

## 🙏 Acknowledgments

- Django Documentation
- React Documentation
- Django REST Framework
- Simple JWT

---

**Module 1 Status**: ✅ Complete and Fully Functional
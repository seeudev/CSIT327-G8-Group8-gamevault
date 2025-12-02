# GameVault Technical Documentation

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Technology Stack](#technology-stack)
3. [Database Schema](#database-schema)
4. [API Documentation](#api-documentation)
5. [Deployment Guide](#deployment-guide)
6. [Development Setup](#development-setup)
7. [Testing](#testing)
8. [Security](#security)

---

## System Architecture

### Overview
GameVault is a Django-based web application following a Model-View-Template (MVT) architecture with a simplicity-first philosophy.

### Architecture Principles
- **Function-based views only** - No class-based views
- **Session-based authentication** - Django's built-in sessions, no JWT
- **Vanilla JavaScript** - No React/Vue frameworks
- **Minimal dependencies** - Core Django with essential packages only

### Project Structure
```
gamevault_backend/
├── manage.py                      # Django CLI entry point
├── gamevault_backend/             # Main application
│   ├── settings.py                # Configuration
│   ├── urls.py                    # Root URL routing
│   ├── wsgi.py                    # WSGI application
│   ├── templates/                 # Base templates
│   │   ├── base.html              # Master template
│   │   ├── store/                 # Store templates
│   │   └── users/                 # Auth templates
│   └── static/                    # Static assets
│       ├── css/                   # Stylesheets
│       │   ├── style.css          # Core styles
│       │   ├── variables.css      # CSS custom properties
│       │   └── modules/           # Component CSS
│       ├── js/                    # JavaScript files
│       └── images/                # Static images
├── store/                         # Store application
│   ├── models.py                  # Data models
│   ├── views.py                   # View functions
│   ├── urls.py                    # Store URL routing
│   ├── serializers.py             # Data serialization
│   ├── email_service.py           # Email functionality
│   ├── middleware.py              # Custom middleware
│   └── promotion_views.py         # Promotion management
└── users/                         # User application
    ├── models.py                  # User models
    ├── views.py                   # Auth views
    ├── urls.py                    # Auth URL routing
    └── email_service.py           # Password reset emails
```

### Request Flow
```
Client Request
    ↓
Django URL Router (urls.py)
    ↓
View Function (views.py)
    ↓
Model Layer (models.py) ←→ Database
    ↓
Template Rendering (*.html)
    ↓
HTTP Response (HTML/JSON)
```

---

## Technology Stack

### Backend
- **Python**: 3.12
- **Django**: 5.2.6
- **Database**: PostgreSQL (production) / SQLite (development)
- **WSGI Server**: Gunicorn 23.0.0

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Custom properties, Grid, Flexbox
- **JavaScript**: ES6+ vanilla JavaScript
- **Chart.js**: 4.4.0 (analytics visualization)

### Dependencies
```txt
Django==5.2.6
psycopg2-binary==2.9.10
dj-database-url==3.0.1
gunicorn==23.0.0
Pillow==11.3.0
python-dotenv==1.0.0
```

### Development Tools
- **Version Control**: Git
- **Package Manager**: pip
- **Virtual Environment**: venv
- **Code Editor**: VS Code (recommended)

---

## Database Schema

### Dual Database Strategy
The application switches between SQLite (dev) and PostgreSQL (production) via `DATABASE_URL` environment variable.

**Configuration** (settings.py):
```python
if 'DATABASE_URL' in os.environ:
    # PostgreSQL (Supabase)
    DATABASES = {
        'default': dj_database_url.parse(os.environ['DATABASE_URL'])
    }
else:
    # SQLite (Development)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
```

### Core Models

#### Users App

**User Model** (extends AbstractUser):
```python
class User(AbstractUser):
    is_admin = models.BooleanField(default=False)  # Separate from is_staff
    
    # Inherited from AbstractUser:
    # username, email, password, first_name, last_name,
    # is_active, is_staff, is_superuser, date_joined, last_login
```

**PasswordResetToken**:
```python
class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
```

**LoginAttempt** (Module 12 - Security):
```python
class LoginAttempt(models.Model):
    username = models.CharField(max_length=150)
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)
    successful = models.BooleanField(default=False)
    
    # Methods: record_attempt(), is_locked_out(), clear_attempts()
```

#### Store App

**Category**:
```python
class Category(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
```

**Tag**:
```python
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
```

**Game**:
```python
class Game(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, null=True, blank=True, 
                                  on_delete=models.SET_NULL)
    tags = models.ManyToManyField(Tag, through='GameTag', 
                                   related_name='games')
    screenshot_url = models.URLField(max_length=500, blank=True)
    file_url = models.URLField(max_length=500, blank=True)
    release_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
```

**GameTag** (Junction table):
```python
class GameTag(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('game', 'tag')
```

**Cart**:
```python
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, 
                              choices=[('active', 'Active'),
                                      ('checked_out', 'Checked Out'),
                                      ('abandoned', 'Abandoned')])
```

**CartItem**:
```python
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, 
                             related_name='items')
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    price_at_addition = models.DecimalField(max_digits=10, 
                                             decimal_places=2)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('cart', 'game')
```

**Transaction**:
```python
class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20,
                                      choices=[('pending', 'Pending'),
                                              ('completed', 'Completed'),
                                              ('failed', 'Failed'),
                                              ('refunded', 'Refunded')])
```

**TransactionItem**:
```python
class TransactionItem(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE,
                                    related_name='items')
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    price_at_purchase = models.DecimalField(max_digits=10, 
                                             decimal_places=2)
    game_key = models.CharField(max_length=50, unique=True, 
                                 blank=True, null=True)
    key_sent_at = models.DateTimeField(null=True, blank=True)
    
    def generate_game_key(self):
        # Format: GAME-XXXX-XXXX-XXXX
        import secrets
        key = f"GAME-{secrets.token_hex(4)}-{secrets.token_hex(4)}-{secrets.token_hex(4)}"
        self.game_key = key.upper()
        self.save()
```

**Review** (Module 11):
```python
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, 
                             related_name='reviews')
    rating = models.SmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    review_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'game')
```

**Wishlist** (Module 10):
```python
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'game')
```

**Promotion** (Module 16):
```python
class Promotion(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    discount_type = models.CharField(max_length=20,
                                     choices=[('percentage', 'Percentage'),
                                             ('fixed', 'Fixed Amount')])
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    games = models.ManyToManyField(Game, blank=True, 
                                   related_name='promotions')
    categories = models.ManyToManyField(Category, blank=True,
                                        related_name='promotions')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def is_currently_active(self):
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date
    
    def calculate_discounted_price(self, original_price):
        if self.discount_type == 'percentage':
            discount = original_price * (self.discount_value / 100)
        else:
            discount = self.discount_value
        return max(original_price - discount, Decimal('0.00'))
```

**PromotionUsage**:
```python
class PromotionUsage(models.Model):
    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE,
                                  related_name='usages')
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    used_at = models.DateTimeField(auto_now_add=True)
```

### Relationships Diagram
```
User (1) ----< (many) Cart
Cart (1) ----< (many) CartItem >---- (1) Game
User (1) ----< (many) Transaction
Transaction (1) ----< (many) TransactionItem >---- (1) Game
User (1) ----< (many) Review >---- (1) Game
User (1) ----< (many) Wishlist >---- (1) Game
Category (1) ----< (many) Game
Game (many) ----< (many) Tag [through GameTag]
Promotion (many) ----< (many) Game
Promotion (many) ----< (many) Category
Promotion (1) ----< (many) PromotionUsage >---- (1) Transaction
```

---

## API Documentation

### Authentication
All API endpoints use session-based authentication. CSRF token required for POST/PUT/DELETE requests.

**CSRF Token Header**:
```javascript
headers: {
    'X-CSRFToken': getCookie('csrftoken')
}
```

### User Authentication API

#### Login
**Endpoint**: `POST /auth/login/`  
**Request Body**: Form data - username, password  
**Response**: Redirect to marketplace or JSON error

#### Register
**Endpoint**: `POST /auth/register/`  
**Request Body**: Form data - username, email, password1, password2  
**Response**: Redirect to marketplace or validation errors

#### Logout
**Endpoint**: `POST /auth/logout/`  
**Response**: Redirect to login page

#### Password Reset Request
**Endpoint**: `POST /auth/password-reset/request/`  
**Request Body**: `{"email": "user@example.com"}`  
**Response**: 
```json
{
    "success": true,
    "message": "Password reset link sent to your email"
}
```

#### Password Reset Confirm
**Endpoint**: `POST /auth/password-reset/confirm/<token>/`  
**Request Body**: `{"new_password": "newpass123"}`  
**Response**:
```json
{
    "success": true,
    "message": "Password successfully reset"
}
```

### Review API (Module 11)

#### Get Reviews for Game
**Endpoint**: `GET /store/api/reviews/<game_id>/`  
**Auth**: Public (no login required)  
**Response**:
```json
{
    "success": true,
    "data": {
        "reviews": [
            {
                "id": 1,
                "user": "john_doe",
                "rating": 5,
                "review_text": "Great game!",
                "created_at": "2025-12-01T10:00:00Z",
                "updated_at": "2025-12-01T10:00:00Z",
                "is_owner": false
            }
        ],
        "rating_stats": {
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
}
```

#### Create Review
**Endpoint**: `POST /store/api/reviews/<game_id>/create/`  
**Auth**: Required (must own game)  
**Request Body**:
```json
{
    "rating": 5,
    "review_text": "Excellent game!"
}
```
**Response**:
```json
{
    "success": true,
    "data": {
        "id": 1,
        "rating": 5,
        "review_text": "Excellent game!",
        "created_at": "2025-12-03T10:00:00Z"
    }
}
```

#### Update Review
**Endpoint**: `PUT /store/api/reviews/<review_id>/update/`  
**Auth**: Required (must be review owner)  
**Request Body**:
```json
{
    "rating": 4,
    "review_text": "Good game, updated review"
}
```

#### Delete Review
**Endpoint**: `DELETE /store/api/reviews/<review_id>/delete/`  
**Auth**: Required (must be review owner)  
**Response**:
```json
{
    "success": true,
    "message": "Review deleted successfully"
}
```

### Wishlist API (Module 10)

#### Get User Wishlist
**Endpoint**: `GET /store/api/wishlist/`  
**Auth**: Required  
**Response**:
```json
{
    "success": true,
    "data": [
        {
            "id": 1,
            "game": {
                "id": 5,
                "title": "Game Title",
                "price": "29.99",
                "screenshot_url": "..."
            },
            "added_at": "2025-12-01T10:00:00Z"
        }
    ]
}
```

#### Add to Wishlist
**Endpoint**: `POST /store/api/wishlist/`  
**Auth**: Required  
**Request Body**:
```json
{
    "game_id": 5
}
```
**Response**:
```json
{
    "success": true,
    "data": {
        "id": 1,
        "game_id": 5,
        "added_at": "2025-12-03T10:00:00Z"
    }
}
```

#### Remove from Wishlist
**Endpoint**: `DELETE /store/api/wishlist/<game_id>/`  
**Auth**: Required  
**Response**:
```json
{
    "success": true,
    "message": "Game removed from wishlist"
}
```

### Analytics API (Admin Only)

#### Get Overview Metrics
**Endpoint**: `GET /store/api/analytics/overview/?days=30`  
**Auth**: Admin required  
**Response**:
```json
{
    "success": true,
    "data": {
        "total_revenue": "15432.50",
        "total_orders": 89,
        "total_items_sold": 134,
        "avg_order_value": "173.40",
        "new_users": 25,
        "active_users": 67
    }
}
```

#### Get Sales Trend
**Endpoint**: `GET /store/api/analytics/sales-trend/?days=30&period=daily`  
**Auth**: Admin required  
**Query Params**: days, period (daily/weekly/monthly), category (optional)  
**Response**:
```json
{
    "success": true,
    "data": {
        "sales_trend": [
            {
                "period": "2025-12-01",
                "revenue": "1234.56",
                "orders": 12
            }
        ]
    }
}
```

#### Get Top Games
**Endpoint**: `GET /store/api/analytics/top-games/?days=30&limit=10`  
**Auth**: Admin required  
**Response**:
```json
{
    "success": true,
    "data": {
        "top_games": [
            {
                "game_id": 5,
                "title": "Game Title",
                "category": "Action",
                "price": "29.99",
                "quantity_sold": 45,
                "revenue": "1349.55",
                "avg_rating": 4.5
            }
        ]
    }
}
```

### User Management API (Admin Only)

#### List All Users
**Endpoint**: `GET /store/api/users/?search=john&role=user`  
**Auth**: Admin required  
**Response**:
```json
{
    "success": true,
    "users": [
        {
            "id": 1,
            "username": "john_doe",
            "email": "john@example.com",
            "is_admin": false,
            "is_active": true,
            "date_joined": "2025-01-01T00:00:00Z"
        }
    ],
    "total": 1
}
```

#### Grant Admin Privileges
**Endpoint**: `POST /store/api/users/<user_id>/grant-admin/`  
**Auth**: Admin required  
**Response**:
```json
{
    "success": true,
    "message": "Admin privileges granted to user 'john_doe'"
}
```

---

## Deployment Guide

### Prerequisites
- Python 3.12+
- PostgreSQL 14+ (production)
- Git
- Server with SSH access (Railway, Heroku, AWS, etc.)

### Environment Variables

Create `.env` file in project root:

```env
# Database (Production)
DATABASE_URL=postgresql://user:password@host:port/database

# Django
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Email (Optional - for production)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@gamevault.com

# Site URL (for emails)
SITE_URL=https://yourdomain.com
```

### Railway Deployment (Recommended)

**1. Prepare Project**

Create `Procfile` in project root:
```
web: gunicorn gamevault_backend.gamevault_backend.wsgi
```

Create `requirements.txt`:
```bash
pip freeze > requirements.txt
```

**2. Railway Setup**

1. Create account at railway.app
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Railway auto-detects Django app

**3. Configure Environment**

In Railway dashboard:
- Go to Variables tab
- Add all environment variables from `.env`
- Railway provides DATABASE_URL automatically if you add PostgreSQL

**4. Add PostgreSQL**

- Click "New" → "Database" → "Add PostgreSQL"
- Railway automatically sets DATABASE_URL

**5. Deploy**

```bash
# Push to GitHub
git add .
git commit -m "Prepare for deployment"
git push origin main

# Railway auto-deploys on push
```

**6. Run Migrations**

In Railway terminal:
```bash
python manage.py migrate
python manage.py collectstatic --noinput
python create_admin.py  # Create first admin user
```

### Manual Server Deployment

**1. Server Setup (Ubuntu/Debian)**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3.12 python3.12-venv python3-pip postgresql nginx -y

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y
```

**2. Create Database**

```bash
sudo -u postgres psql
CREATE DATABASE gamevault;
CREATE USER gamevaultuser WITH PASSWORD 'strongpassword';
ALTER ROLE gamevaultuser SET client_encoding TO 'utf8';
ALTER ROLE gamevaultuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE gamevaultuser SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE gamevault TO gamevaultuser;
\q
```

**3. Clone and Setup Project**

```bash
# Clone repository
git clone https://github.com/yourusername/gamevault.git
cd gamevault

# Create virtual environment
python3.12 -m venv env
source env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
nano .env
# (Add all variables from Environment Variables section)

# Run migrations
cd gamevault_backend
python manage.py migrate
python manage.py collectstatic --noinput

# Create admin user
python create_admin.py
```

**4. Configure Gunicorn**

Create `/etc/systemd/system/gunicorn.service`:

```ini
[Unit]
Description=Gunicorn daemon for GameVault
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/gamevault/gamevault_backend
Environment="PATH=/home/ubuntu/gamevault/env/bin"
ExecStart=/home/ubuntu/gamevault/env/bin/gunicorn \
          --workers 3 \
          --bind unix:/home/ubuntu/gamevault/gamevault.sock \
          gamevault_backend.wsgi:application

[Install]
WantedBy=multi-user.target
```

Start Gunicorn:
```bash
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
```

**5. Configure Nginx**

Create `/etc/nginx/sites-available/gamevault`:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias /home/ubuntu/gamevault/gamevault_backend/staticfiles/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/ubuntu/gamevault/gamevault.sock;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/gamevault /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

**6. Setup SSL (Optional but recommended)**

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### Post-Deployment Checklist

- [ ] Database migrations applied
- [ ] Static files collected
- [ ] Admin user created
- [ ] Environment variables set
- [ ] ALLOWED_HOSTS configured
- [ ] DEBUG=False in production
- [ ] SSL certificate installed
- [ ] Backup strategy implemented
- [ ] Monitoring setup (optional)
- [ ] Email configuration tested

---

## Development Setup

### Local Development Environment

**1. Clone Repository**

```bash
git clone https://github.com/yourusername/gamevault.git
cd gamevault
```

**2. Create Virtual Environment**

```bash
python3.12 -m venv env
source env/bin/activate  # Linux/Mac
# or
env\Scripts\activate  # Windows
```

**3. Install Dependencies**

```bash
pip install -r requirements.txt
```

**4. Setup Database (SQLite - Development)**

```bash
cd gamevault_backend
python manage.py migrate
```

**5. Create Admin User**

```bash
python create_admin.py
# Default credentials: admin / admin123
```

**6. (Optional) Seed Sample Data**

```bash
python create_sample_games.py
```

**7. Run Development Server**

```bash
python manage.py runserver
```

Visit: `http://localhost:8000`

### Development Workflow

**Branch Strategy**:
- `main`: Production-ready code
- `develop`: Development branch
- `feat/*`: Feature branches
- `fix/*`: Bug fix branches

**Making Changes**:

1. Create feature branch:
```bash
git checkout -b feat/module-name
```

2. Make changes and test locally

3. Commit changes:
```bash
git add .
git commit -m "feat: add feature description"
```

4. Push to remote:
```bash
git push origin feat/module-name
```

5. Create Pull Request on GitHub

### Database Management

**Create Migrations**:
```bash
python manage.py makemigrations
```

**Apply Migrations**:
```bash
python manage.py migrate
```

**Reset Database** (Development):
```bash
rm db.sqlite3
python manage.py migrate
python create_admin.py
```

**Reset Supabase** (Production):
```bash
python reset_supabase_db.py  # Interactive script
```

---

## Testing

### Unit Testing (3.1)

**Test Structure**:
```
store/tests.py
users/tests.py
```

**Run All Tests**:
```bash
python manage.py test
```

**Run Specific App Tests**:
```bash
python manage.py test store
python manage.py test users
```

**Test Coverage**:
```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report
```

### Manual Testing Scripts

**Test Profile API** (Module 4):
```bash
python test_profile_api.py
```

**Test Password Reset** (Module 9):
```bash
python test_password_reset.py
```

**Test Login Security** (Module 12):
```bash
python test_login_security.py
```

**Test Analytics** (Module 15):
```bash
python test_analytics.py
python test_analytics_performance.py
```

### Performance Testing (3.2)

**Load Testing with Apache Bench**:

```bash
# Install Apache Bench
sudo apt install apache2-utils

# Test homepage
ab -n 1000 -c 10 http://localhost:8000/

# Test with authentication
ab -n 1000 -c 10 -C "sessionid=yoursessionid" http://localhost:8000/store/games/
```

**Performance Benchmarks**:
- Homepage: < 100ms response time
- Game list: < 200ms response time
- Checkout: < 300ms response time
- Analytics API: < 200ms response time

**Database Query Optimization**:

```python
# Use select_related for ForeignKey
games = Game.objects.select_related('category').all()

# Use prefetch_related for ManyToMany
games = Game.objects.prefetch_related('tags').all()

# Avoid N+1 queries
transactions = Transaction.objects.prefetch_related('items__game').all()
```

### Security Testing (3.3)

**Authentication Tests**:
- [ ] Test login with valid credentials
- [ ] Test login with invalid credentials
- [ ] Test 4-attempt lockout mechanism
- [ ] Test session expiration
- [ ] Test logout functionality
- [ ] Test password reset flow
- [ ] Test CSRF protection on forms

**Authorization Tests**:
- [ ] Test admin-only page access (non-admin users blocked)
- [ ] Test user can only view own transactions
- [ ] Test user can only edit/delete own reviews
- [ ] Test user cannot access other users' game keys

**Input Validation**:
- [ ] Test XSS prevention (sanitized output)
- [ ] Test SQL injection prevention (ORM queries)
- [ ] Test file upload validation
- [ ] Test price manipulation prevention

**Security Checklist**:
```bash
# Check for security issues
python manage.py check --deploy

# Update dependencies
pip list --outdated
pip install --upgrade package-name
```

---

## Security

### Authentication & Authorization

**Session Security**:
- Session cookies are HTTP-only
- CSRF tokens required for state-changing operations
- Session timeout: 2 weeks of inactivity

**Password Security**:
- Django's PBKDF2 password hashing
- Minimum 8 characters
- Password validators enforce complexity

**Login Protection** (Module 12):
- 4 failed attempts trigger 15-minute lockout
- IP address logging for audit
- Username-based locking (not IP-based)

### CSRF Protection

**Template Usage**:
```html
<form method="post">
    {% csrf_token %}
    <!-- form fields -->
</form>
```

**JavaScript AJAX**:
```javascript
fetch(url, {
    method: 'POST',
    headers: {
        'X-CSRFToken': getCookie('csrftoken'),
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
});
```

### SQL Injection Prevention

**Use Django ORM** (parameterized queries):
```python
# ✅ SAFE
games = Game.objects.filter(title__icontains=search_query)

# ❌ NEVER DO THIS
games = Game.objects.raw(f"SELECT * FROM games WHERE title LIKE '%{search_query}%'")
```

### XSS Prevention

**Template Auto-escaping**:
```html
<!-- ✅ Auto-escaped by default -->
<p>{{ user_input }}</p>

<!-- ⚠️ Only use |safe for trusted content -->
<p>{{ admin_html|safe }}</p>
```

**JavaScript**:
```javascript
// ✅ Escape user input
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
```

### Secure Configuration

**settings.py** (Production):
```python
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

### Data Protection

**Sensitive Data**:
- Passwords: Hashed with PBKDF2
- Game keys: Unique, cryptographically secure
- Email: Stored in plaintext (required for communication)

**Backup Strategy**:
```bash
# Database backup (PostgreSQL)
pg_dump -U gamevaultuser gamevault > backup_$(date +%Y%m%d).sql

# Restore
psql -U gamevaultuser gamevault < backup_20251203.sql
```

---

## Troubleshooting

### Common Development Issues

**Issue**: Migrations conflict
```bash
# Solution: Reset migrations (development only)
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete
python manage.py makemigrations
python manage.py migrate
```

**Issue**: Static files not loading
```bash
# Solution: Collect static files
python manage.py collectstatic --clear --noinput
```

**Issue**: Port 8000 already in use
```bash
# Solution: Kill process
lsof -ti:8000 | xargs kill -9
# Or use different port
python manage.py runserver 8080
```

### Production Issues

**Issue**: 500 Internal Server Error
```bash
# Check logs
sudo tail -f /var/log/nginx/error.log
sudo journalctl -u gunicorn -f

# Enable debug temporarily
DEBUG=True python manage.py runserver
```

**Issue**: Database connection refused
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Test connection
psql -U gamevaultuser -d gamevault -h localhost
```

---

## Performance Optimization

### Database Optimization

1. **Indexes**: Add indexes to frequently queried fields
```python
class Game(models.Model):
    title = models.CharField(max_length=200, db_index=True)
```

2. **Query Optimization**: Use select_related and prefetch_related
3. **Connection Pooling**: Configure in DATABASE settings

### Caching Strategy

**Install Redis** (optional):
```bash
pip install django-redis
```

**Configure** (settings.py):
```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

**Usage**:
```python
from django.core.cache import cache

# Cache for 5 minutes
cache.set('key', value, 300)
result = cache.get('key')
```

### Static Files Optimization

1. **Minify CSS/JS** in production
2. **Use CDN** for Chart.js and other libraries
3. **Enable Gzip** in Nginx configuration
4. **Lazy load images**

---

## Appendix

### Useful Commands

**Django Management**:
```bash
python manage.py shell          # Interactive Python shell
python manage.py dbshell         # Database shell
python manage.py createsuperuser # Create superuser
python manage.py showmigrations  # Show migration status
python manage.py sqlmigrate store 0001  # Show SQL for migration
```

**Git Commands**:
```bash
git status                       # Check status
git log --oneline --graph        # View commit history
git branch -a                    # List all branches
git stash                        # Temporarily save changes
git stash pop                    # Restore stashed changes
```

### Resources

- **Django Documentation**: https://docs.djangoproject.com/
- **PostgreSQL Documentation**: https://www.postgresql.org/docs/
- **Chart.js Documentation**: https://www.chartjs.org/docs/
- **Gunicorn Documentation**: https://docs.gunicorn.org/
- **Nginx Documentation**: https://nginx.org/en/docs/

---

**Document Version**: 1.0  
**Last Updated**: December 3, 2025  
**GameVault Development Team**

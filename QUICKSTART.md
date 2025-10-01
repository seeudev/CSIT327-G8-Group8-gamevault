# 🚀 Quick Start Guide - GameVault Module 1

This guide will get you up and running with GameVault's authentication system in under 5 minutes.

## ⚡ Quick Setup (Already Configured)

The project has been fully configured with:
- ✅ Django backend with custom User model
- ✅ Role-based access control (Admin, Buyer, Moderator)
- ✅ JWT authentication with token refresh
- ✅ React frontend with login/register pages
- ✅ Database migrations ready to apply
- ✅ Seeding script for default admin user

## 📋 Prerequisites Check

Make sure you have:
- [x] Python 3.12+ installed
- [x] Node.js 16+ installed
- [x] Virtual environment created and activated
- [x] Dependencies installed

## 🎯 Running the Application

### Step 1: Start the Backend (Terminal 1)

```bash
# Navigate to backend directory
cd gamevault_backend

# Use the virtual environment (adjust path based on your system)
# Windows (if using the project's venv):
& 'C:\Users\harry\Documents\UNI 2\S1Y3\CSIT327 G8\gamevault\env\Scripts\python.exe' manage.py runserver

# macOS/Linux:
python manage.py runserver
```

**Expected output:**
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

### Step 2: Start the Frontend (Terminal 2)

```bash
# Navigate to frontend directory
cd gamevault_frontend

# Start development server
npm start
```

**Expected output:**
```
Compiled successfully!
You can now view gamevault_frontend in the browser.
  Local:            http://localhost:3000
```

## 🧪 Testing the Application

### Option 1: Using the Web Interface

1. **Open your browser** to `http://localhost:3000`

2. **Test Registration:**
   - Click "Sign up" link
   - Fill in the registration form:
     ```
     Username: testuser
     Email: test@gamevault.com
     Password: Test1234
     Confirm Password: Test1234
     ```
   - Click "Create Account"
   - You should be logged in and redirected to the home page

3. **Test Login with Admin:**
   - Click "Logout"
   - Click "Sign in"
   - Enter admin credentials:
     ```
     Username: admin
     Password: admin123
     ```
   - You should see the home page with admin role

### Option 2: Using API Calls

**Register a new user:**
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "apiuser",
    "email": "api@gamevault.com",
    "password": "ApiPass123",
    "password_confirm": "ApiPass123"
  }'
```

**Expected response:**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 2,
    "username": "apiuser",
    "email": "api@gamevault.com",
    ...
  },
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
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

**Get user profile (replace TOKEN with access token from login):**
```bash
curl -X GET http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Bearer TOKEN"
```

## 🔍 What to Look For

### On the Home Page (After Login)
You should see:
- ✓ Welcome message
- ✓ User profile information
- ✓ Username, email, role, and verification status
- ✓ Module 1 completion status
- ✓ Feature cards showing implemented functionality
- ✓ Logout button

### Features to Test
1. **Registration**
   - Username validation (unique)
   - Email validation (unique, valid format)
   - Password strength (min 8 characters)
   - Password confirmation matching

2. **Login**
   - Username OR email login support
   - Invalid credentials error handling
   - Automatic redirect after login

3. **Protected Routes**
   - Try accessing `http://localhost:3000/` without logging in
   - Should redirect to login page

4. **JWT Token Management**
   - Tokens stored in localStorage
   - Automatic token refresh (test by waiting 60 minutes)
   - Token invalidation on logout

5. **Role-Based Access**
   - Admin user has `is_admin = true`
   - Regular users have `is_buyer = true`
   - Roles displayed correctly in UI

## 🎨 UI Features

### Login Page
- Modern gradient background
- Clean white card design
- Password visibility toggle (eye icon)
- Form validation and error messages
- "Sign up" link to registration

### Registration Page
- Two-column layout for name fields
- Real-time validation
- Password strength requirements
- Matching password confirmation
- "Sign in" link to login

### Home Page
- User profile card with all details
- Role badge (Admin/Buyer)
- Verification status badge
- Feature showcase grid
- Next steps information

## 🐛 Common Issues

**Issue: Backend won't start**
- Solution: Make sure virtual environment is activated and dependencies are installed
- Check: `pip list` should show Django, djangorestframework, etc.

**Issue: Frontend won't start**
- Solution: Delete `node_modules` and run `npm install` again
- Check: Node version with `node -v` (should be 16+)

**Issue: CORS errors in browser console**
- Solution: Ensure backend is running and CORS is configured for localhost:3000
- Check: `gamevault_backend/gamevault_backend/settings.py` CORS_ALLOWED_ORIGINS

**Issue: Database errors**
- Solution: Run migrations again
  ```bash
  python manage.py migrate
  python manage.py seed_database
  ```

**Issue: Can't login with admin credentials**
- Solution: Re-run the seeding command
  ```bash
  python manage.py seed_database
  ```

## 📊 Database Info

The database has been seeded with:

**Roles:**
1. Administrator - Full system access
2. Buyer - Standard user access
3. Moderator - Limited admin access

**Default Admin User:**
- Username: `admin`
- Email: `admin@gamevault.com`
- Password: `admin123`
- Role: Administrator

**⚠️ IMPORTANT:** Change the admin password after first login!

## 🎯 Key Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register/` | Register new user | No |
| POST | `/api/auth/login/` | User login | No |
| POST | `/api/auth/logout/` | User logout | Yes |
| GET | `/api/auth/profile/` | Get user profile | Yes |
| PATCH | `/api/auth/profile/` | Update profile | Yes |
| POST | `/api/auth/change-password/` | Change password | Yes |
| GET | `/api/auth/permissions/` | Get user permissions | Yes |
| GET | `/api/auth/roles/` | List all roles | Yes |
| POST | `/api/auth/token/refresh/` | Refresh access token | No |

## ✅ Module 1 Checklist

- [x] Custom User model with role field
- [x] Role model with permissions
- [x] User registration endpoint
- [x] User login endpoint
- [x] JWT authentication with refresh
- [x] Token blacklisting on logout
- [x] User profile management
- [x] Password change functionality
- [x] Admin user seeded in database
- [x] React login component
- [x] React registration component
- [x] Protected routes
- [x] Auth context provider
- [x] API service with interceptors
- [x] Automatic token refresh
- [x] Beautiful responsive UI

## 🎉 You're All Set!

Module 1: Authentication & Authorization is fully implemented and ready to use!

Next modules will build on this foundation:
- Module 2: Admin game management
- Module 3: Public storefront
- Module 4: Production deployment

Happy coding! 🚀

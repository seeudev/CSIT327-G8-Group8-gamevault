# GameVault User Manual

## Table of Contents
1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [User Features](#user-features)
4. [Admin Features](#admin-features)
5. [Troubleshooting](#troubleshooting)

---

## Introduction

Welcome to **GameVault** - your digital game store for instant game key delivery. GameVault allows you to browse, purchase, and manage your game library with secure transactions and immediate access to your game keys.

### Key Features
- 🎮 Browse extensive game catalog with categories and tags
- 🔍 Advanced search and filtering
- 🛒 Shopping cart with promotional pricing
- 💳 Secure checkout process
- 🔑 Instant game key delivery
- ⭐ Rate and review games
- ❤️ Wishlist management
- 📊 Purchase history tracking

---

## Getting Started

### Creating an Account

1. **Navigate to Registration**
   - Click the **"Register"** button in the top-right corner of the homepage
   - Or visit: `http://localhost:8000/auth/register/`

2. **Fill in Your Details**
   - **Username**: Choose a unique username (3-150 characters)
   - **Email**: Enter a valid email address
   - **Password**: Create a strong password (minimum 8 characters)
   - **Confirm Password**: Re-enter your password

3. **Submit Registration**
   - Click the **"Register"** button
   - You'll be automatically logged in and redirected to the marketplace

### Logging In

1. Click **"Login"** in the top navigation bar
2. Enter your username and password
3. Click **"Login"** button

**Security Note**: After 4 failed login attempts, your account will be locked for 15 minutes to prevent unauthorized access.

### Resetting Your Password

1. Click **"Forgot Password?"** on the login page
2. Enter your registered email address
3. Check your email for the password reset link
4. Click the link and enter your new password
5. Submit to update your password

---

## User Features

### 1. Browsing Games

#### Marketplace Homepage
- Access via: `http://localhost:8000/store/games/`
- View all available games in a card grid layout
- Each card displays:
  - Game screenshot/thumbnail
  - Category badge (top-left)
  - Discount badge (bottom-left, if applicable)
  - Game title and description
  - Price (discounted price shown if promotion active)
  - "Add to Cart" button
  - Wishlist heart icon (top-right)

#### Search Functionality
1. Use the **search bar** at the top of the marketplace
2. Type game title or keywords
3. Press **Enter** or click **"Search"**
4. Results update automatically

#### Filtering Games

**By Category:**
- Select a category from the dropdown menu
- Options include: Action, Adventure, RPG, Strategy, Simulation, Sports, Racing, Puzzle, etc.

**By Price Range:**
- Enter minimum price in "Min" field
- Enter maximum price in "Max" field
- Click **"Apply Filters"**

**By Tags:**
- Click the **"Select tags..."** dropdown
- Check multiple tags (e.g., Multiplayer, Single Player, Co-op)
- Click **"Apply Filters"**

**Sorting Options:**
- Relevance (default)
- Price: Low to High
- Price: High to Low
- Newest First
- Oldest First

**Clear Filters:**
- Click **"Clear All"** to reset all filters

### 2. Game Details

Click on any game card to view detailed information:

#### Game Detail Page Components

**Hero Section:**
- Large game screenshot with blurred background
- Game title and category
- Price information with promotional pricing (if applicable)
- "Add to Cart" button
- Download button (if you own the game)

**About Section:**
- Full game description
- System requirements
- Release date
- Developer information

**Reviews Section:**
- Average rating (stars out of 5)
- Total number of reviews
- Individual user reviews with ratings
- Option to write/edit your own review (if you own the game)

### 3. Wishlist Management

**Adding to Wishlist:**
1. Click the **heart icon** on any game card
2. Heart fills with red color when added
3. Success message appears

**Removing from Wishlist:**
1. Click the **filled heart icon** on a wishlisted game
2. Heart becomes outline only
3. Confirmation message appears

**Viewing Your Wishlist:**
1. Click **"Wishlist"** in the navigation bar
2. View all your saved games
3. Add games directly to cart from wishlist
4. Remove games by clicking the heart icon

### 4. Shopping Cart

**Adding Items:**
- Click **"Add to Cart"** on any game card or detail page
- Item is added instantly
- Cart icon shows item count

**Viewing Cart:**
1. Click **"Cart"** in the navigation bar
2. See all added games with:
   - Game thumbnail and title
   - Price per item (with discount if applicable)
   - Remove button

**Cart Features:**
- **Total Savings Banner**: Shows total amount saved from promotions
- **Subtotal**: Displays total cost after discounts
- **Remove Items**: Click "Remove" button next to any game

**Proceeding to Checkout:**
- Click **"Proceed to Checkout"** button at bottom of cart
- Review your order
- Click **"Complete Purchase"** to finalize

### 5. Purchase History

**Accessing Transaction History:**
1. Click **"Transactions"** in the navigation menu
2. View all your past orders

**Transaction History Features:**

**Summary Statistics:**
- Total games purchased
- Total number of orders
- Total amount spent

**Filters:**
- **Search**: Find transactions by game title
- **Status Filter**: All, Completed, Pending, Failed, Refunded
- **Date Range**: Filter by start and end date
- **Sort Options**: Date (newest/oldest), Amount (highest/lowest)

**Transaction Cards Display:**
- Order ID
- Transaction date
- Number of items
- Total amount
- Payment status badge
- "View Details" button

### 6. Transaction Details

Click **"View Details"** on any transaction to see:

**Order Information:**
- Order ID
- Transaction date
- Payment status
- Total amount

**Purchased Games:**
For each game:
- Game title and category
- Price at purchase
- **Game Key** (unique activation code)
- **Copy Key** button (copies to clipboard)
- **Email Key** button (sends key to your email)
- **Download Game** button (if file available)

**Managing Game Keys:**
1. **Copy to Clipboard**: Click "Copy Key" to copy the activation code
2. **Email Delivery**: Click "Send Game Key" to receive via email
3. **Download**: Click "Download Game" if downloadable content is available

### 7. Rating and Reviewing Games

**Writing a Review** (requires game ownership):

1. Navigate to the game's detail page
2. Scroll to the **Reviews** section
3. Click on the star rating (1-5 stars)
4. Optionally, add written feedback in the text area
5. Click **"Submit Review"**

**Editing Your Review:**
1. Find your review in the Reviews section
2. Click **"Edit"** button
3. Modify rating and/or text
4. Click **"Save"**

**Deleting Your Review:**
1. Click **"Delete"** on your review
2. Confirm deletion
3. Review is permanently removed

**Review Guidelines:**
- ⭐ 1 star = Poor
- ⭐⭐ 2 stars = Fair
- ⭐⭐⭐ 3 stars = Good
- ⭐⭐⭐⭐ 4 stars = Great
- ⭐⭐⭐⭐⭐ 5 stars = Excellent

### 8. User Profile

**Viewing Profile:**
1. Click on your username in the top-right corner
2. Select **"Profile"** from dropdown

**Profile Information:**
- Username
- Email address
- Registration date
- Total purchases
- Account status

---

## Admin Features

### Accessing Admin Dashboard

**Requirements:**
- Admin privileges (`is_admin = True`)
- Login with admin credentials

**Access:**
- Click **"Admin Dashboard"** in the navigation bar (red badge)
- Or visit: `http://localhost:8000/store/admin/dashboard/`

### 1. Admin Dashboard Overview

**Key Metrics Cards:**
- Total Revenue
- Total Orders
- Active Users
- Total Games in Catalog

**Quick Actions:**
- Manage Games
- Manage Promotions
- View Users
- View Transactions
- Analytics Dashboard

**Recent Activity:**
- Recent transactions
- Recent admin actions log
- Quick download reports

### 2. Game Management

**Accessing Game Management:**
- Click **"Manage Games"** from admin dashboard
- Or visit: `http://localhost:8000/store/admin/games/`

**Game List Features:**
- Search games by title
- Filter by category
- View all game details in table format

**Adding a New Game:**

1. Click **"Add New Game"** button
2. Fill in the form:
   - **Title**: Game name (required)
   - **Description**: Detailed description
   - **Price**: Decimal format (e.g., 29.99)
   - **Category**: Select from dropdown
   - **Tags**: Select multiple tags
   - **Screenshot URL**: Link to game image
   - **File URL**: Link to downloadable content (optional)
   - **Release Date**: Game release date
3. Click **"Create Game"**

**Editing a Game:**

1. Find the game in the list
2. Click **"Edit"** button
3. Modify any field
4. Click **"Update Game"**

**Deleting a Game:**

1. Click **"Delete"** next to the game
2. Confirm deletion
3. Game is permanently removed

### 3. Promotion Management

**Accessing Promotions:**
- Click **"Manage Promotions"** from admin dashboard
- Or visit: `http://localhost:8000/store/admin/promotions/`

**Creating a Promotion:**

1. Click **"Create New Promotion"**
2. Fill in promotion details:
   - **Name**: Promotion title (e.g., "Spring Sale")
   - **Description**: Optional details
   - **Discount Type**: Percentage or Fixed Amount
   - **Discount Value**: 
     - Percentage: 1-100 (e.g., 25 for 25% off)
     - Fixed: Dollar amount (e.g., 5.00 for $5 off)
   - **Start Date**: When promotion begins
   - **End Date**: When promotion expires
   - **Applicable Games**: Select specific games
   - **Applicable Categories**: Or select entire categories
   - **Active Status**: Toggle on/off manually
3. Click **"Create Promotion"**

**Promotion Features:**
- **Automatic Activation**: Promotions activate/expire based on dates
- **Manual Toggle**: Override with active/inactive status
- **Multiple Games**: Apply to specific games or entire categories
- **Best Price**: System automatically applies the best discount if multiple promotions overlap

**Viewing Promotion Performance:**

1. Click **"View"** on any promotion
2. See performance metrics:
   - Total Revenue Generated
   - Total Uses
   - Customer Savings
   - Daily Usage Trend (chart)
   - Top Games (table)

**Editing Promotions:**
1. Click **"Edit"** on promotion
2. Modify any field
3. Click **"Update Promotion"**

**Deactivating/Activating:**
- Click **"Deactivate"** or **"Activate"** toggle button
- Status updates immediately

**Exporting Reports:**
- Click **"Download CSV Report"** on promotion detail page
- CSV includes all usage details with dates, users, and amounts

### 4. User Management

**Accessing User Management:**
- Click **"View Users"** from admin dashboard
- Or visit: `http://localhost:8000/store/admin/users/`

**User List Features:**
- **Search**: Find users by username or email
- **Filter**: All Users, Admins Only, Regular Users Only
- **User Table**: Shows username, email, admin status, active status, registration date

**Granting Admin Privileges:**

1. Find the user in the list
2. Click **"Grant Admin"** button (appears for non-admin users only)
3. Confirm the action in dialog
4. User immediately gains admin access

**Note**: Admin actions are logged in the AdminActionLog for audit purposes.

### 5. Analytics Dashboard

**Accessing Analytics:**
- Click **"Analytics Dashboard"** from admin dashboard
- Or visit: `http://localhost:8000/store/admin/analytics/`

**Key Metrics Cards:**
- **Total Revenue**: Sum of all completed transactions
- **Total Orders**: Number of transactions
- **Items Sold**: Total game keys sold
- **Active Users**: Users who made purchases
- **New Users**: Recently registered users
- **Average Order Value**: Revenue divided by orders

**Sales Trend Chart:**
- Line chart showing revenue and orders over time
- Supports daily, weekly, and monthly aggregation
- Dual Y-axis for revenue ($) and orders count
- Interactive tooltips on hover

**Category Performance Chart:**
- Doughnut chart showing revenue distribution by category
- Percentage breakdown
- Color-coded categories
- Interactive legend

**Top Games Table:**
- Ranked by quantity sold
- Shows: Game title, category, price, quantity, revenue, avg rating
- Sortable columns
- Responsive design

**Filters:**
- **Date Range**: 7, 30, 90, 180, 365 days
- **Category Filter**: Select specific category or all
- **Chart Period**: Daily, weekly, or monthly data points
- **Apply/Refresh**: Manual filter application

**Exporting Data:**

1. **Sales CSV**: Download all transaction details
2. **Games CSV**: Download game performance data
3. **Users CSV**: Download user statistics
4. **Overview JSON**: Download complete analytics snapshot

Click any export button to download the file immediately.

### 6. Transaction Management

**Viewing All Transactions:**
- Click **"View Transactions"** from admin dashboard

**Transaction Filters:**
- Filter by status (completed, pending, failed, refunded)
- Search by user or game
- Date range selection

**Transaction Actions:**
- View detailed transaction information
- Resend game keys via email
- Check payment status
- View associated user

---

## Troubleshooting

### Common Issues

#### 1. Cannot Login

**Symptoms**: "Invalid username or password" error

**Solutions:**
- Verify username and password are correct (case-sensitive)
- Check if account is locked (wait 15 minutes after 4 failed attempts)
- Use "Forgot Password?" to reset your password
- Ensure account exists (register if new user)

#### 2. Game Key Not Received

**Symptoms**: Game key not visible after purchase

**Solutions:**
1. Check your transaction detail page
2. Game key should be displayed under each purchased game
3. Click **"Send Game Key"** to receive via email
4. Check spam/junk folder for email
5. Contact admin if issue persists

#### 3. Cart Items Disappear

**Symptoms**: Items removed from cart unexpectedly

**Solutions:**
- Cart is session-based; logging out clears cart
- Items remain while logged in
- Complete checkout to save purchases permanently

#### 4. Promotions Not Applying

**Symptoms**: Discounted price not showing

**Solutions:**
- Check if promotion is currently active (date range)
- Verify game or category is included in promotion
- Refresh the page
- Clear browser cache
- Multiple promotions: system applies best discount automatically

#### 5. Cannot Add Review

**Symptoms**: Review form not visible or submit fails

**Solutions:**
- Must own the game to leave a review (purchase required)
- Can only submit one review per game
- Login required to write reviews
- Check for error messages on form submission

#### 6. Wishlist Not Saving

**Symptoms**: Heart icon doesn't stay active

**Solutions:**
- Must be logged in to use wishlist
- Check browser console for JavaScript errors
- Ensure cookies are enabled
- Refresh page to sync wishlist state

#### 7. Search Returns No Results

**Symptoms**: Search shows "No games found"

**Solutions:**
- Check spelling of search terms
- Try broader search keywords
- Clear all filters
- Verify games exist in database
- Try different filter combinations

#### 8. Payment Status Shows Pending

**Symptoms**: Transaction status stuck on "Pending"

**Solutions:**
- Module 13 auto-completes transactions (development mode)
- Contact admin to update payment status
- Check transaction detail page for game keys (available even if pending)

#### 9. Admin Dashboard Not Accessible

**Symptoms**: 403 Forbidden or redirect to home

**Solutions:**
- Verify admin privileges with system administrator
- Regular users cannot access admin features
- Contact admin to grant admin privileges via user management

#### 10. Analytics Charts Not Loading

**Symptoms**: Charts show loading spinner indefinitely

**Solutions:**
- Check browser console for JavaScript errors
- Ensure Chart.js library is loaded
- Verify API endpoints are responding (F12 > Network tab)
- Clear browser cache
- Try different date range filter

### Error Messages

#### "This field is required"
- Fill in all required form fields marked with *
- Check for empty inputs before submitting

#### "User with this username already exists"
- Choose a different unique username during registration

#### "Password too common" / "Password too short"
- Use stronger password (min 8 characters, mix of letters/numbers/symbols)

#### "Invalid token" (Password Reset)
- Token expired (valid for 1 hour)
- Request new password reset link
- Use the link immediately after receiving

#### "You do not have permission to access this page"
- Attempting to access admin-only feature without privileges
- Login with correct account type

### Browser Compatibility

**Supported Browsers:**
- ✅ Chrome (latest)
- ✅ Firefox (latest)
- ✅ Safari (latest)
- ✅ Edge (latest)
- ✅ Mobile Safari (iOS 14+)
- ✅ Chrome Mobile (Android 10+)

**Recommended:**
- Use latest browser version for best experience
- Enable JavaScript (required)
- Allow cookies (required for sessions)

### Performance Tips

1. **Slow Page Load:**
   - Clear browser cache
   - Check internet connection
   - Disable unnecessary browser extensions
   - Use Chrome DevTools to identify bottlenecks

2. **Search/Filter Lag:**
   - Try more specific search terms
   - Use fewer simultaneous filters
   - Sort by relevance for faster results

3. **Image Loading:**
   - Images use lazy loading (load as you scroll)
   - Wait for images to load before scrolling rapidly
   - Check image URLs are valid

### Getting Help

**Contact Information:**
- **Technical Support**: Check GitHub repository issues
- **System Admin**: Contact your system administrator
- **Bug Reports**: Submit via GitHub Issues with:
  - Steps to reproduce
  - Expected vs actual behavior
  - Browser and OS information
  - Console error messages (F12 > Console)

**Useful Keyboard Shortcuts:**
- `Ctrl + F` (or `Cmd + F`): Search on page
- `F5`: Refresh page
- `F12`: Open Developer Tools (for debugging)
- `Ctrl + Shift + Delete`: Clear browsing data

---

## Appendix

### System URLs Reference

**Public Pages:**
- Homepage: `/`
- Game List: `/store/games/`
- Game Detail: `/store/game/<id>/`
- Cart: `/store/cart/`
- Checkout: `/store/checkout/`
- Wishlist: `/store/wishlist/`

**Authentication:**
- Login: `/auth/login/`
- Register: `/auth/register/`
- Logout: `/auth/logout/`
- Password Reset Request: `/auth/password-reset/request/`
- Password Reset Confirm: `/auth/password-reset/confirm/<token>/`

**User Dashboard:**
- Profile: `/auth/profile/`
- Transactions: `/store/transactions/`
- Transaction Detail: `/store/transactions/<id>/`

**Admin Pages:**
- Admin Dashboard: `/store/admin/dashboard/`
- Game Management: `/store/admin/games/`
- User Management: `/store/admin/users/`
- Promotion Management: `/store/admin/promotions/`
- Analytics Dashboard: `/store/admin/analytics/`

### Glossary

- **Game Key**: Unique activation code for purchased games
- **Promotion**: Time-limited discount on games
- **Transaction**: Completed purchase record
- **Wishlist**: Saved games for future purchase
- **Category**: Game genre classification
- **Tag**: Additional game attributes (e.g., Multiplayer)
- **Admin**: User with elevated privileges
- **Session**: Temporary login state

---

**Version**: 1.0  
**Last Updated**: December 3, 2025  
**GameVault Team**

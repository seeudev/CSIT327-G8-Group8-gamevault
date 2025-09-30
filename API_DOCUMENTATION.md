# GameVault API Documentation

## Base URL
```
http://localhost:8000/api/
```

## Authentication

GameVault uses JWT (JSON Web Token) authentication. Most endpoints require authentication.

### Obtain Token
**Endpoint:** `POST /auth/token/`

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Refresh Token
**Endpoint:** `POST /auth/token/refresh/`

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Using the Token
Include the access token in the Authorization header:
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

## Users API

### Register User
**Endpoint:** `POST /users/`

**Authentication:** Not required

**Request Body:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "password2": "string",
  "first_name": "string",
  "last_name": "string"
}
```

**Response:** (201 Created)
```json
{
  "id": 1,
  "username": "string",
  "email": "string",
  "first_name": "string",
  "last_name": "string",
  "phone_number": null,
  "date_of_birth": null,
  "wallet_balance": "0.00",
  "profile": {
    "bio": "",
    "avatar_url": null,
    "is_verified": false
  },
  "date_joined": "2025-01-01T00:00:00Z"
}
```

### Get Current User Profile
**Endpoint:** `GET /users/me/`

**Authentication:** Required

**Response:**
```json
{
  "id": 1,
  "username": "string",
  "email": "string",
  "first_name": "string",
  "last_name": "string",
  "phone_number": "string",
  "date_of_birth": "1990-01-01",
  "wallet_balance": "100.00",
  "profile": {
    "bio": "string",
    "avatar_url": "https://example.com/avatar.jpg",
    "is_verified": true
  },
  "date_joined": "2025-01-01T00:00:00Z"
}
```

### Update Current User Profile
**Endpoint:** `PUT /users/me/` or `PATCH /users/me/`

**Authentication:** Required

**Request Body:**
```json
{
  "first_name": "string",
  "last_name": "string",
  "phone_number": "string",
  "date_of_birth": "1990-01-01"
}
```

## Games API

### List Games
**Endpoint:** `GET /games/`

**Authentication:** Not required

**Query Parameters:**
- `platform` (optional): Filter by platform (PC, PS5, PS4, XBOX, SWITCH)
- `genre` (optional): Filter by genre (case-insensitive contains)
- `page` (optional): Page number for pagination

**Example Request:**
```
GET /games/?platform=PC&genre=action&page=1
```

**Response:**
```json
{
  "count": 50,
  "next": "http://localhost:8000/api/games/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Game Title",
      "description": "Game description...",
      "price": "59.99",
      "platform": "PC",
      "genre": "Action",
      "publisher": "Publisher Name",
      "release_date": "2024-01-01",
      "cover_image_url": "https://example.com/cover.jpg",
      "is_active": true,
      "stock_count": 100,
      "created_at": "2025-01-01T00:00:00Z",
      "updated_at": "2025-01-01T00:00:00Z"
    }
  ]
}
```

### Get Game Details
**Endpoint:** `GET /games/{id}/`

**Authentication:** Not required

**Response:**
```json
{
  "id": 1,
  "title": "Game Title",
  "description": "Game description...",
  "price": "59.99",
  "platform": "PC",
  "genre": "Action",
  "publisher": "Publisher Name",
  "release_date": "2024-01-01",
  "cover_image_url": "https://example.com/cover.jpg",
  "is_active": true,
  "stock_count": 100,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

### Create Game (Admin Only)
**Endpoint:** `POST /games/`

**Authentication:** Required (Admin)

**Request Body:**
```json
{
  "title": "Game Title",
  "description": "Game description...",
  "price": "59.99",
  "platform": "PC",
  "genre": "Action",
  "publisher": "Publisher Name",
  "release_date": "2024-01-01",
  "cover_image_url": "https://example.com/cover.jpg",
  "stock_count": 100
}
```

### Update Game (Admin Only)
**Endpoint:** `PUT /games/{id}/` or `PATCH /games/{id}/`

**Authentication:** Required (Admin)

### Delete Game (Admin Only)
**Endpoint:** `DELETE /games/{id}/`

**Authentication:** Required (Admin)

## Orders API

### List User Orders
**Endpoint:** `GET /orders/`

**Authentication:** Required

**Response:**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "user": 1,
      "user_username": "gamer123",
      "total_amount": "119.98",
      "status": "COMPLETED",
      "items": [
        {
          "id": 1,
          "game": 1,
          "game_title": "Game Title",
          "game_platform": "PC",
          "price": "59.99",
          "game_key": 123,
          "created_at": "2025-01-01T00:00:00Z"
        }
      ],
      "created_at": "2025-01-01T00:00:00Z",
      "updated_at": "2025-01-01T00:00:00Z"
    }
  ]
}
```

### Create Order (Purchase Games)
**Endpoint:** `POST /orders/`

**Authentication:** Required

**Request Body:**
```json
{
  "game_ids": [1, 2, 3]
}
```

**Response:** (201 Created)
```json
{
  "id": 1,
  "user": 1,
  "user_username": "gamer123",
  "total_amount": "179.97",
  "status": "COMPLETED",
  "items": [
    {
      "id": 1,
      "game": 1,
      "game_title": "Game Title 1",
      "game_platform": "PC",
      "price": "59.99",
      "game_key": 123,
      "created_at": "2025-01-01T00:00:00Z"
    }
  ],
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

**Error Responses:**

Insufficient balance:
```json
{
  "error": "Insufficient wallet balance"
}
```

Out of stock:
```json
{
  "error": "Game 'Game Title' is out of stock"
}
```

Game not available:
```json
{
  "error": "Some games are not available"
}
```

### Get Order Details
**Endpoint:** `GET /orders/{id}/`

**Authentication:** Required (Owner only)

**Response:**
```json
{
  "id": 1,
  "user": 1,
  "user_username": "gamer123",
  "total_amount": "59.99",
  "status": "COMPLETED",
  "items": [
    {
      "id": 1,
      "game": 1,
      "game_title": "Game Title",
      "game_platform": "PC",
      "price": "59.99",
      "game_key": 123,
      "created_at": "2025-01-01T00:00:00Z"
    }
  ],
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

### Get Order Game Keys
**Endpoint:** `GET /orders/{id}/keys/`

**Authentication:** Required (Owner only)

**Response:**
```json
[
  {
    "game_title": "Game Title",
    "platform": "PC",
    "key_code": "XXXXX-XXXXX-XXXXX-XXXXX"
  }
]
```

## Status Codes

- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `204 No Content` - Resource deleted successfully
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Permission denied
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

## Error Response Format

```json
{
  "error": "Error message description"
}
```

Or for validation errors:
```json
{
  "field_name": ["Error message for this field"]
}
```

## Platform Values
- `PC` - PC
- `PS5` - PlayStation 5
- `PS4` - PlayStation 4
- `XBOX` - Xbox
- `SWITCH` - Nintendo Switch

## Order Status Values
- `PENDING` - Order is being processed
- `COMPLETED` - Order completed, keys available
- `CANCELLED` - Order cancelled
- `REFUNDED` - Order refunded

## Game Key Status Values
- `AVAILABLE` - Key available for purchase
- `SOLD` - Key has been sold
- `RESERVED` - Key temporarily reserved

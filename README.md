# Green Spoon - Backend API

A Flask-based REST API backend for the Green Spoon recipe sharing application. This backend provides user authentication, recipe management, comments, and admin functionality integrated with Supabase for database and authentication, and Cloudinary for image storage.

## Features

- **User Authentication**: Sign up and login with email/password using Supabase Auth
- **Recipe Management**: Create, read, update, and delete recipes
- **Comments System**: Add and manage comments on recipes
- **User Profiles**: Manage user information, profile pictures, and preferences
- **Admin Dashboard**: Admin-specific routes and functionality
- **Contact Support**: Submit support requests and contact forms
- **Token Validation**: JWT token validation for protected endpoints
- **Image Uploads**: Cloudinary integration for recipe and profile image management
- **CORS Support**: Configured for cross-origin requests from frontend applications

## Tech Stack

- **Framework**: Flask 3.1.1
- **Database & Auth**: Supabase 2.16.0
- **Image Storage**: Cloudinary 1.44.1
- **Python Version**: Python 3.13+
- **Server**: Gunicorn 23.0.0
- **CORS**: Flask-CORS 6.0.1
- **Environment Management**: python-dotenv 1.1.1

## Project Structure

```
backend/
├── main.py                  # Flask app initialization and core routes
├── config.py               # Configuration settings (commented out)
├── requirements.txt        # Python dependencies
├── pyproject.toml         # Project metadata and dependencies
├── README.md              # This file
├── routes/                # API route blueprints
│   ├── admin.py          # Admin-specific endpoints
│   ├── auth_routes.py    # Authentication endpoints (signup, login)
│   ├── recipe_routes.py  # Recipe management endpoints
│   ├── comment_routes.py # Comment management endpoints
│   └── user_routes.py    # User profile endpoints
└── utils/
    └── token_required.py  # JWT token validation decorator
```

## API Endpoints

### Authentication Routes (`/api`)
- `POST /signup` - Create new user account
- `POST /login` - User login
- `GET /validate_token` - Validate JWT token

### Recipe Routes (`/api`)
- Recipe management endpoints (CRUD operations)
- Image upload and management

### Comment Routes (`/api`)
- `POST /create_comment` - Create a new comment (requires authentication)
- Comment retrieval and management

### User Routes (`/api`)
- User profile management
- Profile picture upload and updates

### Admin Routes (`/api`)
- Admin-specific operations and management

### Support (`/api`)
- `POST /contact` - Submit support request (requires authentication)

## Authentication

The API uses JWT (JSON Web Token) authentication via Supabase. Protected endpoints require:

1. Include the token in the `Authorization` header:
   ```
   Authorization: Bearer <your_jwt_token>
   ```

2. The `@token_required` decorator validates the token and extracts the `user_id`

## CORS Configuration

The backend is configured to accept requests from:
- `https://green-spoon.vercel.app` (production frontend)
- `http://localhost:5173` (local development frontend)

To add/modify CORS origins, update the `CORS()` configuration in `main.py`.

## Database Schema

The project uses Supabase with the following main tables:
- **User** - User account information
- **Recipe** - Recipe details and metadata
- **Comment** - Comments on recipes
- **contact_us** - Support request submissions

## Error Handling

The API returns standardized JSON error responses:
```json
{
  "error": "Error message description"
}
```

HTTP Status Codes:
- `200` - OK
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `500` - Internal Server Error

## Related Projects

- **Frontend**: Green Spoon React frontend (https://green-spoon.vercel.app)


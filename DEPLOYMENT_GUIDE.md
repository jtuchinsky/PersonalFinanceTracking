# Personal Finance Tracker - Deployment Guide

This guide explains how to start the separated backend and frontend services for the Personal Finance Tracker application.

## 🏗️ Architecture Overview

The application has been refactored into separate services:

- **User Backend** (Port 8000) - Handles user operations
- **Admin Backend** (Port 8001) - Handles admin operations
- **User Frontend** (Port 3000) - User interface
- **Admin Frontend** (Port 3001) - Admin interface

## 📋 Prerequisites

- Python 3.11+
- Node.js 18+
- `uv` package manager (recommended) or `pip`
- `yarn` package manager
- MongoDB Atlas connection (configured in `.env`)

## 🚀 Quick Start

### 1. Start Backend Services

#### Option A: Using `uv` (Recommended)

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (first time only)
uv venv

# Install dependencies
source .venv/bin/activate && uv pip install -r requirements.txt

# Start User Server (Terminal 1)
source .venv/bin/activate && uvicorn user_server:app --host 0.0.0.0 --port 8000

# Start Admin Server (Terminal 2)
source .venv/bin/activate && uvicorn admin_server:app --host 0.0.0.0 --port 8001
```

#### Option B: Using `pip`

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (first time only)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start User Server (Terminal 1)
uvicorn user_server:app --host 0.0.0.0 --port 8000

# Start Admin Server (Terminal 2)
uvicorn admin_server:app --host 0.0.0.0 --port 8001
```

### 2. Start Frontend Applications

#### User Frontend (Terminal 3)

```bash
cd frontend

# Install dependencies (first time only)
yarn install

# Set environment variables
cp .env.example .env
# Edit .env to set: REACT_APP_USER_BACKEND_URL=http://localhost:8000

# Start user frontend
yarn start
```

#### Admin Frontend (Terminal 4)

```bash
cd frontend-admin

# Install dependencies (first time only)
yarn install

# Set environment variables
cp .env.example .env
# Edit .env to set: REACT_APP_ADMIN_BACKEND_URL=http://localhost:8001

# Start admin frontend
PORT=3001 yarn start
```

## 🌐 Service URLs

### Backend APIs

| Service | URL | Purpose | Documentation |
|---------|-----|---------|---------------|
| **User API** | `http://localhost:8000` | User operations | `http://localhost:8000/docs` |
| **Admin API** | `http://localhost:8001` | Admin operations | `http://localhost:8001/docs` |

### Frontend Applications

| Application | URL | Purpose |
|-------------|-----|---------|
| **User App** | `http://localhost:3000` | User interface |
| **Admin App** | `http://localhost:3001` | Admin interface |

### API Endpoints

#### User Server (`http://localhost:8000/api/`)

- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/dashboard` - User dashboard data
- `GET /api/accounts` - Get user accounts
- `POST /api/accounts` - Create new account
- `GET /api/transactions` - Get transactions
- `POST /api/transactions` - Create transaction
- `GET /api/categories` - Get categories

#### Admin Server (`http://localhost:8001/api/admin/`)

- `GET /api/admin/stats` - System statistics
- `GET /api/admin/users` - Get all users
- `POST /api/admin/users/{user_id}/lock` - Lock user account
- `POST /api/admin/users/{user_id}/unlock` - Unlock user account
- `DELETE /api/admin/users/{user_id}` - Delete user account
- `GET /api/admin/activities` - Get user activities
- `GET /api/admin/emails` - Get sent emails

## ⚙️ Environment Configuration

### Backend Environment (`.env`)

```bash
# MongoDB Configuration
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
DB_NAME=your_database_name

# JWT Configuration
JWT_SECRET=your-secret-key-here
JWT_ALGORITHM=HS256

# Encryption Configuration
ENCRYPTION_KEY=your-encryption-key-here

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

### Frontend Environment

#### User Frontend (`.env`)
```bash
REACT_APP_USER_BACKEND_URL=http://localhost:8000
```

#### Admin Frontend (`.env`)
```bash
REACT_APP_ADMIN_BACKEND_URL=http://localhost:8001
```

## 🔧 Development Commands

### Backend

```bash
# Run tests
cd backend
source .venv/bin/activate && python -m pytest backend_test.py -v

# Create admin user
cd backend
source .venv/bin/activate && python create_admin.py create

# List admin users
cd backend
source .venv/bin/activate && python create_admin.py list
```

### Frontend

```bash
# Build for production (User)
cd frontend && yarn build

# Build for production (Admin)
cd frontend-admin && yarn build

# Run tests
cd frontend && yarn test
cd frontend-admin && yarn test
```

## 🐛 Troubleshooting

### Common Issues

1. **SSL/MongoDB Connection Issues**
   - Ensure you're using `uv` for dependency management
   - Check MongoDB connection string in `.env`
   - Verify network connectivity to MongoDB Atlas

2. **Port Already in Use**
   ```bash
   # Kill processes on specific ports
   lsof -ti:8000 | xargs kill -9  # User server
   lsof -ti:8001 | xargs kill -9  # Admin server
   lsof -ti:3000 | xargs kill -9  # User frontend
   lsof -ti:3001 | xargs kill -9  # Admin frontend
   ```

3. **CORS Issues**
   - Verify `CORS_ORIGINS` in backend `.env` includes frontend URLs
   - Check frontend environment variables point to correct backend URLs

4. **Authentication Issues**
   - Ensure JWT_SECRET is set in backend `.env`
   - Check if admin user exists (use `create_admin.py`)

### Verification Commands

```bash
# Test API endpoints
curl http://localhost:8000/docs  # User API docs
curl http://localhost:8001/docs  # Admin API docs

# Test API functionality
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "name": "Test User", "password": "testpass123"}'

curl -X GET http://localhost:8001/api/admin/stats  # Should return "Not authenticated"
```

## 📊 Monitoring

### Server Logs

Both servers log requests and errors to the console. Monitor the terminals running the servers for:

- Request logs (INFO level)
- Error messages
- Database connection status
- Authentication failures

### Health Checks

- User API: `GET http://localhost:8000/docs`
- Admin API: `GET http://localhost:8001/docs`
- User Frontend: `http://localhost:3000`
- Admin Frontend: `http://localhost:3001`

## 🏭 Production Deployment

For production deployment:

1. **Backend**: Use a process manager like `supervisor` or `pm2`
2. **Frontend**: Build static files and serve with nginx
3. **Database**: Ensure MongoDB Atlas production configuration
4. **Environment**: Set production environment variables
5. **SSL**: Configure HTTPS certificates
6. **Monitoring**: Set up logging and monitoring systems

## 📁 File Structure

```
PersonalFinanceTracking/
├── backend/
│   ├── user_server.py          # User API server
│   ├── admin_server.py         # Admin API server
│   ├── shared/                 # Shared modules
│   │   ├── database.py         # Database connection
│   │   ├── auth.py            # Authentication
│   │   ├── models.py          # Pydantic models
│   │   ├── utils.py           # Utilities
│   │   └── email.py           # Email service
│   ├── requirements.txt        # Python dependencies
│   └── .env                   # Environment variables
├── frontend/                   # User frontend
│   ├── src/
│   ├── package.json
│   └── .env
├── frontend-admin/            # Admin frontend
│   ├── src/
│   ├── package.json
│   └── .env
└── DEPLOYMENT_GUIDE.md        # This file
```

---

## 🎉 Success!

If all services start successfully, you should see:

- ✅ User server running on `http://localhost:8000`
- ✅ Admin server running on `http://localhost:8001`
- ✅ User frontend accessible at `http://localhost:3000`
- ✅ Admin frontend accessible at `http://localhost:3001`

The Personal Finance Tracker is now fully operational with separated admin and user functionality!
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Personal Finance Tracker is a full-stack web application built with FastAPI (backend) and React (frontend). It allows users to manage financial accounts, track transactions, categorize expenses, and provides an admin system for user management.

**Key Features:**
- User authentication with JWT tokens
- Financial account management with encrypted credentials
- Transaction tracking and categorization
- Admin dashboard for user/system management
- MongoDB document storage
- Mock email notification system

## Architecture

### Backend (FastAPI) - Split Architecture
- **User Server**: `backend/user_server.py` - User-facing API (port 8000)
- **Admin Server**: `backend/admin_server.py` - Admin-only API (port 8001)
- **Shared Modules**: `backend/shared/` - Common database, auth, models, and utilities
- **Database**: MongoDB with Motor (async driver)
- **Authentication**: JWT-based with bcrypt password hashing
- **Security**: Fernet encryption for banking credentials
- **Admin tools**: `backend/create_admin.py` for admin account creation

### Frontend (React) - Split Applications
- **User Frontend**: `frontend/` - User application (port 3000)
- **Admin Frontend**: `frontend-admin/` - Admin application (port 3001)
- **Build system**: Create React App with CRACO for customization
- **UI Components**: Radix UI primitives with shadcn/ui styling
- **Styling**: TailwindCSS with custom configuration
- **State management**: React hooks and context
- **Routing**: React Router for navigation

### Key Components
#### User Application
- `Dashboard.js` - Main user dashboard with financial overview
- `AccountManager.js` - Financial account management
- `TransactionForm.js`/`TransactionList.js` - Transaction handling
- `Login.js`/`Register.js` - Authentication components

#### Admin Application
- `AdminDashboard.js` - Admin panel for user management
- `AdminLogin.js` - Admin-specific authentication

## Development Commands

### Backend Development
```bash
# Install Python dependencies
cd backend
pip install -r requirements.txt

# Start USER server (port 8000)
cd backend
python user_server.py

# OR using uvicorn directly:
uvicorn user_server:app --reload --host 0.0.0.0 --port 8000

# Start ADMIN server (port 8001)
cd backend
python admin_server.py

# OR using uvicorn directly:
uvicorn admin_server:app --reload --host 0.0.0.0 --port 8001

# Create admin account (interactive)
cd backend
python create_admin.py create

# List existing admins
cd backend
python create_admin.py list
```

### Frontend Development
```bash
# USER FRONTEND (port 3000)
# Install dependencies
cd frontend
yarn install

# Start development server
cd frontend
yarn start

# Build for production
cd frontend
yarn build

# ADMIN FRONTEND (port 3001)
# Install dependencies
cd frontend-admin
yarn install

# Start development server
REACT_APP_ADMIN_BACKEND_URL=http://localhost:8001 PORT=3001 yarn start

# Build for production
cd frontend-admin
yarn build

# Run tests
cd frontend
yarn test
cd ../frontend-admin
yarn test
```

### Database Setup
```bash
# Seed MongoDB with sample data
cd mongo_seed_kit
python seed_mongo.py

# Apply database indexes
cd mongo_seed_kit
mongosh < mongo_indexes.js
```

## Database Schema

### Collections
- **users** - User accounts with authentication and admin flags
- **accounts** - Financial accounts (checking, savings, credit cards)
- **transactions** - Financial transactions with categories and amounts
- **categories** - Expense categories with colors and icons
- **account_credentials** - Encrypted banking login credentials
- **user_activities** - Audit log for user and admin actions

### Environment Variables
Backend requires these environment variables in `backend/.env`:
- `MONGO_URL` - MongoDB connection string
- `DB_NAME` - Database name (default: finance_tracker)  
- `JWT_SECRET` - Secret key for JWT token signing
- `ENCRYPTION_KEY` - Key for encrypting banking credentials
- `CORS_ORIGINS` - Allowed CORS origins (comma-separated)

## Code Conventions

### Backend
- Uses Pydantic models for request/response validation
- Async/await pattern throughout with Motor MongoDB driver
- HTTPException for error handling
- Dependency injection for authentication middleware
- Comprehensive logging and activity tracking

### Frontend
- Functional components with React hooks
- Custom hooks in `src/hooks/` directory
- Utility functions in `src/lib/utils.js`
- Consistent component structure with props validation
- TailwindCSS for styling with custom utility classes

### Authentication Flow
1. Users register/login through `/api/auth/` endpoints
2. JWT tokens returned and stored client-side
3. Protected routes use Bearer token authentication
4. Admin routes require `is_admin: true` flag validation
5. Activity logging for all user and admin actions

## Testing

### Running Tests
```bash
# Backend tests
cd backend
python -m pytest backend_test.py -v

# Frontend tests  
cd frontend
yarn test
```

### Test Files
- `backend_test.py` - Comprehensive backend API tests
- `tests/` directory - Additional test modules

## Admin System

### Admin Account Creation
Use the command-line tool to create admin accounts:
```bash
cd backend
python create_admin.py create
```

### Admin Features
- User account management (lock/unlock/delete)
- System statistics and monitoring
- Activity log viewing
- Email notification logs
- Cannot modify other admin accounts (protection)

## Security Considerations

- Banking credentials encrypted with Fernet symmetric encryption
- Passwords hashed with bcrypt
- JWT tokens for stateless authentication
- CORS configuration for frontend/backend communication
- Activity logging for audit trail
- Admin account protection mechanisms

## Development Notes

- The application creates sample data on user registration for demo purposes
- Email service is mocked for development (logs to console)
- Default categories are automatically created for new users
- Account balances update automatically with transaction creation
- MongoDB indexes should be applied for production performance
# 💰 Personal Finance Tracker

A full-stack web application for comprehensive personal finance management built with FastAPI (backend) and React (frontend). Track accounts, transactions, categories, and expenses with an intuitive interface and robust admin system.

![MongoDB](https://img.shields.io/badge/MongoDB-4EA94B?style=for-the-badge&logo=mongodb&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)

## ✨ Features

### 🔐 User Management
- **Secure Authentication**: JWT-based authentication with bcrypt password hashing
- **Account Management**: User registration, login, and profile management
- **Admin System**: Comprehensive admin dashboard for user and system management

### 💳 Financial Account Management
- **Multiple Account Types**: Support for checking, savings, and credit card accounts
- **Encrypted Credentials**: Secure storage of banking credentials using Fernet encryption
- **Real-time Balances**: Automatic balance updates with transaction creation

### 📊 Transaction Tracking
- **Comprehensive Tracking**: Record all income and expense transactions
- **Category Management**: Organize transactions with customizable categories
- **Date-based Organization**: Sort and filter transactions by date ranges

### 🎨 Modern UI/UX
- **Responsive Design**: Mobile-friendly interface built with TailwindCSS
- **Component Library**: Radix UI primitives with shadcn/ui styling
- **Interactive Dashboard**: Real-time financial overview and analytics

### ⚙️ Admin Features
- **User Management**: Lock, unlock, and delete user accounts
- **System Monitoring**: Activity logs and system statistics
- **Email Notifications**: Mock email service for development
- **Security Controls**: Admin-only access with protection mechanisms

## 🏗️ Architecture

### Backend (FastAPI)
- **Framework**: FastAPI with async/await patterns
- **Database**: MongoDB with Motor (async driver)
- **Authentication**: JWT tokens with bcrypt password hashing
- **Security**: Fernet encryption for sensitive data
- **API Design**: RESTful endpoints with Pydantic validation

### Frontend (React)
- **Framework**: React with Create React App and CRACO
- **Styling**: TailwindCSS with custom configuration
- **Components**: Radix UI primitives and shadcn/ui
- **State Management**: React hooks and context
- **Routing**: React Router for navigation

### Database (MongoDB)
- **Collections**: Users, accounts, transactions, categories, credentials, activities
- **Indexes**: Optimized indexes for performance
- **Validation**: Schema validation with MongoDB validators
- **Relationships**: Document references with UUID identifiers

## 🚀 Quick Start

### Prerequisites
- **Node.js** 16+ and Yarn
- **Python** 3.8+ and pip
- **MongoDB** 7.0+ (local, Docker, or Atlas)

### 1. Database Setup

#### Option A: Local MongoDB
```bash
# Install MongoDB (Ubuntu/Debian)
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt-get update && sudo apt-get install -y mongodb-org

# Start MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod
```

#### Option B: Docker MongoDB
```bash
docker run -d \
  --name finance-tracker-mongo \
  -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=password \
  -v mongodb_data:/data/db \
  mongo:7.0
```

#### Option C: MongoDB Atlas
```bash
# Use connection string format:
# mongodb+srv://username:password@cluster.mongodb.net/personal_finance_tracker?retryWrites=true&w=majority
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Edit environment variables
nano .env
```

#### Environment Variables (.env)
```bash
# MongoDB Configuration
MONGO_URL=mongodb://localhost:27017
DB_NAME=personal_finance_tracker

# Security Keys
JWT_SECRET=your-super-secret-jwt-key-here
ENCRYPTION_KEY=your-32-character-encryption-key

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

#### Initialize Database
```bash
# Apply database indexes and validation
cd mongo_seed_kit
mongosh personal_finance_tracker < mongo_indexes.js

# Seed with sample data (optional)
python seed_mongo.py
```

#### Start Backend Server
```bash
cd backend
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
yarn install

# Start development server
yarn start
```

The application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### 4. Create Admin Account

```bash
cd backend
python create_admin.py create
```

Follow the interactive prompts to create your admin account.

## 📋 Database Schema

### Collections Overview

#### Users Collection
```javascript
{
  "id": "uuid-string",              // Application UUID
  "email": "user@example.com",      // Unique email
  "name": "John Doe",               // Full name
  "password": "hashed_password",    // Bcrypt hash
  "is_admin": false,                // Admin flag
  "account_status": "active",       // active|locked|deleted
  "last_login": ISODate("..."),     // Last login
  "created_at": ISODate("..."),     // Creation date
  "updated_at": ISODate("...")      // Update date
}
```

#### Accounts Collection
```javascript
{
  "id": "uuid-string",              // Application UUID
  "user_id": "user-uuid",           // User reference
  "name": "Chase Freedom Card",     // Account name
  "account_type": "credit_card",    // checking|savings|credit_card
  "bank_name": "Chase",             // Bank name
  "balance": 1250.75,               // Current balance
  "nickname": "Rewards Card",       // User nickname
  "description": "Main card",       // Description
  "is_default": false,              // Default flag
  "created_at": ISODate("..."),     // Creation date
  "updated_at": ISODate("...")      // Update date
}
```

#### Transactions Collection
```javascript
{
  "id": "uuid-string",              // Application UUID
  "user_id": "user-uuid",           // User reference
  "account_id": "account-uuid",     // Account reference
  "amount": -45.67,                 // Amount (negative = expense)
  "description": "Grocery Store",   // Description
  "category": "Food & Dining",      // Category
  "transaction_type": "debit",      // debit|credit
  "date": ISODate("..."),           // Transaction date
  "created_at": ISODate("..."),     // Creation date
  "updated_at": ISODate("...")      // Update date
}
```

For complete schema documentation, see [MONGODB_SETUP.md](MONGODB_SETUP.md).

## 🛠️ Development

### Backend Development

#### Running Tests
```bash
cd backend
python -m pytest backend_test.py -v
```

#### API Documentation
Visit http://localhost:8000/docs for interactive API documentation with Swagger UI.

#### Database Management
```bash
# Create database backup
mongodump --db personal_finance_tracker --out /backup/$(date +%Y%m%d)

# Restore database
mongorestore --db personal_finance_tracker /backup/20250910/personal_finance_tracker/

# Apply indexes
mongosh personal_finance_tracker < mongo_seed_kit/mongo_indexes.js
```

### Frontend Development

#### Available Scripts
```bash
yarn start      # Start development server
yarn build      # Build for production
yarn test       # Run test suite
yarn lint       # Run ESLint
```

#### Component Development
- Components located in `src/components/`
- Custom hooks in `src/hooks/`
- Utilities in `src/lib/utils.js`
- Styling with TailwindCSS

### Database Operations

#### Indexes
```javascript
// Key indexes for performance
db.users.createIndex({ "email": 1 }, { unique: true })
db.transactions.createIndex({ "user_id": 1, "date": -1 })
db.accounts.createIndex({ "user_id": 1, "account_type": 1 })
```

#### Sample Queries
```javascript
// Get user transactions for current month
db.transactions.find({
  user_id: "user-uuid",
  date: { $gte: ISODate("2025-09-01") }
}).sort({ date: -1 })

// Calculate spending by category
db.transactions.aggregate([
  { $match: { user_id: "user-uuid", transaction_type: "debit" }},
  { $group: { _id: "$category", total: { $sum: { $abs: "$amount" }}}},
  { $sort: { total: -1 }}
])
```

## 🔐 Security

### Authentication
- **JWT Tokens**: Secure stateless authentication
- **Password Hashing**: Bcrypt with salt rounds
- **Admin Protection**: Cannot modify other admin accounts
- **Session Management**: Proper token expiration

### Data Protection
- **Credential Encryption**: Banking credentials encrypted with Fernet
- **Environment Variables**: Sensitive configuration in .env files
- **CORS Configuration**: Restricted cross-origin requests
- **Input Validation**: Pydantic models for API validation

### Activity Logging
- **Audit Trail**: Complete logging of user and admin actions
- **IP Tracking**: User location and access pattern monitoring
- **Admin Monitoring**: Special logging for administrative actions

## 📊 Monitoring & Maintenance

### Database Monitoring
```bash
# Database statistics
mongosh personal_finance_tracker --eval "db.stats()"

# Collection statistics
mongosh personal_finance_tracker --eval "db.transactions.stats()"

# Index usage analysis
mongosh personal_finance_tracker --eval "db.transactions.aggregate([{\$indexStats: {}}])"
```

### Application Monitoring
- **System Statistics**: User counts, transaction volumes
- **Performance Metrics**: Response times, database queries
- **Activity Logs**: User actions and admin operations
- **Email Notifications**: Mock email service for development

### Backup Procedures
```bash
# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
mongodump --db personal_finance_tracker --gzip --out /backup/$DATE
find /backup -type d -mtime +30 -exec rm -rf {} \;
```

## 🚨 Troubleshooting

### Common Issues

#### Backend Connection Issues
```bash
# Check MongoDB status
sudo systemctl status mongod

# Test database connection
mongosh personal_finance_tracker

# Check backend logs
tail -f /var/log/supervisor/backend.log
```

#### Frontend Build Issues
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
yarn install

# Check for TypeScript errors
yarn build
```

#### Database Issues
```bash
# Check disk space
df -h

# Compact collections
mongosh personal_finance_tracker --eval "db.runCommand({compact: 'transactions'})"

# Rebuild indexes
mongosh personal_finance_tracker --eval "db.transactions.reIndex()"
```

## 📚 Documentation

- **[MongoDB Setup Guide](MONGODB_SETUP.md)**: Comprehensive database setup and configuration
- **[Admin Features Guide](ADMIN_FEATURES.md)**: Complete admin system documentation
- **[Development Guide](CLAUDE.md)**: Development setup and coding guidelines
- **[API Documentation](http://localhost:8000/docs)**: Interactive API documentation

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make changes following coding conventions
4. Run tests and linting
5. Submit a pull request

### Code Standards
- **Backend**: Follow PEP 8 and FastAPI best practices
- **Frontend**: Use ESLint and Prettier configurations
- **Database**: Follow MongoDB schema conventions
- **Documentation**: Update relevant documentation

## 📄 License

This project is licensed under the MIT License. See LICENSE file for details.

## 🙏 Acknowledgments

- **FastAPI**: Modern, fast web framework for building APIs
- **React**: A JavaScript library for building user interfaces
- **MongoDB**: Document-based database for modern applications
- **TailwindCSS**: Utility-first CSS framework
- **Radix UI**: Low-level UI primitives for React

---

**Finance Tracker** - Empowering personal finance management through modern technology.

*Last Updated: September 17, 2025*
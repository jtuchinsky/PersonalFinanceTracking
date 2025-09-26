# MongoDB Setup Guide

This guide covers setting up MongoDB for the Personal Finance Tracker application, including database schema, indexes, and configuration.

## Quick Start

1. **Install MongoDB** (local development)
   ```bash
   # macOS with Homebrew
   brew install mongodb-community

   # Start MongoDB
   brew services start mongodb-community
   ```

2. **MongoDB Atlas** (cloud deployment)
   - Create account at https://cloud.mongodb.com/
   - Create new cluster
   - Get connection string

3. **Environment Configuration**
   ```bash
   # backend/.env
   MONGO_URL=mongodb://localhost:27017  # Local
   # or
   MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/  # Atlas

   DB_NAME=finance_tracker
   ```

---

# Database Schema Documentation

## MongoDB Collections Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Personal Finance Tracker Database                     │
│                               (MongoDB)                                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Entity Relationship Diagram

```
┌─────────────────────┐         ┌─────────────────────┐
│       users         │         │    user_activities  │
├─────────────────────┤         ├─────────────────────┤
│ id (PK)            │◄────────┤ user_id (FK)       │
│ email              │         │ id (PK)            │
│ name               │         │ action             │
│ password (hashed)  │         │ details            │
h│ account_status     │         │ ip_address         │
│ last_login         │         │ timestamp          │
│ created_at         │         └─────────────────────┘
│ updated_at         │
└─────────────────────┘

┌─────────────────────┐         ┌─────────────────────┐
│       admins        │         │   admin_activities  │
├─────────────────────┤         ├─────────────────────┤
│ id (PK)            │◄────────┤ admin_id (FK)      │
│ email              │         │ id (PK)            │
│ name               │         │ action             │
│ password (hashed)  │         │ details            │
│ role               │         │ target_user_id     │
│ permissions        │         │ ip_address         │
│ account_status     │         │ timestamp          │
│ created_by         │         └─────────────────────┘
│ last_login         │
│ created_at         │
│ updated_at         │
└─────────────────────┘
         │
         │ 1:N
         ▼
┌─────────────────────┐
│      accounts       │
├─────────────────────┤
│ id (PK)            │
│ user_id (FK)       │◄─────────────────┐
│ name               │                  │
│ account_type       │                  │ 1:1
│ bank_name          │                  │
│ balance            │                  ▼
│ nickname           │         ┌─────────────────────┐
│ description        │         │ account_credentials │
│ is_default         │         ├─────────────────────┤
│ created_at         │         │ id (PK)            │
└─────────────────────┘         │ account_id (FK)    │
         │                      │ username (encrypted)│
         │ 1:N                  │ password (encrypted)│
         ▼                      │ created_at         │
┌─────────────────────┐         └─────────────────────┘
│    transactions     │
├─────────────────────┤         ┌─────────────────────┐
│ id (PK)            │         │     categories      │
│ user_id (FK)       │         ├─────────────────────┤
│ account_id (FK)    │         │ id (PK)            │
│ amount             │         │ name               │
│ description        │         │ color              │
│ category           │◄────────┤ icon               │
│ transaction_type   │         └─────────────────────┘
│ date               │
│ created_at         │
└─────────────────────┘
```

## Collection Details

### 1. users
**Purpose**: Store user authentication and profile information
```json
{
  "id": "uuid4",
  "email": "user@example.com",
  "name": "John Doe",
  "password": "hashed_password_with_bcrypt",
  "account_status": "active|locked|deleted",
  "last_login": "2024-01-01T00:00:00Z",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### 2. admins
**Purpose**: Store admin authentication, roles, and permissions
```json
{
  "id": "uuid4",
  "email": "admin@example.com",
  "name": "System Administrator",
  "password": "hashed_password_with_bcrypt",
  "role": "admin|super_admin",
  "permissions": ["user_management", "system_stats", "view_activities"],
  "account_status": "active|locked|deleted",
  "last_login": "2024-01-01T00:00:00Z",
  "created_by": "admin_uuid4",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### 3. accounts
**Purpose**: Store financial account information
```json
{
  "id": "uuid4",
  "user_id": "user_uuid4",
  "name": "Chase Checking",
  "account_type": "checking|savings|credit_card",
  "bank_name": "Chase Bank",
  "balance": 1500.00,
  "nickname": "Main Checking",
  "description": "Primary checking account",
  "is_default": false,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### 4. transactions
**Purpose**: Store financial transactions
```json
{
  "id": "uuid4",
  "user_id": "user_uuid4",
  "account_id": "account_uuid4",
  "amount": -50.00,
  "description": "Grocery shopping",
  "category": "Food & Dining",
  "transaction_type": "debit|credit",
  "date": "2024-01-01T00:00:00Z",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### 5. categories
**Purpose**: Store expense/income categories
```json
{
  "id": "uuid4",
  "name": "Food & Dining",
  "color": "#FF6B6B",
  "icon": "utensils"
}
```

### 6. account_credentials
**Purpose**: Store encrypted banking login credentials
```json
{
  "id": "uuid4",
  "account_id": "account_uuid4",
  "username": "encrypted_username",
  "password": "encrypted_password",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### 7. user_activities
**Purpose**: Audit log for user actions
```json
{
  "id": "uuid4",
  "user_id": "user_uuid4",
  "action": "login|logout|create_account|create_transaction",
  "details": "User logged in successfully",
  "ip_address": "192.168.1.100",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 8. admin_activities
**Purpose**: Audit log for admin actions
```json
{
  "id": "uuid4",
  "admin_id": "admin_uuid4",
  "action": "admin_login|admin_lock_user|admin_view_stats",
  "details": "Admin locked account for user john@example.com",
  "target_user_id": "user_uuid4",
  "ip_address": "192.168.1.100",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## Database Setup Commands

### 1. Create Database and Collections
```javascript
// Connect to MongoDB
use finance_tracker

// Collections will be created automatically when first document is inserted
// No explicit creation needed for MongoDB collections
```

### 2. Create Indexes for Performance
```javascript
// User indexes
db.users.createIndex({ "email": 1 }, { unique: true, name: "uniq_user_email" })
db.users.createIndex({ "id": 1 }, { unique: true, name: "uniq_user_id" })

// Admin indexes
db.admins.createIndex({ "email": 1 }, { unique: true, name: "uniq_admin_email" })
db.admins.createIndex({ "id": 1 }, { unique: true, name: "uniq_admin_id" })

// Account indexes
db.accounts.createIndex({ "user_id": 1 })

// Transaction indexes
db.transactions.createIndex({ "user_id": 1 })
db.transactions.createIndex({ "account_id": 1 })
db.transactions.createIndex({ "date": -1 })
db.transactions.createIndex({ "user_id": 1, "date": -1 })

// Activity indexes
db.user_activities.createIndex({ "user_id": 1, "timestamp": -1 }, { name: "user_activity_time" })
db.admin_activities.createIndex({ "admin_id": 1, "timestamp": -1 }, { name: "admin_activity_time" })

// Account credentials indexes
db.account_credentials.createIndex({ "account_id": 1 }, { unique: true })

// Category indexes
db.categories.createIndex({ "name": 1 })
```

### 3. Seed Default Categories
```javascript
// Default expense categories
db.categories.insertMany([
  { "id": "cat_1", "name": "Food & Dining", "color": "#FF6B6B", "icon": "utensils" },
  { "id": "cat_2", "name": "Transportation", "color": "#4ECDC4", "icon": "car" },
  { "id": "cat_3", "name": "Shopping", "color": "#45B7D1", "icon": "shopping-bag" },
  { "id": "cat_4", "name": "Entertainment", "color": "#96CEB4", "icon": "music" },
  { "id": "cat_5", "name": "Bills & Utilities", "color": "#FFEAA7", "icon": "zap" },
  { "id": "cat_6", "name": "Healthcare", "color": "#DDA0DD", "icon": "heart" },
  { "id": "cat_7", "name": "Travel", "color": "#98D8C8", "icon": "plane" },
  { "id": "cat_8", "name": "Education", "color": "#F7DC6F", "icon": "book" },
  { "id": "cat_9", "name": "Investments", "color": "#BB8FCE", "icon": "trending-up" },
  { "id": "cat_10", "name": "Other", "color": "#AEB6BF", "icon": "more-horizontal" }
])
```

## Relationships

1. **users → accounts** (1:N): One user can have multiple financial accounts
2. **users → transactions** (1:N): One user can have multiple transactions
3. **users → user_activities** (1:N): One user can have multiple activity log entries
4. **admins → admin_activities** (1:N): One admin can have multiple activity log entries
5. **accounts → transactions** (1:N): One account can have multiple transactions
6. **accounts → account_credentials** (1:1): Each account has one set of encrypted credentials
7. **categories → transactions** (1:N): One category can be used by multiple transactions
8. **admins → admins** (1:N): One super admin can create multiple admin accounts (via created_by)

## Security Features

- **Password Hashing**: User and admin passwords are hashed using bcrypt
- **Credential Encryption**: Banking credentials are encrypted using Fernet symmetric encryption
- **JWT Authentication**: Stateless authentication using JWT tokens with user_type differentiation
- **Database Separation**: Admins and users are stored in completely separate collections
- **Admin Isolation**: Admin functions are isolated in separate server/endpoints (port 8001)
- **Role-Based Access**: Admin roles (admin, super_admin) with granular permissions
- **Activity Logging**: Separate audit trails for user and admin actions
- **Admin Protection**: Admins cannot modify other admin accounts

## Data Flow

1. **User Registration**: Creates user record in users collection with hashed password
2. **Admin Creation**: Creates admin record in admins collection with role and permissions
3. **Account Creation**: Creates account record + encrypted credentials
4. **Transaction Creation**: Updates account balance and creates transaction record
5. **User Actions**: All user operations are logged in user_activities
6. **Admin Actions**: All admin operations are logged in admin_activities
7. **Authentication**: JWT tokens include user_type ("user" or "admin") for proper routing

## Backup and Maintenance

### 1. Backup Commands
```bash
# Full database backup
mongodump --db finance_tracker --out /backup/$(date +%Y%m%d)

# Restore from backup
mongorestore --db finance_tracker /backup/20240101/finance_tracker
```

### 2. Monitoring Queries
```javascript
// Check database size
db.stats()

// Most active users
db.user_activities.aggregate([
  { $group: { _id: "$user_id", count: { $sum: 1 } } },
  { $sort: { count: -1 } },
  { $limit: 10 }
])

// Most active admins
db.admin_activities.aggregate([
  { $group: { _id: "$admin_id", count: { $sum: 1 } } },
  { $sort: { count: -1 } },
  { $limit: 10 }
])

// Transaction volume by month
db.transactions.aggregate([
  { $group: {
    _id: {
      year: { $year: "$date" },
      month: { $month: "$date" }
    },
    count: { $sum: 1 },
    total_amount: { $sum: "$amount" }
  }},
  { $sort: { "_id.year": -1, "_id.month": -1 } }
])
```

## Troubleshooting

### Common Issues

1. **Connection Issues**
   - Check MongoDB service is running
   - Verify connection string format
   - Check firewall settings

2. **Performance Issues**
   - Ensure indexes are created
   - Monitor slow queries with `db.setProfilingLevel(2)`
   - Consider connection pooling

3. **Authentication Issues**
   - Verify user credentials
   - Check database permissions
   - Validate JWT token configuration

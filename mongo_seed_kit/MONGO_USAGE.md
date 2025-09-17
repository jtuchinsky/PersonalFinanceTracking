# MongoDB Seed Kit - Personal Finance Tracker

## Overview
This directory contains MongoDB seeding tools and database initialization scripts for the Personal Finance Tracker application. These tools help you quickly set up sample data and apply necessary database indexes for development and testing.

## Contents

- **`seed_mongo.py`** - Python script to populate MongoDB with sample data
- **`mongo_indexes.js`** - MongoDB shell script to create indexes and validation
- **Sample Data** - Pre-defined users, accounts, transactions, and categories

## Quick Start

### 1. Prerequisites
- MongoDB 7.0+ running locally, Docker, or Atlas connection
- Python 3.8+ with Motor and pymongo installed
- Database: `personal_finance_tracker`

### 2. Apply Database Indexes (Required)
```bash
# Navigate to seed kit directory
cd mongo_seed_kit

# Apply indexes and validation to database
mongosh personal_finance_tracker < mongo_indexes.js
```

### 3. Seed Sample Data (Optional)
```bash
# Run seeding script
python seed_mongo.py
```

## Sample Data Structure

### Users Created
```json
// Regular User
{
  "email": "john.doe@example.com",
  "name": "John Doe",
  "is_admin": false,
  "account_status": "active"
}

// Admin User
{
  "email": "admin@finance.com",
  "name": "System Administrator",
  "is_admin": true,
  "account_status": "active"
}
```

### Financial Accounts
```javascript
// Checking Account
{
  "name": "Chase Premier Checking",
  "account_type": "checking",
  "bank_name": "Chase",
  "balance": 2500.00
}

// Credit Card
{
  "name": "Chase Freedom Card",
  "account_type": "credit_card",
  "bank_name": "Chase",
  "balance": -876.45
}

// Savings Account
{
  "name": "High Yield Savings",
  "account_type": "savings",
  "bank_name": "Marcus",
  "balance": 15000.00
}
```

### Transaction Categories
```javascript
[
  { "name": "Food & Dining", "color": "#ef4444", "icon": "UtensilsCrossed" },
  { "name": "Transportation", "color": "#3b82f6", "icon": "Car" },
  { "name": "Bills & Utilities", "color": "#f59e0b", "icon": "Receipt" },
  { "name": "Shopping", "color": "#8b5cf6", "icon": "ShoppingBag" },
  { "name": "Entertainment", "color": "#06b6d4", "icon": "Film" },
  { "name": "Healthcare", "color": "#10b981", "icon": "Heart" },
  { "name": "Income", "color": "#059669", "icon": "TrendingUp" },
  { "name": "Other", "color": "#6b7280", "icon": "MoreHorizontal" }
]
```

### Sample Transactions
```javascript
// Expense Transaction
{
  "amount": -45.67,
  "description": "Whole Foods Market",
  "category": "Food & Dining",
  "transaction_type": "debit",
  "date": "2025-09-15T12:30:00Z"
}

// Income Transaction
{
  "amount": 3500.00,
  "description": "Salary Deposit",
  "category": "Income",
  "transaction_type": "credit",
  "date": "2025-09-01T09:00:00Z"
}
```

## Database Indexes Applied

### Primary Indexes
```javascript
// Users collection
db.users.createIndex({ "id": 1 }, { unique: true })
db.users.createIndex({ "email": 1 }, { unique: true })
db.users.createIndex({ "is_admin": 1 })

// Accounts collection
db.accounts.createIndex({ "id": 1 }, { unique: true })
db.accounts.createIndex({ "user_id": 1 })

// Transactions collection
db.transactions.createIndex({ "id": 1 }, { unique: true })
db.transactions.createIndex({ "user_id": 1, "date": -1 })
db.transactions.createIndex({ "account_id": 1 })

// Categories collection
db.categories.createIndex({ "id": 1 }, { unique: true })
db.categories.createIndex({ "user_id": 1 })
```

### Performance Indexes
```javascript
// Compound indexes for efficient queries
db.transactions.createIndex({ "user_id": 1, "category": 1 })
db.transactions.createIndex({ "account_id": 1, "date": -1 })
db.accounts.createIndex({ "user_id": 1, "account_type": 1 })

// Text search indexes
db.transactions.createIndex({
  "description": "text",
  "category": "text"
})
```

## Usage Examples

### Basic Seeding
```bash
# Apply indexes first (always required)
mongosh personal_finance_tracker < mongo_indexes.js

# Seed with sample data
python seed_mongo.py
```

### Custom Environment
```bash
# Use custom MongoDB connection
export MONGO_URL="mongodb://username:password@localhost:27017"
export DB_NAME="custom_finance_db"

python seed_mongo.py
```

### Development Reset
```bash
# Clear existing data and reseed
mongosh personal_finance_tracker --eval "db.dropDatabase()"
mongosh personal_finance_tracker < mongo_indexes.js
python seed_mongo.py
```

## File Details

### `seed_mongo.py`
- Creates sample users with hashed passwords
- Generates realistic financial accounts
- Populates transaction history (30 days)
- Sets up default expense categories
- Handles UUID generation for application IDs

### `mongo_indexes.js`
- Creates unique indexes on ID fields
- Establishes foreign key-style indexes
- Applies compound indexes for performance
- Sets up text search capabilities
- Includes schema validation rules

## Important Notes

### Data Consistency
- All sample data uses UUID strings for application IDs
- Relationships maintained between collections
- Encrypted credentials generated for demo accounts
- Activity logs created for audit trail

### Environment Variables
```bash
# Required environment variables
MONGO_URL=mongodb://localhost:27017
DB_NAME=personal_finance_tracker
JWT_SECRET=your-jwt-secret
ENCRYPTION_KEY=your-32-char-encryption-key
```

### Security Considerations
- Sample passwords are hashed with bcrypt
- Banking credentials encrypted with Fernet
- Demo data includes realistic but fake information
- Admin accounts created with secure defaults

## Verification

### Check Seeded Data
```bash
# Count documents in each collection
mongosh personal_finance_tracker --eval "
  print('Users:', db.users.countDocuments({}));
  print('Accounts:', db.accounts.countDocuments({}));
  print('Transactions:', db.transactions.countDocuments({}));
  print('Categories:', db.categories.countDocuments({}));
"

# Verify indexes
mongosh personal_finance_tracker --eval "
  db.users.getIndexes();
  db.transactions.getIndexes();
"
```

### Test Data Quality
```bash
# Check for orphaned records
mongosh personal_finance_tracker --eval "
  db.transactions.countDocuments({
    account_id: { \$nin: db.accounts.distinct('id') }
  })
"
```

## Related Documentation

- **[MONGODB_SETUP.md](../MONGODB_SETUP.md)** - Complete MongoDB setup guide
- **[README.md](../README.md)** - Project overview and setup
- **[ADMIN_FEATURES.md](../ADMIN_FEATURES.md)** - Admin system documentation

## Troubleshooting

### Common Issues

#### Seeding Script Fails
```bash
# Check MongoDB connection
mongosh personal_finance_tracker --eval "db.stats()"

# Verify environment variables
echo $MONGO_URL
echo $DB_NAME
```

#### Index Creation Errors
```bash
# Drop and recreate indexes
mongosh personal_finance_tracker --eval "
  db.users.dropIndexes();
  db.accounts.dropIndexes();
  db.transactions.dropIndexes();
"

# Reapply indexes
mongosh personal_finance_tracker < mongo_indexes.js
```

#### Duplicate Key Errors
```bash
# Clear existing data before reseeding
mongosh personal_finance_tracker --eval "
  db.users.deleteMany({});
  db.accounts.deleteMany({});
  db.transactions.deleteMany({});
  db.categories.deleteMany({});
"
```

---

**Last Updated**: September 17, 2025
**Database**: personal_finance_tracker
**MongoDB Version**: 7.0+
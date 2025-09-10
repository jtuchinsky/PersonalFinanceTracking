# 🍃 MongoDB Setup & Schema Documentation - Finance Tracker

## Overview
This document provides comprehensive instructions for setting up MongoDB for the Finance Tracker application, including database schema, collections, indexing strategies, and maintenance procedures.

## 📋 Table of Contents
- [MongoDB Installation & Setup](#mongodb-installation--setup)
- [Database Configuration](#database-configuration)
- [Application Schema](#application-schema)
- [Collections Overview](#collections-overview)
- [Data Relationships](#data-relationships)
- [Indexing Strategy](#indexing-strategy)
- [Sample Data Structures](#sample-data-structures)
- [Backup & Maintenance](#backup--maintenance)
- [Performance Optimization](#performance-optimization)
- [Troubleshooting](#troubleshooting)

## 🚀 MongoDB Installation & Setup

### Local Development Setup

#### **Option 1: MongoDB Community Server**
```bash
# Ubuntu/Debian
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org

# Start MongoDB service
sudo systemctl start mongod
sudo systemctl enable mongod
```

#### **Option 2: Docker Setup**
```bash
# Pull MongoDB Docker image
docker pull mongo:7.0

# Run MongoDB container
docker run -d \
  --name finance-tracker-mongo \
  -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=password \
  -v mongodb_data:/data/db \
  mongo:7.0

# Connect to MongoDB
docker exec -it finance-tracker-mongo mongosh
```

#### **Option 3: MongoDB Atlas (Cloud)**
```bash
# Connection string format
mongodb+srv://<username>:<password>@<cluster>.mongodb.net/<database>?retryWrites=true&w=majority
```

### Environment Configuration

#### **Backend Environment Variables**
```bash
# /app/backend/.env
MONGO_URL=mongodb://localhost:27017
DB_NAME=finance_tracker
MONGO_USERNAME=admin
MONGO_PASSWORD=password
```

#### **Connection String Examples**
```bash
# Local MongoDB
MONGO_URL=mongodb://localhost:27017

# MongoDB with Authentication
MONGO_URL=mongodb://username:password@localhost:27017

# MongoDB Atlas
MONGO_URL=mongodb+srv://username:password@cluster0.mongodb.net/finance_tracker?retryWrites=true&w=majority

# Docker MongoDB
MONGO_URL=mongodb://admin:password@localhost:27017
```

## 🗄️ Database Configuration

### Database Structure
```
Database: finance_tracker
├── users                    # User accounts and authentication
├── accounts                 # Financial accounts (bank, credit cards)
├── transactions            # Financial transactions
├── categories              # Expense/income categories
├── account_credentials     # Encrypted banking credentials
├── user_activities         # System activity logs
└── email_logs              # Email notification logs (optional)
```

### Connection Setup in Application
```python
# Backend connection (server.py)
from motor.motor_asyncio import AsyncIOMotorClient
import os

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'finance_tracker')]
```

## 📊 Application Schema

### 1. Users Collection

#### **Schema Structure**
```javascript
{
  "_id": ObjectId("..."),
  "id": "uuid-string",                    // Application UUID
  "email": "user@example.com",           // Unique email address
  "name": "John Doe",                     // Full name
  "password": "hashed_password",          // Bcrypt hashed password
  "is_admin": false,                      // Admin role flag
  "account_status": "active",             // active | locked | deleted
  "last_login": ISODate("..."),           // Last login timestamp
  "created_at": ISODate("..."),           // Account creation date
  "updated_at": ISODate("...")            // Last update timestamp
}
```

#### **Validation Rules**
```javascript
// MongoDB Schema Validation
db.createCollection("users", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["id", "email", "name", "password", "created_at"],
      properties: {
        id: { bsonType: "string" },
        email: { bsonType: "string", pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$" },
        name: { bsonType: "string", minLength: 1 },
        password: { bsonType: "string", minLength: 6 },
        is_admin: { bsonType: "bool" },
        account_status: { enum: ["active", "locked", "deleted"] },
        last_login: { bsonType: "date" },
        created_at: { bsonType: "date" },
        updated_at: { bsonType: "date" }
      }
    }
  }
})
```

### 2. Accounts Collection

#### **Schema Structure**
```javascript
{
  "_id": ObjectId("..."),
  "id": "uuid-string",                    // Application UUID
  "user_id": "user-uuid",                 // Reference to users.id
  "name": "Chase Freedom Card",           // Account display name
  "account_type": "credit_card",          // checking | savings | credit_card
  "bank_name": "Chase",                   // Financial institution
  "balance": 1250.75,                     // Current balance (Number)
  "nickname": "Rewards Card",             // User-defined nickname
  "description": "Main rewards card",     // Account description
  "is_default": false,                    // System-created flag
  "created_at": ISODate("..."),           // Account creation date
  "updated_at": ISODate("...")            // Last update timestamp
}
```

#### **Account Types**
```javascript
// Supported account types
const ACCOUNT_TYPES = [
  "checking",      // Bank checking account
  "savings",       // Bank savings account  
  "credit_card"    // Credit card account
];
```

### 3. Transactions Collection

#### **Schema Structure**
```javascript
{
  "_id": ObjectId("..."),
  "id": "uuid-string",                    // Application UUID
  "user_id": "user-uuid",                 // Reference to users.id
  "account_id": "account-uuid",           // Reference to accounts.id
  "amount": -45.67,                       // Transaction amount (+ income, - expense)
  "description": "Grocery Store",         // Transaction description
  "category": "Food & Dining",            // Expense/income category
  "transaction_type": "debit",            // debit | credit
  "date": ISODate("..."),                 // Transaction date
  "created_at": ISODate("..."),           // Record creation date
  "updated_at": ISODate("...")            // Last update timestamp
}
```

#### **Transaction Types**
```javascript
// Transaction types
const TRANSACTION_TYPES = {
  "debit": "Money going out (expenses)",
  "credit": "Money coming in (income)"
};
```

### 4. Categories Collection

#### **Schema Structure**
```javascript
{
  "_id": ObjectId("..."),
  "id": "uuid-string",                    // Application UUID
  "user_id": "user-uuid",                 // Reference to users.id (null for system categories)
  "name": "Food & Dining",                // Category name
  "color": "#ef4444",                     // Hex color code
  "icon": "UtensilsCrossed",              // Lucide icon name
  "is_system": true,                      // System-created category flag
  "created_at": ISODate("..."),           // Category creation date
  "updated_at": ISODate("...")            // Last update timestamp
}
```

#### **Default Categories**
```javascript
const DEFAULT_CATEGORIES = [
  { name: "Food & Dining", color: "#ef4444", icon: "UtensilsCrossed" },
  { name: "Transportation", color: "#3b82f6", icon: "Car" },
  { name: "Bills & Utilities", color: "#f59e0b", icon: "Receipt" },
  { name: "Shopping", color: "#8b5cf6", icon: "ShoppingBag" },
  { name: "Entertainment", color: "#06b6d4", icon: "Film" },
  { name: "Healthcare", color: "#10b981", icon: "Heart" },
  { name: "Income", color: "#059669", icon: "TrendingUp" },
  { name: "Other", color: "#6b7280", icon: "MoreHorizontal" }
];
```

### 5. Account Credentials Collection

#### **Schema Structure**
```javascript
{
  "_id": ObjectId("..."),
  "account_id": "account-uuid",           // Reference to accounts.id
  "user_id": "user-uuid",                 // Reference to users.id
  "encrypted_username": "encrypted_data", // Fernet encrypted username
  "encrypted_password": "encrypted_data", // Fernet encrypted password
  "created_at": ISODate("..."),           // Credential creation date
  "updated_at": ISODate("...")            // Last update timestamp
}
```

#### **Encryption Details**
```python
# Encryption implementation
from cryptography.fernet import Fernet
import base64

# Generate encryption key
ENCRYPTION_KEY = "your-32-char-key-here"
fernet_key = base64.urlsafe_b64encode(ENCRYPTION_KEY.ljust(32)[:32].encode())
cipher_suite = Fernet(fernet_key)

# Encrypt credentials
def encrypt_credential(credential: str) -> str:
    return cipher_suite.encrypt(credential.encode()).decode()

# Decrypt credentials  
def decrypt_credential(encrypted_credential: str) -> str:
    return cipher_suite.decrypt(encrypted_credential.encode()).decode()
```

### 6. User Activities Collection

#### **Schema Structure**
```javascript
{
  "_id": ObjectId("..."),
  "id": "uuid-string",                    // Application UUID
  "user_id": "user-uuid",                 // Reference to users.id
  "action": "login",                      // Action type
  "details": "User logged in successfully", // Action details
  "ip_address": "192.168.1.100",         // User IP address (optional)
  "user_agent": "Mozilla/5.0...",        // User agent string (optional)
  "timestamp": ISODate("..."),            // Action timestamp
  "metadata": {                           // Additional action data
    "browser": "Chrome",
    "os": "Windows",
    "location": "New York, US"
  }
}
```

#### **Activity Types**
```javascript
const ACTIVITY_TYPES = [
  // Authentication
  "login", "logout", "failed_login", "login_blocked",
  
  // Account Management
  "account_created", "account_updated", "account_deleted",
  "account_locked", "account_unlocked",
  
  // Transactions
  "transaction_created", "transaction_updated", "transaction_deleted",
  
  // Admin Actions
  "admin_login", "admin_view_users", "admin_view_stats",
  "admin_lock_user", "admin_unlock_user", "admin_delete_user",
  
  // System Events
  "system_backup", "system_maintenance", "system_error"
];
```

## 🔗 Data Relationships

### Entity Relationship Diagram
```
Users (1) ←→ (N) Accounts
Users (1) ←→ (N) Transactions  
Users (1) ←→ (N) Categories
Users (1) ←→ (N) User_Activities
Accounts (1) ←→ (N) Transactions
Accounts (1) ←→ (1) Account_Credentials
Categories (1) ←→ (N) Transactions
```

### Reference Integrity
```javascript
// Foreign key relationships
{
  "transactions.user_id": "users.id",
  "transactions.account_id": "accounts.id", 
  "accounts.user_id": "users.id",
  "categories.user_id": "users.id",
  "account_credentials.user_id": "users.id",
  "account_credentials.account_id": "accounts.id",
  "user_activities.user_id": "users.id"
}
```

## 📈 Indexing Strategy

### Primary Indexes
```javascript
// Users collection
db.users.createIndex({ "id": 1 }, { unique: true })
db.users.createIndex({ "email": 1 }, { unique: true })
db.users.createIndex({ "is_admin": 1 })
db.users.createIndex({ "account_status": 1 })

// Accounts collection  
db.accounts.createIndex({ "id": 1 }, { unique: true })
db.accounts.createIndex({ "user_id": 1 })
db.accounts.createIndex({ "account_type": 1 })

// Transactions collection
db.transactions.createIndex({ "id": 1 }, { unique: true })
db.transactions.createIndex({ "user_id": 1 })
db.transactions.createIndex({ "account_id": 1 })
db.transactions.createIndex({ "date": -1 })
db.transactions.createIndex({ "category": 1 })
db.transactions.createIndex({ "transaction_type": 1 })

// Categories collection
db.categories.createIndex({ "id": 1 }, { unique: true })
db.categories.createIndex({ "user_id": 1 })
db.categories.createIndex({ "name": 1 })

// Account credentials collection
db.account_credentials.createIndex({ "account_id": 1 }, { unique: true })
db.account_credentials.createIndex({ "user_id": 1 })

// User activities collection
db.user_activities.createIndex({ "user_id": 1 })
db.user_activities.createIndex({ "timestamp": -1 })
db.user_activities.createIndex({ "action": 1 })
```

### Compound Indexes
```javascript
// Optimized query indexes
db.transactions.createIndex({ "user_id": 1, "date": -1 })
db.transactions.createIndex({ "user_id": 1, "category": 1 })
db.transactions.createIndex({ "account_id": 1, "date": -1 })
db.accounts.createIndex({ "user_id": 1, "account_type": 1 })
db.user_activities.createIndex({ "user_id": 1, "timestamp": -1 })
```

### Text Search Indexes
```javascript
// Full-text search capabilities
db.transactions.createIndex({ 
  "description": "text", 
  "category": "text" 
})

db.users.createIndex({ 
  "name": "text", 
  "email": "text" 
})
```

## 💾 Sample Data Structures

### Sample User Document
```javascript
{
  "_id": ObjectId("64f1234567890abcdef12345"),
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "email": "john.doe@example.com",
  "name": "John Doe",
  "password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/lewih5i7gOGYDz1ma",
  "is_admin": false,
  "account_status": "active",
  "last_login": ISODate("2025-09-10T18:30:00.000Z"),
  "created_at": ISODate("2025-09-01T10:00:00.000Z"),
  "updated_at": ISODate("2025-09-10T18:30:00.000Z")
}
```

### Sample Account Document
```javascript
{
  "_id": ObjectId("64f1234567890abcdef12346"),
  "id": "550e8400-e29b-41d4-a716-446655440002",
  "user_id": "550e8400-e29b-41d4-a716-446655440001",
  "name": "Chase Freedom Credit Card",
  "account_type": "credit_card",
  "bank_name": "Chase",
  "balance": -876.45,
  "nickname": "Rewards Card",
  "description": "Main credit card for rewards and daily expenses",
  "is_default": false,
  "created_at": ISODate("2025-09-01T10:15:00.000Z"),
  "updated_at": ISODate("2025-09-10T14:20:00.000Z")
}
```

### Sample Transaction Document
```javascript
{
  "_id": ObjectId("64f1234567890abcdef12347"),
  "id": "550e8400-e29b-41d4-a716-446655440003",
  "user_id": "550e8400-e29b-41d4-a716-446655440001",
  "account_id": "550e8400-e29b-41d4-a716-446655440002",
  "amount": -45.67,
  "description": "Whole Foods Market",
  "category": "Food & Dining",
  "transaction_type": "debit",
  "date": ISODate("2025-09-10T12:30:00.000Z"),
  "created_at": ISODate("2025-09-10T12:35:00.000Z"),
  "updated_at": ISODate("2025-09-10T12:35:00.000Z")
}
```

## 🛠 Database Initialization Script

### Setup Script
```javascript
// MongoDB initialization script
// Run in MongoDB shell: mongosh finance_tracker < init_db.js

use finance_tracker;

// Create collections with validation
db.createCollection("users", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["id", "email", "name", "password", "created_at"],
      properties: {
        id: { bsonType: "string" },
        email: { bsonType: "string" },
        name: { bsonType: "string" },
        password: { bsonType: "string" },
        is_admin: { bsonType: "bool" },
        account_status: { enum: ["active", "locked", "deleted"] }
      }
    }
  }
});

// Create indexes
db.users.createIndex({ "id": 1 }, { unique: true });
db.users.createIndex({ "email": 1 }, { unique: true });

db.accounts.createIndex({ "id": 1 }, { unique: true });
db.accounts.createIndex({ "user_id": 1 });

db.transactions.createIndex({ "id": 1 }, { unique: true });
db.transactions.createIndex({ "user_id": 1, "date": -1 });

db.categories.createIndex({ "id": 1 }, { unique: true });
db.categories.createIndex({ "user_id": 1 });

db.user_activities.createIndex({ "user_id": 1, "timestamp": -1 });

print("Database initialized successfully!");
```

### Environment Setup Script
```bash
#!/bin/bash
# setup_mongodb.sh

# Create data directory
mkdir -p /data/db

# Start MongoDB service
sudo systemctl start mongod

# Wait for MongoDB to start
sleep 5

# Initialize database
mongosh finance_tracker < init_db.js

# Create backup directory
mkdir -p /backup/mongodb

echo "MongoDB setup completed!"
```

## 🔄 Backup & Maintenance

### Backup Procedures

#### **Full Database Backup**
```bash
# Create full backup
mongodump --db finance_tracker --out /backup/mongodb/$(date +%Y%m%d_%H%M%S)

# Compressed backup
mongodump --db finance_tracker --gzip --out /backup/mongodb/$(date +%Y%m%d_%H%M%S)

# Backup with authentication
mongodump --db finance_tracker --username admin --password password --authenticationDatabase admin --out /backup/mongodb/$(date +%Y%m%d_%H%M%S)
```

#### **Collection-Specific Backup**
```bash
# Backup specific collections
mongodump --db finance_tracker --collection users --out /backup/mongodb/users_$(date +%Y%m%d)
mongodump --db finance_tracker --collection transactions --out /backup/mongodb/transactions_$(date +%Y%m%d)
```

#### **Automated Backup Script**
```bash
#!/bin/bash
# backup_mongodb.sh

BACKUP_DIR="/backup/mongodb"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="finance_tracker"

# Create backup directory
mkdir -p $BACKUP_DIR

# Perform backup
mongodump --db $DB_NAME --gzip --out $BACKUP_DIR/$DATE

# Remove backups older than 30 days
find $BACKUP_DIR -type d -mtime +30 -exec rm -rf {} \;

# Log backup completion
echo "$(date): Database backup completed - $BACKUP_DIR/$DATE" >> /var/log/mongodb_backup.log
```

### Restore Procedures

#### **Full Database Restore**
```bash
# Restore full database
mongorestore --db finance_tracker /backup/mongodb/20250910_180000/finance_tracker/

# Restore with drop existing
mongorestore --db finance_tracker --drop /backup/mongodb/20250910_180000/finance_tracker/

# Restore compressed backup
mongorestore --db finance_tracker --gzip /backup/mongodb/20250910_180000/finance_tracker/
```

#### **Collection-Specific Restore**
```bash
# Restore specific collection
mongorestore --db finance_tracker --collection users /backup/mongodb/users_20250910/finance_tracker/users.bson
```

### Maintenance Tasks

#### **Database Statistics**
```javascript
// Get database statistics
use finance_tracker;
db.stats();

// Collection statistics
db.users.stats();
db.transactions.stats();
db.accounts.stats();

// Index usage statistics
db.transactions.aggregate([{ $indexStats: {} }]);
```

#### **Data Cleanup Scripts**
```javascript
// Remove old activity logs (older than 90 days)
db.user_activities.deleteMany({
  timestamp: {
    $lt: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000)
  }
});

// Remove deleted user data (after 30 days)
db.users.deleteMany({
  account_status: "deleted",
  updated_at: {
    $lt: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)
  }
});
```

## ⚡ Performance Optimization

### Query Optimization

#### **Efficient Queries**
```javascript
// Good: Use indexes
db.transactions.find({ user_id: "user-id" }).sort({ date: -1 }).limit(10);

// Good: Compound index usage
db.transactions.find({ 
  user_id: "user-id", 
  date: { $gte: ISODate("2025-01-01") }
}).sort({ date: -1 });

// Bad: Full collection scan
db.transactions.find({ description: /grocery/i });

// Better: Use text index
db.transactions.find({ $text: { $search: "grocery" } });
```

#### **Aggregation Optimization**
```javascript
// Monthly spending by category
db.transactions.aggregate([
  { $match: { 
    user_id: "user-id",
    transaction_type: "debit",
    date: { $gte: ISODate("2025-09-01") }
  }},
  { $group: {
    _id: "$category",
    total: { $sum: { $abs: "$amount" } },
    count: { $sum: 1 }
  }},
  { $sort: { total: -1 } }
]);
```

### Connection Pool Configuration
```python
# Optimized connection settings
from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient(
    mongo_url,
    maxPoolSize=50,
    minPoolSize=10,
    maxIdleTimeMS=30000,
    waitQueueTimeoutMS=5000,
    serverSelectionTimeoutMS=30000
)
```

### Memory Management
```javascript
// MongoDB configuration (mongod.conf)
storage:
  wiredTiger:
    engineConfig:
      cacheSizeGB: 4
      
operationProfiling:
  slowOpThresholdMs: 100
  mode: slowOp
```

## 🔍 Monitoring & Analytics

### Database Monitoring
```javascript
// Current operations
db.currentOp();

// Connection statistics
db.serverStatus().connections;

// Query performance
db.setProfilingLevel(2);
db.system.profile.find().sort({ ts: -1 }).limit(5);
```

### Application Metrics
```python
# Python monitoring script
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def get_database_stats():
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    stats = {
        'total_users': await db.users.count_documents({}),
        'active_users': await db.users.count_documents({'account_status': 'active'}),
        'total_transactions': await db.transactions.count_documents({}),
        'total_accounts': await db.accounts.count_documents({}),
        'database_size': await db.command('dbStats')
    }
    
    return stats
```

## 🚨 Troubleshooting

### Common Issues

#### **Connection Problems**
```bash
# Check MongoDB service status
sudo systemctl status mongod

# Check port availability
netstat -tulpn | grep 27017

# Test connection
mongosh --host localhost --port 27017

# Check MongoDB logs
sudo tail -f /var/log/mongodb/mongod.log
```

#### **Performance Issues**
```javascript
// Check slow queries
db.setProfilingLevel(2, { slowms: 100 });
db.system.profile.find({ ts: { $gte: new Date(Date.now() - 3600000) } }).sort({ ts: -1 });

// Check index usage
db.transactions.explain("executionStats").find({ user_id: "user-id" });

// Analyze collection performance
db.transactions.stats();
```

#### **Storage Issues**
```bash
# Check disk space
df -h

# Check MongoDB data directory size
du -sh /var/lib/mongodb

# Compact collections (if needed)
db.runCommand({ compact: "transactions" });
```

### Error Resolution

#### **Authentication Errors**
```javascript
// Create admin user
use admin;
db.createUser({
  user: "admin",
  pwd: "password",
  roles: ["root"]
});

// Update user permissions
db.updateUser("admin", {
  roles: ["root"]
});
```

#### **Index Errors**
```javascript
// Rebuild indexes
db.transactions.reIndex();

// Drop problematic index
db.transactions.dropIndex("problem_index_name");

// Recreate index
db.transactions.createIndex({ "user_id": 1, "date": -1 });
```

## 📚 Best Practices

### Data Modeling
- **Use UUIDs** for application-level unique identifiers
- **Embed related data** that is frequently accessed together
- **Reference large documents** to avoid document size limits
- **Design for read patterns** - optimize for your most common queries

### Security
- **Enable authentication** in production environments
- **Use connection encryption** (TLS/SSL)
- **Implement role-based access control**
- **Encrypt sensitive data** at the application level

### Performance
- **Create appropriate indexes** for your query patterns
- **Use compound indexes** for multi-field queries
- **Monitor slow queries** and optimize them
- **Implement connection pooling** in your application

### Maintenance
- **Regular backups** with automated scheduling
- **Monitor disk space** and plan for growth
- **Archive old data** to maintain performance
- **Update MongoDB** regularly for security and performance improvements

---

## 🎯 Summary

This MongoDB setup provides a robust foundation for the Finance Tracker application with:

- **Scalable Schema Design** - Optimized for financial data management
- **Comprehensive Indexing** - Fast queries across all access patterns  
- **Security Features** - Encrypted credentials and admin controls
- **Monitoring & Maintenance** - Automated backups and performance tracking
- **Documentation** - Complete reference for all database aspects

The database is designed to handle the full lifecycle of financial data while maintaining performance, security, and data integrity.

---

**Last Updated**: September 10, 2025  
**Version**: 1.0  
**Database Version**: MongoDB 7.0+  
**Author**: Finance Tracker Development Team
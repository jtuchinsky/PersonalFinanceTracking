# Personal Finance Tracker - Database Schema

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
│ is_admin           │         │ ip_address         │
│ account_status     │         │ timestamp          │
│ last_login         │         └─────────────────────┘
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
```
{
  "id": "uuid4",
  "email": "user@example.com",
  "name": "John Doe",
  "password": "hashed_password_with_bcrypt",
  "is_admin": false,
  "account_status": "active|locked|deleted",
  "last_login": "2024-01-01T00:00:00Z",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### 2. accounts
**Purpose**: Store financial account information
```
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

### 3. transactions
**Purpose**: Store financial transactions
```
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

### 4. categories
**Purpose**: Store expense/income categories
```
{
  "id": "uuid4",
  "name": "Food & Dining",
  "color": "#FF6B6B",
  "icon": "utensils"
}
```

### 5. account_credentials
**Purpose**: Store encrypted banking login credentials
```
{
  "id": "uuid4",
  "account_id": "account_uuid4",
  "username": "encrypted_username",
  "password": "encrypted_password",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### 6. user_activities
**Purpose**: Audit log for user and admin actions
```
{
  "id": "uuid4",
  "user_id": "user_uuid4",
  "action": "login|logout|create_account|admin_action",
  "details": "User logged in successfully",
  "ip_address": "192.168.1.100",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## Relationships

1. **users → accounts** (1:N): One user can have multiple financial accounts
2. **users → transactions** (1:N): One user can have multiple transactions
3. **users → user_activities** (1:N): One user can have multiple activity log entries
4. **accounts → transactions** (1:N): One account can have multiple transactions
5. **accounts → account_credentials** (1:1): Each account has one set of encrypted credentials
6. **categories → transactions** (1:N): One category can be used by multiple transactions

## Indexes (Production)

```javascript
// Performance indexes for MongoDB
db.users.createIndex({ "email": 1 }, { unique: true })
db.users.createIndex({ "is_admin": 1 })
db.accounts.createIndex({ "user_id": 1 })
db.transactions.createIndex({ "user_id": 1 })
db.transactions.createIndex({ "account_id": 1 })
db.transactions.createIndex({ "date": -1 })
db.user_activities.createIndex({ "user_id": 1 })
db.user_activities.createIndex({ "timestamp": -1 })
db.account_credentials.createIndex({ "account_id": 1 }, { unique: true })
```

## Security Features

- **Password Hashing**: User passwords are hashed using bcrypt
- **Credential Encryption**: Banking credentials are encrypted using Fernet symmetric encryption
- **JWT Authentication**: Stateless authentication using JWT tokens
- **Admin Separation**: Admin functions are isolated in separate server/endpoints
- **Activity Logging**: All user and admin actions are logged for auditing

## Data Flow

1. **User Registration**: Creates user record with hashed password
2. **Account Creation**: Creates account record + encrypted credentials
3. **Transaction Creation**: Updates account balance and creates transaction record
4. **Admin Actions**: All admin operations are logged in user_activities
5. **Authentication**: JWT tokens reference user.id for session management
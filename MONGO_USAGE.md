# 🍃 MongoDB Usage Guide for Finance Tracker

This document provides comprehensive guidance for managing MongoDB collections, admin accounts, and advanced features in the Finance Tracker application.

## 📋 Table of Contents

- [Database Setup](#database-setup)
- [Admin Account Management](#admin-account-management)
- [Two-Factor Authentication (2FA)](#two-factor-authentication-2fa)
- [Database Collections](#database-collections)
- [Security Features](#security-features)
- [Maintenance & Operations](#maintenance--operations)
- [Troubleshooting](#troubleshooting)

## 🚀 Database Setup

### Initial Setup

1. **Install MongoDB Dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables**
   ```bash
   # Create .env file in backend directory
   MONGO_URL=mongodb://localhost:27017
   DB_NAME=finance_tracker
   JWT_SECRET=your-jwt-secret-key
   ENCRYPTION_KEY=your-encryption-key
   ```

3. **Seed Database with Initial Data**
   ```bash
   cd mongo_seed_kit
   export MONGODB_URI="your_mongodb_connection_string"
   python seed_mongo.py --db finance_tracker --force
   ```

## 👑 Admin Account Management

### Admin Creation Methods

#### Method 1: Basic Admin Creation
```bash
cd backend
python create_admin.py create
```

#### Method 2: Advanced Admin Creation (Recommended)
```bash
cd backend
python create_admin_advanced.py create
```

#### Method 3: Admin with 2FA (Most Secure)
```bash
cd backend
python create_admin_advanced.py create --with-2fa
```

### Admin Management Commands

#### List All Admin Accounts
```bash
python create_admin_advanced.py list
```

Example output:
```
Status   Email                      Name                Role         2FA   Created
🟢       admin@example.com          System Admin        super_admin  ✅    2025-09-27 10:30
🟢       manager@company.com        Manager User        admin        ❌    2025-09-27 11:15
```

#### Enable 2FA for Existing Admin
```bash
python create_admin_advanced.py enable-2fa admin@example.com
```

#### Disable 2FA for Admin
```bash
python create_admin_advanced.py disable-2fa admin@example.com
```

### Admin Roles and Permissions

| Role | Permissions | Description |
|------|-------------|-------------|
| `admin` | user_management, system_stats, view_activities | Standard admin with user management capabilities |
| `super_admin` | All admin permissions + admin_management, system_config | Full system administration access |

## 🔐 Two-Factor Authentication (2FA)

### 2FA Features

- **TOTP Support**: Compatible with Google Authenticator, Authy, Microsoft Authenticator
- **QR Code Setup**: Easy authenticator app configuration
- **Backup Codes**: 8 single-use recovery codes
- **Progressive Authentication**: 2FA only required when enabled

### 2FA Setup Process

1. **Admin creates account with 2FA**:
   ```bash
   python create_admin_advanced.py create --with-2fa
   ```

2. **System generates**:
   - TOTP secret key
   - QR code for authenticator apps
   - 8 backup recovery codes

3. **Admin configures authenticator app**:
   - Scan QR code or manually enter secret
   - Verify with test code

4. **Admin saves backup codes securely**

### 2FA Database Fields

```javascript
// Admin document structure with 2FA
{
  "id": "uuid4-string",
  "email": "admin@example.com",
  "name": "Admin Name",
  "role": "admin",
  "two_factor_enabled": true,
  "two_factor_secret": "base32-encoded-secret",
  "backup_codes": ["ABC123DE", "FGH456IJ", ...],
  "account_status": "active",
  "created_at": ISODate,
  "updated_at": ISODate
}
```

### 2FA API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/admin/2fa/setup` | POST | Initialize 2FA setup |
| `/api/admin/2fa/verify` | POST | Verify and enable 2FA |
| `/api/admin/2fa/disable` | POST | Disable 2FA |
| `/api/admin/2fa/status` | GET | Get 2FA status |
| `/api/admin/2fa/regenerate-backup-codes` | POST | Generate new backup codes |

## 🗃️ Database Collections

### Core Collections

#### `admins` - Admin Accounts
```javascript
{
  "id": "uuid4",
  "email": "admin@example.com",
  "name": "Admin Name",
  "role": "admin|super_admin",
  "permissions": ["user_management", "system_stats"],
  "account_status": "active|locked|deleted",
  "two_factor_enabled": boolean,
  "two_factor_secret": "secret|null",
  "backup_codes": ["code1", "code2"] | null,
  "last_login": ISODate | null,
  "created_by": "admin_id" | null,
  "created_at": ISODate,
  "updated_at": ISODate
}
```

#### `users` - User Accounts
```javascript
{
  "id": "uuid4",
  "email": "user@example.com",
  "name": "User Name",
  "tenant_id": "tenant_id" | null,
  "role": "user|tenant_admin",
  "account_status": "active|locked|deleted",
  "two_factor_enabled": boolean,
  "last_login": ISODate | null,
  "created_at": ISODate,
  "updated_at": ISODate
}
```

### Multi-Tenant Collections

#### `tenants` - Organizational Tenants
```javascript
{
  "id": "uuid4",
  "name": "Company Name",
  "description": "Company description",
  "owner_admin_id": "admin_id",
  "status": "active|suspended|deleted",
  "created_at": ISODate,
  "updated_at": ISODate
}
```

#### `user_invitations` - User Invitation System
```javascript
{
  "id": "uuid4",
  "email": "newuser@example.com",
  "tenant_id": "tenant_id",
  "role": "user|tenant_admin",
  "invited_by_admin_id": "admin_id",
  "status": "pending|accepted|expired|cancelled",
  "invitation_token": "secure_token",
  "expires_at": ISODate,
  "created_at": ISODate,
  "accepted_at": ISODate | null
}
```

### Audit & Monitoring Collections

#### `admin_activities` - Admin Action Logs
```javascript
{
  "id": "uuid4",
  "admin_id": "admin_id",
  "action": "admin_login|user_locked|2fa_enabled",
  "details": "Descriptive action details",
  "target_user_id": "user_id" | null,
  "ip_address": "192.168.1.1" | null,
  "timestamp": ISODate
}
```

#### `user_activities` - User Action Logs
```javascript
{
  "id": "uuid4",
  "user_id": "user_id",
  "action": "login|transaction_created|account_added",
  "details": "Action description",
  "ip_address": "192.168.1.1" | null,
  "timestamp": ISODate
}
```

### Connection & Data Management Collections

#### `sync_jobs` - Connection Sync Jobs
```javascript
{
  "id": "uuid4",
  "connection_id": "connection_id",
  "user_id": "user_id",
  "job_type": "manual|scheduled|retry",
  "status": "pending|running|completed|failed",
  "started_at": ISODate | null,
  "completed_at": ISODate | null,
  "error_message": "error_details" | null,
  "items_synced": 0,
  "created_at": ISODate
}
```

#### `data_integrity_checks` - Data Quality Checks
```javascript
{
  "id": "uuid4",
  "check_type": "duplicates|orphaned_transactions|balance_mismatch",
  "tenant_id": "tenant_id" | null,
  "status": "running|completed|failed",
  "issues_found": 0,
  "issues_resolved": 0,
  "details": { "check_specific_data": "..." },
  "created_by": "admin_id",
  "created_at": ISODate,
  "completed_at": ISODate | null
}
```

## 🔒 Security Features

### Authentication & Authorization

1. **JWT Tokens**: Secure token-based authentication
2. **Role-Based Access**: Admin and user roles with specific permissions
3. **2FA Protection**: Optional TOTP-based two-factor authentication
4. **Session Management**: Tracked user sessions with expiration

### Data Protection

1. **Password Hashing**: bcrypt with salt for all passwords
2. **Credential Encryption**: Fernet symmetric encryption for banking data
3. **Admin Separation**: Admins stored in separate collection from users
4. **Activity Logging**: Comprehensive audit trails for compliance

### Security Best Practices

1. **Environment Variables**: All secrets stored in environment variables
2. **Input Validation**: Pydantic models for request/response validation
3. **Database Indexes**: Optimized queries with proper indexing
4. **CORS Configuration**: Controlled cross-origin resource sharing

## 🛠️ Maintenance & Operations

### Database Indexes

Critical indexes for performance:

```javascript
// Admin collection indexes
db.admins.createIndex({"email": 1}, {unique: true})
db.admins.createIndex({"id": 1}, {unique: true})

// User collection indexes
db.users.createIndex({"email": 1}, {unique: true})
db.users.createIndex({"tenant_id": 1})

// Activity indexes
db.admin_activities.createIndex({"admin_id": 1, "timestamp": -1})
db.user_activities.createIndex({"user_id": 1, "timestamp": -1})

// Invitation indexes
db.user_invitations.createIndex({"email": 1, "tenant_id": 1})
db.user_invitations.createIndex({"invitation_token": 1}, {unique: true})
```

### Regular Maintenance Tasks

#### Weekly Tasks
- Review admin activity logs
- Check failed login attempts
- Monitor system performance

#### Monthly Tasks
- Audit user permissions
- Clean up expired invitations
- Review data integrity checks

#### Backup Procedures
```bash
# Create database backup
mongodump --uri="your_connection_string" --db finance_tracker --out backup_$(date +%Y%m%d)

# Restore from backup
mongorestore --uri="your_connection_string" --db finance_tracker backup_20250927/finance_tracker
```

## 🚨 Troubleshooting

### Common Issues

#### Admin Cannot Login
1. **Check account status**: Ensure admin account is not locked
2. **Verify 2FA codes**: If 2FA enabled, check authenticator app time sync
3. **Password issues**: Use backup codes if 2FA fails
4. **Database connection**: Verify MongoDB connectivity

```bash
# Check admin status
python create_admin_advanced.py list

# Disable 2FA if needed
python create_admin_advanced.py disable-2fa admin@example.com
```

#### 2FA Setup Issues
1. **Time synchronization**: Ensure server and device clocks are synchronized
2. **QR code scanning**: Manual secret entry if QR code fails
3. **Backup codes**: Always save backup codes during setup

#### Database Performance
1. **Check indexes**: Ensure all required indexes exist
2. **Query optimization**: Use MongoDB profiler to identify slow queries
3. **Connection pooling**: Monitor connection usage

### Error Codes and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `Admin not found` | Email doesn't exist | Check email spelling, create admin if needed |
| `Invalid 2FA code` | Time sync or wrong code | Check device time, try backup code |
| `Account locked` | Security lockout | Admin must unlock via database or other admin |
| `Connection failed` | MongoDB unavailable | Check connection string, restart MongoDB |

### Debug Commands

```bash
# Check database connection
python -c "from motor.motor_asyncio import AsyncIOMotorClient; import asyncio; asyncio.run(AsyncIOMotorClient('your_url').admin.command('ping'))"

# List all collections
python -c "from motor.motor_asyncio import AsyncIOMotorClient; import asyncio; print(asyncio.run(AsyncIOMotorClient('your_url').finance_tracker.list_collection_names()))"

# Count admin accounts
python -c "from motor.motor_asyncio import AsyncIOMotorClient; import asyncio; print(asyncio.run(AsyncIOMotorClient('your_url').finance_tracker.admins.count_documents({})))"
```

## 📞 Support & Documentation

### Additional Resources

- **Admin Features Documentation**: `ADMIN_FEATURES.md`
- **API Documentation**: FastAPI auto-generated docs at `/docs`
- **Database Setup**: `MONGODB_SETUP.md`
- **Claude Instructions**: `CLAUDE.md`

### Getting Help

1. **Check logs**: Review application and MongoDB logs
2. **Admin activities**: Check admin_activities collection for audit trail
3. **System status**: Use admin dashboard for system overview
4. **Documentation**: Refer to comprehensive feature documentation

---

**Last Updated**: September 27, 2025
**Version**: 2.3 - Enhanced 2FA and Admin Management
**Author**: Finance Tracker Development Team
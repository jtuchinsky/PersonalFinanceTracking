# 🔐 Finance Tracker Admin System Documentation

## Overview
The Finance Tracker includes a comprehensive admin system that allows administrators to manage users, monitor system activities, and maintain the platform. This document covers all admin features, setup, and usage instructions.

## 🎯 Admin Features

### 🔐 Admin Authentication
- **Secure Admin Login**: JWT-based authentication with admin role verification
- **Database Separation**: Admins stored in separate `admins` collection, completely isolated from users
- **Role-Based Access**: Support for different admin roles (admin, super_admin) with granular permissions
- **Admin Protection**: Cannot delete or modify other admin accounts through the system
- **Separate Servers**: Admin functionality runs on dedicated server (port 8001)

### 📊 Admin Dashboard Features

#### **System Overview**
- **User Statistics**: Total, Active, Locked, and Deleted user counts
- **Account Statistics**: Total financial accounts across all users
- **Transaction Statistics**: Total transactions in the system
- **Real-time Monitoring**: Live system activity feeds

#### **User Management (Privacy-First)**
- **View All Users**: Complete list of all registered users (NO financial data exposed)
- **User Details**: Name, email, account status, tenant affiliation, 2FA status
- **Account Control**: Lock/unlock user accounts
- **Account Deletion**: Permanently delete user accounts
- **Admin Protection**: Prevents modification of other admin accounts
- **Session Monitoring**: View user's active sessions and last login activity
- **2FA Management**: Reset user's two-factor authentication when needed

#### **Activity Monitoring**
- **System Activity Logs**: Complete audit trail of all user and admin actions
- **Real-time Tracking**: Live activity feed with timestamps
- **Action Types**: Login attempts, account modifications, admin actions
- **IP Tracking**: Monitor user locations and access patterns

#### **Email Notification System**
- **Mock Email Service**: Development-friendly email simulation
- **Email Templates**: Pre-built templates for all notification types
- **Email Logging**: Complete log of all sent notifications
- **Notification Types**:
  - Account deletion notifications
  - Account lock/unlock notifications
  - Admin welcome emails

## 🚀 Getting Started

### Admin Account Creation

#### **Method 1: Command-Line Tool (Interactive)**
```bash
cd backend
python create_admin.py create
```

**Interactive Prompts:**
- Email address (must be valid format)
- Full name (for the admin user)
- Password (minimum 8 characters, hidden input)
- Password confirmation

#### **Method 2: Database Seeding (Creates Default Admin)**
```bash
cd mongo_seed_kit
export MONGODB_URI="your_mongodb_connection_string"
python seed_mongo.py --db finance_tracker --force
```

**Default Admin Created:**
- Email: admin@example.com
- Password: Admin#12345
- Role: super_admin

#### **Method 3: List Existing Admins**
```bash
cd backend
python create_admin.py list
```

### Default Admin Account (Created by Seeding)

| Email | Name | Password | Role | Status |
|-------|------|----------|------|--------|
| admin@example.com | System Administrator | Admin#12345 | super_admin | Active |

**Additional Test Accounts:**

| Email | Name | Password | Role | Status |
|-------|------|----------|------|--------|
| user@example.com | John Doe | User#12345 | user | Active |

## 🎨 Admin Interface

### Accessing Admin Panel
1. **Navigate** to admin frontend: http://localhost:3001
2. **Login** with admin credentials (separate from user login)
3. **Admin Dashboard** loads automatically after successful authentication
4. **Dedicated Interface**: Completely separate admin application on port 3001

### Admin Dashboard Layout
- **Header**: Welcome message and logout option
- **Tab Navigation**:
  - Overview (System statistics)
  - User Management (User control)
  - Activity Logs (System monitoring)
  - Email Logs (Notification tracking)
- **Separate Backend**: Admin API runs on dedicated server (port 8001)
- **Security**: Admin routes protected by admin-only JWT tokens

## 👥 User Management

### User Information Display
- **User Details**: Name, email, admin status
- **Account Status**: Active, Locked, or Deleted
- **Financial Summary**: Number of accounts, transactions, total balance
- **Activity Tracking**: Last login date and time

### User Actions

#### **Lock User Account**
```
Action: Restricts user login access
Email: Automatic notification sent to user
Effect: User cannot log in until unlocked
Protection: Cannot lock admin accounts
```

#### **Unlock User Account**
```
Action: Restores user login access
Email: Automatic notification sent to user
Effect: User can log in normally
Logging: Action logged in system activities
```

#### **Delete User Account**
```
Action: Permanently removes user and all data
Email: Notification sent before deletion
Effect: Removes user, accounts, transactions, categories
Protection: Cannot delete admin accounts
Warning: This action cannot be undone
```

## 📧 Email Notification System

### Email Templates

#### **Account Deletion Notification**
```
Subject: Your Finance Tracker Account Has Been Deleted
Content: Informs user of account deletion with details and support contact
```

#### **Account Lock Notification**
```
Subject: Your Finance Tracker Account Has Been Locked
Content: Notifies user of account lock with support information
```

#### **Account Unlock Notification**
```
Subject: Your Finance Tracker Account Has Been Unlocked
Content: Confirms account unlock and restored access
```

#### **Admin Welcome Email**
```
Subject: Welcome to Finance Tracker Admin Panel
Content: Welcome message with admin privileges and responsibilities
```

### Email Logging
- **Complete Tracking**: All sent emails logged with timestamps
- **Email Content**: Full email body and recipient information
- **Status Monitoring**: Delivery status tracking
- **Admin Review**: Email logs accessible through admin panel

## 🏢 User & Tenant Lifecycle Management (NEW)

### Multi-Tenant Architecture
- **Tenant Creation**: Admins can create new organizational tenants
- **Tenant Management**: View and manage all active tenants
- **Isolated Data**: Each tenant's data is completely separated
- **Scalable Design**: Ready for SaaS multi-tenant deployment

### User Invitation System
- **Email Invitations**: Send secure invitation emails to new users
- **Role Assignment**: Assign user roles during invitation (user, tenant_admin)
- **Expiry Management**: Invitations expire after 7 days automatically
- **Resend Capability**: Resend invitations for pending users
- **Token Security**: Unique invitation tokens prevent unauthorized access

### Enhanced User Management
- **Privacy-First Design**: Admins CANNOT see user financial data (balances, amounts)
- **Tenant Filtering**: Filter users by tenant organization
- **Session Monitoring**: View user's active sessions and last login activity
- **2FA Management**: Reset user's two-factor authentication
- **Advanced Security**: Monitor user sessions across devices

### User Lifecycle Features
- **Account Creation**: Create user accounts through invitation system
- **Account Modification**: Lock/unlock user accounts with notifications
- **Account Deletion**: Permanently remove users with complete data cleanup
- **Status Tracking**: Monitor user account status changes over time
- **Audit Compliance**: Complete audit trail for regulatory compliance

### New Email Templates
- **User Invitation**: Welcome new users with secure invitation links
- **Invitation Reminder**: Resend invitations for pending users
- **2FA Reset Notification**: Inform users when 2FA is reset by admin
- **Account Status Changes**: Enhanced notifications for all account changes
- **Bank Re-authentication**: Notify users when bank connections require re-authentication

## 🔗 Connection & Sync Health Management (NEW)

### Bank & Broker Connection Monitoring
- **Connection Overview**: View all user bank and broker connections across the platform
- **Real-time Status**: Monitor connection health, sync status, and error conditions
- **Institution Tracking**: Track connections by financial institution and connection type
- **Privacy-First Design**: View connection metadata without accessing user financial data

### Connection Management Features
- **Manual Sync Trigger**: Force immediate synchronization for troubleshooting
- **Re-authentication Links**: Generate secure re-auth links for expired connections
- **Sync Job History**: View detailed sync job logs and status for each connection
- **Error Monitoring**: Track sync errors and connection failures for proactive support

### Admin Connection Controls
```
Connection Actions Available:
- Manual sync trigger with optional full-sync mode
- Generate secure re-authentication links for users
- View sync job history and status tracking
- Monitor connection health across all users
- Filter connections by tenant, status, or institution
```

### Connection Status Tracking
- **Active Connections**: Healthy, syncing connections
- **Error Connections**: Connections with sync errors or failures
- **Expired Connections**: Connections requiring user re-authentication
- **Disconnected Connections**: Inactive or disabled connections

## 📊 Data Integrity & Quality Management (NEW)

### Automated Integrity Checks
- **Duplicate Detection**: Identify and report duplicate transactions
- **Orphaned Transaction Cleanup**: Find transactions without valid account references
- **Balance Reconciliation**: Detect account balance mismatches
- **Category Validation**: Verify transaction category consistency

### Data Quality Monitoring
- **Real-time Checks**: Run integrity checks on-demand or scheduled
- **Issue Reporting**: Detailed reports of data quality issues found
- **Trend Analysis**: Track data quality improvements over time
- **Compliance Readiness**: Ensure data meets regulatory standards

### Integrity Check Types
```
Available Integrity Checks:
- Duplicates: Find duplicate transactions across accounts
- Orphaned Transactions: Identify transactions without valid accounts
- Balance Mismatch: Detect inconsistencies in account balances
- Category Validation: Verify transaction categorization accuracy
```

### Data Integrity Dashboard
- **Check History**: View all integrity checks with timestamps and results
- **Issue Summary**: Summary of issues found and resolution status
- **Automated Reports**: Detailed reports of data quality metrics
- **Resolution Tracking**: Monitor progress on data quality improvements

## 🔒 Security Features

### Authentication & Authorization
- **JWT Token Security**: Secure token-based authentication
- **Admin Role Verification**: Middleware ensures admin-only access
- **Session Management**: Proper session handling and timeout

### Activity Logging
- **Separate Audit Trails**: User activities and admin activities stored in separate collections
- **User Activities**: Logged in `user_activities` collection
- **Admin Activities**: Logged in `admin_activities` collection with target user tracking
- **Complete Audit Trail**: Every action logged with details
- **User Identification**: User ID/Admin ID and action details recorded
- **Timestamp Tracking**: Precise time logging for all activities
- **IP Address Logging**: Track user locations and access patterns

### Data Protection
- **Admin Account Protection**: Cannot delete or modify other admins
- **Secure Credential Storage**: Encrypted password storage with bcrypt
- **Account Credential Encryption**: User banking credentials encrypted with Fernet

## 📊 System Monitoring

### Statistics Dashboard
- **User Metrics**: Total, active, locked, deleted user counts
- **Financial Metrics**: Total accounts and transactions across platform
- **Activity Metrics**: Recent system activities and trends
- **Performance Indicators**: System health and usage statistics

### Activity Monitoring
```
Activity Types Tracked:
- User login/logout events
- Account lock/unlock actions  
- Account deletion events
- Admin panel access
- User registration events
- Transaction creation/modification
- Account management actions
```

### Real-time Updates
- **Live Activity Feed**: Real-time system activity monitoring
- **Automatic Refresh**: Statistics update automatically
- **Instant Notifications**: Immediate feedback on admin actions

## 🛠 Technical Implementation

### Backend Architecture
- **Split Architecture**: Separate user server (port 8000) and admin server (port 8001)
- **FastAPI Framework**: Modern, fast web framework
- **MongoDB Database**: Document-based data storage with separate collections
- **JWT Authentication**: Secure token-based auth with user_type differentiation
- **Async Operations**: High-performance async/await patterns
- **Shared Modules**: Common database, auth, models, and utilities

### Admin API Endpoints (Port 8001)
```
# Authentication
POST /api/auth/login                        - Admin login (separate from user login)

# Tenant Management (NEW)
POST /api/admin/tenants                     - Create new tenant
GET  /api/admin/tenants                     - List all active tenants

# User Invitation System (NEW)
POST /api/admin/users/invite                - Invite user to join tenant
POST /api/admin/users/invite/{id}/resend    - Resend invitation email

# Enhanced User Management (Privacy-First)
GET  /api/admin/users?tenantId=...          - User list (NO financial data)
POST /api/admin/users/{id}/lock             - Lock user account
POST /api/admin/users/{id}/unlock           - Unlock user account
POST /api/admin/users/{id}/reset-2fa        - Reset user's 2FA
GET  /api/admin/users/{id}/sessions         - View user's active sessions
DELETE /api/admin/users/{id}                - Delete user account

# System Monitoring
GET  /api/admin/stats                       - System statistics
GET  /api/admin/activities                  - Activity logs
GET  /api/admin/emails                      - Email notification logs

# Connection & Sync Management (NEW)
GET  /api/admin/connections?tenantId=...    - Bank/broker connections overview
POST /api/admin/connections/{id}/sync       - Trigger manual sync for connection
POST /api/admin/connections/{id}/reauth-link - Generate re-authentication link
GET  /api/admin/connections/{id}/sync-jobs  - View sync job history

# Data Integrity Management (NEW)
GET  /api/admin/imports?tenantId=...        - Data import job history
POST /api/admin/integrity-checks           - Run data integrity checks
GET  /api/admin/integrity-checks?tenantId=... - View integrity check results
```

### Frontend Architecture
- **Split Applications**: User frontend (port 3000) and admin frontend (port 3001)
- **React Components**: Modern React-based UI
- **Responsive Design**: Mobile-friendly interface
- **Real-time Updates**: Live data updates
- **Professional UI**: Clean, modern admin interface
- **Separate Authentication**: Independent admin login system

## 🔧 Development & Maintenance

### Environment Setup
```bash
# Backend environment variables
MONGO_URL=mongodb://localhost:27017
DB_NAME=finance_tracker
JWT_SECRET=your-secret-key
ENCRYPTION_KEY=your-encryption-key
```

### Database Collections
```
# Core User Management
users               - Regular user accounts (no admin flags)
admins              - Admin accounts with roles and permissions

# Multi-Tenant Support (NEW)
tenants             - Organizational tenants for SaaS model
user_invitations    - Email-based user invitation system
user_sessions       - User session tracking for admin monitoring

# Audit & Compliance
user_activities     - User action audit logs
admin_activities    - Admin action audit logs

# Financial Data (User-Only Access)
accounts           - Financial accounts
transactions       - Financial transactions
categories         - Expense categories
account_credentials - Encrypted banking credentials

# Connection & Data Management (NEW)
sync_jobs          - Sync job tracking and history
import_jobs        - Data import job tracking
data_integrity_checks - Data quality check results
```

### Maintenance Tasks
- **Regular Activity Review**: Monitor system activities for unusual patterns
- **User Account Audits**: Periodic review of user accounts and permissions
- **Email Log Review**: Check email delivery and user communications
- **Performance Monitoring**: System performance and usage statistics

## 🚨 Troubleshooting

### Common Issues

#### **Admin Panel Not Accessible**
```
Solution: Ensure admin account exists in admins collection
Check: Navigate to correct admin frontend URL (port 3001)
Verify: Admin server is running on port 8001
Confirm: Admin login credentials are correct
```

#### **Email Notifications Not Sending**
```
Solution: Check mock email service configuration
Verify: Email templates are properly formatted
Review: Email logs in admin panel for delivery status
```

#### **Command-Line Tool Errors**
```
Solution: Verify MongoDB connection string
Check: Environment variables are properly set
Ensure: Database permissions are correctly configured
```

### Log Files
```bash
# Backend logs
tail -f /var/log/supervisor/backend.*.log

# Frontend logs  
tail -f /var/log/supervisor/frontend.*.log

# System logs
sudo journalctl -u supervisor -f
```

## 📈 Best Practices

### Admin Account Management
- **Strong Passwords**: Use complex passwords for admin accounts
- **Limited Admin Accounts**: Only create necessary admin accounts
- **Regular Audits**: Periodically review admin account access
- **Activity Monitoring**: Regularly check admin activity logs

### User Management
- **Clear Communication**: Always notify users of account changes
- **Documentation**: Document reasons for user account actions
- **Backup Procedures**: Ensure data backup before user deletion
- **Support Process**: Provide clear support channels for users

### Security Practices
- **Regular Reviews**: Periodic security audits
- **Activity Monitoring**: Watch for unusual admin activities
- **Access Control**: Limit admin panel access to authorized personnel
- **Incident Response**: Have procedures for security incidents

## 📞 Support & Documentation

### Admin Support
- **Activity Logs**: Review system activities for troubleshooting
- **Email Logs**: Check email delivery status and content
- **User Feedback**: Monitor user communications and complaints
- **System Health**: Regular monitoring of system performance

### User Support
- **Account Issues**: Help users with locked/deleted accounts
- **Access Problems**: Assist with login and authentication issues
- **Data Recovery**: Support for account restoration when possible
- **General Support**: Provide guidance on platform usage

---

## 🎉 Conclusion

The Finance Tracker Admin System provides comprehensive tools for platform management, user oversight, and system monitoring. With features ranging from user account management to detailed activity logging, administrators have complete control over the platform while maintaining security and user privacy.

The system is designed to be intuitive, secure, and scalable, providing administrators with all the tools needed to effectively manage the Finance Tracker platform.

---

**Last Updated**: September 26, 2025
**Version**: 2.2 - Complete Admin System with Connection & Data Management
**Author**: Finance Tracker Development Team

### 🆕 Version 2.2 Features (NEW)
- **Connection & Sync Health Management**: Complete bank/broker connection monitoring and control
- **Data Integrity & Quality Management**: Automated data quality checks and monitoring
- **Manual Sync Control**: Admin-triggered synchronization for troubleshooting
- **Re-authentication Management**: Secure link generation for expired connections
- **Comprehensive Data Validation**: Multi-type integrity checks for data quality assurance

### 🔄 Version 2.1 Features
- **Multi-Tenant Architecture**: Full SaaS-ready tenant management system
- **User Invitation System**: Email-based secure user invitations with expiry
- **Privacy-First User Management**: Admin interfaces with zero financial data exposure
- **Enhanced Session Monitoring**: Real-time user session tracking across devices
- **2FA Management**: Admin capability to reset user two-factor authentication
- **Advanced Audit Logging**: Comprehensive compliance-ready activity tracking
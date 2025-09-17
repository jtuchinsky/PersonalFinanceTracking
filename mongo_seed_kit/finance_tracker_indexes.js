// MongoDB Finance Tracker Indexes Creation Script
// Usage: mongosh "mongodb+srv://..." --file finance_tracker_indexes.js

use("personasal_finance-tracker");

print("📊 Creating Finance Tracker database indexes...");

// Users Collection Indexes
db.users.createIndex({ "id": 1 }, { unique: true, name: "uniq_user_id" });
db.users.createIndex({ "email": 1 }, { unique: true, name: "uniq_email" });
db.users.createIndex({ "is_admin": 1 }, { name: "idx_is_admin" });
db.users.createIndex({ "account_status": 1 }, { name: "idx_account_status" });
print("✅ Users collection indexes created");

// Accounts Collection Indexes
db.accounts.createIndex({ "id": 1 }, { unique: true, name: "uniq_account_id" });
db.accounts.createIndex({ "user_id": 1 }, { name: "idx_account_user_id" });
db.accounts.createIndex({ "account_type": 1 }, { name: "idx_account_type" });
db.accounts.createIndex({ "user_id": 1, "account_type": 1 }, { name: "idx_user_account_type" });
print("✅ Accounts collection indexes created");

// Transactions Collection Indexes
db.transactions.createIndex({ "id": 1 }, { unique: true, name: "uniq_transaction_id" });
db.transactions.createIndex({ "user_id": 1 }, { name: "idx_transaction_user_id" });
db.transactions.createIndex({ "account_id": 1 }, { name: "idx_transaction_account_id" });
db.transactions.createIndex({ "date": -1 }, { name: "idx_transaction_date_desc" });
db.transactions.createIndex({ "category": 1 }, { name: "idx_transaction_category" });
db.transactions.createIndex({ "transaction_type": 1 }, { name: "idx_transaction_type" });
db.transactions.createIndex({ "user_id": 1, "date": -1 }, { name: "idx_user_date_desc" });
db.transactions.createIndex({ "user_id": 1, "category": 1 }, { name: "idx_user_category" });
db.transactions.createIndex({ "account_id": 1, "date": -1 }, { name: "idx_account_date_desc" });
print("✅ Transactions collection indexes created");

// Categories Collection Indexes
db.categories.createIndex({ "id": 1 }, { unique: true, name: "uniq_category_id" });
db.categories.createIndex({ "user_id": 1 }, { name: "idx_category_user_id" });
db.categories.createIndex({ "name": 1 }, { name: "idx_category_name" });
print("✅ Categories collection indexes created");

// Account Credentials Collection Indexes
db.account_credentials.createIndex({ "account_id": 1 }, { unique: true, name: "uniq_credential_account_id" });
db.account_credentials.createIndex({ "user_id": 1 }, { name: "idx_credential_user_id" });
print("✅ Account credentials collection indexes created");

// User Activities Collection Indexes
db.user_activities.createIndex({ "user_id": 1 }, { name: "idx_activity_user_id" });
db.user_activities.createIndex({ "timestamp": -1 }, { name: "idx_activity_timestamp_desc" });
db.user_activities.createIndex({ "action": 1 }, { name: "idx_activity_action" });
db.user_activities.createIndex({ "user_id": 1, "timestamp": -1 }, { name: "idx_user_activity_time_desc" });
print("✅ User activities collection indexes created");

// Text Search Indexes
db.transactions.createIndex({ "description": "text", "category": "text" }, { name: "text_search_transactions" });
db.users.createIndex({ "name": "text", "email": "text" }, { name: "text_search_users" });
print("✅ Text search indexes created");

print("🎉 All Finance Tracker database indexes created successfully!");
print("Database: personasal_finance-tracker");
print("Total indexes created: 21");
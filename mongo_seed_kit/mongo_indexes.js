// Run with: mongosh "$MONGODB_URI" --file mongo_indexes.js --eval "const DB='finance_app'"
(function() {
  const dbname = (typeof DB !== 'undefined' && DB) ? DB : 'finance_app';
  const dbh = db.getSiblingDB(dbname);

  dbh.users.createIndex({ email: 1 }, { unique: true, name: "uniq_email" });
  dbh.audit_logs.createIndex({ user_id: 1, created_at: -1 }, { name: "user_time" });
  dbh.plaid_items.createIndex({ item_id: 1 }, { unique: true, name: "uniq_item" });
  dbh.transactions.createIndex({ user_id: 1, date: -1 }, { name: "user_date" });
  dbh.sessions.createIndex({ expires_at: 1 }, { expireAfterSeconds: 0, name: "ttl_expires" });

  print("✅ Indexes ensured on DB '" + dbname + "'");
})();

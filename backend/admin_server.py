from fastapi import FastAPI, APIRouter, HTTPException, Depends
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from typing import List
from datetime import datetime, timezone

from shared.database import db, shutdown_db_client
from shared.auth import get_admin_user, verify_password, create_access_token
from shared.models import AdminStats, UserManagement, UserActivity, AdminLogin, Admin, AdminActivity
from shared.utils import log_user_activity
from shared.email import email_service

# Create the admin app
app = FastAPI(title="Personal Finance Tracker Admin API")

# Create auth router
auth_router = APIRouter(prefix="/api/auth")

# Admin authentication routes
@auth_router.post("/login")
async def admin_login(login_data: AdminLogin):
    admin = await db.admins.find_one({"email": login_data.email})
    if not admin or not verify_password(login_data.password, admin["password"]):
        # Log failed login attempt
        activity = AdminActivity(
            admin_id="unknown",
            action="failed_admin_login",
            details=f"Failed admin login attempt for {login_data.email}"
        )
        await db.admin_activities.insert_one(activity.dict())
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Check account status
    if admin.get("account_status", "active") == "locked":
        activity = AdminActivity(
            admin_id=admin["id"],
            action="admin_login_blocked",
            details="Admin login attempt on locked account"
        )
        await db.admin_activities.insert_one(activity.dict())
        raise HTTPException(status_code=403, detail="Account is locked. Please contact system administrator.")

    if admin.get("account_status", "active") == "deleted":
        activity = AdminActivity(
            admin_id=admin["id"],
            action="admin_login_blocked",
            details="Admin login attempt on deleted account"
        )
        await db.admin_activities.insert_one(activity.dict())
        raise HTTPException(status_code=403, detail="Account not found.")

    # Update last login
    await db.admins.update_one(
        {"id": admin["id"]},
        {"$set": {"last_login": datetime.now(timezone.utc)}}
    )

    # Create admin token
    token = create_access_token(admin["id"], admin["email"], user_type="admin")
    admin_obj = Admin(**{k: v for k, v in admin.items() if k != "password"})

    # Log successful admin login
    activity = AdminActivity(
        admin_id=admin["id"],
        action="admin_login",
        details="Admin logged in successfully"
    )
    await db.admin_activities.insert_one(activity.dict())

    return {"access_token": token, "token_type": "bearer", "user": admin_obj}

# Create a router with the /api/admin prefix
admin_router = APIRouter(prefix="/api/admin")

# Admin routes
@admin_router.get("/stats", response_model=AdminStats)
async def get_admin_stats(admin_id: str = Depends(get_admin_user)):
    # Get user statistics
    total_users = await db.users.count_documents({})
    active_users = await db.users.count_documents({"account_status": "active"})
    locked_users = await db.users.count_documents({"account_status": "locked"})
    deleted_users = await db.users.count_documents({"account_status": "deleted"})

    # Get account and transaction statistics
    total_accounts = await db.accounts.count_documents({})
    total_transactions = await db.transactions.count_documents({})

    # Get recent activities
    recent_activities_data = await db.user_activities.find().sort("timestamp", -1).limit(20).to_list(length=None)
    recent_activities = [UserActivity(**activity) for activity in recent_activities_data]

    await log_user_activity(admin_id, "admin_view_stats", "Admin viewed system statistics")

    return AdminStats(
        total_users=total_users,
        active_users=active_users,
        locked_users=locked_users,
        deleted_users=deleted_users,
        total_accounts=total_accounts,
        total_transactions=total_transactions,
        recent_activities=recent_activities
    )

@admin_router.get("/users", response_model=List[UserManagement])
async def get_all_users(admin_id: str = Depends(get_admin_user)):
    users = await db.users.find().to_list(length=None)
    user_list = []

    for user in users:
        # Get user's account count and balance
        user_accounts = await db.accounts.find({"user_id": user["id"]}).to_list(length=None)
        total_accounts = len(user_accounts)
        total_balance = sum(account.get("balance", 0) for account in user_accounts)

        # Get user's transaction count
        total_transactions = await db.transactions.count_documents({"user_id": user["id"]})

        user_management = UserManagement(
            id=user["id"],
            email=user["email"],
            name=user["name"],
            account_status=user.get("account_status", "active"),
            is_admin=user.get("is_admin", False),
            total_accounts=total_accounts,
            total_transactions=total_transactions,
            total_balance=total_balance,
            last_login=user.get("last_login"),
            created_at=user["created_at"]
        )
        user_list.append(user_management)

    await log_user_activity(admin_id, "admin_view_users", "Admin viewed all users list")

    return user_list

@admin_router.post("/users/{user_id}/lock")
async def lock_user_account(user_id: str, admin_id: str = Depends(get_admin_user)):
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.get("is_admin", False):
        raise HTTPException(status_code=400, detail="Cannot lock admin accounts")

    # Update user status
    await db.users.update_one(
        {"id": user_id},
        {"$set": {"account_status": "locked", "updated_at": datetime.now(timezone.utc)}}
    )

    # Send email notification
    templates = email_service.get_email_templates()
    template = templates["account_locked"]

    email_body = template["body"].format(
        user_name=user["name"],
        user_email=user["email"],
        action_date=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    )

    email_service.send_email(
        to_email=user["email"],
        subject=template["subject"],
        body=email_body,
        email_type="account_locked"
    )

    await log_user_activity(admin_id, "admin_lock_user", f"Admin locked account for user {user['email']}")
    await log_user_activity(user_id, "account_locked", "Account locked by administrator")

    return {"message": "User account locked successfully", "email_sent": True}

@admin_router.post("/users/{user_id}/unlock")
async def unlock_user_account(user_id: str, admin_id: str = Depends(get_admin_user)):
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update user status
    await db.users.update_one(
        {"id": user_id},
        {"$set": {"account_status": "active", "updated_at": datetime.now(timezone.utc)}}
    )

    # Send email notification
    templates = email_service.get_email_templates()
    template = templates["account_unlocked"]

    email_body = template["body"].format(
        user_name=user["name"],
        user_email=user["email"],
        action_date=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    )

    email_service.send_email(
        to_email=user["email"],
        subject=template["subject"],
        body=email_body,
        email_type="account_unlocked"
    )

    await log_user_activity(admin_id, "admin_unlock_user", f"Admin unlocked account for user {user['email']}")
    await log_user_activity(user_id, "account_unlocked", "Account unlocked by administrator")

    return {"message": "User account unlocked successfully", "email_sent": True}

@admin_router.delete("/users/{user_id}")
async def delete_user_account(user_id: str, admin_id: str = Depends(get_admin_user)):
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.get("is_admin", False):
        raise HTTPException(status_code=400, detail="Cannot delete admin accounts")

    # Send email notification before deletion
    templates = email_service.get_email_templates()
    template = templates["account_deleted"]

    email_body = template["body"].format(
        user_name=user["name"],
        user_email=user["email"],
        action_date=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    )

    email_service.send_email(
        to_email=user["email"],
        subject=template["subject"],
        body=email_body,
        email_type="account_deleted"
    )

    # Mark user as deleted (soft delete)
    await db.users.update_one(
        {"id": user_id},
        {"$set": {"account_status": "deleted", "updated_at": datetime.now(timezone.utc)}}
    )

    # Optional: Also delete user's accounts and transactions (hard delete)
    await db.accounts.delete_many({"user_id": user_id})
    await db.transactions.delete_many({"user_id": user_id})
    await db.categories.delete_many({"user_id": user_id})

    await log_user_activity(admin_id, "admin_delete_user", f"Admin deleted account for user {user['email']}")
    await log_user_activity(user_id, "account_deleted", "Account deleted by administrator")

    return {"message": "User account deleted successfully", "email_sent": True}

@admin_router.get("/activities")
async def get_user_activities(admin_id: str = Depends(get_admin_user), limit: int = 100):
    activities = await db.user_activities.find().sort("timestamp", -1).limit(limit).to_list(length=None)

    await log_user_activity(admin_id, "admin_view_activities", f"Admin viewed user activities (limit: {limit})")

    return [UserActivity(**activity) for activity in activities]

@admin_router.get("/emails")
async def get_sent_emails(admin_id: str = Depends(get_admin_user)):
    await log_user_activity(admin_id, "admin_view_emails", "Admin viewed sent emails log")

    return {"sent_emails": email_service.sent_emails}

# Include the routers in the main app
app.include_router(auth_router)
app.include_router(admin_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db():
    await shutdown_db_client()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
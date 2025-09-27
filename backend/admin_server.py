from fastapi import FastAPI, APIRouter, HTTPException, Depends
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from typing import List
from datetime import datetime, timezone

from shared.database import db, shutdown_db_client
from shared.auth import get_admin_user, verify_password, create_access_token
from shared.models import (
    AdminStats, UserManagement, UserActivity, AdminLogin, Admin, AdminActivity,
    Tenant, TenantCreate, UserInvitation, InviteUser, UserManagementSecure, UserSession,
    ConnectionStatus, SyncJobRequest, ReauthRequest, SyncJob, ImportJob, DataIntegrityCheck
)
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

# Tenant Management Routes
@admin_router.post("/tenants", response_model=Tenant)
async def create_tenant(tenant_data: TenantCreate, admin_id: str = Depends(get_admin_user)):
    """Create a new tenant"""
    # Check if tenant name already exists
    existing_tenant = await db.tenants.find_one({"name": tenant_data.name})
    if existing_tenant:
        raise HTTPException(status_code=400, detail="Tenant name already exists")

    # Create tenant
    tenant = Tenant(
        name=tenant_data.name,
        description=tenant_data.description,
        owner_admin_id=admin_id
    )

    await db.tenants.insert_one(tenant.dict())

    # Log admin activity
    activity = AdminActivity(
        admin_id=admin_id,
        action="create_tenant",
        details=f"Created tenant: {tenant.name}"
    )
    await db.admin_activities.insert_one(activity.dict())

    return tenant

@admin_router.get("/tenants", response_model=List[Tenant])
async def get_tenants(admin_id: str = Depends(get_admin_user)):
    """Get all tenants"""
    tenants_data = await db.tenants.find({"status": {"$ne": "deleted"}}).to_list(length=None)
    tenants = [Tenant(**tenant) for tenant in tenants_data]

    # Log admin activity
    activity = AdminActivity(
        admin_id=admin_id,
        action="view_tenants",
        details="Admin viewed tenants list"
    )
    await db.admin_activities.insert_one(activity.dict())

    return tenants

@admin_router.post("/users/invite")
async def invite_user(invite_data: InviteUser, admin_id: str = Depends(get_admin_user)):
    """Invite a user to join a tenant"""
    import secrets
    from datetime import timedelta

    # Check if tenant exists
    tenant = await db.tenants.find_one({"id": invite_data.tenant_id, "status": "active"})
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    # Check if user already exists with this email
    existing_user = await db.users.find_one({"email": invite_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    # Check if there's already a pending invitation
    existing_invite = await db.user_invitations.find_one({
        "email": invite_data.email,
        "tenant_id": invite_data.tenant_id,
        "status": "pending"
    })
    if existing_invite:
        raise HTTPException(status_code=400, detail="User already has a pending invitation for this tenant")

    # Create invitation
    invitation = UserInvitation(
        email=invite_data.email,
        tenant_id=invite_data.tenant_id,
        role=invite_data.role,
        invited_by_admin_id=admin_id,
        invitation_token=secrets.token_urlsafe(32),
        expires_at=datetime.now(timezone.utc) + timedelta(days=7)  # Expires in 7 days
    )

    await db.user_invitations.insert_one(invitation.dict())

    # Send invitation email
    templates = email_service.get_email_templates()
    template = templates.get("user_invitation", {
        "subject": "Invitation to Join Finance Tracker",
        "body": """Dear {user_email},

You have been invited to join the {tenant_name} tenant in our Finance Tracker application.

Your role will be: {role}
Invitation expires: {expires_at}
Invitation token: {invitation_token}

Click here to accept the invitation: [INVITATION_LINK]

If you did not expect this invitation, please ignore this email.

Best regards,
Finance Tracker Admin Team"""
    })

    email_body = template["body"].format(
        user_email=invite_data.email,
        tenant_name=tenant["name"],
        role=invite_data.role,
        expires_at=invitation.expires_at.strftime("%Y-%m-%d %H:%M:%S UTC"),
        invitation_token=invitation.invitation_token
    )

    email_service.send_email(
        to_email=invite_data.email,
        subject=template["subject"],
        body=email_body,
        email_type="user_invitation"
    )

    # Log admin activity
    activity = AdminActivity(
        admin_id=admin_id,
        action="invite_user",
        details=f"Invited user {invite_data.email} to tenant {tenant['name']} as {invite_data.role}"
    )
    await db.admin_activities.insert_one(activity.dict())

    return {
        "message": "User invited successfully",
        "invitation_id": invitation.id,
        "expires_at": invitation.expires_at,
        "email_sent": True
    }

@admin_router.post("/users/invite/{invitation_id}/resend")
async def resend_invitation(invitation_id: str, admin_id: str = Depends(get_admin_user)):
    """Resend an invitation email"""
    invitation = await db.user_invitations.find_one({"id": invitation_id, "status": "pending"})
    if not invitation:
        raise HTTPException(status_code=404, detail="Pending invitation not found")

    # Check if invitation is expired
    if datetime.now(timezone.utc) > invitation["expires_at"]:
        # Update invitation status to expired
        await db.user_invitations.update_one(
            {"id": invitation_id},
            {"$set": {"status": "expired"}}
        )
        raise HTTPException(status_code=400, detail="Invitation has expired")

    # Get tenant info
    tenant = await db.tenants.find_one({"id": invitation["tenant_id"]})

    # Resend email (same as invitation email)
    templates = email_service.get_email_templates()
    template = templates.get("user_invitation", {
        "subject": "Reminder: Invitation to Join Finance Tracker",
        "body": """Dear {user_email},

This is a reminder that you have been invited to join the {tenant_name} tenant in our Finance Tracker application.

Your role will be: {role}
Invitation expires: {expires_at}
Invitation token: {invitation_token}

Click here to accept the invitation: [INVITATION_LINK]

If you did not expect this invitation, please ignore this email.

Best regards,
Finance Tracker Admin Team"""
    })

    email_body = template["body"].format(
        user_email=invitation["email"],
        tenant_name=tenant["name"],
        role=invitation["role"],
        expires_at=invitation["expires_at"].strftime("%Y-%m-%d %H:%M:%S UTC"),
        invitation_token=invitation["invitation_token"]
    )

    email_service.send_email(
        to_email=invitation["email"],
        subject=template["subject"],
        body=email_body,
        email_type="user_invitation_reminder"
    )

    # Log admin activity
    activity = AdminActivity(
        admin_id=admin_id,
        action="resend_invitation",
        details=f"Resent invitation to {invitation['email']} for tenant {tenant['name']}"
    )
    await db.admin_activities.insert_one(activity.dict())

    return {"message": "Invitation resent successfully", "email_sent": True}

# Enhanced user management with tenant support
@admin_router.get("/users", response_model=List[UserManagementSecure])
async def get_users_secure(tenant_id: str = None, admin_id: str = Depends(get_admin_user)):
    """Get users with privacy-first approach (no financial data)"""
    query = {}
    if tenant_id:
        query["tenant_id"] = tenant_id

    users = await db.users.find(query).to_list(length=None)
    user_list = []

    for user in users:
        # Get active session count
        session_count = await db.user_sessions.count_documents({
            "user_id": user["id"],
            "is_active": True,
            "expires_at": {"$gt": datetime.now(timezone.utc)}
        })

        user_management = UserManagementSecure(
            id=user["id"],
            email=user["email"],
            name=user["name"],
            tenant_id=user.get("tenant_id"),
            role=user.get("role", "user"),
            account_status=user.get("account_status", "active"),
            two_factor_enabled=user.get("two_factor_enabled", False),
            last_login=user.get("last_login"),
            created_at=user["created_at"],
            session_count=session_count
        )
        user_list.append(user_management)

    # Log admin activity
    activity = AdminActivity(
        admin_id=admin_id,
        action="view_users",
        details=f"Admin viewed users list (tenant_id: {tenant_id or 'all'})"
    )
    await db.admin_activities.insert_one(activity.dict())

    return user_list

@admin_router.post("/users/{user_id}/reset-2fa")
async def reset_user_2fa(user_id: str, admin_id: str = Depends(get_admin_user)):
    """Reset user's two-factor authentication"""
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Reset 2FA
    await db.users.update_one(
        {"id": user_id},
        {"$set": {
            "two_factor_enabled": False,
            "two_factor_secret": None,
            "updated_at": datetime.now(timezone.utc)
        }}
    )

    # Send notification email
    templates = email_service.get_email_templates()
    template = templates.get("2fa_reset", {
        "subject": "Two-Factor Authentication Reset",
        "body": """Dear {user_name},

Your two-factor authentication has been reset by an administrator.

If you did not request this change, please contact support immediately.

Best regards,
Finance Tracker Team"""
    })

    email_body = template["body"].format(
        user_name=user["name"]
    )

    email_service.send_email(
        to_email=user["email"],
        subject=template["subject"],
        body=email_body,
        email_type="2fa_reset"
    )

    # Log admin activity
    activity = AdminActivity(
        admin_id=admin_id,
        action="reset_user_2fa",
        details=f"Reset 2FA for user {user['email']}",
        target_user_id=user_id
    )
    await db.admin_activities.insert_one(activity.dict())

    return {"message": "Two-factor authentication reset successfully", "email_sent": True}

@admin_router.get("/users/{user_id}/sessions")
async def get_user_sessions(user_id: str, admin_id: str = Depends(get_admin_user)):
    """Get user's active sessions"""
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get active sessions
    sessions = await db.user_sessions.find({
        "user_id": user_id,
        "is_active": True,
        "expires_at": {"$gt": datetime.now(timezone.utc)}
    }).sort("last_activity", -1).to_list(length=None)

    # Log admin activity
    activity = AdminActivity(
        admin_id=admin_id,
        action="view_user_sessions",
        details=f"Viewed sessions for user {user['email']}",
        target_user_id=user_id
    )
    await db.admin_activities.insert_one(activity.dict())

    return {
        "user_id": user_id,
        "user_email": user["email"],
        "sessions": [UserSession(**session) for session in sessions]
    }

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

# Connection & Sync Management Routes
@admin_router.get("/connections", response_model=List[ConnectionStatus])
async def get_connections(tenant_id: str = None, admin_id: str = Depends(get_admin_user)):
    """Get all bank/broker connections with status"""
    import uuid

    query = {}
    if tenant_id:
        # Filter by tenant if provided
        users_in_tenant = await db.users.find({"tenant_id": tenant_id}).to_list(length=None)
        user_ids = [user["id"] for user in users_in_tenant]
        query["user_id"] = {"$in": user_ids}

    # Since we don't have actual Plaid/bank connections yet, we'll generate mock data
    # In a real implementation, this would query actual connection data
    connections = []

    # Get all users for connection simulation
    users = await db.users.find(query).to_list(length=None)

    for user in users[:10]:  # Limit to first 10 users for demo
        # Create mock connections based on user's accounts
        user_accounts = await db.accounts.find({"user_id": user["id"]}).to_list(length=None)

        for account in user_accounts:
            # Create a mock connection for each account
            connection = ConnectionStatus(
                id=str(uuid.uuid4()),
                user_id=user["id"],
                user_name=user["name"],
                user_email=user["email"],
                tenant_id=user.get("tenant_id"),
                institution_name=account["bank_name"],
                connection_type="bank" if account["account_type"] in ["checking", "savings"] else "credit",
                status="active" if user.get("account_status") == "active" else "disconnected",
                last_sync_at=user.get("last_login"),
                next_sync_at=None,  # Would be calculated based on sync schedule
                sync_error_code=None,
                sync_error_message=None,
                item_id=f"item_{account['id'][:8]}",
                created_at=account["created_at"],
                requires_reauth=False
            )
            connections.append(connection)

    # Log admin activity
    activity = AdminActivity(
        admin_id=admin_id,
        action="view_connections",
        details=f"Admin viewed bank connections (tenant_id: {tenant_id or 'all'})"
    )
    await db.admin_activities.insert_one(activity.dict())

    return connections

@admin_router.post("/connections/{connection_id}/sync")
async def trigger_manual_sync(connection_id: str, sync_request: SyncJobRequest, admin_id: str = Depends(get_admin_user)):
    """Trigger manual sync for a connection"""
    import uuid

    # In a real implementation, this would:
    # 1. Validate the connection exists
    # 2. Create a sync job
    # 3. Queue the job for processing
    # 4. Return job status

    # For now, create a mock sync job
    sync_job = SyncJob(
        id=str(uuid.uuid4()),
        connection_id=connection_id,
        user_id=sync_request.user_id or "unknown",
        job_type="manual",
        status="pending",
        started_at=None,
        completed_at=None,
        error_message=None,
        items_synced=0,
        created_at=datetime.now(timezone.utc)
    )

    # Store sync job (in real implementation, this would go to a job queue)
    await db.sync_jobs.insert_one(sync_job.dict())

    # Log admin activity
    activity = AdminActivity(
        admin_id=admin_id,
        action="trigger_sync",
        details=f"Admin triggered manual sync for connection {connection_id}",
        target_user_id=sync_request.user_id
    )
    await db.admin_activities.insert_one(activity.dict())

    return {
        "message": "Manual sync triggered successfully",
        "job_id": sync_job.id,
        "status": sync_job.status,
        "force_full_sync": sync_request.force_full_sync
    }

@admin_router.post("/connections/{connection_id}/reauth-link")
async def generate_reauth_link(connection_id: str, reauth_request: ReauthRequest, admin_id: str = Depends(get_admin_user)):
    """Generate re-authentication link for user"""
    import secrets

    # Validate user exists
    user = await db.users.find_one({"id": reauth_request.user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # In a real implementation, this would:
    # 1. Create a Plaid Link token for re-authentication
    # 2. Store the token with expiry
    # 3. Send secure link to user

    # For now, generate a mock reauth token
    reauth_token = secrets.token_urlsafe(32)
    reauth_link = f"https://link.financetracker.com/reauth?token={reauth_token}&connection_id={connection_id}"

    # Send email to user with reauth link
    templates = email_service.get_email_templates()
    template = templates.get("bank_reauth", {
        "subject": "Re-authenticate Your Bank Connection",
        "body": """Dear {user_name},

Your bank connection requires re-authentication to continue syncing your financial data.

Connection: {institution_name}
Secure Re-authentication Link: {reauth_link}

This link will expire in 24 hours for security purposes.

If you did not request this re-authentication, please contact our support team.

Best regards,
Finance Tracker Team"""
    })

    email_body = template["body"].format(
        user_name=user["name"],
        institution_name="Your Bank",  # Would be actual institution name
        reauth_link=reauth_link
    )

    email_service.send_email(
        to_email=user["email"],
        subject=template["subject"],
        body=email_body,
        email_type="bank_reauth"
    )

    # Log admin activity
    activity = AdminActivity(
        admin_id=admin_id,
        action="generate_reauth_link",
        details=f"Admin generated re-auth link for connection {connection_id}",
        target_user_id=reauth_request.user_id
    )
    await db.admin_activities.insert_one(activity.dict())

    return {
        "message": "Re-authentication link generated and sent to user",
        "email_sent": True,
        "reauth_token": reauth_token,
        "expires_in": "24 hours"
    }

@admin_router.get("/connections/{connection_id}/sync-jobs")
async def get_sync_jobs(connection_id: str, admin_id: str = Depends(get_admin_user), limit: int = 10):
    """Get sync job history for a connection"""
    sync_jobs = await db.sync_jobs.find(
        {"connection_id": connection_id}
    ).sort("created_at", -1).limit(limit).to_list(length=None)

    # Log admin activity
    activity = AdminActivity(
        admin_id=admin_id,
        action="view_sync_jobs",
        details=f"Admin viewed sync job history for connection {connection_id}"
    )
    await db.admin_activities.insert_one(activity.dict())

    return {
        "connection_id": connection_id,
        "sync_jobs": [SyncJob(**job) for job in sync_jobs]
    }

# Data Import & Integrity Routes
@admin_router.get("/imports", response_model=List[ImportJob])
async def get_import_jobs(tenant_id: str = None, admin_id: str = Depends(get_admin_user), limit: int = 50):
    """Get data import job history"""
    query = {}
    if tenant_id:
        query["tenant_id"] = tenant_id

    import_jobs = await db.import_jobs.find(query).sort("created_at", -1).limit(limit).to_list(length=None)

    # Log admin activity
    activity = AdminActivity(
        admin_id=admin_id,
        action="view_imports",
        details=f"Admin viewed import jobs (tenant_id: {tenant_id or 'all'})"
    )
    await db.admin_activities.insert_one(activity.dict())

    return [ImportJob(**job) for job in import_jobs]

@admin_router.post("/integrity-checks")
async def run_data_integrity_check(check_type: str, tenant_id: str = None, admin_id: str = Depends(get_admin_user)):
    """Run data integrity checks"""
    import uuid

    valid_check_types = ["duplicates", "orphaned_transactions", "balance_mismatch", "category_validation"]
    if check_type not in valid_check_types:
        raise HTTPException(status_code=400, detail=f"Invalid check type. Must be one of: {valid_check_types}")

    # Create integrity check job
    integrity_check = DataIntegrityCheck(
        id=str(uuid.uuid4()),
        check_type=check_type,
        tenant_id=tenant_id,
        status="running",
        created_by=admin_id,
        created_at=datetime.now(timezone.utc)
    )

    # Store the check job
    await db.data_integrity_checks.insert_one(integrity_check.dict())

    # In a real implementation, this would queue the integrity check for background processing
    # For now, we'll run a mock check
    issues_found = 0
    details = {}

    if check_type == "duplicates":
        # Mock duplicate check
        issues_found = 3
        details = {"duplicate_transactions": 3, "affected_users": 2}
    elif check_type == "orphaned_transactions":
        # Mock orphaned transaction check
        issues_found = 1
        details = {"orphaned_transactions": 1, "affected_accounts": 1}
    elif check_type == "balance_mismatch":
        # Mock balance mismatch check
        issues_found = 0
        details = {"mismatched_accounts": 0}
    elif check_type == "category_validation":
        # Mock category validation
        issues_found = 5
        details = {"invalid_categories": 5, "missing_categories": 2}

    # Update the check with results
    await db.data_integrity_checks.update_one(
        {"id": integrity_check.id},
        {"$set": {
            "status": "completed",
            "issues_found": issues_found,
            "details": details,
            "completed_at": datetime.now(timezone.utc)
        }}
    )

    # Log admin activity
    activity = AdminActivity(
        admin_id=admin_id,
        action="run_integrity_check",
        details=f"Admin ran {check_type} integrity check (tenant_id: {tenant_id or 'all'})"
    )
    await db.admin_activities.insert_one(activity.dict())

    return {
        "message": f"Data integrity check '{check_type}' completed",
        "check_id": integrity_check.id,
        "issues_found": issues_found,
        "details": details
    }

@admin_router.get("/integrity-checks", response_model=List[DataIntegrityCheck])
async def get_integrity_checks(tenant_id: str = None, admin_id: str = Depends(get_admin_user), limit: int = 20):
    """Get data integrity check history"""
    query = {}
    if tenant_id:
        query["tenant_id"] = tenant_id

    integrity_checks = await db.data_integrity_checks.find(query).sort("created_at", -1).limit(limit).to_list(length=None)

    # Log admin activity
    activity = AdminActivity(
        admin_id=admin_id,
        action="view_integrity_checks",
        details=f"Admin viewed integrity check history (tenant_id: {tenant_id or 'all'})"
    )
    await db.admin_activities.insert_one(activity.dict())

    return [DataIntegrityCheck(**check) for check in integrity_checks]

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
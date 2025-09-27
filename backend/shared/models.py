from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime, timezone
import uuid

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    name: str
    account_status: str = "active"  # active, locked, deleted
    last_login: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Admin(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    name: str
    role: str = "admin"  # admin, super_admin
    permissions: List[str] = Field(default_factory=list)  # specific permissions
    account_status: str = "active"  # active, locked, deleted
    last_login: Optional[datetime] = None
    created_by: Optional[str] = None  # admin ID who created this admin
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class AdminCreate(BaseModel):
    email: EmailStr
    name: str
    password: str
    role: str = "admin"
    permissions: List[str] = Field(default_factory=list)

class AdminLogin(BaseModel):
    email: EmailStr
    password: str

class Account(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    name: str
    account_type: str  # checking, savings, credit_card
    bank_name: str
    balance: float
    nickname: Optional[str] = None
    description: Optional[str] = None
    is_default: bool = False  # True for system-created mock accounts
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AccountCreate(BaseModel):
    name: str
    account_type: str
    bank_name: str
    nickname: Optional[str] = None
    description: Optional[str] = None
    account_username: str
    account_password: str
    initial_balance: float = 0.0

class AccountUpdate(BaseModel):
    name: Optional[str] = None
    nickname: Optional[str] = None
    description: Optional[str] = None

class Transaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    account_id: str
    amount: float
    description: str
    category: str
    transaction_type: str  # debit, credit
    date: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TransactionCreate(BaseModel):
    account_id: str
    amount: float
    description: str
    category: str
    transaction_type: str
    date: datetime

class Category(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    color: str
    icon: str

class DashboardData(BaseModel):
    total_balance: float
    monthly_spending: float
    accounts: List[Account]
    recent_transactions: List[Transaction]
    category_spending: dict

class UserActivity(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    action: str
    details: str
    ip_address: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AdminStats(BaseModel):
    total_users: int
    active_users: int
    locked_users: int
    deleted_users: int
    total_accounts: int
    total_transactions: int
    recent_activities: List[UserActivity]

class UserManagement(BaseModel):
    id: str
    email: str
    name: str
    account_status: str
    total_accounts: int
    total_transactions: int
    total_balance: float
    last_login: Optional[datetime]
    created_at: datetime

class AdminActivity(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    admin_id: str
    action: str
    details: str
    target_user_id: Optional[str] = None  # if action is on a specific user
    ip_address: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Tenant Management Models
class Tenant(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    owner_admin_id: str  # Admin who created this tenant
    status: str = "active"  # active, suspended, deleted
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TenantCreate(BaseModel):
    name: str
    description: Optional[str] = None

class UserInvitation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    tenant_id: str
    role: str = "user"  # user, tenant_admin
    invited_by_admin_id: str
    status: str = "pending"  # pending, accepted, expired, cancelled
    invitation_token: str
    expires_at: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    accepted_at: Optional[datetime] = None

class InviteUser(BaseModel):
    email: EmailStr
    tenant_id: str
    role: str = "user"

class UserSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    session_token: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime
    is_active: bool = True

# Enhanced User model with tenant support
class UserWithTenant(User):
    tenant_id: Optional[str] = None
    role: str = "user"  # user, tenant_admin
    two_factor_enabled: bool = False
    sessions: List[UserSession] = Field(default_factory=list)

# Enhanced UserManagement model without financial data
class UserManagementSecure(BaseModel):
    id: str
    email: str
    name: str
    tenant_id: Optional[str]
    role: str
    account_status: str
    two_factor_enabled: bool
    last_login: Optional[datetime]
    created_at: datetime
    session_count: int = 0

# Connection & Sync Management Models
class ConnectionStatus(BaseModel):
    """Admin view of user bank/broker connections"""
    id: str
    user_id: str
    user_name: str
    user_email: str
    tenant_id: Optional[str]
    institution_name: str
    connection_type: str  # "bank", "credit", "investment"
    status: str  # "active", "error", "disconnected", "expired"
    last_sync_at: Optional[datetime]
    next_sync_at: Optional[datetime]
    sync_error_code: Optional[str]
    sync_error_message: Optional[str]
    item_id: str
    created_at: datetime
    requires_reauth: bool = False

class SyncJobRequest(BaseModel):
    """Request to trigger manual sync"""
    user_id: Optional[str] = None
    connection_id: Optional[str] = None
    force_full_sync: bool = False

class ReauthRequest(BaseModel):
    """Request to generate re-authentication link"""
    connection_id: str
    user_id: str

class SyncJob(BaseModel):
    """Sync job status tracking"""
    id: str
    connection_id: str
    user_id: str
    job_type: str  # "manual", "scheduled", "retry"
    status: str  # "pending", "running", "completed", "failed"
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]
    items_synced: int = 0
    created_at: datetime

# Data Import & Integrity Models
class ImportJob(BaseModel):
    """Data import job tracking"""
    id: str
    user_id: str
    tenant_id: Optional[str]
    import_type: str  # "csv", "qif", "ofx", "manual"
    file_name: Optional[str]
    status: str  # "pending", "processing", "completed", "failed"
    records_total: int = 0
    records_processed: int = 0
    records_imported: int = 0
    records_skipped: int = 0
    records_failed: int = 0
    error_summary: Optional[str]
    created_by: str  # admin_id or user_id
    created_at: datetime
    completed_at: Optional[datetime]

class DataIntegrityCheck(BaseModel):
    """Data integrity check results"""
    id: str
    check_type: str  # "duplicates", "orphaned_transactions", "balance_mismatch", "category_validation"
    tenant_id: Optional[str]
    status: str  # "running", "completed", "failed"
    issues_found: int = 0
    issues_resolved: int = 0
    details: Optional[dict] = None
    created_by: str  # admin_id
    created_at: datetime
    completed_at: Optional[datetime]
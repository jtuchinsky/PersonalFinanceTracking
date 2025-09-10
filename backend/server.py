from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import jwt
import bcrypt
from decimal import Decimal
from cryptography.fernet import Fernet
import base64

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT settings
JWT_SECRET = os.environ.get("JWT_SECRET", "finance-tracker-secret-key-2025")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Encryption settings for account credentials
ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY", "finance-tracker-encryption-key-2025")
# Generate a proper Fernet key from the encryption key
fernet_key = base64.urlsafe_b64encode(ENCRYPTION_KEY.ljust(32)[:32].encode())
cipher_suite = Fernet(fernet_key)

# Create the main app without a prefix
app = FastAPI(title="Personal Finance Tracker API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Security
security = HTTPBearer()

# Pydantic Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    name: str
    is_admin: bool = False
    account_status: str = "active"  # active, locked, deleted
    last_login: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str

class UserLogin(BaseModel):
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
    is_admin: bool
    total_accounts: int
    total_transactions: int
    total_balance: float
    last_login: Optional[datetime]
    created_at: datetime

# Helper functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(user_id: str, email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    payload = {"user_id": user_id, "email": email, "exp": expire}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def encrypt_credential(credential: str) -> str:
    """Encrypt account credentials"""
    return cipher_suite.encrypt(credential.encode()).decode()

def decrypt_credential(encrypted_credential: str) -> str:
    """Decrypt account credentials"""
    return cipher_suite.decrypt(encrypted_credential.encode()).decode()

# Mock Email Service
class EmailService:
    def __init__(self):
        self.sent_emails = []  # Store sent emails for logging
    
    def send_email(self, to_email: str, subject: str, body: str, email_type: str = "notification"):
        """Mock email sending - logs email instead of actually sending"""
        email_log = {
            "id": str(uuid.uuid4()),
            "to": to_email,
            "subject": subject,
            "body": body,
            "type": email_type,
            "sent_at": datetime.now(timezone.utc),
            "status": "sent"
        }
        self.sent_emails.append(email_log)
        
        # Log to console for development
        print(f"\n📧 MOCK EMAIL SENT:")
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        print(f"Body: {body}")
        print(f"Type: {email_type}")
        print(f"Sent at: {email_log['sent_at']}")
        print("=" * 50)
        
        return email_log
    
    def get_email_templates(self):
        return {
            "account_deleted": {
                "subject": "Your Finance Tracker Account Has Been Deleted",
                "body": """Dear {user_name},

We're writing to inform you that your Finance Tracker account ({user_email}) has been deleted by an administrator.

If you believe this was done in error, please contact our support team immediately.

Account Details:
- Email: {user_email}
- Deletion Date: {action_date}
- Reason: Administrative action

All your account data, including transactions and financial information, has been permanently removed from our system.

Best regards,
Finance Tracker Admin Team"""
            },
            "account_locked": {
                "subject": "Your Finance Tracker Account Has Been Locked",
                "body": """Dear {user_name},

Your Finance Tracker account ({user_email}) has been temporarily locked by an administrator.

Account Details:
- Email: {user_email}
- Lock Date: {action_date}
- Status: Locked

You will not be able to access your account until it is unlocked. If you need assistance, please contact our support team.

Best regards,
Finance Tracker Admin Team"""
            },
            "account_unlocked": {
                "subject": "Your Finance Tracker Account Has Been Unlocked",
                "body": """Dear {user_name},

Good news! Your Finance Tracker account ({user_email}) has been unlocked by an administrator.

Account Details:
- Email: {user_email}
- Unlock Date: {action_date}
- Status: Active

You can now log in and access your account normally.

Best regards,
Finance Tracker Admin Team"""
            },
            "admin_welcome": {
                "subject": "Welcome to Finance Tracker Admin Panel",
                "body": """Dear {user_name},

Congratulations! You have been granted administrator access to the Finance Tracker system.

Admin Account Details:
- Email: {user_email}
- Access Level: Administrator
- Granted Date: {action_date}

As an administrator, you can:
- View all user accounts
- Lock/unlock user accounts
- Delete user accounts
- View system statistics
- Monitor user activities

Please use these privileges responsibly and in accordance with our policies.

Best regards,
Finance Tracker System"""
            }
        }

email_service = EmailService()

async def log_user_activity(user_id: str, action: str, details: str, ip_address: str = None):
    """Log user activity for admin monitoring"""
    activity = UserActivity(
        user_id=user_id,
        action=action,
        details=details,
        ip_address=ip_address
    )
    
    activity_dict = activity.model_dump()
    await db.user_activities.insert_one(activity_dict)
    return activity

# Initialize default categories
DEFAULT_CATEGORIES = [
    {"name": "Food & Dining", "color": "#ef4444", "icon": "UtensilsCrossed"},
    {"name": "Transportation", "color": "#3b82f6", "icon": "Car"},
    {"name": "Bills & Utilities", "color": "#f59e0b", "icon": "Receipt"},
    {"name": "Shopping", "color": "#8b5cf6", "icon": "ShoppingBag"},
    {"name": "Entertainment", "color": "#06b6d4", "icon": "Film"},
    {"name": "Healthcare", "color": "#10b981", "icon": "Heart"},
    {"name": "Income", "color": "#059669", "icon": "TrendingUp"},
    {"name": "Other", "color": "#6b7280", "icon": "MoreHorizontal"}
]

# Auth routes
@api_router.post("/auth/register")
async def register(user_data: UserCreate):
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    hashed_password = hash_password(user_data.password)
    user = User(email=user_data.email, name=user_data.name)
    user_dict = user.model_dump()
    user_dict["password"] = hashed_password
    
    await db.users.insert_one(user_dict)
    
    # Create default accounts with mock data
    accounts = [
        {
            "id": str(uuid.uuid4()),
            "user_id": user.id,
            "name": "TD Bank Checking",
            "account_type": "checking",
            "bank_name": "TD Bank",
            "balance": 2543.67,
            "nickname": "My Checking",
            "description": "Primary checking account for daily expenses",
            "is_default": True,
            "created_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user.id,
            "name": "TD Bank Savings",
            "account_type": "savings", 
            "bank_name": "TD Bank",
            "balance": 12847.23,
            "nickname": "Emergency Fund",
            "description": "High-yield savings account for emergencies",
            "is_default": True,
            "created_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user.id,
            "name": "Chase Freedom Credit Card",
            "account_type": "credit_card",
            "bank_name": "Chase",
            "balance": -876.45,
            "nickname": "Rewards Card",
            "description": "Credit card with cashback rewards",
            "is_default": True,
            "created_at": datetime.now(timezone.utc)
        }
    ]
    
    await db.accounts.insert_many(accounts)
    
    # Initialize categories for user
    categories = [
        {**cat, "id": str(uuid.uuid4()), "user_id": user.id} 
        for cat in DEFAULT_CATEGORIES
    ]
    await db.categories.insert_many(categories)
    
    # Create sample transactions
    sample_transactions = [
        {
            "id": str(uuid.uuid4()),
            "user_id": user.id,
            "account_id": accounts[0]["id"],
            "amount": -45.67,
            "description": "Grocery Store",
            "category": "Food & Dining",
            "transaction_type": "debit",
            "date": datetime.now(timezone.utc) - timedelta(days=1),
            "created_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user.id,
            "account_id": accounts[0]["id"],
            "amount": -25.00,
            "description": "Gas Station",
            "category": "Transportation",
            "transaction_type": "debit",
            "date": datetime.now(timezone.utc) - timedelta(days=2),
            "created_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": user.id,
            "account_id": accounts[1]["id"],
            "amount": 2500.00,
            "description": "Salary Deposit",
            "category": "Income",
            "transaction_type": "credit",
            "date": datetime.now(timezone.utc) - timedelta(days=3),
            "created_at": datetime.now(timezone.utc)
        }
    ]
    
    await db.transactions.insert_many(sample_transactions)
    
    # Generate token
    token = create_access_token(user.id, user.email)
    
    return {"access_token": token, "token_type": "bearer", "user": user}

@api_router.post("/auth/login")
async def login(login_data: UserLogin):
    user = await db.users.find_one({"email": login_data.email})
    if not user or not verify_password(login_data.password, user["password"]):
        await log_user_activity("unknown", "failed_login", f"Failed login attempt for {login_data.email}")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Check account status
    if user.get("account_status", "active") == "locked":
        await log_user_activity(user["id"], "login_blocked", "Login attempt on locked account")
        raise HTTPException(status_code=403, detail="Account is locked. Please contact administrator.")
    
    if user.get("account_status", "active") == "deleted":
        await log_user_activity(user["id"], "login_blocked", "Login attempt on deleted account")
        raise HTTPException(status_code=403, detail="Account not found.")
    
    # Update last login
    await db.users.update_one(
        {"id": user["id"]},
        {"$set": {"last_login": datetime.now(timezone.utc)}}
    )
    
    token = create_access_token(user["id"], user["email"])
    user_obj = User(**{k: v for k, v in user.items() if k != "password"})
    
    # Log successful login
    await log_user_activity(user["id"], "login", "User logged in successfully")
    
    return {"access_token": token, "token_type": "bearer", "user": user_obj}

# Dashboard route
@api_router.get("/dashboard", response_model=DashboardData)
async def get_dashboard(user_id: str = Depends(get_current_user)):
    # Get accounts
    accounts = await db.accounts.find({"user_id": user_id}).to_list(length=None)
    account_objects = [Account(**account) for account in accounts]
    
    # Calculate total balance
    total_balance = sum(account.balance for account in account_objects)
    
    # Get recent transactions (last 10)
    transactions = await db.transactions.find(
        {"user_id": user_id}
    ).sort("date", -1).limit(10).to_list(length=None)
    transaction_objects = [Transaction(**transaction) for transaction in transactions]
    
    # Calculate monthly spending (current month debits)
    current_month_start = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_transactions = await db.transactions.find({
        "user_id": user_id,
        "transaction_type": "debit",
        "date": {"$gte": current_month_start}
    }).to_list(length=None)
    
    monthly_spending = abs(sum(t["amount"] for t in monthly_transactions))
    
    # Calculate category spending
    category_spending = {}
    for transaction in monthly_transactions:
        category = transaction["category"]
        category_spending[category] = category_spending.get(category, 0) + abs(transaction["amount"])
    
    return DashboardData(
        total_balance=total_balance,
        monthly_spending=monthly_spending,
        accounts=account_objects,
        recent_transactions=transaction_objects,
        category_spending=category_spending
    )

# Account routes
@api_router.get("/accounts", response_model=List[Account])
async def get_accounts(user_id: str = Depends(get_current_user)):
    accounts = await db.accounts.find({"user_id": user_id}).to_list(length=None)
    return [Account(**account) for account in accounts]

@api_router.post("/accounts", response_model=Account)
async def create_account(
    account_data: AccountCreate,
    user_id: str = Depends(get_current_user)
):
    # Create new account
    account = Account(
        user_id=user_id,
        name=account_data.name,
        account_type=account_data.account_type,
        bank_name=account_data.bank_name,
        balance=account_data.initial_balance,
        nickname=account_data.nickname,
        description=account_data.description,
        is_default=False
    )
    
    account_dict = account.model_dump()
    
    # Store encrypted credentials separately (not in the account model)
    credentials = {
        "account_id": account.id,
        "user_id": user_id,
        "encrypted_username": encrypt_credential(account_data.account_username),
        "encrypted_password": encrypt_credential(account_data.account_password),
        "created_at": datetime.now(timezone.utc)
    }
    
    # Insert account and credentials
    await db.accounts.insert_one(account_dict)
    await db.account_credentials.insert_one(credentials)
    
    return account

@api_router.delete("/accounts/{account_id}")
async def delete_account(
    account_id: str,
    user_id: str = Depends(get_current_user)
):
    # Check if account belongs to user
    account = await db.accounts.find_one({"id": account_id, "user_id": user_id})
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Check if account has transactions
    transaction_count = await db.transactions.count_documents({"account_id": account_id})
    if transaction_count > 0:
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete account with existing transactions. Please delete transactions first."
        )
    
    # Delete account and its credentials
    await db.accounts.delete_one({"id": account_id, "user_id": user_id})
    await db.account_credentials.delete_one({"account_id": account_id, "user_id": user_id})
    
    return {"message": "Account deleted successfully"}

@api_router.put("/accounts/{account_id}", response_model=Account)
async def update_account(
    account_id: str,
    account_update: AccountUpdate,
    user_id: str = Depends(get_current_user)
):
    # Check if account belongs to user
    account = await db.accounts.find_one({"id": account_id, "user_id": user_id})
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Prepare update data
    update_data = {}
    if account_update.name is not None:
        update_data["name"] = account_update.name
    if account_update.nickname is not None:
        update_data["nickname"] = account_update.nickname
    if account_update.description is not None:
        update_data["description"] = account_update.description
    
    if update_data:
        await db.accounts.update_one(
            {"id": account_id, "user_id": user_id},
            {"$set": update_data}
        )
    
    # Return updated account
    updated_account = await db.accounts.find_one({"id": account_id, "user_id": user_id})
    return Account(**updated_account)

# Transaction routes
@api_router.get("/transactions", response_model=List[Transaction])
async def get_transactions(
    user_id: str = Depends(get_current_user),
    account_id: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 50
):
    query = {"user_id": user_id}
    if account_id:
        query["account_id"] = account_id
    if category:
        query["category"] = category
    
    transactions = await db.transactions.find(query).sort("date", -1).limit(limit).to_list(length=None)
    return [Transaction(**transaction) for transaction in transactions]

@api_router.post("/transactions", response_model=Transaction)
async def create_transaction(
    transaction_data: TransactionCreate,
    user_id: str = Depends(get_current_user)
):
    # Verify account belongs to user
    account = await db.accounts.find_one({"id": transaction_data.account_id, "user_id": user_id})
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    transaction = Transaction(
        user_id=user_id,
        **transaction_data.model_dump()
    )
    
    transaction_dict = transaction.model_dump()
    await db.transactions.insert_one(transaction_dict)
    
    # Update account balance
    balance_change = transaction.amount if transaction.transaction_type == "credit" else -abs(transaction.amount)
    await db.accounts.update_one(
        {"id": transaction.account_id},
        {"$inc": {"balance": balance_change}}
    )
    
    return transaction

# Category routes
@api_router.get("/categories", response_model=List[Category])
async def get_categories(user_id: str = Depends(get_current_user)):
    categories = await db.categories.find({"user_id": user_id}).to_list(length=None)
    return [Category(**category) for category in categories]

# Admin middleware
async def get_admin_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    user_id = await get_current_user(credentials)
    user = await db.users.find_one({"id": user_id})
    
    if not user or not user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return user_id

# Admin routes
@api_router.get("/admin/stats", response_model=AdminStats)
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

@api_router.get("/admin/users", response_model=List[UserManagement])
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

@api_router.post("/admin/users/{user_id}/lock")
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

@api_router.post("/admin/users/{user_id}/unlock")
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

@api_router.delete("/admin/users/{user_id}")
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

@api_router.get("/admin/activities")
async def get_user_activities(admin_id: str = Depends(get_admin_user), limit: int = 100):
    activities = await db.user_activities.find().sort("timestamp", -1).limit(limit).to_list(length=None)
    
    await log_user_activity(admin_id, "admin_view_activities", f"Admin viewed user activities (limit: {limit})")
    
    return [UserActivity(**activity) for activity in activities]

@api_router.get("/admin/emails")
async def get_sent_emails(admin_id: str = Depends(get_admin_user)):
    await log_user_activity(admin_id, "admin_view_emails", "Admin viewed sent emails log")
    
    return {"sent_emails": email_service.sent_emails}

# Include the router in the main app
app.include_router(api_router)

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
async def shutdown_db_client():
    client.close()
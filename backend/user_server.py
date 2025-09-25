from fastapi import FastAPI, APIRouter, HTTPException, Depends
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from typing import List, Optional
from datetime import datetime, timezone, timedelta
import uuid

from shared.database import db, shutdown_db_client
from shared.auth import get_current_user, hash_password, verify_password, create_access_token
from shared.models import (
    User, UserCreate, UserLogin, Account, AccountCreate, AccountUpdate,
    Transaction, TransactionCreate, Category, DashboardData
)
from shared.utils import encrypt_credential, log_user_activity

# Create the user app
app = FastAPI(title="Personal Finance Tracker User API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

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
async def shutdown_db():
    await shutdown_db_client()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
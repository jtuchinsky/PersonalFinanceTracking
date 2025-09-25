from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime, timezone
import uuid

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
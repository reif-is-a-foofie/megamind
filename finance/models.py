"""
Finance Data Models - Unified Financial Data Structures

Defines the core data structures for both traditional banking and cryptocurrency
assets, providing a consistent interface for financial data management.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
from decimal import Decimal
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Index, ForeignKey, Numeric, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class AccountType(Enum):
    """Types of financial accounts."""
    CHECKING = "checking"
    SAVINGS = "savings"
    CREDIT = "credit"
    INVESTMENT = "investment"
    CRYPTO = "crypto"


class TransactionType(Enum):
    """Types of financial transactions."""
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"
    PURCHASE = "purchase"
    PAYMENT = "payment"
    FEE = "fee"
    INTEREST = "interest"
    DIVIDEND = "dividend"


class Account(Base):
    """Represents a financial account (bank or crypto)."""
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    account_type = Column(String(50), nullable=False, index=True)
    institution = Column(String(100), nullable=False, index=True)  # Bank name or exchange
    account_number = Column(String(100), nullable=True)  # Masked for security
    currency = Column(String(10), nullable=False, default="USD")
    is_active = Column(Boolean, default=True, nullable=False)
    account_metadata = Column(JSON, nullable=True)  # Account-specific data
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    balances = relationship("Balance", back_populates="account", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="account", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Account(id={self.id}, name='{self.name}', type='{self.account_type}', institution='{self.institution}')>"


class Balance(Base):
    """Represents account balance at a point in time."""
    __tablename__ = "balances"
    
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False, index=True)
    amount = Column(Numeric(20, 8), nullable=False)  # Supports crypto precision
    currency = Column(String(10), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    balance_metadata = Column(JSON, nullable=True)  # Additional balance data
    
    # Relationships
    account = relationship("Account", back_populates="balances")
    
    def __repr__(self):
        return f"<Balance(id={self.id}, account_id={self.account_id}, amount={self.amount}, currency='{self.currency}')>"


class Transaction(Base):
    """Represents a financial transaction."""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False, index=True)
    transaction_type = Column(String(50), nullable=False, index=True)
    amount = Column(Numeric(20, 8), nullable=False)
    currency = Column(String(10), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True, index=True)
    external_id = Column(String(200), nullable=True, index=True)  # ID from bank/exchange
    timestamp = Column(DateTime, nullable=False, index=True)
    transaction_metadata = Column(JSON, nullable=True)  # Transaction-specific data
    
    # Relationships
    account = relationship("Account", back_populates="transactions")
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, account_id={self.account_id}, type='{self.transaction_type}', amount={self.amount})>"


class Portfolio(Base):
    """Represents a portfolio of accounts."""
    __tablename__ = "portfolios"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    total_value = Column(Numeric(20, 8), nullable=False, default=0)
    currency = Column(String(10), nullable=False, default="USD")
    last_updated = Column(DateTime, default=datetime.utcnow, nullable=False)
    portfolio_metadata = Column(JSON, nullable=True)
    
    def __repr__(self):
        return f"<Portfolio(id={self.id}, name='{self.name}', value={self.total_value})>"


# Performance indexes
Index("idx_accounts_institution_type", Account.institution, Account.account_type)
Index("idx_balances_account_timestamp", Balance.account_id, Balance.timestamp)
Index("idx_transactions_account_timestamp", Transaction.account_id, Transaction.timestamp)
Index("idx_transactions_type_category", Transaction.transaction_type, Transaction.category)

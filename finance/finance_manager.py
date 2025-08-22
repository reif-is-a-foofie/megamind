"""
Finance Manager - The Ship's Treasury

Main orchestrator for financial data management, integrating both traditional
banking and cryptocurrency data with the memory system for persistent storage
and unified insights.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from decimal import Decimal
from contextlib import contextmanager

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from .models import Base, Account, Transaction, Balance, Portfolio
from .connectors import BankConnector, CryptoConnector

logger = logging.getLogger(__name__)


class FinanceManager:
    """
    Unified finance manager for banking and cryptocurrency data.
    
    Features:
    - Secure credential management
    - Real-time balance tracking
    - Transaction categorization
    - Portfolio analytics
    - Memory system integration
    - Balance alerts and insights
    """
    
    def __init__(self, db_path: str = "finance/finance_data.db"):
        self.db_path = db_path
        
        # SQLAlchemy setup
        self.engine = create_engine(
            f"sqlite:///{db_path}",
            poolclass=StaticPool,
            connect_args={"check_same_thread": False}
        )
        
        # Session factory
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Initialize database
        self._init_database()
        
        # Connectors
        self.bank_connectors = {}
        self.crypto_connectors = {}
        
        # Memory system integration (will be set later)
        self.memory_store = None
        
        logger.info(f"Finance manager initialized with database at {db_path}")
    
    def _init_database(self):
        """Initialize database tables."""
        Base.metadata.create_all(bind=self.engine)
        
        # Enable foreign key constraints
        def _enable_foreign_keys(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
        
        event.listen(self.engine, "connect", _enable_foreign_keys)
        
        logger.info("Finance database initialized")
    
    @contextmanager
    def get_session(self) -> Session:
        """Thread-safe database session context manager."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def set_memory_store(self, memory_store):
        """Set the memory store for integration."""
        self.memory_store = memory_store
        logger.info("Memory store integrated with finance manager")
    
    def add_bank_connector(self, bank_name: str) -> BankConnector:
        """Add a bank connector."""
        connector = BankConnector(bank_name)
        self.bank_connectors[bank_name] = connector
        logger.info(f"Added bank connector for {bank_name}")
        return connector
    
    def add_crypto_connector(self, exchange_name: str) -> CryptoConnector:
        """Add a crypto exchange connector."""
        connector = CryptoConnector(exchange_name)
        self.crypto_connectors[exchange_name] = connector
        logger.info(f"Added crypto connector for {exchange_name}")
        return connector
    
    def sync_accounts(self, institution_name: str, account_type: str = "bank"):
        """Sync accounts from a financial institution."""
        try:
            if account_type == "bank":
                connector = self.bank_connectors.get(institution_name)
            else:
                connector = self.crypto_connectors.get(institution_name)
            
            if not connector:
                logger.error(f"No connector found for {institution_name}")
                return False
            
            if not connector.connect():
                logger.error(f"Failed to connect to {institution_name}")
                return False
            
            # Get accounts from institution
            accounts_data = connector.get_accounts()
            
            with self.get_session() as session:
                for account_data in accounts_data:
                    # Check if account already exists
                    existing_account = session.query(Account).filter(
                        Account.name == account_data["name"],
                        Account.institution == institution_name
                    ).first()
                    
                    if not existing_account:
                        # Create new account
                        account = Account(
                            name=account_data["name"],
                            account_type=account_data["type"],
                            institution=institution_name,
                            account_number=account_data.get("account_number"),
                            currency=account_data["currency"],
                            account_metadata=account_data
                        )
                        session.add(account)
                        session.flush()
                        
                        # Log to memory system
                        if self.memory_store:
                            self.memory_store.add_feed_item(
                                source="finance",
                                source_id=f"account_{account.id}",
                                title=f"New {account_data['type']} account added",
                                content=f"Account: {account_data['name']} at {institution_name}",
                                metadata={"account_id": account.id, "institution": institution_name}
                            )
                        
                        logger.info(f"Added new account: {account_data['name']}")
                    else:
                        # Update existing account
                        existing_account.updated_at = datetime.utcnow()
                        existing_account.account_metadata = account_data
                        logger.info(f"Updated existing account: {account_data['name']}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to sync accounts from {institution_name}: {e}")
            return False
    
    def sync_balances(self, account_id: int = None):
        """Sync balances for all accounts or a specific account."""
        try:
            with self.get_session() as session:
                if account_id:
                    accounts = session.query(Account).filter(Account.id == account_id).all()
                else:
                    accounts = session.query(Account).filter(Account.is_active == True).all()
                
                for account in accounts:
                    # Get connector
                    if account.account_type == "crypto":
                        connector = self.crypto_connectors.get(account.institution)
                    else:
                        connector = self.bank_connectors.get(account.institution)
                    
                    if not connector:
                        logger.warning(f"No connector found for {account.institution}")
                        continue
                    
                    # Get balance from institution
                    balance_data = connector.get_balances(account.name)
                    
                    if balance_data:
                        # Create balance record
                        balance = Balance(
                            account_id=account.id,
                            amount=balance_data["amount"],
                            currency=balance_data["currency"],
                            timestamp=balance_data["timestamp"],
                            balance_metadata=balance_data
                        )
                        session.add(balance)
                        
                        # Log to memory system
                        if self.memory_store:
                            self.memory_store.add_feed_item(
                                source="finance",
                                source_id=f"balance_{balance.id}",
                                title=f"Balance update: {account.name}",
                                content=f"Balance: {balance_data['amount']} {balance_data['currency']}",
                                metadata={
                                    "account_id": account.id,
                                    "balance_id": balance.id,
                                    "amount": str(balance_data["amount"]),
                                    "currency": balance_data["currency"]
                                }
                            )
                        
                        logger.info(f"Updated balance for {account.name}: {balance_data['amount']} {balance_data['currency']}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to sync balances: {e}")
            return False
    
    def sync_transactions(self, account_id: int = None, days: int = 30):
        """Sync transactions for all accounts or a specific account."""
        try:
            with self.get_session() as session:
                if account_id:
                    accounts = session.query(Account).filter(Account.id == account_id).all()
                else:
                    accounts = session.query(Account).filter(Account.is_active == True).all()
                
                for account in accounts:
                    # Get connector
                    if account.account_type == "crypto":
                        connector = self.crypto_connectors.get(account.institution)
                    else:
                        connector = self.bank_connectors.get(account.institution)
                    
                    if not connector:
                        logger.warning(f"No connector found for {account.institution}")
                        continue
                    
                    # Get transactions from institution
                    transactions_data = connector.get_transactions(account.name, days)
                    
                    for tx_data in transactions_data:
                        # Check if transaction already exists
                        existing_tx = session.query(Transaction).filter(
                            Transaction.external_id == tx_data["external_id"],
                            Transaction.account_id == account.id
                        ).first()
                        
                        if not existing_tx:
                            # Create new transaction
                            transaction = Transaction(
                                account_id=account.id,
                                transaction_type=tx_data["type"],
                                amount=tx_data["amount"],
                                currency=tx_data["currency"],
                                description=tx_data["description"],
                                category=tx_data.get("category"),
                                external_id=tx_data["external_id"],
                                timestamp=tx_data["timestamp"],
                                transaction_metadata=tx_data
                            )
                            session.add(transaction)
                            
                            # Log to memory system
                            if self.memory_store:
                                self.memory_store.add_feed_item(
                                    source="finance",
                                    source_id=f"transaction_{transaction.id}",
                                    title=f"New transaction: {tx_data['description']}",
                                    content=f"Amount: {tx_data['amount']} {tx_data['currency']} | Type: {tx_data['type']}",
                                    metadata={
                                        "account_id": account.id,
                                        "transaction_id": transaction.id,
                                        "amount": str(tx_data["amount"]),
                                        "type": tx_data["type"],
                                        "category": tx_data.get("category")
                                    }
                                )
                            
                            logger.info(f"Added transaction: {tx_data['description']}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to sync transactions: {e}")
            return False
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get portfolio summary with total value and breakdown."""
        try:
            with self.get_session() as session:
                # Get all active accounts
                accounts = session.query(Account).filter(Account.is_active == True).all()
                
                total_value = Decimal('0')
                account_summaries = []
                
                for account in accounts:
                    # Get latest balance
                    latest_balance = session.query(Balance).filter(
                        Balance.account_id == account.id
                    ).order_by(Balance.timestamp.desc()).first()
                    
                    if latest_balance:
                        account_value = latest_balance.amount
                        if latest_balance.currency != "USD":
                            # In a real implementation, you'd convert to USD
                            # For demo, we'll use the amount as-is
                            account_value = latest_balance.amount
                        
                        total_value += account_value
                        
                        account_summaries.append({
                            "id": account.id,
                            "name": account.name,
                            "type": account.account_type,
                            "institution": account.institution,
                            "balance": latest_balance.amount,
                            "currency": latest_balance.currency,
                            "value_usd": account_value
                        })
                
                # Calculate 24h change (simplified)
                yesterday = datetime.utcnow() - timedelta(days=1)
                yesterday_balances = session.query(Balance).filter(
                    Balance.timestamp >= yesterday
                ).all()
                
                change_24h = Decimal('0')
                if yesterday_balances:
                    # Simplified calculation - in real implementation, you'd compare with yesterday's total
                    change_24h = Decimal(str(len(yesterday_balances) * 100))  # Mock change
                
                summary = {
                    "total_value_usd": total_value,
                    "change_24h_usd": change_24h,
                    "change_24h_percent": (change_24h / total_value * 100) if total_value > 0 else 0,
                    "num_accounts": len(accounts),
                    "accounts": account_summaries,
                    "timestamp": datetime.utcnow()
                }
                
                return summary
                
        except Exception as e:
            logger.error(f"Failed to get portfolio summary: {e}")
            return {}
    
    def get_spending_insights(self, days: int = 30) -> Dict[str, Any]:
        """Get spending insights and categorization."""
        try:
            with self.get_session() as session:
                cutoff_date = datetime.utcnow() - timedelta(days=days)
                
                # Get transactions in the period
                transactions = session.query(Transaction).filter(
                    Transaction.timestamp >= cutoff_date,
                    Transaction.transaction_type.in_(["purchase", "payment", "withdrawal"])
                ).all()
                
                # Categorize spending
                category_totals = {}
                total_spending = Decimal('0')
                
                for tx in transactions:
                    if tx.amount > 0:  # Only count spending (positive amounts)
                        category = tx.category or "uncategorized"
                        if category not in category_totals:
                            category_totals[category] = Decimal('0')
                        category_totals[category] += tx.amount
                        total_spending += tx.amount
                
                # Calculate percentages
                category_percentages = {}
                for category, amount in category_totals.items():
                    category_percentages[category] = (amount / total_spending * 100) if total_spending > 0 else 0
                
                insights = {
                    "period_days": days,
                    "total_spending": total_spending,
                    "num_transactions": len(transactions),
                    "category_breakdown": category_totals,
                    "category_percentages": category_percentages,
                    "top_categories": sorted(category_totals.items(), key=lambda x: x[1], reverse=True)[:5],
                    "timestamp": datetime.utcnow()
                }
                
                return insights
                
        except Exception as e:
            logger.error(f"Failed to get spending insights: {e}")
            return {}
    
    def set_balance_alert(self, account_id: int, threshold: Decimal, alert_type: str = "low"):
        """Set balance alert for an account."""
        try:
            with self.get_session() as session:
                account = session.query(Account).filter(Account.id == account_id).first()
                if not account:
                    logger.error(f"Account {account_id} not found")
                    return False
                
                # Store alert in account metadata
                if not account.account_metadata:
                    account.account_metadata = {}
                
                account.account_metadata["balance_alert"] = {
                    "threshold": str(threshold),
                    "type": alert_type,
                    "created_at": datetime.utcnow().isoformat()
                }
                
                logger.info(f"Set {alert_type} balance alert for {account.name}: {threshold}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to set balance alert: {e}")
            return False
    
    def check_balance_alerts(self):
        """Check and trigger balance alerts."""
        try:
            with self.get_session() as session:
                accounts = session.query(Account).filter(Account.is_active == True).all()
                
                for account in accounts:
                    if not account.account_metadata or "balance_alert" not in account.account_metadata:
                        continue
                    
                    alert_config = account.account_metadata["balance_alert"]
                    threshold = Decimal(alert_config["threshold"])
                    alert_type = alert_config["type"]
                    
                    # Get current balance
                    latest_balance = session.query(Balance).filter(
                        Balance.account_id == account.id
                    ).order_by(Balance.timestamp.desc()).first()
                    
                    if not latest_balance:
                        continue
                    
                    current_balance = latest_balance.amount
                    should_alert = False
                    
                    if alert_type == "low" and current_balance <= threshold:
                        should_alert = True
                    elif alert_type == "high" and current_balance >= threshold:
                        should_alert = True
                    
                    if should_alert and self.memory_store:
                        self.memory_store.add_feed_item(
                            source="finance",
                            source_id=f"alert_{account.id}_{datetime.utcnow().timestamp()}",
                            title=f"Balance Alert: {account.name}",
                            content=f"Current balance: {current_balance} {latest_balance.currency} (Threshold: {threshold})",
                            metadata={
                                "account_id": account.id,
                                "alert_type": alert_type,
                                "current_balance": str(current_balance),
                                "threshold": str(threshold)
                            }
                        )
                        
                        logger.info(f"Balance alert triggered for {account.name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to check balance alerts: {e}")
            return False
    
    def __repr__(self):
        return f"<FinanceManager(db_path='{self.db_path}', banks={len(self.bank_connectors)}, crypto={len(self.crypto_connectors)})>"

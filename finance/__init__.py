"""
Unified Finance System - The Ship's Treasury

This module provides unified financial data aggregation for both traditional
banking and cryptocurrency assets. It integrates with the memory system to
provide persistent financial history and insights.
"""

from .finance_manager import FinanceManager
from .models import Account, Transaction, Balance, Portfolio
from .connectors import BankConnector, CryptoConnector
from .analytics import FinanceAnalytics

__all__ = ["FinanceManager", "Account", "Transaction", "Balance", "Portfolio", 
           "BankConnector", "CryptoConnector", "FinanceAnalytics"]

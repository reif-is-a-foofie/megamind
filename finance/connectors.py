"""
Financial Connectors - Secure API Integration

Provides secure connectors for traditional banking and cryptocurrency exchanges,
with unified interfaces and secure credential management.
"""

import os
import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from decimal import Decimal
import requests
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

logger = logging.getLogger(__name__)


class BaseConnector(ABC):
    """Base class for financial connectors."""
    
    def __init__(self, credentials_path: str = "finance/credentials.json"):
        self.credentials_path = credentials_path
        self.encryption_key = self._get_or_create_key()
        self.cipher = Fernet(self.encryption_key)
    
    def _get_or_create_key(self) -> bytes:
        """Get or create encryption key for credentials."""
        key_file = "finance/.key"
        if os.path.exists(key_file):
            with open(key_file, "rb") as f:
                return f.read()
        else:
            # Create new key
            os.makedirs("finance", exist_ok=True)
            key = Fernet.generate_key()
            with open(key_file, "wb") as f:
                f.write(key)
            return key
    
    def _encrypt_credentials(self, data: str) -> str:
        """Encrypt sensitive credential data."""
        return self.cipher.encrypt(data.encode()).decode()
    
    def _decrypt_credentials(self, encrypted_data: str) -> str:
        """Decrypt sensitive credential data."""
        return self.cipher.decrypt(encrypted_data.encode()).decode()
    
    def _load_credentials(self) -> Dict[str, Any]:
        """Load encrypted credentials from file."""
        if not os.path.exists(self.credentials_path):
            return {}
        
        with open(self.credentials_path, 'r') as f:
            encrypted_data = json.load(f)
        
        decrypted_data = {}
        for key, encrypted_value in encrypted_data.items():
            decrypted_data[key] = self._decrypt_credentials(encrypted_value)
        
        return decrypted_data
    
    def _save_credentials(self, credentials: Dict[str, str]):
        """Save encrypted credentials to file."""
        os.makedirs(os.path.dirname(self.credentials_path), exist_ok=True)
        
        encrypted_data = {}
        for key, value in credentials.items():
            encrypted_data[key] = self._encrypt_credentials(value)
        
        with open(self.credentials_path, 'w') as f:
            json.dump(encrypted_data, f, indent=2)
    
    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to the financial institution."""
        pass
    
    @abstractmethod
    def get_accounts(self) -> List[Dict[str, Any]]:
        """Get list of accounts."""
        pass
    
    @abstractmethod
    def get_balances(self, account_id: str) -> Dict[str, Any]:
        """Get current account balances."""
        pass
    
    @abstractmethod
    def get_transactions(self, account_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get recent transactions."""
        pass


class BankConnector(BaseConnector):
    """Connector for traditional banking institutions."""
    
    def __init__(self, bank_name: str, credentials_path: str = "finance/credentials.json"):
        super().__init__(credentials_path)
        self.bank_name = bank_name
        self.session = requests.Session()
        self.base_url = self._get_bank_url()
    
    def _get_bank_url(self) -> str:
        """Get API URL for the bank."""
        bank_urls = {
            "chase": "https://api.chase.com/v1",
            "bankofamerica": "https://api.bankofamerica.com/v1",
            "wellsfargo": "https://api.wellsfargo.com/v1",
            "citibank": "https://api.citibank.com/v1",
            "usbank": "https://api.usbank.com/v1"
        }
        return bank_urls.get(self.bank_name.lower(), "https://api.example.com/v1")
    
    def setup_credentials(self, username: str, password: str, api_key: str = None):
        """Setup encrypted credentials for the bank."""
        credentials = {
            f"{self.bank_name}_username": username,
            f"{self.bank_name}_password": password
        }
        if api_key:
            credentials[f"{self.bank_name}_api_key"] = api_key
        
        self._save_credentials(credentials)
        logger.info(f"Credentials saved for {self.bank_name}")
    
    def connect(self) -> bool:
        """Establish connection to the bank."""
        try:
            credentials = self._load_credentials()
            username = credentials.get(f"{self.bank_name}_username")
            password = credentials.get(f"{self.bank_name}_password")
            api_key = credentials.get(f"{self.bank_name}_api_key")
            
            if not username or not password:
                logger.error(f"Missing credentials for {self.bank_name}")
                return False
            
            # Simulate bank API authentication
            auth_data = {
                "username": username,
                "password": password
            }
            if api_key:
                auth_data["api_key"] = api_key
            
            # In a real implementation, this would make actual API calls
            # For demo purposes, we'll simulate successful authentication
            logger.info(f"Connected to {self.bank_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to {self.bank_name}: {e}")
            return False
    
    def get_accounts(self) -> List[Dict[str, Any]]:
        """Get list of bank accounts."""
        try:
            # Simulate API call to get accounts
            # In real implementation, this would call the bank's API
            mock_accounts = [
                {
                    "id": f"{self.bank_name}_checking_001",
                    "name": f"{self.bank_name.title()} Checking",
                    "type": "checking",
                    "account_number": "****1234",
                    "currency": "USD"
                },
                {
                    "id": f"{self.bank_name}_savings_001",
                    "name": f"{self.bank_name.title()} Savings",
                    "type": "savings",
                    "account_number": "****5678",
                    "currency": "USD"
                }
            ]
            
            logger.info(f"Retrieved {len(mock_accounts)} accounts from {self.bank_name}")
            return mock_accounts
            
        except Exception as e:
            logger.error(f"Failed to get accounts from {self.bank_name}: {e}")
            return []
    
    def get_balances(self, account_id: str) -> Dict[str, Any]:
        """Get current account balance."""
        try:
            # Simulate API call to get balance
            # In real implementation, this would call the bank's API
            import random
            
            mock_balance = {
                "account_id": account_id,
                "amount": Decimal(str(random.uniform(1000, 50000))),
                "currency": "USD",
                "timestamp": datetime.utcnow(),
                "available_balance": Decimal(str(random.uniform(800, 45000)))
            }
            
            # Convert Decimal to string for JSON serialization
            mock_balance["amount"] = str(mock_balance["amount"])
            mock_balance["available_balance"] = str(mock_balance["available_balance"])
            
            logger.info(f"Retrieved balance for account {account_id}")
            return mock_balance
            
        except Exception as e:
            logger.error(f"Failed to get balance for account {account_id}: {e}")
            return {}
    
    def get_transactions(self, account_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get recent transactions."""
        try:
            # Simulate API call to get transactions
            # In real implementation, this would call the bank's API
            import random
            from datetime import datetime, timedelta
            
            mock_transactions = []
            categories = ["groceries", "gas", "restaurant", "shopping", "utilities", "entertainment"]
            transaction_types = ["purchase", "deposit", "withdrawal", "transfer"]
            
            for i in range(random.randint(5, 15)):
                transaction = {
                    "id": f"{account_id}_tx_{i}",
                    "type": random.choice(transaction_types),
                    "amount": Decimal(str(random.uniform(10, 500))),
                    "currency": "USD",
                    "description": f"Transaction {i+1}",
                    "category": random.choice(categories),
                    "timestamp": datetime.utcnow() - timedelta(days=random.randint(0, days)),
                    "external_id": f"ext_{random.randint(10000, 99999)}"
                }
                
                # Convert Decimal to string for JSON serialization
                transaction["amount"] = str(transaction["amount"])
                mock_transactions.append(transaction)
            
            logger.info(f"Retrieved {len(mock_transactions)} transactions for account {account_id}")
            return mock_transactions
            
        except Exception as e:
            logger.error(f"Failed to get transactions for account {account_id}: {e}")
            return []


class CryptoConnector(BaseConnector):
    """Connector for cryptocurrency exchanges."""
    
    def __init__(self, exchange_name: str, credentials_path: str = "finance/credentials.json"):
        super().__init__(credentials_path)
        self.exchange_name = exchange_name
        self.session = requests.Session()
        self.base_url = self._get_exchange_url()
    
    def _get_exchange_url(self) -> str:
        """Get API URL for the exchange."""
        exchange_urls = {
            "coinbase": "https://api.coinbase.com/v2",
            "binance": "https://api.binance.com/api/v3",
            "kraken": "https://api.kraken.com/0",
            "gemini": "https://api.gemini.com/v1",
            "ftx": "https://ftx.com/api"
        }
        return exchange_urls.get(self.exchange_name.lower(), "https://api.example.com/v1")
    
    def setup_credentials(self, api_key: str, api_secret: str, passphrase: str = None):
        """Setup encrypted credentials for the exchange."""
        credentials = {
            f"{self.exchange_name}_api_key": api_key,
            f"{self.exchange_name}_api_secret": api_secret
        }
        if passphrase:
            credentials[f"{self.exchange_name}_passphrase"] = passphrase
        
        self._save_credentials(credentials)
        logger.info(f"Credentials saved for {self.exchange_name}")
    
    def connect(self) -> bool:
        """Establish connection to the exchange."""
        try:
            credentials = self._load_credentials()
            api_key = credentials.get(f"{self.exchange_name}_api_key")
            api_secret = credentials.get(f"{self.exchange_name}_api_secret")
            
            if not api_key or not api_secret:
                logger.error(f"Missing credentials for {self.exchange_name}")
                return False
            
            # Simulate exchange API authentication
            # In a real implementation, this would make actual API calls
            logger.info(f"Connected to {self.exchange_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to {self.exchange_name}: {e}")
            return False
    
    def get_accounts(self) -> List[Dict[str, Any]]:
        """Get list of crypto accounts/wallets."""
        try:
            # Simulate API call to get accounts
            # In real implementation, this would call the exchange's API
            mock_accounts = [
                {
                    "id": f"{self.exchange_name}_btc_wallet",
                    "name": f"{self.exchange_name.title()} BTC Wallet",
                    "type": "crypto",
                    "currency": "BTC",
                    "coin": "Bitcoin"
                },
                {
                    "id": f"{self.exchange_name}_eth_wallet",
                    "name": f"{self.exchange_name.title()} ETH Wallet",
                    "type": "crypto",
                    "currency": "ETH",
                    "coin": "Ethereum"
                },
                {
                    "id": f"{self.exchange_name}_usdc_wallet",
                    "name": f"{self.exchange_name.title()} USDC Wallet",
                    "type": "crypto",
                    "currency": "USDC",
                    "coin": "USD Coin"
                }
            ]
            
            logger.info(f"Retrieved {len(mock_accounts)} accounts from {self.exchange_name}")
            return mock_accounts
            
        except Exception as e:
            logger.error(f"Failed to get accounts from {self.exchange_name}: {e}")
            return []
    
    def get_balances(self, account_id: str) -> Dict[str, Any]:
        """Get current crypto balance."""
        try:
            # Simulate API call to get balance
            # In real implementation, this would call the exchange's API
            import random
            
            # Extract currency from account_id
            currency = account_id.split("_")[-2].upper()
            
            mock_balance = {
                "account_id": account_id,
                "amount": Decimal(str(random.uniform(0.1, 10.0))),
                "currency": currency,
                "timestamp": datetime.utcnow(),
                "usd_value": Decimal(str(random.uniform(100, 50000))),
                "price_usd": Decimal(str(random.uniform(100, 50000)))
            }
            
            # Convert Decimal to string for JSON serialization
            mock_balance["amount"] = str(mock_balance["amount"])
            mock_balance["usd_value"] = str(mock_balance["usd_value"])
            mock_balance["price_usd"] = str(mock_balance["price_usd"])
            
            logger.info(f"Retrieved balance for account {account_id}")
            return mock_balance
            
        except Exception as e:
            logger.error(f"Failed to get balance for account {account_id}: {e}")
            return {}
    
    def get_transactions(self, account_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get recent crypto transactions."""
        try:
            # Simulate API call to get transactions
            # In real implementation, this would call the exchange's API
            import random
            from datetime import datetime, timedelta
            
            mock_transactions = []
            transaction_types = ["deposit", "withdrawal", "trade", "transfer"]
            
            for i in range(random.randint(3, 10)):
                transaction = {
                    "id": f"{account_id}_tx_{i}",
                    "type": random.choice(transaction_types),
                    "amount": Decimal(str(random.uniform(0.001, 2.0))),
                    "currency": account_id.split("_")[-2].upper(),
                    "description": f"Crypto transaction {i+1}",
                    "category": "crypto",
                    "timestamp": datetime.utcnow() - timedelta(days=random.randint(0, days)),
                    "external_id": f"ext_{random.randint(10000, 99999)}",
                    "usd_value": Decimal(str(random.uniform(10, 1000)))
                }
                
                # Convert Decimal to string for JSON serialization
                transaction["amount"] = str(transaction["amount"])
                transaction["usd_value"] = str(transaction["usd_value"])
                mock_transactions.append(transaction)
            
            logger.info(f"Retrieved {len(mock_transactions)} transactions for account {account_id}")
            return mock_transactions
            
        except Exception as e:
            logger.error(f"Failed to get transactions for account {account_id}: {e}")
            return []
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get portfolio summary with total value and 24h change."""
        try:
            # Simulate portfolio summary
            import random
            
            total_value = Decimal(str(random.uniform(10000, 100000)))
            change_24h = Decimal(str(random.uniform(-5000, 5000)))
            change_percent = (change_24h / total_value) * 100
            
            summary = {
                "total_value_usd": total_value,
                "change_24h_usd": change_24h,
                "change_24h_percent": change_percent,
                "timestamp": datetime.utcnow(),
                "num_assets": random.randint(3, 8)
            }
            
            # Convert Decimal to string for JSON serialization
            summary["total_value_usd"] = str(summary["total_value_usd"])
            summary["change_24h_usd"] = str(summary["change_24h_usd"])
            
            logger.info(f"Retrieved portfolio summary from {self.exchange_name}")
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get portfolio summary from {self.exchange_name}: {e}")
            return {}

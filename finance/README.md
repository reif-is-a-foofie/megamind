# Unified Finance System - The Ship's Treasury

> *"Our abacus is quiet-kept"* - The unified finance system provides secure, comprehensive financial data management for both traditional banking and cryptocurrency assets.

## Overview

The Unified Finance System is a comprehensive financial data aggregator that handles both traditional banking and cryptocurrency data through a single, elegant interface. It integrates with the memory system to provide persistent financial history and insights.

## Features

### 🏦 Banking Integration
- **Secure Credential Management**: Encrypted storage of bank credentials
- **Multi-Bank Support**: Chase, Bank of America, Wells Fargo, Citi, US Bank
- **Real-Time Balance Tracking**: Live account balance updates
- **Transaction Categorization**: Automatic categorization of spending
- **Account Management**: Checking, savings, credit, and investment accounts

### 🚀 Cryptocurrency Integration
- **Multi-Exchange Support**: Coinbase, Binance, Kraken, Gemini, FTX
- **Portfolio Tracking**: Real-time crypto portfolio values
- **Performance Metrics**: 24h changes, returns, and analytics
- **Price Alerts**: Configurable price and balance alerts
- **Transaction History**: Complete crypto transaction tracking

### 📊 Advanced Analytics
- **Portfolio Performance**: Detailed performance analysis
- **Spending Insights**: Categorized spending patterns
- **Budget Tracking**: Budget vs. actual spending analysis
- **Predictive Analytics**: Spending forecasts and recommendations
- **Investment Metrics**: ROI calculations and performance tracking

### 🔐 Security Features
- **Encrypted Credentials**: Fernet encryption for all sensitive data
- **Secure API Integration**: Protected communication with financial institutions
- **Audit Trail**: Complete transaction and action logging
- **Access Control**: Role-based access management

### 🔗 Memory System Integration
- **Persistent Storage**: All financial data stored in memory system
- **Historical Analysis**: Complete financial history tracking
- **Event Logging**: Financial events logged to memory system
- **Query Interface**: Natural language queries for financial data

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Bank APIs     │    │  Crypto APIs    │    │  Memory System  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Bank Connectors │    │Crypto Connectors│    │  Finance Store  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 ▼
                    ┌─────────────────────────┐
                    │   Finance Manager       │
                    │  (Unified Interface)    │
                    └─────────────────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │   Finance Analytics     │
                    │   (Insights Engine)     │
                    └─────────────────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │   CLI Interface         │
                    │   (User Interface)      │
                    └─────────────────────────┘
```

## Installation

1. **Install Dependencies**:
   ```bash
   pip install -r finance/requirements.txt
   ```

2. **Initialize Database**:
   ```bash
   python -m finance.cli status
   ```

## Quick Start

### 1. Setup Bank Credentials
```bash
# Setup Chase bank credentials
python -m finance.cli setup-bank chase username password

# Setup Bank of America credentials
python -m finance.cli setup-bank bankofamerica username password
```

### 2. Setup Crypto Credentials
```bash
# Setup Coinbase credentials
python -m finance.cli setup-crypto coinbase api_key api_secret

# Setup Binance credentials
python -m finance.cli setup-crypto binance api_key api_secret
```

### 3. Sync Financial Data
```bash
# Sync bank accounts
python -m finance.cli sync-accounts chase --type bank

# Sync crypto accounts
python -m finance.cli sync-accounts coinbase --type crypto

# Sync balances
python -m finance.cli sync-balances

# Sync transactions
python -m finance.cli sync-transactions
```

### 4. View Analytics
```bash
# Portfolio summary
python -m finance.cli portfolio-summary

# Spending insights
python -m finance.cli spending-insights

# Performance analysis
python -m finance.cli performance-analysis

# Investment metrics
python -m finance.cli investment-metrics

# Predictive insights
python -m finance.cli predictive-insights
```

### 5. Generate Reports
```bash
# Generate comprehensive report
python -m finance.cli generate-report

# Check system status
python -m finance.cli status
```

## Data Models

### Account
- **id**: Unique identifier
- **name**: Account name
- **account_type**: checking, savings, credit, investment, crypto
- **institution**: Bank or exchange name
- **account_number**: Masked account number
- **currency**: Account currency
- **is_active**: Account status
- **account_metadata**: Additional account data

### Balance
- **id**: Unique identifier
- **account_id**: Reference to account
- **amount**: Balance amount
- **currency**: Balance currency
- **timestamp**: Balance timestamp
- **balance_metadata**: Additional balance data

### Transaction
- **id**: Unique identifier
- **account_id**: Reference to account
- **transaction_type**: deposit, withdrawal, transfer, purchase, etc.
- **amount**: Transaction amount
- **currency**: Transaction currency
- **description**: Transaction description
- **category**: Transaction category
- **external_id**: External transaction ID
- **timestamp**: Transaction timestamp
- **transaction_metadata**: Additional transaction data

## API Reference

### FinanceManager

#### Core Methods
- `add_bank_connector(bank_name)`: Add bank connector
- `add_crypto_connector(exchange_name)`: Add crypto connector
- `sync_accounts(institution_name, account_type)`: Sync accounts
- `sync_balances(account_id)`: Sync account balances
- `sync_transactions(account_id, days)`: Sync transactions
- `get_portfolio_summary()`: Get portfolio summary
- `get_spending_insights(days)`: Get spending insights
- `set_balance_alert(account_id, threshold, alert_type)`: Set balance alert
- `check_balance_alerts()`: Check and trigger alerts

#### Database Management
- `get_session()`: Get database session
- `set_memory_store(memory_store)`: Set memory system integration

### FinanceAnalytics

#### Analytics Methods
- `get_portfolio_performance(days)`: Portfolio performance analysis
- `get_spending_analysis(days)`: Detailed spending analysis
- `get_budget_analysis(budget_limits)`: Budget tracking
- `get_investment_metrics()`: Investment performance metrics
- `get_predictive_insights()`: Predictive analytics
- `generate_report()`: Comprehensive financial report

### Connectors

#### BankConnector
- `setup_credentials(username, password, api_key)`: Setup credentials
- `connect()`: Establish connection
- `get_accounts()`: Get bank accounts
- `get_balances(account_id)`: Get account balances
- `get_transactions(account_id, days)`: Get transactions

#### CryptoConnector
- `setup_credentials(api_key, api_secret, passphrase)`: Setup credentials
- `connect()`: Establish connection
- `get_accounts()`: Get crypto accounts
- `get_balances(account_id)`: Get crypto balances
- `get_transactions(account_id, days)`: Get crypto transactions
- `get_portfolio_summary()`: Get portfolio summary

## Security

### Credential Encryption
- All credentials are encrypted using Fernet (AES-128)
- Encryption key is stored separately from credentials
- Credentials are never stored in plain text

### API Security
- Secure HTTPS communication with financial institutions
- API keys and secrets are encrypted
- Session management with automatic timeout

### Data Protection
- All sensitive data is encrypted at rest
- Database access is controlled and logged
- Audit trail for all financial operations

## Integration

### Memory System
The finance system integrates with the memory system to:
- Store all financial transactions and balances
- Provide historical analysis capabilities
- Enable natural language queries
- Maintain audit trails

### Feed System
Financial data is integrated into the unified feed system:
- Real-time balance updates
- Transaction notifications
- Alert notifications
- Portfolio performance updates

## Performance

### Database Optimization
- Indexed queries for fast data retrieval
- Efficient relationship mapping
- Optimized balance and transaction queries

### Caching
- In-memory caching for frequently accessed data
- Session-level caching for database operations
- Configurable cache expiration

### Scalability
- Modular connector architecture
- Support for multiple financial institutions
- Horizontal scaling capabilities

## Monitoring

### System Health
- Database connection monitoring
- API endpoint health checks
- Credential validation
- Error tracking and logging

### Performance Metrics
- Response time monitoring
- Database query performance
- API call success rates
- Memory usage tracking

## Troubleshooting

### Common Issues

1. **Connection Errors**
   - Verify credentials are correct
   - Check network connectivity
   - Ensure API endpoints are accessible

2. **Data Sync Issues**
   - Check account permissions
   - Verify API rate limits
   - Review error logs

3. **Performance Issues**
   - Monitor database performance
   - Check cache hit rates
   - Review query optimization

### Debug Mode
Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

### Planned Features
- **Real-time WebSocket Integration**: Live price and balance updates
- **Advanced Portfolio Analytics**: Risk analysis and optimization
- **Tax Reporting**: Automated tax document generation
- **Mobile Integration**: Mobile app support
- **AI-Powered Insights**: Machine learning for financial insights

### Scalability Improvements
- **Microservices Architecture**: Service decomposition
- **Event-Driven Architecture**: Asynchronous processing
- **Cloud Deployment**: Multi-cloud support
- **API Gateway**: Centralized API management

## Contributing

### Development Setup
1. Clone the repository
2. Install dependencies: `pip install -r finance/requirements.txt`
3. Set up development database
4. Run tests: `python -m pytest finance/tests/`

### Code Standards
- Follow PEP 8 style guidelines
- Add comprehensive docstrings
- Include unit tests for new features
- Update documentation for API changes

## License

This project is part of the Megamind system and follows the same licensing terms.

---

*"The ship's treasury is now fully operational!"* 🚢💰

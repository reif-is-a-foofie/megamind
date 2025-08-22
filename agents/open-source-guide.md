# Open Source Assessment Guide

## Before Writing Custom Code

**Always check if the problem has already been solved by a stable, well-maintained open source project.**

## Assessment Criteria

### 1. **Stability & Maturity**
- [ ] Active development (commits in last 6 months)
- [ ] Stable releases (no breaking changes in recent versions)
- [ ] Good documentation and examples
- [ ] Production usage by other projects

### 2. **Community Health**
- [ ] Active community (issues, discussions, PRs)
- [ ] Responsive maintainers
- [ ] Good issue resolution time
- [ ] Regular releases

### 3. **License Compatibility**
- [ ] Compatible with our project license
- [ ] No restrictive commercial terms
- [ ] Allows integration and modification

### 4. **Technical Fit**
- [ ] Meets our specific requirements
- [ ] Integrates well with existing stack
- [ ] Performance characteristics suitable
- [ ] Security practices acceptable

## Common Open Source Solutions by Contract Type

### Financial Integrations
- **Bank APIs:** Plaid, Stripe, Open Banking APIs
- **Crypto:** Coinbase API, Binance API, CoinGecko
- **Accounting:** QuickBooks API, Xero API

### Data Processing
- **ETL:** Apache Airflow, Luigi, Prefect
- **Streaming:** Apache Kafka, Redis Streams
- **Caching:** Redis, Memcached

### UI/UX
- **Terminal UI:** Rich, Textual, Blessed
- **Charts:** Plotly, Matplotlib, Altair
- **Notifications:** Pushbullet, IFTTT

### Knowledge Management
- **Search:** Elasticsearch, Meilisearch
- **Graph DB:** Neo4j, ArangoDB
- **Vector DB:** Pinecone, Weaviate

## Integration Approach

### 1. **Direct Integration**
```python
# Use library directly
import plaid
client = plaid.Client(api_key)
```

### 2. **Wrapper/Adapter**
```python
# Create mission-specific wrapper
class BankConnector:
    def __init__(self):
        self.plaid_client = plaid.Client(api_key)
    
    def get_balance(self):
        # Mission-specific logic
        return self.plaid_client.accounts.get()
```

### 3. **Service Layer**
```python
# Abstract service interface
class FinancialService:
    def get_balance(self):
        # Can switch between Plaid, Stripe, etc.
        pass
```

## Proposal Format

When proposing open source integration:

```json
{
  "contract_id": "finance.01",
  "open_source_solution": {
    "name": "Plaid API",
    "url": "https://plaid.com",
    "license": "MIT",
    "stability": "High - used by major fintech companies",
    "integration_approach": "Direct integration with wrapper",
    "mission_alignment": "Enables bank integration for user financial freedom"
  }
}
```

## Benefits

- **Faster Development:** Leverage battle-tested solutions
- **Better Quality:** Community-tested and maintained
- **Reduced Maintenance:** Less custom code to maintain
- **Mission Alignment:** Focus on integration, not reinvention

## Remember

**"We could write a custom CSV parser, but I think I have a better idea — just use `pandas` with `read_csv`, which handles all the edge cases and integrates directly into your pipeline."**

Always prefer open source over reinventing the wheel.

"""
Finance System CLI - The Ship's Treasury

Command-line interface for the unified finance system, providing easy access
to banking and cryptocurrency operations, analytics, and insights.
"""

import argparse
import json
import sys
from datetime import datetime
from typing import Optional
from decimal import Decimal

from .finance_manager import FinanceManager
from .analytics import FinanceAnalytics


class FinanceCLI:
    """Command-line interface for the finance system."""
    
    def __init__(self, db_path: Optional[str] = None):
        self.finance_manager = FinanceManager(db_path or "finance/finance_data.db")
        self.analytics = FinanceAnalytics(self.finance_manager)
    
    def setup_bank_credentials(self, bank_name: str, username: str, password: str, api_key: Optional[str] = None):
        """Setup encrypted credentials for a bank."""
        try:
            connector = self.finance_manager.add_bank_connector(bank_name)
            connector.setup_credentials(username, password, api_key)
            print(f"✅ Credentials saved for {bank_name}")
        except Exception as e:
            print(f"❌ Error setting up credentials: {e}")
            sys.exit(1)
    
    def setup_crypto_credentials(self, exchange_name: str, api_key: str, api_secret: str, passphrase: Optional[str] = None):
        """Setup encrypted credentials for a crypto exchange."""
        try:
            connector = self.finance_manager.add_crypto_connector(exchange_name)
            connector.setup_credentials(api_key, api_secret, passphrase)
            print(f"✅ Credentials saved for {exchange_name}")
        except Exception as e:
            print(f"❌ Error setting up credentials: {e}")
            sys.exit(1)
    
    def sync_accounts(self, institution_name: str, account_type: str = "bank"):
        """Sync accounts from a financial institution."""
        try:
            # Ensure connector exists
            if account_type == "bank":
                if institution_name not in self.finance_manager.bank_connectors:
                    self.finance_manager.add_bank_connector(institution_name)
            else:
                if institution_name not in self.finance_manager.crypto_connectors:
                    self.finance_manager.add_crypto_connector(institution_name)
            
            success = self.finance_manager.sync_accounts(institution_name, account_type)
            if success:
                print(f"✅ Synced accounts from {institution_name}")
            else:
                print(f"❌ Failed to sync accounts from {institution_name}")
        except Exception as e:
            print(f"❌ Error syncing accounts: {e}")
            sys.exit(1)
    
    def sync_balances(self, account_id: Optional[int] = None):
        """Sync balances for all accounts or a specific account."""
        try:
            success = self.finance_manager.sync_balances(account_id)
            if success:
                if account_id:
                    print(f"✅ Synced balance for account {account_id}")
                else:
                    print("✅ Synced balances for all accounts")
            else:
                print("❌ Failed to sync balances")
        except Exception as e:
            print(f"❌ Error syncing balances: {e}")
            sys.exit(1)
    
    def sync_transactions(self, account_id: Optional[int] = None, days: int = 30):
        """Sync transactions for all accounts or a specific account."""
        try:
            success = self.finance_manager.sync_transactions(account_id, days)
            if success:
                if account_id:
                    print(f"✅ Synced transactions for account {account_id} (last {days} days)")
                else:
                    print(f"✅ Synced transactions for all accounts (last {days} days)")
            else:
                print("❌ Failed to sync transactions")
        except Exception as e:
            print(f"❌ Error syncing transactions: {e}")
            sys.exit(1)
    
    def portfolio_summary(self):
        """Show portfolio summary."""
        try:
            summary = self.finance_manager.get_portfolio_summary()
            
            print("\n💰 Portfolio Summary")
            print("=" * 50)
            print(f"Total Value: ${summary.get('total_value_usd', 0):,.2f}")
            print(f"24h Change: ${summary.get('change_24h_usd', 0):+,.2f} ({summary.get('change_24h_percent', 0):+.2f}%)")
            print(f"Number of Accounts: {summary.get('num_accounts', 0)}")
            
            if summary.get('accounts'):
                print("\n📊 Account Breakdown:")
                for account in summary['accounts']:
                    print(f"  {account['name']} ({account['institution']})")
                    print(f"    Balance: {account['balance']} {account['currency']}")
                    print(f"    Value: ${account['value_usd']:,.2f}")
                    print()
            
        except Exception as e:
            print(f"❌ Error getting portfolio summary: {e}")
            sys.exit(1)
    
    def spending_insights(self, days: int = 30):
        """Show spending insights."""
        try:
            insights = self.finance_manager.get_spending_insights(days)
            
            print(f"\n💸 Spending Insights (Last {days} days)")
            print("=" * 50)
            print(f"Total Spending: ${insights.get('total_spending', 0):,.2f}")
            print(f"Number of Transactions: {insights.get('num_transactions', 0)}")
            print(f"Average Transaction: ${insights.get('average_transaction', 0):,.2f}")
            
            if insights.get('category_breakdown'):
                print("\n📈 Category Breakdown:")
                for category, data in insights['category_breakdown'].items():
                    print(f"  {category}: ${data['total']:,.2f} ({data['count']} transactions)")
            
            if insights.get('actions_by_type'):
                print("\n🎯 Action Types:")
                for action_type, count in insights['actions_by_type'].items():
                    print(f"  {action_type}: {count}")
            
        except Exception as e:
            print(f"❌ Error getting spending insights: {e}")
            sys.exit(1)
    
    def performance_analysis(self, days: int = 30):
        """Show portfolio performance analysis."""
        try:
            performance = self.analytics.get_portfolio_performance(days)
            
            print(f"\n📈 Portfolio Performance (Last {days} days)")
            print("=" * 50)
            print(f"Total Value: ${performance.get('total_value', 0):,.2f}")
            print(f"Total Change: ${performance.get('total_change', 0):+,.2f}")
            print(f"Overall Change: {performance.get('overall_change_percent', 0):+.2f}%")
            
            if performance.get('best_performer'):
                best = performance['best_performer']
                print(f"\n🏆 Best Performer: {best['name']}")
                print(f"  Change: {best['change_percent']:+.2f}%")
            
            if performance.get('worst_performer'):
                worst = performance['worst_performer']
                print(f"\n📉 Worst Performer: {worst['name']}")
                print(f"  Change: {worst['change_percent']:+.2f}%")
            
            if performance.get('account_performance'):
                print(f"\n📊 Account Performance:")
                for account in performance['account_performance'][:5]:  # Show top 5
                    print(f"  {account['name']}: {account['change_percent']:+.2f}%")
            
        except Exception as e:
            print(f"❌ Error getting performance analysis: {e}")
            sys.exit(1)
    
    def investment_metrics(self):
        """Show investment-specific metrics."""
        try:
            metrics = self.analytics.get_investment_metrics()
            
            print("\n🚀 Investment Metrics")
            print("=" * 50)
            print(f"Total Investments: {metrics.get('total_investments', 0)}")
            print(f"Total Value: ${metrics.get('total_value', 0):,.2f}")
            print(f"Total Return: ${metrics.get('total_return', 0):+,.2f}")
            print(f"Overall Return: {metrics.get('overall_return_percent', 0):+.2f}%")
            
            if metrics.get('best_investment'):
                best = metrics['best_investment']
                print(f"\n🏆 Best Investment: {best['name']}")
                print(f"  Return: {best['return_percent']:+.2f}%")
            
            if metrics.get('worst_investment'):
                worst = metrics['worst_investment']
                print(f"\n📉 Worst Investment: {worst['name']}")
                print(f"  Return: {worst['return_percent']:+.2f}%")
            
        except Exception as e:
            print(f"❌ Error getting investment metrics: {e}")
            sys.exit(1)
    
    def predictive_insights(self):
        """Show predictive insights."""
        try:
            insights = self.analytics.get_predictive_insights()
            
            print("\n🔮 Predictive Insights")
            print("=" * 50)
            print(f"Predicted Monthly Spending: ${insights.get('predicted_monthly_spending', 0):,.2f}")
            
            if insights.get('spending_forecast'):
                print("\n📊 Spending Forecast:")
                for category, amount in insights['spending_forecast'].items():
                    print(f"  {category}: ${float(amount):,.2f}")
            
            if insights.get('budget_recommendations'):
                print("\n💰 Budget Recommendations:")
                for category, amount in insights['budget_recommendations'].items():
                    print(f"  {category}: ${float(amount):,.2f}")
            
            if insights.get('risk_factors'):
                print("\n⚠️  Risk Factors:")
                for risk in insights['risk_factors']:
                    print(f"  • {risk}")
            
            if insights.get('opportunities'):
                print("\n💡 Opportunities:")
                for opportunity in insights['opportunities']:
                    print(f"  • {opportunity}")
            
        except Exception as e:
            print(f"❌ Error getting predictive insights: {e}")
            sys.exit(1)
    
    def set_balance_alert(self, account_id: int, threshold: str, alert_type: str = "low"):
        """Set balance alert for an account."""
        try:
            threshold_decimal = Decimal(threshold)
            success = self.finance_manager.set_balance_alert(account_id, threshold_decimal, alert_type)
            if success:
                print(f"✅ Set {alert_type} balance alert for account {account_id}: {threshold}")
            else:
                print(f"❌ Failed to set balance alert")
        except Exception as e:
            print(f"❌ Error setting balance alert: {e}")
            sys.exit(1)
    
    def check_alerts(self):
        """Check and trigger balance alerts."""
        try:
            success = self.finance_manager.check_balance_alerts()
            if success:
                print("✅ Balance alerts checked")
            else:
                print("❌ Failed to check balance alerts")
        except Exception as e:
            print(f"❌ Error checking alerts: {e}")
            sys.exit(1)
    
    def generate_report(self):
        """Generate comprehensive financial report."""
        try:
            report = self.analytics.generate_report()
            
            print("\n📋 Financial Report")
            print("=" * 50)
            print(f"Report Date: {report.get('report_date', 'N/A')}")
            
            summary = report.get('summary', {})
            print(f"\n📊 Summary:")
            print(f"  Total Portfolio Value: ${summary.get('total_portfolio_value', '0')}")
            print(f"  Portfolio Change: {summary.get('portfolio_change_percent', 0):+.2f}%")
            print(f"  Monthly Spending: ${summary.get('total_monthly_spending', '0')}")
            print(f"  Transactions: {summary.get('num_transactions', 0)}")
            
            if summary.get('key_insights'):
                print(f"\n💡 Key Insights:")
                for insight in summary['key_insights']:
                    print(f"  • {insight}")
            
            # Save report to file
            filename = f"finance_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            print(f"\n📁 Report saved to: {filename}")
            
        except Exception as e:
            print(f"❌ Error generating report: {e}")
            sys.exit(1)
    
    def status(self):
        """Show system status."""
        try:
            with self.finance_manager.get_session() as session:
                from .models import Account, Transaction, Balance
                
                num_accounts = session.query(Account).count()
                num_transactions = session.query(Transaction).count()
                num_balances = session.query(Balance).count()
            
            print("\n💰 Finance System Status")
            print("=" * 30)
            print(f"Database: {self.finance_manager.db_path}")
            print(f"Accounts: {num_accounts}")
            print(f"Transactions: {num_transactions}")
            print(f"Balance Records: {num_balances}")
            print(f"Bank Connectors: {len(self.finance_manager.bank_connectors)}")
            print(f"Crypto Connectors: {len(self.finance_manager.crypto_connectors)}")
            
        except Exception as e:
            print(f"❌ Error getting status: {e}")
            sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Finance System CLI - The Ship's Treasury",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Setup bank credentials
  python -m finance.cli setup-bank chase username password
  
  # Setup crypto credentials
  python -m finance.cli setup-crypto coinbase api_key api_secret
  
  # Sync accounts
  python -m finance.cli sync-accounts chase bank
  
  # Sync balances
  python -m finance.cli sync-balances
  
  # Show portfolio summary
  python -m finance.cli portfolio-summary
  
  # Generate report
  python -m finance.cli generate-report
        """
    )
    
    parser.add_argument("--db-path", help="Database path")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Setup credentials
    bank_creds_parser = subparsers.add_parser("setup-bank", help="Setup bank credentials")
    bank_creds_parser.add_argument("bank_name", help="Bank name")
    bank_creds_parser.add_argument("username", help="Username")
    bank_creds_parser.add_argument("password", help="Password")
    bank_creds_parser.add_argument("--api-key", help="API key (optional)")
    
    crypto_creds_parser = subparsers.add_parser("setup-crypto", help="Setup crypto credentials")
    crypto_creds_parser.add_argument("exchange_name", help="Exchange name")
    crypto_creds_parser.add_argument("api_key", help="API key")
    crypto_creds_parser.add_argument("api_secret", help="API secret")
    crypto_creds_parser.add_argument("--passphrase", help="Passphrase (optional)")
    
    # Sync operations
    sync_accounts_parser = subparsers.add_parser("sync-accounts", help="Sync accounts")
    sync_accounts_parser.add_argument("institution_name", help="Institution name")
    sync_accounts_parser.add_argument("--type", choices=["bank", "crypto"], default="bank", help="Account type")
    
    sync_balances_parser = subparsers.add_parser("sync-balances", help="Sync balances")
    sync_balances_parser.add_argument("--account-id", type=int, help="Specific account ID")
    
    sync_transactions_parser = subparsers.add_parser("sync-transactions", help="Sync transactions")
    sync_transactions_parser.add_argument("--account-id", type=int, help="Specific account ID")
    sync_transactions_parser.add_argument("--days", type=int, default=30, help="Days to sync")
    
    # Analytics
    subparsers.add_parser("portfolio-summary", help="Show portfolio summary")
    subparsers.add_parser("spending-insights", help="Show spending insights")
    subparsers.add_parser("performance-analysis", help="Show performance analysis")
    subparsers.add_parser("investment-metrics", help="Show investment metrics")
    subparsers.add_parser("predictive-insights", help="Show predictive insights")
    
    # Alerts
    alert_parser = subparsers.add_parser("set-alert", help="Set balance alert")
    alert_parser.add_argument("account_id", type=int, help="Account ID")
    alert_parser.add_argument("threshold", help="Threshold amount")
    alert_parser.add_argument("--type", choices=["low", "high"], default="low", help="Alert type")
    
    subparsers.add_parser("check-alerts", help="Check balance alerts")
    
    # Reports
    subparsers.add_parser("generate-report", help="Generate financial report")
    subparsers.add_parser("status", help="Show system status")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = FinanceCLI(args.db_path)
    
    # Execute command
    if args.command == "setup-bank":
        cli.setup_bank_credentials(args.bank_name, args.username, args.password, args.api_key)
    elif args.command == "setup-crypto":
        cli.setup_crypto_credentials(args.exchange_name, args.api_key, args.api_secret, args.passphrase)
    elif args.command == "sync-accounts":
        cli.sync_accounts(args.institution_name, args.type)
    elif args.command == "sync-balances":
        cli.sync_balances(args.account_id)
    elif args.command == "sync-transactions":
        cli.sync_transactions(args.account_id, args.days)
    elif args.command == "portfolio-summary":
        cli.portfolio_summary()
    elif args.command == "spending-insights":
        cli.spending_insights()
    elif args.command == "performance-analysis":
        cli.performance_analysis()
    elif args.command == "investment-metrics":
        cli.investment_metrics()
    elif args.command == "predictive-insights":
        cli.predictive_insights()
    elif args.command == "set-alert":
        cli.set_balance_alert(args.account_id, args.threshold, args.type)
    elif args.command == "check-alerts":
        cli.check_alerts()
    elif args.command == "generate-report":
        cli.generate_report()
    elif args.command == "status":
        cli.status()


if __name__ == "__main__":
    main()

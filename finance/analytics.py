"""
Finance Analytics - Advanced Financial Insights

Provides advanced analytics and insights for financial data,
including portfolio performance, spending patterns, and predictive analysis.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from decimal import Decimal
from collections import defaultdict

from .models import Account, Transaction, Balance
from .finance_manager import FinanceManager

logger = logging.getLogger(__name__)


class FinanceAnalytics:
    """
    Advanced financial analytics and insights.
    
    Features:
    - Portfolio performance analysis
    - Spending pattern recognition
    - Budget tracking and alerts
    - Investment performance metrics
    - Predictive spending analysis
    """
    
    def __init__(self, finance_manager: FinanceManager):
        self.finance_manager = finance_manager
    
    def get_portfolio_performance(self, days: int = 30) -> Dict[str, Any]:
        """Get detailed portfolio performance metrics."""
        try:
            with self.finance_manager.get_session() as session:
                # Get all accounts
                accounts = session.query(Account).filter(Account.is_active == True).all()
                
                performance_data = {
                    "period_days": days,
                    "total_accounts": len(accounts),
                    "account_performance": [],
                    "total_value": Decimal('0'),
                    "total_change": Decimal('0'),
                    "best_performer": None,
                    "worst_performer": None
                }
                
                best_change = Decimal('-999999')
                worst_change = Decimal('999999')
                
                for account in accounts:
                    # Get balances for the period
                    cutoff_date = datetime.utcnow() - timedelta(days=days)
                    balances = session.query(Balance).filter(
                        Balance.account_id == account.id,
                        Balance.timestamp >= cutoff_date
                    ).order_by(Balance.timestamp).all()
                    
                    if len(balances) >= 2:
                        start_balance = balances[0].amount
                        end_balance = balances[-1].amount
                        change = end_balance - start_balance
                        change_percent = (change / start_balance * 100) if start_balance > 0 else 0
                        
                        account_perf = {
                            "account_id": account.id,
                            "name": account.name,
                            "type": account.account_type,
                            "institution": account.institution,
                            "start_balance": start_balance,
                            "end_balance": end_balance,
                            "change": change,
                            "change_percent": change_percent,
                            "currency": balances[0].currency
                        }
                        
                        performance_data["account_performance"].append(account_perf)
                        performance_data["total_value"] += end_balance
                        performance_data["total_change"] += change
                        
                        # Track best/worst performers
                        if change_percent > best_change:
                            best_change = change_percent
                            performance_data["best_performer"] = account_perf
                        
                        if change_percent < worst_change:
                            worst_change = change_percent
                            performance_data["worst_performer"] = account_perf
                
                # Calculate overall performance
                if performance_data["total_value"] > 0:
                    performance_data["overall_change_percent"] = (
                        performance_data["total_change"] / 
                        (performance_data["total_value"] - performance_data["total_change"]) * 100
                    )
                else:
                    performance_data["overall_change_percent"] = 0
                
                performance_data["timestamp"] = datetime.utcnow()
                return performance_data
                
        except Exception as e:
            logger.error(f"Failed to get portfolio performance: {e}")
            return {}
    
    def get_spending_analysis(self, days: int = 30) -> Dict[str, Any]:
        """Get detailed spending analysis and patterns."""
        try:
            with self.finance_manager.get_session() as session:
                cutoff_date = datetime.utcnow() - timedelta(days=days)
                
                # Get all spending transactions
                transactions = session.query(Transaction).filter(
                    Transaction.timestamp >= cutoff_date,
                    Transaction.transaction_type.in_(["purchase", "payment", "withdrawal"]),
                    Transaction.amount > 0
                ).all()
                
                analysis = {
                    "period_days": days,
                    "total_spending": Decimal('0'),
                    "num_transactions": len(transactions),
                    "average_transaction": Decimal('0'),
                    "category_breakdown": {},
                    "daily_spending": {},
                    "account_breakdown": {},
                    "trends": {}
                }
                
                # Calculate totals and averages
                for tx in transactions:
                    analysis["total_spending"] += tx.amount
                    
                    # Category breakdown
                    category = tx.category or "uncategorized"
                    if category not in analysis["category_breakdown"]:
                        analysis["category_breakdown"][category] = {
                            "total": Decimal('0'),
                            "count": 0,
                            "average": Decimal('0')
                        }
                    analysis["category_breakdown"][category]["total"] += tx.amount
                    analysis["category_breakdown"][category]["count"] += 1
                    
                    # Daily breakdown
                    day_key = tx.timestamp.strftime("%Y-%m-%d")
                    if day_key not in analysis["daily_spending"]:
                        analysis["daily_spending"][day_key] = Decimal('0')
                    analysis["daily_spending"][day_key] += tx.amount
                    
                    # Account breakdown
                    account_name = tx.account.name
                    if account_name not in analysis["account_breakdown"]:
                        analysis["account_breakdown"][account_name] = Decimal('0')
                    analysis["account_breakdown"][account_name] += tx.amount
                
                # Calculate averages
                if analysis["num_transactions"] > 0:
                    analysis["average_transaction"] = analysis["total_spending"] / analysis["num_transactions"]
                
                # Calculate category averages
                for category_data in analysis["category_breakdown"].values():
                    if category_data["count"] > 0:
                        category_data["average"] = category_data["total"] / category_data["count"]
                
                # Identify trends
                analysis["trends"] = self._analyze_spending_trends(analysis["daily_spending"])
                
                analysis["timestamp"] = datetime.utcnow()
                return analysis
                
        except Exception as e:
            logger.error(f"Failed to get spending analysis: {e}")
            return {}
    
    def _analyze_spending_trends(self, daily_spending: Dict[str, Decimal]) -> Dict[str, Any]:
        """Analyze spending trends over time."""
        if not daily_spending:
            return {}
        
        # Sort by date
        sorted_days = sorted(daily_spending.items())
        values = [float(amount) for _, amount in sorted_days]
        
        # Calculate basic trends
        if len(values) >= 2:
            trend_direction = "increasing" if values[-1] > values[0] else "decreasing"
            trend_strength = abs(values[-1] - values[0]) / max(values[0], 1)
            
            # Find peak spending day
            peak_day = max(daily_spending.items(), key=lambda x: x[1])
            
            # Calculate volatility (standard deviation)
            mean = sum(values) / len(values)
            variance = sum((x - mean) ** 2 for x in values) / len(values)
            volatility = variance ** 0.5
            
            return {
                "direction": trend_direction,
                "strength": trend_strength,
                "peak_day": peak_day[0],
                "peak_amount": str(peak_day[1]),
                "volatility": volatility,
                "mean_daily_spending": mean
            }
        
        return {}
    
    def get_budget_analysis(self, budget_limits: Dict[str, Decimal]) -> Dict[str, Any]:
        """Analyze spending against budget limits."""
        try:
            # Get current month spending
            current_month = datetime.utcnow().replace(day=1)
            days_in_month = (datetime.utcnow().replace(day=1) + timedelta(days=32)).replace(day=1) - current_month
            days_elapsed = (datetime.utcnow() - current_month).days
            
            spending_analysis = self.get_spending_analysis(days_elapsed)
            
            budget_analysis = {
                "month": current_month.strftime("%Y-%m"),
                "days_elapsed": days_elapsed,
                "days_total": days_in_month.days,
                "progress_percent": (days_elapsed / days_in_month.days) * 100,
                "category_status": {},
                "overall_status": "on_track",
                "alerts": []
            }
            
            total_budget = Decimal('0')
            total_spent = spending_analysis.get("total_spending", Decimal('0'))
            
            for category, limit in budget_limits.items():
                category_spent = spending_analysis.get("category_breakdown", {}).get(category, {}).get("total", Decimal('0'))
                spent_percent = (category_spent / limit * 100) if limit > 0 else 0
                
                status = "on_track"
                if spent_percent > 100:
                    status = "over_budget"
                elif spent_percent > 80:
                    status = "near_limit"
                
                budget_analysis["category_status"][category] = {
                    "limit": str(limit),
                    "spent": str(category_spent),
                    "remaining": str(limit - category_spent),
                    "spent_percent": spent_percent,
                    "status": status
                }
                
                total_budget += limit
                
                # Generate alerts
                if spent_percent > 100:
                    budget_analysis["alerts"].append(f"OVER BUDGET: {category} exceeded by {spent_percent - 100:.1f}%")
                elif spent_percent > 80:
                    budget_analysis["alerts"].append(f"WARNING: {category} at {spent_percent:.1f}% of budget")
            
            # Overall budget status
            if total_budget > 0:
                overall_spent_percent = (total_spent / total_budget * 100)
                if overall_spent_percent > 100:
                    budget_analysis["overall_status"] = "over_budget"
                elif overall_spent_percent > 80:
                    budget_analysis["overall_status"] = "near_limit"
                
                budget_analysis["overall"] = {
                    "total_budget": str(total_budget),
                    "total_spent": str(total_spent),
                    "remaining": str(total_budget - total_spent),
                    "spent_percent": overall_spent_percent
                }
            
            budget_analysis["timestamp"] = datetime.utcnow()
            return budget_analysis
            
        except Exception as e:
            logger.error(f"Failed to get budget analysis: {e}")
            return {}
    
    def get_investment_metrics(self) -> Dict[str, Any]:
        """Get investment-specific performance metrics."""
        try:
            with self.finance_manager.get_session() as session:
                # Get investment accounts
                investment_accounts = session.query(Account).filter(
                    Account.account_type.in_(["investment", "crypto"])
                ).all()
                
                metrics = {
                    "total_investments": len(investment_accounts),
                    "accounts": [],
                    "total_value": Decimal('0'),
                    "total_return": Decimal('0'),
                    "best_investment": None,
                    "worst_investment": None
                }
                
                best_return = Decimal('-999999')
                worst_return = Decimal('999999')
                
                for account in investment_accounts:
                    # Get recent balances for return calculation
                    balances = session.query(Balance).filter(
                        Balance.account_id == account.id
                    ).order_by(Balance.timestamp.desc()).limit(2).all()
                    
                    if len(balances) >= 2:
                        current_balance = balances[0].amount
                        previous_balance = balances[1].amount
                        return_amount = current_balance - previous_balance
                        return_percent = (return_amount / previous_balance * 100) if previous_balance > 0 else 0
                        
                        account_metrics = {
                            "account_id": account.id,
                            "name": account.name,
                            "type": account.account_type,
                            "current_value": current_balance,
                            "return_amount": return_amount,
                            "return_percent": return_percent,
                            "currency": balances[0].currency
                        }
                        
                        metrics["accounts"].append(account_metrics)
                        metrics["total_value"] += current_balance
                        metrics["total_return"] += return_amount
                        
                        # Track best/worst performers
                        if return_percent > best_return:
                            best_return = return_percent
                            metrics["best_investment"] = account_metrics
                        
                        if return_percent < worst_return:
                            worst_return = return_percent
                            metrics["worst_investment"] = account_metrics
                
                # Calculate overall return
                if metrics["total_value"] > 0:
                    metrics["overall_return_percent"] = (
                        metrics["total_return"] / 
                        (metrics["total_value"] - metrics["total_return"]) * 100
                    )
                else:
                    metrics["overall_return_percent"] = 0
                
                metrics["timestamp"] = datetime.utcnow()
                return metrics
                
        except Exception as e:
            logger.error(f"Failed to get investment metrics: {e}")
            return {}
    
    def get_predictive_insights(self) -> Dict[str, Any]:
        """Generate predictive insights based on historical data."""
        try:
            # Get historical spending data
            spending_analysis = self.get_spending_analysis(90)  # 3 months
            
            insights = {
                "predicted_monthly_spending": Decimal('0'),
                "spending_forecast": {},
                "budget_recommendations": {},
                "risk_factors": [],
                "opportunities": []
            }
            
            if spending_analysis:
                # Simple prediction based on average daily spending
                avg_daily = spending_analysis.get("average_transaction", Decimal('0'))
                num_transactions = spending_analysis.get("num_transactions", 0)
                days = spending_analysis.get("period_days", 30)
                
                if days > 0:
                    avg_daily_spending = spending_analysis.get("total_spending", Decimal('0')) / days
                    predicted_monthly = avg_daily_spending * 30
                    insights["predicted_monthly_spending"] = predicted_monthly
                    
                    # Category forecasts
                    category_breakdown = spending_analysis.get("category_breakdown", {})
                    for category, data in category_breakdown.items():
                        avg_category_daily = data["total"] / days
                        predicted_category_monthly = avg_category_daily * 30
                        insights["spending_forecast"][category] = str(predicted_category_monthly)
                    
                    # Budget recommendations
                    for category, data in category_breakdown.items():
                        current_monthly = (data["total"] / days) * 30
                        recommended_budget = current_monthly * Decimal('1.1')  # 10% buffer
                        insights["budget_recommendations"][category] = str(recommended_budget)
                    
                    # Risk factors
                    if predicted_monthly > Decimal('5000'):
                        insights["risk_factors"].append("High predicted monthly spending")
                    
                    # Opportunities
                    if avg_daily_spending < Decimal('50'):
                        insights["opportunities"].append("Low daily spending - good savings potential")
            
            insights["timestamp"] = datetime.utcnow()
            return insights
            
        except Exception as e:
            logger.error(f"Failed to get predictive insights: {e}")
            return {}
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive financial report."""
        try:
            report = {
                "report_date": datetime.utcnow().isoformat(),
                "portfolio_performance": self.get_portfolio_performance(),
                "spending_analysis": self.get_spending_analysis(),
                "investment_metrics": self.get_investment_metrics(),
                "predictive_insights": self.get_predictive_insights(),
                "summary": {}
            }
            
            # Generate summary
            portfolio = report["portfolio_performance"]
            spending = report["spending_analysis"]
            
            report["summary"] = {
                "total_portfolio_value": str(portfolio.get("total_value", Decimal('0'))),
                "portfolio_change_percent": portfolio.get("overall_change_percent", 0),
                "total_monthly_spending": str(spending.get("total_spending", Decimal('0'))),
                "num_transactions": spending.get("num_transactions", 0),
                "key_insights": []
            }
            
            # Add key insights
            if portfolio.get("best_performer"):
                report["summary"]["key_insights"].append(
                    f"Best performing account: {portfolio['best_performer']['name']} "
                    f"({portfolio['best_performer']['change_percent']:.1f}%)"
                )
            
            if spending.get("trends", {}).get("direction"):
                report["summary"]["key_insights"].append(
                    f"Spending trend: {spending['trends']['direction']}"
                )
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate report: {e}")
            return {}

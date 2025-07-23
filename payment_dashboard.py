#!/usr/bin/env python3
"""
Payment Dashboard
Display complete payment infrastructure metrics and analytics
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List
import json

class PaymentDashboard:
    """Dashboard for payment infrastructure metrics"""
    
    def __init__(self):
        self.db_path = "payment_infrastructure.db"
    
    def get_dashboard_data(self) -> Dict:
        """Get comprehensive dashboard data"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Get customers data
            customers_df = pd.read_sql_query("SELECT * FROM customers", conn)
            
            # Get payment intents data
            payments_df = pd.read_sql_query("SELECT * FROM payment_intents", conn)
            
            # Get subscriptions data
            subscriptions_df = pd.read_sql_query("SELECT * FROM subscriptions", conn)
            
            # Get revenue analytics data
            revenue_df = pd.read_sql_query("SELECT * FROM revenue_analytics", conn)
            
            # Get tax records data
            tax_df = pd.read_sql_query("SELECT * FROM tax_records", conn)
            
            # Get webhook events data
            webhooks_df = pd.read_sql_query("SELECT * FROM webhook_events", conn)
            
            conn.close()
            
            # Calculate metrics
            total_customers = len(customers_df)
            total_payments = len(payments_df)
            successful_payments = len(payments_df[payments_df['status'] == 'succeeded'])
            total_subscriptions = len(subscriptions_df)
            active_subscriptions = len(subscriptions_df[subscriptions_df['status'] == 'active'])
            
            # Calculate revenue metrics
            total_revenue = revenue_df['revenue'].sum() if len(revenue_df) > 0 else 0
            total_tax_collected = tax_df['tax_amount'].sum() if len(tax_df) > 0 else 0
            
            # Calculate MRR and ARR
            monthly_subscriptions = subscriptions_df[
                (subscriptions_df['status'] == 'active') & 
                (subscriptions_df['interval'] == 'month')
            ]
            yearly_subscriptions = subscriptions_df[
                (subscriptions_df['status'] == 'active') & 
                (subscriptions_df['interval'] == 'year')
            ]
            
            mrr = monthly_subscriptions['amount'].sum() if len(monthly_subscriptions) > 0 else 0
            arr = yearly_subscriptions['amount'].sum() if len(yearly_subscriptions) > 0 else 0
            
            # Calculate conversion rates
            payment_success_rate = (successful_payments / total_payments * 100) if total_payments > 0 else 0
            subscription_conversion_rate = (active_subscriptions / total_subscriptions * 100) if total_subscriptions > 0 else 0
            
            # Get recent activity
            recent_payments = payments_df.head(5).to_dict('records') if len(payments_df) > 0 else []
            recent_subscriptions = subscriptions_df.head(5).to_dict('records') if len(subscriptions_df) > 0 else []
            recent_webhooks = webhooks_df.head(5).to_dict('records') if len(webhooks_df) > 0 else []
            
            # Get customer breakdown
            paying_customers = len(customers_df[customers_df['total_spent'] > 0])
            new_customers_30d = len(customers_df[
                customers_df['created_at'] >= (datetime.now() - timedelta(days=30)).isoformat()
            ])
            
            return {
                "overview": {
                    "total_customers": total_customers,
                    "paying_customers": paying_customers,
                    "new_customers_30d": new_customers_30d,
                    "total_payments": total_payments,
                    "successful_payments": successful_payments,
                    "payment_success_rate": payment_success_rate,
                    "total_subscriptions": total_subscriptions,
                    "active_subscriptions": active_subscriptions,
                    "subscription_conversion_rate": subscription_conversion_rate,
                    "total_revenue": total_revenue,
                    "total_tax_collected": total_tax_collected,
                    "mrr": mrr,
                    "arr": arr
                },
                "recent_payments": recent_payments,
                "recent_subscriptions": recent_subscriptions,
                "recent_webhooks": recent_webhooks,
                "revenue_trends": revenue_df.to_dict('records') if len(revenue_df) > 0 else [],
                "customer_metrics": {
                    "average_spend": customers_df['total_spent'].mean() if len(customers_df) > 0 else 0,
                    "top_spenders": customers_df.nlargest(5, 'total_spent').to_dict('records') if len(customers_df) > 0 else []
                }
            }
            
        except Exception as e:
            print(f"❌ Failed to get dashboard data: {e}")
            return {}
    
    def print_dashboard(self):
        """Print comprehensive dashboard"""
        data = self.get_dashboard_data()
        
        if not data:
            print("❌ No dashboard data available")
            return
        
        print("💳 COMPLETE PAYMENT INFRASTRUCTURE DASHBOARD")
        print("=" * 60)
        print(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Overview Metrics
        overview = data["overview"]
        print("📊 OVERVIEW METRICS")
        print("-" * 30)
        print(f"👥 Total Customers: {overview['total_customers']}")
        print(f"💰 Paying Customers: {overview['paying_customers']}")
        print(f"🆕 New Customers (30d): {overview['new_customers_30d']}")
        print(f"💳 Total Payments: {overview['total_payments']}")
        print(f"✅ Successful Payments: {overview['successful_payments']}")
        print(f"📈 Payment Success Rate: {overview['payment_success_rate']:.1f}%")
        print(f"🔄 Total Subscriptions: {overview['total_subscriptions']}")
        print(f"✅ Active Subscriptions: {overview['active_subscriptions']}")
        print(f"📊 Subscription Conversion: {overview['subscription_conversion_rate']:.1f}%")
        print()
        
        # Revenue Metrics
        print("💰 REVENUE METRICS")
        print("-" * 30)
        print(f"💵 Total Revenue: ${overview['total_revenue']/100:.2f}")
        print(f"🧾 Tax Collected: ${overview['total_tax_collected']/100:.2f}")
        print(f"📈 Monthly Recurring Revenue (MRR): ${overview['mrr']/100:.2f}")
        print(f"📊 Annual Recurring Revenue (ARR): ${overview['arr']/100:.2f}")
        print()
        
        # Customer Metrics
        customer_metrics = data["customer_metrics"]
        print("👥 CUSTOMER METRICS")
        print("-" * 30)
        print(f"💸 Average Customer Spend: ${customer_metrics['average_spend']/100:.2f}")
        
        top_spenders = customer_metrics["top_spenders"]
        if top_spenders:
            print(f"🏆 Top Spenders:")
            for i, customer in enumerate(top_spenders[:3], 1):
                print(f"   {i}. {customer.get('name', 'Unknown')}: ${customer.get('total_spent', 0)/100:.2f}")
        print()
        
        # Recent Payments
        recent_payments = data["recent_payments"]
        if recent_payments:
            print("💳 RECENT PAYMENTS")
            print("-" * 30)
            for payment in recent_payments[:3]:
                created_at = payment.get('created_at', 'Unknown')
                if created_at != 'Unknown':
                    try:
                        dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        created_at = dt.strftime('%m/%d %H:%M')
                    except:
                        pass
                
                print(f"   ${payment.get('amount', 0)/100:.2f} {payment.get('currency', 'usd').upper()}")
                print(f"   Status: {payment.get('status', 'Unknown').title()}")
                print(f"   Date: {created_at}")
                print()
        
        # Recent Subscriptions
        recent_subscriptions = data["recent_subscriptions"]
        if recent_subscriptions:
            print("🔄 RECENT SUBSCRIPTIONS")
            print("-" * 30)
            for sub in recent_subscriptions[:3]:
                created_at = sub.get('created_at', 'Unknown')
                if created_at != 'Unknown':
                    try:
                        dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        created_at = dt.strftime('%m/%d %H:%M')
                    except:
                        pass
                
                print(f"   ${sub.get('amount', 0)/100:.2f} {sub.get('currency', 'usd').upper()}")
                print(f"   Status: {sub.get('status', 'Unknown').title()}")
                print(f"   Interval: {sub.get('interval', 'Unknown').title()}")
                print(f"   Date: {created_at}")
                print()
        
        # Recent Webhooks
        recent_webhooks = data["recent_webhooks"]
        if recent_webhooks:
            print("📡 RECENT WEBHOOK EVENTS")
            print("-" * 30)
            for webhook in recent_webhooks[:3]:
                processed_at = webhook.get('processed_at', 'Unknown')
                if processed_at != 'Unknown':
                    try:
                        dt = datetime.fromisoformat(processed_at.replace('Z', '+00:00'))
                        processed_at = dt.strftime('%m/%d %H:%M')
                    except:
                        pass
                
                print(f"   {webhook.get('event_type', 'Unknown').replace('_', ' ').title()}")
                print(f"   Status: {webhook.get('status', 'Unknown').title()}")
                print(f"   Processed: {processed_at}")
                print()
        
        # Performance Insights
        print("💡 PERFORMANCE INSIGHTS")
        print("-" * 30)
        
        if overview['total_payments'] > 0:
            if overview['payment_success_rate'] > 95:
                print("✅ Excellent payment success rate! Your payment processing is working well.")
            elif overview['payment_success_rate'] > 90:
                print("🟡 Good payment success rate. Consider optimizing payment flow.")
            else:
                print("🔴 Low payment success rate. Review payment processing and fraud detection.")
            
            if overview['subscription_conversion_rate'] > 80:
                print("✅ High subscription conversion rate! Your subscription model is effective.")
            elif overview['subscription_conversion_rate'] > 60:
                print("🟡 Moderate subscription conversion rate. Consider improving onboarding.")
            else:
                print("🔴 Low subscription conversion rate. Focus on subscription optimization.")
            
            if overview['mrr'] > 10000:  # $100 MRR
                print("💰 Strong MRR! Your recurring revenue model is working.")
            elif overview['mrr'] > 1000:  # $10 MRR
                print("🟡 Growing MRR. Focus on scaling successful subscriptions.")
            else:
                print("🔴 Low MRR. Focus on converting customers to subscriptions.")
            
            if overview['total_customers'] > 0:
                customer_ltv = overview['total_revenue'] / overview['total_customers']
                print(f"💎 Customer LTV: ${customer_ltv/100:.2f}")
        else:
            print("📝 No payment activity yet. Start processing real payments!")
        
        print()
        
        # Recommendations
        print("🎯 RECOMMENDATIONS")
        print("-" * 30)
        
        if overview['total_payments'] == 0:
            print("1. 🚀 Start processing real payments")
            print("2. 💳 Set up payment methods")
            print("3. 🔄 Create subscription plans")
            print("4. 📊 Implement analytics tracking")
            print("5. 🧾 Set up tax calculation")
        else:
            if overview['payment_success_rate'] < 95:
                print("1. 🔍 Review failed payment reasons")
                print("2. 💳 Optimize payment method options")
                print("3. 🛡️ Improve fraud detection")
                print("4. 📱 Enhance mobile payment experience")
                print("5. 🔄 Test payment flow regularly")
            
            if overview['subscription_conversion_rate'] < 70:
                print("1. 🎯 Improve subscription onboarding")
                print("2. 💰 Optimize pricing strategy")
                print("3. 🎁 Add subscription incentives")
                print("4. 📧 Enhance subscription marketing")
                print("5. 🔄 Simplify subscription process")
            
            if overview['mrr'] < 1000:
                print("1. 📈 Focus on high-value subscriptions")
                print("2. 🎯 Target enterprise customers")
                print("3. 💰 Increase subscription prices")
                print("4. 🔄 Upsell existing customers")
                print("5. 📊 Optimize subscription retention")
        
        print()
        print("🚀 Ready to scale your payment infrastructure!")

def main():
    """Main execution function"""
    dashboard = PaymentDashboard()
    dashboard.print_dashboard()

if __name__ == "__main__":
    main() 
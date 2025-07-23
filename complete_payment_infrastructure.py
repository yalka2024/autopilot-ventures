#!/usr/bin/env python3
"""
Complete Payment Infrastructure
End-to-end payment processing with Stripe integration
"""

import stripe
import json
import time
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import os
import logging
from dataclasses import dataclass
import asyncio
import aiohttp
import random
from decimal import Decimal
import hashlib
import hmac

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PaymentIntent:
    """Payment intent data structure"""
    id: str
    amount: int
    currency: str
    status: str
    customer_id: str
    product_id: str
    created_at: datetime
    payment_method_id: Optional[str] = None
    subscription_id: Optional[str] = None

@dataclass
class Subscription:
    """Subscription data structure"""
    id: str
    customer_id: str
    product_id: str
    status: str
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool
    created_at: datetime
    amount: int
    currency: str
    interval: str  # monthly, yearly, weekly

@dataclass
class Customer:
    """Customer data structure"""
    id: str
    email: str
    name: str
    created_at: datetime
    subscription_count: int = 0
    total_spent: int = 0
    payment_methods: List[str] = None

class CompletePaymentInfrastructure:
    """Complete payment infrastructure with Stripe integration"""
    
    def __init__(self):
        self.db_path = "payment_infrastructure.db"
        self.init_database()
        
        # Initialize Stripe (replace with your actual keys)
        self.stripe_secret_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_...")
        self.stripe_publishable_key = os.getenv("STRIPE_PUBLISHABLE_KEY", "pk_test_...")
        self.webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_...")
        
        # Initialize Stripe client
        stripe.api_key = self.stripe_secret_key
        
        # Payment configuration
        self.supported_currencies = ["usd", "eur", "gbp", "cad", "aud"]
        self.default_currency = "usd"
        
        # Tax configuration
        self.tax_rates = {
            "us": 0.08,  # 8% average US tax rate
            "eu": 0.20,  # 20% average EU VAT
            "ca": 0.13,  # 13% average Canadian tax
            "au": 0.10,  # 10% average Australian GST
            "gb": 0.20   # 20% UK VAT
        }
        
        logger.info("Complete Payment Infrastructure initialized")
    
    def init_database(self):
        """Initialize database for payment infrastructure"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create customers table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS customers (
                    id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    name TEXT,
                    created_at TEXT,
                    subscription_count INTEGER DEFAULT 0,
                    total_spent INTEGER DEFAULT 0,
                    payment_methods TEXT,
                    tax_location TEXT,
                    metadata TEXT
                )
            ''')
            
            # Create payment intents table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS payment_intents (
                    id TEXT PRIMARY KEY,
                    amount INTEGER NOT NULL,
                    currency TEXT NOT NULL,
                    status TEXT NOT NULL,
                    customer_id TEXT,
                    product_id TEXT,
                    created_at TEXT,
                    payment_method_id TEXT,
                    subscription_id TEXT,
                    metadata TEXT,
                    FOREIGN KEY (customer_id) REFERENCES customers (id)
                )
            ''')
            
            # Create subscriptions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS subscriptions (
                    id TEXT PRIMARY KEY,
                    customer_id TEXT NOT NULL,
                    product_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    current_period_start TEXT,
                    current_period_end TEXT,
                    cancel_at_period_end BOOLEAN DEFAULT FALSE,
                    created_at TEXT,
                    amount INTEGER NOT NULL,
                    currency TEXT NOT NULL,
                    interval TEXT NOT NULL,
                    metadata TEXT,
                    FOREIGN KEY (customer_id) REFERENCES customers (id)
                )
            ''')
            
            # Create revenue analytics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS revenue_analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    revenue INTEGER NOT NULL,
                    currency TEXT NOT NULL,
                    customer_count INTEGER DEFAULT 0,
                    subscription_count INTEGER DEFAULT 0,
                    churn_rate REAL DEFAULT 0.0,
                    mrr INTEGER DEFAULT 0,
                    arr INTEGER DEFAULT 0,
                    metadata TEXT
                )
            ''')
            
            # Create tax records table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tax_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id TEXT NOT NULL,
                    amount INTEGER NOT NULL,
                    tax_amount INTEGER NOT NULL,
                    tax_rate REAL NOT NULL,
                    country TEXT NOT NULL,
                    transaction_date TEXT,
                    metadata TEXT,
                    FOREIGN KEY (customer_id) REFERENCES customers (id)
                )
            ''')
            
            # Create webhook events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS webhook_events (
                    id TEXT PRIMARY KEY,
                    event_type TEXT NOT NULL,
                    event_data TEXT NOT NULL,
                    processed_at TEXT,
                    status TEXT DEFAULT 'pending'
                )
            ''')
            
            conn.commit()
            conn.close()
            print("✅ Payment infrastructure database initialized")
            
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
    
    async def create_customer(self, email: str, name: str, metadata: Dict = None) -> Dict:
        """Create a new customer in Stripe and local database"""
        try:
            print(f"👤 Creating customer: {email}")
            
            # Create customer in Stripe
            stripe_customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata=metadata or {}
            )
            
            # Create customer in local database
            customer = Customer(
                id=stripe_customer.id,
                email=email,
                name=name,
                created_at=datetime.now(),
                payment_methods=[]
            )
            
            await self.store_customer(customer)
            
            print(f"✅ Customer created: {stripe_customer.id}")
            return {
                "customer_id": stripe_customer.id,
                "email": email,
                "name": name,
                "status": "created"
            }
            
        except Exception as e:
            logger.error(f"Customer creation failed: {e}")
            return {"error": str(e)}
    
    async def store_customer(self, customer: Customer):
        """Store customer in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO customers (
                    id, email, name, created_at, subscription_count,
                    total_spent, payment_methods, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                customer.id, customer.email, customer.name,
                customer.created_at.isoformat(), customer.subscription_count,
                customer.total_spent, json.dumps(customer.payment_methods or []),
                json.dumps({})
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to store customer: {e}")
    
    async def create_payment_intent(self, customer_id: str, product_id: str, amount: int, 
                                  currency: str = "usd", metadata: Dict = None) -> Dict:
        """Create a payment intent for one-time payment"""
        try:
            print(f"💳 Creating payment intent: ${amount/100:.2f} {currency.upper()}")
            
            # Create payment intent in Stripe
            payment_intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                customer=customer_id,
                metadata={
                    "product_id": product_id,
                    **(metadata or {})
                },
                automatic_payment_methods={
                    "enabled": True,
                }
            )
            
            # Store payment intent locally
            intent = PaymentIntent(
                id=payment_intent.id,
                amount=amount,
                currency=currency,
                status=payment_intent.status,
                customer_id=customer_id,
                product_id=product_id,
                created_at=datetime.now()
            )
            
            await self.store_payment_intent(intent)
            
            print(f"✅ Payment intent created: {payment_intent.id}")
            return {
                "payment_intent_id": payment_intent.id,
                "client_secret": payment_intent.client_secret,
                "amount": amount,
                "currency": currency,
                "status": payment_intent.status
            }
            
        except Exception as e:
            logger.error(f"Payment intent creation failed: {e}")
            return {"error": str(e)}
    
    async def store_payment_intent(self, intent: PaymentIntent):
        """Store payment intent in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO payment_intents (
                    id, amount, currency, status, customer_id, product_id,
                    created_at, payment_method_id, subscription_id, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                intent.id, intent.amount, intent.currency, intent.status,
                intent.customer_id, intent.product_id, intent.created_at.isoformat(),
                intent.payment_method_id, intent.subscription_id, json.dumps({})
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to store payment intent: {e}")
    
    async def create_subscription(self, customer_id: str, product_id: str, price_id: str,
                                interval: str = "month", metadata: Dict = None) -> Dict:
        """Create a subscription for recurring billing"""
        try:
            print(f"🔄 Creating subscription for customer: {customer_id}")
            
            # Create subscription in Stripe
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}],
                metadata=metadata or {},
                payment_behavior="default_incomplete",
                expand=["latest_invoice.payment_intent"]
            )
            
            # Store subscription locally
            sub = Subscription(
                id=subscription.id,
                customer_id=customer_id,
                product_id=product_id,
                status=subscription.status,
                current_period_start=datetime.fromtimestamp(subscription.current_period_start),
                current_period_end=datetime.fromtimestamp(subscription.current_period_end),
                cancel_at_period_end=subscription.cancel_at_period_end,
                created_at=datetime.now(),
                amount=subscription.items.data[0].price.unit_amount,
                currency=subscription.currency,
                interval=interval
            )
            
            await self.store_subscription(sub)
            
            print(f"✅ Subscription created: {subscription.id}")
            return {
                "subscription_id": subscription.id,
                "status": subscription.status,
                "client_secret": subscription.latest_invoice.payment_intent.client_secret,
                "amount": sub.amount,
                "currency": sub.currency,
                "interval": interval
            }
            
        except Exception as e:
            logger.error(f"Subscription creation failed: {e}")
            return {"error": str(e)}
    
    async def store_subscription(self, subscription: Subscription):
        """Store subscription in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO subscriptions (
                    id, customer_id, product_id, status, current_period_start,
                    current_period_end, cancel_at_period_end, created_at,
                    amount, currency, interval, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                subscription.id, subscription.customer_id, subscription.product_id,
                subscription.status, subscription.current_period_start.isoformat(),
                subscription.current_period_end.isoformat(), subscription.cancel_at_period_end,
                subscription.created_at.isoformat(), subscription.amount,
                subscription.currency, subscription.interval, json.dumps({})
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to store subscription: {e}")
    
    async def process_webhook(self, payload: str, signature: str) -> Dict:
        """Process Stripe webhook events"""
        try:
            print("📡 Processing webhook event...")
            
            # Verify webhook signature
            event = stripe.Webhook.construct_event(
                payload, signature, self.webhook_secret
            )
            
            # Store webhook event
            await self.store_webhook_event(event)
            
            # Process different event types
            if event.type == "payment_intent.succeeded":
                await self.handle_payment_success(event.data.object)
            elif event.type == "payment_intent.payment_failed":
                await self.handle_payment_failure(event.data.object)
            elif event.type == "invoice.payment_succeeded":
                await self.handle_subscription_payment(event.data.object)
            elif event.type == "customer.subscription.deleted":
                await self.handle_subscription_cancellation(event.data.object)
            elif event.type == "customer.subscription.updated":
                await self.handle_subscription_update(event.data.object)
            
            print(f"✅ Webhook processed: {event.type}")
            return {"status": "processed", "event_type": event.type}
            
        except Exception as e:
            logger.error(f"Webhook processing failed: {e}")
            return {"error": str(e)}
    
    async def store_webhook_event(self, event):
        """Store webhook event in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO webhook_events (
                    id, event_type, event_data, processed_at, status
                ) VALUES (?, ?, ?, ?, ?)
            ''', (
                event.id, event.type, json.dumps(event.data),
                datetime.now().isoformat(), "processed"
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to store webhook event: {e}")
    
    async def handle_payment_success(self, payment_intent):
        """Handle successful payment"""
        try:
            print(f"✅ Payment succeeded: {payment_intent.id}")
            
            # Update payment intent status
            await self.update_payment_intent_status(payment_intent.id, "succeeded")
            
            # Calculate and store tax
            await self.calculate_and_store_tax(payment_intent)
            
            # Update customer total spent
            await self.update_customer_spending(payment_intent.customer, payment_intent.amount)
            
            # Update revenue analytics
            await self.update_revenue_analytics(payment_intent.amount, payment_intent.currency)
            
        except Exception as e:
            logger.error(f"Payment success handling failed: {e}")
    
    async def handle_payment_failure(self, payment_intent):
        """Handle failed payment"""
        try:
            print(f"❌ Payment failed: {payment_intent.id}")
            
            # Update payment intent status
            await self.update_payment_intent_status(payment_intent.id, "failed")
            
            # Log failure reason
            logger.warning(f"Payment failed: {payment_intent.last_payment_error}")
            
        except Exception as e:
            logger.error(f"Payment failure handling failed: {e}")
    
    async def handle_subscription_payment(self, invoice):
        """Handle subscription payment"""
        try:
            print(f"🔄 Subscription payment: {invoice.subscription}")
            
            # Update subscription status
            await self.update_subscription_status(invoice.subscription, "active")
            
            # Calculate and store tax
            await self.calculate_and_store_tax(invoice)
            
            # Update revenue analytics
            await self.update_revenue_analytics(invoice.amount_paid, invoice.currency)
            
        except Exception as e:
            logger.error(f"Subscription payment handling failed: {e}")
    
    async def handle_subscription_cancellation(self, subscription):
        """Handle subscription cancellation"""
        try:
            print(f"🚫 Subscription cancelled: {subscription.id}")
            
            # Update subscription status
            await self.update_subscription_status(subscription.id, "cancelled")
            
            # Update customer subscription count
            await self.update_customer_subscription_count(subscription.customer, -1)
            
        except Exception as e:
            logger.error(f"Subscription cancellation handling failed: {e}")
    
    async def handle_subscription_update(self, subscription):
        """Handle subscription update"""
        try:
            print(f"🔄 Subscription updated: {subscription.id}")
            
            # Update subscription in database
            await self.update_subscription_data(subscription)
            
        except Exception as e:
            logger.error(f"Subscription update handling failed: {e}")
    
    async def update_payment_intent_status(self, intent_id: str, status: str):
        """Update payment intent status"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE payment_intents SET status = ? WHERE id = ?
            ''', (status, intent_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to update payment intent status: {e}")
    
    async def update_subscription_status(self, subscription_id: str, status: str):
        """Update subscription status"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE subscriptions SET status = ? WHERE id = ?
            ''', (status, subscription_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to update subscription status: {e}")
    
    async def calculate_and_store_tax(self, transaction):
        """Calculate and store tax for transaction"""
        try:
            # Get customer location (simplified)
            customer_location = "us"  # Default to US
            
            # Get tax rate
            tax_rate = self.tax_rates.get(customer_location, 0.0)
            
            # Calculate tax amount
            tax_amount = int(transaction.amount * tax_rate)
            
            # Store tax record
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO tax_records (
                    customer_id, amount, tax_amount, tax_rate, country, transaction_date
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                transaction.customer, transaction.amount, tax_amount,
                tax_rate, customer_location, datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            print(f"💰 Tax calculated: ${tax_amount/100:.2f} ({tax_rate*100:.1f}%)")
            
        except Exception as e:
            logger.error(f"Tax calculation failed: {e}")
    
    async def update_customer_spending(self, customer_id: str, amount: int):
        """Update customer total spending"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE customers SET total_spent = total_spent + ? WHERE id = ?
            ''', (amount, customer_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to update customer spending: {e}")
    
    async def update_customer_subscription_count(self, customer_id: str, change: int):
        """Update customer subscription count"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE customers SET subscription_count = subscription_count + ? WHERE id = ?
            ''', (change, customer_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to update customer subscription count: {e}")
    
    async def update_revenue_analytics(self, amount: int, currency: str):
        """Update revenue analytics"""
        try:
            today = datetime.now().date().isoformat()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if record exists for today
            cursor.execute('''
                SELECT id, revenue FROM revenue_analytics WHERE date = ?
            ''', (today,))
            
            result = cursor.fetchone()
            
            if result:
                # Update existing record
                cursor.execute('''
                    UPDATE revenue_analytics SET revenue = revenue + ? WHERE date = ?
                ''', (amount, today))
            else:
                # Create new record
                cursor.execute('''
                    INSERT INTO revenue_analytics (
                        date, revenue, currency, customer_count, subscription_count
                    ) VALUES (?, ?, ?, 0, 0)
                ''', (today, amount, currency))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to update revenue analytics: {e}")
    
    async def update_subscription_data(self, subscription):
        """Update subscription data in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE subscriptions SET
                    status = ?, current_period_start = ?, current_period_end = ?,
                    cancel_at_period_end = ?
                WHERE id = ?
            ''', (
                subscription.status,
                datetime.fromtimestamp(subscription.current_period_start).isoformat(),
                datetime.fromtimestamp(subscription.current_period_end).isoformat(),
                subscription.cancel_at_period_end,
                subscription.id
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to update subscription data: {e}")
    
    async def get_revenue_analytics(self, days: int = 30) -> Dict:
        """Get revenue analytics for specified period"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Get revenue data
            revenue_df = pd.read_sql_query('''
                SELECT * FROM revenue_analytics 
                WHERE date >= date('now', '-{} days')
                ORDER BY date
            '''.format(days), conn)
            
            # Get customer data
            customers_df = pd.read_sql_query("SELECT * FROM customers", conn)
            
            # Get subscription data
            subscriptions_df = pd.read_sql_query("SELECT * FROM subscriptions", conn)
            
            conn.close()
            
            # Calculate metrics
            total_revenue = revenue_df['revenue'].sum() if len(revenue_df) > 0 else 0
            total_customers = len(customers_df)
            active_subscriptions = len(subscriptions_df[subscriptions_df['status'] == 'active'])
            
            # Calculate MRR (Monthly Recurring Revenue)
            monthly_subscriptions = subscriptions_df[
                (subscriptions_df['status'] == 'active') & 
                (subscriptions_df['interval'] == 'month')
            ]
            mrr = monthly_subscriptions['amount'].sum() if len(monthly_subscriptions) > 0 else 0
            
            # Calculate ARR (Annual Recurring Revenue)
            yearly_subscriptions = subscriptions_df[
                (subscriptions_df['status'] == 'active') & 
                (subscriptions_df['interval'] == 'year')
            ]
            arr = yearly_subscriptions['amount'].sum() if len(yearly_subscriptions) > 0 else 0
            
            return {
                "total_revenue": total_revenue,
                "total_customers": total_customers,
                "active_subscriptions": active_subscriptions,
                "mrr": mrr,
                "arr": arr,
                "daily_revenue": revenue_df.to_dict('records') if len(revenue_df) > 0 else [],
                "customer_breakdown": {
                    "new_customers": len(customers_df[customers_df['created_at'] >= (datetime.now() - timedelta(days=days)).isoformat()]),
                    "paying_customers": len(customers_df[customers_df['total_spent'] > 0]),
                    "average_spend": customers_df['total_spent'].mean() if len(customers_df) > 0 else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get revenue analytics: {e}")
            return {}
    
    async def create_test_payment_flow(self, product_id: str) -> Dict:
        """Create a complete test payment flow"""
        try:
            print("🧪 Creating test payment flow...")
            
            # Create test customer
            customer_result = await self.create_customer(
                email="test@example.com",
                name="Test Customer",
                metadata={"test": True}
            )
            
            if "error" in customer_result:
                return customer_result
            
            customer_id = customer_result["customer_id"]
            
            # Create payment intent
            payment_result = await self.create_payment_intent(
                customer_id=customer_id,
                product_id=product_id,
                amount=2999,  # $29.99
                currency="usd",
                metadata={"test": True}
            )
            
            if "error" in payment_result:
                return payment_result
            
            # Create subscription
            subscription_result = await self.create_subscription(
                customer_id=customer_id,
                product_id=product_id,
                price_id="price_test_monthly",  # You'll need to create this in Stripe
                interval="month",
                metadata={"test": True}
            )
            
            return {
                "customer": customer_result,
                "payment_intent": payment_result,
                "subscription": subscription_result,
                "status": "test_flow_created"
            }
            
        except Exception as e:
            logger.error(f"Test payment flow creation failed: {e}")
            return {"error": str(e)}

def main():
    """Main execution function"""
    async def run_payment_infrastructure():
        payment_system = CompletePaymentInfrastructure()
        
        print("💳 COMPLETE PAYMENT INFRASTRUCTURE")
        print("=" * 50)
        
        # Test the payment infrastructure
        test_result = await payment_system.create_test_payment_flow("test_product_1")
        
        if "error" not in test_result:
            print("✅ Test payment flow created successfully")
            print(f"   👤 Customer: {test_result['customer']['customer_id']}")
            print(f"   💳 Payment Intent: {test_result['payment_intent']['payment_intent_id']}")
            print(f"   🔄 Subscription: {test_result['subscription']['subscription_id']}")
        else:
            print(f"❌ Test payment flow failed: {test_result['error']}")
        
        # Get revenue analytics
        analytics = await payment_system.get_revenue_analytics()
        
        print(f"\n📊 REVENUE ANALYTICS")
        print("-" * 30)
        print(f"💰 Total Revenue: ${analytics.get('total_revenue', 0)/100:.2f}")
        print(f"👥 Total Customers: {analytics.get('total_customers', 0)}")
        print(f"🔄 Active Subscriptions: {analytics.get('active_subscriptions', 0)}")
        print(f"📈 MRR: ${analytics.get('mrr', 0)/100:.2f}")
        print(f"📊 ARR: ${analytics.get('arr', 0)/100:.2f}")
        
        print(f"\n🎉 Payment infrastructure is ready for real transactions!")
    
    # Run the async function
    asyncio.run(run_payment_infrastructure())

if __name__ == "__main__":
    main() 
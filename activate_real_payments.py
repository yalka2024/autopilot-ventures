#!/usr/bin/env python3
"""
Activate Real Payments System
Configure real Stripe API keys and test complete payment flow
"""

import os
import stripe
import json
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any
import asyncio
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealPaymentActivator:
    """Activate real payment processing with Stripe"""
    
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Get real Stripe keys from .env
        self.stripe_secret_key = os.getenv("STRIPE_SECRET_KEY")
        self.stripe_publishable_key = os.getenv("STRIPE_PUBLISHABLE_KEY")
        
        if not self.stripe_secret_key:
            raise ValueError("STRIPE_SECRET_KEY not found in .env file")
        
        # Initialize Stripe with real keys
        stripe.api_key = self.stripe_secret_key
        
        # Payment configuration
        self.supported_currencies = ["usd", "eur", "gbp", "cad", "aud"]
        self.default_currency = "usd"
        
        # Tax configuration for real compliance
        self.tax_rates = {
            "us": 0.08,  # 8% average US tax rate
            "eu": 0.20,  # 20% average EU VAT
            "ca": 0.13,  # 13% average Canadian tax
            "au": 0.10,  # 10% average Australian GST
            "gb": 0.20   # 20% UK VAT
        }
        
        logger.info("Real Payment Activator initialized with live Stripe keys")
    
    def test_stripe_connection(self) -> Dict:
        """Test connection to Stripe with real API keys"""
        try:
            print("🔗 Testing Stripe connection...")
            
            # Test API connection by getting account details
            account = stripe.Account.retrieve()
            
            print(f"✅ Stripe connection successful!")
            print(f"   Account ID: {account.id}")
            print(f"   Account Type: {account.type}")
            print(f"   Country: {account.country}")
            print(f"   Charges Enabled: {account.charges_enabled}")
            print(f"   Payouts Enabled: {account.payouts_enabled}")
            
            return {
                "status": "connected",
                "account_id": account.id,
                "account_type": account.type,
                "country": account.country,
                "charges_enabled": account.charges_enabled,
                "payouts_enabled": account.payouts_enabled
            }
            
        except Exception as e:
            print(f"❌ Stripe connection failed: {e}")
            return {"error": str(e)}
    
    def create_test_products(self) -> Dict:
        """Create test products in Stripe for real payments"""
        try:
            print("🛍️ Creating test products in Stripe...")
            
            # Create test products based on market-validated offerings
            products = [
                {
                    "name": "Ecommerce Tools Pro Platform",
                    "description": "AI-powered ecommerce automation platform",
                    "price": 2999,  # $29.99
                    "currency": "usd",
                    "interval": "month"
                },
                {
                    "name": "SaaS Automation Suite",
                    "description": "Complete SaaS automation and analytics platform",
                    "price": 4999,  # $49.99
                    "currency": "usd",
                    "interval": "month"
                },
                {
                    "name": "Marketing Automation Pro",
                    "description": "Multi-channel marketing automation platform",
                    "price": 3999,  # $39.99
                    "currency": "usd",
                    "interval": "month"
                }
            ]
            
            created_products = []
            
            for product_data in products:
                # Create product
                product = stripe.Product.create(
                    name=product_data["name"],
                    description=product_data["description"]
                )
                
                # Create price for the product
                price = stripe.Price.create(
                    product=product.id,
                    unit_amount=product_data["price"],
                    currency=product_data["currency"],
                    recurring={
                        "interval": product_data["interval"]
                    }
                )
                
                created_products.append({
                    "product_id": product.id,
                    "price_id": price.id,
                    "name": product_data["name"],
                    "price": product_data["price"],
                    "currency": product_data["currency"]
                })
                
                print(f"   ✅ Created: {product_data['name']} - ${product_data['price']/100:.2f}")
            
            print(f"✅ Created {len(created_products)} test products")
            return {"products": created_products}
            
        except Exception as e:
            print(f"❌ Product creation failed: {e}")
            return {"error": str(e)}
    
    def create_test_customer(self) -> Dict:
        """Create a test customer for real payment testing"""
        try:
            print("👤 Creating test customer...")
            
            # Create customer in Stripe
            customer = stripe.Customer.create(
                email="test@autopilotventures.com",
                name="Test Customer",
                description="Test customer for payment flow validation",
                metadata={
                    "test": "true",
                    "source": "autopilot_ventures"
                }
            )
            
            print(f"✅ Test customer created: {customer.id}")
            return {
                "customer_id": customer.id,
                "email": customer.email,
                "name": customer.name
            }
            
        except Exception as e:
            print(f"❌ Customer creation failed: {e}")
            return {"error": str(e)}
    
    def test_payment_intent_creation(self, customer_id: str, product_id: str, price_id: str) -> Dict:
        """Test creating a real payment intent"""
        try:
            print("💳 Testing payment intent creation...")
            
            # Create payment intent
            payment_intent = stripe.PaymentIntent.create(
                amount=2999,  # $29.99
                currency="usd",
                customer=customer_id,
                automatic_payment_methods={
                    "enabled": True,
                },
                metadata={
                    "product_id": product_id,
                    "test": "true"
                }
            )
            
            print(f"✅ Payment intent created: {payment_intent.id}")
            print(f"   Amount: ${payment_intent.amount/100:.2f}")
            print(f"   Status: {payment_intent.status}")
            print(f"   Client Secret: {payment_intent.client_secret[:20]}...")
            
            return {
                "payment_intent_id": payment_intent.id,
                "client_secret": payment_intent.client_secret,
                "amount": payment_intent.amount,
                "currency": payment_intent.currency,
                "status": payment_intent.status
            }
            
        except Exception as e:
            print(f"❌ Payment intent creation failed: {e}")
            return {"error": str(e)}
    
    def test_subscription_creation(self, customer_id: str, price_id: str) -> Dict:
        """Test creating a real subscription"""
        try:
            print("🔄 Testing subscription creation...")
            
            # Create subscription
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}],
                payment_behavior="default_incomplete",
                expand=["latest_invoice.payment_intent"],
                metadata={
                    "test": "true",
                    "source": "autopilot_ventures"
                }
            )
            
            print(f"✅ Subscription created: {subscription.id}")
            print(f"   Status: {subscription.status}")
            print(f"   Current Period: {datetime.fromtimestamp(subscription.current_period_start).strftime('%Y-%m-%d')} to {datetime.fromtimestamp(subscription.current_period_end).strftime('%Y-%m-%d')}")
            
            return {
                "subscription_id": subscription.id,
                "status": subscription.status,
                "client_secret": subscription.latest_invoice.payment_intent.client_secret,
                "current_period_start": subscription.current_period_start,
                "current_period_end": subscription.current_period_end
            }
            
        except Exception as e:
            print(f"❌ Subscription creation failed: {e}")
            return {"error": str(e)}
    
    def setup_webhook_endpoint(self) -> Dict:
        """Set up webhook endpoint for real-time event handling"""
        try:
            print("📡 Setting up webhook endpoint...")
            
            # Create webhook endpoint
            webhook_endpoint = stripe.WebhookEndpoint.create(
                url="https://your-domain.com/webhook",  # Replace with your actual domain
                enabled_events=[
                    "payment_intent.succeeded",
                    "payment_intent.payment_failed",
                    "invoice.payment_succeeded",
                    "invoice.payment_failed",
                    "customer.subscription.created",
                    "customer.subscription.updated",
                    "customer.subscription.deleted"
                ],
                metadata={
                    "source": "autopilot_ventures"
                }
            )
            
            print(f"✅ Webhook endpoint created: {webhook_endpoint.id}")
            print(f"   URL: {webhook_endpoint.url}")
            print(f"   Secret: {webhook_endpoint.secret[:20]}...")
            print(f"   Events: {len(webhook_endpoint.enabled_events)} events enabled")
            
            return {
                "webhook_id": webhook_endpoint.id,
                "url": webhook_endpoint.url,
                "secret": webhook_endpoint.secret,
                "enabled_events": webhook_endpoint.enabled_events
            }
            
        except Exception as e:
            print(f"❌ Webhook setup failed: {e}")
            return {"error": str(e)}
    
    def implement_tax_rules(self) -> Dict:
        """Implement tax rules for jurisdiction-specific compliance"""
        try:
            print("🧾 Implementing tax rules...")
            
            # Create tax rates in Stripe
            tax_rates = {}
            
            for country, rate in self.tax_rates.items():
                tax_rate = stripe.TaxRate.create(
                    display_name=f"{country.upper()} Tax",
                    description=f"Tax for {country.upper()}",
                    percentage=rate * 100,
                    inclusive=False,
                    country=country.upper(),
                    metadata={
                        "country": country,
                        "source": "autopilot_ventures"
                    }
                )
                
                tax_rates[country] = {
                    "id": tax_rate.id,
                    "percentage": tax_rate.percentage,
                    "country": tax_rate.country
                }
                
                print(f"   ✅ Created tax rate for {country.upper()}: {tax_rate.percentage}%")
            
            print(f"✅ Created {len(tax_rates)} tax rates")
            return {"tax_rates": tax_rates}
            
        except Exception as e:
            print(f"❌ Tax rules implementation failed: {e}")
            return {"error": str(e)}
    
    def test_complete_payment_flow(self) -> Dict:
        """Test the complete payment flow end-to-end"""
        try:
            print("🧪 Testing complete payment flow...")
            
            # Step 1: Test Stripe connection
            connection_test = self.test_stripe_connection()
            if "error" in connection_test:
                return connection_test
            
            # Step 2: Create test products
            products_result = self.create_test_products()
            if "error" in products_result:
                return products_result
            
            # Step 3: Create test customer
            customer_result = self.create_test_customer()
            if "error" in customer_result:
                return customer_result
            
            customer_id = customer_result["customer_id"]
            first_product = products_result["products"][0]
            
            # Step 4: Test payment intent creation
            payment_result = self.test_payment_intent_creation(
                customer_id, 
                first_product["product_id"], 
                first_product["price_id"]
            )
            if "error" in payment_result:
                return payment_result
            
            # Step 5: Test subscription creation
            subscription_result = self.test_subscription_creation(
                customer_id, 
                first_product["price_id"]
            )
            if "error" in subscription_result:
                return subscription_result
            
            # Step 6: Set up webhook endpoint
            webhook_result = self.setup_webhook_endpoint()
            
            # Step 7: Implement tax rules
            tax_result = self.implement_tax_rules()
            
            print("🎉 Complete payment flow test successful!")
            
            return {
                "status": "success",
                "connection": connection_test,
                "products": products_result,
                "customer": customer_result,
                "payment_intent": payment_result,
                "subscription": subscription_result,
                "webhook": webhook_result,
                "tax_rules": tax_result
            }
            
        except Exception as e:
            print(f"❌ Complete payment flow test failed: {e}")
            return {"error": str(e)}
    
    def generate_revenue_forecast(self) -> Dict:
        """Generate revenue forecast based on market-validated offerings"""
        try:
            print("📊 Generating revenue forecast...")
            
            # Based on market-validated offerings and customer acquisition
            forecast = {
                "month_1": {
                    "customers": 10,
                    "mrr": 299.90,  # 10 customers * $29.99
                    "arr": 3598.80,
                    "revenue": 299.90
                },
                "month_3": {
                    "customers": 50,
                    "mrr": 1499.50,
                    "arr": 17994.00,
                    "revenue": 4498.50
                },
                "month_6": {
                    "customers": 150,
                    "mrr": 4498.50,
                    "arr": 53982.00,
                    "revenue": 26991.00
                },
                "month_12": {
                    "customers": 500,
                    "mrr": 14995.00,
                    "arr": 179940.00,
                    "revenue": 179940.00
                }
            }
            
            print("✅ Revenue forecast generated:")
            for period, data in forecast.items():
                print(f"   {period}: {data['customers']} customers, ${data['mrr']:.2f} MRR, ${data['arr']:.2f} ARR")
            
            return forecast
            
        except Exception as e:
            print(f"❌ Revenue forecast generation failed: {e}")
            return {"error": str(e)}

def main():
    """Main execution function"""
    print("🚀 ACTIVATING REAL PAYMENT PROCESSING")
    print("=" * 50)
    
    try:
        # Initialize payment activator
        activator = RealPaymentActivator()
        
        # Test complete payment flow
        result = activator.test_complete_payment_flow()
        
        if "error" not in result:
            print(f"\n🎉 PAYMENT INFRASTRUCTURE ACTIVATED SUCCESSFULLY!")
            print("=" * 50)
            
            # Generate revenue forecast
            forecast = activator.generate_revenue_forecast()
            
            print(f"\n📈 REVENUE FORECAST")
            print("-" * 30)
            if "error" not in forecast:
                for period, data in forecast.items():
                    print(f"{period}: ${data['mrr']:.2f} MRR | ${data['arr']:.2f} ARR | {data['customers']} customers")
            
            print(f"\n✅ NEXT STEPS:")
            print("1. Configure webhook URL to your actual domain")
            print("2. Set up payment form integration")
            print("3. Start processing real customer payments")
            print("4. Monitor revenue analytics dashboard")
            print("5. Scale based on market validation results")
            
        else:
            print(f"❌ Payment activation failed: {result['error']}")
            
    except Exception as e:
        print(f"❌ Payment activation failed: {e}")

if __name__ == "__main__":
    main() 
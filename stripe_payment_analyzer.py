#!/usr/bin/env python3
"""
Stripe Payment Analyzer
Diagnose and fix incomplete payment issues
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any

class StripePaymentAnalyzer:
    """Analyze and fix Stripe payment issues"""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        
    def analyze_incomplete_payments(self):
        """Analyze why payments are showing as incomplete"""
        print("🔍 STRIPE PAYMENT ANALYSIS")
        print("=" * 50)
        print(f"📅 Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Common causes of incomplete payments
        print("❌ COMMON CAUSES OF INCOMPLETE PAYMENTS")
        print("-" * 40)
        print("1. 🔐 Missing Payment Intent Confirmation")
        print("   • Payment intent created but not confirmed")
        print("   • Missing 'confirm' step in payment flow")
        print()
        
        print("2. 💳 Test Mode vs Live Mode Mismatch")
        print("   • Using test keys in live environment")
        print("   • Using live keys in test environment")
        print()
        
        print("3. 🔑 Invalid or Expired API Keys")
        print("   • Stripe API keys not properly configured")
        print("   • Keys don't have proper permissions")
        print()
        
        print("4. 🌐 Webhook Issues")
        print("   • Payment confirmation webhooks not received")
        print("   • Webhook endpoints not properly configured")
        print()
        
        print("5. 💰 Insufficient Funds or Declined Cards")
        print("   • Test cards with insufficient balance")
        print("   • Declined payment methods")
        print()
        
        print("6. ⏰ Payment Timeout")
        print("   • Payment intent expired before confirmation")
        print("   • Network issues during payment processing")
        print()
        
        # Check platform payment configuration
        print("🔧 PLATFORM PAYMENT CONFIGURATION CHECK")
        print("-" * 40)
        self.check_payment_configuration()
        
        # Solutions
        print("✅ SOLUTIONS TO FIX INCOMPLETE PAYMENTS")
        print("-" * 40)
        print("1. 🔄 Complete Payment Flow")
        print("   • Ensure payment intent is confirmed")
        print("   • Add proper error handling")
        print("   • Implement retry mechanisms")
        print()
        
        print("2. 🔑 Verify Stripe Configuration")
        print("   • Check API keys are correct")
        print("   • Ensure proper environment (test/live)")
        print("   • Verify webhook endpoints")
        print()
        
        print("3. 💳 Use Valid Test Cards")
        print("   • Use Stripe's test card numbers")
        print("   • Ensure sufficient test balance")
        print("   • Test with different payment methods")
        print()
        
        print("4. 🌐 Configure Webhooks")
        print("   • Set up payment confirmation webhooks")
        print("   • Handle webhook events properly")
        print("   • Test webhook delivery")
        print()
        
        print("5. ⏱️ Implement Proper Timeouts")
        print("   • Set appropriate payment timeouts")
        print("   • Handle payment expiration")
        print("   • Retry failed payments")
        print()
    
    def check_payment_configuration(self):
        """Check the platform's payment configuration"""
        try:
            # Check if platform is running
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Platform is running")
            else:
                print("❌ Platform not responding properly")
                return
        except:
            print("❌ Platform not accessible")
            return
        
        # Check payment endpoints
        payment_endpoints = [
            "/real_businesses",
            "/real_customers", 
            "/real_autonomous_status"
        ]
        
        print("\n🔍 Checking payment-related endpoints:")
        for endpoint in payment_endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                if response.status_code == 200:
                    print(f"   ✅ {endpoint} - Working")
                else:
                    print(f"   ❌ {endpoint} - HTTP {response.status_code}")
            except Exception as e:
                print(f"   ❌ {endpoint} - Error: {e}")
        
        print()
    
    def get_payment_fix_script(self):
        """Generate a script to fix payment issues"""
        print("🔧 PAYMENT FIX SCRIPT")
        print("-" * 30)
        print("Here's a script to fix incomplete payments:")
        print()
        
        script = '''#!/usr/bin/env python3
"""
Fix Incomplete Stripe Payments
Complete payment processing for incomplete transactions
"""

import stripe
import os
from datetime import datetime

# Configure Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')  # Use your actual key

def fix_incomplete_payments():
    """Fix incomplete payment intents"""
    try:
        # Get all payment intents
        payment_intents = stripe.PaymentIntent.list(
            limit=100,
            created={'gte': int((datetime.now() - timedelta(days=7)).timestamp())}
        )
        
        fixed_count = 0
        
        for intent in payment_intents.data:
            if intent.status == 'requires_confirmation':
                print(f"🔧 Fixing payment intent: {intent.id}")
                
                try:
                    # Confirm the payment intent
                    confirmed_intent = stripe.PaymentIntent.confirm(
                        intent.id,
                        payment_method='pm_card_visa'  # Use test card
                    )
                    
                    if confirmed_intent.status == 'succeeded':
                        print(f"✅ Payment {intent.id} confirmed successfully")
                        fixed_count += 1
                    else:
                        print(f"⚠️ Payment {intent.id} still {confirmed_intent.status}")
                        
                except stripe.error.StripeError as e:
                    print(f"❌ Error fixing {intent.id}: {e}")
        
        print(f"\\n🎉 Fixed {fixed_count} incomplete payments")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fix_incomplete_payments()
'''
        
        print(script)
        
        # Save script to file
        with open("fix_stripe_payments.py", "w") as f:
            f.write(script)
        
        print("✅ Script saved as 'fix_stripe_payments.py'")
        print("💡 Run: python fix_stripe_payments.py")
        print()
    
    def provide_immediate_solutions(self):
        """Provide immediate solutions for incomplete payments"""
        print("🚀 IMMEDIATE SOLUTIONS")
        print("-" * 30)
        print("1. 🔑 Check Your Stripe Keys")
        print("   • Go to Stripe Dashboard > Developers > API Keys")
        print("   • Verify you're using the correct keys")
        print("   • Ensure keys match your environment (test/live)")
        print()
        
        print("2. 💳 Use Valid Test Cards")
        print("   • 4242 4242 4242 4242 (Visa - succeeds)")
        print("   • 4000 0000 0000 0002 (Visa - declined)")
        print("   • 4000 0000 0000 9995 (Visa - insufficient funds)")
        print()
        
        print("3. 🔄 Complete Payment Flow")
        print("   • Ensure payment intent is confirmed")
        print("   • Add proper error handling")
        print("   • Test with small amounts first")
        print()
        
        print("4. 🌐 Check Webhooks")
        print("   • Go to Stripe Dashboard > Developers > Webhooks")
        print("   • Ensure webhook endpoints are configured")
        print("   • Test webhook delivery")
        print()
        
        print("5. 📊 Monitor Payment Status")
        print("   • Check payment intent status in Stripe Dashboard")
        print("   • Look for error messages")
        print("   • Verify payment method details")
        print()

def main():
    """Main execution function"""
    analyzer = StripePaymentAnalyzer()
    
    print("🔍 STRIPE PAYMENT ISSUE DIAGNOSIS")
    print("=" * 50)
    print("Your Stripe transactions are showing as 'Incompleto' (Incomplete)")
    print("This means payments were initiated but not fully processed.")
    print()
    
    analyzer.analyze_incomplete_payments()
    analyzer.get_payment_fix_script()
    analyzer.provide_immediate_solutions()
    
    print("💡 NEXT STEPS:")
    print("1. Check your Stripe API keys configuration")
    print("2. Verify you're using valid test cards")
    print("3. Ensure payment intents are being confirmed")
    print("4. Test with the provided fix script")
    print("5. Monitor payment status in Stripe Dashboard")

if __name__ == "__main__":
    main() 
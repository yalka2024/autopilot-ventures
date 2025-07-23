#!/usr/bin/env python3
"""
Fix Incomplete Stripe Payments
Complete payment processing for incomplete transactions
"""

import stripe
import os
import requests
import json
from datetime import datetime, timedelta

# Configure Stripe - Replace with your actual key
# stripe.api_key = os.getenv('STRIPE_SECRET_KEY')  # Uncomment and set your key

def check_platform_payments():
    """Check current payment status from platform"""
    try:
        response = requests.get("http://localhost:8080/real_businesses", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"🏢 Platform Businesses: {len(data.get('businesses', []))}")
            print(f"💰 Total Revenue: ${data.get('total_income', 0):,.2f}")
            return data
        else:
            print(f"❌ Platform not responding: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error checking platform: {e}")
        return None

def fix_incomplete_payments():
    """Fix incomplete payment intents"""
    print("🔧 FIXING INCOMPLETE STRIPE PAYMENTS")
    print("=" * 50)
    
    # First check platform status
    platform_data = check_platform_payments()
    
    if not platform_data:
        print("❌ Cannot access platform. Make sure it's running.")
        return
    
    print("\n📊 CURRENT STATUS:")
    print(f"   Businesses: {len(platform_data.get('businesses', []))}")
    print(f"   Revenue: ${platform_data.get('total_income', 0):,.2f}")
    
    # Check if Stripe is configured
    if not stripe.api_key:
        print("\n❌ STRIPE NOT CONFIGURED")
        print("To fix incomplete payments, you need to:")
        print("1. Get your Stripe API key from dashboard")
        print("2. Set it in this script")
        print("3. Run the fix function")
        print("\n💡 For now, here's what you can do manually:")
        print_manual_fix_instructions()
        return
    
    try:
        # Get all payment intents from last 7 days
        payment_intents = stripe.PaymentIntent.list(
            limit=100,
            created={'gte': int((datetime.now() - timedelta(days=7)).timestamp())}
        )
        
        print(f"\n🔍 Found {len(payment_intents.data)} payment intents")
        
        incomplete_count = 0
        fixed_count = 0
        
        for intent in payment_intents.data:
            print(f"\n📋 Payment Intent: {intent.id}")
            print(f"   Status: {intent.status}")
            print(f"   Amount: ${intent.amount/100:,.2f}")
            print(f"   Created: {datetime.fromtimestamp(intent.created)}")
            
            if intent.status == 'requires_confirmation':
                incomplete_count += 1
                print(f"   🔧 This payment needs confirmation")
                
                try:
                    # Confirm the payment intent with test card
                    confirmed_intent = stripe.PaymentIntent.confirm(
                        intent.id,
                        payment_method='pm_card_visa'  # Test card
                    )
                    
                    if confirmed_intent.status == 'succeeded':
                        print(f"   ✅ Payment confirmed successfully!")
                        fixed_count += 1
                    else:
                        print(f"   ⚠️ Payment still {confirmed_intent.status}")
                        
                except stripe.error.StripeError as e:
                    print(f"   ❌ Error confirming: {e}")
            else:
                print(f"   ✅ Payment is {intent.status}")
        
        print(f"\n🎉 SUMMARY:")
        print(f"   Incomplete payments found: {incomplete_count}")
        print(f"   Successfully fixed: {fixed_count}")
        
    except Exception as e:
        print(f"❌ Error accessing Stripe: {e}")
        print_manual_fix_instructions()

def print_manual_fix_instructions():
    """Print manual fix instructions"""
    print("\n📋 MANUAL FIX INSTRUCTIONS")
    print("=" * 40)
    print("Since Stripe API is not configured, here's how to fix manually:")
    print()
    print("1. 🔑 GET YOUR STRIPE API KEY")
    print("   • Go to Stripe Dashboard")
    print("   • Developers > API Keys")
    print("   • Copy your Secret Key")
    print()
    print("2. 🔧 CONFIGURE THE SCRIPT")
    print("   • Open fix_stripe_payments.py")
    print("   • Uncomment line: stripe.api_key = 'your_key_here'")
    print("   • Replace 'your_key_here' with your actual key")
    print()
    print("3. 💳 USE TEST CARDS")
    print("   • 4242 4242 4242 4242 (Visa - succeeds)")
    print("   • 4000 0000 0000 0002 (Visa - declined)")
    print("   • 4000 0000 0000 9995 (Visa - insufficient funds)")
    print()
    print("4. 🔄 COMPLETE PAYMENT FLOW")
    print("   • Ensure payment intents are confirmed")
    print("   • Add proper error handling")
    print("   • Test with small amounts first")
    print()
    print("5. 🌐 CHECK WEBHOOKS")
    print("   • Go to Stripe Dashboard > Developers > Webhooks")
    print("   • Ensure webhook endpoints are configured")
    print("   • Test webhook delivery")
    print()

def check_stripe_dashboard():
    """Provide guidance for checking Stripe dashboard"""
    print("\n📊 STRIPE DASHBOARD CHECKLIST")
    print("=" * 40)
    print("Go to your Stripe Dashboard and check:")
    print()
    print("1. 📈 PAYMENTS SECTION")
    print("   • Look for payment intents with status 'requires_confirmation'")
    print("   • Check if there are any error messages")
    print("   • Verify payment method details")
    print()
    print("2. 🔑 API KEYS")
    print("   • Developers > API Keys")
    print("   • Verify you're using the correct keys")
    print("   • Check if you're in test mode or live mode")
    print()
    print("3. 🌐 WEBHOOKS")
    print("   • Developers > Webhooks")
    print("   • Ensure webhook endpoints are configured")
    print("   • Check webhook delivery status")
    print()
    print("4. 💳 PAYMENT METHODS")
    print("   • Check if test cards are being used")
    print("   • Verify card details are valid")
    print("   • Ensure sufficient test balance")
    print()

def main():
    """Main execution function"""
    print("🔧 STRIPE PAYMENT FIX TOOL")
    print("=" * 50)
    print("This tool will help fix your incomplete Stripe payments")
    print()
    
    # Check platform first
    platform_data = check_platform_payments()
    
    if platform_data:
        print("✅ Platform is accessible")
        print(f"   Found {len(platform_data.get('businesses', []))} businesses")
        print(f"   Total revenue: ${platform_data.get('total_income', 0):,.2f}")
    else:
        print("❌ Platform not accessible")
        print("   Make sure the platform is running at http://localhost:8080")
    
    print("\nChoose an option:")
    print("1. Fix incomplete payments (requires Stripe API key)")
    print("2. Show manual fix instructions")
    print("3. Check Stripe dashboard checklist")
    print("4. Exit")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        fix_incomplete_payments()
    elif choice == "2":
        print_manual_fix_instructions()
    elif choice == "3":
        check_stripe_dashboard()
    elif choice == "4":
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Start Income Generation
Trigger the autonomous system and show timeline to first Stripe payment
"""

import requests
import time
from datetime import datetime, timedelta

def start_autonomous_income_generation():
    """Start the autonomous income generation system"""
    
    print("🚀 STARTING AUTONOMOUS INCOME GENERATION")
    print("=" * 50)
    print()
    
    # Check current status
    print("📊 Current Status:")
    try:
        response = requests.get("http://localhost:8080/real_autonomous_status", timeout=5)
        if response.status_code == 200:
            status = response.json()
            print(f"   AI Active: {'✅ YES' if status.get('ai_active') else '❌ NO'}")
            print(f"   Businesses Created: {status.get('businesses_created', 0)}")
            print(f"   Customers Acquired: {status.get('customers_acquired', 0)}")
            print(f"   Total Income: ${status.get('total_income', 0):,.2f}")
        else:
            print("   ❌ Could not get status")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    
    # Start autonomous system
    print("🤖 Starting Autonomous AI System...")
    try:
        response = requests.post("http://localhost:8080/start_real_autonomous_system", timeout=30)
        if response.status_code == 200:
            result = response.json()
            print("✅ Autonomous system started successfully!")
            print(f"   Message: {result.get('message', 'N/A')}")
        else:
            print(f"❌ Failed to start system: {response.status_code}")
    except Exception as e:
        print(f"❌ Error starting system: {e}")
    
    print()
    
    # Show timeline
    print("⏰ INCOME GENERATION TIMELINE")
    print("=" * 50)
    
    start_time = datetime.now()
    
    timeline = [
        {
            "time_minutes": 2,
            "milestone": "AI Market Research Complete",
            "description": "AI analyzes market opportunities and selects business type"
        },
        {
            "time_minutes": 5,
            "milestone": "AI Business Planning Complete", 
            "description": "AI creates business plan and strategy"
        },
        {
            "time_minutes": 10,
            "milestone": "Real Product Built",
            "description": "AI builds SaaS app, e-commerce platform, or website"
        },
        {
            "time_minutes": 14,
            "milestone": "Marketing Campaigns Launched",
            "description": "AI executes ads on Google, Facebook, LinkedIn, and email"
        },
        {
            "time_minutes": 16,
            "milestone": "First Customers Arriving",
            "description": "Customers start clicking ads and visiting the business"
        },
        {
            "time_minutes": 18,
            "milestone": "First Orders Being Processed",
            "description": "AI processes first customer orders and payments"
        },
        {
            "time_minutes": 20,
            "milestone": "FIRST STRIPE PAYMENT RECEIVED",
            "description": "Real money hits your Stripe account!"
        }
    ]
    
    for step in timeline:
        estimated_time = start_time + timedelta(minutes=step["time_minutes"])
        print(f"📅 {step['milestone']}")
        print(f"   Time: +{step['time_minutes']} minutes")
        print(f"   Estimated: {estimated_time.strftime('%H:%M:%S')}")
        print(f"   Description: {step['description']}")
        print()
    
    # Real-time monitoring
    print("🔍 REAL-TIME MONITORING")
    print("=" * 50)
    print("Monitoring your Stripe account for payments...")
    print("Press Ctrl+C to stop monitoring")
    print()
    
    try:
        while True:
            # Check current status
            try:
                response = requests.get("http://localhost:8080/real_autonomous_status", timeout=5)
                if response.status_code == 200:
                    status = response.json()
                    current_time = datetime.now()
                    elapsed_minutes = (current_time - start_time).total_seconds() / 60
                    
                    print(f"⏱️  {current_time.strftime('%H:%M:%S')} (+{elapsed_minutes:.1f}min)")
                    print(f"   Businesses: {status.get('businesses_created', 0)}")
                    print(f"   Customers: {status.get('customers_acquired', 0)}")
                    print(f"   Income: ${status.get('total_income', 0):,.2f}")
                    
                    # Check if we have income
                    if status.get('total_income', 0) > 0:
                        print("🎉 FIRST INCOME GENERATED!")
                        print(f"💰 Amount: ${status.get('total_income', 0):,.2f}")
                        print("💳 Check your Stripe dashboard now!")
                        break
                    
                    print()
                    
                else:
                    print("❌ Could not get status")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
            
            # Wait 30 seconds before next check
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\n⏹️  Monitoring stopped by user")
    
    print()
    print("🎯 NEXT STEPS:")
    print("1. Check your Stripe dashboard for payments")
    print("2. Monitor the platform at http://localhost:8080")
    print("3. Use the performance monitoring scripts to track progress")
    print("4. The AI will continue generating income 24/7")

if __name__ == "__main__":
    start_autonomous_income_generation() 
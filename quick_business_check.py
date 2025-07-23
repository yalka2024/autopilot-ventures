#!/usr/bin/env python3
"""
Quick Business Status Checker
Get immediate overview of all businesses created by the platform
"""

import requests
import json
from datetime import datetime
from typing import Dict, List

def get_business_status():
    """Get current business status from the platform"""
    try:
        # Get businesses
        response = requests.get("http://localhost:8080/real_businesses", timeout=10)
        if response.status_code == 200:
            businesses_data = response.json()
        else:
            print(f"❌ Failed to get businesses: HTTP {response.status_code}")
            return
        
        # Get autonomous status
        try:
            autonomous_response = requests.get("http://localhost:8080/real_autonomous_status", timeout=10)
            autonomous_data = autonomous_response.json() if autonomous_response.status_code == 200 else {}
        except:
            autonomous_data = {}
        
        # Display results
        print("🏢 BUSINESS STATUS OVERVIEW")
        print("=" * 50)
        print(f"📅 Checked at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        businesses = businesses_data.get("businesses", [])
        total_income = businesses_data.get("total_income", 0)
        
        print("📊 SUMMARY")
        print("-" * 20)
        print(f"🏢 Total Businesses: {len(businesses)}")
        print(f"💰 Total Revenue: ${total_income:,.2f}")
        print()
        
        if businesses:
            print("📋 BUSINESS LIST")
            print("-" * 20)
            for i, business in enumerate(businesses, 1):
                print(f"{i}. {business.get('name', 'Unknown')}")
                print(f"   💰 Revenue: ${business.get('revenue', 0):,.2f}")
                print(f"   👥 Customers: {business.get('customers_acquired', 0):,}")
                print(f"   📈 Success Rate: {business.get('success_rate', 0):.1%}")
                print(f"   🤖 Autonomous: {'✅ Yes' if business.get('autonomous_creation') else '❌ No'}")
                print(f"   📅 Created: {business.get('created_at', 'Unknown')[:10]}")
                print()
        
        # Autonomous system status
        if autonomous_data:
            print("🤖 AUTONOMOUS SYSTEM")
            print("-" * 20)
            print(f"   AI Active: {'✅ Yes' if autonomous_data.get('ai_active') else '❌ No'}")
            print(f"   Websites Built: {autonomous_data.get('websites_built', 0)}")
            print(f"   Marketing Campaigns: {autonomous_data.get('marketing_campaigns', 0)}")
            print(f"   Last Activity: {autonomous_data.get('last_activity', 'Unknown')}")
            print()
        
        # Quick recommendations
        print("💡 QUICK INSIGHTS")
        print("-" * 20)
        if businesses:
            autonomous_count = sum(1 for b in businesses if b.get('autonomous_creation'))
            manual_count = len(businesses) - autonomous_count
            
            print(f"   • {autonomous_count} businesses created by AI")
            print(f"   • {manual_count} businesses created manually")
            
            if autonomous_count > 0:
                avg_revenue = total_income / len(businesses)
                print(f"   • Average revenue per business: ${avg_revenue:,.2f}")
            
            if total_income > 0:
                print(f"   • Platform is generating revenue!")
            else:
                print(f"   • No revenue generated yet")
        else:
            print("   • No businesses created yet")
            print("   • Start the autonomous system to create businesses")
        
    except Exception as e:
        print(f"❌ Error checking business status: {e}")
        print("💡 Make sure the platform is running at http://localhost:8080")

if __name__ == "__main__":
    get_business_status() 
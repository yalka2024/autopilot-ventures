#!/usr/bin/env python3
"""
Quick Performance Check
Rapid platform status verification script
"""

import requests
import time
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def quick_check():
    """Quick performance check of the platform"""
    base_url = "http://localhost:8080"
    
    print("⚡ QUICK PERFORMANCE CHECK")
    print("=" * 40)
    
    # Check if platform is running
    try:
        start_time = time.time()
        response = requests.get(f"{base_url}/health", timeout=5)
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            print(f"✅ Platform Status: RUNNING ({response_time:.3f}s)")
        else:
            print(f"❌ Platform Status: ERROR (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Platform Status: OFFLINE - {str(e)}")
        return False
    
    # Quick checks
    checks = [
        ("Autonomous Status", "/real_autonomous_status"),
        ("Phase 1 System", "/phase1_status"),
        ("Stripe Integration", "/stripe_status"),
        ("Business Count", "/real_businesses"),
        ("Customer Count", "/real_customers")
    ]
    
    results = {}
    for name, endpoint in checks:
        try:
            start_time = time.time()
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {name}: OK ({response_time:.3f}s)")
                results[name] = {"status": "success", "data": data}
            else:
                print(f"❌ {name}: ERROR ({response.status_code})")
                results[name] = {"status": "error", "code": response.status_code}
        except Exception as e:
            print(f"❌ {name}: FAILED - {str(e)}")
            results[name] = {"status": "exception", "error": str(e)}
    
    # Environment check
    print("\n🔧 Environment Check:")
    env_vars = ['OPENAI_SECRET_KEY', 'STRIPE_SECRET_KEY', 'STRIPE_PUBLISHABLE_KEY']
    for var in env_vars:
        value = os.getenv(var)
        if value:
            print(f"   ✅ {var}: CONFIGURED")
        else:
            print(f"   ❌ {var}: MISSING")
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 QUICK SUMMARY")
    print("=" * 40)
    
    successful_checks = sum(1 for r in results.values() if r.get("status") == "success")
    total_checks = len(results)
    
    print(f"Platform: {'✅ OPERATIONAL' if successful_checks == total_checks else '⚠️ ISSUES'}")
    print(f"Success Rate: {successful_checks}/{total_checks} ({successful_checks/total_checks*100:.1f}%)")
    
    # Show business metrics if available
    if "Business Count" in results and results["Business Count"]["status"] == "success":
        businesses = results["Business Count"]["data"]
        print(f"Businesses Created: {businesses.get('total_businesses', 0)}")
        print(f"Total Income: ${businesses.get('total_income', 0):,.2f}")
    
    if "Customer Count" in results and results["Customer Count"]["status"] == "success":
        customers = results["Customer Count"]["data"]
        print(f"Customers Acquired: {customers.get('total_customers', 0)}")
    
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return successful_checks == total_checks

if __name__ == "__main__":
    quick_check() 
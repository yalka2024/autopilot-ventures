#!/usr/bin/env python3
"""
Business Performance Monitor
Track revenue, customers, and business metrics
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
import matplotlib.pyplot as plt
import pandas as pd

class BusinessPerformanceMonitor:
    """Monitor business performance metrics"""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.history = []
        
    def get_business_metrics(self) -> Dict[str, Any]:
        """Get current business metrics"""
        try:
            response = requests.get(f"{self.base_url}/real_businesses", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def get_customer_metrics(self) -> Dict[str, Any]:
        """Get current customer metrics"""
        try:
            response = requests.get(f"{self.base_url}/real_customers", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def get_autonomous_status(self) -> Dict[str, Any]:
        """Get autonomous system status"""
        try:
            response = requests.get(f"{self.base_url}/real_autonomous_status", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def record_metrics(self):
        """Record current metrics for tracking"""
        timestamp = datetime.now()
        
        business_data = self.get_business_metrics()
        customer_data = self.get_customer_metrics()
        autonomous_data = self.get_autonomous_status()
        
        metrics = {
            "timestamp": timestamp.isoformat(),
            "businesses": {
                "total_businesses": business_data.get("total_businesses", 0),
                "total_income": business_data.get("total_income", 0),
                "businesses_list": business_data.get("businesses", [])
            },
            "customers": {
                "total_customers": customer_data.get("total_customers", 0),
                "customers_list": customer_data.get("customers", [])
            },
            "autonomous_system": {
                "ai_active": autonomous_data.get("ai_active", False),
                "websites_built": autonomous_data.get("websites_built", 0),
                "marketing_campaigns": autonomous_data.get("marketing_campaigns", 0)
            }
        }
        
        self.history.append(metrics)
        return metrics
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        if not self.history:
            return {"error": "No historical data available"}
        
        # Calculate growth metrics
        first_record = self.history[0]
        latest_record = self.history[-1]
        
        # Business growth
        business_growth = {
            "total_businesses": {
                "start": first_record["businesses"]["total_businesses"],
                "current": latest_record["businesses"]["total_businesses"],
                "growth": latest_record["businesses"]["total_businesses"] - first_record["businesses"]["total_businesses"]
            },
            "total_income": {
                "start": first_record["businesses"]["total_income"],
                "current": latest_record["businesses"]["total_income"],
                "growth": latest_record["businesses"]["total_income"] - first_record["businesses"]["total_income"]
            }
        }
        
        # Customer growth
        customer_growth = {
            "total_customers": {
                "start": first_record["customers"]["total_customers"],
                "current": latest_record["customers"]["total_customers"],
                "growth": latest_record["customers"]["total_customers"] - first_record["customers"]["total_customers"]
            }
        }
        
        # Calculate rates
        time_span = datetime.fromisoformat(latest_record["timestamp"]) - datetime.fromisoformat(first_record["timestamp"])
        hours_elapsed = time_span.total_seconds() / 3600
        
        if hours_elapsed > 0:
            business_per_hour = business_growth["total_businesses"]["growth"] / hours_elapsed
            income_per_hour = business_growth["total_income"]["growth"] / hours_elapsed
            customers_per_hour = customer_growth["total_customers"]["growth"] / hours_elapsed
        else:
            business_per_hour = income_per_hour = customers_per_hour = 0
        
        return {
            "timestamp": datetime.now().isoformat(),
            "monitoring_duration_hours": hours_elapsed,
            "business_metrics": business_growth,
            "customer_metrics": customer_growth,
            "rates": {
                "businesses_per_hour": business_per_hour,
                "income_per_hour": income_per_hour,
                "customers_per_hour": customers_per_hour
            },
            "current_status": {
                "ai_active": latest_record["autonomous_system"]["ai_active"],
                "websites_built": latest_record["autonomous_system"]["websites_built"],
                "marketing_campaigns": latest_record["autonomous_system"]["marketing_campaigns"]
            }
        }
    
    def print_performance_report(self):
        """Print formatted performance report"""
        report = self.generate_performance_report()
        
        if "error" in report:
            print(f"❌ Error generating report: {report['error']}")
            return
        
        print("📊 BUSINESS PERFORMANCE REPORT")
        print("=" * 50)
        print(f"Monitoring Duration: {report['monitoring_duration_hours']:.1f} hours")
        print()
        
        # Business metrics
        print("🏢 BUSINESS METRICS:")
        business = report["business_metrics"]
        print(f"   Total Businesses: {business['total_businesses']['current']} (+{business['total_businesses']['growth']})")
        print(f"   Total Income: ${business['total_income']['current']:,.2f} (+${business['total_income']['growth']:,.2f})")
        print(f"   Businesses/Hour: {report['rates']['businesses_per_hour']:.2f}")
        print(f"   Income/Hour: ${report['rates']['income_per_hour']:.2f}")
        print()
        
        # Customer metrics
        print("👥 CUSTOMER METRICS:")
        customer = report["customer_metrics"]
        print(f"   Total Customers: {customer['total_customers']['current']} (+{customer['total_customers']['growth']})")
        print(f"   Customers/Hour: {report['rates']['customers_per_hour']:.2f}")
        print()
        
        # System status
        print("🤖 AUTONOMOUS SYSTEM STATUS:")
        status = report["current_status"]
        print(f"   AI Active: {'✅ YES' if status['ai_active'] else '❌ NO'}")
        print(f"   Websites Built: {status['websites_built']}")
        print(f"   Marketing Campaigns: {status['marketing_campaigns']}")
        print()
        
        # Performance rating
        income_per_hour = report['rates']['income_per_hour']
        if income_per_hour > 100:
            rating = "🚀 EXCEPTIONAL"
        elif income_per_hour > 50:
            rating = "✅ EXCELLENT"
        elif income_per_hour > 10:
            rating = "👍 GOOD"
        elif income_per_hour > 0:
            rating = "⚠️ MODERATE"
        else:
            rating = "❌ NEEDS ATTENTION"
        
        print(f"🏆 PERFORMANCE RATING: {rating}")
        print(f"💰 Revenue Generation: ${income_per_hour:.2f}/hour")
    
    def save_history(self, filename: str = None):
        """Save monitoring history to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"business_performance_history_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.history, f, indent=2)
        
        print(f"💾 Performance history saved to: {filename}")
    
    def continuous_monitoring(self, interval_minutes: int = 5, duration_hours: int = 1):
        """Run continuous monitoring"""
        print(f"🔍 Starting continuous monitoring...")
        print(f"   Interval: {interval_minutes} minutes")
        print(f"   Duration: {duration_hours} hours")
        print(f"   Total recordings: {(duration_hours * 60) // interval_minutes}")
        print()
        
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=duration_hours)
        recording_count = 0
        
        while datetime.now() < end_time:
            recording_count += 1
            print(f"📊 Recording #{recording_count} - {datetime.now().strftime('%H:%M:%S')}")
            
            metrics = self.record_metrics()
            
            # Print current status
            print(f"   Businesses: {metrics['businesses']['total_businesses']}")
            print(f"   Income: ${metrics['businesses']['total_income']:,.2f}")
            print(f"   Customers: {metrics['customers']['total_customers']}")
            print()
            
            # Wait for next interval
            if datetime.now() < end_time:
                time.sleep(interval_minutes * 60)
        
        print("✅ Continuous monitoring completed!")
        self.print_performance_report()
        self.save_history()

def main():
    """Main execution function"""
    monitor = BusinessPerformanceMonitor()
    
    print("🚀 BUSINESS PERFORMANCE MONITOR")
    print("=" * 40)
    
    # Initial metrics
    print("📊 Current Metrics:")
    metrics = monitor.record_metrics()
    print(f"   Businesses: {metrics['businesses']['total_businesses']}")
    print(f"   Income: ${metrics['businesses']['total_income']:,.2f}")
    print(f"   Customers: {metrics['customers']['total_customers']}")
    print()
    
    # Ask user for monitoring mode
    print("Choose monitoring mode:")
    print("1. Single snapshot")
    print("2. Continuous monitoring (1 hour)")
    print("3. Continuous monitoring (custom)")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        monitor.print_performance_report()
        monitor.save_history()
    elif choice == "2":
        monitor.continuous_monitoring(interval_minutes=5, duration_hours=1)
    elif choice == "3":
        interval = int(input("Enter interval in minutes (default 5): ") or "5")
        duration = int(input("Enter duration in hours (default 1): ") or "1")
        monitor.continuous_monitoring(interval_minutes=interval, duration_hours=duration)
    else:
        print("Invalid choice. Running single snapshot...")
        monitor.print_performance_report()
        monitor.save_history()

if __name__ == "__main__":
    main() 
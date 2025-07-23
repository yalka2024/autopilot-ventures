#!/usr/bin/env python3
"""
Business Tracker - Monitor All Businesses Created by the Platform
Track revenue, customers, and performance metrics for each business
"""

import requests
import json
import time
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import os

class BusinessTracker:
    """Comprehensive business tracking and monitoring system"""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.db_path = "business_tracker.db"
        self.init_database()
        
    def init_database(self):
        """Initialize SQLite database for business tracking"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create businesses table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS businesses (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    niche TEXT,
                    status TEXT,
                    created_at TEXT,
                    revenue_generated REAL DEFAULT 0,
                    customers_acquired INTEGER DEFAULT 0,
                    success_rate REAL DEFAULT 0,
                    last_updated TEXT,
                    parent_company TEXT,
                    ai_agents_assigned TEXT,
                    market_research TEXT,
                    business_model TEXT,
                    autonomous_creation BOOLEAN DEFAULT 0
                )
            ''')
            
            # Create revenue tracking table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS revenue_tracking (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    business_id TEXT,
                    timestamp TEXT,
                    revenue_amount REAL,
                    revenue_type TEXT,
                    customer_count INTEGER,
                    FOREIGN KEY (business_id) REFERENCES businesses (id)
                )
            ''')
            
            # Create customer tracking table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS customer_tracking (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    business_id TEXT,
                    timestamp TEXT,
                    customer_count INTEGER,
                    acquisition_source TEXT,
                    conversion_rate REAL,
                    FOREIGN KEY (business_id) REFERENCES businesses (id)
                )
            ''')
            
            # Create performance metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    business_id TEXT,
                    timestamp TEXT,
                    metric_type TEXT,
                    metric_value REAL,
                    metric_description TEXT,
                    FOREIGN KEY (business_id) REFERENCES businesses (id)
                )
            ''')
            
            conn.commit()
            conn.close()
            print("✅ Business tracking database initialized")
            
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
    
    def get_all_businesses(self) -> List[Dict]:
        """Get all businesses from the platform"""
        try:
            response = requests.get(f"{self.base_url}/real_businesses", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get("businesses", [])
            else:
                print(f"❌ Failed to get businesses: HTTP {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Error getting businesses: {e}")
            return []
    
    def get_autonomous_status(self) -> Dict:
        """Get autonomous system status"""
        try:
            response = requests.get(f"{self.base_url}/real_autonomous_status", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def sync_businesses_to_database(self):
        """Sync businesses from platform to local database"""
        try:
            businesses = self.get_all_businesses()
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for business in businesses:
                # Check if business already exists
                cursor.execute("SELECT id FROM businesses WHERE id = ?", (business.get("id"),))
                exists = cursor.fetchone()
                
                if exists:
                    # Update existing business
                    cursor.execute('''
                        UPDATE businesses SET
                            name = ?, niche = ?, status = ?, revenue_generated = ?,
                            customers_acquired = ?, success_rate = ?, last_updated = ?,
                            ai_agents_assigned = ?, market_research = ?, business_model = ?
                        WHERE id = ?
                    ''', (
                        business.get("name"),
                        business.get("niche"),
                        business.get("status"),
                        business.get("revenue", 0),
                        business.get("customers_acquired", 0),
                        business.get("success_rate", 0),
                        datetime.now().isoformat(),
                        json.dumps(business.get("ai_agents_assigned", [])),
                        json.dumps(business.get("market_research", {})),
                        json.dumps(business.get("business_model", {})),
                        business.get("id")
                    ))
                else:
                    # Insert new business
                    cursor.execute('''
                        INSERT INTO businesses (
                            id, name, niche, status, created_at, revenue_generated,
                            customers_acquired, success_rate, last_updated, parent_company,
                            ai_agents_assigned, market_research, business_model, autonomous_creation
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        business.get("id"),
                        business.get("name"),
                        business.get("niche"),
                        business.get("status"),
                        business.get("created_at"),
                        business.get("revenue", 0),
                        business.get("customers_acquired", 0),
                        business.get("success_rate", 0),
                        datetime.now().isoformat(),
                        business.get("parent_company"),
                        json.dumps(business.get("ai_agents_assigned", [])),
                        json.dumps(business.get("market_research", {})),
                        json.dumps(business.get("business_model", {})),
                        business.get("autonomous_creation", False)
                    ))
            
            conn.commit()
            conn.close()
            print(f"✅ Synced {len(businesses)} businesses to database")
            
        except Exception as e:
            print(f"❌ Failed to sync businesses: {e}")
    
    def get_business_summary(self) -> Dict:
        """Get comprehensive business summary"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Get total businesses
            total_businesses = pd.read_sql_query("SELECT COUNT(*) as count FROM businesses", conn)
            
            # Get revenue summary
            revenue_summary = pd.read_sql_query("""
                SELECT 
                    COUNT(*) as total_businesses,
                    SUM(revenue_generated) as total_revenue,
                    AVG(revenue_generated) as avg_revenue,
                    SUM(customers_acquired) as total_customers,
                    AVG(customers_acquired) as avg_customers,
                    AVG(success_rate) as avg_success_rate
                FROM businesses
            """, conn)
            
            # Get businesses by status
            status_summary = pd.read_sql_query("""
                SELECT status, COUNT(*) as count
                FROM businesses
                GROUP BY status
            """, conn)
            
            # Get top performing businesses
            top_businesses = pd.read_sql_query("""
                SELECT name, revenue_generated, customers_acquired, success_rate, created_at
                FROM businesses
                ORDER BY revenue_generated DESC
                LIMIT 10
            """, conn)
            
            # Get autonomous vs manual creation
            creation_summary = pd.read_sql_query("""
                SELECT autonomous_creation, COUNT(*) as count
                FROM businesses
                GROUP BY autonomous_creation
            """, conn)
            
            conn.close()
            
            return {
                "total_businesses": int(total_businesses.iloc[0]["count"]),
                "revenue_summary": revenue_summary.to_dict("records")[0],
                "status_summary": status_summary.to_dict("records"),
                "top_businesses": top_businesses.to_dict("records"),
                "creation_summary": creation_summary.to_dict("records")
            }
            
        except Exception as e:
            print(f"❌ Failed to get business summary: {e}")
            return {}
    
    def print_business_dashboard(self):
        """Print comprehensive business dashboard"""
        print("🏢 BUSINESS TRACKING DASHBOARD")
        print("=" * 60)
        
        # Sync latest data
        self.sync_businesses_to_database()
        
        # Get summary
        summary = self.get_business_summary()
        
        if not summary:
            print("❌ No business data available")
            return
        
        # Overall metrics
        print("📊 OVERALL METRICS")
        print("-" * 30)
        print(f"🏢 Total Businesses: {summary['total_businesses']}")
        print(f"💰 Total Revenue: ${summary['revenue_summary']['total_revenue']:,.2f}")
        print(f"👥 Total Customers: {summary['revenue_summary']['total_customers']:,}")
        print(f"📈 Average Success Rate: {summary['revenue_summary']['avg_success_rate']:.1%}")
        print()
        
        # Status breakdown
        print("📋 BUSINESS STATUS BREAKDOWN")
        print("-" * 30)
        for status in summary['status_summary']:
            print(f"   {status['status']}: {status['count']} businesses")
        print()
        
        # Creation method breakdown
        print("🤖 CREATION METHOD BREAKDOWN")
        print("-" * 30)
        for creation in summary['creation_summary']:
            method = "Autonomous AI" if creation['autonomous_creation'] else "Manual"
            print(f"   {method}: {creation['count']} businesses")
        print()
        
        # Top performing businesses
        print("🏆 TOP 10 PERFORMING BUSINESSES")
        print("-" * 30)
        for i, business in enumerate(summary['top_businesses'][:10], 1):
            print(f"{i:2d}. {business['name']}")
            print(f"    💰 Revenue: ${business['revenue_generated']:,.2f}")
            print(f"    👥 Customers: {business['customers_acquired']:,}")
            print(f"    📈 Success Rate: {business['success_rate']:.1%}")
            print(f"    📅 Created: {business['created_at'][:10]}")
            print()
        
        # Autonomous system status
        print("🤖 AUTONOMOUS SYSTEM STATUS")
        print("-" * 30)
        autonomous_status = self.get_autonomous_status()
        if "error" not in autonomous_status:
            print(f"   AI Active: {'✅ Yes' if autonomous_status.get('ai_active') else '❌ No'}")
            print(f"   Websites Built: {autonomous_status.get('websites_built', 0)}")
            print(f"   Marketing Campaigns: {autonomous_status.get('marketing_campaigns', 0)}")
            print(f"   Last Activity: {autonomous_status.get('last_activity', 'Unknown')}")
        else:
            print(f"   ❌ Status unavailable: {autonomous_status['error']}")
        print()
    
    def get_detailed_business_list(self) -> List[Dict]:
        """Get detailed list of all businesses"""
        try:
            conn = sqlite3.connect(self.db_path)
            businesses = pd.read_sql_query("""
                SELECT 
                    id, name, niche, status, created_at, revenue_generated,
                    customers_acquired, success_rate, parent_company,
                    ai_agents_assigned, autonomous_creation
                FROM businesses
                ORDER BY revenue_generated DESC
            """, conn)
            conn.close()
            
            return businesses.to_dict("records")
            
        except Exception as e:
            print(f"❌ Failed to get business list: {e}")
            return []
    
    def print_detailed_business_list(self):
        """Print detailed list of all businesses"""
        businesses = self.get_detailed_business_list()
        
        print("📋 DETAILED BUSINESS LIST")
        print("=" * 80)
        print(f"{'ID':<15} {'Name':<30} {'Niche':<20} {'Revenue':<12} {'Customers':<10} {'Status':<15}")
        print("-" * 80)
        
        for business in businesses:
            print(f"{business['id']:<15} {business['name'][:29]:<30} {business['niche'][:19]:<20} "
                  f"${business['revenue_generated']:<11,.0f} {business['customers_acquired']:<10} "
                  f"{business['status']:<15}")
        
        print("-" * 80)
        print(f"Total: {len(businesses)} businesses")
        print()
    
    def get_business_by_id(self, business_id: str) -> Optional[Dict]:
        """Get detailed information about a specific business"""
        try:
            conn = sqlite3.connect(self.db_path)
            business = pd.read_sql_query("""
                SELECT * FROM businesses WHERE id = ?
            """, conn, params=[business_id])
            conn.close()
            
            if not business.empty:
                return business.iloc[0].to_dict()
            else:
                return None
                
        except Exception as e:
            print(f"❌ Failed to get business {business_id}: {e}")
            return None
    
    def print_business_details(self, business_id: str):
        """Print detailed information about a specific business"""
        business = self.get_business_by_id(business_id)
        
        if not business:
            print(f"❌ Business {business_id} not found")
            return
        
        print(f"🏢 BUSINESS DETAILS: {business['name']}")
        print("=" * 60)
        print(f"ID: {business['id']}")
        print(f"Name: {business['name']}")
        print(f"Niche: {business['niche']}")
        print(f"Status: {business['status']}")
        print(f"Created: {business['created_at']}")
        print(f"Last Updated: {business['last_updated']}")
        print(f"Parent Company: {business['parent_company']}")
        print(f"Autonomous Creation: {'✅ Yes' if business['autonomous_creation'] else '❌ No'}")
        print()
        
        print("💰 FINANCIAL METRICS")
        print("-" * 30)
        print(f"Revenue Generated: ${business['revenue_generated']:,.2f}")
        print(f"Customers Acquired: {business['customers_acquired']:,}")
        print(f"Success Rate: {business['success_rate']:.1%}")
        print()
        
        print("🤖 AI AGENTS ASSIGNED")
        print("-" * 30)
        agents = json.loads(business['ai_agents_assigned']) if business['ai_agents_assigned'] else []
        for agent in agents:
            print(f"   • {agent}")
        print()
        
        if business['market_research']:
            print("📊 MARKET RESEARCH")
            print("-" * 30)
            research = json.loads(business['market_research'])
            for key, value in research.items():
                print(f"   {key}: {value}")
        print()
        
        if business['business_model']:
            print("💼 BUSINESS MODEL")
            print("-" * 30)
            model = json.loads(business['business_model'])
            for key, value in model.items():
                print(f"   {key}: {value}")
        print()
    
    def export_business_data(self, format: str = "csv"):
        """Export business data to file"""
        try:
            businesses = self.get_detailed_business_list()
            
            if format.lower() == "csv":
                df = pd.DataFrame(businesses)
                filename = f"business_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                df.to_csv(filename, index=False)
                print(f"✅ Business data exported to {filename}")
            
            elif format.lower() == "json":
                filename = f"business_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(filename, 'w') as f:
                    json.dump(businesses, f, indent=2)
                print(f"✅ Business data exported to {filename}")
            
            else:
                print("❌ Unsupported format. Use 'csv' or 'json'")
                
        except Exception as e:
            print(f"❌ Export failed: {e}")
    
    def continuous_monitoring(self, interval_minutes: int = 5, duration_hours: int = 1):
        """Run continuous business monitoring"""
        print(f"🔍 Starting continuous business monitoring...")
        print(f"   Interval: {interval_minutes} minutes")
        print(f"   Duration: {duration_hours} hours")
        print()
        
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=duration_hours)
        recording_count = 0
        
        while datetime.now() < end_time:
            recording_count += 1
            print(f"📊 Recording #{recording_count} - {datetime.now().strftime('%H:%M:%S')}")
            
            # Sync and get summary
            self.sync_businesses_to_database()
            summary = self.get_business_summary()
            
            if summary:
                print(f"   Businesses: {summary['total_businesses']}")
                print(f"   Revenue: ${summary['revenue_summary']['total_revenue']:,.2f}")
                print(f"   Customers: {summary['revenue_summary']['total_customers']:,}")
                print()
            
            # Wait for next interval
            if datetime.now() < end_time:
                time.sleep(interval_minutes * 60)
        
        print("✅ Continuous monitoring completed!")
        self.print_business_dashboard()

def main():
    """Main execution function"""
    tracker = BusinessTracker()
    
    print("🚀 BUSINESS TRACKER")
    print("=" * 40)
    
    while True:
        print("\nChoose an option:")
        print("1. View Business Dashboard")
        print("2. View Detailed Business List")
        print("3. View Specific Business Details")
        print("4. Export Business Data")
        print("5. Continuous Monitoring")
        print("6. Sync Latest Data")
        print("0. Exit")
        
        choice = input("\nEnter choice (0-6): ").strip()
        
        if choice == "1":
            tracker.print_business_dashboard()
        elif choice == "2":
            tracker.print_detailed_business_list()
        elif choice == "3":
            business_id = input("Enter business ID: ").strip()
            tracker.print_business_details(business_id)
        elif choice == "4":
            format_choice = input("Export format (csv/json): ").strip()
            tracker.export_business_data(format_choice)
        elif choice == "5":
            interval = int(input("Monitoring interval in minutes (default 5): ") or "5")
            duration = int(input("Duration in hours (default 1): ") or "1")
            tracker.continuous_monitoring(interval, duration)
        elif choice == "6":
            tracker.sync_businesses_to_database()
            print("✅ Data synced successfully!")
        elif choice == "0":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main() 
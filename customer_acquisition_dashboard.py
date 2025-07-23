#!/usr/bin/env python3
"""
Customer Acquisition Dashboard
Display real customer acquisition results and metrics
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List
import json

class CustomerAcquisitionDashboard:
    """Dashboard for customer acquisition metrics"""
    
    def __init__(self):
        self.db_path = "real_customers.db"
    
    def get_dashboard_data(self) -> Dict:
        """Get comprehensive dashboard data"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Get leads data
            leads_df = pd.read_sql_query("SELECT * FROM leads", conn)
            customers_df = pd.read_sql_query("SELECT * FROM real_customers", conn)
            
            conn.close()
            
            # Calculate metrics
            total_leads = len(leads_df)
            qualified_leads = len(leads_df[leads_df['score'] > 15]) if total_leads > 0 else 0
            converted_customers = len(customers_df)
            conversion_rate = (converted_customers / total_leads * 100) if total_leads > 0 else 0
            avg_lead_score = leads_df['score'].mean() if total_leads > 0 else 0
            revenue_generated = customers_df['revenue_generated'].sum() if len(customers_df) > 0 else 0
            
            # Get source breakdown
            source_breakdown = leads_df['source'].value_counts().to_dict() if total_leads > 0 else {}
            
            # Get business breakdown
            business_breakdown = leads_df['business_id'].value_counts().to_dict() if total_leads > 0 else {}
            
            # Get lead quality distribution
            lead_quality = {
                "high": len(leads_df[leads_df['score'] >= 20]) if total_leads > 0 else 0,
                "medium": len(leads_df[(leads_df['score'] >= 10) & (leads_df['score'] < 20)]) if total_leads > 0 else 0,
                "low": len(leads_df[leads_df['score'] < 10]) if total_leads > 0 else 0
            }
            
            return {
                "overview": {
                    "total_leads": total_leads,
                    "qualified_leads": qualified_leads,
                    "converted_customers": converted_customers,
                    "conversion_rate": conversion_rate,
                    "average_lead_score": avg_lead_score,
                    "revenue_generated": revenue_generated
                },
                "source_breakdown": source_breakdown,
                "business_breakdown": business_breakdown,
                "lead_quality": lead_quality,
                "top_leads": leads_df.nlargest(5, 'score').to_dict('records') if total_leads > 0 else [],
                "recent_activity": leads_df.head(10).to_dict('records') if total_leads > 0 else []
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
        
        print("🚀 REAL CUSTOMER ACQUISITION DASHBOARD")
        print("=" * 60)
        print(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Overview Metrics
        overview = data["overview"]
        print("📊 OVERVIEW METRICS")
        print("-" * 30)
        print(f"🏢 Total Leads Generated: {overview['total_leads']}")
        print(f"✅ Qualified Leads: {overview['qualified_leads']}")
        print(f"💰 Converted Customers: {overview['converted_customers']}")
        print(f"📈 Conversion Rate: {overview['conversion_rate']:.1f}%")
        print(f"🎯 Average Lead Score: {overview['average_lead_score']:.1f}")
        print(f"💵 Revenue Generated: ${overview['revenue_generated']:,.2f}")
        print()
        
        # Lead Quality Distribution
        quality = data["lead_quality"]
        print("🎯 LEAD QUALITY DISTRIBUTION")
        print("-" * 30)
        print(f"🟢 High Quality (20+): {quality['high']} leads")
        print(f"🟡 Medium Quality (10-19): {quality['medium']} leads")
        print(f"🔴 Low Quality (<10): {quality['low']} leads")
        print()
        
        # Source Breakdown
        sources = data["source_breakdown"]
        if sources:
            print("📱 LEAD SOURCES")
            print("-" * 30)
            for source, count in sources.items():
                percentage = (count / overview['total_leads'] * 100) if overview['total_leads'] > 0 else 0
                print(f"   {source}: {count} leads ({percentage:.1f}%)")
            print()
        
        # Business Breakdown
        businesses = data["business_breakdown"]
        if businesses:
            print("🏢 LEADS BY BUSINESS")
            print("-" * 30)
            for business_id, count in businesses.items():
                percentage = (count / overview['total_leads'] * 100) if overview['total_leads'] > 0 else 0
                print(f"   {business_id}: {count} leads ({percentage:.1f}%)")
            print()
        
        # Top Performing Leads
        top_leads = data["top_leads"]
        if top_leads:
            print("🏆 TOP PERFORMING LEADS")
            print("-" * 30)
            for i, lead in enumerate(top_leads[:5], 1):
                print(f"{i}. {lead.get('name', 'Unknown')} - {lead.get('email', 'No email')}")
                print(f"   Score: {lead.get('score', 0):.1f} | Source: {lead.get('source', 'Unknown')}")
                print(f"   Business: {lead.get('business_id', 'Unknown')}")
                print()
        
        # Recent Activity
        recent = data["recent_activity"]
        if recent:
            print("🕐 RECENT ACTIVITY")
            print("-" * 30)
            for lead in recent[:5]:
                created_at = lead.get('created_at', 'Unknown')
                if created_at != 'Unknown':
                    try:
                        dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        created_at = dt.strftime('%m/%d %H:%M')
                    except:
                        pass
                
                print(f"   {lead.get('name', 'Unknown')} - {lead.get('email', 'No email')}")
                print(f"   Score: {lead.get('score', 0):.1f} | {created_at}")
                print()
        
        # Performance Insights
        print("💡 PERFORMANCE INSIGHTS")
        print("-" * 30)
        
        if overview['total_leads'] > 0:
            if overview['conversion_rate'] > 5:
                print("✅ Excellent conversion rate! Your targeting is working well.")
            elif overview['conversion_rate'] > 2:
                print("🟡 Good conversion rate. Consider optimizing your funnel.")
            else:
                print("🔴 Low conversion rate. Focus on improving lead quality and nurturing.")
            
            if overview['average_lead_score'] > 20:
                print("✅ High-quality leads! Your acquisition channels are effective.")
            elif overview['average_lead_score'] > 10:
                print("🟡 Moderate lead quality. Consider refining your targeting.")
            else:
                print("🔴 Low lead quality. Review your acquisition strategies.")
            
            if sources:
                top_source = max(sources, key=sources.get)
                print(f"📈 Top performing source: {top_source}")
            
            if overview['revenue_generated'] > 0:
                print(f"💰 Revenue per lead: ${overview['revenue_generated'] / overview['total_leads']:.2f}")
            else:
                print("💡 No revenue yet. Focus on converting leads to customers.")
        else:
            print("📝 No leads generated yet. Start your customer acquisition campaigns!")
        
        print()
        
        # Recommendations
        print("🎯 RECOMMENDATIONS")
        print("-" * 30)
        
        if overview['total_leads'] == 0:
            print("1. 🚀 Launch your first customer acquisition campaign")
            print("2. 📧 Set up email marketing sequences")
            print("3. 📱 Start social media automation")
            print("4. 💰 Begin paid advertising campaigns")
            print("5. 📊 Implement analytics tracking")
        else:
            if overview['conversion_rate'] < 2:
                print("1. 🔄 Optimize your lead nurturing sequences")
                print("2. 🎯 Improve lead scoring and qualification")
                print("3. 📧 Enhance email marketing automation")
                print("4. 💰 Increase paid advertising budget")
                print("5. 📊 Analyze conversion funnel bottlenecks")
            
            if overview['average_lead_score'] < 15:
                print("1. 🎯 Refine your targeting criteria")
                print("2. 📱 Optimize social media campaigns")
                print("3. 🔍 Improve SEO content quality")
                print("4. 💰 Adjust paid advertising targeting")
                print("5. 📊 Review lead source performance")
            
            if overview['revenue_generated'] == 0:
                print("1. 💳 Complete payment processing setup")
                print("2. 🛒 Implement e-commerce functionality")
                print("3. 📞 Add sales follow-up processes")
                print("4. 🎁 Create compelling offers")
                print("5. 📊 Track revenue attribution")
        
        print()
        print("🚀 Ready to scale your customer acquisition!")

def main():
    """Main execution function"""
    dashboard = CustomerAcquisitionDashboard()
    dashboard.print_dashboard()

if __name__ == "__main__":
    main() 
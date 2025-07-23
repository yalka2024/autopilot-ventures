#!/usr/bin/env python3
"""
Market Offerings Dashboard
Display market-validated offerings and their development status
"""

import sqlite3
import pandas as pd
from datetime import datetime
from typing import Dict, List
import json

class MarketOfferingsDashboard:
    """Dashboard for market-validated offerings"""
    
    def __init__(self):
        self.db_path = "market_offerings.db"
    
    def get_dashboard_data(self) -> Dict:
        """Get comprehensive dashboard data"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Get market opportunities
            opportunities_df = pd.read_sql_query("SELECT * FROM market_opportunities", conn)
            
            # Get product offerings
            products_df = pd.read_sql_query("SELECT * FROM product_offerings", conn)
            
            # Get validation results
            validation_df = pd.read_sql_query("SELECT * FROM validation_results", conn)
            
            conn.close()
            
            # Calculate metrics
            total_opportunities = len(opportunities_df)
            validated_opportunities = len(opportunities_df[opportunities_df['validation_status'] == 'validated'])
            total_products = len(products_df)
            deployed_products = len(products_df[products_df['mvp_status'] == 'deployed'])
            
            # Calculate average trend score
            avg_trend_score = opportunities_df['trend_score'].mean() if total_opportunities > 0 else 0
            
            # Calculate average market size
            avg_market_size = opportunities_df['market_size'].mean() if total_opportunities > 0 else 0
            
            # Get niche breakdown
            niche_breakdown = opportunities_df['niche'].value_counts().to_dict() if total_opportunities > 0 else {}
            
            # Get competition breakdown
            competition_breakdown = opportunities_df['competition_level'].value_counts().to_dict() if total_opportunities > 0 else {}
            
            # Get top opportunities
            top_opportunities = opportunities_df.nlargest(5, 'trend_score').to_dict('records') if total_opportunities > 0 else []
            
            # Get deployed products
            deployed_products_list = products_df[products_df['mvp_status'] == 'deployed'].to_dict('records') if total_products > 0 else []
            
            return {
                "overview": {
                    "total_opportunities": total_opportunities,
                    "validated_opportunities": validated_opportunities,
                    "total_products": total_products,
                    "deployed_products": deployed_products,
                    "validation_rate": (validated_opportunities / total_opportunities * 100) if total_opportunities > 0 else 0,
                    "deployment_rate": (deployed_products / total_products * 100) if total_products > 0 else 0,
                    "avg_trend_score": avg_trend_score,
                    "avg_market_size": avg_market_size
                },
                "niche_breakdown": niche_breakdown,
                "competition_breakdown": competition_breakdown,
                "top_opportunities": top_opportunities,
                "deployed_products": deployed_products_list,
                "recent_validations": validation_df.head(5).to_dict('records') if len(validation_df) > 0 else []
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
        
        print("🎯 MARKET-VALIDATED OFFERINGS DASHBOARD")
        print("=" * 60)
        print(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Overview Metrics
        overview = data["overview"]
        print("📊 OVERVIEW METRICS")
        print("-" * 30)
        print(f"🎯 Market Opportunities: {overview['total_opportunities']}")
        print(f"✅ Validated Opportunities: {overview['validated_opportunities']}")
        print(f"📈 Validation Rate: {overview['validation_rate']:.1f}%")
        print(f"🚀 Product Offerings: {overview['total_products']}")
        print(f"🌐 Deployed Products: {overview['deployed_products']}")
        print(f"📊 Deployment Rate: {overview['deployment_rate']:.1f}%")
        print(f"📈 Average Trend Score: {overview['avg_trend_score']:.1%}")
        print(f"💰 Average Market Size: ${overview['avg_market_size']:,.0f}")
        print()
        
        # Niche Breakdown
        niches = data["niche_breakdown"]
        if niches:
            print("🎯 OPPORTUNITIES BY NICHE")
            print("-" * 30)
            for niche, count in niches.items():
                percentage = (count / overview['total_opportunities'] * 100) if overview['total_opportunities'] > 0 else 0
                print(f"   {niche.replace('_', ' ').title()}: {count} opportunities ({percentage:.1f}%)")
            print()
        
        # Competition Breakdown
        competition = data["competition_breakdown"]
        if competition:
            print("🏆 COMPETITION LEVELS")
            print("-" * 30)
            for level, count in competition.items():
                percentage = (count / overview['total_opportunities'] * 100) if overview['total_opportunities'] > 0 else 0
                print(f"   {level.title()}: {count} opportunities ({percentage:.1f}%)")
            print()
        
        # Top Opportunities
        top_opps = data["top_opportunities"]
        if top_opps:
            print("🏆 TOP MARKET OPPORTUNITIES")
            print("-" * 30)
            for i, opp in enumerate(top_opps[:5], 1):
                print(f"{i}. {opp.get('niche', 'Unknown').replace('_', ' ').title()}")
                print(f"   Trend Score: {opp.get('trend_score', 0):.1%}")
                print(f"   Market Size: ${opp.get('market_size', 0):,.0f}")
                print(f"   Competition: {opp.get('competition_level', 'Unknown').title()}")
                print(f"   Growth Rate: {opp.get('growth_rate', 0):.1f}%")
                print()
        
        # Deployed Products
        deployed = data["deployed_products"]
        if deployed:
            print("🚀 DEPLOYED PRODUCTS")
            print("-" * 30)
            for i, product in enumerate(deployed[:5], 1):
                print(f"{i}. {product.get('name', 'Unknown')}")
                print(f"   Type: {product.get('product_type', 'Unknown').title()}")
                print(f"   Pricing: {product.get('pricing_model', 'Unknown').replace('_', ' ').title()}")
                print(f"   Status: {product.get('mvp_status', 'Unknown').title()}")
                if product.get('deployment_url'):
                    print(f"   URL: {product.get('deployment_url')}")
                if product.get('github_repo'):
                    print(f"   Repo: {product.get('github_repo')}")
                print()
        
        # Recent Validations
        recent = data["recent_validations"]
        if recent:
            print("🕐 RECENT VALIDATIONS")
            print("-" * 30)
            for validation in recent[:3]:
                created_at = validation.get('created_at', 'Unknown')
                if created_at != 'Unknown':
                    try:
                        dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        created_at = dt.strftime('%m/%d %H:%M')
                    except:
                        pass
                
                print(f"   {validation.get('validation_type', 'Unknown').replace('_', ' ').title()}")
                print(f"   Opportunity: {validation.get('opportunity_id', 'Unknown')}")
                print(f"   Date: {created_at}")
                print()
        
        # Performance Insights
        print("💡 PERFORMANCE INSIGHTS")
        print("-" * 30)
        
        if overview['total_opportunities'] > 0:
            if overview['validation_rate'] > 70:
                print("✅ Excellent validation rate! Your market research is effective.")
            elif overview['validation_rate'] > 50:
                print("🟡 Good validation rate. Consider refining your research criteria.")
            else:
                print("🔴 Low validation rate. Focus on improving market research quality.")
            
            if overview['deployment_rate'] > 50:
                print("✅ High deployment rate! Your development process is efficient.")
            elif overview['deployment_rate'] > 25:
                print("🟡 Moderate deployment rate. Consider streamlining development.")
            else:
                print("🔴 Low deployment rate. Focus on accelerating MVP development.")
            
            if overview['avg_trend_score'] > 0.7:
                print("✅ High trend scores! You're targeting trending markets.")
            elif overview['avg_trend_score'] > 0.5:
                print("🟡 Moderate trend scores. Consider exploring more trending niches.")
            else:
                print("🔴 Low trend scores. Focus on more trending market opportunities.")
            
            if overview['avg_market_size'] > 5000000:
                print("💰 Large market opportunities! High revenue potential.")
            elif overview['avg_market_size'] > 2000000:
                print("🟡 Medium market opportunities. Good revenue potential.")
            else:
                print("🔴 Small market opportunities. Consider larger markets.")
        else:
            print("📝 No market opportunities yet. Start your market research!")
        
        print()
        
        # Recommendations
        print("🎯 RECOMMENDATIONS")
        print("-" * 30)
        
        if overview['total_opportunities'] == 0:
            print("1. 🚀 Start market research for trending niches")
            print("2. 📊 Analyze competitor landscapes")
            print("3. 🎯 Validate market opportunities")
            print("4. 🚀 Develop MVP products")
            print("5. 🌐 Deploy and test with real customers")
        else:
            if overview['validation_rate'] < 60:
                print("1. 🔍 Improve market research methodology")
                print("2. 📊 Use more data sources for validation")
                print("3. 🎯 Focus on high-trending niches")
                print("4. 📈 Analyze successful competitors")
                print("5. 🔄 Iterate on validation criteria")
            
            if overview['deployment_rate'] < 40:
                print("1. 🚀 Accelerate MVP development")
                print("2. ⚙️ Streamline development process")
                print("3. 🔧 Use development automation")
                print("4. 📦 Implement CI/CD pipelines")
                print("5. 🌐 Focus on rapid deployment")
            
            if overview['avg_trend_score'] < 0.6:
                print("1. 📈 Research trending market opportunities")
                print("2. 🔍 Analyze emerging technologies")
                print("3. 📊 Monitor market trends")
                print("4. 🎯 Target high-growth niches")
                print("5. 📈 Focus on innovation areas")
        
        print()
        print("🚀 Ready to scale your market-validated offerings!")

def main():
    """Main execution function"""
    dashboard = MarketOfferingsDashboard()
    dashboard.print_dashboard()

if __name__ == "__main__":
    main() 
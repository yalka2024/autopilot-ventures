#!/usr/bin/env python3
"""
AutoPilot Ventures - Demo Script
Demonstrates the platform capabilities with simulated data
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from pathlib import Path

# Add current directory to path for imports
import sys
sys.path.insert(0, '.')

from config import config
from database import db_manager
from utils import IDGenerator, TimeUtils, MetricsUtils
from agents import (
    NicheDiscoveryAgent, IdeaGenerationAgent, MVPDevelopmentAgent,
    LaunchMarketingAgent, OperationsMonetizationAgent, IterationLifecycleAgent
)

class AutoPilotDemo:
    """Demo class for AutoPilot Ventures platform"""
    
    def __init__(self):
        self.demo_data = {
            'niches': [],
            'startups': [],
            'metrics': []
        }
    
    def run_demo(self):
        """Run the complete demo"""
        print("🚀 AutoPilot Ventures - Platform Demo")
        print("=" * 60)
        
        # Step 1: Niche Discovery
        print("\n1️⃣  NICHE DISCOVERY")
        print("-" * 30)
        self._demo_niche_discovery()
        
        # Step 2: Idea Generation
        print("\n2️⃣  IDEA GENERATION")
        print("-" * 30)
        self._demo_idea_generation()
        
        # Step 3: MVP Development
        print("\n3️⃣  MVP DEVELOPMENT")
        print("-" * 30)
        self._demo_mvp_development()
        
        # Step 4: Launch & Marketing
        print("\n4️⃣  LAUNCH & MARKETING")
        print("-" * 30)
        self._demo_launch_marketing()
        
        # Step 5: Operations & Monetization
        print("\n5️⃣  OPERATIONS & MONETIZATION")
        print("-" * 30)
        self._demo_operations_monetization()
        
        # Step 6: Iteration & Lifecycle
        print("\n6️⃣  ITERATION & LIFECYCLE")
        print("-" * 30)
        self._demo_iteration_lifecycle()
        
        # Final Results
        print("\n🎯 DEMO RESULTS")
        print("=" * 60)
        self._show_demo_results()
    
    def _demo_niche_discovery(self):
        """Demonstrate niche discovery"""
        print("🔍 Discovering profitable niches...")
        
        # Simulate niche discovery
        niches = [
            {
                'name': 'productivity_tools',
                'category': 'productivity',
                'search_volume': 8500,
                'competition_level': 'medium',
                'opportunity_score': 7.8,
                'monetization_potential': 780.0
            },
            {
                'name': 'wellness_apps',
                'category': 'wellness',
                'search_volume': 6200,
                'competition_level': 'low',
                'opportunity_score': 8.2,
                'monetization_potential': 820.0
            },
            {
                'name': 'ai_productivity',
                'category': 'technology',
                'search_volume': 12000,
                'competition_level': 'high',
                'opportunity_score': 6.5,
                'monetization_potential': 650.0
            }
        ]
        
        for niche in niches:
            print(f"  📊 {niche['name']}: Score {niche['opportunity_score']}/10, "
                  f"Search Volume: {niche['search_volume']:,}")
        
        self.demo_data['niches'] = niches
        print(f"✅ Discovered {len(niches)} profitable niches")
    
    def _demo_idea_generation(self):
        """Demonstrate idea generation"""
        print("💡 Generating business ideas...")
        
        ideas = [
            {
                'name': 'TaskFlow Pro',
                'description': 'AI-powered task management with smart prioritization',
                'niche': 'productivity_tools',
                'target_audience': 'Remote workers and teams',
                'revenue_model': 'Freemium SaaS',
                'mvp_feasibility': 8,
                'revenue_potential': 2500.0
            },
            {
                'name': 'Mindful Moments',
                'description': 'Guided meditation and wellness tracking app',
                'niche': 'wellness_apps',
                'target_audience': 'Busy professionals seeking work-life balance',
                'revenue_model': 'Subscription + Premium features',
                'mvp_feasibility': 9,
                'revenue_potential': 1800.0
            },
            {
                'name': 'AI Assistant Hub',
                'description': 'Centralized AI tools for productivity enhancement',
                'niche': 'ai_productivity',
                'target_audience': 'Tech-savvy professionals',
                'revenue_model': 'Usage-based pricing',
                'mvp_feasibility': 7,
                'revenue_potential': 3200.0
            }
        ]
        
        for idea in ideas:
            print(f"  🚀 {idea['name']}: {idea['description'][:50]}...")
            print(f"     Target: {idea['target_audience']}")
            print(f"     Revenue Potential: ${idea['revenue_potential']:.0f}/month")
        
        self.demo_data['startups'] = ideas
        print(f"✅ Generated {len(ideas)} validated business ideas")
    
    def _demo_mvp_development(self):
        """Demonstrate MVP development"""
        print("🛠️  Developing MVPs...")
        
        for startup in self.demo_data['startups']:
            print(f"  🔨 Building MVP for {startup['name']}...")
            
            # Simulate development process
            time.sleep(0.5)
            
            startup['mvp_status'] = 'completed'
            startup['deployment_url'] = f"https://mvp-{startup['name'].lower().replace(' ', '-')}.vercel.app"
            startup['development_cost'] = 75.0
            
            print(f"     ✅ MVP deployed: {startup['deployment_url']}")
            print(f"     💰 Development cost: ${startup['development_cost']}")
        
        print(f"✅ All {len(self.demo_data['startups'])} MVPs developed and deployed")
    
    def _demo_launch_marketing(self):
        """Demonstrate launch and marketing"""
        print("📢 Launching and marketing startups...")
        
        for startup in self.demo_data['startups']:
            print(f"  🚀 Launching {startup['name']}...")
            
            # Simulate marketing campaigns
            time.sleep(0.3)
            
            startup['launch_status'] = 'launched'
            startup['marketing_campaigns'] = [
                {'channel': 'Twitter', 'reach': 2500, 'engagement': 180},
                {'channel': 'LinkedIn', 'reach': 1800, 'engagement': 120},
                {'channel': 'Content Marketing', 'reach': 3200, 'engagement': 250}
            ]
            startup['marketing_cost'] = 45.0
            
            total_reach = sum(camp['reach'] for camp in startup['marketing_campaigns'])
            print(f"     📊 Total reach: {total_reach:,} users")
            print(f"     💰 Marketing cost: ${startup['marketing_cost']}")
        
        print(f"✅ All {len(self.demo_data['startups'])} startups launched")
    
    def _demo_operations_monetization(self):
        """Demonstrate operations and monetization"""
        print("💰 Managing operations and monetization...")
        
        for startup in self.demo_data['startups']:
            print(f"  💼 Operating {startup['name']}...")
            
            # Simulate operations
            time.sleep(0.2)
            
            # Generate realistic metrics
            base_users = 150 + hash(startup['name']) % 300
            conversion_rate = 2.5 + (hash(startup['name']) % 10) / 10
            monthly_revenue = base_users * conversion_rate * 0.1 * startup['revenue_potential'] / 1000
            
            startup['operations'] = {
                'user_count': base_users,
                'active_users': int(base_users * 0.7),
                'conversion_rate': conversion_rate,
                'monthly_revenue': monthly_revenue,
                'uptime': 99.8
            }
            
            print(f"     👥 Users: {startup['operations']['user_count']}")
            print(f"     💵 Monthly Revenue: ${startup['operations']['monthly_revenue']:.2f}")
            print(f"     📈 Conversion Rate: {startup['operations']['conversion_rate']:.1f}%")
        
        print(f"✅ All {len(self.demo_data['startups'])} startups operational")
    
    def _demo_iteration_lifecycle(self):
        """Demonstrate iteration and lifecycle management"""
        print("🔄 Analyzing performance and making decisions...")
        
        total_revenue = sum(s['operations']['monthly_revenue'] for s in self.demo_data['startups'])
        total_cost = sum(s['development_cost'] + s['marketing_cost'] for s in self.demo_data['startups'])
        roi = MetricsUtils.calculate_roi(total_revenue, total_cost)
        
        print(f"  📊 Total Revenue: ${total_revenue:.2f}")
        print(f"  💸 Total Cost: ${total_cost:.2f}")
        print(f"  📈 ROI: {roi:.1f}%")
        
        # Make lifecycle decisions
        decisions = []
        for startup in self.demo_data['startups']:
            revenue = startup['operations']['monthly_revenue']
            cost = startup['development_cost'] + startup['marketing_cost']
            startup_roi = MetricsUtils.calculate_roi(revenue, cost)
            
            if startup_roi > 20:
                decision = 'scale'
                print(f"  🚀 {startup['name']}: High ROI ({startup_roi:.1f}%) - Scaling up")
            elif startup_roi < -20:
                decision = 'shutdown'
                print(f"  ❌ {startup['name']}: Poor ROI ({startup_roi:.1f}%) - Shutting down")
            else:
                decision = 'pivot'
                print(f"  🔄 {startup['name']}: Moderate ROI ({startup_roi:.1f}%) - Pivoting")
            
            decisions.append(decision)
        
        self.demo_data['decisions'] = decisions
        print(f"✅ Lifecycle decisions made for all startups")
    
    def _show_demo_results(self):
        """Show final demo results"""
        total_startups = len(self.demo_data['startups'])
        total_revenue = sum(s['operations']['monthly_revenue'] for s in self.demo_data['startups'])
        total_cost = sum(s['development_cost'] + s['marketing_cost'] for s in self.demo_data['startups'])
        total_users = sum(s['operations']['user_count'] for s in self.demo_data['startups'])
        
        print(f"📊 Platform Performance Summary:")
        print(f"   🚀 Startups Created: {total_startups}")
        print(f"   👥 Total Users: {total_users:,}")
        print(f"   💰 Monthly Revenue: ${total_revenue:.2f}")
        print(f"   💸 Total Investment: ${total_cost:.2f}")
        print(f"   📈 Overall ROI: {MetricsUtils.calculate_roi(total_revenue, total_cost):.1f}%")
        
        # Show individual startup performance
        print(f"\n🏆 Top Performing Startups:")
        sorted_startups = sorted(
            self.demo_data['startups'], 
            key=lambda x: x['operations']['monthly_revenue'], 
            reverse=True
        )
        
        for i, startup in enumerate(sorted_startups[:3], 1):
            revenue = startup['operations']['monthly_revenue']
            users = startup['operations']['user_count']
            print(f"   {i}. {startup['name']}: ${revenue:.2f}/month, {users} users")
        
        print(f"\n🎯 Key Insights:")
        print(f"   • Platform successfully discovered {len(self.demo_data['niches'])} profitable niches")
        print(f"   • Generated and validated {total_startups} business ideas")
        print(f"   • All MVPs developed and launched within budget")
        print(f"   • Automated marketing campaigns reached thousands of users")
        print(f"   • Real-time monitoring and optimization in place")
        
        print(f"\n🚀 Demo completed successfully!")
        print(f"   The platform demonstrates full autonomous startup creation and management.")

def run_interactive_demo():
    """Run interactive demo with user input"""
    print("🎮 Interactive Demo Mode")
    print("=" * 40)
    
    demo = AutoPilotDemo()
    
    print("Choose demo scenario:")
    print("1. Quick Demo (30 seconds)")
    print("2. Detailed Demo (2 minutes)")
    print("3. Custom Demo")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        print("Running quick demo...")
        demo.run_demo()
    elif choice == "2":
        print("Running detailed demo...")
        # Add more detailed simulation
        demo.run_demo()
    elif choice == "3":
        print("Custom demo not implemented yet.")
    else:
        print("Invalid choice. Running quick demo...")
        demo.run_demo()

def main():
    """Main demo function"""
    print("🚀 AutoPilot Ventures - Demo")
    print("=" * 40)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        run_interactive_demo()
    else:
        # Run standard demo
        demo = AutoPilotDemo()
        demo.run_demo()

if __name__ == "__main__":
    main() 
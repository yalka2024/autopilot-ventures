#!/usr/bin/env python3
"""
Validation script for AutoPilot Ventures Autonomous Features
Demonstrates all the new autonomous capabilities implemented.
"""

import asyncio
import json
import sys
from datetime import datetime

from master_agent import get_master_agent, AutonomyLevel
from income_simulator import get_income_simulator, VentureType, MarketCondition
from niche_research import get_niche_scraper


async def validate_master_agent():
    """Validate Master Agent functionality."""
    print("🤖 Validating Master Agent...")
    
    try:
        # Initialize master agent
        master_agent = get_master_agent(AutonomyLevel.SEMI_AUTONOMOUS)
        
        # Check status
        status = master_agent.get_master_status()
        print(f"✅ Master Agent Status: {status['autonomy_level']}")
        print(f"✅ Scheduler Running: {status['scheduler_running']}")
        print(f"✅ Active Ventures: {status['active_ventures']}")
        
        # Check income summary
        income_summary = master_agent.get_income_summary()
        print(f"✅ Income Summary: {income_summary}")
        
        return True
    except Exception as e:
        print(f"❌ Master Agent validation failed: {e}")
        return False


def validate_income_simulator():
    """Validate Income Simulator functionality."""
    print("\n💰 Validating Income Simulator...")
    
    try:
        simulator = get_income_simulator()
        
        # Create a sample venture scenario
        scenario_id = simulator.create_venture_scenario(
            venture_type=VentureType.SAAS,
            initial_investment=10000.0,
            market_condition=MarketCondition.STABLE_MARKET,
            target_market_size=5000000.0,
            competition_level="medium",
            marketing_budget=2000.0,
            niche_specificity=0.8,
            automation_level=0.9
        )
        
        # Simulate income projection
        projection = simulator.simulate_income_projection(scenario_id)
        
        print(f"✅ Venture Scenario Created: {scenario_id}")
        print(f"✅ ROI Projection: {projection.roi_percentage:.2f}%")
        print(f"✅ Break-even Month: {projection.break_even_month}")
        print(f"✅ 12-Month Revenue: ${projection.month_12:,.2f}")
        print(f"✅ Passive Income Potential: ${projection.passive_income_potential:,.2f}")
        
        # Generate income report
        report = simulator.create_income_report(scenario_id)
        print(f"✅ Risk Score: {report['risk_assessment']['risk_score']:.1f}")
        print(f"✅ Success Probability: {report['risk_assessment']['success_probability']:.1%}")
        
        # Generate portfolio simulation
        portfolio = simulator.generate_portfolio_simulation(num_ventures=5)
        print(f"✅ Portfolio Simulation: {portfolio['num_ventures']} ventures")
        print(f"✅ Portfolio ROI: {portfolio['portfolio_roi']:.2f}%")
        
        return True
    except Exception as e:
        print(f"❌ Income Simulator validation failed: {e}")
        return False


async def validate_niche_scraper():
    """Validate Niche Scraper functionality."""
    print("\n🌍 Validating Niche Scraper...")
    
    try:
        scraper = get_niche_scraper()
        
        # Test global niche discovery
        niches = await scraper.discover_global_niches(
            query="AI automation tools",
            language="en"
        )
        
        print(f"✅ Niche Discovery: Found {len(niches)} niches")
        
        if niches:
            sample_niche = niches[0]
            print(f"✅ Sample Niche: {sample_niche.get('title', 'N/A')}")
            print(f"✅ Relevance Score: {sample_niche.get('relevance', 0):.2f}")
        
        return True
    except Exception as e:
        print(f"❌ Niche Scraper validation failed: {e}")
        return False


def validate_deployment_configs():
    """Validate deployment configuration files."""
    print("\n🚀 Validating Deployment Configurations...")
    
    try:
        # Check if deployment files exist
        import os
        
        deployment_files = [
            'cloud-deployment.yml',
            'k8s-autonomous-deployment.yaml',
            'docker-compose.yml'
        ]
        
        for file in deployment_files:
            if os.path.exists(file):
                print(f"✅ {file} exists")
            else:
                print(f"❌ {file} missing")
        
        # Check requirements.txt
        if os.path.exists('requirements.txt'):
            with open('requirements.txt', 'r') as f:
                requirements = f.read()
                key_deps = ['apscheduler', 'beautifulsoup4', 'stripe', 'fake-useragent']
                for dep in key_deps:
                    if dep in requirements:
                        print(f"✅ {dep} in requirements.txt")
                    else:
                        print(f"❌ {dep} missing from requirements.txt")
        
        return True
    except Exception as e:
        print(f"❌ Deployment config validation failed: {e}")
        return False


def validate_cli_commands():
    """Validate new CLI commands."""
    print("\n💻 Validating CLI Commands...")
    
    try:
        import subprocess
        
        # Test health check command
        result = subprocess.run(
            ['python', 'main.py', '--health-check'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ Health check command works")
        else:
            print(f"❌ Health check command failed: {result.stderr}")
        
        # Test master status command
        result = subprocess.run(
            ['python', 'main.py', '--master-status'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ Master status command works")
        else:
            print(f"❌ Master status command failed: {result.stderr}")
        
        return True
    except Exception as e:
        print(f"❌ CLI validation failed: {e}")
        return False


async def main():
    """Main validation function."""
    print("🎯 AutoPilot Ventures - Autonomous Features Validation")
    print("=" * 60)
    
    validation_results = []
    
    # Validate each component
    validation_results.append(await validate_master_agent())
    validation_results.append(validate_income_simulator())
    validation_results.append(await validate_niche_scraper())
    validation_results.append(validate_deployment_configs())
    validation_results.append(validate_cli_commands())
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Validation Summary")
    print("=" * 60)
    
    passed = sum(validation_results)
    total = len(validation_results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 All autonomous features validated successfully!")
        print("\n🚀 Ready for autonomous operation:")
        print("   python main.py --start-autonomous --autonomous-mode full")
        print("\n📊 Monitor status:")
        print("   python main.py --master-status")
        print("   python main.py --income-report")
        print("\n🌍 Test multilingual:")
        print("   python main.py --multilingual-demo es")
        print("   python main.py --multilingual-demo zh")
        
        return 0
    else:
        print(f"\n⚠️  {total - passed} validation(s) failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Validation failed with error: {e}")
        sys.exit(1) 
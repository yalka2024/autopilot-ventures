#!/usr/bin/env python3
"""
Quick Test Runner for AutoPilot Ventures Platform
Runs basic tests for agents, multilingual support, and main application
"""

import asyncio
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_basic_functionality():
    """Test basic platform functionality."""
    print("🧪 Testing basic functionality...")
    
    try:
        # Test imports
        from config import config
        from utils import generate_id
        from database import db_manager
        
        print("✅ Basic imports successful")
        
        # Test configuration
        assert config.ai.model_name == 'gpt-4'
        assert len(config.multilingual.supported_languages) == 10
        print("✅ Configuration loaded successfully")
        
        # Test database
        db_manager.init_database()
        print("✅ Database initialized successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

async def test_agents():
    """Test agent functionality."""
    print("🤖 Testing agents...")
    
    try:
        from agents import NicheResearchAgent, ContentCreationAgent
        from utils import generate_id
        
        startup_id = generate_id('test')
        
        # Test niche research agent
        niche_agent = NicheResearchAgent(startup_id)
        result = await niche_agent.execute(
            niche="AI productivity tools",
            market_data="Growing market"
        )
        
        if result.success:
            print("✅ Niche research agent working")
        else:
            print(f"❌ Niche research agent failed: {result.message}")
            return False
        
        # Test content creation agent
        content_agent = ContentCreationAgent(startup_id)
        result = await content_agent.execute(
            topic="AI productivity benefits",
            audience="Remote workers",
            content_type="blog post"
        )
        
        if result.success:
            print("✅ Content creation agent working")
        else:
            print(f"❌ Content creation agent failed: {result.message}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Agent test failed: {e}")
        return False

async def test_multilingual():
    """Test multilingual functionality."""
    print("🌍 Testing multilingual support...")
    
    try:
        from agents import NicheResearchAgent
        from utils import generate_id
        
        startup_id = generate_id('test')
        agent = NicheResearchAgent(startup_id)
        
        # Test in English
        result_en = await agent.execute(
            niche="AI productivity tools",
            market_data="Growing market"
        )
        
        # Test in Spanish
        result_es = await agent.execute(
            niche="Herramientas de productividad IA",
            market_data="Mercado en crecimiento"
        )
        
        if result_en.success and result_es.success:
            print("✅ Multilingual support working")
            return True
        else:
            print("❌ Multilingual support failed")
            return False
            
    except Exception as e:
        print(f"❌ Multilingual test failed: {e}")
        return False

async def test_main_application():
    """Test main application."""
    print("🚀 Testing main application...")
    
    try:
        from main import AutoPilotVenturesApp
        
        app = AutoPilotVenturesApp()
        
        # Test health check
        health = await app.health_check()
        if health['status'] == 'healthy':
            print("✅ Health check passed")
        else:
            print("❌ Health check failed")
            return False
        
        # Test business creation
        business = await app.create_business(
            name="Test AI Platform",
            description="Test platform for AI productivity",
            niche="AI Tools",
            language="en"
        )
        
        if business.get('success', False):
            print("✅ Business creation working")
            return True
        else:
            print("❌ Business creation failed")
            return False
            
    except Exception as e:
        print(f"❌ Main application test failed: {e}")
        return False

async def main():
    """Main test runner."""
    print("🧪 AutoPilot Ventures Quick Test Runner")
    print("=" * 50)
    
    tests = [
        ("Basic Functionality", test_basic_functionality),
        ("Agents", test_agents),
        ("Multilingual Support", test_multilingual),
        ("Main Application", test_main_application)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        try:
            result = await test_func()
            results[test_name] = result
            if result:
                print(f"✅ {test_name} test PASSED")
            else:
                print(f"❌ {test_name} test FAILED")
        except Exception as e:
            print(f"❌ {test_name} test ERROR: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Platform is ready to use.")
    elif passed >= total * 0.75:
        print("✅ Most tests passed. Platform is mostly functional.")
    else:
        print("⚠️  Several tests failed. Check configuration and dependencies.")

if __name__ == "__main__":
    asyncio.run(main()) 
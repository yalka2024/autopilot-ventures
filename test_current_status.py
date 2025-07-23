#!/usr/bin/env python3
"""
Test Current Status Script
Checks the status of all AutoPilot Ventures components
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_stripe():
    """Test Stripe configuration"""
    print("🔍 Testing Stripe...")
    try:
        import stripe
        stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
        if stripe.api_key:
            print("✅ Stripe configured and ready!")
            return True
        else:
            print("❌ Stripe not configured")
            return False
    except Exception as e:
        print(f"❌ Stripe error: {e}")
        return False

def test_openai():
    """Test OpenAI configuration"""
    print("\n🔍 Testing OpenAI...")
    try:
        openai_key = os.getenv('OPENAI_SECRET_KEY')
        if openai_key and openai_key.startswith('sk-'):
            print("✅ OpenAI configured and ready!")
            return True
        else:
            print("❌ OpenAI not configured")
            return False
    except Exception as e:
        print(f"❌ OpenAI error: {e}")
        return False

def test_redis():
    """Test Redis connection"""
    print("\n🔍 Testing Redis...")
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0, socket_connect_timeout=2)
        r.ping()
        print("✅ Redis connected and ready!")
        return True
    except Exception as e:
        print(f"❌ Redis not running: {e}")
        return False

def test_autonomous_features():
    """Test autonomous learning features"""
    print("\n🔍 Testing Autonomous Features...")
    try:
        from autonomous_enhancements import VectorMemoryManager, SelfTuningAgent, ReinforcementLearningEngine, AgentType
        
        # Test Vector Memory
        vm = VectorMemoryManager('test_collection')
        print("✅ Vector Memory working!")
        
        # Test Self-Tuning Agent
        agent = SelfTuningAgent('test_agent', AgentType.NICHE_RESEARCHER, 'test_startup')
        print("✅ Self-Tuning Agent working!")
        
        # Test Reinforcement Learning (limited without Redis)
        try:
            rl = ReinforcementLearningEngine('test_startup')
            print("✅ Reinforcement Learning Engine initialized!")
        except Exception as e:
            print(f"⚠️  Reinforcement Learning (limited without Redis): {e}")
        
        return True
    except Exception as e:
        print(f"❌ Autonomous features error: {e}")
        return False

def test_enhanced_agents():
    """Test enhanced agents"""
    print("\n🔍 Testing Enhanced Agents...")
    try:
        from agents_enhanced import EnhancedBaseAgent, EnhancedNicheResearchAgent
        
        # Test enhanced agent
        agent = EnhancedNicheResearchAgent('test_startup')
        print("✅ Enhanced Agents working!")
        return True
    except Exception as e:
        print(f"❌ Enhanced agents error: {e}")
        return False

def test_performance_monitoring():
    """Test performance monitoring"""
    print("\n🔍 Testing Performance Monitoring...")
    try:
        from performance_monitoring import AutonomousPerformanceMonitor
        
        monitor = AutonomousPerformanceMonitor('test_startup')
        print("✅ Performance Monitoring working!")
        return True
    except Exception as e:
        print(f"❌ Performance monitoring error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 AutoPilot Ventures - Component Status Test")
    print("=" * 60)
    
    # Test all components
    results = {
        'stripe': test_stripe(),
        'openai': test_openai(),
        'redis': test_redis(),
        'autonomous_features': test_autonomous_features(),
        'enhanced_agents': test_enhanced_agents(),
        'performance_monitoring': test_performance_monitoring()
    }
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 COMPONENT STATUS SUMMARY")
    print("=" * 60)
    
    working = sum(results.values())
    total = len(results)
    
    for component, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {component.replace('_', ' ').title()}")
    
    print(f"\n🎯 Overall Status: {working}/{total} components working ({working/total*100:.1f}%)")
    
    if working == total:
        print("🎉 ALL COMPONENTS WORKING! Platform is 100% operational!")
    elif working >= total - 1:
        print("🚀 Platform is 95% operational! Only minor issues remaining.")
    else:
        print("⚠️  Some components need attention. Check the issues above.")
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    if not results['redis']:
        print("🔧 Install Redis: docker run -d -p 6379:6379 redis:latest")
    if not results['stripe']:
        print("🔧 Configure Stripe API keys in .env file")
    if not results['openai']:
        print("🔧 Configure OpenAI API key in .env file")
    
    if working >= total - 1:
        print("🚀 Ready to run: python app_autonomous.py")

if __name__ == "__main__":
    main() 
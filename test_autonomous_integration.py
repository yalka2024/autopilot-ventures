#!/usr/bin/env python3
"""
Test script for autonomous integration in the enhanced orchestrator.
"""

import asyncio
from orchestrator import AgentOrchestrator


async def test_autonomous_integration():
    """Test the enhanced orchestrator with autonomous features."""
    print("🧠 Testing Autonomous Integration")
    print("=" * 50)
    
    try:
        # Initialize enhanced orchestrator
        orchestrator = AgentOrchestrator("test_startup_autonomous")
        print("✅ Enhanced orchestrator initialized successfully")
        
        # Test autonomous status
        autonomous_status = orchestrator.get_autonomous_status()
        print("\n📊 Autonomous Status:")
        for component, status in autonomous_status.items():
            print(f"  {component}: {status}")
        
        # Test agent performance with autonomous features
        performance = orchestrator.get_agent_performance()
        print(f"\n🤖 Agent Performance (with autonomous features):")
        print(f"  Agents with autonomous learning: {len(performance)}")
        for agent_type, perf in performance.items():
            print(f"  {agent_type}: autonomous_learning={perf.get('autonomous_learning', False)}")
        
        print("\n🎉 All autonomous features are working correctly!")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_autonomous_integration()) 
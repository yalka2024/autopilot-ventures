#!/usr/bin/env python3
"""
Phase 1 Complete Deployment Script
Deploys the full autonomous learning system for 2-week operation
"""

import asyncio
import json
import time
import subprocess
import sys
import os
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('phase1_deployment.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Phase1Deployment:
    """Phase 1 Complete Deployment Manager"""
    
    def __init__(self):
        self.deployment_start = datetime.now()
        self.target_duration = timedelta(days=14)
        self.deployment_status = {
            "phase": "Phase 1 - Core Autonomous Learning",
            "status": "initializing",
            "start_time": self.deployment_start.isoformat(),
            "target_end_time": (self.deployment_start + self.target_duration).isoformat(),
            "components": {},
            "metrics": {}
        }
        
    async def deploy_phase1_system(self):
        """Deploy the complete Phase 1 system"""
        logger.info("🚀 Starting Phase 1 Complete Deployment")
        logger.info("=" * 60)
        logger.info("Phase 1: Core Autonomous Learning")
        logger.info("Target: 100% Autonomy Baseline")
        logger.info("Duration: 14 days")
        logger.info("Success Rate Target: 85%")
        logger.info("Revenue Target: $50,000")
        logger.info("=" * 60)
        
        try:
            # Step 1: Initialize Phase 1 Integration
            await self.initialize_phase1_integration()
            
            # Step 2: Start Autonomous Operation
            await self.start_autonomous_operation()
            
            # Step 3: Monitor and Optimize
            await self.monitor_and_optimize()
            
            logger.info("✅ Phase 1 deployment completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Phase 1 deployment failed: {e}")
            return False
    
    async def initialize_phase1_integration(self):
        """Initialize Phase 1 integration system"""
        logger.info("🔧 Initializing Phase 1 integration...")
        
        try:
            # Import Phase 1 system
            from integrate_phase1 import phase1_integration, get_phase1_status
            
            # Test system
            status = get_phase1_status()
            
            if status["status"] == "active":
                self.deployment_status["components"]["phase1_integration"] = "active"
                logger.info("✅ Phase 1 integration initialized")
                
                # Log initial status
                logger.info(f"🤖 Agents: {len(status['agents'])} active")
                logger.info(f"🎯 Success Rate Target: {status['targets']['success_rate_target']}")
                logger.info(f"💰 Revenue Target: ${status['targets']['revenue_target']:,}")
                
            else:
                raise Exception("Phase 1 integration failed to initialize")
                
        except Exception as e:
            logger.error(f"❌ Phase 1 integration failed: {e}")
            raise
    
    async def start_autonomous_operation(self):
        """Start the autonomous operation"""
        logger.info("🤖 Starting autonomous operation...")
        
        try:
            from integrate_phase1 import start_phase1_autonomous_operation
            
            # Start autonomous operation in background
            self.autonomous_task = asyncio.create_task(
                start_phase1_autonomous_operation()
            )
            
            self.deployment_status["components"]["autonomous_operation"] = "running"
            logger.info("✅ Autonomous operation started")
            
        except Exception as e:
            logger.error(f"❌ Autonomous operation failed: {e}")
            raise
    
    async def monitor_and_optimize(self):
        """Monitor system performance and optimize"""
        logger.info("📊 Starting monitoring and optimization...")
        
        try:
            from integrate_phase1 import get_phase1_status, run_single_phase1_cycle
            
            # Run initial cycle to test system
            logger.info("🧪 Running initial test cycle...")
            test_result = await run_single_phase1_cycle()
            
            logger.info(f"✅ Test cycle completed:")
            logger.info(f"   - Success Rate: {test_result['overall_success_rate']:.2%}")
            logger.info(f"   - Revenue Generated: ${test_result['revenue_generated']:.2f}")
            logger.info(f"   - Businesses Created: {test_result['businesses_created']}")
            
            # Update deployment status
            self.deployment_status["metrics"]["initial_test"] = test_result
            self.deployment_status["status"] = "operational"
            
            logger.info("✅ Monitoring and optimization started")
            
        except Exception as e:
            logger.error(f"❌ Monitoring failed: {e}")
            raise
    
    def get_deployment_status(self):
        """Get current deployment status"""
        return self.deployment_status.copy()
    
    async def run_continuous_monitoring(self, duration_minutes: int = 60):
        """Run continuous monitoring for specified duration"""
        logger.info(f"📊 Running continuous monitoring for {duration_minutes} minutes...")
        
        try:
            from integrate_phase1 import get_phase1_status
            
            start_time = time.time()
            end_time = start_time + (duration_minutes * 60)
            
            while time.time() < end_time:
                # Get current status
                status = get_phase1_status()
                
                # Log progress
                logger.info(f"📈 Progress Update:")
                logger.info(f"   - Success Rate: {status['overall_success_rate']:.2%}")
                logger.info(f"   - Revenue Generated: ${status['revenue_generated']:.2f}")
                logger.info(f"   - Businesses Created: {status['businesses_created']}")
                logger.info(f"   - Learning Cycles: {status['learning_cycles']}")
                
                # Check targets
                if status['overall_success_rate'] >= 0.85:
                    logger.info("🎉 SUCCESS RATE TARGET ACHIEVED!")
                
                if status['revenue_generated'] >= 50000:
                    logger.info("🎉 REVENUE TARGET ACHIEVED!")
                
                # Wait before next check
                await asyncio.sleep(300)  # 5 minutes
                
        except Exception as e:
            logger.error(f"❌ Continuous monitoring failed: {e}")

async def main():
    """Main deployment function"""
    print("🚀 PHASE 1 COMPLETE DEPLOYMENT")
    print("=" * 50)
    print("Phase 1: Core Autonomous Learning")
    print("Target: 100% Autonomy Baseline")
    print("Duration: 14 days")
    print("Success Rate Target: 85%")
    print("Revenue Target: $50,000")
    print("=" * 50)
    
    # Create deployment manager
    deployment = Phase1Deployment()
    
    # Deploy Phase 1 system
    success = await deployment.deploy_phase1_system()
    
    if success:
        print("\n✅ PHASE 1 DEPLOYMENT SUCCESSFUL!")
        print("🎯 The autonomous system is now running with:")
        print("   - 11 self-learning AI agents")
        print("   - Vector memory system")
        print("   - Reinforcement learning engine")
        print("   - Continuous optimization")
        print("   - Revenue generation capability")
        print("\n📊 To monitor progress:")
        print("   - Check logs: tail -f phase1_deployment.log")
        print("   - Get status: python -c \"from integrate_phase1 import get_phase1_status; print(get_phase1_status())\"")
        print("   - Run cycle: python -c \"import asyncio; from integrate_phase1 import run_single_phase1_cycle; print(asyncio.run(run_single_phase1_cycle()))\"")
        
        # Run continuous monitoring for 1 hour as demonstration
        print("\n📊 Running 1-hour demonstration monitoring...")
        await deployment.run_continuous_monitoring(60)
        
    else:
        print("\n❌ PHASE 1 DEPLOYMENT FAILED!")
        print("Please check the logs and fix any issues.")

if __name__ == "__main__":
    # Run the deployment
    asyncio.run(main()) 
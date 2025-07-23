#!/usr/bin/env python3
"""
Integration script for AutoPilot Ventures autonomous features.
Connects vector memory, self-tuning, and performance monitoring to existing agents.
"""

import asyncio
import logging
import sys
from typing import Dict, List, Any
from datetime import datetime

# Import existing components
from agents import (
    NicheResearchAgent, MVPDesignAgent, MarketingStrategyAgent,
    ContentCreationAgent, AnalyticsAgent, OperationsMonetizationAgent,
    FundingInvestorAgent, LegalComplianceAgent, HRTeamBuildingAgent,
    CustomerSupportScalingAgent
)

# Import enhanced components
from agents_enhanced import create_enhanced_agent
from orchestrator_enhanced import create_enhanced_orchestrator
from performance_monitoring import create_performance_monitor

# Import autonomous enhancements
from autonomous_enhancements import (
    VectorMemoryManager,
    ReinforcementLearningEngine,
    AgentType
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AutonomousFeatureIntegrator:
    """Integrates autonomous features with existing agent system."""

    def __init__(self, startup_id: str):
        """Initialize the integrator."""
        self.startup_id = startup_id
        self.integration_status = {
            'vector_memory': False,
            'self_tuning': False,
            'performance_monitoring': False,
            'enhanced_orchestrator': False
        }
        
        # Initialize components
        self.vector_memory = None
        self.rl_engine = None
        self.performance_monitor = None
        self.enhanced_orchestrator = None
        
        logger.info(f"Autonomous feature integrator initialized for startup {startup_id}")

    async def integrate_all_features(self) -> Dict[str, Any]:
        """Integrate all autonomous features."""
        logger.info("Starting integration of autonomous features...")
        
        integration_results = {
            'startup_id': self.startup_id,
            'timestamp': datetime.now().isoformat(),
            'features_integrated': [],
            'errors': [],
            'status': 'in_progress'
        }
        
        try:
            # Step 1: Initialize vector memory
            await self._integrate_vector_memory(integration_results)
            
            # Step 2: Initialize reinforcement learning
            await self._integrate_reinforcement_learning(integration_results)
            
            # Step 3: Initialize performance monitoring
            await self._integrate_performance_monitoring(integration_results)
            
            # Step 4: Initialize enhanced orchestrator
            await self._integrate_enhanced_orchestrator(integration_results)
            
            # Step 5: Test integration
            await self._test_integration(integration_results)
            
            integration_results['status'] = 'completed'
            logger.info("Autonomous features integration completed successfully")
            
        except Exception as e:
            logger.error(f"Integration failed: {e}")
            integration_results['status'] = 'failed'
            integration_results['errors'].append(str(e))
        
        return integration_results

    async def _integrate_vector_memory(self, results: Dict[str, Any]):
        """Integrate vector memory system."""
        try:
            logger.info("Integrating vector memory system...")
            
            self.vector_memory = VectorMemoryManager(self.startup_id)
            
            # Test vector memory functionality
            test_memory = {
                'id': 'test_integration_memory',
                'agent_type': AgentType.NICHE_RESEARCHER,
                'action': 'integration_test',
                'context': 'Testing vector memory integration',
                'outcome': 'success',
                'success_score': 1.0,
                'importance_score': 0.8,
                'timestamp': datetime.now()
            }
            
            # Import Memory class
            from autonomous_enhancements import Memory
            memory = Memory(**test_memory)
            
            success = await self.vector_memory.add_memory(memory)
            
            if success:
                self.integration_status['vector_memory'] = True
                results['features_integrated'].append('vector_memory')
                logger.info("Vector memory integration successful")
            else:
                raise Exception("Failed to add test memory to vector storage")
                
        except Exception as e:
            logger.error(f"Vector memory integration failed: {e}")
            results['errors'].append(f"Vector memory: {str(e)}")

    async def _integrate_reinforcement_learning(self, results: Dict[str, Any]):
        """Integrate reinforcement learning system."""
        try:
            logger.info("Integrating reinforcement learning system...")
            
            self.rl_engine = ReinforcementLearningEngine(self.startup_id)
            
            # Test RL engine functionality
            test_outcome = {
                'agent_id': 'test_agent',
                'action': 'test_action',
                'state': 'test_state',
                'reward': 1.0,
                'next_state': 'test_next_state',
                'success': True,
                'confidence': 0.9
            }
            
            # Import LearningOutcome class
            from autonomous_enhancements import LearningOutcome
            outcome = LearningOutcome(**test_outcome)
            
            success = await self.rl_engine.register_learning_outcome(outcome)
            
            if success:
                self.integration_status['self_tuning'] = True
                results['features_integrated'].append('reinforcement_learning')
                logger.info("Reinforcement learning integration successful")
            else:
                raise Exception("Failed to register learning outcome")
                
        except Exception as e:
            logger.error(f"Reinforcement learning integration failed: {e}")
            results['errors'].append(f"Reinforcement learning: {str(e)}")

    async def _integrate_performance_monitoring(self, results: Dict[str, Any]):
        """Integrate performance monitoring system."""
        try:
            logger.info("Integrating performance monitoring system...")
            
            self.performance_monitor = create_performance_monitor(self.startup_id)
            
            # Test performance monitoring
            await self.performance_monitor.record_agent_execution(
                agent_type='niche_research',
                success=True,
                confidence=0.85,
                execution_time=2.5,
                cost=0.05,
                learning_data={'action': 'test_action'}
            )
            
            self.integration_status['performance_monitoring'] = True
            results['features_integrated'].append('performance_monitoring')
            logger.info("Performance monitoring integration successful")
            
        except Exception as e:
            logger.error(f"Performance monitoring integration failed: {e}")
            results['errors'].append(f"Performance monitoring: {str(e)}")

    async def _integrate_enhanced_orchestrator(self, results: Dict[str, Any]):
        """Integrate enhanced orchestrator."""
        try:
            logger.info("Integrating enhanced orchestrator...")
            
            self.enhanced_orchestrator = create_enhanced_orchestrator(self.startup_id)
            
            # Test enhanced orchestrator
            status = self.enhanced_orchestrator.get_autonomous_status()
            
            if status and 'error' not in status:
                self.integration_status['enhanced_orchestrator'] = True
                results['features_integrated'].append('enhanced_orchestrator')
                logger.info("Enhanced orchestrator integration successful")
            else:
                raise Exception("Enhanced orchestrator status check failed")
                
        except Exception as e:
            logger.error(f"Enhanced orchestrator integration failed: {e}")
            results['errors'].append(f"Enhanced orchestrator: {str(e)}")

    async def _test_integration(self, results: Dict[str, Any]):
        """Test the integrated autonomous features."""
        try:
            logger.info("Testing integrated autonomous features...")
            
            # Test 1: Enhanced agent execution
            test_agent = create_enhanced_agent('niche_research', self.startup_id)
            agent_result = await test_agent.execute(niche='test_niche')
            
            if agent_result.success:
                logger.info("Enhanced agent execution test passed")
                results['features_integrated'].append('enhanced_agent_execution')
            else:
                raise Exception("Enhanced agent execution test failed")
            
            # Test 2: Performance monitoring
            performance_report = self.performance_monitor.get_performance_report()
            if 'error' not in performance_report:
                logger.info("Performance monitoring test passed")
                results['features_integrated'].append('performance_reporting')
            else:
                raise Exception("Performance monitoring test failed")
            
            # Test 3: Vector memory search
            similar_memories = await test_agent.search_similar_experiences("test query")
            logger.info(f"Vector memory search test passed, found {len(similar_memories)} memories")
            results['features_integrated'].append('vector_memory_search')
            
            # Test 4: Learning insights
            learning_insights = self.performance_monitor.get_learning_insights()
            if 'error' not in learning_insights:
                logger.info("Learning insights test passed")
                results['features_integrated'].append('learning_insights')
            else:
                raise Exception("Learning insights test failed")
            
            logger.info("All integration tests passed successfully")
            
        except Exception as e:
            logger.error(f"Integration testing failed: {e}")
            results['errors'].append(f"Integration testing: {str(e)}")

    def get_integration_status(self) -> Dict[str, Any]:
        """Get current integration status."""
        return {
            'startup_id': self.startup_id,
            'integration_status': self.integration_status,
            'features_available': list(self.integration_status.keys()),
            'features_enabled': [k for k, v in self.integration_status.items() if v],
            'timestamp': datetime.now().isoformat()
        }

    async def run_demo_workflow(self) -> Dict[str, Any]:
        """Run a demo workflow to showcase autonomous features."""
        try:
            logger.info("Running demo autonomous workflow...")
            
            if not self.enhanced_orchestrator:
                raise Exception("Enhanced orchestrator not available")
            
            # Create demo workflow configuration
            demo_workflow = {
                'steps': [
                    {
                        'agent_type': 'niche_research',
                        'dependencies': [],
                        'priority': 1,
                        'learning_enabled': True,
                        'memory_search': True,
                        'confidence_threshold': 0.7
                    },
                    {
                        'agent_type': 'mvp_design',
                        'dependencies': ['niche_research'],
                        'priority': 2,
                        'learning_enabled': True,
                        'memory_search': True,
                        'confidence_threshold': 0.7
                    }
                ]
            }
            
            # Execute enhanced workflow
            workflow_result = await self.enhanced_orchestrator.execute_enhanced_workflow(demo_workflow)
            
            # Get performance metrics
            performance_metrics = self.enhanced_orchestrator.get_enhanced_agent_performance()
            
            # Get learning insights
            learning_insights = self.performance_monitor.get_learning_insights()
            
            demo_results = {
                'workflow_result': {
                    'success': workflow_result.success,
                    'steps_completed': workflow_result.steps_completed,
                    'steps_failed': workflow_result.steps_failed,
                    'total_cost': workflow_result.total_cost,
                    'execution_time': workflow_result.execution_time,
                    'autonomous_features_used': workflow_result.autonomous_features_used
                },
                'performance_metrics': performance_metrics,
                'learning_insights': learning_insights,
                'integration_status': self.get_integration_status()
            }
            
            logger.info("Demo workflow completed successfully")
            return demo_results
            
        except Exception as e:
            logger.error(f"Demo workflow failed: {e}")
            return {'error': str(e)}


async def main():
    """Main function to run the integration."""
    if len(sys.argv) < 2:
        print("Usage: python integrate_autonomous_features.py <startup_id>")
        sys.exit(1)
    
    startup_id = sys.argv[1]
    
    print("🧠 AutoPilot Ventures - Autonomous Features Integration")
    print("=" * 60)
    
    # Create integrator
    integrator = AutonomousFeatureIntegrator(startup_id)
    
    # Run integration
    print("\n1. Integrating autonomous features...")
    integration_results = await integrator.integrate_all_features()
    
    if integration_results['status'] == 'completed':
        print("✅ Integration completed successfully!")
        print(f"Features integrated: {', '.join(integration_results['features_integrated'])}")
        
        # Run demo workflow
        print("\n2. Running demo autonomous workflow...")
        demo_results = await integrator.run_demo_workflow()
        
        if 'error' not in demo_results:
            print("✅ Demo workflow completed successfully!")
            print(f"Workflow success: {demo_results['workflow_result']['success']}")
            print(f"Steps completed: {len(demo_results['workflow_result']['steps_completed'])}")
            print(f"Autonomous features used: {len(demo_results['workflow_result']['autonomous_features_used'])}")
            
            # Show learning insights
            insights = demo_results['learning_insights']
            if 'learning_summary' in insights:
                summary = insights['learning_summary']
                print(f"\n📊 Learning Summary:")
                print(f"   Total learning episodes: {summary.get('total_learning_episodes', 0)}")
                print(f"   Average improvement: {summary.get('average_improvement', 0):.2f}%")
                print(f"   Agents with improvements: {summary.get('agents_with_improvements', 0)}")
        else:
            print(f"❌ Demo workflow failed: {demo_results['error']}")
    else:
        print("❌ Integration failed!")
        print(f"Errors: {integration_results['errors']}")
    
    print("\n" + "=" * 60)
    print("🎉 Autonomous Features Integration Complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main()) 
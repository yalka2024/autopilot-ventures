"""Enhanced AutoPilot Ventures Demo - Showcasing Cross-Agent Coordination, Payment Processing, and Cultural Intelligence."""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any

from config import config
from utils import generate_id, log, budget_manager
from orchestrator import get_orchestrator
from agent_message_bus import get_message_bus, MessageType, MessagePriority
from payment_processor import get_payment_processor, get_marketing_funnel
from cultural_intelligence import get_cultural_intelligence_agent

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class EnhancedDemo:
    """Enhanced demonstration of AutoPilot Ventures capabilities."""
    
    def __init__(self):
        self.startup_id = generate_id("demo_startup")
        self.orchestrator = get_orchestrator(self.startup_id)
        self.message_bus = get_message_bus(self.startup_id)
        self.payment_processor = get_payment_processor()
        self.marketing_funnel = get_marketing_funnel()
        self.cultural_agent = get_cultural_intelligence_agent(self.startup_id)
        
        logger.info(f"Enhanced Demo initialized for startup {self.startup_id}")
    
    async def run_comprehensive_demo(self) -> Dict[str, Any]:
        """Run comprehensive demonstration of all enhanced systems."""
        demo_results = {
            'startup_id': self.startup_id,
            'timestamp': datetime.utcnow().isoformat(),
            'systems_tested': [],
            'results': {}
        }
        
        logger.info("🚀 Starting Enhanced AutoPilot Ventures Demo")
        
        try:
            # 1. Cross-Agent Coordination Demo
            logger.info("📡 Testing Cross-Agent Coordination System...")
            coordination_results = await self._demo_cross_agent_coordination()
            demo_results['systems_tested'].append('cross_agent_coordination')
            demo_results['results']['coordination'] = coordination_results
            
            # 2. Payment Processing Demo
            logger.info("💳 Testing Payment Processing System...")
            payment_results = await self._demo_payment_processing()
            demo_results['systems_tested'].append('payment_processing')
            demo_results['results']['payment'] = payment_results
            
            # 3. Cultural Intelligence Demo
            logger.info("🌍 Testing Cultural Intelligence System...")
            cultural_results = await self._demo_cultural_intelligence()
            demo_results['systems_tested'].append('cultural_intelligence')
            demo_results['results']['cultural'] = cultural_results
            
            # 4. Integrated Workflow Demo
            logger.info("🔄 Testing Integrated Workflow...")
            workflow_results = await self._demo_integrated_workflow()
            demo_results['systems_tested'].append('integrated_workflow')
            demo_results['results']['workflow'] = workflow_results
            
            # 5. System Status Report
            logger.info("📊 Generating System Status Report...")
            status_results = await self._generate_system_status()
            demo_results['results']['system_status'] = status_results
            
            logger.info("✅ Enhanced Demo completed successfully!")
            return demo_results
            
        except Exception as e:
            logger.error(f"❌ Demo failed: {e}")
            demo_results['error'] = str(e)
            return demo_results
    
    async def _demo_cross_agent_coordination(self) -> Dict[str, Any]:
        """Demonstrate cross-agent coordination capabilities."""
        results = {
            'message_bus_status': {},
            'agent_communication': {},
            'conflict_resolution': {},
            'shared_context': {}
        }
        
        try:
            # Test message bus status
            results['message_bus_status'] = self.message_bus.get_bus_status()
            
            # Test agent communication
            await self.message_bus.broadcast_message(
                sender="demo_coordinator",
                message_type=MessageType.DATA_SHARE,
                content={
                    'data_key': 'demo_data',
                    'data_value': {
                        'message': 'Hello from demo coordinator!',
                        'timestamp': datetime.utcnow().isoformat()
                    }
                },
                priority=MessagePriority.NORMAL
            )
            
            # Test shared context
            self.message_bus.set_shared_context(
                'demo_context',
                {
                    'demo_mode': True,
                    'test_data': 'This is shared context data',
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
            
            shared_context = self.message_bus.get_shared_context('demo_context')
            results['shared_context'] = {
                'context_created': shared_context is not None,
                'context_data': shared_context.data if shared_context else None
            }
            
            # Test conflict resolution
            conflict_data = {
                'conflict_type': 'budget_conflict',
                'conflict_data': {
                    'total_budget': 1000,
                    'requests': [
                        {'agent': 'marketing_strategy', 'amount': 600, 'priority': 2, 'estimated_roi': 0.8},
                        {'agent': 'content_creation', 'amount': 500, 'priority': 1, 'estimated_roi': 0.6}
                    ]
                }
            }
            
            await self.message_bus.send_message(
                sender="demo_coordinator",
                recipients=["conflict_resolver"],
                message_type=MessageType.CONFLICT_ALERT,
                content=conflict_data,
                priority=MessagePriority.HIGH
            )
            
            results['conflict_resolution'] = {
                'conflict_sent': True,
                'conflict_type': 'budget_conflict',
                'resolution_triggered': True
            }
            
            logger.info("✅ Cross-agent coordination demo completed")
            return results
            
        except Exception as e:
            logger.error(f"❌ Cross-agent coordination demo failed: {e}")
            results['error'] = str(e)
            return results
    
    async def _demo_payment_processing(self) -> Dict[str, Any]:
        """Demonstrate payment processing capabilities."""
        results = {
            'customer_creation': {},
            'subscription_management': {},
            'revenue_tracking': {},
            'marketing_funnel': {}
        }
        
        try:
            # Test customer creation
            customer_data = {
                'email': 'demo@autopilotventures.com',
                'name': 'Demo Customer',
                'phone': '+1234567890',
                'metadata': {'demo': True, 'source': 'enhanced_demo'}
            }
            
            customer = await self.payment_processor.create_customer(**customer_data)
            results['customer_creation'] = {
                'success': True,
                'customer_id': customer.id,
                'email': customer.email,
                'name': customer.name
            }
            
            # Test subscription creation
            subscription = await self.payment_processor.create_subscription(
                customer_id=customer.id,
                plan_id='pro_plan',
                metadata={'demo': True}
            )
            
            results['subscription_management'] = {
                'success': True,
                'subscription_id': subscription.id,
                'plan_id': subscription.plan_id,
                'status': subscription.status.value,
                'amount': subscription.amount
            }
            
            # Test revenue tracking
            revenue_data = self.payment_processor.get_monthly_revenue()
            results['revenue_tracking'] = {
                'monthly_revenue': revenue_data['monthly_revenue'],
                'active_subscriptions': revenue_data['active_subscriptions'],
                'currency': revenue_data['currency']
            }
            
            # Test marketing funnel
            await self.marketing_funnel.track_lead(
                email='demo@autopilotventures.com',
                source='enhanced_demo',
                stage='purchase'
            )
            
            funnel_metrics = self.marketing_funnel.get_funnel_metrics()
            results['marketing_funnel'] = {
                'lead_tracked': True,
                'funnel_metrics': funnel_metrics
            }
            
            logger.info("✅ Payment processing demo completed")
            return results
            
        except Exception as e:
            logger.error(f"❌ Payment processing demo failed: {e}")
            results['error'] = str(e)
            return results
    
    async def _demo_cultural_intelligence(self) -> Dict[str, Any]:
        """Demonstrate cultural intelligence capabilities."""
        results = {
            'cultural_profiles': {},
            'market_analysis': {},
            'content_translation': {},
            'cultural_adaptation': {}
        }
        
        try:
            # Test cultural profiles
            supported_countries = ['US', 'CN', 'ES']
            cultural_profiles = {}
            
            for country in supported_countries:
                profile = self.cultural_agent.get_cultural_profile(country)
                if profile:
                    cultural_profiles[country] = {
                        'country_name': profile.country_name,
                        'language': profile.language,
                        'market_maturity': profile.market_maturity.value,
                        'ecommerce_adoption': profile.ecommerce_adoption,
                        'payment_preferences': profile.payment_preferences[:3]  # Top 3
                    }
            
            results['cultural_profiles'] = cultural_profiles
            
            # Test market analysis
            market_opportunity = await self.cultural_agent.research_local_market(
                country_code='US',
                niche='SaaS productivity tools'
            )
            
            results['market_analysis'] = {
                'country_code': market_opportunity.country_code,
                'niche': market_opportunity.niche,
                'market_size': market_opportunity.market_size,
                'competition_level': market_opportunity.competition_level,
                'cultural_fit_score': market_opportunity.cultural_fit_score,
                'success_probability': market_opportunity.success_probability
            }
            
            # Test content translation
            original_content = "Welcome to our amazing productivity platform! Boost your efficiency today."
            translated_content = await self.cultural_agent.translate_content(
                content=original_content,
                target_language='es',
                cultural_context={'formality': 'medium', 'relationship_focus': 'medium'}
            )
            
            results['content_translation'] = {
                'original': original_content,
                'translated': translated_content,
                'target_language': 'es',
                'cultural_context_applied': True
            }
            
            # Test cultural fit analysis
            cultural_fit_analysis = await self.cultural_agent.analyze_cultural_fit(
                product_concept="Personal productivity SaaS with AI assistance",
                target_countries=['US', 'CN', 'ES']
            )
            
            results['cultural_adaptation'] = {
                'product_concept': "Personal productivity SaaS with AI assistance",
                'target_countries': ['US', 'CN', 'ES'],
                'fit_scores': {
                    country: analysis['cultural_fit_score']
                    for country, analysis in cultural_fit_analysis.items()
                },
                'adaptations': {
                    country: analysis['cultural_adaptations']
                    for country, analysis in cultural_fit_analysis.items()
                }
            }
            
            logger.info("✅ Cultural intelligence demo completed")
            return results
            
        except Exception as e:
            logger.error(f"❌ Cultural intelligence demo failed: {e}")
            results['error'] = str(e)
            return results
    
    async def _demo_integrated_workflow(self) -> Dict[str, Any]:
        """Demonstrate integrated workflow with all systems."""
        results = {
            'workflow_execution': {},
            'agent_coordination': {},
            'payment_integration': {},
            'cultural_adaptation': {}
        }
        
        try:
            # Define a realistic workflow configuration
            workflow_config = {
                'niche_research': {
                    'niche': 'AI-powered productivity tools',
                    'market_data': 'Global SaaS market analysis'
                },
                'mvp_design': {
                    'niche': 'AI-powered productivity tools',
                    'target_audience': 'Remote workers and small businesses',
                    'requirements': 'AI assistance, collaboration features, mobile app'
                },
                'marketing_strategy': {
                    'product': 'AI-powered productivity platform',
                    'target_audience': 'Remote workers and small businesses',
                    'budget': 5000.0
                }
            }
            
            # Execute workflow with enhanced coordination
            workflow_result = await self.orchestrator.execute_workflow(workflow_config)
            
            results['workflow_execution'] = {
                'success': workflow_result.success,
                'steps_completed': workflow_result.steps_completed,
                'steps_failed': workflow_result.steps_failed,
                'total_cost': workflow_result.total_cost,
                'execution_time': workflow_result.execution_time
            }
            
            # Test agent coordination during workflow
            results['agent_coordination'] = {
                'message_bus_active': self.message_bus.is_running,
                'shared_context_count': len(self.message_bus.shared_context),
                'registered_agents': len(self.message_bus.registered_agents)
            }
            
            # Test payment integration
            if workflow_result.success:
                # Simulate customer creation after successful workflow
                customer = await self.payment_processor.create_customer(
                    email='workflow_demo@autopilotventures.com',
                    name='Workflow Demo Customer',
                    metadata={'workflow_id': workflow_result.workflow_id}
                )
                
                results['payment_integration'] = {
                    'customer_created': True,
                    'customer_id': customer.id,
                    'workflow_id': workflow_result.workflow_id
                }
            
            # Test cultural adaptation
            cultural_analysis = await self.cultural_agent.analyze_cultural_fit(
                product_concept="AI-powered productivity platform",
                target_countries=['US', 'ES']
            )
            
            results['cultural_adaptation'] = {
                'product_concept': "AI-powered productivity platform",
                'cultural_analysis': cultural_analysis
            }
            
            logger.info("✅ Integrated workflow demo completed")
            return results
            
        except Exception as e:
            logger.error(f"❌ Integrated workflow demo failed: {e}")
            results['error'] = str(e)
            return results
    
    async def _generate_system_status(self) -> Dict[str, Any]:
        """Generate comprehensive system status report."""
        return {
            'orchestrator_status': self.orchestrator.get_workflow_status(),
            'agent_performance': self.orchestrator.get_agent_performance(),
            'message_bus_status': self.message_bus.get_bus_status(),
            'payment_processor_status': {
                'monthly_revenue': self.payment_processor.get_monthly_revenue(),
                'customer_metrics': self.payment_processor.get_customer_metrics()
            },
            'marketing_funnel_status': self.marketing_funnel.get_funnel_metrics(),
            'cultural_agent_status': self.cultural_agent.get_agent_status(),
            'budget_status': {
                'remaining_budget': budget_manager.get_remaining_budget(),
                'daily_spent': budget_manager.get_daily_spent()
            }
        }


async def main():
    """Main demo execution function."""
    print("🚀 AutoPilot Ventures Enhanced Demo")
    print("=" * 50)
    
    # Initialize demo
    demo = EnhancedDemo()
    
    # Run comprehensive demo
    results = await demo.run_comprehensive_demo()
    
    # Display results
    print("\n📊 Demo Results Summary:")
    print("=" * 50)
    
    if 'error' in results:
        print(f"❌ Demo failed: {results['error']}")
        return
    
    print(f"✅ Systems tested: {len(results['systems_tested'])}")
    for system in results['systems_tested']:
        print(f"   - {system}")
    
    print(f"\n🎯 Key Achievements:")
    print("=" * 30)
    
    # Cross-agent coordination results
    if 'coordination' in results['results']:
        coord = results['results']['coordination']
        print(f"📡 Cross-Agent Coordination:")
        print(f"   - Message bus active: {coord['message_bus_status']['is_running']}")
        print(f"   - Registered agents: {coord['message_bus_status']['registered_agents']}")
        print(f"   - Shared context working: {coord['shared_context']['context_created']}")
    
    # Payment processing results
    if 'payment' in results['results']:
        payment = results['results']['payment']
        print(f"💳 Payment Processing:")
        print(f"   - Customer created: {payment['customer_creation']['success']}")
        print(f"   - Subscription active: {payment['subscription_management']['success']}")
        print(f"   - Monthly revenue tracking: ${payment['revenue_tracking']['monthly_revenue']:.2f}")
    
    # Cultural intelligence results
    if 'cultural' in results['results']:
        cultural = results['results']['cultural']
        print(f"🌍 Cultural Intelligence:")
        print(f"   - Cultural profiles: {len(cultural['cultural_profiles'])} countries")
        print(f"   - Market analysis completed: {cultural['market_analysis']['country_code']}")
        print(f"   - Content translation working: {bool(cultural['content_translation']['translated'])}")
    
    # Integrated workflow results
    if 'workflow' in results['results']:
        workflow = results['results']['workflow']
        print(f"🔄 Integrated Workflow:")
        print(f"   - Workflow success: {workflow['workflow_execution']['success']}")
        print(f"   - Steps completed: {len(workflow['workflow_execution']['steps_completed'])}")
        print(f"   - Total cost: ${workflow['workflow_execution']['total_cost']:.2f}")
    
    print(f"\n🎉 Enhanced Demo Completed Successfully!")
    print(f"📈 Your AutoPilot Ventures platform now has:")
    print(f"   - Real-time agent coordination")
    print(f"   - Automated payment processing")
    print(f"   - Cultural intelligence for global markets")
    print(f"   - Integrated workflow management")
    
    # Save results to file
    with open('enhanced_demo_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to: enhanced_demo_results.json")


if __name__ == "__main__":
    asyncio.run(main()) 
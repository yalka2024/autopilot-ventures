#!/usr/bin/env python3
"""
Comprehensive Agent Testing Script for AutoPilot Ventures
Tests all 10 agents with multilingual support and coordination
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Optional, Any
from pathlib import Path
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AgentTester:
    """Comprehensive agent testing class."""
    
    def __init__(self):
        self.test_results = {}
        self.languages = {
            'en': 'English',
            'es': 'Spanish',
            'zh': 'Chinese',
            'fr': 'French',
            'de': 'German'
        }
        
        self.agent_configs = {
            'niche_research': {
                'en': {'niche': 'AI productivity tools', 'market_data': 'Growing market for AI solutions'},
                'es': {'niche': 'Herramientas de productividad IA', 'market_data': 'Mercado en crecimiento para soluciones IA'},
                'zh': {'niche': 'AI生产力工具', 'market_data': 'AI解决方案市场快速增长'},
                'fr': {'niche': 'Outils de productivité IA', 'market_data': 'Marché en croissance pour les solutions IA'},
                'de': {'niche': 'KI-Produktivitätstools', 'market_data': 'Wachsender Markt für KI-Lösungen'}
            },
            'mvp_design': {
                'en': {'niche': 'AI productivity tools', 'target_audience': 'Remote workers', 'requirements': 'Simple interface'},
                'es': {'niche': 'Herramientas de productividad IA', 'target_audience': 'Trabajadores remotos', 'requirements': 'Interfaz simple'},
                'zh': {'niche': 'AI生产力工具', 'target_audience': '远程工作者', 'requirements': '简单界面'},
                'fr': {'niche': 'Outils de productivité IA', 'target_audience': 'Travailleurs à distance', 'requirements': 'Interface simple'},
                'de': {'niche': 'KI-Produktivitätstools', 'target_audience': 'Remote-Arbeiter', 'requirements': 'Einfache Benutzeroberfläche'}
            },
            'marketing_strategy': {
                'en': {'product': 'AI task management app', 'target_audience': 'Remote workers', 'budget': 1000.0},
                'es': {'product': 'Aplicación de gestión de tareas IA', 'target_audience': 'Trabajadores remotos', 'budget': 1000.0},
                'zh': {'product': 'AI任务管理应用', 'target_audience': '远程工作者', 'budget': 1000.0},
                'fr': {'product': 'Application de gestion de tâches IA', 'target_audience': 'Travailleurs à distance', 'budget': 1000.0},
                'de': {'product': 'KI-Aufgabenverwaltungs-App', 'target_audience': 'Remote-Arbeiter', 'budget': 1000.0}
            },
            'content_creation': {
                'en': {'topic': 'AI productivity benefits', 'audience': 'Remote workers', 'content_type': 'blog post'},
                'es': {'topic': 'Beneficios de productividad IA', 'audience': 'Trabajadores remotos', 'content_type': 'artículo de blog'},
                'zh': {'topic': 'AI生产力优势', 'audience': '远程工作者', 'content_type': '博客文章'},
                'fr': {'topic': 'Avantages de productivité IA', 'audience': 'Travailleurs à distance', 'content_type': 'article de blog'},
                'de': {'topic': 'KI-Produktivitätsvorteile', 'audience': 'Remote-Arbeiter', 'content_type': 'Blogbeitrag'}
            },
            'analytics': {
                'en': {'data': 'User engagement metrics', 'metrics': 'daily active users, session duration'},
                'es': {'data': 'Métricas de engagement de usuarios', 'metrics': 'usuarios activos diarios, duración de sesión'},
                'zh': {'data': '用户参与度指标', 'metrics': '日活跃用户、会话时长'},
                'fr': {'data': 'Métriques d\'engagement utilisateur', 'metrics': 'utilisateurs actifs quotidiens, durée de session'},
                'de': {'data': 'Nutzer-Engagement-Metriken', 'metrics': 'tägliche aktive Nutzer, Sitzungsdauer'}
            }
        }

    async def test_single_agent(self, agent_type: str, language: str = 'en') -> Dict:
        """Test a single agent with specific language configuration."""
        logger.info(f"Testing {agent_type} agent in {language}")
        
        try:
            # Import agent classes
            from agents import (
                NicheResearchAgent, MVPDesignAgent, MarketingStrategyAgent,
                ContentCreationAgent, AnalyticsAgent, OperationsMonetizationAgent,
                FundingInvestorAgent, LegalComplianceAgent, HRTeamBuildingAgent,
                CustomerSupportScalingAgent
            )
            from utils import generate_id
            
            # Agent class mapping
            agent_classes = {
                'niche_research': NicheResearchAgent,
                'mvp_design': MVPDesignAgent,
                'marketing_strategy': MarketingStrategyAgent,
                'content_creation': ContentCreationAgent,
                'analytics': AnalyticsAgent,
                'operations_monetization': OperationsMonetizationAgent,
                'funding_investor': FundingInvestorAgent,
                'legal_compliance': LegalComplianceAgent,
                'hr_team_building': HRTeamBuildingAgent,
                'customer_support_scaling': CustomerSupportScalingAgent
            }
            
            if agent_type not in agent_classes:
                return {'success': False, 'error': f'Unknown agent type: {agent_type}'}
            
            # Create test startup ID
            startup_id = generate_id('test_startup')
            
            # Initialize agent
            agent_class = agent_classes[agent_type]
            agent = agent_class(startup_id)
            
            # Get test parameters for this agent and language
            test_params = self.agent_configs.get(agent_type, {}).get(language, {})
            
            # Add default parameters if not in config
            if not test_params:
                test_params = self._get_default_params(agent_type, language)
            
            # Execute agent
            start_time = time.time()
            result = await agent.execute(**test_params)
            execution_time = time.time() - start_time
            
            return {
                'success': result.success,
                'data': result.data,
                'message': result.message,
                'cost': result.cost,
                'execution_time': execution_time,
                'language': language,
                'agent_type': agent_type
            }
            
        except Exception as e:
            logger.error(f"Error testing {agent_type} agent in {language}: {e}")
            return {
                'success': False, 
                'error': str(e),
                'language': language,
                'agent_type': agent_type
            }

    def _get_default_params(self, agent_type: str, language: str) -> Dict:
        """Get default parameters for agents not in the config."""
        defaults = {
            'operations_monetization': {
                'current_operations': 'Freemium SaaS model',
                'revenue_data': 'Monthly recurring revenue of $50,000'
            },
            'funding_investor': {
                'startup_info': 'AI productivity platform with 10,000 users',
                'funding_stage': 'Series A',
                'target_amount': 500000.0
            },
            'legal_compliance': {
                'document_type': 'Terms of Service',
                'content': 'AI-powered productivity platform terms',
                'jurisdiction': 'US'
            },
            'hr_team_building': {
                'company_info': 'AI productivity startup',
                'hiring_needs': 'Software engineers and product managers',
                'team_size': 15
            },
            'customer_support_scaling': {
                'customer_queries': 'Technical support and feature requests',
                'current_scale': '1000 customers',
                'language': language
            }
        }
        return defaults.get(agent_type, {})

    async def test_all_agents_multilingual(self) -> Dict:
        """Test all agents in multiple languages."""
        logger.info("Starting comprehensive multilingual agent testing...")
        
        results = {
            'total_tests': 0,
            'successful_tests': 0,
            'failed_tests': 0,
            'total_cost': 0.0,
            'total_time': 0.0,
            'results_by_agent': {},
            'results_by_language': {},
            'detailed_results': {}
        }
        
        # Test all agents in English first
        for agent_type in self.agent_configs.keys():
            logger.info(f"Testing {agent_type} agent in English...")
            result = await self.test_single_agent(agent_type, 'en')
            
            results['total_tests'] += 1
            if result['success']:
                results['successful_tests'] += 1
                results['total_cost'] += result.get('cost', 0.0)
                results['total_time'] += result.get('execution_time', 0.0)
            else:
                results['failed_tests'] += 1
            
            # Store results
            if agent_type not in results['results_by_agent']:
                results['results_by_agent'][agent_type] = []
            results['results_by_agent'][agent_type].append(result)
            
            results['detailed_results'][f'{agent_type}_en'] = result
        
        # Test first 3 agents in other languages
        for language in ['es', 'zh', 'fr', 'de']:
            for agent_type in list(self.agent_configs.keys())[:3]:
                logger.info(f"Testing {agent_type} agent in {language}...")
                result = await self.test_single_agent(agent_type, language)
                
                results['total_tests'] += 1
                if result['success']:
                    results['successful_tests'] += 1
                    results['total_cost'] += result.get('cost', 0.0)
                    results['total_time'] += result.get('execution_time', 0.0)
                else:
                    results['failed_tests'] += 1
                
                # Store results
                if agent_type not in results['results_by_agent']:
                    results['results_by_agent'][agent_type] = []
                results['results_by_agent'][agent_type].append(result)
                
                if language not in results['results_by_language']:
                    results['results_by_language'][language] = []
                results['results_by_language'][language].append(result)
                
                results['detailed_results'][f'{agent_type}_{language}'] = result
        
        return results

    async def test_agent_coordination(self) -> Dict:
        """Test agent coordination and communication."""
        logger.info("Testing agent coordination...")
        
        try:
            from meta_agent_coordinator import MetaAgentCoordinator
            import redis
            
            # Try to connect to Redis
            try:
                redis_client = redis.Redis(host='localhost', port=6379, db=0)
                redis_client.ping()
                redis_available = True
            except:
                redis_available = False
                logger.warning("Redis not available, skipping coordination tests")
            
            if redis_available:
                coordinator = MetaAgentCoordinator(redis_client)
                
                # Test coordination summary
                summary = await coordinator.get_coordination_summary()
                
                return {
                    'success': True,
                    'coordinator_summary': summary,
                    'redis_available': True
                }
            else:
                return {
                    'success': True,
                    'message': 'Coordination tests skipped (Redis not available)',
                    'redis_available': False
                }
                
        except Exception as e:
            logger.error(f"Error testing agent coordination: {e}")
            return {'success': False, 'error': str(e)}

    def generate_test_report(self, results: Dict) -> str:
        """Generate a comprehensive test report."""
        report = []
        report.append("=" * 60)
        report.append("🤖 AUTOPILOT VENTURES AGENT TEST REPORT")
        report.append("=" * 60)
        report.append("")
        
        # Summary
        report.append("📊 TEST SUMMARY")
        report.append("-" * 30)
        report.append(f"Total Tests: {results['total_tests']}")
        report.append(f"Successful: {results['successful_tests']}")
        report.append(f"Failed: {results['failed_tests']}")
        report.append(f"Success Rate: {(results['successful_tests']/results['total_tests']*100):.1f}%")
        report.append(f"Total Cost: ${results['total_cost']:.4f}")
        report.append(f"Total Time: {results['total_time']:.2f}s")
        report.append("")
        
        # Results by Agent
        report.append("🤖 RESULTS BY AGENT")
        report.append("-" * 30)
        for agent_type, agent_results in results['results_by_agent'].items():
            successful = sum(1 for r in agent_results if r['success'])
            total = len(agent_results)
            success_rate = (successful / total * 100) if total > 0 else 0
            report.append(f"{agent_type.replace('_', ' ').title()}: {successful}/{total} ({success_rate:.1f}%)")
        report.append("")
        
        # Results by Language
        report.append("🌍 RESULTS BY LANGUAGE")
        report.append("-" * 30)
        for language, lang_results in results['results_by_language'].items():
            successful = sum(1 for r in lang_results if r['success'])
            total = len(lang_results)
            success_rate = (successful / total * 100) if total > 0 else 0
            lang_name = self.languages.get(language, language)
            report.append(f"{lang_name} ({language}): {successful}/{total} ({success_rate:.1f}%)")
        report.append("")
        
        # Detailed Results
        report.append("📋 DETAILED RESULTS")
        report.append("-" * 30)
        for test_name, result in results['detailed_results'].items():
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            cost = result.get('cost', 0.0)
            time = result.get('execution_time', 0.0)
            report.append(f"{test_name}: {status} (${cost:.4f}, {time:.2f}s)")
        
        return "\n".join(report)

async def main():
    """Main testing function."""
    print("🤖 AutoPilot Ventures Agent Testing")
    print("=" * 50)
    
    tester = AgentTester()
    
    # Test all agents
    print("Testing all agents with multilingual support...")
    results = await tester.test_all_agents_multilingual()
    
    # Test coordination
    print("Testing agent coordination...")
    coordination_results = await tester.test_agent_coordination()
    results['coordination'] = coordination_results
    
    # Generate and print report
    report = tester.generate_test_report(results)
    print("\n" + report)
    
    # Save results to file
    with open('agent_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Detailed results saved to: agent_test_results.json")
    
    # Summary
    success_rate = (results['successful_tests'] / results['total_tests'] * 100) if results['total_tests'] > 0 else 0
    print(f"\n🎯 Overall Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("🎉 Excellent! All agents are working properly.")
    elif success_rate >= 60:
        print("✅ Good! Most agents are working, some issues to address.")
    else:
        print("⚠️  Issues detected. Check the detailed results for problems.")

if __name__ == "__main__":
    asyncio.run(main()) 
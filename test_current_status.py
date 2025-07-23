#!/usr/bin/env python3
"""
End-to-End Income Generation Validation Script
Tests complete business creation workflow using all 10 agents
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import random

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class BusinessValidation:
    """Business validation result."""
    business_id: str
    language: str
    niche: str
    agents_executed: List[str]
    success_rate: float
    total_cost: float
    estimated_revenue: float
    market_fit_score: float
    compliance_status: str
    timestamp: datetime

@dataclass
class AgentExecutionResult:
    """Individual agent execution result."""
    agent_type: str
    success: bool
    execution_time: float
    cost: float
    data: Dict[str, Any]
    confidence: float
    language: str

class EndToEndIncomeValidator:
    """Comprehensive end-to-end income generation validator."""
    
    def __init__(self):
        self.test_businesses = {
            'fr': {
                'name': 'Plateforme SaaS de Productivité IA',
                'description': 'Solution SaaS française pour la productivité d\'équipe avec IA',
                'niche': 'Productivité SaaS',
                'target_audience': 'PME françaises',
                'expected_revenue': 3000.0  # €3K/month
            },
            'hi': {
                'name': 'AI उत्पादकता SaaS प्लेटफॉर्म',
                'description': 'भारतीय कंपनियों के लिए AI-संचालित उत्पादकता समाधान',
                'niche': 'SaaS उत्पादकता',
                'target_audience': 'भारतीय स्टार्टअप',
                'expected_revenue': 2500.0  # ₹2.5K/month
            }
        }
        
        self.agent_workflow = [
            'niche_research',
            'mvp_design', 
            'marketing_strategy',
            'content_creation',
            'analytics',
            'operations_monetization',
            'funding_investor',
            'legal_compliance',
            'hr_team_building',
            'customer_support_scaling'
        ]

    async def validate_complete_business_creation(self, language: str) -> BusinessValidation:
        """Validate complete business creation workflow for a language."""
        logger.info(f"Starting complete business validation for {language}")
        
        start_time = time.time()
        business_config = self.test_businesses[language]
        business_id = f"business_{language}_{int(time.time())}"
        
        # Execute all 10 agents in sequence
        agent_results = []
        total_cost = 0.0
        successful_agents = 0
        
        for agent_type in self.agent_workflow:
            logger.info(f"Executing {agent_type} agent for {language}")
            
            try:
                result = await self._execute_agent(agent_type, language, business_config)
                agent_results.append(result)
                
                if result.success:
                    successful_agents += 1
                    total_cost += result.cost
                
                # Add delay between agents to simulate real workflow
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Agent {agent_type} failed: {e}")
                agent_results.append(AgentExecutionResult(
                    agent_type=agent_type,
                    success=False,
                    execution_time=0.0,
                    cost=0.0,
                    data={'error': str(e)},
                    confidence=0.0,
                    language=language
                ))
        
        # Calculate metrics
        execution_time = time.time() - start_time
        success_rate = successful_agents / len(self.agent_workflow)
        
        # Estimate revenue based on agent performance
        estimated_revenue = self._estimate_revenue(agent_results, business_config['expected_revenue'])
        
        # Calculate market fit score
        market_fit_score = self._calculate_market_fit(agent_results)
        
        # Check compliance status
        compliance_status = self._check_compliance(agent_results, language)
        
        validation = BusinessValidation(
            business_id=business_id,
            language=language,
            niche=business_config['niche'],
            agents_executed=[r.agent_type for r in agent_results if r.success],
            success_rate=success_rate,
            total_cost=total_cost,
            estimated_revenue=estimated_revenue,
            market_fit_score=market_fit_score,
            compliance_status=compliance_status,
            timestamp=datetime.utcnow()
        )
        
        logger.info(f"Business validation completed for {language}: {success_rate*100:.1f}% success rate")
        return validation

    async def _execute_agent(self, agent_type: str, language: str, business_config: Dict) -> AgentExecutionResult:
        """Execute a single agent with business context."""
        start_time = time.time()
        
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
            
            # Create startup ID
            startup_id = generate_id('test_startup')
            
            # Initialize agent
            agent_class = agent_classes[agent_type]
            agent = agent_class(startup_id)
            
            # Prepare parameters based on agent type and language
            params = self._prepare_agent_params(agent_type, language, business_config)
            
            # Execute agent
            result = await agent.execute(**params)
            
            execution_time = time.time() - start_time
            
            return AgentExecutionResult(
                agent_type=agent_type,
                success=result.success,
                execution_time=execution_time,
                cost=result.cost,
                data=result.data,
                confidence=self._calculate_confidence(result),
                language=language
            )
            
        except Exception as e:
            logger.error(f"Error executing {agent_type}: {e}")
            execution_time = time.time() - start_time
            
            return AgentExecutionResult(
                agent_type=agent_type,
                success=False,
                execution_time=execution_time,
                cost=0.0,
                data={'error': str(e)},
                confidence=0.0,
                language=language
            )

    def _prepare_agent_params(self, agent_type: str, language: str, business_config: Dict) -> Dict[str, Any]:
        """Prepare parameters for agent execution based on language and business config."""
        base_params = {
            'niche_research': {
                'niche': business_config['niche'],
                'market_data': f"Growing market for {business_config['niche']} in {language}"
            },
            'mvp_design': {
                'niche': business_config['niche'],
                'target_audience': business_config['target_audience'],
                'requirements': f"Localized SaaS solution for {language} market"
            },
            'marketing_strategy': {
                'product': business_config['name'],
                'target_audience': business_config['target_audience'],
                'budget': 2000.0
            },
            'content_creation': {
                'topic': f"Benefits of {business_config['niche']}",
                'audience': business_config['target_audience'],
                'content_type': 'blog post',
                'tone': 'professional'
            },
            'analytics': {
                'data': f"Market data for {business_config['niche']} in {language}",
                'metrics': 'user engagement, conversion rates, market size',
                'questions': f"What drives adoption in {language} market?"
            },
            'operations_monetization': {
                'current_operations': 'SaaS subscription model',
                'revenue_data': f"Target: {business_config['expected_revenue']} per month"
            },
            'funding_investor': {
                'startup_info': business_config['description'],
                'funding_stage': 'Seed',
                'target_amount': 50000.0
            },
            'legal_compliance': {
                'document_type': 'Terms of Service',
                'content': business_config['description'],
                'jurisdiction': self._get_jurisdiction(language)
            },
            'hr_team_building': {
                'company_info': business_config['description'],
                'hiring_needs': 'Software engineers and sales team',
                'team_size': 8
            },
            'customer_support_scaling': {
                'customer_queries': 'Technical support and onboarding',
                'current_scale': '100 customers',
                'language': language
            }
        }
        
        return base_params.get(agent_type, {})

    def _get_jurisdiction(self, language: str) -> str:
        """Get jurisdiction for language."""
        jurisdiction_map = {
            'fr': 'FR',
            'hi': 'IN',
            'en': 'US',
            'es': 'ES',
            'zh': 'CN'
        }
        return jurisdiction_map.get(language, 'US')

    def _calculate_confidence(self, result) -> float:
        """Calculate confidence score for agent result."""
        try:
            # Base confidence on success and data quality
            if not result.success:
                return 0.0
            
            # Check data completeness
            data = result.data or {}
            required_fields = ['timestamp', 'data']
            completeness = sum(1 for field in required_fields if field in data) / len(required_fields)
            
            # Confidence based on completeness and success
            confidence = 0.7 + (completeness * 0.3)
            return min(confidence, 1.0)
            
        except Exception:
            return 0.5

    def _estimate_revenue(self, agent_results: List[AgentExecutionResult], target_revenue: float) -> float:
        """Estimate revenue based on agent performance."""
        try:
            # Calculate success rate
            successful_agents = sum(1 for r in agent_results if r.success)
            success_rate = successful_agents / len(agent_results)
            
            # Calculate average confidence
            avg_confidence = sum(r.confidence for r in agent_results) / len(agent_results)
            
            # Revenue estimation formula
            # Higher success rate and confidence = higher revenue potential
            revenue_multiplier = (success_rate * 0.6) + (avg_confidence * 0.4)
            estimated_revenue = target_revenue * revenue_multiplier
            
            return estimated_revenue
            
        except Exception:
            return target_revenue * 0.5

    def _calculate_market_fit(self, agent_results: List[AgentExecutionResult]) -> float:
        """Calculate market fit score based on agent results."""
        try:
            # Weight different agents for market fit
            market_fit_weights = {
                'niche_research': 0.25,
                'marketing_strategy': 0.20,
                'analytics': 0.20,
                'operations_monetization': 0.15,
                'customer_support_scaling': 0.10,
                'mvp_design': 0.10
            }
            
            total_score = 0.0
            total_weight = 0.0
            
            for result in agent_results:
                weight = market_fit_weights.get(result.agent_type, 0.05)
                score = result.confidence if result.success else 0.0
                
                total_score += score * weight
                total_weight += weight
            
            market_fit_score = total_score / total_weight if total_weight > 0 else 0.0
            return market_fit_score
            
        except Exception:
            return 0.5

    def _check_compliance(self, agent_results: List[AgentExecutionResult], language: str) -> str:
        """Check compliance status based on agent results."""
        try:
            # Check legal compliance agent
            legal_result = next((r for r in agent_results if r.agent_type == 'legal_compliance'), None)
            
            if legal_result and legal_result.success:
                return 'compliant'
            elif legal_result and not legal_result.success:
                return 'non_compliant'
            else:
                return 'unknown'
                
        except Exception:
            return 'unknown'

    async def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run comprehensive validation for all test businesses."""
        logger.info("Starting comprehensive end-to-end validation...")
        
        validation_results = {
            'timestamp': datetime.utcnow().isoformat(),
            'businesses': {},
            'summary': {},
            'recommendations': []
        }
        
        # Validate French business
        logger.info("Validating French SaaS business...")
        fr_validation = await self.validate_complete_business_creation('fr')
        validation_results['businesses']['french'] = fr_validation
        
        # Validate Hindi business
        logger.info("Validating Hindi SaaS business...")
        hi_validation = await self.validate_complete_business_creation('hi')
        validation_results['businesses']['hindi'] = hi_validation
        
        # Generate summary
        validation_results['summary'] = self._generate_validation_summary(validation_results['businesses'])
        
        # Generate recommendations
        validation_results['recommendations'] = self._generate_recommendations(validation_results['businesses'])
        
        return validation_results

    def _generate_validation_summary(self, businesses: Dict[str, BusinessValidation]) -> Dict[str, Any]:
        """Generate validation summary."""
        total_businesses = len(businesses)
        avg_success_rate = sum(b.success_rate for b in businesses.values()) / total_businesses
        avg_revenue = sum(b.estimated_revenue for b in businesses.values()) / total_businesses
        avg_market_fit = sum(b.market_fit_score for b in businesses.values()) / total_businesses
        total_cost = sum(b.total_cost for b in businesses.values())
        
        return {
            'total_businesses': total_businesses,
            'average_success_rate': avg_success_rate,
            'average_estimated_revenue': avg_revenue,
            'average_market_fit_score': avg_market_fit,
            'total_agent_cost': total_cost,
            'roi_estimate': (avg_revenue - total_cost) / total_cost if total_cost > 0 else 0,
            'overall_status': 'success' if avg_success_rate >= 0.7 else 'needs_improvement'
        }

    def _generate_recommendations(self, businesses: Dict[str, BusinessValidation]) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []
        
        for lang, business in businesses.items():
            if business.success_rate < 0.8:
                recommendations.append(f"Improve agent success rate for {lang} business (current: {business.success_rate*100:.1f}%)")
            
            if business.market_fit_score < 0.7:
                recommendations.append(f"Enhance market fit for {lang} business (current: {business.market_fit_score*100:.1f}%)")
            
            if business.compliance_status == 'non_compliant':
                recommendations.append(f"Address compliance issues for {lang} business")
            
            if business.estimated_revenue < business.test_businesses[lang]['expected_revenue'] * 0.8:
                recommendations.append(f"Optimize revenue potential for {lang} business")
        
        # Add general recommendations
        recommendations.append("Implement A/B testing for different market approaches")
        recommendations.append("Add more granular market validation")
        recommendations.append("Consider expanding to additional languages")
        
        return recommendations

    def print_validation_report(self, validation_results: Dict[str, Any]):
        """Print comprehensive validation report."""
        print("\n" + "="*80)
        print("🎯 END-TO-END INCOME GENERATION VALIDATION REPORT")
        print("="*80)
        
        # Summary
        summary = validation_results['summary']
        print(f"\n📊 OVERALL SUMMARY:")
        print(f"   Total Businesses: {summary['total_businesses']}")
        print(f"   Average Success Rate: {summary['average_success_rate']*100:.1f}%")
        print(f"   Average Estimated Revenue: ${summary['average_estimated_revenue']:,.2f}/month")
        print(f"   Average Market Fit Score: {summary['average_market_fit_score']*100:.1f}%")
        print(f"   Total Agent Cost: ${summary['total_agent_cost']:.2f}")
        print(f"   ROI Estimate: {summary['roi_estimate']*100:.1f}%")
        print(f"   Overall Status: {summary['overall_status'].upper()}")
        
        # Individual business results
        print(f"\n🏢 BUSINESS RESULTS:")
        for lang, business in validation_results['businesses'].items():
            print(f"\n   {lang.upper()} Business:")
            print(f"     Success Rate: {business.success_rate*100:.1f}%")
            print(f"     Estimated Revenue: ${business.estimated_revenue:,.2f}/month")
            print(f"     Market Fit Score: {business.market_fit_score*100:.1f}%")
            print(f"     Compliance Status: {business.compliance_status}")
            print(f"     Agents Executed: {len(business.agents_executed)}/10")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        for i, rec in enumerate(validation_results['recommendations'], 1):
            print(f"   {i}. {rec}")
        
        print("\n" + "="*80)


async def main():
    """Main validation function."""
    print("🎯 AutoPilot Ventures End-to-End Income Generation Validation")
    print("="*60)
    
    validator = EndToEndIncomeValidator()
    
    # Run comprehensive validation
    validation_results = await validator.run_comprehensive_validation()
    
    # Print report
    validator.print_validation_report(validation_results)
    
    # Save results
    with open('validation_results.json', 'w', encoding='utf-8') as f:
        json.dump(validation_results, f, indent=2, default=str, ensure_ascii=False)
    
    print(f"\n📄 Detailed results saved to: validation_results.json")
    
    # Return success/failure based on overall status
    summary = validation_results['summary']
    if summary['overall_status'] == 'success':
        print("🎉 Validation successful! Platform ready for income generation.")
        return True
    else:
        print("⚠️  Validation completed with issues. Review recommendations.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1) 
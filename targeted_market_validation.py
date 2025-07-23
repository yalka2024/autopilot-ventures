#!/usr/bin/env python3
"""
Targeted Market Validation System
Validates market fit for business ideas across multiple languages and regions
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
class MarketValidationResult:
    """Market validation result."""
    business_id: str
    language: str
    region: str
    market_size: float
    competition_level: str
    customer_interest: float
    pricing_acceptance: float
    market_fit_score: float
    validation_methods: List[str]
    recommendations: List[str]
    timestamp: datetime

@dataclass
class ValidationMethod:
    """Validation method configuration."""
    name: str
    weight: float
    description: str
    success_criteria: Dict[str, Any]

class TargetedMarketValidator:
    """Targeted market validation system."""
    
    def __init__(self):
        self.validation_methods = {
            'competitor_analysis': ValidationMethod(
                name='Competitor Analysis',
                weight=0.25,
                description='Analyze existing competitors and market saturation',
                success_criteria={'competition_level': 'low', 'market_gap': True}
            ),
            'customer_surveys': ValidationMethod(
                name='Customer Surveys',
                weight=0.30,
                description='Direct customer feedback and interest measurement',
                success_criteria={'interest_score': 0.7, 'willingness_to_pay': 0.6}
            ),
            'market_size_analysis': ValidationMethod(
                name='Market Size Analysis',
                weight=0.20,
                description='Total addressable market and growth potential',
                success_criteria={'market_size': 1000000, 'growth_rate': 0.15}
            ),
            'pricing_validation': ValidationMethod(
                name='Pricing Validation',
                weight=0.15,
                description='Price sensitivity and willingness to pay',
                success_criteria={'price_acceptance': 0.7, 'value_perception': 0.8}
            ),
            'trend_analysis': ValidationMethod(
                name='Trend Analysis',
                weight=0.10,
                description='Market trends and timing validation',
                success_criteria={'trend_direction': 'positive', 'timing': 'optimal'}
            )
        }
        
        self.test_markets = {
            'fr': {
                'region': 'France',
                'market_size': 5000000,
                'competition_level': 'medium',
                'growth_rate': 0.12,
                'pricing_sensitivity': 0.6
            },
            'hi': {
                'region': 'India',
                'market_size': 15000000,
                'competition_level': 'high',
                'growth_rate': 0.25,
                'pricing_sensitivity': 0.8
            },
            'es': {
                'region': 'Spain',
                'market_size': 3000000,
                'competition_level': 'low',
                'growth_rate': 0.18,
                'pricing_sensitivity': 0.5
            },
            'de': {
                'region': 'Germany',
                'market_size': 8000000,
                'competition_level': 'medium',
                'growth_rate': 0.10,
                'pricing_sensitivity': 0.4
            },
            'ja': {
                'region': 'Japan',
                'market_size': 12000000,
                'competition_level': 'high',
                'growth_rate': 0.08,
                'pricing_sensitivity': 0.3
            }
        }

    async def validate_market_fit(self, business_config: Dict[str, Any], language: str) -> MarketValidationResult:
        """Validate market fit for a specific business in a language/region."""
        logger.info(f"Starting market validation for {language} market")
        
        market_data = self.test_markets.get(language, {})
        business_id = f"market_validation_{language}_{int(time.time())}"
        
        # Run all validation methods
        validation_results = {}
        total_score = 0.0
        total_weight = 0.0
        
        for method_name, method in self.validation_methods.items():
            logger.info(f"Running {method.name} for {language}")
            
            try:
                result = await self._run_validation_method(method_name, business_config, language, market_data)
                validation_results[method_name] = result
                
                # Calculate weighted score
                method_score = self._calculate_method_score(result, method.success_criteria)
                total_score += method_score * method.weight
                total_weight += method.weight
                
            except Exception as e:
                logger.error(f"Validation method {method_name} failed: {e}")
                validation_results[method_name] = {'error': str(e), 'score': 0.0}
        
        # Calculate overall market fit score
        market_fit_score = total_score / total_weight if total_weight > 0 else 0.0
        
        # Generate recommendations
        recommendations = self._generate_market_recommendations(validation_results, language, market_data)
        
        # Create validation result
        validation_result = MarketValidationResult(
            business_id=business_id,
            language=language,
            region=market_data.get('region', 'Unknown'),
            market_size=market_data.get('market_size', 0),
            competition_level=market_data.get('competition_level', 'unknown'),
            customer_interest=self._extract_customer_interest(validation_results),
            pricing_acceptance=self._extract_pricing_acceptance(validation_results),
            market_fit_score=market_fit_score,
            validation_methods=list(validation_results.keys()),
            recommendations=recommendations,
            timestamp=datetime.utcnow()
        )
        
        logger.info(f"Market validation completed for {language}: {market_fit_score*100:.1f}% fit score")
        return validation_result

    async def _run_validation_method(self, method_name: str, business_config: Dict, language: str, market_data: Dict) -> Dict[str, Any]:
        """Run a specific validation method."""
        if method_name == 'competitor_analysis':
            return await self._analyze_competitors(business_config, language, market_data)
        elif method_name == 'customer_surveys':
            return await self._conduct_customer_surveys(business_config, language, market_data)
        elif method_name == 'market_size_analysis':
            return await self._analyze_market_size(business_config, language, market_data)
        elif method_name == 'pricing_validation':
            return await self._validate_pricing(business_config, language, market_data)
        elif method_name == 'trend_analysis':
            return await self._analyze_trends(business_config, language, market_data)
        else:
            raise ValueError(f"Unknown validation method: {method_name}")

    async def _analyze_competitors(self, business_config: Dict, language: str, market_data: Dict) -> Dict[str, Any]:
        """Analyze competitors in the market."""
        try:
            # Simulate competitor analysis
            competition_level = market_data.get('competition_level', 'medium')
            
            # Generate competitor data
            competitors = []
            if competition_level == 'high':
                competitors = [
                    {'name': f'Competitor A ({language})', 'market_share': 0.25, 'strengths': ['brand', 'features']},
                    {'name': f'Competitor B ({language})', 'market_share': 0.20, 'strengths': ['pricing', 'support']},
                    {'name': f'Competitor C ({language})', 'market_share': 0.15, 'strengths': ['innovation', 'user_experience']}
                ]
            elif competition_level == 'medium':
                competitors = [
                    {'name': f'Competitor A ({language})', 'market_share': 0.30, 'strengths': ['brand']},
                    {'name': f'Competitor B ({language})', 'market_share': 0.20, 'strengths': ['pricing']}
                ]
            else:  # low
                competitors = [
                    {'name': f'Competitor A ({language})', 'market_share': 0.40, 'strengths': ['first_mover']}
                ]
            
            # Calculate market gaps
            total_share = sum(c['market_share'] for c in competitors)
            available_market = 1.0 - total_share
            
            # Identify opportunities
            opportunities = []
            if available_market > 0.3:
                opportunities.append('large_market_gap')
            if any(c['market_share'] > 0.4 for c in competitors):
                opportunities.append('dominant_player_vulnerability')
            if competition_level == 'low':
                opportunities.append('first_mover_advantage')
            
            return {
                'competition_level': competition_level,
                'competitors': competitors,
                'available_market': available_market,
                'opportunities': opportunities,
                'market_gap': available_market > 0.2,
                'score': 1.0 if available_market > 0.3 else 0.5
            }
            
        except Exception as e:
            logger.error(f"Competitor analysis failed: {e}")
            return {'error': str(e), 'score': 0.0}

    async def _conduct_customer_surveys(self, business_config: Dict, language: str, market_data: Dict) -> Dict[str, Any]:
        """Conduct customer surveys to validate interest."""
        try:
            # Simulate customer survey results
            survey_size = 100
            interest_responses = []
            pricing_responses = []
            
            # Generate realistic survey responses based on market characteristics
            base_interest = 0.6 if market_data.get('competition_level') == 'low' else 0.4
            pricing_sensitivity = market_data.get('pricing_sensitivity', 0.5)
            
            for _ in range(survey_size):
                # Interest level (0-1)
                interest = max(0, min(1, base_interest + random.normalvariate(0, 0.2)))
                interest_responses.append(interest)
                
                # Willingness to pay (0-1)
                willingness = max(0, min(1, (1 - pricing_sensitivity) + random.normalvariate(0, 0.15)))
                pricing_responses.append(willingness)
            
            avg_interest = sum(interest_responses) / len(interest_responses)
            avg_willingness = sum(pricing_responses) / len(pricing_responses)
            
            # Calculate confidence intervals
            interest_std = (sum((x - avg_interest) ** 2 for x in interest_responses) / len(interest_responses)) ** 0.5
            willingness_std = (sum((x - avg_willingness) ** 2 for x in pricing_responses) / len(pricing_responses)) ** 0.5
            
            return {
                'survey_size': survey_size,
                'interest_score': avg_interest,
                'interest_confidence': 1.96 * interest_std / (survey_size ** 0.5),  # 95% CI
                'willingness_to_pay': avg_willingness,
                'willingness_confidence': 1.96 * willingness_std / (survey_size ** 0.5),
                'responses': {
                    'high_interest': sum(1 for x in interest_responses if x > 0.7),
                    'medium_interest': sum(1 for x in interest_responses if 0.4 <= x <= 0.7),
                    'low_interest': sum(1 for x in interest_responses if x < 0.4)
                },
                'score': (avg_interest * 0.6) + (avg_willingness * 0.4)
            }
            
        except Exception as e:
            logger.error(f"Customer survey failed: {e}")
            return {'error': str(e), 'score': 0.0}

    async def _analyze_market_size(self, business_config: Dict, language: str, market_data: Dict) -> Dict[str, Any]:
        """Analyze market size and growth potential."""
        try:
            market_size = market_data.get('market_size', 1000000)
            growth_rate = market_data.get('growth_rate', 0.10)
            
            # Calculate addressable market
            target_audience_percentage = 0.15  # Assume 15% of market is addressable
            addressable_market = market_size * target_audience_percentage
            
            # Project growth
            projected_market_1y = addressable_market * (1 + growth_rate)
            projected_market_3y = addressable_market * ((1 + growth_rate) ** 3)
            
            # Market size categories
            if addressable_market > 5000000:
                size_category = 'very_large'
                size_score = 1.0
            elif addressable_market > 1000000:
                size_category = 'large'
                size_score = 0.8
            elif addressable_market > 500000:
                size_category = 'medium'
                size_score = 0.6
            else:
                size_category = 'small'
                size_score = 0.4
            
            return {
                'total_market_size': market_size,
                'addressable_market': addressable_market,
                'growth_rate': growth_rate,
                'projected_market_1y': projected_market_1y,
                'projected_market_3y': projected_market_3y,
                'size_category': size_category,
                'growth_potential': 'high' if growth_rate > 0.15 else 'medium' if growth_rate > 0.08 else 'low',
                'score': size_score * (1 + min(growth_rate, 0.3))
            }
            
        except Exception as e:
            logger.error(f"Market size analysis failed: {e}")
            return {'error': str(e), 'score': 0.0}

    async def _validate_pricing(self, business_config: Dict, language: str, market_data: Dict) -> Dict[str, Any]:
        """Validate pricing strategy and customer willingness to pay."""
        try:
            # Simulate pricing validation
            base_price = 50.0  # Base monthly price
            pricing_sensitivity = market_data.get('pricing_sensitivity', 0.5)
            
            # Test different price points
            price_points = [base_price * 0.5, base_price, base_price * 1.5, base_price * 2.0]
            acceptance_rates = []
            
            for price in price_points:
                # Calculate acceptance rate based on pricing sensitivity
                base_acceptance = 1.0 - (pricing_sensitivity * (price / base_price - 1))
                acceptance_rate = max(0.1, min(0.9, base_acceptance + random.normalvariate(0, 0.1)))
                acceptance_rates.append(acceptance_rate)
            
            # Find optimal price point
            optimal_index = acceptance_rates.index(max(acceptance_rates))
            optimal_price = price_points[optimal_index]
            optimal_acceptance = acceptance_rates[optimal_index]
            
            # Calculate value perception
            value_perception = optimal_acceptance * (1 - pricing_sensitivity)
            
            return {
                'tested_prices': price_points,
                'acceptance_rates': acceptance_rates,
                'optimal_price': optimal_price,
                'optimal_acceptance': optimal_acceptance,
                'price_acceptance': optimal_acceptance,
                'value_perception': value_perception,
                'pricing_strategy': 'premium' if optimal_price > base_price * 1.2 else 'competitive' if optimal_price > base_price * 0.8 else 'budget',
                'score': (optimal_acceptance * 0.6) + (value_perception * 0.4)
            }
            
        except Exception as e:
            logger.error(f"Pricing validation failed: {e}")
            return {'error': str(e), 'score': 0.0}

    async def _analyze_trends(self, business_config: Dict, language: str, market_data: Dict) -> Dict[str, Any]:
        """Analyze market trends and timing."""
        try:
            # Simulate trend analysis
            current_trends = [
                'ai_adoption_increasing',
                'remote_work_growth',
                'digital_transformation',
                'sustainability_focus'
            ]
            
            # Calculate trend alignment
            business_keywords = business_config.get('niche', '').lower()
            trend_alignment = 0.0
            
            if 'ai' in business_keywords or 'intelligence' in business_keywords:
                trend_alignment += 0.3
            if 'productivity' in business_keywords or 'efficiency' in business_keywords:
                trend_alignment += 0.25
            if 'saas' in business_keywords or 'software' in business_keywords:
                trend_alignment += 0.25
            if 'remote' in business_keywords or 'digital' in business_keywords:
                trend_alignment += 0.2
            
            # Determine timing
            if trend_alignment > 0.7:
                timing = 'optimal'
                timing_score = 1.0
            elif trend_alignment > 0.4:
                timing = 'good'
                timing_score = 0.7
            else:
                timing = 'poor'
                timing_score = 0.3
            
            # Market maturity
            competition_level = market_data.get('competition_level', 'medium')
            if competition_level == 'low':
                maturity = 'early_stage'
                maturity_score = 0.9
            elif competition_level == 'medium':
                maturity = 'growth_stage'
                maturity_score = 0.7
            else:
                maturity = 'mature'
                maturity_score = 0.4
            
            return {
                'current_trends': current_trends,
                'trend_alignment': trend_alignment,
                'trend_direction': 'positive' if trend_alignment > 0.5 else 'neutral',
                'timing': timing,
                'market_maturity': maturity,
                'recommended_entry': 'immediate' if timing == 'optimal' and maturity == 'early_stage' else 'planned',
                'score': (timing_score * 0.6) + (maturity_score * 0.4)
            }
            
        except Exception as e:
            logger.error(f"Trend analysis failed: {e}")
            return {'error': str(e), 'score': 0.0}

    def _calculate_method_score(self, result: Dict[str, Any], success_criteria: Dict[str, Any]) -> float:
        """Calculate score for a validation method based on success criteria."""
        try:
            if 'error' in result:
                return 0.0
            
            # Use the score if provided
            if 'score' in result:
                return result['score']
            
            # Calculate score based on criteria
            score = 0.0
            criteria_met = 0
            total_criteria = len(success_criteria)
            
            for criterion, target_value in success_criteria.items():
                if criterion in result:
                    actual_value = result[criterion]
                    
                    if isinstance(target_value, (int, float)):
                        if isinstance(actual_value, (int, float)):
                            if actual_value >= target_value:
                                criteria_met += 1
                    elif isinstance(target_value, str):
                        if actual_value == target_value:
                            criteria_met += 1
                    elif isinstance(target_value, bool):
                        if actual_value == target_value:
                            criteria_met += 1
            
            score = criteria_met / total_criteria if total_criteria > 0 else 0.0
            return score
            
        except Exception:
            return 0.0

    def _extract_customer_interest(self, validation_results: Dict[str, Any]) -> float:
        """Extract customer interest from validation results."""
        try:
            survey_result = validation_results.get('customer_surveys', {})
            return survey_result.get('interest_score', 0.0)
        except Exception:
            return 0.0

    def _extract_pricing_acceptance(self, validation_results: Dict[str, Any]) -> float:
        """Extract pricing acceptance from validation results."""
        try:
            pricing_result = validation_results.get('pricing_validation', {})
            return pricing_result.get('price_acceptance', 0.0)
        except Exception:
            return 0.0

    def _generate_market_recommendations(self, validation_results: Dict[str, Any], language: str, market_data: Dict) -> List[str]:
        """Generate market-specific recommendations."""
        recommendations = []
        
        # Analyze competitor results
        competitor_result = validation_results.get('competitor_analysis', {})
        if competitor_result.get('available_market', 0) < 0.2:
            recommendations.append(f"Market is highly saturated in {language}. Consider niche positioning.")
        
        # Analyze customer survey results
        survey_result = validation_results.get('customer_surveys', {})
        if survey_result.get('interest_score', 0) < 0.5:
            recommendations.append(f"Low customer interest in {language} market. Reconsider value proposition.")
        
        # Analyze market size
        size_result = validation_results.get('market_size_analysis', {})
        if size_result.get('addressable_market', 0) < 500000:
            recommendations.append(f"Small addressable market in {language}. Consider expanding target audience.")
        
        # Analyze pricing
        pricing_result = validation_results.get('pricing_validation', {})
        if pricing_result.get('price_acceptance', 0) < 0.6:
            recommendations.append(f"Low price acceptance in {language} market. Consider pricing strategy adjustment.")
        
        # Analyze trends
        trend_result = validation_results.get('trend_analysis', {})
        if trend_result.get('timing') == 'poor':
            recommendations.append(f"Poor market timing in {language}. Consider delaying launch or pivoting.")
        
        # Add positive recommendations
        if competitor_result.get('available_market', 0) > 0.4:
            recommendations.append(f"Large market gap in {language}. Excellent opportunity for market entry.")
        
        if survey_result.get('interest_score', 0) > 0.7:
            recommendations.append(f"High customer interest in {language} market. Strong validation for launch.")
        
        return recommendations

    async def run_comprehensive_market_validation(self) -> Dict[str, Any]:
        """Run comprehensive market validation for all test markets."""
        logger.info("Starting comprehensive market validation...")
        
        validation_results = {
            'timestamp': datetime.utcnow().isoformat(),
            'markets': {},
            'summary': {},
            'recommendations': []
        }
        
        # Test business configuration
        test_business = {
            'name': 'AI Productivity SaaS Platform',
            'niche': 'AI-powered productivity tools',
            'target_audience': 'Small and medium businesses',
            'pricing_model': 'subscription',
            'base_price': 50.0
        }
        
        # Validate each market
        for language in self.test_markets.keys():
            logger.info(f"Validating market for {language}")
            market_validation = await self.validate_market_fit(test_business, language)
            validation_results['markets'][language] = market_validation
        
        # Generate summary
        validation_results['summary'] = self._generate_validation_summary(validation_results['markets'])
        
        # Generate global recommendations
        validation_results['recommendations'] = self._generate_global_recommendations(validation_results['markets'])
        
        return validation_results

    def _generate_validation_summary(self, markets: Dict[str, MarketValidationResult]) -> Dict[str, Any]:
        """Generate validation summary across all markets."""
        total_markets = len(markets)
        avg_market_fit = sum(m.market_fit_score for m in markets.values()) / total_markets
        avg_customer_interest = sum(m.customer_interest for m in markets.values()) / total_markets
        avg_pricing_acceptance = sum(m.pricing_acceptance for m in markets.values()) / total_markets
        
        # Find best markets
        sorted_markets = sorted(markets.items(), key=lambda x: x[1].market_fit_score, reverse=True)
        best_markets = [lang for lang, _ in sorted_markets[:3]]
        
        return {
            'total_markets': total_markets,
            'average_market_fit': avg_market_fit,
            'average_customer_interest': avg_customer_interest,
            'average_pricing_acceptance': avg_pricing_acceptance,
            'best_markets': best_markets,
            'overall_opportunity': 'high' if avg_market_fit > 0.7 else 'medium' if avg_market_fit > 0.5 else 'low'
        }

    def _generate_global_recommendations(self, markets: Dict[str, MarketValidationResult]) -> List[str]:
        """Generate global recommendations based on all market validations."""
        recommendations = []
        
        # Find best performing markets
        best_markets = sorted(markets.items(), key=lambda x: x[1].market_fit_score, reverse=True)
        
        if best_markets:
            best_lang, best_market = best_markets[0]
            recommendations.append(f"Focus on {best_market.region} ({best_lang}) as primary market with {best_market.market_fit_score*100:.1f}% fit score")
        
        # Identify patterns
        high_interest_markets = [lang for lang, market in markets.items() if market.customer_interest > 0.7]
        if len(high_interest_markets) > 2:
            recommendations.append(f"High customer interest across multiple markets: {', '.join(high_interest_markets)}")
        
        low_competition_markets = [lang for lang, market in markets.items() if market.competition_level == 'low']
        if low_competition_markets:
            recommendations.append(f"Low competition opportunities in: {', '.join(low_competition_markets)}")
        
        # Pricing strategy recommendations
        avg_pricing = sum(m.pricing_acceptance for m in markets.values()) / len(markets)
        if avg_pricing < 0.6:
            recommendations.append("Consider global pricing strategy adjustment due to low acceptance rates")
        
        return recommendations

    def print_validation_report(self, validation_results: Dict[str, Any]):
        """Print comprehensive market validation report."""
        print("\n" + "="*80)
        print("🎯 TARGETED MARKET VALIDATION REPORT")
        print("="*80)
        
        # Summary
        summary = validation_results['summary']
        print(f"\n📊 OVERALL SUMMARY:")
        print(f"   Total Markets: {summary['total_markets']}")
        print(f"   Average Market Fit: {summary['average_market_fit']*100:.1f}%")
        print(f"   Average Customer Interest: {summary['average_customer_interest']*100:.1f}%")
        print(f"   Average Pricing Acceptance: {summary['average_pricing_acceptance']*100:.1f}%")
        print(f"   Best Markets: {', '.join(summary['best_markets'])}")
        print(f"   Overall Opportunity: {summary['overall_opportunity'].upper()}")
        
        # Individual market results
        print(f"\n🌍 MARKET RESULTS:")
        for lang, market in validation_results['markets'].items():
            print(f"\n   {lang.upper()} ({market.region}):")
            print(f"     Market Fit Score: {market.market_fit_score*100:.1f}%")
            print(f"     Customer Interest: {market.customer_interest*100:.1f}%")
            print(f"     Pricing Acceptance: {market.pricing_acceptance*100:.1f}%")
            print(f"     Market Size: {market.market_size:,}")
            print(f"     Competition Level: {market.competition_level}")
            print(f"     Validation Methods: {len(market.validation_methods)}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        for i, rec in enumerate(validation_results['recommendations'], 1):
            print(f"   {i}. {rec}")
        
        print("\n" + "="*80)


async def main():
    """Main validation function."""
    print("🎯 AutoPilot Ventures Targeted Market Validation")
    print("="*50)
    
    validator = TargetedMarketValidator()
    
    # Run comprehensive validation
    validation_results = await validator.run_comprehensive_market_validation()
    
    # Print report
    validator.print_validation_report(validation_results)
    
    # Save results
    with open('market_validation_results.json', 'w', encoding='utf-8') as f:
        json.dump(validation_results, f, indent=2, default=str, ensure_ascii=False)
    
    print(f"\n📄 Detailed results saved to: market_validation_results.json")
    
    # Return success/failure based on overall opportunity
    summary = validation_results['summary']
    if summary['overall_opportunity'] in ['high', 'medium']:
        print("🎉 Market validation successful! Strong opportunities identified.")
        return True
    else:
        print("⚠️  Market validation completed with limited opportunities.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1) 
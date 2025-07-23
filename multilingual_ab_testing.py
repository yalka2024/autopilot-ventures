#!/usr/bin/env python3
"""
Multilingual A/B Testing System
Tests different strategies across multiple languages and regions
"""

import asyncio
import json
import logging
import random
import statistics
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import numpy as np
from scipy import stats
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestType(Enum):
    """Types of A/B tests"""
    PRICING = "pricing"
    FEATURE = "feature"
    MESSAGING = "messaging"
    UI_UX = "ui_ux"
    PAYMENT_METHOD = "payment_method"
    ONBOARDING = "onboarding"

class Language(Enum):
    """Supported languages for testing"""
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    PORTUGUESE = "pt"
    ITALIAN = "it"
    JAPANESE = "ja"
    CHINESE = "zh"
    ARABIC = "ar"
    HINDI = "hi"

@dataclass
class ABTestVariant:
    """A/B test variant configuration"""
    name: str
    description: str
    parameters: Dict[str, Any]
    traffic_percentage: float
    is_control: bool = False

@dataclass
class ABTestResult:
    """Results for a single variant"""
    variant_name: str
    conversion_rate: float
    revenue_per_user: float
    user_satisfaction: float
    sample_size: int
    confidence_interval: Tuple[float, float]
    p_value: float
    is_significant: bool

@dataclass
class ABTest:
    """Complete A/B test configuration"""
    test_id: str
    name: str
    description: str
    test_type: TestType
    language: Language
    variants: List[ABTestVariant]
    start_date: datetime
    end_date: datetime
    target_sample_size: int
    confidence_level: float
    metrics: List[str]
    status: str = "active"

class MultilingualABTesting:
    """Multilingual A/B testing system"""
    
    def __init__(self):
        self.active_tests: Dict[str, ABTest] = {}
        self.test_results: Dict[str, Dict[str, ABTestResult]] = {}
        self.user_assignments: Dict[str, Dict[str, str]] = {}  # user_id -> test_id -> variant
        self.test_data: Dict[str, List[Dict]] = {}
        
    async def create_test(self, test_config: ABTest) -> str:
        """Create a new A/B test"""
        try:
            # Validate test configuration
            if not test_config.variants:
                raise ValueError("At least one variant is required")
            
            if sum(v.traffic_percentage for v in test_config.variants) != 100:
                raise ValueError("Traffic percentages must sum to 100")
            
            # Initialize test data structures
            self.active_tests[test_config.test_id] = test_config
            self.test_results[test_config.test_id] = {}
            self.user_assignments[test_config.test_id] = {}
            self.test_data[test_config.test_id] = []
            
            logger.info(f"Created A/B test: {test_config.name} ({test_config.test_id})")
            return test_config.test_id
            
        except Exception as e:
            logger.error(f"Error creating A/B test: {e}")
            raise
    
    async def assign_user_to_variant(self, user_id: str, test_id: str) -> str:
        """Assign a user to a test variant"""
        try:
            if test_id not in self.active_tests:
                raise ValueError(f"Test {test_id} not found")
            
            test = self.active_tests[test_id]
            
            # Check if user is already assigned
            if user_id in self.user_assignments[test_id]:
                return self.user_assignments[test_id][user_id]
            
            # Assign user based on traffic percentages
            rand = random.random() * 100
            cumulative = 0
            
            for variant in test.variants:
                cumulative += variant.traffic_percentage
                if rand <= cumulative:
                    self.user_assignments[test_id][user_id] = variant.name
                    logger.info(f"Assigned user {user_id} to variant {variant.name} in test {test_id}")
                    return variant.name
            
            # Fallback to first variant
            variant_name = test.variants[0].name
            self.user_assignments[test_id][user_id] = variant_name
            return variant_name
            
        except Exception as e:
            logger.error(f"Error assigning user to variant: {e}")
            raise
    
    async def record_event(self, test_id: str, user_id: str, event_type: str, 
                          value: float = 1.0, metadata: Dict = None) -> None:
        """Record an event for A/B test analysis"""
        try:
            if test_id not in self.active_tests:
                return
            
            variant = self.user_assignments.get(test_id, {}).get(user_id)
            if not variant:
                return
            
            event_data = {
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id,
                "variant": variant,
                "event_type": event_type,
                "value": value,
                "metadata": metadata or {}
            }
            
            self.test_data[test_id].append(event_data)
            logger.debug(f"Recorded event: {event_type} for user {user_id} in variant {variant}")
            
        except Exception as e:
            logger.error(f"Error recording event: {e}")
    
    async def calculate_variant_metrics(self, test_id: str, variant_name: str) -> ABTestResult:
        """Calculate metrics for a specific variant"""
        try:
            test = self.active_tests[test_id]
            variant_data = [d for d in self.test_data[test_id] if d["variant"] == variant_name]
            
            if not variant_data:
                return None
            
            # Calculate basic metrics
            total_users = len(set(d["user_id"] for d in variant_data))
            conversions = len([d for d in variant_data if d["event_type"] == "conversion"])
            conversion_rate = conversions / total_users if total_users > 0 else 0
            
            # Calculate revenue per user
            revenue_events = [d for d in variant_data if d["event_type"] == "purchase"]
            total_revenue = sum(d["value"] for d in revenue_events)
            revenue_per_user = total_revenue / total_users if total_users > 0 else 0
            
            # Calculate user satisfaction (from feedback events)
            satisfaction_events = [d for d in variant_data if d["event_type"] == "feedback"]
            user_satisfaction = statistics.mean([d["value"] for d in satisfaction_events]) if satisfaction_events else 0
            
            # Calculate confidence interval using Wilson score interval
            confidence_interval = self._wilson_score_interval(conversions, total_users, test.confidence_level)
            
            # Calculate p-value (simplified)
            p_value = self._calculate_p_value(test_id, variant_name)
            
            result = ABTestResult(
                variant_name=variant_name,
                conversion_rate=conversion_rate,
                revenue_per_user=revenue_per_user,
                user_satisfaction=user_satisfaction,
                sample_size=total_users,
                confidence_interval=confidence_interval,
                p_value=p_value,
                is_significant=p_value < (1 - test.confidence_level)
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating variant metrics: {e}")
            raise
    
    def _wilson_score_interval(self, successes: int, total: int, confidence: float) -> Tuple[float, float]:
        """Calculate Wilson score confidence interval"""
        if total == 0:
            return (0, 0)
        
        p_hat = successes / total
        z = stats.norm.ppf((1 + confidence) / 2)
        
        denominator = 1 + z**2 / total
        centre_adjusted_probability = (p_hat + z * z / (2 * total)) / denominator
        adjusted_standard_error = z * np.sqrt((p_hat * (1 - p_hat) + z * z / (4 * total)) / total) / denominator
        
        lower_bound = centre_adjusted_probability - adjusted_standard_error
        upper_bound = centre_adjusted_probability + adjusted_standard_error
        
        return (max(0, lower_bound), min(1, upper_bound))
    
    def _calculate_p_value(self, test_id: str, variant_name: str) -> float:
        """Calculate p-value for statistical significance"""
        try:
            test = self.active_tests[test_id]
            control_variant = next((v for v in test.variants if v.is_control), test.variants[0])
            
            if variant_name == control_variant.name:
                return 1.0
            
            # Get control and test variant data
            control_data = [d for d in self.test_data[test_id] if d["variant"] == control_variant.name]
            test_data = [d for d in self.test_data[test_id] if d["variant"] == variant_name]
            
            if not control_data or not test_data:
                return 1.0
            
            # Calculate conversion rates
            control_conversions = len([d for d in control_data if d["event_type"] == "conversion"])
            control_total = len(set(d["user_id"] for d in control_data))
            control_rate = control_conversions / control_total if control_total > 0 else 0
            
            test_conversions = len([d for d in test_data if d["event_type"] == "conversion"])
            test_total = len(set(d["user_id"] for d in test_data))
            test_rate = test_conversions / test_total if test_total > 0 else 0
            
            # Perform chi-square test
            contingency_table = np.array([
                [control_conversions, control_total - control_conversions],
                [test_conversions, test_total - test_conversions]
            ])
            
            chi2, p_value, _, _ = stats.chi2_contingency(contingency_table)
            return p_value
            
        except Exception as e:
            logger.error(f"Error calculating p-value: {e}")
            return 1.0
    
    async def analyze_test(self, test_id: str) -> Dict[str, Any]:
        """Analyze complete A/B test results"""
        try:
            if test_id not in self.active_tests:
                raise ValueError(f"Test {test_id} not found")
            
            test = self.active_tests[test_id]
            results = {}
            
            # Calculate metrics for each variant
            for variant in test.variants:
                result = await self.calculate_variant_metrics(test_id, variant.name)
                if result:
                    results[variant.name] = result
            
            # Find winner
            winner = None
            best_metric = 0
            
            for variant_name, result in results.items():
                if result.conversion_rate > best_metric:
                    best_metric = result.conversion_rate
                    winner = variant_name
            
            analysis = {
                "test_id": test_id,
                "test_name": test.name,
                "language": test.language.value,
                "test_type": test.test_type.value,
                "status": test.status,
                "start_date": test.start_date.isoformat(),
                "end_date": test.end_date.isoformat(),
                "total_users": sum(r.sample_size for r in results.values()),
                "results": {name: asdict(result) for name, result in results.items()},
                "winner": winner,
                "recommendations": self._generate_recommendations(results, test),
                "analysis_timestamp": datetime.now().isoformat()
            }
            
            self.test_results[test_id] = results
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing test: {e}")
            raise
    
    def _generate_recommendations(self, results: Dict[str, ABTestResult], test: ABTest) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        if not results:
            return ["Insufficient data for analysis"]
        
        # Check statistical significance
        significant_variants = [name for name, result in results.items() if result.is_significant]
        
        if significant_variants:
            recommendations.append(f"Found {len(significant_variants)} statistically significant variants")
        
        # Check sample size
        total_users = sum(r.sample_size for r in results.values())
        if total_users < test.target_sample_size:
            recommendations.append(f"Continue test to reach target sample size of {test.target_sample_size}")
        
        # Check conversion rates
        conversion_rates = [(name, result.conversion_rate) for name, result in results.items()]
        conversion_rates.sort(key=lambda x: x[1], reverse=True)
        
        best_variant = conversion_rates[0]
        worst_variant = conversion_rates[-1]
        
        if best_variant[1] > worst_variant[1] * 1.2:  # 20% improvement
            recommendations.append(f"Consider implementing {best_variant[0]} variant")
        
        return recommendations
    
    async def create_multilingual_test_suite(self) -> List[str]:
        """Create a comprehensive multilingual test suite"""
        test_ids = []
        
        # Pricing test across languages
        pricing_variants = [
            ABTestVariant("control", "Standard pricing", {"price": 29.99}, 33.33, True),
            ABTestVariant("premium", "Premium pricing", {"price": 39.99}, 33.33),
            ABTestVariant("discount", "Discount pricing", {"price": 19.99}, 33.34)
        ]
        
        for language in Language:
            test = ABTest(
                test_id=f"pricing_{language.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                name=f"Pricing Optimization - {language.value.upper()}",
                description=f"Test different pricing strategies for {language.value} market",
                test_type=TestType.PRICING,
                language=language,
                variants=pricing_variants,
                start_date=datetime.now(),
                end_date=datetime.now() + timedelta(days=30),
                target_sample_size=1000,
                confidence_level=0.95,
                metrics=["conversion_rate", "revenue_per_user", "user_satisfaction"]
            )
            
            test_id = await self.create_test(test)
            test_ids.append(test_id)
        
        # Feature test for onboarding
        onboarding_variants = [
            ABTestVariant("control", "Standard onboarding", {"steps": 5, "video": False}, 50, True),
            ABTestVariant("simplified", "Simplified onboarding", {"steps": 3, "video": True}, 50)
        ]
        
        for language in [Language.ENGLISH, Language.SPANISH, Language.FRENCH]:
            test = ABTest(
                test_id=f"onboarding_{language.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                name=f"Onboarding Optimization - {language.value.upper()}",
                description=f"Test simplified onboarding for {language.value} users",
                test_type=TestType.ONBOARDING,
                language=language,
                variants=onboarding_variants,
                start_date=datetime.now(),
                end_date=datetime.now() + timedelta(days=21),
                target_sample_size=500,
                confidence_level=0.95,
                metrics=["completion_rate", "time_to_complete", "user_satisfaction"]
            )
            
            test_id = await self.create_test(test)
            test_ids.append(test_id)
        
        logger.info(f"Created {len(test_ids)} multilingual test suites")
        return test_ids
    
    async def simulate_test_data(self, test_id: str, num_users: int = 100) -> None:
        """Simulate test data for development and testing"""
        try:
            if test_id not in self.active_tests:
                raise ValueError(f"Test {test_id} not found")
            
            test = self.active_tests[test_id]
            
            for i in range(num_users):
                user_id = f"user_{test_id}_{i}"
                
                # Assign user to variant
                variant_name = await self.assign_user_to_variant(user_id, test_id)
                
                # Simulate user behavior
                await self.record_event(test_id, user_id, "page_view", 1.0)
                
                # Simulate conversion with different rates per variant
                variant = next(v for v in test.variants if v.name == variant_name)
                conversion_prob = 0.05 if variant.is_control else 0.08  # 8% for test variants
                
                if random.random() < conversion_prob:
                    await self.record_event(test_id, user_id, "conversion", 1.0)
                    
                    # Simulate purchase
                    if random.random() < 0.7:  # 70% of conversions purchase
                        purchase_amount = random.uniform(20, 50)
                        await self.record_event(test_id, user_id, "purchase", purchase_amount)
                
                # Simulate feedback
                if random.random() < 0.3:  # 30% provide feedback
                    satisfaction = random.uniform(3.0, 5.0)
                    await self.record_event(test_id, user_id, "feedback", satisfaction)
            
            logger.info(f"Simulated data for {num_users} users in test {test_id}")
            
        except Exception as e:
            logger.error(f"Error simulating test data: {e}")
            raise
    
    async def export_results(self, test_id: str, format: str = "json") -> str:
        """Export test results in specified format"""
        try:
            analysis = await self.analyze_test(test_id)
            
            if format.lower() == "json":
                return json.dumps(analysis, indent=2, default=str)
            elif format.lower() == "csv":
                # Convert to CSV format
                csv_data = []
                for variant_name, result in analysis["results"].items():
                    row = {
                        "test_id": test_id,
                        "variant": variant_name,
                        "conversion_rate": result["conversion_rate"],
                        "revenue_per_user": result["revenue_per_user"],
                        "sample_size": result["sample_size"],
                        "is_significant": result["is_significant"]
                    }
                    csv_data.append(row)
                
                df = pd.DataFrame(csv_data)
                return df.to_csv(index=False)
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        except Exception as e:
            logger.error(f"Error exporting results: {e}")
            raise

async def main():
    """Main function to demonstrate multilingual A/B testing"""
    ab_testing = MultilingualABTesting()
    
    # Create multilingual test suite
    test_ids = await ab_testing.create_multilingual_test_suite()
    
    # Simulate data for first test
    if test_ids:
        await ab_testing.simulate_test_data(test_ids[0], num_users=200)
        
        # Analyze results
        analysis = await ab_testing.analyze_test(test_ids[0])
        print(f"Test Analysis: {json.dumps(analysis, indent=2, default=str)}")
        
        # Export results
        json_results = await ab_testing.export_results(test_ids[0], "json")
        print(f"JSON Results: {json_results}")

if __name__ == "__main__":
    asyncio.run(main()) 
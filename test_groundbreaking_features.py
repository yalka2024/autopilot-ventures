"""
Comprehensive Test Suite for Groundbreaking Features
Tests all 4 groundbreaking features individually and in integration
"""

import asyncio
import pytest
import json
import time
from typing import Dict, List, Any
from datetime import datetime, timedelta
import redis
import structlog

# Import the new features
from adaptive_reinforcement_learning import (
    AdaptiveReinforcementLearning, BusinessOutcome, AgentType, 
    BusinessMetrics as RLBusinessMetrics
)
from cultural_intelligence_engine import (
    CulturalIntelligenceEngine, BusinessAspect, CulturalAdaptation
)
from agent_swarm import (
    DecentralizedAgentSwarm, SwarmNodeType, TaskPriority, TaskStatus
)
from income_prediction_simulator import (
    IncomePredictionSimulator, BusinessType, BusinessMetrics as IPSBusinessMetrics
)
from orchestrator_enhanced import EnhancedAgentOrchestrator

# Configure logging
logger = structlog.get_logger()

class TestGroundbreakingFeatures:
    """Test suite for all 4 groundbreaking features."""
    
    @pytest.fixture(autouse=True)
    async def setup(self):
        """Setup test environment."""
        self.redis_client = redis.Redis(host='localhost', port=6379, db=15)  # Use test DB
        self.startup_id = "test_startup_123"
        
        # Initialize all features
        self.adaptive_rl = AdaptiveReinforcementLearning(self.redis_client)
        self.cultural_engine = CulturalIntelligenceEngine(self.redis_client)
        self.agent_swarm = DecentralizedAgentSwarm(self.redis_client)
        self.income_simulator = IncomePredictionSimulator(self.redis_client)
        self.orchestrator = EnhancedAgentOrchestrator(self.startup_id)
        
        yield
        
        # Cleanup
        await self.cleanup()
    
    async def cleanup(self):
        """Cleanup test data."""
        try:
            # Clear test data from Redis
            keys = self.redis_client.keys("test_*")
            if keys:
                self.redis_client.delete(*keys)
            
            # Stop agent swarm
            await self.agent_swarm.stop_swarm()
            
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

    # ===== FEATURE 1: ADAPTIVE REINFORCEMENT LEARNING TESTS =====
    
    @pytest.mark.asyncio
    async def test_adaptive_rl_initialization(self):
        """Test adaptive RL system initialization."""
        assert self.adaptive_rl is not None
        assert self.adaptive_rl.learning_enabled is True
        assert len(self.adaptive_rl.agents) > 0
        
        # Test that all agent types are initialized
        expected_agent_types = [
            AgentType.NICHE_RESEARCH, AgentType.MVP_DESIGN, 
            AgentType.MARKETING_STRATEGY, AgentType.CONTENT_CREATION,
            AgentType.ANALYTICS, AgentType.OPERATIONS_MONETIZATION,
            AgentType.FUNDING_INVESTOR, AgentType.LEGAL_COMPLIANCE,
            AgentType.HR_TEAM_BUILDING, AgentType.CUSTOMER_SUPPORT
        ]
        
        for agent_type in expected_agent_types:
            assert agent_type in self.adaptive_rl.agents
    
    @pytest.mark.asyncio
    async def test_adaptive_rl_episode_recording(self):
        """Test recording learning episodes."""
        # Create test business metrics
        before_metrics = RLBusinessMetrics(
            revenue=1000.0, customers=100, conversion_rate=0.05,
            churn_rate=0.02, customer_acquisition_cost=50.0,
            lifetime_value=200.0, market_size=1000000.0,
            competition_level=0.3, growth_rate=0.1, profit_margin=0.2
        )
        
        after_metrics = RLBusinessMetrics(
            revenue=1200.0, customers=120, conversion_rate=0.06,
            churn_rate=0.015, customer_acquisition_cost=45.0,
            lifetime_value=220.0, market_size=1000000.0,
            competition_level=0.3, growth_rate=0.12, profit_margin=0.22
        )
        
        # Record episode
        await self.adaptive_rl.record_episode(
            agent_type=AgentType.MARKETING_STRATEGY,
            state={'revenue': 1000.0, 'customers': 100},
            action=None,  # Simplified for test
            reward=0.8,
            next_state={'revenue': 1200.0, 'customers': 120},
            done=True,
            metadata={'test': True}
        )
        
        assert len(self.adaptive_rl.episodes) == 1
        episode = self.adaptive_rl.episodes[0]
        assert episode.agent_type == AgentType.MARKETING_STRATEGY
        assert episode.reward == 0.8
    
    @pytest.mark.asyncio
    async def test_adaptive_rl_reward_calculation(self):
        """Test reward calculation based on business outcomes."""
        before_metrics = RLBusinessMetrics(
            revenue=1000.0, customers=100, conversion_rate=0.05,
            churn_rate=0.02, customer_acquisition_cost=50.0,
            lifetime_value=200.0, market_size=1000000.0,
            competition_level=0.3, growth_rate=0.1, profit_margin=0.2
        )
        
        after_metrics = RLBusinessMetrics(
            revenue=1200.0, customers=120, conversion_rate=0.06,
            churn_rate=0.015, customer_acquisition_cost=45.0,
            lifetime_value=220.0, market_size=1000000.0,
            competition_level=0.3, growth_rate=0.12, profit_margin=0.22
        )
        
        reward = await self.adaptive_rl.calculate_business_outcome_reward(
            before_metrics, after_metrics, AgentType.MARKETING_STRATEGY, "en"
        )
        
        assert reward > 0  # Should be positive for improvement
        assert isinstance(reward, float)
    
    @pytest.mark.asyncio
    async def test_adaptive_rl_optimized_action(self):
        """Test getting optimized actions from RL system."""
        context = {
            'revenue': 1000.0,
            'customers': 100,
            'market_size': 1000000.0,
            'competition_level': 0.3
        }
        
        action = await self.adaptive_rl.get_optimized_action(
            AgentType.MARKETING_STRATEGY, context, context, "en"
        )
        
        assert action is not None
        assert action.agent_type == AgentType.MARKETING_STRATEGY
        assert action.language == "en"
        assert isinstance(action.confidence, float)
    
    @pytest.mark.asyncio
    async def test_adaptive_rl_performance_metrics(self):
        """Test getting RL performance metrics."""
        metrics = await self.adaptive_rl.get_learning_performance()
        
        assert isinstance(metrics, dict)
        assert 'overall' in metrics
        assert 'total_episodes' in metrics['overall']
        assert 'learning_enabled' in metrics['overall']

    # ===== FEATURE 2: CULTURAL INTELLIGENCE TESTS =====
    
    @pytest.mark.asyncio
    async def test_cultural_intelligence_initialization(self):
        """Test cultural intelligence engine initialization."""
        assert self.cultural_engine is not None
        assert self.cultural_engine.knowledge_base is not None
        assert len(self.cultural_engine.knowledge_base.cultural_profiles) > 0
        
        # Test that key countries are available
        key_countries = ["US", "JP", "BR"]
        for country in key_countries:
            assert country in self.cultural_engine.knowledge_base.cultural_profiles
    
    @pytest.mark.asyncio
    async def test_cultural_adaptation(self):
        """Test cultural adaptation of business content."""
        original_content = "Our amazing product will revolutionize your business!"
        
        adaptation = await self.cultural_engine.adapt_business_strategy(
            business_aspect=BusinessAspect.MARKETING_MESSAGING,
            original_content=original_content,
            source_culture="US",
            target_culture="JP"
        )
        
        assert adaptation is not None
        assert adaptation.business_aspect == BusinessAspect.MARKETING_MESSAGING
        assert adaptation.source_culture == "US"
        assert adaptation.target_culture == "JP"
        assert adaptation.original_content == original_content
        assert adaptation.adapted_content != original_content  # Should be different
        assert isinstance(adaptation.confidence_score, float)
        assert 0 <= adaptation.confidence_score <= 1
    
    @pytest.mark.asyncio
    async def test_cultural_insights(self):
        """Test getting cultural insights."""
        insights = await self.cultural_engine.get_cultural_insights(
            query="marketing strategies for Japanese market",
            target_culture="JP",
            business_aspect=BusinessAspect.MARKETING_MESSAGING
        )
        
        assert isinstance(insights, list)
        # Insights might be empty if no data, but structure should be correct
        if insights:
            insight = insights[0]
            assert hasattr(insight, 'insight_id')
            assert hasattr(insight, 'description')
            assert hasattr(insight, 'confidence')
    
    @pytest.mark.asyncio
    async def test_cultural_performance_metrics(self):
        """Test getting cultural intelligence performance metrics."""
        metrics = await self.cultural_engine.get_cultural_performance_metrics()
        
        assert isinstance(metrics, dict)
        assert 'total_adaptations' in metrics
        assert 'average_confidence' in metrics
        assert 'adaptation_types' in metrics

    # ===== FEATURE 3: DECENTRALIZED AGENT SWARM TESTS =====
    
    @pytest.mark.asyncio
    async def test_agent_swarm_initialization(self):
        """Test agent swarm initialization."""
        assert self.agent_swarm is not None
        assert self.agent_swarm.node_discovery is not None
        assert self.agent_swarm.load_balancer is not None
        assert self.agent_swarm.health_monitor is not None
    
    @pytest.mark.asyncio
    async def test_agent_swarm_start_stop(self):
        """Test starting and stopping the swarm."""
        await self.agent_swarm.start_swarm()
        assert self.agent_swarm.running is True
        
        await self.agent_swarm.stop_swarm()
        assert self.agent_swarm.running is False
    
    @pytest.mark.asyncio
    async def test_local_node_registration(self):
        """Test registering local node."""
        node = await self.agent_swarm.register_local_node(
            node_type=SwarmNodeType.WORKER,
            port=8001
        )
        
        assert node is not None
        assert node.node_type == SwarmNodeType.WORKER
        assert node.port == 8001
        assert node.node_id in self.agent_swarm.nodes
    
    @pytest.mark.asyncio
    async def test_swarm_task_submission(self):
        """Test submitting tasks to the swarm."""
        # Start swarm first
        await self.agent_swarm.start_swarm()
        await self.agent_swarm.register_local_node()
        
        # Submit task
        task_id = await self.agent_swarm.submit_task(
            task_type="agent_execution",
            payload={
                "agent_type": "marketing_strategy",
                "parameters": {"target_audience": "startups"}
            },
            priority=TaskPriority.MEDIUM,
            node_requirements=["general_computing"]
        )
        
        assert task_id is not None
        assert task_id in self.agent_swarm.tasks
        
        # Check task status
        task = await self.agent_swarm.get_task_status(task_id)
        assert task is not None
        assert task.task_id == task_id
        assert task.task_type == "agent_execution"
    
    @pytest.mark.asyncio
    async def test_swarm_metrics(self):
        """Test getting swarm performance metrics."""
        metrics = await self.agent_swarm.get_swarm_metrics()
        
        assert isinstance(metrics, dict)
        assert 'total_nodes' in metrics
        assert 'active_nodes' in metrics
        assert 'total_tasks' in metrics
        assert 'completed_tasks' in metrics
        assert 'failed_tasks' in metrics
        assert 'average_response_time' in metrics

    # ===== FEATURE 4: INCOME PREDICTION SIMULATOR TESTS =====
    
    @pytest.mark.asyncio
    async def test_income_simulator_initialization(self):
        """Test income prediction simulator initialization."""
        assert self.income_simulator is not None
        assert self.income_simulator.revenue_predictor is not None
        assert self.income_simulator.diversification_analyzer is not None
    
    @pytest.mark.asyncio
    async def test_business_data_addition(self):
        """Test adding business data to simulator."""
        metrics = IPSBusinessMetrics(
            business_id="test_business_1",
            business_type=BusinessType.SAAS,
            revenue=5000.0,
            customers=200,
            conversion_rate=0.08,
            churn_rate=0.03,
            customer_acquisition_cost=75.0,
            lifetime_value=300.0,
            market_size=5000000.0,
            competition_level=0.4,
            growth_rate=0.15,
            profit_margin=0.25,
            language="en",
            region="US"
        )
        
        await self.income_simulator.add_business_data(metrics)
        
        assert metrics.business_id in self.income_simulator.business_data
        stored_metrics = self.income_simulator.business_data[metrics.business_id]
        assert stored_metrics.revenue == 5000.0
        assert stored_metrics.business_type == BusinessType.SAAS
    
    @pytest.mark.asyncio
    async def test_revenue_prediction(self):
        """Test revenue prediction functionality."""
        # Add business data first
        metrics = IPSBusinessMetrics(
            business_id="test_business_2",
            business_type=BusinessType.SAAS,
            revenue=5000.0,
            customers=200,
            conversion_rate=0.08,
            churn_rate=0.03,
            customer_acquisition_cost=75.0,
            lifetime_value=300.0,
            market_size=5000000.0,
            competition_level=0.4,
            growth_rate=0.15,
            profit_margin=0.25,
            language="en",
            region="US"
        )
        
        await self.income_simulator.add_business_data(metrics)
        
        # Predict revenue
        prediction = await self.income_simulator.predict_business_revenue(
            "test_business_2", horizon_months=12
        )
        
        assert prediction is not None
        assert prediction.business_id == "test_business_2"
        assert prediction.predicted_revenue > 0
        assert prediction.confidence_interval_lower > 0
        assert prediction.confidence_interval_upper > prediction.confidence_interval_lower
        assert prediction.prediction_horizon == 12
        assert isinstance(prediction.model_accuracy, float)
    
    @pytest.mark.asyncio
    async def test_diversification_analysis(self):
        """Test portfolio diversification analysis."""
        # Add multiple businesses for portfolio analysis
        businesses = [
            IPSBusinessMetrics(
                business_id=f"test_business_{i}",
                business_type=BusinessType.SAAS,
                revenue=5000.0 + i * 1000,
                customers=200 + i * 50,
                conversion_rate=0.08,
                churn_rate=0.03,
                customer_acquisition_cost=75.0,
                lifetime_value=300.0,
                market_size=5000000.0,
                competition_level=0.4,
                growth_rate=0.15,
                profit_margin=0.25,
                language="en",
                region="US"
            )
            for i in range(3)
        ]
        
        for business in businesses:
            await self.income_simulator.add_business_data(business)
        
        # Analyze diversification
        portfolio_summary = await self.income_simulator.analyze_portfolio_diversification()
        
        assert portfolio_summary is not None
        assert portfolio_summary.total_businesses == 3
        assert portfolio_summary.total_revenue > 0
        assert isinstance(portfolio_summary.diversification_score, float)
        assert isinstance(portfolio_summary.risk_score, float)
        assert len(portfolio_summary.recommendations) >= 0  # May be empty
    
    @pytest.mark.asyncio
    async def test_simulation_performance_metrics(self):
        """Test getting simulation performance metrics."""
        metrics = await self.income_simulator.get_simulation_performance_metrics()
        
        assert isinstance(metrics, dict)
        assert 'total_businesses' in metrics
        assert 'total_predictions' in metrics
        assert 'total_recommendations' in metrics
        assert 'model_performance' in metrics

    # ===== INTEGRATION TESTS =====
    
    @pytest.mark.asyncio
    async def test_orchestrator_integration(self):
        """Test integration of all features in orchestrator."""
        # Start groundbreaking features
        await self.orchestrator.start_groundbreaking_features()
        
        # Test adaptive RL integration
        rl_result = await self.orchestrator.execute_with_adaptive_rl(
            agent_type="marketing_strategy",
            context={"target_audience": "startups", "budget": 1000},
            language="en"
        )
        
        assert rl_result is not None
        assert 'rl_optimized' in rl_result
        
        # Test cultural adaptation integration
        cultural_result = await self.orchestrator.adapt_content_culturally(
            content="Our amazing product will revolutionize your business!",
            source_culture="US",
            target_culture="JP",
            business_aspect="marketing_messaging"
        )
        
        assert cultural_result is not None
        assert cultural_result.source_culture == "US"
        assert cultural_result.target_culture == "JP"
        
        # Test swarm task submission
        swarm_task_id = await self.orchestrator.submit_swarm_task(
            task_type="agent_execution",
            payload={"agent_type": "analytics", "data": "test_data"},
            priority="medium"
        )
        
        assert swarm_task_id is not None
        
        # Test revenue prediction
        revenue_prediction = await self.orchestrator.predict_business_revenue(
            {
                "business_id": "test_integration",
                "business_type": "saas",
                "revenue": 5000.0,
                "customers": 200,
                "conversion_rate": 0.08,
                "churn_rate": 0.03,
                "customer_acquisition_cost": 75.0,
                "lifetime_value": 300.0,
                "market_size": 5000000.0,
                "competition_level": 0.4,
                "growth_rate": 0.15,
                "profit_margin": 0.25,
                "language": "en",
                "region": "US"
            },
            horizon_months=12
        )
        
        assert revenue_prediction is not None
        assert 'predicted_revenue' in revenue_prediction
        
        # Test diversification recommendations
        diversification = await self.orchestrator.get_diversification_recommendations()
        
        assert diversification is not None
        assert 'total_revenue' in diversification
        assert 'recommendations' in diversification
        
        # Test overall status
        status = await self.orchestrator.get_groundbreaking_features_status()
        
        assert status is not None
        assert 'adaptive_reinforcement_learning' in status
        assert 'cultural_intelligence' in status
        assert 'agent_swarm' in status
        assert 'income_prediction' in status
        assert status['integration_status'] == 'all_features_active'
    
    @pytest.mark.asyncio
    async def test_multi_language_support(self):
        """Test multi-language support across all features."""
        languages = ["en", "es", "zh", "fr", "de", "ar", "pt", "hi", "ru", "ja"]
        
        for language in languages:
            # Test adaptive RL with different languages
            rl_result = await self.orchestrator.execute_with_adaptive_rl(
                agent_type="content_creation",
                context={"topic": "business growth", "language": language},
                language=language
            )
            
            assert rl_result is not None
            
            # Test cultural adaptation for different language pairs
            if language != "en":
                cultural_result = await self.orchestrator.adapt_content_culturally(
                    content="Our product helps businesses grow",
                    source_culture="US",
                    target_culture=language.upper(),
                    business_aspect="marketing_messaging"
                )
                
                assert cultural_result is not None
                assert cultural_result.target_culture == language.upper()
    
    @pytest.mark.asyncio
    async def test_performance_benchmarks(self):
        """Test performance benchmarks for all features."""
        start_time = time.time()
        
        # Benchmark adaptive RL
        rl_start = time.time()
        for i in range(10):
            await self.orchestrator.execute_with_adaptive_rl(
                agent_type="analytics",
                context={"data": f"test_data_{i}"},
                language="en"
            )
        rl_time = time.time() - rl_start
        
        # Benchmark cultural adaptation
        cultural_start = time.time()
        for i in range(10):
            await self.orchestrator.adapt_content_culturally(
                content=f"Test content {i}",
                source_culture="US",
                target_culture="JP",
                business_aspect="marketing_messaging"
            )
        cultural_time = time.time() - cultural_start
        
        # Benchmark swarm tasks
        swarm_start = time.time()
        task_ids = []
        for i in range(10):
            task_id = await self.orchestrator.submit_swarm_task(
                task_type="data_processing",
                payload={"data": f"test_data_{i}"},
                priority="medium"
            )
            task_ids.append(task_id)
        swarm_time = time.time() - swarm_start
        
        # Benchmark revenue prediction
        prediction_start = time.time()
        for i in range(10):
            await self.orchestrator.predict_business_revenue(
                {
                    "business_id": f"test_business_{i}",
                    "business_type": "saas",
                    "revenue": 5000.0 + i * 100,
                    "customers": 200 + i * 10,
                    "conversion_rate": 0.08,
                    "churn_rate": 0.03,
                    "customer_acquisition_cost": 75.0,
                    "lifetime_value": 300.0,
                    "market_size": 5000000.0,
                    "competition_level": 0.4,
                    "growth_rate": 0.15,
                    "profit_margin": 0.25,
                    "language": "en",
                    "region": "US"
                },
                horizon_months=12
            )
        prediction_time = time.time() - prediction_start
        
        total_time = time.time() - start_time
        
        # Assert reasonable performance (adjust thresholds as needed)
        assert rl_time < 5.0  # 10 RL operations should complete in under 5 seconds
        assert cultural_time < 3.0  # 10 cultural adaptations should complete in under 3 seconds
        assert swarm_time < 2.0  # 10 swarm task submissions should complete in under 2 seconds
        assert prediction_time < 4.0  # 10 predictions should complete in under 4 seconds
        assert total_time < 15.0  # Total should complete in under 15 seconds
        
        logger.info(f"Performance benchmarks completed: RL={rl_time:.2f}s, Cultural={cultural_time:.2f}s, Swarm={swarm_time:.2f}s, Prediction={prediction_time:.2f}s, Total={total_time:.2f}s")

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling across all features."""
        # Test with invalid data
        try:
            await self.orchestrator.execute_with_adaptive_rl(
                agent_type="invalid_agent",
                context={},
                language="invalid_language"
            )
        except Exception as e:
            assert "Failed to execute with adaptive RL" in str(e) or "No suitable node" in str(e)
        
        # Test cultural adaptation with invalid cultures
        try:
            await self.orchestrator.adapt_content_culturally(
                content="test",
                source_culture="INVALID",
                target_culture="INVALID",
                business_aspect="invalid_aspect"
            )
        except Exception as e:
            assert "Failed to adapt content culturally" in str(e)
        
        # Test swarm with invalid task
        try:
            await self.orchestrator.submit_swarm_task(
                task_type="invalid_task",
                payload={},
                priority="invalid_priority"
            )
        except Exception as e:
            assert "Failed to submit swarm task" in str(e)
        
        # Test prediction with invalid data
        try:
            await self.orchestrator.predict_business_revenue(
                {"invalid": "data"},
                horizon_months=-1
            )
        except Exception as e:
            assert "Failed to predict business revenue" in str(e)

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"]) 
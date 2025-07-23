"""
Self-Optimization System for AutoPilot Ventures
Enables agents to collaboratively learn and optimize across all ventures
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import numpy as np
from collections import defaultdict
import redis
import structlog
from prometheus_client import Counter, Histogram, Gauge

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

class LearningType(Enum):
    SUCCESS_PATTERN = "success_pattern"
    FAILURE_PATTERN = "failure_pattern"
    MARKET_INSIGHT = "market_insight"
    STRATEGY_IMPROVEMENT = "strategy_improvement"
    TECHNOLOGY_OPTIMIZATION = "technology_optimization"
    CUSTOMER_BEHAVIOR = "customer_behavior"
    COMPETITIVE_ANALYSIS = "competitive_analysis"
    FINANCIAL_OPTIMIZATION = "financial_optimization"

class OptimizationLevel(Enum):
    VENTURE_SPECIFIC = "venture_specific"
    NICHE_LEVEL = "niche_level"
    CROSS_NICHE = "cross_niche"
    GLOBAL = "global"

@dataclass
class LearningEvent:
    id: str
    venture_id: str
    agent_type: str
    learning_type: LearningType
    optimization_level: OptimizationLevel
    description: str
    data: Dict[str, Any]
    success_metrics: Dict[str, float]
    timestamp: datetime
    confidence_score: float
    applied_to_ventures: Set[str] = field(default_factory=set)
    validated: bool = False

@dataclass
class OptimizationStrategy:
    id: str
    name: str
    description: str
    learning_events: List[str]
    success_rate: float
    application_count: int
    last_updated: datetime
    active: bool = True

class CollaborativeLearningEngine:
    """Engine for collaborative learning across ventures"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.learning_events = {}
        self.optimization_strategies = {}
        self.venture_performance = defaultdict(dict)
        self.agent_learnings = defaultdict(list)
        
        # Metrics
        self.learning_events_total = Counter('learning_events_total', 'Total learning events', ['type', 'level'])
        self.optimization_applications = Counter('optimization_applications_total', 'Optimization applications', ['strategy_id'])
        self.success_rate_improvement = Gauge('success_rate_improvement', 'Success rate improvement', ['venture_id'])
        self.collaborative_insights = Counter('collaborative_insights_total', 'Collaborative insights generated')
        
        # Learning patterns
        self.success_patterns = defaultdict(list)
        self.failure_patterns = defaultdict(list)
        self.market_insights = defaultdict(list)
        self.strategy_improvements = defaultdict(list)
    
    async def record_learning_event(self, venture_id: str, agent_type: str, 
                                  learning_type: LearningType, description: str,
                                  data: Dict[str, Any], success_metrics: Dict[str, float],
                                  confidence_score: float = 0.8) -> str:
        """Record a learning event from an agent"""
        try:
            learning_id = f"learning_{int(time.time())}_{venture_id}"
            
            # Determine optimization level based on learning type and data
            optimization_level = await self._determine_optimization_level(learning_type, data, venture_id)
            
            learning_event = LearningEvent(
                id=learning_id,
                venture_id=venture_id,
                agent_type=agent_type,
                learning_type=learning_type,
                optimization_level=optimization_level,
                description=description,
                data=data,
                success_metrics=success_metrics,
                timestamp=datetime.utcnow(),
                confidence_score=confidence_score
            )
            
            # Store learning event
            self.learning_events[learning_id] = learning_event
            await self._store_learning_event(learning_event)
            
            # Update agent learnings
            self.agent_learnings[agent_type].append(learning_id)
            
            # Update metrics
            self.learning_events_total.labels(type=learning_type.value, level=optimization_level.value).inc()
            
            # Trigger collaborative analysis
            await self._trigger_collaborative_analysis(learning_event)
            
            logger.info("Learning event recorded", 
                      learning_id=learning_id, venture_id=venture_id, 
                      agent_type=agent_type, learning_type=learning_type.value)
            
            return learning_id
            
        except Exception as e:
            logger.error("Failed to record learning event", error=str(e))
            raise
    
    async def _determine_optimization_level(self, learning_type: LearningType, 
                                          data: Dict[str, Any], venture_id: str) -> OptimizationLevel:
        """Determine the optimization level for a learning event"""
        try:
            # Check if this is venture-specific
            if learning_type in [LearningType.SUCCESS_PATTERN, LearningType.FAILURE_PATTERN]:
                return OptimizationLevel.VENTURE_SPECIFIC
            
            # Check if this applies to the same niche
            niche = data.get('niche', '')
            if niche:
                similar_ventures = await self._find_similar_ventures(niche)
                if len(similar_ventures) > 1:
                    return OptimizationLevel.NICHE_LEVEL
            
            # Check if this is a global insight
            if learning_type in [LearningType.MARKET_INSIGHT, LearningType.TECHNOLOGY_OPTIMIZATION]:
                return OptimizationLevel.GLOBAL
            
            # Default to cross-niche
            return OptimizationLevel.CROSS_NICHE
            
        except Exception as e:
            logger.error("Error determining optimization level", error=str(e))
            return OptimizationLevel.VENTURE_SPECIFIC
    
    async def _find_similar_ventures(self, niche: str) -> List[str]:
        """Find ventures in the same niche"""
        try:
            # This would query the database for similar ventures
            # For now, return empty list
            return []
        except Exception as e:
            logger.error("Error finding similar ventures", error=str(e))
            return []
    
    async def _trigger_collaborative_analysis(self, learning_event: LearningEvent):
        """Trigger collaborative analysis when new learning is recorded"""
        try:
            # Analyze patterns across ventures
            await self._analyze_cross_venture_patterns(learning_event)
            
            # Generate optimization strategies
            await self._generate_optimization_strategies(learning_event)
            
            # Apply learnings to other ventures
            await self._apply_learnings_to_ventures(learning_event)
            
            self.collaborative_insights.inc()
            
        except Exception as e:
            logger.error("Collaborative analysis failed", error=str(e))
    
    async def _analyze_cross_venture_patterns(self, learning_event: LearningEvent):
        """Analyze patterns across multiple ventures"""
        try:
            learning_type = learning_event.learning_type
            
            if learning_type == LearningType.SUCCESS_PATTERN:
                self.success_patterns[learning_event.agent_type].append(learning_event)
            elif learning_type == LearningType.FAILURE_PATTERN:
                self.failure_patterns[learning_event.agent_type].append(learning_event)
            elif learning_type == LearningType.MARKET_INSIGHT:
                self.market_insights[learning_event.agent_type].append(learning_event)
            elif learning_type == LearningType.STRATEGY_IMPROVEMENT:
                self.strategy_improvements[learning_event.agent_type].append(learning_event)
            
            # Analyze patterns
            await self._identify_patterns(learning_type, learning_event.agent_type)
            
        except Exception as e:
            logger.error("Pattern analysis failed", error=str(e))
    
    async def _identify_patterns(self, learning_type: LearningType, agent_type: str):
        """Identify patterns in learning events"""
        try:
            if learning_type == LearningType.SUCCESS_PATTERN:
                patterns = self.success_patterns[agent_type]
            elif learning_type == LearningType.FAILURE_PATTERN:
                patterns = self.failure_patterns[agent_type]
            elif learning_type == LearningType.MARKET_INSIGHT:
                patterns = self.market_insights[agent_type]
            elif learning_type == LearningType.STRATEGY_IMPROVEMENT:
                patterns = self.strategy_improvements[agent_type]
            else:
                return
            
            if len(patterns) >= 3:  # Need at least 3 events to identify patterns
                await self._extract_pattern_insights(patterns, learning_type, agent_type)
                
        except Exception as e:
            logger.error("Pattern identification failed", error=str(e))
    
    async def _extract_pattern_insights(self, patterns: List[LearningEvent], 
                                      learning_type: LearningType, agent_type: str):
        """Extract insights from patterns"""
        try:
            # Analyze common elements
            common_elements = await self._find_common_elements(patterns)
            
            # Calculate success correlation
            success_correlation = await self._calculate_success_correlation(patterns)
            
            # Generate optimization strategy
            if success_correlation > 0.7:  # High correlation threshold
                await self._create_optimization_strategy(patterns, common_elements, success_correlation)
                
        except Exception as e:
            logger.error("Pattern insight extraction failed", error=str(e))
    
    async def _find_common_elements(self, patterns: List[LearningEvent]) -> Dict[str, Any]:
        """Find common elements across learning events"""
        try:
            common_elements = {}
            
            # Analyze data fields
            for field in ['market_size', 'competition_level', 'pricing_strategy', 'marketing_channel']:
                values = [event.data.get(field) for event in patterns if event.data.get(field)]
                if values:
                    common_elements[field] = {
                        'most_common': max(set(values), key=values.count),
                        'frequency': values.count(max(set(values), key=values.count)) / len(values)
                    }
            
            return common_elements
            
        except Exception as e:
            logger.error("Common elements analysis failed", error=str(e))
            return {}
    
    async def _calculate_success_correlation(self, patterns: List[LearningEvent]) -> float:
        """Calculate correlation between patterns and success"""
        try:
            success_rates = [event.success_metrics.get('success_rate', 0) for event in patterns]
            confidence_scores = [event.confidence_score for event in patterns]
            
            if len(success_rates) < 2:
                return 0.0
            
            # Calculate correlation coefficient
            correlation = np.corrcoef(success_rates, confidence_scores)[0, 1]
            return correlation if not np.isnan(correlation) else 0.0
            
        except Exception as e:
            logger.error("Success correlation calculation failed", error=str(e))
            return 0.0
    
    async def _create_optimization_strategy(self, patterns: List[LearningEvent], 
                                          common_elements: Dict[str, Any], 
                                          success_correlation: float):
        """Create an optimization strategy based on patterns"""
        try:
            strategy_id = f"strategy_{int(time.time())}"
            
            # Calculate average success rate
            success_rates = [event.success_metrics.get('success_rate', 0) for event in patterns]
            avg_success_rate = sum(success_rates) / len(success_rates)
            
            strategy = OptimizationStrategy(
                id=strategy_id,
                name=f"Optimization Strategy {strategy_id}",
                description=f"Strategy based on {len(patterns)} learning events with {success_correlation:.2f} correlation",
                learning_events=[event.id for event in patterns],
                success_rate=avg_success_rate,
                application_count=0,
                last_updated=datetime.utcnow()
            )
            
            self.optimization_strategies[strategy_id] = strategy
            await self._store_optimization_strategy(strategy)
            
            logger.info("Optimization strategy created", 
                      strategy_id=strategy_id, success_rate=avg_success_rate,
                      correlation=success_correlation)
            
        except Exception as e:
            logger.error("Strategy creation failed", error=str(e))
    
    async def _apply_learnings_to_ventures(self, learning_event: LearningEvent):
        """Apply learnings to other ventures"""
        try:
            # Find applicable ventures
            applicable_ventures = await self._find_applicable_ventures(learning_event)
            
            for venture_id in applicable_ventures:
                await self._apply_learning_to_venture(learning_event, venture_id)
                
        except Exception as e:
            logger.error("Learning application failed", error=str(e))
    
    async def _find_applicable_ventures(self, learning_event: LearningEvent) -> List[str]:
        """Find ventures where this learning can be applied"""
        try:
            applicable_ventures = []
            
            # Get all ventures (this would query the database)
            all_ventures = await self._get_all_ventures()
            
            for venture_id in all_ventures:
                if venture_id != learning_event.venture_id:
                    # Check if learning is applicable
                    if await self._is_learning_applicable(learning_event, venture_id):
                        applicable_ventures.append(venture_id)
            
            return applicable_ventures
            
        except Exception as e:
            logger.error("Applicable ventures search failed", error=str(e))
            return []
    
    async def _get_all_ventures(self) -> List[str]:
        """Get all venture IDs"""
        try:
            # This would query the database
            # For now, return empty list
            return []
        except Exception as e:
            logger.error("Failed to get all ventures", error=str(e))
            return []
    
    async def _is_learning_applicable(self, learning_event: LearningEvent, venture_id: str) -> bool:
        """Check if learning is applicable to a venture"""
        try:
            # Check optimization level
            if learning_event.optimization_level == OptimizationLevel.GLOBAL:
                return True
            
            # Check niche similarity
            venture_niche = await self._get_venture_niche(venture_id)
            learning_niche = learning_event.data.get('niche', '')
            
            if learning_event.optimization_level == OptimizationLevel.NICHE_LEVEL:
                return venture_niche == learning_niche
            
            # For cross-niche, check if there are similarities
            return await self._check_niche_similarity(venture_niche, learning_niche)
            
        except Exception as e:
            logger.error("Learning applicability check failed", error=str(e))
            return False
    
    async def _get_venture_niche(self, venture_id: str) -> str:
        """Get venture niche"""
        try:
            # This would query the database
            # For now, return empty string
            return ""
        except Exception as e:
            logger.error("Failed to get venture niche", error=str(e))
            return ""
    
    async def _check_niche_similarity(self, niche1: str, niche2: str) -> bool:
        """Check if two niches are similar"""
        try:
            # Simple similarity check
            # In a real implementation, this would use NLP or semantic similarity
            return niche1.lower() == niche2.lower()
        except Exception as e:
            logger.error("Niche similarity check failed", error=str(e))
            return False
    
    async def _apply_learning_to_venture(self, learning_event: LearningEvent, venture_id: str):
        """Apply learning to a specific venture"""
        try:
            # Create optimization recommendation
            recommendation = await self._create_optimization_recommendation(learning_event, venture_id)
            
            # Store recommendation
            await self._store_optimization_recommendation(recommendation)
            
            # Update learning event
            learning_event.applied_to_ventures.add(venture_id)
            
            logger.info("Learning applied to venture", 
                      learning_id=learning_event.id, venture_id=venture_id)
            
        except Exception as e:
            logger.error("Learning application to venture failed", error=str(e))
    
    async def _create_optimization_recommendation(self, learning_event: LearningEvent, 
                                                venture_id: str) -> Dict[str, Any]:
        """Create optimization recommendation for a venture"""
        try:
            recommendation = {
                "id": f"rec_{int(time.time())}_{venture_id}",
                "venture_id": venture_id,
                "learning_event_id": learning_event.id,
                "agent_type": learning_event.agent_type,
                "recommendation_type": learning_event.learning_type.value,
                "description": learning_event.description,
                "expected_improvement": learning_event.success_metrics.get('improvement_potential', 0.1),
                "confidence_score": learning_event.confidence_score,
                "created_at": datetime.utcnow().isoformat(),
                "status": "pending"
            }
            
            return recommendation
            
        except Exception as e:
            logger.error("Recommendation creation failed", error=str(e))
            return {}
    
    async def get_optimization_insights(self, venture_id: str = None, 
                                      agent_type: str = None) -> Dict[str, Any]:
        """Get optimization insights for ventures or agents"""
        try:
            insights = {
                "total_learning_events": len(self.learning_events),
                "total_strategies": len(self.optimization_strategies),
                "success_patterns": len(self.success_patterns),
                "failure_patterns": len(self.failure_patterns),
                "market_insights": len(self.market_insights),
                "strategy_improvements": len(self.strategy_improvements),
                "recent_learnings": [],
                "top_strategies": []
            }
            
            # Get recent learnings
            recent_events = sorted(
                self.learning_events.values(), 
                key=lambda x: x.timestamp, 
                reverse=True
            )[:10]
            
            insights["recent_learnings"] = [
                {
                    "id": event.id,
                    "venture_id": event.venture_id,
                    "agent_type": event.agent_type,
                    "learning_type": event.learning_type.value,
                    "description": event.description,
                    "success_rate": event.success_metrics.get('success_rate', 0),
                    "timestamp": event.timestamp.isoformat()
                }
                for event in recent_events
            ]
            
            # Get top strategies
            top_strategies = sorted(
                self.optimization_strategies.values(),
                key=lambda x: x.success_rate,
                reverse=True
            )[:5]
            
            insights["top_strategies"] = [
                {
                    "id": strategy.id,
                    "name": strategy.name,
                    "success_rate": strategy.success_rate,
                    "application_count": strategy.application_count,
                    "last_updated": strategy.last_updated.isoformat()
                }
                for strategy in top_strategies
            ]
            
            return insights
            
        except Exception as e:
            logger.error("Failed to get optimization insights", error=str(e))
            return {}
    
    async def _store_learning_event(self, learning_event: LearningEvent):
        """Store learning event in Redis"""
        try:
            key = f"learning_event:{learning_event.id}"
            await self.redis.set(key, json.dumps(learning_event.__dict__, default=str))
            await self.redis.expire(key, 86400 * 30)  # 30 days
        except Exception as e:
            logger.error("Failed to store learning event", error=str(e))
    
    async def _store_optimization_strategy(self, strategy: OptimizationStrategy):
        """Store optimization strategy in Redis"""
        try:
            key = f"optimization_strategy:{strategy.id}"
            await self.redis.set(key, json.dumps(strategy.__dict__, default=str))
            await self.redis.expire(key, 86400 * 30)  # 30 days
        except Exception as e:
            logger.error("Failed to store optimization strategy", error=str(e))
    
    async def _store_optimization_recommendation(self, recommendation: Dict[str, Any]):
        """Store optimization recommendation in Redis"""
        try:
            key = f"optimization_recommendation:{recommendation['id']}"
            await self.redis.set(key, json.dumps(recommendation))
            await self.redis.expire(key, 86400 * 30)  # 30 days
        except Exception as e:
            logger.error("Failed to store optimization recommendation", error=str(e))

# Initialize the collaborative learning engine
async def initialize_collaborative_learning(redis_url: str = "redis://localhost:6379") -> CollaborativeLearningEngine:
    """Initialize the collaborative learning engine"""
    try:
        redis_client = redis.from_url(redis_url)
        learning_engine = CollaborativeLearningEngine(redis_client)
        
        logger.info("Collaborative learning engine initialized successfully")
        return learning_engine
        
    except Exception as e:
        logger.error("Failed to initialize collaborative learning engine", error=str(e))
        raise

if __name__ == "__main__":
    # Example usage
    async def main():
        learning_engine = await initialize_collaborative_learning()
        
        # Example learning event
        learning_event = await learning_engine.record_learning_event(
            venture_id="venture123",
            agent_type="marketing_strategy",
            learning_type=LearningType.SUCCESS_PATTERN,
            description="Social media advertising with video content shows 3x better conversion",
            data={
                "marketing_channel": "social_media",
                "content_type": "video",
                "target_audience": "millennials",
                "niche": "technology"
            },
            success_metrics={
                "conversion_rate": 0.15,
                "roi": 3.2,
                "success_rate": 0.85
            },
            confidence_score=0.9
        )
        
        print(f"Learning event recorded: {learning_event}")
        
        # Get insights
        insights = await learning_engine.get_optimization_insights()
        print("Optimization insights:", json.dumps(insights, indent=2))
    
    asyncio.run(main()) 
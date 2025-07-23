"""
Agent Collaboration System for AutoPilot Ventures
Enables agents to share learnings, collaborate, and optimize together across ventures
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

class CollaborationType(Enum):
    KNOWLEDGE_SHARING = "knowledge_sharing"
    STRATEGY_COLLABORATION = "strategy_collaboration"
    PROBLEM_SOLVING = "problem_solving"
    INNOVATION = "innovation"
    OPTIMIZATION = "optimization"

class AgentRole(Enum):
    INITIATOR = "initiator"
    CONTRIBUTOR = "contributor"
    VALIDATOR = "validator"
    IMPLEMENTER = "implementer"

@dataclass
class CollaborationSession:
    id: str
    session_type: CollaborationType
    participants: List[str]  # Agent types
    venture_ids: List[str]
    topic: str
    description: str
    insights: List[Dict[str, Any]] = field(default_factory=list)
    decisions: List[Dict[str, Any]] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    success_metrics: Dict[str, float] = field(default_factory=dict)

@dataclass
class AgentInsight:
    id: str
    agent_type: str
    venture_id: str
    insight_type: str
    description: str
    data: Dict[str, Any]
    confidence: float
    timestamp: datetime
    shared_with: Set[str] = field(default_factory=set)
    validated_by: Set[str] = field(default_factory=set)

@dataclass
class CollaborativeStrategy:
    id: str
    name: str
    description: str
    contributing_agents: List[str]
    venture_applications: List[str]
    success_rate: float
    implementation_guide: Dict[str, Any]
    created_at: datetime
    last_updated: datetime
    active: bool = True

class AgentCollaborationSystem:
    """System for agent collaboration and knowledge sharing"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.collaboration_sessions = {}
        self.agent_insights = {}
        self.collaborative_strategies = {}
        self.agent_networks = defaultdict(set)
        self.knowledge_base = defaultdict(list)
        
        # Metrics
        self.collaboration_sessions_total = Counter('collaboration_sessions_total', 'Total collaboration sessions', ['type'])
        self.insights_shared = Counter('insights_shared_total', 'Insights shared between agents', ['from_agent', 'to_agent'])
        self.strategies_created = Counter('collaborative_strategies_created', 'Collaborative strategies created')
        self.success_rate_improvement = Gauge('collaborative_success_improvement', 'Success rate improvement from collaboration', ['venture_id'])
        
        # Agent expertise areas
        self.agent_expertise = {
            "niche_research": ["market_analysis", "competition_research", "trend_identification"],
            "mvp_design": ["product_development", "technology_selection", "user_experience"],
            "marketing_strategy": ["campaign_planning", "audience_targeting", "channel_optimization"],
            "content_creation": ["copywriting", "visual_design", "content_strategy"],
            "analytics": ["data_analysis", "performance_tracking", "insight_generation"],
            "operations_monetization": ["business_optimization", "revenue_generation", "cost_management"],
            "funding_investor": ["investment_strategy", "funding_optimization", "financial_planning"],
            "legal_compliance": ["legal_requirements", "compliance_management", "risk_assessment"],
            "hr_team_building": ["team_management", "talent_acquisition", "culture_development"],
            "customer_support_scaling": ["customer_service", "scaling_strategies", "support_optimization"]
        }
    
    async def initiate_collaboration(self, initiator_agent: str, session_type: CollaborationType,
                                   topic: str, description: str, venture_ids: List[str]) -> str:
        """Initiate a collaboration session between agents"""
        try:
            session_id = f"collab_{int(time.time())}_{initiator_agent}"
            
            # Determine participants based on session type and topic
            participants = await self._determine_participants(session_type, topic, venture_ids)
            
            session = CollaborationSession(
                id=session_id,
                session_type=session_type,
                participants=participants,
                venture_ids=venture_ids,
                topic=topic,
                description=description
            )
            
            self.collaboration_sessions[session_id] = session
            await self._store_collaboration_session(session)
            
            # Update metrics
            self.collaboration_sessions_total.labels(type=session_type.value).inc()
            
            # Notify participants
            await self._notify_participants(session)
            
            logger.info("Collaboration session initiated", 
                      session_id=session_id, initiator=initiator_agent,
                      participants=participants, topic=topic)
            
            return session_id
            
        except Exception as e:
            logger.error("Failed to initiate collaboration", error=str(e))
            raise
    
    async def _determine_participants(self, session_type: CollaborationType, 
                                    topic: str, venture_ids: List[str]) -> List[str]:
        """Determine which agents should participate in the collaboration"""
        try:
            participants = set()
            
            # Add agents based on session type
            if session_type == CollaborationType.KNOWLEDGE_SHARING:
                # All agents can share knowledge
                participants.update(self.agent_expertise.keys())
            
            elif session_type == CollaborationType.STRATEGY_COLLABORATION:
                # Strategy-focused agents
                strategy_agents = ["niche_research", "marketing_strategy", "operations_monetization", "analytics"]
                participants.update(strategy_agents)
            
            elif session_type == CollaborationType.PROBLEM_SOLVING:
                # Problem-solving focused agents
                problem_agents = ["analytics", "operations_monetization", "customer_support_scaling"]
                participants.update(problem_agents)
            
            elif session_type == CollaborationType.INNOVATION:
                # Innovation-focused agents
                innovation_agents = ["niche_research", "mvp_design", "marketing_strategy", "content_creation"]
                participants.update(innovation_agents)
            
            elif session_type == CollaborationType.OPTIMIZATION:
                # Optimization-focused agents
                optimization_agents = ["analytics", "operations_monetization", "marketing_strategy"]
                participants.update(optimization_agents)
            
            # Add agents based on topic keywords
            topic_keywords = topic.lower().split()
            for agent_type, expertise_areas in self.agent_expertise.items():
                for expertise in expertise_areas:
                    if any(keyword in expertise for keyword in topic_keywords):
                        participants.add(agent_type)
            
            return list(participants)
            
        except Exception as e:
            logger.error("Failed to determine participants", error=str(e))
            return []
    
    async def share_insight(self, agent_type: str, venture_id: str, insight_type: str,
                          description: str, data: Dict[str, Any], confidence: float) -> str:
        """Share an insight with other agents"""
        try:
            insight_id = f"insight_{int(time.time())}_{agent_type}"
            
            insight = AgentInsight(
                id=insight_id,
                agent_type=agent_type,
                venture_id=venture_id,
                insight_type=insight_type,
                description=description,
                data=data,
                confidence=confidence,
                timestamp=datetime.utcnow()
            )
            
            self.agent_insights[insight_id] = insight
            await self._store_agent_insight(insight)
            
            # Share with relevant agents
            await self._share_insight_with_agents(insight)
            
            # Add to knowledge base
            self.knowledge_base[insight_type].append(insight_id)
            
            logger.info("Insight shared", 
                      insight_id=insight_id, agent_type=agent_type,
                      insight_type=insight_type, description=description)
            
            return insight_id
            
        except Exception as e:
            logger.error("Failed to share insight", error=str(e))
            raise
    
    async def _share_insight_with_agents(self, insight: AgentInsight):
        """Share insight with relevant agents"""
        try:
            # Determine which agents would benefit from this insight
            relevant_agents = await self._find_relevant_agents(insight)
            
            for agent_type in relevant_agents:
                if agent_type != insight.agent_type:
                    # Share the insight
                    insight.shared_with.add(agent_type)
                    
                    # Update metrics
                    self.insights_shared.labels(from_agent=insight.agent_type, to_agent=agent_type).inc()
                    
                    # Update agent network
                    self.agent_networks[insight.agent_type].add(agent_type)
                    
                    logger.info("Insight shared with agent", 
                              insight_id=insight.id, from_agent=insight.agent_type,
                              to_agent=agent_type)
            
        except Exception as e:
            logger.error("Failed to share insight with agents", error=str(e))
    
    async def _find_relevant_agents(self, insight: AgentInsight) -> List[str]:
        """Find agents that would benefit from this insight"""
        try:
            relevant_agents = []
            
            # Check agent expertise areas
            for agent_type, expertise_areas in self.agent_expertise.items():
                for expertise in expertise_areas:
                    if expertise in insight.insight_type.lower() or expertise in insight.description.lower():
                        relevant_agents.append(agent_type)
                        break
            
            # Add agents based on insight type
            if insight.insight_type == "market_analysis":
                relevant_agents.extend(["marketing_strategy", "niche_research", "analytics"])
            elif insight.insight_type == "performance_optimization":
                relevant_agents.extend(["operations_monetization", "analytics", "customer_support_scaling"])
            elif insight.insight_type == "customer_behavior":
                relevant_agents.extend(["marketing_strategy", "content_creation", "customer_support_scaling"])
            elif insight.insight_type == "technology_trend":
                relevant_agents.extend(["mvp_design", "analytics", "operations_monetization"])
            
            return list(set(relevant_agents))  # Remove duplicates
            
        except Exception as e:
            logger.error("Failed to find relevant agents", error=str(e))
            return []
    
    async def validate_insight(self, agent_type: str, insight_id: str, validation_score: float, 
                             comments: str = "") -> bool:
        """Validate an insight from another agent"""
        try:
            if insight_id not in self.agent_insights:
                raise ValueError(f"Insight {insight_id} not found")
            
            insight = self.agent_insights[insight_id]
            insight.validated_by.add(agent_type)
            
            # Update insight confidence based on validation
            if validation_score > 0.7:
                insight.confidence = min(1.0, insight.confidence + 0.1)
            elif validation_score < 0.3:
                insight.confidence = max(0.0, insight.confidence - 0.1)
            
            # Store updated insight
            await self._store_agent_insight(insight)
            
            logger.info("Insight validated", 
                      insight_id=insight_id, validator=agent_type,
                      validation_score=validation_score, new_confidence=insight.confidence)
            
            return True
            
        except Exception as e:
            logger.error("Failed to validate insight", error=str(e))
            return False
    
    async def create_collaborative_strategy(self, session_id: str, strategy_name: str,
                                          description: str, contributing_agents: List[str],
                                          implementation_guide: Dict[str, Any]) -> str:
        """Create a collaborative strategy based on session insights"""
        try:
            if session_id not in self.collaboration_sessions:
                raise ValueError(f"Session {session_id} not found")
            
            session = self.collaboration_sessions[session_id]
            
            # Calculate success rate based on session insights
            success_rate = await self._calculate_strategy_success_rate(session)
            
            strategy_id = f"strategy_{int(time.time())}"
            
            strategy = CollaborativeStrategy(
                id=strategy_id,
                name=strategy_name,
                description=description,
                contributing_agents=contributing_agents,
                venture_applications=session.venture_ids,
                success_rate=success_rate,
                implementation_guide=implementation_guide,
                created_at=datetime.utcnow(),
                last_updated=datetime.utcnow()
            )
            
            self.collaborative_strategies[strategy_id] = strategy
            await self._store_collaborative_strategy(strategy)
            
            # Update metrics
            self.strategies_created.inc()
            
            # End the collaboration session
            session.end_time = datetime.utcnow()
            session.decisions.append({
                "strategy_id": strategy_id,
                "decision": "Create collaborative strategy",
                "timestamp": datetime.utcnow().isoformat()
            })
            
            await self._store_collaboration_session(session)
            
            logger.info("Collaborative strategy created", 
                      strategy_id=strategy_id, session_id=session_id,
                      contributing_agents=contributing_agents, success_rate=success_rate)
            
            return strategy_id
            
        except Exception as e:
            logger.error("Failed to create collaborative strategy", error=str(e))
            raise
    
    async def _calculate_strategy_success_rate(self, session: CollaborationSession) -> float:
        """Calculate expected success rate for a strategy"""
        try:
            # Analyze session insights
            total_confidence = 0
            insight_count = 0
            
            for insight_id in session.insights:
                if insight_id in self.agent_insights:
                    insight = self.agent_insights[insight_id]
                    total_confidence += insight.confidence
                    insight_count += 1
            
            if insight_count == 0:
                return 0.5  # Default success rate
            
            avg_confidence = total_confidence / insight_count
            
            # Factor in number of participants (more collaboration = higher success)
            collaboration_bonus = min(0.2, len(session.participants) * 0.02)
            
            success_rate = min(1.0, avg_confidence + collaboration_bonus)
            
            return success_rate
            
        except Exception as e:
            logger.error("Failed to calculate strategy success rate", error=str(e))
            return 0.5
    
    async def apply_collaborative_strategy(self, strategy_id: str, venture_id: str) -> Dict[str, Any]:
        """Apply a collaborative strategy to a venture"""
        try:
            if strategy_id not in self.collaborative_strategies:
                raise ValueError(f"Strategy {strategy_id} not found")
            
            strategy = self.collaborative_strategies[strategy_id]
            
            # Check if strategy is applicable to this venture
            if not await self._is_strategy_applicable(strategy, venture_id):
                return {"success": False, "reason": "Strategy not applicable to this venture"}
            
            # Apply the strategy
            implementation_result = await self._implement_strategy(strategy, venture_id)
            
            # Update strategy metrics
            strategy.last_updated = datetime.utcnow()
            await self._store_collaborative_strategy(strategy)
            
            # Update success rate improvement metric
            self.success_rate_improvement.labels(venture_id=venture_id).set(
                implementation_result.get('success_rate_improvement', 0)
            )
            
            logger.info("Collaborative strategy applied", 
                      strategy_id=strategy_id, venture_id=venture_id,
                      result=implementation_result)
            
            return implementation_result
            
        except Exception as e:
            logger.error("Failed to apply collaborative strategy", error=str(e))
            return {"success": False, "error": str(e)}
    
    async def _is_strategy_applicable(self, strategy: CollaborativeStrategy, venture_id: str) -> bool:
        """Check if a strategy is applicable to a venture"""
        try:
            # Check if venture is in the original applications
            if venture_id in strategy.venture_applications:
                return True
            
            # Check venture characteristics against strategy requirements
            venture_characteristics = await self._get_venture_characteristics(venture_id)
            strategy_requirements = strategy.implementation_guide.get('requirements', {})
            
            # Simple applicability check
            for requirement, value in strategy_requirements.items():
                if requirement in venture_characteristics:
                    if venture_characteristics[requirement] != value:
                        return False
            
            return True
            
        except Exception as e:
            logger.error("Strategy applicability check failed", error=str(e))
            return False
    
    async def _get_venture_characteristics(self, venture_id: str) -> Dict[str, Any]:
        """Get venture characteristics"""
        try:
            # This would query the database for venture characteristics
            # For now, return empty dict
            return {}
        except Exception as e:
            logger.error("Failed to get venture characteristics", error=str(e))
            return {}
    
    async def _implement_strategy(self, strategy: CollaborativeStrategy, venture_id: str) -> Dict[str, Any]:
        """Implement a strategy for a venture"""
        try:
            implementation_guide = strategy.implementation_guide
            
            # Simulate strategy implementation
            implementation_result = {
                "success": True,
                "strategy_id": strategy.id,
                "venture_id": venture_id,
                "implementation_steps": implementation_guide.get('steps', []),
                "success_rate_improvement": strategy.success_rate * 0.1,  # 10% of strategy success rate
                "estimated_roi": strategy.success_rate * 2.5,  # Estimated ROI
                "implementation_time": "2-4 weeks",
                "resources_required": implementation_guide.get('resources', [])
            }
            
            return implementation_result
            
        except Exception as e:
            logger.error("Strategy implementation failed", error=str(e))
            return {"success": False, "error": str(e)}
    
    async def get_collaboration_insights(self, venture_id: str = None, 
                                      agent_type: str = None) -> Dict[str, Any]:
        """Get insights about agent collaboration"""
        try:
            insights = {
                "total_sessions": len(self.collaboration_sessions),
                "total_insights": len(self.agent_insights),
                "total_strategies": len(self.collaborative_strategies),
                "active_sessions": len([s for s in self.collaboration_sessions.values() if s.end_time is None]),
                "recent_collaborations": [],
                "top_strategies": [],
                "agent_network": {}
            }
            
            # Get recent collaborations
            recent_sessions = sorted(
                self.collaboration_sessions.values(),
                key=lambda x: x.start_time,
                reverse=True
            )[:10]
            
            insights["recent_collaborations"] = [
                {
                    "id": session.id,
                    "type": session.session_type.value,
                    "topic": session.topic,
                    "participants": session.participants,
                    "venture_count": len(session.venture_ids),
                    "start_time": session.start_time.isoformat(),
                    "status": "active" if session.end_time is None else "completed"
                }
                for session in recent_sessions
            ]
            
            # Get top strategies
            top_strategies = sorted(
                self.collaborative_strategies.values(),
                key=lambda x: x.success_rate,
                reverse=True
            )[:5]
            
            insights["top_strategies"] = [
                {
                    "id": strategy.id,
                    "name": strategy.name,
                    "success_rate": strategy.success_rate,
                    "contributing_agents": strategy.contributing_agents,
                    "venture_applications": len(strategy.venture_applications),
                    "created_at": strategy.created_at.isoformat()
                }
                for strategy in top_strategies
            ]
            
            # Get agent network
            insights["agent_network"] = {
                agent: list(connections) 
                for agent, connections in self.agent_networks.items()
            }
            
            return insights
            
        except Exception as e:
            logger.error("Failed to get collaboration insights", error=str(e))
            return {}
    
    async def _notify_participants(self, session: CollaborationSession):
        """Notify participants about a collaboration session"""
        try:
            # This would send notifications to participating agents
            # For now, just log the notification
            logger.info("Notifying participants about collaboration session", 
                      session_id=session.id, participants=session.participants)
            
        except Exception as e:
            logger.error("Failed to notify participants", error=str(e))
    
    async def _store_collaboration_session(self, session: CollaborationSession):
        """Store collaboration session in Redis"""
        try:
            key = f"collaboration_session:{session.id}"
            await self.redis.set(key, json.dumps(session.__dict__, default=str))
            await self.redis.expire(key, 86400 * 30)  # 30 days
        except Exception as e:
            logger.error("Failed to store collaboration session", error=str(e))
    
    async def _store_agent_insight(self, insight: AgentInsight):
        """Store agent insight in Redis"""
        try:
            key = f"agent_insight:{insight.id}"
            await self.redis.set(key, json.dumps(insight.__dict__, default=str))
            await self.redis.expire(key, 86400 * 30)  # 30 days
        except Exception as e:
            logger.error("Failed to store agent insight", error=str(e))
    
    async def _store_collaborative_strategy(self, strategy: CollaborativeStrategy):
        """Store collaborative strategy in Redis"""
        try:
            key = f"collaborative_strategy:{strategy.id}"
            await self.redis.set(key, json.dumps(strategy.__dict__, default=str))
            await self.redis.expire(key, 86400 * 30)  # 30 days
        except Exception as e:
            logger.error("Failed to store collaborative strategy", error=str(e))

# Initialize the agent collaboration system
async def initialize_agent_collaboration(redis_url: str = "redis://localhost:6379") -> AgentCollaborationSystem:
    """Initialize the agent collaboration system"""
    try:
        redis_client = redis.from_url(redis_url)
        collaboration_system = AgentCollaborationSystem(redis_client)
        
        logger.info("Agent collaboration system initialized successfully")
        return collaboration_system
        
    except Exception as e:
        logger.error("Failed to initialize agent collaboration system", error=str(e))
        raise

if __name__ == "__main__":
    # Example usage
    async def main():
        collaboration_system = await initialize_agent_collaboration()
        
        # Example collaboration session
        session_id = await collaboration_system.initiate_collaboration(
            initiator_agent="marketing_strategy",
            session_type=CollaborationType.STRATEGY_COLLABORATION,
            topic="Social media marketing optimization",
            description="Collaborate on improving social media marketing strategies across ventures",
            venture_ids=["venture123", "venture456"]
        )
        
        print(f"Collaboration session created: {session_id}")
        
        # Example insight sharing
        insight_id = await collaboration_system.share_insight(
            agent_type="analytics",
            venture_id="venture123",
            insight_type="performance_optimization",
            description="Video content performs 3x better than static images on social media",
            data={"content_type": "video", "performance_boost": 3.0},
            confidence=0.9
        )
        
        print(f"Insight shared: {insight_id}")
        
        # Get collaboration insights
        insights = await collaboration_system.get_collaboration_insights()
        print("Collaboration insights:", json.dumps(insights, indent=2))
    
    asyncio.run(main()) 
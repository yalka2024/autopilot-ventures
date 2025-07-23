"""
Adaptive Reinforcement Learning for Self-Evolving Agents
Enables agents to learn from business outcomes and auto-optimize strategies
"""

import asyncio
import json
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import redis
import pickle
from collections import defaultdict
import structlog

# ML libraries for reinforcement learning
try:
    from stable_baselines3 import PPO, A2C, DQN
    from stable_baselines3.common.vec_env import DummyVecEnv
    from stable_baselines3.common.callbacks import BaseCallback
    STABLE_BASELINES_AVAILABLE = True
except ImportError:
    STABLE_BASELINES_AVAILABLE = False
    print("Warning: stable-baselines3 not available, using simplified RL")

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("Warning: PyTorch not available, using simplified RL")

from config import config
from utils import generate_id, log

# Configure structured logging
logger = structlog.get_logger()

class BusinessOutcome(Enum):
    """Types of business outcomes for reward calculation."""
    REVENUE_INCREASE = "revenue_increase"
    CUSTOMER_ACQUISITION = "customer_acquisition"
    CONVERSION_RATE_IMPROVEMENT = "conversion_rate_improvement"
    COST_REDUCTION = "cost_reduction"
    FAILURE_RATE_REDUCTION = "failure_rate_reduction"
    CUSTOMER_SATISFACTION = "customer_satisfaction"
    MARKET_EXPANSION = "market_expansion"

class AgentType(Enum):
    """Types of agents that can use reinforcement learning."""
    NICHE_RESEARCH = "niche_research"
    MVP_DESIGN = "mvp_design"
    MARKETING_STRATEGY = "marketing_strategy"
    CONTENT_CREATION = "content_creation"
    ANALYTICS = "analytics"
    OPERATIONS_MONETIZATION = "operations_monetization"
    FUNDING_INVESTOR = "funding_investor"
    LEGAL_COMPLIANCE = "legal_compliance"
    HR_TEAM_BUILDING = "hr_team_building"
    CUSTOMER_SUPPORT = "customer_support"

@dataclass
class BusinessMetrics:
    """Business metrics for reward calculation."""
    revenue: float = 0.0
    customers: int = 0
    conversion_rate: float = 0.0
    cost: float = 0.0
    failure_rate: float = 0.0
    satisfaction_score: float = 0.0
    market_reach: int = 0
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class AgentAction:
    """Agent action with context for learning."""
    agent_type: AgentType
    action_type: str
    parameters: Dict[str, Any]
    context: Dict[str, Any]
    language: str = "en"
    timestamp: datetime = field(default_factory=datetime.utcnow)
    confidence: float = 0.0

@dataclass
class LearningEpisode:
    """Complete learning episode with state, action, reward."""
    episode_id: str
    agent_type: AgentType
    state: Dict[str, Any]
    action: AgentAction
    reward: float
    next_state: Dict[str, Any]
    done: bool
    metadata: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)

class RewardCalculator:
    """Calculates rewards based on business outcomes."""
    
    def __init__(self):
        self.reward_weights = {
            BusinessOutcome.REVENUE_INCREASE: 1.0,
            BusinessOutcome.CUSTOMER_ACQUISITION: 0.8,
            BusinessOutcome.CONVERSION_RATE_IMPROVEMENT: 0.9,
            BusinessOutcome.COST_REDUCTION: 0.7,
            BusinessOutcome.FAILURE_RATE_REDUCTION: 0.6,
            BusinessOutcome.CUSTOMER_SATISFACTION: 0.5,
            BusinessOutcome.MARKET_EXPANSION: 0.4
        }
    
    def calculate_reward(
        self, 
        before_metrics: BusinessMetrics, 
        after_metrics: BusinessMetrics,
        agent_type: AgentType,
        language: str = "en"
    ) -> float:
        """Calculate reward based on business outcome improvements."""
        reward = 0.0
        
        # Revenue increase reward
        if after_metrics.revenue > before_metrics.revenue:
            revenue_improvement = (after_metrics.revenue - before_metrics.revenue) / max(before_metrics.revenue, 1)
            reward += revenue_improvement * self.reward_weights[BusinessOutcome.REVENUE_INCREASE]
        
        # Customer acquisition reward
        if after_metrics.customers > before_metrics.customers:
            customer_improvement = (after_metrics.customers - before_metrics.customers) / max(before_metrics.customers, 1)
            reward += customer_improvement * self.reward_weights[BusinessOutcome.CUSTOMER_ACQUISITION]
        
        # Conversion rate improvement
        if after_metrics.conversion_rate > before_metrics.conversion_rate:
            conversion_improvement = (after_metrics.conversion_rate - before_metrics.conversion_rate) / max(before_metrics.conversion_rate, 0.01)
            reward += conversion_improvement * self.reward_weights[BusinessOutcome.CONVERSION_RATE_IMPROVEMENT]
        
        # Cost reduction reward
        if after_metrics.cost < before_metrics.cost:
            cost_reduction = (before_metrics.cost - after_metrics.cost) / max(before_metrics.cost, 1)
            reward += cost_reduction * self.reward_weights[BusinessOutcome.COST_REDUCTION]
        
        # Failure rate reduction
        if after_metrics.failure_rate < before_metrics.failure_rate:
            failure_reduction = (before_metrics.failure_rate - after_metrics.failure_rate) / max(before_metrics.failure_rate, 0.01)
            reward += failure_reduction * self.reward_weights[BusinessOutcome.FAILURE_RATE_REDUCTION]
        
        # Customer satisfaction improvement
        if after_metrics.satisfaction_score > before_metrics.satisfaction_score:
            satisfaction_improvement = (after_metrics.satisfaction_score - before_metrics.satisfaction_score) / max(before_metrics.satisfaction_score, 0.1)
            reward += satisfaction_improvement * self.reward_weights[BusinessOutcome.CUSTOMER_SATISFACTION]
        
        # Market expansion reward
        if after_metrics.market_reach > before_metrics.market_reach:
            market_improvement = (after_metrics.market_reach - before_metrics.market_reach) / max(before_metrics.market_reach, 1)
            reward += market_improvement * self.reward_weights[BusinessOutcome.MARKET_EXPANSION]
        
        # Language-specific adjustments
        language_multiplier = self._get_language_multiplier(language)
        reward *= language_multiplier
        
        # Agent-type specific adjustments
        agent_multiplier = self._get_agent_multiplier(agent_type)
        reward *= agent_multiplier
        
        return max(reward, -1.0)  # Cap negative rewards
    
    def _get_language_multiplier(self, language: str) -> float:
        """Get language-specific reward multiplier."""
        # Higher rewards for non-English languages to encourage global expansion
        multipliers = {
            "en": 1.0,
            "es": 1.1,
            "zh": 1.2,
            "fr": 1.1,
            "de": 1.1,
            "ar": 1.3,
            "pt": 1.1,
            "hi": 1.2,
            "ru": 1.1,
            "ja": 1.2
        }
        return multipliers.get(language, 1.0)
    
    def _get_agent_multiplier(self, agent_type: AgentType) -> float:
        """Get agent-type specific reward multiplier."""
        # Higher rewards for revenue-generating agents
        multipliers = {
            AgentType.MARKETING_STRATEGY: 1.2,
            AgentType.OPERATIONS_MONETIZATION: 1.3,
            AgentType.CONTENT_CREATION: 1.1,
            AgentType.ANALYTICS: 1.0,
            AgentType.NICHE_RESEARCH: 0.9,
            AgentType.MVP_DESIGN: 0.8,
            AgentType.FUNDING_INVESTOR: 1.1,
            AgentType.LEGAL_COMPLIANCE: 0.7,
            AgentType.HR_TEAM_BUILDING: 0.8,
            AgentType.CUSTOMER_SUPPORT: 0.9
        }
        return multipliers.get(agent_type, 1.0)

class SimpleQTable:
    """Simple Q-learning table for agents without stable-baselines3."""
    
    def __init__(self, learning_rate: float = 0.1, discount_factor: float = 0.95, epsilon: float = 0.1):
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.q_table = defaultdict(lambda: defaultdict(float))
        self.action_counts = defaultdict(int)
    
    def get_action(self, state: str, available_actions: List[str]) -> str:
        """Get action using epsilon-greedy policy."""
        if np.random.random() < self.epsilon:
            return np.random.choice(available_actions)
        
        # Choose best action based on Q-values
        q_values = [self.q_table[state][action] for action in available_actions]
        max_q = max(q_values)
        best_actions = [action for action, q in zip(available_actions, q_values) if q == max_q]
        return np.random.choice(best_actions)
    
    def update(self, state: str, action: str, reward: float, next_state: str, next_actions: List[str]):
        """Update Q-table using Q-learning algorithm."""
        current_q = self.q_table[state][action]
        
        if next_actions:
            next_max_q = max(self.q_table[next_state][next_action] for next_action in next_actions)
        else:
            next_max_q = 0
        
        new_q = current_q + self.learning_rate * (reward + self.discount_factor * next_max_q - current_q)
        self.q_table[state][action] = new_q
        self.action_counts[action] += 1
    
    def get_state_value(self, state: str) -> float:
        """Get the maximum Q-value for a state."""
        if not self.q_table[state]:
            return 0.0
        return max(self.q_table[state].values())

class AdaptiveReinforcementLearning:
    """Adaptive reinforcement learning system for self-evolving agents."""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client or redis.Redis.from_url(config.database.url.replace('sqlite', 'redis'))
        self.reward_calculator = RewardCalculator()
        self.agents = {}
        self.episodes = []
        self.learning_enabled = True
        self.min_episodes_for_learning = 10
        self.performance_threshold = 0.6
        
        # Initialize learning models for each agent type
        self._initialize_learning_models()
        
        logger.info("Adaptive Reinforcement Learning system initialized")
    
    def _initialize_learning_models(self):
        """Initialize learning models for each agent type."""
        for agent_type in AgentType:
            if STABLE_BASELINES_AVAILABLE:
                # Use stable-baselines3 for advanced RL
                self.agents[agent_type] = self._create_stable_baselines_model(agent_type)
            else:
                # Use simple Q-learning table
                self.agents[agent_type] = SimpleQTable()
        
        logger.info(f"Initialized learning models for {len(self.agents)} agent types")
    
    def _create_stable_baselines_model(self, agent_type: AgentType):
        """Create stable-baselines3 model for agent type."""
        # Define action and observation spaces based on agent type
        if agent_type in [AgentType.MARKETING_STRATEGY, AgentType.CONTENT_CREATION]:
            # These agents have more complex action spaces
            return PPO("MlpPolicy", env=None, verbose=0)
        else:
            # Simpler agents can use DQN
            return DQN("MlpPolicy", env=None, verbose=0)
    
    async def record_episode(
        self,
        agent_type: AgentType,
        state: Dict[str, Any],
        action: AgentAction,
        reward: float,
        next_state: Dict[str, Any],
        done: bool,
        metadata: Dict[str, Any]
    ):
        """Record a learning episode."""
        episode = LearningEpisode(
            episode_id=generate_id("episode"),
            agent_type=agent_type,
            state=state,
            action=action,
            reward=reward,
            next_state=next_state,
            done=done,
            metadata=metadata
        )
        
        self.episodes.append(episode)
        
        # Store in Redis for persistence
        if self.redis_client:
            await self._store_episode_redis(episode)
        
        # Trigger learning if enough episodes
        if len(self.episodes) >= self.min_episodes_for_learning:
            await self._trigger_learning(agent_type)
        
        logger.info(f"Recorded episode for {agent_type.value}", 
                   episode_id=episode.episode_id, reward=reward)
    
    async def _store_episode_redis(self, episode: LearningEpisode):
        """Store episode in Redis."""
        try:
            episode_data = {
                'episode_id': episode.episode_id,
                'agent_type': episode.agent_type.value,
                'state': json.dumps(episode.state),
                'action': json.dumps(episode.action.__dict__),
                'reward': episode.reward,
                'next_state': json.dumps(episode.next_state),
                'done': episode.done,
                'metadata': json.dumps(episode.metadata),
                'timestamp': episode.timestamp.isoformat()
            }
            
            # Store in Redis hash
            key = f"rl_episode:{episode.episode_id}"
            self.redis_client.hset(key, mapping=episode_data)
            self.redis_client.expire(key, 86400 * 30)  # 30 days TTL
            
        except Exception as e:
            logger.error(f"Failed to store episode in Redis: {e}")
    
    async def _trigger_learning(self, agent_type: AgentType):
        """Trigger learning process for agent type."""
        try:
            # Get recent episodes for this agent type
            recent_episodes = [
                ep for ep in self.episodes[-100:]  # Last 100 episodes
                if ep.agent_type == agent_type
            ]
            
            if len(recent_episodes) < 5:
                return
            
            # Update learning model
            if isinstance(self.agents[agent_type], SimpleQTable):
                await self._update_q_table(agent_type, recent_episodes)
            else:
                await self._update_stable_baselines_model(agent_type, recent_episodes)
            
            logger.info(f"Triggered learning for {agent_type.value}", 
                       episodes_used=len(recent_episodes))
            
        except Exception as e:
            logger.error(f"Failed to trigger learning for {agent_type.value}: {e}")
    
    async def _update_q_table(self, agent_type: AgentType, episodes: List[LearningEpisode]):
        """Update Q-table with recent episodes."""
        q_table = self.agents[agent_type]
        
        for episode in episodes:
            state_str = self._state_to_string(episode.state)
            next_state_str = self._state_to_string(episode.next_state)
            action_str = self._action_to_string(episode.action)
            
            # Get available actions for next state (simplified)
            next_actions = self._get_available_actions(episode.agent_type)
            
            q_table.update(state_str, action_str, episode.reward, next_state_str, next_actions)
    
    async def _update_stable_baselines_model(self, agent_type: AgentType, episodes: List[LearningEpisode]):
        """Update stable-baselines3 model with recent episodes."""
        # This would require creating a proper environment
        # For now, we'll use a simplified approach
        logger.info(f"Stable-baselines3 learning update for {agent_type.value}")
    
    def _state_to_string(self, state: Dict[str, Any]) -> str:
        """Convert state dictionary to string representation."""
        # Create a simplified state representation for Q-learning
        state_parts = []
        for key, value in state.items():
            if isinstance(value, (int, float, str, bool)):
                state_parts.append(f"{key}:{value}")
            elif isinstance(value, dict):
                state_parts.append(f"{key}:{len(value)}")
            elif isinstance(value, list):
                state_parts.append(f"{key}:{len(value)}")
        
        return "|".join(sorted(state_parts))
    
    def _action_to_string(self, action: AgentAction) -> str:
        """Convert action to string representation."""
        return f"{action.action_type}:{action.language}"
    
    def _get_available_actions(self, agent_type: AgentType) -> List[str]:
        """Get available actions for agent type."""
        # Simplified action space
        base_actions = ["optimize", "explore", "exploit", "adapt"]
        languages = config.multilingual.supported_languages
        
        actions = []
        for action in base_actions:
            for lang in languages:
                actions.append(f"{action}:{lang}")
        
        return actions
    
    async def get_optimized_action(
        self,
        agent_type: AgentType,
        current_state: Dict[str, Any],
        context: Dict[str, Any],
        language: str = "en"
    ) -> AgentAction:
        """Get optimized action based on learned policy."""
        try:
            if agent_type not in self.agents:
                logger.warning(f"No learning model for agent type: {agent_type.value}")
                return self._get_default_action(agent_type, context, language)
            
            # Convert state to string for Q-learning
            state_str = self._state_to_string(current_state)
            
            if isinstance(self.agents[agent_type], SimpleQTable):
                # Use Q-table to get action
                available_actions = self._get_available_actions(agent_type)
                action_str = self.agents[agent_type].get_action(state_str, available_actions)
                
                # Parse action string
                action_type, action_language = action_str.split(":", 1)
                
                return AgentAction(
                    agent_type=agent_type,
                    action_type=action_type,
                    parameters=self._get_action_parameters(action_type, context),
                    context=context,
                    language=action_language,
                    confidence=self.agents[agent_type].get_state_value(state_str)
                )
            else:
                # Use stable-baselines3 model
                return await self._get_stable_baselines_action(agent_type, current_state, context, language)
                
        except Exception as e:
            logger.error(f"Failed to get optimized action: {e}")
            return self._get_default_action(agent_type, context, language)
    
    def _get_default_action(self, agent_type: AgentType, context: Dict[str, Any], language: str) -> AgentAction:
        """Get default action when learning fails."""
        return AgentAction(
            agent_type=agent_type,
            action_type="explore",
            parameters={"strategy": "default"},
            context=context,
            language=language,
            confidence=0.5
        )
    
    async def _get_stable_baselines_action(
        self, 
        agent_type: AgentType, 
        current_state: Dict[str, Any], 
        context: Dict[str, Any], 
        language: str
    ) -> AgentAction:
        """Get action from stable-baselines3 model."""
        # Simplified implementation
        return AgentAction(
            agent_type=agent_type,
            action_type="optimize",
            parameters={"strategy": "ml_optimized"},
            context=context,
            language=language,
            confidence=0.8
        )
    
    def _get_action_parameters(self, action_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get parameters for action type."""
        if action_type == "optimize":
            return {
                "strategy": "performance_optimization",
                "focus": context.get("focus", "revenue"),
                "timeframe": "short_term"
            }
        elif action_type == "explore":
            return {
                "strategy": "exploration",
                "risk_level": "medium",
                "budget_allocation": 0.2
            }
        elif action_type == "exploit":
            return {
                "strategy": "exploitation",
                "focus": "best_performing",
                "scaling_factor": 1.5
            }
        elif action_type == "adapt":
            return {
                "strategy": "adaptation",
                "learning_rate": 0.1,
                "adaptation_threshold": 0.1
            }
        else:
            return {"strategy": "default"}
    
    async def calculate_business_outcome_reward(
        self,
        before_metrics: BusinessMetrics,
        after_metrics: BusinessMetrics,
        agent_type: AgentType,
        language: str = "en"
    ) -> float:
        """Calculate reward based on business outcome improvements."""
        return self.reward_calculator.calculate_reward(
            before_metrics, after_metrics, agent_type, language
        )
    
    async def get_learning_performance(self, agent_type: Optional[AgentType] = None) -> Dict[str, Any]:
        """Get learning performance metrics."""
        if agent_type:
            agents_to_check = [agent_type]
        else:
            agents_to_check = list(self.agents.keys())
        
        performance = {}
        
        for agent in agents_to_check:
            if agent in self.agents:
                model = self.agents[agent]
                
                if isinstance(model, SimpleQTable):
                    # Calculate Q-table performance metrics
                    total_states = len(model.q_table)
                    total_actions = sum(len(actions) for actions in model.q_table.values())
                    avg_q_value = np.mean([max(q_values.values()) for q_values in model.q_table.values()]) if model.q_table else 0
                    
                    performance[agent.value] = {
                        "model_type": "q_table",
                        "total_states": total_states,
                        "total_actions": total_actions,
                        "average_q_value": avg_q_value,
                        "learning_rate": model.learning_rate,
                        "epsilon": model.epsilon
                    }
                else:
                    performance[agent.value] = {
                        "model_type": "stable_baselines3",
                        "model_class": type(model).__name__,
                        "status": "active"
                    }
        
        # Overall performance metrics
        total_episodes = len(self.episodes)
        recent_episodes = [ep for ep in self.episodes if (datetime.utcnow() - ep.timestamp).days < 7]
        
        performance["overall"] = {
            "total_episodes": total_episodes,
            "recent_episodes": len(recent_episodes),
            "learning_enabled": self.learning_enabled,
            "min_episodes_for_learning": self.min_episodes_for_learning
        }
        
        return performance
    
    async def update_learning_parameters(
        self,
        agent_type: AgentType,
        learning_rate: Optional[float] = None,
        epsilon: Optional[float] = None,
        discount_factor: Optional[float] = None
    ):
        """Update learning parameters for agent type."""
        if agent_type in self.agents and isinstance(self.agents[agent_type], SimpleQTable):
            q_table = self.agents[agent_type]
            
            if learning_rate is not None:
                q_table.learning_rate = learning_rate
            if epsilon is not None:
                q_table.epsilon = epsilon
            if discount_factor is not None:
                q_table.discount_factor = discount_factor
            
            logger.info(f"Updated learning parameters for {agent_type.value}",
                       learning_rate=q_table.learning_rate,
                       epsilon=q_table.epsilon,
                       discount_factor=q_table.discount_factor)
    
    async def reset_learning_model(self, agent_type: AgentType):
        """Reset learning model for agent type."""
        if agent_type in self.agents:
            if isinstance(self.agents[agent_type], SimpleQTable):
                self.agents[agent_type] = SimpleQTable()
            else:
                self.agents[agent_type] = self._create_stable_baselines_model(agent_type)
            
            logger.info(f"Reset learning model for {agent_type.value}")

# Global instance
_adaptive_rl_instance = None

def get_adaptive_reinforcement_learning(redis_client: Optional[redis.Redis] = None) -> AdaptiveReinforcementLearning:
    """Get global adaptive reinforcement learning instance."""
    global _adaptive_rl_instance
    if _adaptive_rl_instance is None:
        _adaptive_rl_instance = AdaptiveReinforcementLearning(redis_client)
    return _adaptive_rl_instance 
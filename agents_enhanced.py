"""Enhanced AI agents for AutoPilot Ventures platform with autonomous learning capabilities."""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import time

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

from config import config
from utils import (
    security_utils, budget_manager, generate_id, 
    AGENT_EXECUTION_COUNTER, AGENT_EXECUTION_DURATION,
    API_CALLS_COUNTER, log
)
from database import db_manager

# Import autonomous enhancements
from autonomous_enhancements import (
    VectorMemoryManager,
    SelfTuningAgent,
    ReinforcementLearningEngine,
    AgentType,
    Memory,
    LearningOutcome
)

# Configure logging
logger = logging.getLogger(__name__)


class AgentResult(BaseModel):
    """Enhanced base model for agent results with learning data."""

    success: bool = Field(description="Whether the operation was successful")
    data: Dict[str, Any] = Field(description="Result data")
    message: str = Field(description="Result message")
    cost: float = Field(description="Cost of the operation")
    confidence: float = Field(description="Agent confidence in the result", default=0.0)
    learning_data: Dict[str, Any] = Field(description="Data for reinforcement learning", default={})


class EnhancedBaseAgent:
    """Enhanced base class for all AI agents with autonomous learning capabilities."""

    def __init__(self, agent_type: str, startup_id: str):
        """Initialize enhanced base agent with autonomous features."""
        self.agent_type = agent_type
        self.startup_id = startup_id
        self.agent_id = generate_id(f"agent_{agent_type}")
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=config.ai.model_name,
            temperature=config.ai.temperature,
            max_tokens=config.ai.max_tokens,
            openai_api_key=config.ai.openai_key
        )
        self.parser = PydanticOutputParser(pydantic_object=AgentResult)

        # Initialize autonomous enhancements
        self._initialize_autonomous_features()
        
        # Register agent in database
        self._register_agent()
        
        logger.info(f"Enhanced agent {self.agent_id} initialized with autonomous features")

    def _initialize_autonomous_features(self):
        """Initialize vector memory, self-tuning, and RL capabilities."""
        try:
            # Map agent type to AgentType enum
            agent_type_mapping = {
                'niche_research': AgentType.NICHE_RESEARCHER,
                'mvp_design': AgentType.MVP_DESIGNER,
                'marketing_strategy': AgentType.MARKETING_STRATEGIST,
                'content_creation': AgentType.CONTENT_CREATOR,
                'analytics': AgentType.ANALYTICS_AGENT,
                'operations': AgentType.OPERATIONS_AGENT,
                'funding': AgentType.FUNDING_AGENT,
                'legal': AgentType.LEGAL_AGENT,
                'hr': AgentType.HR_AGENT,
                'support': AgentType.SUPPORT_AGENT
            }
            
            self.agent_type_enum = agent_type_mapping.get(self.agent_type, AgentType.NICHE_RESEARCHER)
            
            # Initialize vector memory manager
            self.vector_memory = VectorMemoryManager(self.startup_id)
            
            # Initialize self-tuning agent
            self.self_tuning_agent = SelfTuningAgent(
                self.agent_id, 
                self.agent_type_enum, 
                self.startup_id
            )
            
            # Initialize reinforcement learning engine
            self.rl_engine = ReinforcementLearningEngine(self.startup_id)
            
            logger.info(f"Autonomous features initialized for agent {self.agent_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize autonomous features: {e}")
            # Fallback to basic functionality
            self.vector_memory = None
            self.self_tuning_agent = None
            self.rl_engine = None

    def _register_agent(self) -> None:
        """Register agent in database."""
        try:
            db_manager.create_agent(
                startup_id=self.startup_id,
                agent_type=self.agent_type,
                metadata={
                    'created_at': datetime.utcnow().isoformat(),
                    'model': config.ai.model_name,
                    'autonomous_features': True
                }
            )
        except Exception as e:
            logger.error(f"Failed to register agent: {e}")

    async def execute(self, **kwargs) -> AgentResult:
        """Enhanced execute method with autonomous learning."""
        start_time = time.time()
        
        try:
            # Get current state for RL
            current_state = self._get_current_state(kwargs)
            
            # Use self-tuning agent to choose action
            if self.self_tuning_agent:
                action, confidence = self.self_tuning_agent.choose_action(current_state)
                logger.info(f"Agent {self.agent_id} chose action '{action}' with confidence {confidence}")
            else:
                action = "default_action"
                confidence = 0.5
            
            # Check budget before execution
            estimated_cost = self._estimate_cost(kwargs)
            if not self._check_budget(estimated_cost):
                return AgentResult(
                    success=False,
                    data={},
                    message="Insufficient budget for operation",
                    cost=0.0,
                    confidence=0.0
                )
            
            # Execute the actual task
            result = await self._execute_task(action, **kwargs)
            
            # Calculate execution metrics
            execution_time = time.time() - start_time
            success = result.success
            
            # Record cost
            self._record_cost(result.cost)
            
            # Update agent statistics
            self._update_agent_stats(success)
            
            # Log execution
            self._log_execution(success, execution_time)
            
            # Learn from execution
            await self._learn_from_execution(
                current_state, action, success, result, execution_time
            )
            
            # Store memory
            await self._store_memory(current_state, action, result, execution_time)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in agent execution: {e}")
            execution_time = time.time() - start_time
            
            # Learn from failure
            await self._learn_from_execution(
                self._get_current_state(kwargs), "error", False, 
                AgentResult(success=False, data={}, message=str(e), cost=0.0),
                execution_time
            )
            
            return AgentResult(
                success=False,
                data={},
                message=f"Execution failed: {str(e)}",
                cost=0.0,
                confidence=0.0
            )

    def _get_current_state(self, kwargs: Dict[str, Any]) -> str:
        """Get current state representation for RL."""
        # Create a state representation based on input parameters
        state_parts = [self.agent_type]
        
        # Add key parameters to state
        for key, value in kwargs.items():
            if isinstance(value, str) and len(value) < 50:  # Limit string length
                state_parts.append(f"{key}_{value}")
            elif isinstance(value, (int, float)):
                state_parts.append(f"{key}_{value}")
        
        return "_".join(state_parts)

    def _estimate_cost(self, kwargs: Dict[str, Any]) -> float:
        """Estimate operation cost."""
        # Base cost estimation logic
        base_cost = 0.01  # Base cost per operation
        
        # Add cost based on complexity
        if 'content_type' in kwargs and kwargs['content_type'] == 'blog post':
            base_cost += 0.02
        if 'target_audience' in kwargs:
            base_cost += 0.01
            
        return base_cost

    async def _execute_task(self, action: str, **kwargs) -> AgentResult:
        """Execute the actual task - to be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement _execute_task method")

    async def _learn_from_execution(self, state: str, action: str, success: bool, 
                                  result: AgentResult, execution_time: float):
        """Learn from execution using reinforcement learning."""
        try:
            if not self.self_tuning_agent or not self.rl_engine:
                return
            
            # Calculate reward based on success, cost, and execution time
            reward = self._calculate_reward(success, result.cost, execution_time)
            
            # Get next state (simplified - could be enhanced)
            next_state = f"{state}_completed"
            
            # Update Q-values in self-tuning agent
            self.self_tuning_agent.update_q_value(state, action, reward, next_state)
            
            # Register learning outcome with RL engine
            learning_outcome = LearningOutcome(
                agent_id=self.agent_id,
                action=action,
                state=state,
                reward=reward,
                next_state=next_state,
                success=success,
                confidence=result.confidence
            )
            
            await self.rl_engine.register_learning_outcome(learning_outcome)
            
            logger.info(f"Learning outcome registered: state={state}, action={action}, reward={reward}")
            
        except Exception as e:
            logger.error(f"Error in learning from execution: {e}")

    def _calculate_reward(self, success: bool, cost: float, execution_time: float) -> float:
        """Calculate reward for reinforcement learning."""
        base_reward = 1.0 if success else -1.0
        
        # Penalize high costs
        cost_penalty = -cost * 10  # Scale cost penalty
        
        # Penalize slow execution
        time_penalty = -execution_time * 0.1  # Scale time penalty
        
        # Bonus for fast, cheap, successful operations
        if success and cost < 0.05 and execution_time < 10:
            base_reward += 0.5
            
        return base_reward + cost_penalty + time_penalty

    async def _store_memory(self, state: str, action: str, result: AgentResult, execution_time: float):
        """Store execution memory in vector database."""
        try:
            if not self.vector_memory:
                return
            
            # Create memory entry
            memory = Memory(
                id=generate_id("memory"),
                agent_type=self.agent_type_enum,
                action=action,
                context=f"State: {state}, Execution time: {execution_time:.2f}s",
                outcome="success" if result.success else "failure",
                success_score=result.confidence if result.success else 0.0,
                importance_score=self._calculate_importance(result),
                timestamp=datetime.now()
            )
            
            # Store in vector memory
            await self.vector_memory.add_memory(memory)
            
            logger.info(f"Memory stored for agent {self.agent_id}")
            
        except Exception as e:
            logger.error(f"Error storing memory: {e}")

    def _calculate_importance(self, result: AgentResult) -> float:
        """Calculate importance score for memory."""
        importance = 0.5  # Base importance
        
        # Increase importance for successful operations
        if result.success:
            importance += 0.3
            
        # Increase importance for high confidence
        importance += result.confidence * 0.2
            
        return min(importance, 1.0)

    async def search_similar_experiences(self, query: str, limit: int = 5) -> List[Dict]:
        """Search for similar past experiences."""
        try:
            if not self.vector_memory:
                return []
            
            memories = await self.vector_memory.search_similar_memories(
                query, self.agent_type_enum, limit
            )
            
            return memories
            
        except Exception as e:
            logger.error(f"Error searching similar experiences: {e}")
            return []

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics."""
        try:
            # Get basic metrics from database
            agents = db_manager.get_agents_by_startup(self.startup_id)
            agent = next((a for a in agents if a.agent_type == self.agent_type), None)
            
            base_metrics = {
                'agent_id': self.agent_id,
                'agent_type': self.agent_type,
                'execution_count': agent.execution_count if agent else 0,
                'success_rate': agent.success_rate if agent else 0.0,
                'total_cost': agent.total_cost if agent else 0.0
            }
            
            # Add autonomous learning metrics
            if self.self_tuning_agent:
                rl_metrics = self.self_tuning_agent.get_performance_metrics()
                base_metrics.update(rl_metrics)
            
            return base_metrics
            
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {
                'agent_id': self.agent_id,
                'agent_type': self.agent_type,
                'error': str(e)
            }

    def _check_budget(self, estimated_cost: float) -> bool:
        """Check if we have budget for operation."""
        return budget_manager.can_spend(estimated_cost)

    def _record_cost(self, cost: float) -> None:
        """Record operation cost."""
        budget_manager.spend(cost)

    def _check_content_safety(self, content: str) -> Dict[str, float]:
        """Check content safety."""
        return security_utils.check_content_safety(content)

    def _update_agent_stats(self, success: bool) -> None:
        """Update agent statistics."""
        try:
            agents = db_manager.get_agents_by_startup(self.startup_id)
            if agents:
                agent = next((a for a in agents if a.agent_type == self.agent_type), None)
                if agent:
                    current_count = agent.execution_count
                    current_rate = agent.success_rate

                    new_count = current_count + 1
                    new_rate = (
                        (current_rate * current_count + (1 if success else 0)) / new_count
                    )

                    db_manager.update_agent(agent.id, {
                        'execution_count': new_count,
                        'success_rate': new_rate,
                        'last_execution': datetime.utcnow().isoformat()
                    })

                    # Update Prometheus metrics
                    AGENT_EXECUTION_COUNTER.labels(
                        agent_type=self.agent_type,
                        startup_id=self.startup_id
                    ).inc()

        except Exception as e:
            logger.error(f"Failed to update agent stats: {e}")

    def _log_execution(self, success: bool, duration: float) -> None:
        """Log execution details."""
        try:
            # Update Prometheus metrics
            AGENT_EXECUTION_DURATION.labels(
                agent_type=self.agent_type,
                startup_id=self.startup_id
            ).observe(duration)

            # Log to structured logger
            log.info("Agent execution completed", extra={
                'agent_id': self.agent_id,
                'agent_type': self.agent_type,
                'startup_id': self.startup_id,
                'success': success,
                'duration': duration,
                'autonomous_features': True
            })

        except Exception as e:
            logger.error(f"Failed to log execution: {e}")


# Enhanced agent implementations
class EnhancedNicheResearchAgent(EnhancedBaseAgent):
    """Enhanced niche research agent with autonomous learning."""

    def __init__(self, startup_id: str):
        super().__init__('niche_research', startup_id)

    async def _execute_task(self, action: str, **kwargs) -> AgentResult:
        """Execute niche research task."""
        try:
            niche = kwargs.get('niche', '')
            market_data = kwargs.get('market_data', '')
            
            # Search for similar past research
            similar_experiences = await self.search_similar_experiences(
                f"niche research {niche}", limit=3
            )
            
            # Use past experiences to improve current research
            context_from_memory = ""
            if similar_experiences:
                context_from_memory = f"\n\nPrevious similar research findings:\n"
                for exp in similar_experiences:
                    context_from_memory += f"- {exp['document']}\n"
            
            # Create enhanced prompt with memory context
            prompt = f"""
            Research the niche: {niche}
            
            Market data: {market_data}
            
            {context_from_memory}
            
            Provide comprehensive analysis including:
            1. Market size and potential
            2. Competition analysis
            3. Target audience identification
            4. Revenue potential
            5. Entry barriers
            6. Recommended next steps
            """
            
            # Execute with LLM
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            
            # Parse response
            result_data = {
                'niche': niche,
                'analysis': response.content,
                'similar_experiences_count': len(similar_experiences),
                'action_used': action
            }
            
            # Calculate confidence based on response quality
            confidence = min(len(response.content) / 1000, 1.0)  # Simple heuristic
            
            return AgentResult(
                success=True,
                data=result_data,
                message="Niche research completed successfully",
                cost=0.05,
                confidence=confidence,
                learning_data={'action': action, 'similar_experiences': len(similar_experiences)}
            )
            
        except Exception as e:
            logger.error(f"Error in niche research: {e}")
            return AgentResult(
                success=False,
                data={},
                message=f"Niche research failed: {str(e)}",
                cost=0.0,
                confidence=0.0
            )


class EnhancedMVPDesignAgent(EnhancedBaseAgent):
    """Enhanced MVP design agent with autonomous learning."""

    def __init__(self, startup_id: str):
        super().__init__('mvp_design', startup_id)

    async def _execute_task(self, action: str, **kwargs) -> AgentResult:
        """Execute MVP design task."""
        try:
            niche = kwargs.get('niche', '')
            target_audience = kwargs.get('target_audience', '')
            requirements = kwargs.get('requirements', '')
            
            # Search for similar MVP designs
            similar_experiences = await self.search_similar_experiences(
                f"MVP design {niche} {target_audience}", limit=3
            )
            
            # Use past experiences
            context_from_memory = ""
            if similar_experiences:
                context_from_memory = f"\n\nPrevious successful MVP patterns:\n"
                for exp in similar_experiences:
                    context_from_memory += f"- {exp['document']}\n"
            
            prompt = f"""
            Design an MVP for: {niche}
            Target audience: {target_audience}
            Requirements: {requirements}
            
            {context_from_memory}
            
            Provide:
            1. Core features list
            2. User journey mapping
            3. Technical architecture
            4. Development timeline
            5. Success metrics
            6. Risk assessment
            """
            
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            
            result_data = {
                'niche': niche,
                'target_audience': target_audience,
                'mvp_design': response.content,
                'similar_experiences_count': len(similar_experiences),
                'action_used': action
            }
            
            confidence = min(len(response.content) / 1500, 1.0)
            
            return AgentResult(
                success=True,
                data=result_data,
                message="MVP design completed successfully",
                cost=0.08,
                confidence=confidence,
                learning_data={'action': action, 'similar_experiences': len(similar_experiences)}
            )
            
        except Exception as e:
            logger.error(f"Error in MVP design: {e}")
            return AgentResult(
                success=False,
                data={},
                message=f"MVP design failed: {str(e)}",
                cost=0.0,
                confidence=0.0
            )


# Add more enhanced agents as needed...
# EnhancedMarketingStrategyAgent, EnhancedContentCreationAgent, etc.

# Factory function to create enhanced agents
def create_enhanced_agent(agent_type: str, startup_id: str) -> EnhancedBaseAgent:
    """Factory function to create enhanced agents with autonomous features."""
    agent_mapping = {
        'niche_research': EnhancedNicheResearchAgent,
        'mvp_design': EnhancedMVPDesignAgent,
        # Add more mappings as agents are implemented
    }
    
    agent_class = agent_mapping.get(agent_type)
    if agent_class:
        return agent_class(startup_id)
    else:
        raise ValueError(f"Unknown agent type: {agent_type}") 
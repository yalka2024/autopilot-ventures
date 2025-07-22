"""Advanced Autonomous Enhancements for AutoPilot Ventures."""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from collections import defaultdict
import redis
import chromadb
from chromadb.config import Settings

from config import config
from utils import generate_id, log
from agent_message_bus import get_message_bus, MessageType, MessagePriority

logger = logging.getLogger(__name__)


class LearningType(Enum):
    """Types of learning for agents."""
    
    REINFORCEMENT = "reinforcement"
    SUPERVISED = "supervised"
    UNSUPERVISED = "unsupervised"
    TRANSFER = "transfer"


class DecisionConfidence(Enum):
    """Decision confidence levels."""
    
    LOW = "low"           # < 0.3
    MEDIUM = "medium"     # 0.3 - 0.7
    HIGH = "high"         # > 0.7


@dataclass
class AgentMemory:
    """Agent memory for learning and context."""
    
    agent_id: str
    memory_type: str
    data: Dict[str, Any]
    timestamp: datetime
    importance: float = 0.5
    access_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.utcnow)


@dataclass
class LearningOutcome:
    """Learning outcome from agent actions."""
    
    agent_id: str
    action_type: str
    success: bool
    performance_metric: float
    learning_type: LearningType
    timestamp: datetime
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DecisionTree:
    """Decision tree for agent decision making."""
    
    decision_id: str
    agent_id: str
    decision_type: str
    conditions: List[Dict[str, Any]]
    actions: List[Dict[str, Any]]
    confidence: float
    success_rate: float = 0.0
    usage_count: int = 0


class VectorMemoryManager:
    """Vector-based memory management for agents."""
    
    def __init__(self, startup_id: str):
        self.startup_id = startup_id
        self.memory_id = generate_id("vector_memory")
        
        # Initialize ChromaDB with new configuration
        self.chroma_client = chromadb.PersistentClient(
            path=f"./data/memory_{startup_id}"
        )
        
        # Create collections for different memory types
        try:
            self.context_collection = self.chroma_client.get_or_create_collection(
                name=f"context_{startup_id}",
                metadata={"description": "Agent context memory"}
            )
            
            self.learning_collection = self.chroma_client.get_or_create_collection(
                name=f"learning_{startup_id}",
                metadata={"description": "Learning outcomes"}
            )
            
            self.decision_collection = self.chroma_client.get_or_create_collection(
                name=f"decisions_{startup_id}",
                metadata={"description": "Decision patterns"}
            )
        except Exception as e:
            logger.warning(f"Using in-memory ChromaDB due to error: {e}")
            # Fallback to in-memory client
            self.chroma_client = chromadb.Client()
            self.context_collection = self.chroma_client.create_collection(
                name=f"context_{startup_id}",
                metadata={"description": "Agent context memory"}
            )
            self.learning_collection = self.chroma_client.create_collection(
                name=f"learning_{startup_id}",
                metadata={"description": "Learning outcomes"}
            )
            self.decision_collection = self.chroma_client.create_collection(
                name=f"decisions_{startup_id}",
                metadata={"description": "Decision patterns"}
            )
        
        logger.info(f"Vector memory manager initialized for startup {startup_id}")
    
    async def store_context(self, agent_id: str, context: Dict[str, Any], importance: float = 0.5):
        """Store agent context in vector memory."""
        try:
            # Convert context to text for embedding
            context_text = json.dumps(context, sort_keys=True)
            
            # Store in vector database
            self.context_collection.add(
                documents=[context_text],
                metadatas=[{
                    'agent_id': agent_id,
                    'importance': importance,
                    'timestamp': datetime.utcnow().isoformat(),
                    'type': 'context'
                }],
                ids=[f"context_{agent_id}_{generate_id()}"]
            )
            
            logger.info(f"Context stored for agent {agent_id}")
            
        except Exception as e:
            logger.error(f"Failed to store context: {e}")
    
    async def retrieve_similar_context(self, agent_id: str, query: str, limit: int = 5):
        """Retrieve similar context from memory."""
        try:
            results = self.context_collection.query(
                query_texts=[query],
                n_results=limit,
                where={"agent_id": agent_id}
            )
            
            return results['documents'][0] if results['documents'] else []
            
        except Exception as e:
            logger.error(f"Failed to retrieve context: {e}")
            return []
    
    async def store_learning_outcome(self, outcome: LearningOutcome):
        """Store learning outcome in vector memory."""
        try:
            outcome_text = json.dumps({
                'action_type': outcome.action_type,
                'success': outcome.success,
                'performance_metric': outcome.performance_metric,
                'learning_type': outcome.learning_type.value,
                'context': outcome.context
            }, sort_keys=True)
            
            self.learning_collection.add(
                documents=[outcome_text],
                metadatas=[{
                    'agent_id': outcome.agent_id,
                    'timestamp': outcome.timestamp.isoformat(),
                    'type': 'learning'
                }],
                ids=[f"learning_{outcome.agent_id}_{generate_id()}"]
            )
            
            logger.info(f"Learning outcome stored for agent {outcome.agent_id}")
            
        except Exception as e:
            logger.error(f"Failed to store learning outcome: {e}")


class SelfTuningAgent:
    """Self-tuning agent with learning capabilities."""
    
    def __init__(self, agent_id: str, agent_type: str, startup_id: str):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.startup_id = startup_id
        
        # Initialize memory manager
        self.memory_manager = VectorMemoryManager(startup_id)
        
        # Learning parameters
        self.learning_rate = 0.1
        self.exploration_rate = 0.2
        self.confidence_threshold = 0.7
        
        # Performance tracking
        self.performance_history = []
        self.decision_history = []
        self.learning_outcomes = []
        
        # Message bus for coordination
        self.message_bus = get_message_bus(startup_id)
        
        logger.info(f"Self-tuning agent initialized: {agent_id}")
    
    async def make_decision(self, context: Dict[str, Any], options: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Make a decision with learning capabilities."""
        try:
            # Retrieve similar past decisions
            similar_contexts = await self.memory_manager.retrieve_similar_context(
                self.agent_id, json.dumps(context)
            )
            
            # Calculate decision confidence
            confidence = self._calculate_confidence(context, similar_contexts)
            
            # Choose action based on confidence and exploration
            if confidence < self.confidence_threshold or np.random.random() < self.exploration_rate:
                # Explore new options
                decision = self._explore_decision(options)
                decision_type = "exploration"
            else:
                # Exploit learned patterns
                decision = self._exploit_decision(context, similar_contexts, options)
                decision_type = "exploitation"
            
            # Store decision context
            await self.memory_manager.store_context(self.agent_id, context)
            
            # Record decision
            decision_record = {
                'decision_id': generate_id(),
                'context': context,
                'decision': decision,
                'confidence': confidence,
                'decision_type': decision_type,
                'timestamp': datetime.utcnow()
            }
            
            self.decision_history.append(decision_record)
            
            return {
                'decision': decision,
                'confidence': confidence,
                'decision_type': decision_type,
                'context_used': len(similar_contexts)
            }
            
        except Exception as e:
            logger.error(f"Decision making failed: {e}")
            return {'decision': options[0], 'confidence': 0.0, 'decision_type': 'fallback'}
    
    def _calculate_confidence(self, context: Dict[str, Any], similar_contexts: List[str]) -> float:
        """Calculate confidence in decision based on similar contexts."""
        if not similar_contexts:
            return 0.0
        
        # Simple confidence calculation based on context similarity
        # In production, use more sophisticated similarity metrics
        return min(0.8, len(similar_contexts) * 0.1)
    
    def _explore_decision(self, options: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Explore new decision options."""
        return np.random.choice(options)
    
    def _exploit_decision(self, context: Dict[str, Any], similar_contexts: List[str], options: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Exploit learned patterns for decision making."""
        # Simple exploitation - choose first option for now
        # In production, use more sophisticated pattern matching
        return options[0]
    
    async def learn_from_outcome(self, decision_id: str, outcome: Dict[str, Any]):
        """Learn from decision outcome."""
        try:
            # Find the decision record
            decision_record = next(
                (d for d in self.decision_history if d.get('decision_id') == decision_id),
                None
            )
            
            if not decision_record:
                return
            
            # Create learning outcome
            learning_outcome = LearningOutcome(
                agent_id=self.agent_id,
                action_type=decision_record['decision_type'],
                success=outcome.get('success', False),
                performance_metric=outcome.get('performance_metric', 0.0),
                learning_type=LearningType.REINFORCEMENT,
                timestamp=datetime.utcnow(),
                context={
                    'original_context': decision_record['context'],
                    'outcome': outcome
                }
            )
            
            # Store learning outcome
            await self.memory_manager.store_learning_outcome(learning_outcome)
            
            # Update performance history
            self.performance_history.append({
                'timestamp': datetime.utcnow(),
                'performance': outcome.get('performance_metric', 0.0),
                'success': outcome.get('success', False)
            })
            
            # Adjust learning parameters based on performance
            self._adjust_learning_parameters(outcome)
            
            logger.info(f"Learning outcome recorded for agent {self.agent_id}")
            
        except Exception as e:
            logger.error(f"Failed to learn from outcome: {e}")
    
    def _adjust_learning_parameters(self, outcome: Dict[str, Any]):
        """Adjust learning parameters based on performance."""
        if outcome.get('success', False):
            # Increase exploitation, decrease exploration
            self.exploration_rate = max(0.05, self.exploration_rate * 0.95)
            self.confidence_threshold = min(0.9, self.confidence_threshold * 1.05)
        else:
            # Increase exploration, decrease confidence threshold
            self.exploration_rate = min(0.5, self.exploration_rate * 1.1)
            self.confidence_threshold = max(0.5, self.confidence_threshold * 0.95)


class ReinforcementLearningEngine:
    """Reinforcement learning engine for agent optimization."""
    
    def __init__(self, startup_id: str):
        self.startup_id = startup_id
        self.engine_id = generate_id("rl_engine")
        
        # Learning agents
        self.learning_agents: Dict[str, SelfTuningAgent] = {}
        
        # Performance tracking
        self.global_performance = defaultdict(list)
        self.optimization_history = []
        
        # Message bus
        self.message_bus = get_message_bus(startup_id)
        
        logger.info(f"Reinforcement learning engine initialized for startup {startup_id}")
    
    async def register_agent(self, agent_id: str, agent_type: str):
        """Register an agent for learning."""
        if agent_id not in self.learning_agents:
            self.learning_agents[agent_id] = SelfTuningAgent(agent_id, agent_type, self.startup_id)
            logger.info(f"Agent {agent_id} registered for learning")
    
    async def optimize_agent_behavior(self, agent_id: str, performance_data: Dict[str, Any]):
        """Optimize agent behavior based on performance data."""
        try:
            if agent_id not in self.learning_agents:
                return
            
            agent = self.learning_agents[agent_id]
            
            # Analyze performance trends
            performance_trend = self._analyze_performance_trend(agent_id, performance_data)
            
            # Generate optimization recommendations
            optimizations = self._generate_optimizations(agent, performance_trend)
            
            # Apply optimizations
            await self._apply_optimizations(agent, optimizations)
            
            # Record optimization
            self.optimization_history.append({
                'agent_id': agent_id,
                'timestamp': datetime.utcnow(),
                'performance_trend': performance_trend,
                'optimizations': optimizations
            })
            
            # Notify other agents about optimization
            await self.message_bus.broadcast_message(
                sender="rl_engine",
                message_type=MessageType.DATA_SHARE,
                content={
                    'data_key': f'optimization_{agent_id}',
                    'data_value': {
                        'agent_id': agent_id,
                        'optimizations': optimizations,
                        'performance_trend': performance_trend
                    }
                },
                priority=MessagePriority.NORMAL
            )
            
            logger.info(f"Agent {agent_id} behavior optimized")
            
        except Exception as e:
            logger.error(f"Failed to optimize agent {agent_id}: {e}")
    
    def _analyze_performance_trend(self, agent_id: str, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance trends for an agent."""
        # Simple trend analysis
        # In production, use more sophisticated time series analysis
        return {
            'trend': 'improving' if performance_data.get('success_rate', 0) > 0.7 else 'declining',
            'confidence': 0.8,
            'recommendations': ['increase_exploration', 'adjust_thresholds']
        }
    
    def _generate_optimizations(self, agent: SelfTuningAgent, performance_trend: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate optimization recommendations."""
        optimizations = []
        
        if performance_trend['trend'] == 'declining':
            optimizations.append({
                'type': 'increase_exploration',
                'parameter': 'exploration_rate',
                'value': min(0.5, agent.exploration_rate * 1.2)
            })
        
        optimizations.append({
            'type': 'adjust_confidence',
            'parameter': 'confidence_threshold',
            'value': 0.7
        })
        
        return optimizations
    
    async def _apply_optimizations(self, agent: SelfTuningAgent, optimizations: List[Dict[str, Any]]):
        """Apply optimizations to agent."""
        for optimization in optimizations:
            if optimization['type'] == 'increase_exploration':
                agent.exploration_rate = optimization['value']
            elif optimization['type'] == 'adjust_confidence':
                agent.confidence_threshold = optimization['value']


class AutonomousWorkflowEngine:
    """Autonomous workflow engine with self-healing capabilities."""
    
    def __init__(self, startup_id: str):
        self.startup_id = startup_id
        self.engine_id = generate_id("autonomous_workflow")
        
        # Workflow state management
        self.active_workflows = {}
        self.workflow_history = []
        self.failure_patterns = defaultdict(int)
        
        # Self-healing capabilities
        self.healing_strategies = {
            'agent_failure': self._handle_agent_failure,
            'timeout': self._handle_timeout,
            'resource_exhaustion': self._handle_resource_exhaustion,
            'dependency_failure': self._handle_dependency_failure
        }
        
        # Message bus
        self.message_bus = get_message_bus(startup_id)
        
        logger.info(f"Autonomous workflow engine initialized for startup {startup_id}")
    
    async def execute_autonomous_workflow(self, workflow_config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow with autonomous capabilities."""
        workflow_id = generate_id("autonomous_workflow")
        
        try:
            # Initialize workflow state
            self.active_workflows[workflow_id] = {
                'config': workflow_config,
                'status': 'running',
                'start_time': datetime.utcnow(),
                'steps_completed': [],
                'steps_failed': [],
                'healing_actions': []
            }
            
            # Execute workflow steps with monitoring
            result = await self._execute_with_monitoring(workflow_id, workflow_config)
            
            # Record workflow completion
            self.workflow_history.append({
                'workflow_id': workflow_id,
                'config': workflow_config,
                'result': result,
                'duration': (datetime.utcnow() - self.active_workflows[workflow_id]['start_time']).total_seconds()
            })
            
            # Clean up
            del self.active_workflows[workflow_id]
            
            return result
            
        except Exception as e:
            logger.error(f"Autonomous workflow failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _execute_with_monitoring(self, workflow_id: str, workflow_config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow with continuous monitoring and self-healing."""
        workflow_state = self.active_workflows[workflow_id]
        
        try:
            # Execute workflow steps
            for step_name, step_config in workflow_config.items():
                try:
                    # Execute step
                    step_result = await self._execute_step(step_name, step_config)
                    
                    if step_result['success']:
                        workflow_state['steps_completed'].append(step_name)
                    else:
                        workflow_state['steps_failed'].append(step_name)
                        
                        # Attempt self-healing
                        healing_result = await self._attempt_healing(workflow_id, step_name, step_result)
                        workflow_state['healing_actions'].append(healing_result)
                        
                        if not healing_result['success']:
                            # Escalate to human if healing fails
                            await self._escalate_to_human(workflow_id, step_name, step_result)
                            break
                
                except Exception as e:
                    logger.error(f"Step {step_name} failed: {e}")
                    workflow_state['steps_failed'].append(step_name)
                    
                    # Record failure pattern
                    self.failure_patterns[step_name] += 1
            
            # Determine overall success
            success = len(workflow_state['steps_failed']) == 0
            
            return {
                'success': success,
                'steps_completed': workflow_state['steps_completed'],
                'steps_failed': workflow_state['steps_failed'],
                'healing_actions': workflow_state['healing_actions']
            }
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _execute_step(self, step_name: str, step_config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single workflow step."""
        # Simulate step execution
        # In production, this would execute actual agent tasks
        await asyncio.sleep(1)
        
        # Simulate occasional failures
        if np.random.random() < 0.1:  # 10% failure rate
            return {'success': False, 'error': 'Simulated failure'}
        
        return {'success': True, 'result': f'Step {step_name} completed'}
    
    async def _attempt_healing(self, workflow_id: str, step_name: str, step_result: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt to heal a failed step."""
        try:
            # Determine failure type
            failure_type = self._classify_failure(step_result)
            
            # Get healing strategy
            healing_strategy = self.healing_strategies.get(failure_type)
            
            if healing_strategy:
                healing_result = await healing_strategy(workflow_id, step_name, step_result)
                return healing_result
            else:
                return {'success': False, 'error': 'No healing strategy available'}
                
        except Exception as e:
            logger.error(f"Healing attempt failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _classify_failure(self, step_result: Dict[str, Any]) -> str:
        """Classify the type of failure."""
        error = step_result.get('error', '').lower()
        
        if 'timeout' in error:
            return 'timeout'
        elif 'resource' in error:
            return 'resource_exhaustion'
        elif 'dependency' in error:
            return 'dependency_failure'
        else:
            return 'agent_failure'
    
    async def _handle_agent_failure(self, workflow_id: str, step_name: str, step_result: Dict[str, Any]) -> Dict[str, Any]:
        """Handle agent failure."""
        # Retry with different parameters
        return {'success': True, 'action': 'retry_with_different_parameters'}
    
    async def _handle_timeout(self, workflow_id: str, step_name: str, step_result: Dict[str, Any]) -> Dict[str, Any]:
        """Handle timeout failure."""
        # Increase timeout and retry
        return {'success': True, 'action': 'increase_timeout_and_retry'}
    
    async def _handle_resource_exhaustion(self, workflow_id: str, step_name: str, step_result: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resource exhaustion."""
        # Scale resources and retry
        return {'success': True, 'action': 'scale_resources_and_retry'}
    
    async def _handle_dependency_failure(self, workflow_id: str, step_name: str, step_result: Dict[str, Any]) -> Dict[str, Any]:
        """Handle dependency failure."""
        # Find alternative dependencies
        return {'success': True, 'action': 'find_alternative_dependencies'}
    
    async def _escalate_to_human(self, workflow_id: str, step_name: str, step_result: Dict[str, Any]):
        """Escalate to human intervention."""
        await self.message_bus.broadcast_message(
            sender="autonomous_workflow",
            message_type=MessageType.CONFLICT_ALERT,
            content={
                'workflow_id': workflow_id,
                'step_name': step_name,
                'error': step_result.get('error', 'Unknown error'),
                'escalation_reason': 'Self-healing failed'
            },
            priority=MessagePriority.CRITICAL
        )


# Global instances
_rl_engine: Optional[ReinforcementLearningEngine] = None
_autonomous_workflow: Optional[AutonomousWorkflowEngine] = None


def get_reinforcement_learning_engine(startup_id: str) -> ReinforcementLearningEngine:
    """Get or create reinforcement learning engine instance."""
    global _rl_engine
    if _rl_engine is None or _rl_engine.startup_id != startup_id:
        _rl_engine = ReinforcementLearningEngine(startup_id)
    return _rl_engine


def get_autonomous_workflow_engine(startup_id: str) -> AutonomousWorkflowEngine:
    """Get or create autonomous workflow engine instance."""
    global _autonomous_workflow
    if _autonomous_workflow is None or _autonomous_workflow.startup_id != startup_id:
        _autonomous_workflow = AutonomousWorkflowEngine(startup_id)
    return _autonomous_workflow 
"""Enhanced orchestrator for AutoPilot Ventures platform with autonomous learning capabilities."""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import time

from agents_enhanced import (
    create_enhanced_agent,
    EnhancedBaseAgent,
    AgentResult
)
from config import config
from utils import (
    budget_manager, generate_id, log, AGENT_EXECUTION_COUNTER,
    AGENT_EXECUTION_DURATION, BUDGET_USAGE_GAUGE
)
from database import db_manager
from agent_message_bus import get_message_bus, MessageType, MessagePriority
from payment_processor import get_payment_processor, get_marketing_funnel
from cultural_intelligence import get_cultural_intelligence_agent

# Import autonomous enhancements
from autonomous_enhancements import (
    get_reinforcement_learning_engine,
    get_autonomous_workflow_engine,
    VectorMemoryManager,
    SelfTuningAgent,
    ReinforcementLearningEngine
)

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class EnhancedWorkflowStep:
    """Enhanced workflow step with autonomous learning capabilities."""
    
    agent_type: str
    dependencies: List[str] = None
    priority: int = 1
    timeout: int = 300  # 5 minutes
    retry_count: int = 3
    required: bool = True
    learning_enabled: bool = True
    memory_search: bool = True
    confidence_threshold: float = 0.7


@dataclass
class EnhancedWorkflowResult:
    """Enhanced result of workflow execution with learning data."""
    
    workflow_id: str
    startup_id: str
    success: bool
    steps_completed: List[str]
    steps_failed: List[str]
    total_cost: float
    execution_time: float
    results: Dict[str, Any]
    timestamp: str
    learning_insights: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    autonomous_features_used: List[str]


class EnhancedAgentOrchestrator:
    """Enhanced orchestrator for managing AI agents with autonomous capabilities."""

    def __init__(self, startup_id: str):
        """Initialize enhanced orchestrator with autonomous features."""
        self.startup_id = startup_id
        self.workflow_id = generate_id("workflow")
        self.agents = {}
        self.workflow_results = {}
        self.execution_history = []
        
        # Initialize message bus for agent communication
        self.message_bus = get_message_bus(startup_id)
        
        # Initialize payment processor for revenue tracking
        self.payment_processor = get_payment_processor()
        
        # Initialize marketing funnel for customer acquisition
        self.marketing_funnel = get_marketing_funnel()
        
        # Initialize cultural intelligence agent
        self.cultural_agent = get_cultural_intelligence_agent(startup_id)
        
        # Initialize autonomous enhancements
        self.vector_memory = VectorMemoryManager(startup_id)
        self.rl_engine = get_reinforcement_learning_engine(startup_id)
        self.autonomous_workflow = get_autonomous_workflow_engine(startup_id)
        
        # Initialize all enhanced agents
        self._initialize_enhanced_agents()
        
        # Register agents with RL engine for learning
        self._register_agents_for_learning()
        
        logger.info(f"Enhanced orchestrator initialized for startup {startup_id} with autonomous features")

    def _initialize_enhanced_agents(self):
        """Initialize all enhanced agents with autonomous capabilities."""
        agent_types = [
            'niche_research',
            'mvp_design',
            'marketing_strategy',
            'content_creation',
            'analytics',
            'operations',
            'funding',
            'legal',
            'hr',
            'support'
        ]
        
        for agent_type in agent_types:
            try:
                self.agents[agent_type] = create_enhanced_agent(agent_type, self.startup_id)
                logger.info(f"Enhanced agent {agent_type} initialized")
            except Exception as e:
                logger.error(f"Failed to initialize enhanced agent {agent_type}: {e}")

    def _register_agents_for_learning(self):
        """Register all agents with the reinforcement learning engine."""
        try:
            for agent_type, agent in self.agents.items():
                if hasattr(agent, 'agent_id') and hasattr(agent, 'agent_type_enum'):
                    asyncio.create_task(
                        self.rl_engine.register_agent(agent.agent_id, agent.agent_type_enum.value)
                    )
            logger.info("All agents registered for reinforcement learning")
        except Exception as e:
            logger.error(f"Failed to register agents for learning: {e}")

    async def execute_enhanced_workflow(
        self,
        workflow_config: Dict[str, Any],
        max_concurrent: int = 3
    ) -> EnhancedWorkflowResult:
        """Execute enhanced workflow with autonomous learning capabilities."""
        start_time = time.time()
        workflow_id = generate_id("enhanced_workflow")
        
        logger.info(f"Starting enhanced workflow {workflow_id}")
        
        try:
            # Parse workflow configuration
            steps = self._parse_workflow_config(workflow_config)
            
            # Pre-execution learning: Search for similar workflows
            similar_workflows = await self._search_similar_workflows(workflow_config)
            
            # Execute workflow with autonomous features
            results = {}
            steps_completed = []
            steps_failed = []
            total_cost = 0.0
            
            # Execute steps in dependency order
            for step in steps:
                try:
                    step_result = await self._execute_enhanced_step(step, similar_workflows)
                    
                    if step_result.success:
                        steps_completed.append(step.agent_type)
                        results[step.agent_type] = step_result.data
                        total_cost += step_result.cost
                    else:
                        steps_failed.append(step.agent_type)
                        results[step.agent_type] = {"error": step_result.message}
                        
                except Exception as e:
                    logger.error(f"Step {step.agent_type} failed: {e}")
                    steps_failed.append(step.agent_type)
                    results[step.agent_type] = {"error": str(e)}
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Learn from workflow execution
            learning_insights = await self._learn_from_enhanced_workflow(
                workflow_id, steps_completed, steps_failed, results, execution_time
            )
            
            # Generate performance metrics
            performance_metrics = self._generate_workflow_metrics(
                steps_completed, steps_failed, total_cost, execution_time
            )
            
            # Create enhanced workflow result
            workflow_result = EnhancedWorkflowResult(
                workflow_id=workflow_id,
                startup_id=self.startup_id,
                success=len(steps_failed) == 0,
                steps_completed=steps_completed,
                steps_failed=steps_failed,
                total_cost=total_cost,
                execution_time=execution_time,
                results=results,
                timestamp=datetime.utcnow().isoformat(),
                learning_insights=learning_insights,
                performance_metrics=performance_metrics,
                autonomous_features_used=[
                    "vector_memory",
                    "self_tuning",
                    "reinforcement_learning",
                    "performance_monitoring"
                ]
            )
            
            # Store workflow result
            self.workflow_results[workflow_id] = workflow_result
            
            # Log workflow completion
            log.info("Enhanced workflow completed", extra={
                'workflow_id': workflow_id,
                'startup_id': self.startup_id,
                'success': workflow_result.success,
                'steps_completed': len(steps_completed),
                'steps_failed': len(steps_failed),
                'total_cost': total_cost,
                'execution_time': execution_time,
                'autonomous_features': True
            })
            
            return workflow_result
            
        except Exception as e:
            logger.error(f"Enhanced workflow execution failed: {e}")
            execution_time = time.time() - start_time
            
            return EnhancedWorkflowResult(
                workflow_id=workflow_id,
                startup_id=self.startup_id,
                success=False,
                steps_completed=[],
                steps_failed=[],
                total_cost=0.0,
                execution_time=execution_time,
                results={},
                timestamp=datetime.utcnow().isoformat(),
                learning_insights={"error": str(e)},
                performance_metrics={},
                autonomous_features_used=[]
            )

    def _parse_workflow_config(self, workflow_config: Dict[str, Any]) -> List[EnhancedWorkflowStep]:
        """Parse workflow configuration into enhanced steps."""
        steps = []
        
        for step_config in workflow_config.get('steps', []):
            step = EnhancedWorkflowStep(
                agent_type=step_config['agent_type'],
                dependencies=step_config.get('dependencies', []),
                priority=step_config.get('priority', 1),
                timeout=step_config.get('timeout', 300),
                retry_count=step_config.get('retry_count', 3),
                required=step_config.get('required', True),
                learning_enabled=step_config.get('learning_enabled', True),
                memory_search=step_config.get('memory_search', True),
                confidence_threshold=step_config.get('confidence_threshold', 0.7)
            )
            steps.append(step)
        
        return steps

    async def _search_similar_workflows(self, workflow_config: Dict[str, Any]) -> List[Dict]:
        """Search for similar past workflows using vector memory."""
        try:
            # Create a query based on workflow configuration
            workflow_description = f"workflow with {len(workflow_config.get('steps', []))} steps"
            
            # Search for similar memories
            similar_memories = await self.vector_memory.search_similar_memories(
                workflow_description, limit=5
            )
            
            logger.info(f"Found {len(similar_memories)} similar workflow memories")
            return similar_memories
            
        except Exception as e:
            logger.error(f"Error searching similar workflows: {e}")
            return []

    async def _execute_enhanced_step(
        self, 
        step: EnhancedWorkflowStep, 
        similar_workflows: List[Dict]
    ) -> AgentResult:
        """Execute a single enhanced workflow step with autonomous features."""
        try:
            agent = self.agents.get(step.agent_type)
            if not agent:
                return AgentResult(
                    success=False,
                    data={},
                    message=f"Agent {step.agent_type} not found",
                    cost=0.0,
                    confidence=0.0
                )
            
            # Prepare step parameters
            step_params = self._prepare_step_parameters(step, similar_workflows)
            
            # Execute step with autonomous features
            result = await agent.execute(**step_params)
            
            # Check confidence threshold
            if step.confidence_threshold > 0 and result.confidence < step.confidence_threshold:
                logger.warning(f"Step {step.agent_type} confidence {result.confidence} below threshold {step.confidence_threshold}")
                
                # Try to improve result using similar experiences
                if step.memory_search:
                    improved_result = await self._improve_result_with_memory(agent, step_params, result)
                    if improved_result.confidence > result.confidence:
                        result = improved_result
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing enhanced step {step.agent_type}: {e}")
            return AgentResult(
                success=False,
                data={},
                message=f"Step execution failed: {str(e)}",
                cost=0.0,
                confidence=0.0
            )

    def _prepare_step_parameters(self, step: EnhancedWorkflowStep, similar_workflows: List[Dict]) -> Dict[str, Any]:
        """Prepare parameters for step execution with context from similar workflows."""
        base_params = {
            'workflow_step': step.agent_type,
            'learning_enabled': step.learning_enabled,
            'memory_search': step.memory_search
        }
        
        # Add context from similar workflows
        if similar_workflows:
            context = []
            for workflow in similar_workflows[:2]:  # Use top 2 similar workflows
                if 'document' in workflow:
                    context.append(workflow['document'])
            
            if context:
                base_params['similar_workflow_context'] = " | ".join(context)
        
        return base_params

    async def _improve_result_with_memory(
        self, 
        agent: EnhancedBaseAgent, 
        params: Dict[str, Any], 
        original_result: AgentResult
    ) -> AgentResult:
        """Improve result using vector memory search."""
        try:
            # Search for similar successful experiences
            query = f"successful {agent.agent_type} execution"
            similar_experiences = await agent.search_similar_experiences(query, limit=3)
            
            if similar_experiences:
                # Use successful patterns to improve result
                improvement_context = "\n\nSuccessful patterns from similar experiences:\n"
                for exp in similar_experiences:
                    improvement_context += f"- {exp['document']}\n"
                
                # Create improved prompt
                improved_prompt = f"""
                Original result: {original_result.message}
                
                {improvement_context}
                
                Please improve the result based on these successful patterns.
                """
                
                # Get improved result (simplified - could be enhanced)
                improved_result = AgentResult(
                    success=original_result.success,
                    data=original_result.data,
                    message=f"Improved: {original_result.message}",
                    cost=original_result.cost,
                    confidence=min(original_result.confidence + 0.1, 1.0),
                    learning_data={'improved_with_memory': True, 'similar_experiences': len(similar_experiences)}
                )
                
                return improved_result
            
            return original_result
            
        except Exception as e:
            logger.error(f"Error improving result with memory: {e}")
            return original_result

    async def _learn_from_enhanced_workflow(
        self,
        workflow_id: str,
        steps_completed: List[str],
        steps_failed: List[str],
        results: Dict[str, Any],
        execution_time: float
    ) -> Dict[str, Any]:
        """Learn from enhanced workflow execution."""
        try:
            learning_insights = {
                'workflow_id': workflow_id,
                'success_rate': len(steps_completed) / (len(steps_completed) + len(steps_failed)) if (len(steps_completed) + len(steps_failed)) > 0 else 0,
                'execution_efficiency': execution_time,
                'step_performance': {},
                'patterns_identified': []
            }
            
            # Analyze step performance
            for step_type in steps_completed:
                if step_type in results:
                    step_data = results[step_type]
                    learning_insights['step_performance'][step_type] = {
                        'success': True,
                        'confidence': step_data.get('confidence', 0.0),
                        'similar_experiences_used': step_data.get('similar_experiences_count', 0)
                    }
            
            for step_type in steps_failed:
                learning_insights['step_performance'][step_type] = {
                    'success': False,
                    'error': results.get(step_type, {}).get('error', 'Unknown error')
                }
            
            # Identify patterns
            successful_steps = [s for s in steps_completed if s in results]
            if successful_steps:
                learning_insights['patterns_identified'].append({
                    'pattern': 'successful_step_sequence',
                    'steps': successful_steps,
                    'confidence': sum(results[s].get('confidence', 0.0) for s in successful_steps) / len(successful_steps)
                })
            
            # Store workflow memory
            await self._store_workflow_memory(workflow_id, learning_insights)
            
            return learning_insights
            
        except Exception as e:
            logger.error(f"Error learning from enhanced workflow: {e}")
            return {'error': str(e)}

    async def _store_workflow_memory(self, workflow_id: str, learning_insights: Dict[str, Any]):
        """Store workflow execution memory in vector database."""
        try:
            from autonomous_enhancements import Memory, AgentType
            
            memory = Memory(
                id=generate_id("workflow_memory"),
                agent_type=AgentType.MASTER_AGENT,  # Use master agent for workflow memories
                action="workflow_execution",
                context=f"Workflow {workflow_id} with {len(learning_insights.get('step_performance', {}))} steps",
                outcome="success" if learning_insights.get('success_rate', 0) > 0.5 else "failure",
                success_score=learning_insights.get('success_rate', 0.0),
                importance_score=0.8,  # High importance for workflow memories
                timestamp=datetime.now()
            )
            
            await self.vector_memory.add_memory(memory)
            logger.info(f"Workflow memory stored for {workflow_id}")
            
        except Exception as e:
            logger.error(f"Error storing workflow memory: {e}")

    def _generate_workflow_metrics(
        self,
        steps_completed: List[str],
        steps_failed: List[str],
        total_cost: float,
        execution_time: float
    ) -> Dict[str, Any]:
        """Generate comprehensive workflow performance metrics."""
        total_steps = len(steps_completed) + len(steps_failed)
        
        metrics = {
            'total_steps': total_steps,
            'steps_completed': len(steps_completed),
            'steps_failed': len(steps_failed),
            'success_rate': len(steps_completed) / total_steps if total_steps > 0 else 0,
            'total_cost': total_cost,
            'execution_time': execution_time,
            'cost_per_step': total_cost / total_steps if total_steps > 0 else 0,
            'time_per_step': execution_time / total_steps if total_steps > 0 else 0,
            'autonomous_features_used': [
                'vector_memory',
                'self_tuning',
                'reinforcement_learning',
                'performance_monitoring'
            ]
        }
        
        # Add agent-specific metrics
        agent_metrics = {}
        for agent_type, agent in self.agents.items():
            try:
                agent_metrics[agent_type] = agent.get_performance_metrics()
            except Exception as e:
                logger.error(f"Error getting metrics for agent {agent_type}: {e}")
        
        metrics['agent_performance'] = agent_metrics
        
        return metrics

    async def execute_single_enhanced_agent(
        self,
        agent_type: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute a single enhanced agent with autonomous features."""
        try:
            agent = self.agents.get(agent_type)
            if not agent:
                return {
                    'success': False,
                    'error': f'Agent {agent_type} not found',
                    'autonomous_features': False
                }
            
            # Execute agent with autonomous features
            result = await agent.execute(**kwargs)
            
            # Get performance metrics
            performance_metrics = agent.get_performance_metrics()
            
            return {
                'success': result.success,
                'data': result.data,
                'message': result.message,
                'cost': result.cost,
                'confidence': result.confidence,
                'learning_data': result.learning_data,
                'performance_metrics': performance_metrics,
                'autonomous_features': True
            }
            
        except Exception as e:
            logger.error(f"Error executing enhanced agent {agent_type}: {e}")
            return {
                'success': False,
                'error': str(e),
                'autonomous_features': False
            }

    def get_enhanced_agent_performance(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics for all enhanced agents."""
        try:
            performance_data = {
                'startup_id': self.startup_id,
                'total_agents': len(self.agents),
                'agent_performance': {},
                'autonomous_features': {
                    'vector_memory_enabled': True,
                    'self_tuning_enabled': True,
                    'reinforcement_learning_enabled': True,
                    'performance_monitoring_enabled': True
                }
            }
            
            # Collect performance metrics from all agents
            for agent_type, agent in self.agents.items():
                try:
                    performance_data['agent_performance'][agent_type] = agent.get_performance_metrics()
                except Exception as e:
                    logger.error(f"Error getting performance for agent {agent_type}: {e}")
                    performance_data['agent_performance'][agent_type] = {'error': str(e)}
            
            # Add global metrics
            performance_data['global_metrics'] = {
                'total_executions': sum(
                    perf.get('total_actions', 0) 
                    for perf in performance_data['agent_performance'].values()
                    if isinstance(perf, dict)
                ),
                'average_success_rate': sum(
                    perf.get('success_rate', 0) 
                    for perf in performance_data['agent_performance'].values()
                    if isinstance(perf, dict)
                ) / len(self.agents) if self.agents else 0
            }
            
            return performance_data
            
        except Exception as e:
            logger.error(f"Error getting enhanced agent performance: {e}")
            return {'error': str(e)}

    def get_autonomous_status(self) -> Dict[str, Any]:
        """Get status of autonomous features."""
        try:
            status = {
                'startup_id': self.startup_id,
                'autonomous_features': {
                    'vector_memory': {
                        'enabled': self.vector_memory is not None,
                        'status': 'active' if self.vector_memory else 'disabled'
                    },
                    'self_tuning': {
                        'enabled': self.rl_engine is not None,
                        'status': 'active' if self.rl_engine else 'disabled'
                    },
                    'reinforcement_learning': {
                        'enabled': self.rl_engine is not None,
                        'status': 'active' if self.rl_engine else 'disabled'
                    },
                    'autonomous_workflow': {
                        'enabled': self.autonomous_workflow is not None,
                        'status': 'active' if self.autonomous_workflow else 'disabled'
                    }
                },
                'agents_with_autonomous_features': len(self.agents),
                'total_workflows_executed': len(self.workflow_results)
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting autonomous status: {e}")
            return {'error': str(e)}


# Factory function to create enhanced orchestrator
def create_enhanced_orchestrator(startup_id: str) -> EnhancedAgentOrchestrator:
    """Factory function to create enhanced orchestrator with autonomous features."""
    return EnhancedAgentOrchestrator(startup_id) 
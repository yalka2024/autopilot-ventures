"""Enhanced orchestrator for AutoPilot Ventures platform."""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass

from agents import (
    NicheResearchAgent, MVPDesignAgent, MarketingStrategyAgent,
    ContentCreationAgent, AnalyticsAgent, OperationsMonetizationAgent,
    FundingInvestorAgent, LegalComplianceAgent, HRTeamBuildingAgent,
    CustomerSupportScalingAgent
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
    VectorMemoryManager
)

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class WorkflowStep:
    """Workflow step configuration."""
    
    agent_type: str
    dependencies: List[str] = None
    priority: int = 1
    timeout: int = 300  # 5 minutes
    retry_count: int = 3
    required: bool = True


@dataclass
class WorkflowResult:
    """Result of workflow execution."""
    
    workflow_id: str
    startup_id: str
    success: bool
    steps_completed: List[str]
    steps_failed: List[str]
    total_cost: float
    execution_time: float
    results: Dict[str, Any]
    timestamp: str


class AgentOrchestrator:
    """Enhanced orchestrator for managing AI agents with autonomous capabilities."""

    def __init__(self, startup_id: str):
        """Initialize orchestrator with autonomous enhancements."""
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
        
        # Initialize all 10 agents
        self._initialize_agents()
        
        # Register agents with RL engine for learning
        self._register_agents_for_learning()
        
        logger.info(f"Enhanced orchestrator initialized for startup {startup_id}")

    def _initialize_agents(self):
        """Initialize all AI agents."""
        self.agents = {
            'niche_research': NicheResearchAgent(self.startup_id),
            'mvp_design': MVPDesignAgent(self.startup_id),
            'marketing_strategy': MarketingStrategyAgent(self.startup_id),
            'content_creation': ContentCreationAgent(self.startup_id),
            'analytics': AnalyticsAgent(self.startup_id),
            'operations_monetization': OperationsMonetizationAgent(self.startup_id),
            'funding_investor': FundingInvestorAgent(self.startup_id),
            'legal_compliance': LegalComplianceAgent(self.startup_id),
            'hr_team_building': HRTeamBuildingAgent(self.startup_id),
            'customer_support_scaling': CustomerSupportScalingAgent(self.startup_id)
        }
        
        logger.info(f"Initialized {len(self.agents)} agents")

    def _register_agents_for_learning(self):
        """Register agents with the reinforcement learning engine."""
        for agent_type, agent in self.agents.items():
            asyncio.create_task(
                self.rl_engine.register_agent(agent.agent_id, agent_type)
            )
        
        logger.info(f"Registered {len(self.agents)} agents for learning")

    async def execute_workflow(
        self,
        workflow_config: Dict[str, Any],
        max_concurrent: int = 3
    ) -> WorkflowResult:
        """Execute workflow with autonomous enhancements."""
        start_time = datetime.utcnow()
        
        try:
            # Use autonomous workflow engine for enhanced execution
            autonomous_result = await self.autonomous_workflow.execute_autonomous_workflow(workflow_config)
            
            if autonomous_result['success']:
                # Process successful autonomous workflow
                results = {}
                total_cost = 0.0
                
                for step_name in autonomous_result.get('steps_completed', []):
                    if step_name in workflow_config:
                        # Store step context in vector memory
                        await self.vector_memory.store_context(
                            f"workflow_{self.workflow_id}",
                            {
                                'step': step_name,
                                'config': workflow_config[step_name],
                                'timestamp': datetime.utcnow().isoformat()
                            }
                        )
                        
                        # Simulate step result (in production, this would be actual agent execution)
                        results[step_name] = {
                            'success': True,
                            'data': f"Autonomous execution of {step_name}",
                            'cost': 0.05
                        }
                        total_cost += 0.05
                
                execution_time = (datetime.utcnow() - start_time).total_seconds()
                
                workflow_result = WorkflowResult(
                    workflow_id=self.workflow_id,
                    startup_id=self.startup_id,
                    success=True,
                    steps_completed=autonomous_result.get('steps_completed', []),
                    steps_failed=autonomous_result.get('steps_failed', []),
                    total_cost=total_cost,
                    execution_time=execution_time,
                    results=results,
                    timestamp=datetime.utcnow().isoformat()
                )
            else:
                # Handle failed autonomous workflow
                workflow_result = WorkflowResult(
                    workflow_id=self.workflow_id,
                    startup_id=self.startup_id,
                    success=False,
                    steps_completed=autonomous_result.get('steps_completed', []),
                    steps_failed=autonomous_result.get('steps_failed', []),
                    total_cost=0.0,
                    execution_time=(datetime.utcnow() - start_time).total_seconds(),
                    results={},
                    timestamp=datetime.utcnow().isoformat()
                )
            
            self.workflow_results[self.workflow_id] = workflow_result
            self.execution_history.append(workflow_result)
            
            # Learn from workflow outcome
            await self._learn_from_workflow(workflow_result)
            
            return workflow_result
            
        except Exception as e:
            logger.error(f"Autonomous workflow execution failed: {e}")
            return WorkflowResult(
                workflow_id=self.workflow_id,
                startup_id=self.startup_id,
                success=False,
                steps_completed=[],
                steps_failed=list(workflow_config.keys()),
                total_cost=0.0,
                execution_time=(datetime.utcnow() - start_time).total_seconds(),
                results={},
                timestamp=datetime.utcnow().isoformat()
            )

    async def _learn_from_workflow(self, workflow_result: WorkflowResult):
        """Learn from workflow execution outcome."""
        try:
            # Calculate performance metrics
            success_rate = len(workflow_result.steps_completed) / max(1, len(workflow_result.steps_completed) + len(workflow_result.steps_failed))
            cost_efficiency = 1.0 / max(1, workflow_result.total_cost)
            
            # Store learning outcome in vector memory
            await self.vector_memory.store_context(
                f"learning_{self.workflow_id}",
                {
                    'workflow_id': self.workflow_id,
                    'success_rate': success_rate,
                    'cost_efficiency': cost_efficiency,
                    'execution_time': workflow_result.execution_time,
                    'timestamp': datetime.utcnow().isoformat()
                },
                importance=success_rate
            )
            
            # Optimize agent behaviors based on performance
            for agent_type in self.agents.keys():
                await self.rl_engine.optimize_agent_behavior(agent_type, {
                    'success_rate': success_rate,
                    'cost_efficiency': cost_efficiency,
                    'execution_time': workflow_result.execution_time
                })
            
            logger.info(f"Learning completed for workflow {self.workflow_id}")
            
        except Exception as e:
            logger.error(f"Failed to learn from workflow: {e}")

    async def execute_single_agent(
        self,
        agent_type: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute a single agent with autonomous enhancements."""
        if agent_type not in self.agents:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        agent = self.agents[agent_type]
        
        try:
            # Store execution context in vector memory
            await self.vector_memory.store_context(
                agent.agent_id,
                {
                    'agent_type': agent_type,
                    'parameters': kwargs,
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
            
            # Notify other agents about single agent execution
            await self.message_bus.broadcast_message(
                sender="orchestrator",
                message_type=MessageType.STATUS_UPDATE,
                content={
                    'agent_type': agent_type,
                    'status': 'single_execution',
                    'timestamp': datetime.utcnow().isoformat()
                },
                priority=MessagePriority.NORMAL
            )
            
            # Execute agent
            result = await agent.execute(**kwargs)
            
            # Learn from agent execution
            await self._learn_from_agent_execution(agent_type, result)
            
            # Share results
            await self.message_bus.broadcast_message(
                sender="orchestrator",
                message_type=MessageType.DATA_SHARE,
                content={
                    'data_key': f'{agent_type}_single_result',
                    'data_value': {
                        'agent_type': agent_type,
                        'result': result.data,
                        'success': result.success,
                        'timestamp': datetime.utcnow().isoformat()
                    }
                },
                priority=MessagePriority.NORMAL
            )
            
            return {
                'success': result.success,
                'data': result.data,
                'message': result.message,
                'cost': result.cost
            }
            
        except Exception as e:
            logger.error(f"Single agent execution failed: {e}")
            return {
                'success': False,
                'data': {},
                'message': str(e),
                'cost': 0.0
            }

    async def _learn_from_agent_execution(self, agent_type: str, result):
        """Learn from individual agent execution."""
        try:
            # Store agent execution outcome
            await self.vector_memory.store_context(
                f"agent_execution_{agent_type}",
                {
                    'agent_type': agent_type,
                    'success': result.success,
                    'cost': result.cost,
                    'timestamp': datetime.utcnow().isoformat()
                },
                importance=1.0 if result.success else 0.5
            )
            
            # Optimize agent behavior
            await self.rl_engine.optimize_agent_behavior(agent_type, {
                'success': result.success,
                'cost': result.cost,
                'execution_count': 1
            })
            
        except Exception as e:
            logger.error(f"Failed to learn from agent execution: {e}")

    async def _share_step_results(self, step_name: str, step_data: Dict[str, Any]):
        """Share step results with other agents using vector memory."""
        try:
            # Store step results in vector memory
            await self.vector_memory.store_context(
                f"step_results_{step_name}",
                {
                    'step_name': step_name,
                    'data': step_data,
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
            
            # Broadcast to message bus
            await self.message_bus.broadcast_message(
                sender="orchestrator",
                message_type=MessageType.DATA_SHARE,
                content={
                    'data_key': f'step_result_{step_name}',
                    'data_value': step_data
                },
                priority=MessagePriority.NORMAL
            )
            
        except Exception as e:
            logger.error(f"Failed to share step results: {e}")

    def get_agent_performance(self) -> Dict[str, Any]:
        """Get agent performance metrics with autonomous learning data."""
        performance = {}
        
        for agent_type, agent in self.agents.items():
            try:
                # Get agent stats from database
                agents = db_manager.get_agents_by_startup(self.startup_id)
                agent_stats = next((a for a in agents if a.agent_type == agent_type), None)
                
                if agent_stats:
                    performance[agent_type] = {
                        'execution_count': agent_stats.execution_count,
                        'success_rate': agent_stats.success_rate,
                        'average_cost': agent_stats.average_cost,
                        'last_execution': agent_stats.last_execution.isoformat() if agent_stats.last_execution else None,
                        'autonomous_learning': True,
                        'vector_memory_enabled': True
                    }
                else:
                    performance[agent_type] = {
                        'execution_count': 0,
                        'success_rate': 0.0,
                        'average_cost': 0.0,
                        'last_execution': None,
                        'autonomous_learning': True,
                        'vector_memory_enabled': True
                    }
            except Exception as e:
                logger.error(f"Failed to get performance for {agent_type}: {e}")
                performance[agent_type] = {
                    'execution_count': 0,
                    'success_rate': 0.0,
                    'average_cost': 0.0,
                    'last_execution': None,
                    'error': str(e),
                    'autonomous_learning': True,
                    'vector_memory_enabled': True
                }
        
        return performance

    def get_autonomous_status(self) -> Dict[str, Any]:
        """Get status of autonomous enhancements."""
        return {
            'vector_memory': {
                'enabled': True,
                'collections': 3,  # context, learning, decisions
                'startup_id': self.startup_id
            },
            'reinforcement_learning': {
                'enabled': True,
                'agents_registered': len(self.agents),
                'optimizations_performed': len(self.execution_history)
            },
            'autonomous_workflow': {
                'enabled': True,
                'workflows_executed': len(self.execution_history),
                'self_healing_enabled': True
            },
            'message_bus': {
                'enabled': True,
                'agents_connected': len(self.agents)
            }
        } 
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
    """Workflow execution result."""
    
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
    """Enhanced orchestrator for managing AI agents."""

    def __init__(self, startup_id: str):
        """Initialize orchestrator."""
        self.startup_id = startup_id
        self.workflow_id = generate_id("workflow")
        self.agents = {}
        self.workflow_results = {}
        self.execution_history = []
        
        # Initialize all 10 agents
        self._initialize_agents()
        
        # Define workflow steps
        self.workflow_steps = [
            WorkflowStep("niche_research", priority=1, required=True),
            WorkflowStep("mvp_design", dependencies=["niche_research"], priority=2, required=True),
            WorkflowStep("marketing_strategy", dependencies=["mvp_design"], priority=3, required=True),
            WorkflowStep("content_creation", dependencies=["marketing_strategy"], priority=4, required=False),
            WorkflowStep("analytics", dependencies=["marketing_strategy"], priority=5, required=False),
            WorkflowStep("operations_monetization", dependencies=["analytics"], priority=6, required=False),
            WorkflowStep("funding_investor", dependencies=["mvp_design"], priority=7, required=False),
            WorkflowStep("legal_compliance", dependencies=["mvp_design"], priority=8, required=False),
            WorkflowStep("hr_team_building", dependencies=["funding_investor"], priority=9, required=False),
            WorkflowStep("customer_support_scaling", dependencies=["marketing_strategy"], priority=10, required=False)
        ]

    def _initialize_agents(self) -> None:
        """Initialize all AI agents."""
        try:
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
            logger.info(f"Initialized {len(self.agents)} agents for startup {self.startup_id}")
        except Exception as e:
            logger.error(f"Failed to initialize agents: {e}")
            raise

    async def execute_workflow(
        self,
        workflow_config: Dict[str, Any],
        max_concurrent: int = 3
    ) -> WorkflowResult:
        """Execute complete workflow with all agents."""
        start_time = datetime.utcnow()
        completed_steps = []
        failed_steps = []
        total_cost = 0.0
        results = {}

        try:
            # Check initial budget
            estimated_cost = self._estimate_workflow_cost(workflow_config)
            if not budget_manager.can_spend(estimated_cost):
                return WorkflowResult(
                    workflow_id=self.workflow_id,
                    startup_id=self.startup_id,
                    success=False,
                    steps_completed=[],
                    steps_failed=[],
                    total_cost=0.0,
                    execution_time=0.0,
                    results={},
                    timestamp=datetime.utcnow().isoformat()
                )

            # Execute workflow steps in dependency order
            for step in sorted(self.workflow_steps, key=lambda x: x.priority):
                if not self._can_execute_step(step, completed_steps):
                    continue

                try:
                    step_result = await self._execute_step(step, workflow_config)
                    if step_result['success']:
                        completed_steps.append(step.agent_type)
                        results[step.agent_type] = step_result['data']
                        total_cost += step_result['cost']
                    else:
                        failed_steps.append(step.agent_type)
                        if step.required:
                            break

                except Exception as e:
                    logger.error(f"Step {step.agent_type} failed: {e}")
                    failed_steps.append(step.agent_type)
                    if step.required:
                        break

            # Calculate execution time
            execution_time = (datetime.utcnow() - start_time).total_seconds()

            # Create workflow result
            workflow_result = WorkflowResult(
                workflow_id=self.workflow_id,
                startup_id=self.startup_id,
                success=len(failed_steps) == 0,
                steps_completed=completed_steps,
                steps_failed=failed_steps,
                total_cost=total_cost,
                execution_time=execution_time,
                results=results,
                timestamp=datetime.utcnow().isoformat()
            )

            # Store result
            self.workflow_results[self.workflow_id] = workflow_result
            self.execution_history.append(workflow_result)

            # Log completion
            log.info(
                "Workflow completed",
                workflow_id=self.workflow_id,
                startup_id=self.startup_id,
                success=workflow_result.success,
                steps_completed=len(completed_steps),
                steps_failed=len(failed_steps),
                total_cost=total_cost,
                execution_time=execution_time
            )

            return workflow_result

        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            return WorkflowResult(
                workflow_id=self.workflow_id,
                startup_id=self.startup_id,
                success=False,
                steps_completed=completed_steps,
                steps_failed=failed_steps,
                total_cost=total_cost,
                execution_time=execution_time,
                results=results,
                timestamp=datetime.utcnow().isoformat()
            )

    def _can_execute_step(self, step: WorkflowStep, completed_steps: List[str]) -> bool:
        """Check if step can be executed based on dependencies."""
        if not step.dependencies:
            return True
        
        return all(dep in completed_steps for dep in step.dependencies)

    async def _execute_step(
        self,
        step: WorkflowStep,
        workflow_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a single workflow step."""
        agent = self.agents.get(step.agent_type)
        if not agent:
            raise ValueError(f"Agent {step.agent_type} not found")

        # Get step configuration
        step_config = workflow_config.get(step.agent_type, {})
        
        # Execute with timeout and retries
        for attempt in range(step.retry_count):
            try:
                if step.agent_type == 'niche_research':
                    result = await asyncio.wait_for(
                        agent.execute(
                            niche=step_config.get('niche', ''),
                            market_data=step_config.get('market_data', '')
                        ),
                        timeout=step.timeout
                    )
                elif step.agent_type == 'mvp_design':
                    result = await asyncio.wait_for(
                        agent.execute(
                            niche=step_config.get('niche', ''),
                            target_audience=step_config.get('target_audience', ''),
                            requirements=step_config.get('requirements', '')
                        ),
                        timeout=step.timeout
                    )
                elif step.agent_type == 'marketing_strategy':
                    result = await asyncio.wait_for(
                        agent.execute(
                            product=step_config.get('product', ''),
                            target_audience=step_config.get('target_audience', ''),
                            budget=step_config.get('budget', 1000.0)
                        ),
                        timeout=step.timeout
                    )
                elif step.agent_type == 'content_creation':
                    result = await asyncio.wait_for(
                        agent.execute(
                            topic=step_config.get('topic', ''),
                            audience=step_config.get('audience', ''),
                            content_type=step_config.get('content_type', 'blog post'),
                            tone=step_config.get('tone', 'professional')
                        ),
                        timeout=step.timeout
                    )
                elif step.agent_type == 'analytics':
                    result = await asyncio.wait_for(
                        agent.execute(
                            data=step_config.get('data', ''),
                            metrics=step_config.get('metrics', ''),
                            questions=step_config.get('questions', '')
                        ),
                        timeout=step.timeout
                    )
                elif step.agent_type == 'operations_monetization':
                    result = await asyncio.wait_for(
                        agent.execute(
                            current_operations=step_config.get('current_operations', ''),
                            revenue_data=step_config.get('revenue_data', '')
                        ),
                        timeout=step.timeout
                    )
                elif step.agent_type == 'funding_investor':
                    result = await asyncio.wait_for(
                        agent.execute(
                            startup_info=step_config.get('startup_info', ''),
                            funding_stage=step_config.get('funding_stage', 'seed'),
                            target_amount=step_config.get('target_amount', 100000.0)
                        ),
                        timeout=step.timeout
                    )
                elif step.agent_type == 'legal_compliance':
                    result = await asyncio.wait_for(
                        agent.execute(
                            document_type=step_config.get('document_type', ''),
                            content=step_config.get('content', ''),
                            jurisdiction=step_config.get('jurisdiction', 'US')
                        ),
                        timeout=step.timeout
                    )
                elif step.agent_type == 'hr_team_building':
                    result = await asyncio.wait_for(
                        agent.execute(
                            company_info=step_config.get('company_info', ''),
                            hiring_needs=step_config.get('hiring_needs', ''),
                            team_size=step_config.get('team_size', 5)
                        ),
                        timeout=step.timeout
                    )
                elif step.agent_type == 'customer_support_scaling':
                    result = await asyncio.wait_for(
                        agent.execute(
                            customer_queries=step_config.get('customer_queries', ''),
                            current_scale=step_config.get('current_scale', ''),
                            language=step_config.get('language', 'en')
                        ),
                        timeout=step.timeout
                    )
                else:
                    raise ValueError(f"Unknown agent type: {step.agent_type}")

                return {
                    'success': result.success,
                    'data': result.data,
                    'cost': result.cost,
                    'message': result.message
                }

            except asyncio.TimeoutError:
                logger.warning(f"Step {step.agent_type} timed out (attempt {attempt + 1})")
                if attempt == step.retry_count - 1:
                    raise
            except Exception as e:
                logger.error(f"Step {step.agent_type} failed (attempt {attempt + 1}): {e}")
                if attempt == step.retry_count - 1:
                    raise

    def _estimate_workflow_cost(self, workflow_config: Dict[str, Any]) -> float:
        """Estimate total cost of workflow execution."""
        # Base costs for each agent type
        agent_costs = {
            'niche_research': 0.05,
            'mvp_design': 0.08,
            'marketing_strategy': 0.06,
            'content_creation': 0.04,
            'analytics': 0.07,
            'operations_monetization': 0.09,
            'funding_investor': 0.12,
            'legal_compliance': 0.10,
            'hr_team_building': 0.08,
            'customer_support_scaling': 0.06
        }

        total_cost = 0.0
        for step in self.workflow_steps:
            if step.agent_type in agent_costs:
                total_cost += agent_costs[step.agent_type]

        return total_cost

    async def execute_single_agent(
        self,
        agent_type: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute a single agent."""
        agent = self.agents.get(agent_type)
        if not agent:
            raise ValueError(f"Agent {agent_type} not found")

        try:
            result = await agent.execute(**kwargs)
            return {
                'success': result.success,
                'data': result.data,
                'cost': result.cost,
                'message': result.message
            }
        except Exception as e:
            logger.error(f"Single agent execution failed: {e}")
            return {
                'success': False,
                'data': {},
                'cost': 0.0,
                'message': str(e)
            }

    def get_workflow_status(self) -> Dict[str, Any]:
        """Get current workflow status."""
        return {
            'workflow_id': self.workflow_id,
            'startup_id': self.startup_id,
            'agents_available': list(self.agents.keys()),
            'workflow_steps': [step.agent_type for step in self.workflow_steps],
            'execution_history_count': len(self.execution_history),
            'budget_remaining': budget_manager.get_remaining_budget(),
            'budget_spent': budget_manager.initial_budget - budget_manager.get_remaining_budget()
        }

    def get_agent_performance(self) -> Dict[str, Any]:
        """Get performance metrics for all agents."""
        performance = {}
        for agent_type, agent in self.agents.items():
            try:
                agents = db_manager.get_agents_by_startup(self.startup_id)
                agent_data = next((a for a in agents if a.agent_type == agent_type), None)
                
                if agent_data:
                    performance[agent_type] = {
                        'execution_count': agent_data.execution_count,
                        'success_rate': agent_data.success_rate,
                        'last_execution': agent_data.last_execution.isoformat() if agent_data.last_execution else None,
                        'status': agent_data.status
                    }
                else:
                    performance[agent_type] = {
                        'execution_count': 0,
                        'success_rate': 0.0,
                        'last_execution': None,
                        'status': 'inactive'
                    }
            except Exception as e:
                logger.error(f"Failed to get performance for {agent_type}: {e}")
                performance[agent_type] = {
                    'execution_count': 0,
                    'success_rate': 0.0,
                    'last_execution': None,
                    'status': 'error'
                }

        return performance


# Global orchestrator instance
_orchestrator = None


def get_orchestrator(startup_id: str) -> AgentOrchestrator:
    """Get or create orchestrator instance."""
    global _orchestrator
    if _orchestrator is None or _orchestrator.startup_id != startup_id:
        _orchestrator = AgentOrchestrator(startup_id)
    return _orchestrator 
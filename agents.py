"""Enhanced AI agents for AutoPilot Ventures platform."""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

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

# Configure logging
logger = logging.getLogger(__name__)


class AgentResult(BaseModel):
    """Base model for agent results."""

    success: bool = Field(description="Whether the operation was successful")
    data: Dict[str, Any] = Field(description="Result data")
    message: str = Field(description="Result message")
    cost: float = Field(description="Cost of the operation")


class BaseAgent:
    """Base class for all AI agents."""

    def __init__(self, agent_type: str, startup_id: str):
        """Initialize base agent."""
        self.agent_type = agent_type
        self.startup_id = startup_id
        self.agent_id = generate_id(f"agent_{agent_type}")
        self.llm = ChatOpenAI(
            model=config.ai.model_name,
            temperature=config.ai.temperature,
            max_tokens=config.ai.max_tokens,
            openai_api_key=config.ai.openai_key
        )
        self.parser = PydanticOutputParser(pydantic_object=AgentResult)

        # Register agent in database
        self._register_agent()

    def _register_agent(self) -> None:
        """Register agent in database."""
        try:
            db_manager.create_agent(
                startup_id=self.startup_id,
                agent_type=self.agent_type,
                metadata={
                    'created_at': datetime.utcnow().isoformat(),
                    'model': config.ai.model_name
                }
            )
        except Exception as e:
            logger.error(f"Failed to register agent: {e}")

    async def execute(self, **kwargs) -> AgentResult:
        """Execute agent task."""
        raise NotImplementedError("Subclasses must implement execute method")

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
                agent = agents[0]  # Get first agent of this type
                current_count = agent.execution_count
                current_rate = agent.success_rate

                new_count = current_count + 1
                new_rate = (
                    (current_rate * current_count + (1 if success else 0)) / new_count
                )

                db_manager.update_agent(agent.id, {
                    'execution_count': new_count,
                    'success_rate': new_rate,
                    'last_execution': datetime.utcnow()
                })
        except Exception as e:
            logger.error(f"Failed to update agent stats: {e}")

    def _log_execution(self, success: bool, duration: float) -> None:
        """Log execution metrics."""
        # Update Prometheus metrics
        AGENT_EXECUTION_COUNTER.labels(
            agent_type=self.agent_type,
            status='success' if success else 'failure'
        ).inc()
        
        AGENT_EXECUTION_DURATION.labels(agent_type=self.agent_type).observe(duration)
        
        # Structured logging
        log.info(
            "Agent execution completed",
            agent_type=self.agent_type,
            startup_id=self.startup_id,
            success=success,
            duration=duration
        )


# Existing 6 agents remain unchanged...
class NicheResearchAgent(BaseAgent):
    """Agent for niche research and market analysis."""

    def __init__(self, startup_id: str):
        super().__init__('niche_research', startup_id)

        self.prompt_template = PromptTemplate(
            input_variables=["niche", "market_data"],
            template="""
            Analyze the niche market for startup opportunities:

            Niche: {niche}
            Market Data: {market_data}

            Provide:
            1. Market size and growth potential
            2. Competition analysis
            3. Target audience identification
            4. Revenue potential
            5. Entry barriers and risks
            6. Recommended positioning strategy

            Format your response as structured analysis.
            """
        )

    async def execute(self, niche: str, market_data: str = "") -> AgentResult:
        """Execute niche research."""
        start_time = datetime.utcnow()
        try:
            # Check budget
            if not self._check_budget(0.05):
                return AgentResult(
                    success=False,
                    data={},
                    message="Insufficient budget for niche research",
                    cost=0.0
                )

            # Check content safety
            safety_result = self._check_content_safety(niche)
            if safety_result['toxicity'] > config.security.content_safety_threshold:
                return AgentResult(
                    success=False,
                    data={},
                    message="Niche contains inappropriate content",
                    cost=0.0
                )

            # Generate prompt
            prompt = self.prompt_template.format(
                niche=niche,
                market_data=market_data or "No additional market data provided"
            )

            # Execute LLM call
            messages = [
                SystemMessage(content="You are a market research expert."),
                HumanMessage(content=prompt)
            ]

            response = await asyncio.to_thread(
                self.llm.invoke, messages
            )

            # Parse response
            result_data = {
                'niche': niche,
                'analysis': response.content,
                'safety_score': safety_result,
                'timestamp': datetime.utcnow().isoformat()
            }

            # Record cost and update stats
            self._record_cost(0.05)
            self._update_agent_stats(True)

            duration = (datetime.utcnow() - start_time).total_seconds()
            self._log_execution(True, duration)

            return AgentResult(
                success=True,
                data=result_data,
                message="Niche research completed successfully",
                cost=0.05
            )

        except Exception as e:
            logger.error(f"Niche research failed: {e}")
            self._update_agent_stats(False)
            duration = (datetime.utcnow() - start_time).total_seconds()
            self._log_execution(False, duration)
            return AgentResult(
                success=False,
                data={},
                message=f"Research failed: {str(e)}",
                cost=0.0
            )


class MVPDesignAgent(BaseAgent):
    """Agent for MVP design and development planning."""

    def __init__(self, startup_id: str):
        super().__init__('mvp_design', startup_id)

        self.prompt_template = PromptTemplate(
            input_variables=["niche", "target_audience", "requirements"],
            template="""
            Design an MVP for the following startup:

            Niche: {niche}
            Target Audience: {target_audience}
            Requirements: {requirements}

            Provide:
            1. Core features and functionality
            2. Technology stack recommendations
            3. Development timeline
            4. Resource requirements
            5. Success metrics
            6. Risk mitigation strategies

            Format your response as structured MVP design.
            """
        )

    async def execute(
        self,
        niche: str,
        target_audience: str,
        requirements: str = ""
    ) -> AgentResult:
        """Execute MVP design."""
        start_time = datetime.utcnow()
        try:
            # Check budget
            if not self._check_budget(0.08):
                return AgentResult(
                    success=False,
                    data={},
                    message="Insufficient budget for MVP design",
                    cost=0.0
                )

            # Check content safety
            combined_content = f"{niche} {target_audience} {requirements}"
            safety_result = self._check_content_safety(combined_content)
            if safety_result['toxicity'] > config.security.content_safety_threshold:
                return AgentResult(
                    success=False,
                    data={},
                    message="Content contains inappropriate material",
                    cost=0.0
                )

            # Generate prompt
            prompt = self.prompt_template.format(
                niche=niche,
                target_audience=target_audience,
                requirements=requirements or "No specific requirements provided"
            )

            # Execute LLM call
            messages = [
                SystemMessage(content="You are an MVP design expert."),
                HumanMessage(content=prompt)
            ]

            response = await asyncio.to_thread(
                self.llm.invoke, messages
            )

            # Parse response
            result_data = {
                'niche': niche,
                'target_audience': target_audience,
                'mvp_design': response.content,
                'safety_score': safety_result,
                'timestamp': datetime.utcnow().isoformat()
            }

            # Record cost and update stats
            self._record_cost(0.08)
            self._update_agent_stats(True)

            duration = (datetime.utcnow() - start_time).total_seconds()
            self._log_execution(True, duration)

            return AgentResult(
                success=True,
                data=result_data,
                message="MVP design completed successfully",
                cost=0.08
            )

        except Exception as e:
            logger.error(f"MVP design failed: {e}")
            self._update_agent_stats(False)
            duration = (datetime.utcnow() - start_time).total_seconds()
            self._log_execution(False, duration)
            return AgentResult(
                success=False,
                data={},
                message=f"Design failed: {str(e)}",
                cost=0.0
            )


class MarketingStrategyAgent(BaseAgent):
    """Agent for marketing strategy development."""

    def __init__(self, startup_id: str):
        super().__init__('marketing_strategy', startup_id)

        self.prompt_template = PromptTemplate(
            input_variables=["product", "target_audience", "budget"],
            template="""
            Develop a marketing strategy for the following product:

            Product: {product}
            Target Audience: {target_audience}
            Budget: ${budget}

            Provide:
            1. Marketing channels and tactics
            2. Budget allocation strategy
            3. Content marketing plan
            4. Social media strategy
            5. Performance metrics
            6. Timeline and milestones

            Format your response as structured marketing strategy.
            """
        )

    async def execute(
        self,
        product: str,
        target_audience: str,
        budget: float
    ) -> AgentResult:
        """Execute marketing strategy development."""
        start_time = datetime.utcnow()
        try:
            # Check budget
            if not self._check_budget(0.06):
                return AgentResult(
                    success=False,
                    data={},
                    message="Insufficient budget for marketing strategy",
                    cost=0.0
                )

            # Check content safety
            combined_content = f"{product} {target_audience}"
            safety_result = self._check_content_safety(combined_content)
            if safety_result['toxicity'] > config.security.content_safety_threshold:
                return AgentResult(
                    success=False,
                    data={},
                    message="Content contains inappropriate material",
                    cost=0.0
                )

            # Generate prompt
            prompt = self.prompt_template.format(
                product=product,
                target_audience=target_audience,
                budget=budget
            )

            # Execute LLM call
            messages = [
                SystemMessage(content="You are a marketing strategy expert."),
                HumanMessage(content=prompt)
            ]

            response = await asyncio.to_thread(
                self.llm.invoke, messages
            )

            # Parse response
            result_data = {
                'product': product,
                'target_audience': target_audience,
                'budget': budget,
                'marketing_strategy': response.content,
                'safety_score': safety_result,
                'timestamp': datetime.utcnow().isoformat()
            }

            # Record cost and update stats
            self._record_cost(0.06)
            self._update_agent_stats(True)

            duration = (datetime.utcnow() - start_time).total_seconds()
            self._log_execution(True, duration)

            return AgentResult(
                success=True,
                data=result_data,
                message="Marketing strategy completed successfully",
                cost=0.06
            )

        except Exception as e:
            logger.error(f"Marketing strategy failed: {e}")
            self._update_agent_stats(False)
            duration = (datetime.utcnow() - start_time).total_seconds()
            self._log_execution(False, duration)
            return AgentResult(
                success=False,
                data={},
                message=f"Strategy failed: {str(e)}",
                cost=0.0
            )


class ContentCreationAgent(BaseAgent):
    """Agent for content creation and copywriting."""

    def __init__(self, startup_id: str):
        super().__init__('content_creation', startup_id)

        self.prompt_template = PromptTemplate(
            input_variables=["topic", "audience", "content_type", "tone"],
            template="""
            Create content for the following specifications:

            Topic: {topic}
            Target Audience: {audience}
            Content Type: {content_type}
            Tone: {tone}

            Provide:
            1. Engaging headline
            2. Main content body
            3. Call-to-action
            4. SEO optimization suggestions
            5. Distribution recommendations

            Format your response as structured content.
            """
        )

    async def execute(
        self,
        topic: str,
        audience: str,
        content_type: str = "blog post",
        tone: str = "professional"
    ) -> AgentResult:
        """Execute content creation."""
        start_time = datetime.utcnow()
        try:
            # Check budget
            if not self._check_budget(0.04):
                return AgentResult(
                    success=False,
                    data={},
                    message="Insufficient budget for content creation",
                    cost=0.0
                )

            # Check content safety
            combined_content = f"{topic} {audience}"
            safety_result = self._check_content_safety(combined_content)
            if safety_result['toxicity'] > config.security.content_safety_threshold:
                return AgentResult(
                    success=False,
                    data={},
                    message="Content contains inappropriate material",
                    cost=0.0
                )

            # Generate prompt
            prompt = self.prompt_template.format(
                topic=topic,
                audience=audience,
                content_type=content_type,
                tone=tone
            )

            # Execute LLM call
            messages = [
                SystemMessage(content="You are a content creation expert."),
                HumanMessage(content=prompt)
            ]

            response = await asyncio.to_thread(
                self.llm.invoke, messages
            )

            # Parse response
            result_data = {
                'topic': topic,
                'audience': audience,
                'content_type': content_type,
                'tone': tone,
                'content': response.content,
                'safety_score': safety_result,
                'timestamp': datetime.utcnow().isoformat()
            }

            # Record cost and update stats
            self._record_cost(0.04)
            self._update_agent_stats(True)

            duration = (datetime.utcnow() - start_time).total_seconds()
            self._log_execution(True, duration)

            return AgentResult(
                success=True,
                data=result_data,
                message="Content creation completed successfully",
                cost=0.04
            )

        except Exception as e:
            logger.error(f"Content creation failed: {e}")
            self._update_agent_stats(False)
            duration = (datetime.utcnow() - start_time).total_seconds()
            self._log_execution(False, duration)
            return AgentResult(
                success=False,
                data={},
                message=f"Content creation failed: {str(e)}",
                cost=0.0
            )


class AnalyticsAgent(BaseAgent):
    """Agent for data analysis and insights."""

    def __init__(self, startup_id: str):
        super().__init__('analytics', startup_id)

        self.prompt_template = PromptTemplate(
            input_variables=["data", "metrics", "questions"],
            template="""
            Analyze the following data and provide insights:

            Data: {data}
            Metrics: {metrics}
            Questions: {questions}

            Provide:
            1. Key performance indicators
            2. Trend analysis
            3. Insights and recommendations
            4. Action items
            5. Risk assessment
            6. Growth opportunities

            Format your response as structured analysis.
            """
        )

    async def execute(
        self,
        data: str,
        metrics: str,
        questions: str = ""
    ) -> AgentResult:
        """Execute data analysis."""
        start_time = datetime.utcnow()
        try:
            # Check budget
            if not self._check_budget(0.07):
                return AgentResult(
                    success=False,
                    data={},
                    message="Insufficient budget for analytics",
                    cost=0.0
                )

            # Check content safety
            combined_content = f"{data} {metrics} {questions}"
            safety_result = self._check_content_safety(combined_content)
            if safety_result['toxicity'] > config.security.content_safety_threshold:
                return AgentResult(
                    success=False,
                    data={},
                    message="Data contains inappropriate content",
                    cost=0.0
                )

            # Generate prompt
            prompt = self.prompt_template.format(
                data=data,
                metrics=metrics,
                questions=questions or "No specific questions provided"
            )

            # Execute LLM call
            messages = [
                SystemMessage(content="You are a data analytics expert."),
                HumanMessage(content=prompt)
            ]

            response = await asyncio.to_thread(
                self.llm.invoke, messages
            )

            # Parse response
            result_data = {
                'data': data,
                'metrics': metrics,
                'questions': questions,
                'analysis': response.content,
                'safety_score': safety_result,
                'timestamp': datetime.utcnow().isoformat()
            }

            # Record cost and update stats
            self._record_cost(0.07)
            self._update_agent_stats(True)

            duration = (datetime.utcnow() - start_time).total_seconds()
            self._log_execution(True, duration)

            return AgentResult(
                success=True,
                data=result_data,
                message="Analytics completed successfully",
                cost=0.07
            )

        except Exception as e:
            logger.error(f"Analytics failed: {e}")
            self._update_agent_stats(False)
            duration = (datetime.utcnow() - start_time).total_seconds()
            self._log_execution(False, duration)
            return AgentResult(
                success=False,
                data={},
                message=f"Analysis failed: {str(e)}",
                cost=0.0
            )


class OperationsMonetizationAgent(BaseAgent):
    """Agent for operations optimization and monetization."""

    def __init__(self, startup_id: str):
        super().__init__('operations_monetization', startup_id)

        self.prompt_template = PromptTemplate(
            input_variables=["current_operations", "revenue_data"],
            template="""
            Optimize operations and monetization for the following startup:

            Current Operations: {current_operations}
            Revenue Data: {revenue_data}

            Provide:
            1. Operational efficiency improvements
            2. Revenue optimization strategies
            3. Cost reduction opportunities
            4. Scalability recommendations
            5. Monetization models
            6. Implementation roadmap

            Format your response as structured optimization plan.
            """
        )

    async def execute(
        self,
        current_operations: str,
        revenue_data: str
    ) -> AgentResult:
        """Execute operations optimization."""
        start_time = datetime.utcnow()
        try:
            # Check budget
            if not self._check_budget(0.09):
                return AgentResult(
                    success=False,
                    data={},
                    message="Insufficient budget for operations optimization",
                    cost=0.0
                )

            # Check content safety
            combined_content = f"{current_operations} {revenue_data}"
            safety_result = self._check_content_safety(combined_content)
            if safety_result['toxicity'] > config.security.content_safety_threshold:
                return AgentResult(
                    success=False,
                    data={},
                    message="Content contains inappropriate material",
                    cost=0.0
                )

            # Generate prompt
            prompt = self.prompt_template.format(
                current_operations=current_operations,
                revenue_data=revenue_data
            )

            # Execute LLM call
            messages = [
                SystemMessage(content="You are an operations and monetization expert."),
                HumanMessage(content=prompt)
            ]

            response = await asyncio.to_thread(
                self.llm.invoke, messages
            )

            # Parse response
            result_data = {
                'current_operations': current_operations,
                'revenue_data': revenue_data,
                'optimization_plan': response.content,
                'safety_score': safety_result,
                'timestamp': datetime.utcnow().isoformat()
            }

            # Record cost and update stats
            self._record_cost(0.09)
            self._update_agent_stats(True)

            duration = (datetime.utcnow() - start_time).total_seconds()
            self._log_execution(True, duration)

            return AgentResult(
                success=True,
                data=result_data,
                message="Operations optimization completed successfully",
                cost=0.09
            )

        except Exception as e:
            logger.error(f"Operations optimization failed: {e}")
            self._update_agent_stats(False)
            duration = (datetime.utcnow() - start_time).total_seconds()
            self._log_execution(False, duration)
            return AgentResult(
                success=False,
                data={},
                message=f"Optimization failed: {str(e)}",
                cost=0.0
            )


# NEW AGENTS - 4 Additional Agents

class FundingInvestorAgent(BaseAgent):
    """Agent for funding and investor relations."""

    def __init__(self, startup_id: str):
        super().__init__('funding_investor', startup_id)

        self.prompt_template = PromptTemplate(
            input_variables=["startup_info", "funding_stage", "target_amount"],
            template="""
            Develop funding strategy and investor relations for the startup:

            Startup Info: {startup_info}
            Current Funding Stage: {funding_stage}
            Target Funding Amount: ${target_amount}

            Provide:
            1. Pitch deck structure and key slides
            2. Investor targeting strategy
            3. Valuation analysis and justification
            4. Due diligence preparation checklist
            5. Investor outreach templates
            6. Funding timeline and milestones

            Format your response as structured funding strategy.
            """
        )

    async def execute(
        self,
        startup_info: str,
        funding_stage: str,
        target_amount: float
    ) -> AgentResult:
        """Execute funding and investor relations."""
        start_time = datetime.utcnow()
        try:
            # Check budget
            if not self._check_budget(0.12):
                return AgentResult(
                    success=False,
                    data={},
                    message="Insufficient budget for funding strategy",
                    cost=0.0
                )

            # Check content safety
            combined_content = f"{startup_info} {funding_stage}"
            safety_result = self._check_content_safety(combined_content)
            if safety_result['toxicity'] > config.security.content_safety_threshold:
                return AgentResult(
                    success=False,
                    data={},
                    message="Content contains inappropriate material",
                    cost=0.0
                )

            # Generate prompt
            prompt = self.prompt_template.format(
                startup_info=startup_info,
                funding_stage=funding_stage,
                target_amount=target_amount
            )

            # Execute LLM call
            messages = [
                SystemMessage(content="You are a funding and investor relations expert."),
                HumanMessage(content=prompt)
            ]

            response = await asyncio.to_thread(
                self.llm.invoke, messages
            )

            # Parse response
            result_data = {
                'startup_info': startup_info,
                'funding_stage': funding_stage,
                'target_amount': target_amount,
                'funding_strategy': response.content,
                'safety_score': safety_result,
                'timestamp': datetime.utcnow().isoformat()
            }

            # Record cost and update stats
            self._record_cost(0.12)
            self._update_agent_stats(True)

            duration = (datetime.utcnow() - start_time).total_seconds()
            self._log_execution(True, duration)

            return AgentResult(
                success=True,
                data=result_data,
                message="Funding strategy completed successfully",
                cost=0.12
            )

        except Exception as e:
            logger.error(f"Funding strategy failed: {e}")
            self._update_agent_stats(False)
            duration = (datetime.utcnow() - start_time).total_seconds()
            self._log_execution(False, duration)
            return AgentResult(
                success=False,
                data={},
                message=f"Funding strategy failed: {str(e)}",
                cost=0.0
            )


class LegalComplianceAgent(BaseAgent):
    """Agent for legal and compliance management."""

    def __init__(self, startup_id: str):
        super().__init__('legal_compliance', startup_id)

        self.prompt_template = PromptTemplate(
            input_variables=["document_type", "content", "jurisdiction"],
            template="""
            Review and analyze legal document for compliance:

            Document Type: {document_type}
            Content: {content}
            Jurisdiction: {jurisdiction}

            Provide:
            1. Legal compliance assessment
            2. Risk identification and mitigation
            3. Required modifications and clauses
            4. Regulatory requirements checklist
            5. GDPR/CCPA compliance analysis
            6. Legal recommendations

            Format your response as structured legal analysis.
            """
        )

    async def execute(
        self,
        document_type: str,
        content: str,
        jurisdiction: str = "US"
    ) -> AgentResult:
        """Execute legal and compliance review."""
        start_time = datetime.utcnow()
        try:
            # Check budget
            if not self._check_budget(0.10):
                return AgentResult(
                    success=False,
                    data={},
                    message="Insufficient budget for legal review",
                    cost=0.0
                )

            # Check content safety
            combined_content = f"{document_type} {content} {jurisdiction}"
            safety_result = self._check_content_safety(combined_content)
            if safety_result['toxicity'] > config.security.content_safety_threshold:
                return AgentResult(
                    success=False,
                    data={},
                    message="Content contains inappropriate material",
                    cost=0.0
                )

            # Generate prompt
            prompt = self.prompt_template.format(
                document_type=document_type,
                content=content,
                jurisdiction=jurisdiction
            )

            # Execute LLM call
            messages = [
                SystemMessage(content="You are a legal and compliance expert."),
                HumanMessage(content=prompt)
            ]

            response = await asyncio.to_thread(
                self.llm.invoke, messages
            )

            # Parse response
            result_data = {
                'document_type': document_type,
                'content': content,
                'jurisdiction': jurisdiction,
                'legal_analysis': response.content,
                'safety_score': safety_result,
                'timestamp': datetime.utcnow().isoformat()
            }

            # Record cost and update stats
            self._record_cost(0.10)
            self._update_agent_stats(True)

            duration = (datetime.utcnow() - start_time).total_seconds()
            self._log_execution(True, duration)

            return AgentResult(
                success=True,
                data=result_data,
                message="Legal review completed successfully",
                cost=0.10
            )

        except Exception as e:
            logger.error(f"Legal review failed: {e}")
            self._update_agent_stats(False)
            duration = (datetime.utcnow() - start_time).total_seconds()
            self._log_execution(False, duration)
            return AgentResult(
                success=False,
                data={},
                message=f"Legal review failed: {str(e)}",
                cost=0.0
            )


class HRTeamBuildingAgent(BaseAgent):
    """Agent for HR and team building."""

    def __init__(self, startup_id: str):
        super().__init__('hr_team_building', startup_id)

        self.prompt_template = PromptTemplate(
            input_variables=["company_info", "hiring_needs", "team_size"],
            template="""
            Develop HR strategy and team building plan:

            Company Info: {company_info}
            Hiring Needs: {hiring_needs}
            Current Team Size: {team_size}

            Provide:
            1. Recruitment strategy and job descriptions
            2. Interview process and evaluation criteria
            3. Onboarding and training programs
            4. Team culture and engagement initiatives
            5. Performance management framework
            6. Remote work policies and tools

            Format your response as structured HR strategy.
            """
        )

    async def execute(
        self,
        company_info: str,
        hiring_needs: str,
        team_size: int
    ) -> AgentResult:
        """Execute HR and team building strategy."""
        start_time = datetime.utcnow()
        try:
            # Check budget
            if not self._check_budget(0.08):
                return AgentResult(
                    success=False,
                    data={},
                    message="Insufficient budget for HR strategy",
                    cost=0.0
                )

            # Check content safety
            combined_content = f"{company_info} {hiring_needs}"
            safety_result = self._check_content_safety(combined_content)
            if safety_result['toxicity'] > config.security.content_safety_threshold:
                return AgentResult(
                    success=False,
                    data={},
                    message="Content contains inappropriate material",
                    cost=0.0
                )

            # Generate prompt
            prompt = self.prompt_template.format(
                company_info=company_info,
                hiring_needs=hiring_needs,
                team_size=team_size
            )

            # Execute LLM call
            messages = [
                SystemMessage(content="You are an HR and team building expert."),
                HumanMessage(content=prompt)
            ]

            response = await asyncio.to_thread(
                self.llm.invoke, messages
            )

            # Parse response
            result_data = {
                'company_info': company_info,
                'hiring_needs': hiring_needs,
                'team_size': team_size,
                'hr_strategy': response.content,
                'safety_score': safety_result,
                'timestamp': datetime.utcnow().isoformat()
            }

            # Record cost and update stats
            self._record_cost(0.08)
            self._update_agent_stats(True)

            duration = (datetime.utcnow() - start_time).total_seconds()
            self._log_execution(True, duration)

            return AgentResult(
                success=True,
                data=result_data,
                message="HR strategy completed successfully",
                cost=0.08
            )

        except Exception as e:
            logger.error(f"HR strategy failed: {e}")
            self._update_agent_stats(False)
            duration = (datetime.utcnow() - start_time).total_seconds()
            self._log_execution(False, duration)
            return AgentResult(
                success=False,
                data={},
                message=f"HR strategy failed: {str(e)}",
                cost=0.0
            )


class CustomerSupportScalingAgent(BaseAgent):
    """Agent for customer support and scaling."""

    def __init__(self, startup_id: str):
        super().__init__('customer_support_scaling', startup_id)

        self.prompt_template = PromptTemplate(
            input_variables=["customer_queries", "current_scale", "language"],
            template="""
            Develop customer support and scaling strategy:

            Customer Queries: {customer_queries}
            Current Scale: {current_scale}
            Primary Language: {language}

            Provide:
            1. Support ticket categorization and routing
            2. Response templates and automation
            3. Multilingual support strategy
            4. Scaling recommendations and tools
            5. Customer satisfaction metrics
            6. Support team training and processes

            Format your response as structured support strategy.
            """
        )

    async def execute(
        self,
        customer_queries: str,
        current_scale: str,
        language: str = "en"
    ) -> AgentResult:
        """Execute customer support and scaling strategy."""
        start_time = datetime.utcnow()
        try:
            # Check budget
            if not self._check_budget(0.06):
                return AgentResult(
                    success=False,
                    data={},
                    message="Insufficient budget for support strategy",
                    cost=0.0
                )

            # Check content safety
            combined_content = f"{customer_queries} {current_scale}"
            safety_result = self._check_content_safety(combined_content)
            if safety_result['toxicity'] > config.security.content_safety_threshold:
                return AgentResult(
                    success=False,
                    data={},
                    message="Content contains inappropriate material",
                    cost=0.0
                )

            # Generate prompt
            prompt = self.prompt_template.format(
                customer_queries=customer_queries,
                current_scale=current_scale,
                language=language
            )

            # Execute LLM call
            messages = [
                SystemMessage(content="You are a customer support and scaling expert."),
                HumanMessage(content=prompt)
            ]

            response = await asyncio.to_thread(
                self.llm.invoke, messages
            )

            # Parse response
            result_data = {
                'customer_queries': customer_queries,
                'current_scale': current_scale,
                'language': language,
                'support_strategy': response.content,
                'safety_score': safety_result,
                'timestamp': datetime.utcnow().isoformat()
            }

            # Record cost and update stats
            self._record_cost(0.06)
            self._update_agent_stats(True)

            duration = (datetime.utcnow() - start_time).total_seconds()
            self._log_execution(True, duration)

            return AgentResult(
                success=True,
                data=result_data,
                message="Support strategy completed successfully",
                cost=0.06
            )

        except Exception as e:
            logger.error(f"Support strategy failed: {e}")
            self._update_agent_stats(False)
            duration = (datetime.utcnow() - start_time).total_seconds()
            self._log_execution(False, duration)
            return AgentResult(
                success=False,
                data={},
                message=f"Support strategy failed: {str(e)}",
                cost=0.0
            ) 
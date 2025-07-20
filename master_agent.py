"""Master Agent for autonomous startup orchestration."""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import stripe

from config import config
from utils import (
    budget_manager,
    generate_id,
    log,
    security_utils,
    alert_manager,
    secrets_manager,
    AGENT_EXECUTION_COUNTER,
    AGENT_EXECUTION_DURATION,
    BUDGET_USAGE_GAUGE,
)
from database import db_manager
from agents import (
    NicheResearchAgent,
    MVPDesignAgent,
    MarketingStrategyAgent,
    ContentCreationAgent,
    AnalyticsAgent,
    OperationsMonetizationAgent,
    FundingInvestorAgent,
    LegalComplianceAgent,
    HRTeamBuildingAgent,
    CustomerSupportScalingAgent,
)
from orchestrator import AgentOrchestrator

# Configure logging
logger = logging.getLogger(__name__)


class AutonomyLevel(Enum):
    """Autonomy levels for the platform."""

    MANUAL = "manual"
    SEMI_AUTONOMOUS = "semi_autonomous"
    FULLY_AUTONOMOUS = "fully_autonomous"


class VentureStatus(Enum):
    """Venture status tracking."""

    DISCOVERED = "discovered"
    EVALUATING = "evaluating"
    VIABLE = "viable"
    LAUNCHING = "launching"
    ACTIVE = "active"
    MONETIZING = "monetizing"
    SCALING = "scaling"
    FAILED = "failed"
    PAUSED = "paused"


@dataclass
class VentureOpportunity:
    """Data class for venture opportunities."""

    id: str
    niche: str
    market_size: float
    competition_level: str
    revenue_potential: float
    startup_cost: float
    time_to_market: int  # days
    risk_level: str
    target_markets: List[str]
    language: str
    discovered_at: datetime
    status: VentureStatus
    evaluation_score: float
    metadata: Dict[str, Any]


@dataclass
class IncomeProjection:
    """Income projection for ventures."""

    venture_id: str
    month_1: float
    month_3: float
    month_6: float
    month_12: float
    break_even_month: int
    total_investment: float
    roi_percentage: float
    passive_income_potential: float


class MasterAgent:
    """Master agent for autonomous startup orchestration."""

    def __init__(self, autonomy_level: AutonomyLevel = AutonomyLevel.SEMI_AUTONOMOUS):
        """Initialize master agent."""
        self.autonomy_level = autonomy_level
        self.scheduler = AsyncIOScheduler()
        self.ventures: Dict[str, VentureOpportunity] = {}
        self.income_projections: Dict[str, IncomeProjection] = {}
        self.cycle_count = 0
        self.total_revenue = 0.0
        self.active_ventures = 0

        # Initialize Stripe
        self._initialize_stripe()

        # Configure scheduler
        self._configure_scheduler()

        # Start scheduler
        self.scheduler.start()

        log.info("Master Agent initialized", autonomy_level=autonomy_level.value, scheduler_started=True)

    def _initialize_stripe(self) -> None:
        """Initialize Stripe for payment processing."""
        try:
            stripe_key = secrets_manager.get_secret("STRIPE_SECRET_KEY")
            if stripe_key:
                stripe.api_key = stripe_key
                log.info("Stripe initialized successfully")
            else:
                log.warning("Stripe key not found, payment features disabled")
        except Exception as e:
            log.error(f"Failed to initialize Stripe: {e}")

    def _configure_scheduler(self) -> None:
        """Configure autonomous scheduling."""
        # Daily niche discovery - run immediately for testing
        from datetime import datetime
        self.scheduler.add_job(
            self._discovery_cycle,
            'date',
            run_date=datetime.now(),
            id="daily_discovery",
            name="Daily Niche Discovery",
            replace_existing=True,
        )

        # Weekly evaluation at 9 AM on Mondays
        self.scheduler.add_job(
            self._evaluation_cycle,
            CronTrigger(day_of_week="mon", hour=9, minute=0),
            id="weekly_evaluation",
            name="Weekly Venture Evaluation",
            replace_existing=True,
        )

        # Monthly scaling review at 10 AM on 1st of month
        self.scheduler.add_job(
            self._scaling_cycle,
            CronTrigger(day=1, hour=10, minute=0),
            id="monthly_scaling",
            name="Monthly Scaling Review",
            replace_existing=True,
        )

        # Hourly monitoring
        self.scheduler.add_job(
            self._monitoring_cycle,
            CronTrigger(minute=0),
            id="hourly_monitoring",
            name="Hourly Monitoring",
            replace_existing=True,
        )

    async def _discovery_cycle(self) -> None:
        """Daily autonomous niche discovery cycle."""
        try:
            log.info("Starting daily discovery cycle", cycle_count=self.cycle_count)

            # Check budget for discovery
            if not budget_manager.can_spend(10.0):
                log.warning("Insufficient budget for discovery cycle")
                return

            # Initialize niche research agent
            startup_id = generate_id("discovery")
            niche_agent = NicheResearchAgent(startup_id)

            # Global niche discovery queries
            discovery_queries = [
                "emerging markets 2025",
                "trending products Africa",
                "niche opportunities Asia",
                "passive income ideas",
                "ecommerce trends 2025",
                "content monetization opportunities",
                "SaaS opportunities emerging markets",
                "digital products demand",
                "subscription business ideas",
                "micro-SaaS opportunities",
            ]

            discovered_ventures = []

            for query in discovery_queries:
                try:
                    # Execute niche research
                    result = await niche_agent.execute(
                        niche=query, market_data="Global market analysis for autonomous discovery"
                    )

                    if result.success:
                        # Parse discovered niches
                        niches = self._parse_discovery_results(result.data)

                        for niche in niches:
                            venture = self._create_venture_opportunity(niche, query)
                            if venture:
                                discovered_ventures.append(venture)
                                self.ventures[venture.id] = venture

                    # Rate limiting
                    await asyncio.sleep(2)

                except Exception as e:
                    log.error(f"Discovery query failed: {query}, error: {e}")
                    continue

            # Log discovery results
            log.info(
                "Discovery cycle completed",
                ventures_discovered=len(discovered_ventures),
                total_ventures=len(self.ventures),
            )

            # Send discovery report
            await self._send_discovery_report(discovered_ventures)

        except Exception as e:
            log.error(f"Discovery cycle failed: {e}")
            alert_manager.send_slack_alert(f"Discovery cycle failed: {e}")

    async def _evaluation_cycle(self) -> None:
        """Weekly venture evaluation and launch cycle."""
        try:
            log.info("Starting weekly evaluation cycle")

            # Get ventures to evaluate
            pending_ventures = [v for v in self.ventures.values() if v.status == VentureStatus.DISCOVERED]

            for venture in pending_ventures[:5]:  # Limit to 5 per cycle
                try:
                    # Evaluate venture viability
                    is_viable = await self._evaluate_venture(venture)

                    if is_viable:
                        # Launch venture
                        await self._launch_venture(venture)
                    else:
                        venture.status = VentureStatus.FAILED
                        log.info(f"Venture {venture.niche} marked as non-viable")

                except Exception as e:
                    log.error(f"Venture evaluation failed: {venture.id}, error: {e}")
                    continue

            # Update venture statuses
            self._update_venture_statuses()

        except Exception as e:
            log.error(f"Evaluation cycle failed: {e}")
            alert_manager.send_slack_alert(f"Evaluation cycle failed: {e}")

    async def _scaling_cycle(self) -> None:
        """Monthly scaling and optimization cycle."""
        try:
            log.info("Starting monthly scaling cycle")

            # Get active ventures
            active_ventures = [
                v for v in self.ventures.values() if v.status in [VentureStatus.ACTIVE, VentureStatus.MONETIZING]
            ]

            for venture in active_ventures:
                try:
                    # Analyze performance
                    performance = await self._analyze_venture_performance(venture)

                    # Optimize if needed
                    if performance["needs_optimization"]:
                        await self._optimize_venture(venture, performance)

                    # Scale if profitable
                    if performance["should_scale"]:
                        await self._scale_venture(venture)

                except Exception as e:
                    log.error(f"Venture scaling failed: {venture.id}, error: {e}")
                    continue

            # Generate monthly report
            await self._generate_monthly_report()

        except Exception as e:
            log.error(f"Scaling cycle failed: {e}")
            alert_manager.send_slack_alert(f"Scaling cycle failed: {e}")

    async def _monitoring_cycle(self) -> None:
        """Hourly monitoring and alerting cycle."""
        try:
            # Check budget
            remaining_budget = budget_manager.get_remaining_budget()
            if remaining_budget < 50.0:
                alert_manager.send_slack_alert(f"Low budget alert: ${remaining_budget:.2f} remaining")

            # Check active ventures
            active_count = len(
                [
                    v
                    for v in self.ventures.values()
                    if v.status in [VentureStatus.ACTIVE, VentureStatus.MONETIZING, VentureStatus.SCALING]
                ]
            )

            # Update metrics
            BUDGET_USAGE_GAUGE.set(500.0 - remaining_budget)

            # Log monitoring status
            log.info(
                "Monitoring cycle completed",
                remaining_budget=remaining_budget,
                active_ventures=active_count,
                total_ventures=len(self.ventures),
            )

        except Exception as e:
            log.error(f"Monitoring cycle failed: {e}")

    def _parse_discovery_results(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse discovery results into structured niches."""
        niches = []

        try:
            # Extract niches from AI response
            content = data.get("analysis", "")

            # Simple parsing - in production, use more sophisticated NLP
            lines = content.split("\n")
            for line in lines:
                if any(keyword in line.lower() for keyword in ["niche", "opportunity", "market", "trend"]):
                    niches.append(
                        {
                            "name": line.strip(),
                            "source": data.get("niche", ""),
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                    )

        except Exception as e:
            log.error(f"Failed to parse discovery results: {e}")

        return niches

    def _create_venture_opportunity(self, niche_data: Dict[str, Any], source: str) -> Optional[VentureOpportunity]:
        """Create venture opportunity from discovered niche."""
        try:
            venture_id = generate_id("venture")

            # Estimate market metrics (in production, use real market data APIs)
            market_size = self._estimate_market_size(niche_data["name"])
            revenue_potential = market_size * 0.01  # 1% market capture
            startup_cost = min(revenue_potential * 0.1, 100.0)  # 10% of revenue potential, max $100

            venture = VentureOpportunity(
                id=venture_id,
                niche=niche_data["name"],
                market_size=market_size,
                competition_level=self._assess_competition(niche_data["name"]),
                revenue_potential=revenue_potential,
                startup_cost=startup_cost,
                time_to_market=30,  # 30 days
                risk_level=self._assess_risk(niche_data["name"]),
                target_markets=["global"],
                language="en",
                discovered_at=datetime.utcnow(),
                status=VentureStatus.DISCOVERED,
                evaluation_score=0.0,
                metadata={"source": source, "discovery_method": "autonomous_scraping", "ai_generated": True},
            )

            return venture

        except Exception as e:
            log.error(f"Failed to create venture opportunity: {e}")
            return None

    def _estimate_market_size(self, niche: str) -> float:
        """Estimate market size for niche (simplified)."""
        # In production, integrate with market research APIs
        base_size = 1000000.0  # $1M base market

        # Adjust based on keywords
        if "ecommerce" in niche.lower():
            return base_size * 5
        elif "saas" in niche.lower():
            return base_size * 3
        elif "content" in niche.lower():
            return base_size * 2
        elif "mobile" in niche.lower():
            return base_size * 4
        else:
            return base_size

    def _assess_competition(self, niche: str) -> str:
        """Assess competition level for niche."""
        # Simplified assessment - in production, use real competition analysis
        if any(word in niche.lower() for word in ["emerging", "new", "trending"]):
            return "low"
        elif any(word in niche.lower() for word in ["established", "popular"]):
            return "high"
        else:
            return "medium"

    def _assess_risk(self, niche: str) -> str:
        """Assess risk level for niche."""
        # Simplified risk assessment
        if any(word in niche.lower() for word in ["regulated", "legal", "financial"]):
            return "high"
        elif any(word in niche.lower() for word in ["content", "digital", "online"]):
            return "low"
        else:
            return "medium"

    async def _evaluate_venture(self, venture: VentureOpportunity) -> bool:
        """Evaluate venture viability using AI agents."""
        try:
            # Check budget for evaluation
            if not budget_manager.can_spend(venture.startup_cost):
                log.warning(f"Insufficient budget for venture {venture.id}")
                return False

            # Create orchestrator for evaluation
            orchestrator = AgentOrchestrator(venture.id)

            # Evaluation workflow
            evaluation_config = {
                "niche_research": {
                    "niche": venture.niche,
                    "market_data": f"Market size: ${venture.market_size:,.0f}, Competition: {venture.competition_level}",
                },
                "analytics": {
                    "data": f"Venture: {venture.niche}, Revenue potential: ${venture.revenue_potential:,.0f}",
                    "metrics": "market_size,competition,revenue_potential,risk_level",
                    "questions": "Is this venture viable? What are the key success factors?",
                },
            }

            # Execute evaluation
            result = await orchestrator.execute_workflow(evaluation_config)

            if result.success:
                # Parse evaluation results
                evaluation_score = self._parse_evaluation_score(result.results)
                venture.evaluation_score = evaluation_score

                # Determine viability (score > 0.7)
                is_viable = evaluation_score > 0.7

                log.info(f"Venture {venture.niche} evaluated", score=evaluation_score, viable=is_viable)

                return is_viable
            else:
                log.warning(f"Venture evaluation failed: {venture.id}")
                return False

        except Exception as e:
            log.error(f"Venture evaluation failed: {venture.id}, error: {e}")
            return False

    def _parse_evaluation_score(self, results: Dict[str, Any]) -> float:
        """Parse evaluation score from AI results."""
        try:
            # Extract score from analytics results
            analytics_data = results.get("analytics", {})
            analysis = analytics_data.get("analysis", "")

            # Simple scoring - in production, use more sophisticated analysis
            positive_keywords = ["viable", "profitable", "opportunity", "potential", "success"]
            negative_keywords = ["risky", "saturated", "difficult", "challenging", "unviable"]

            positive_count = sum(1 for keyword in positive_keywords if keyword in analysis.lower())
            negative_count = sum(1 for keyword in negative_keywords if keyword in analysis.lower())

            if positive_count + negative_count == 0:
                return 0.5  # Neutral score

            score = positive_count / (positive_count + negative_count)
            return min(max(score, 0.0), 1.0)  # Clamp between 0 and 1

        except Exception as e:
            log.error(f"Failed to parse evaluation score: {e}")
            return 0.5

    async def _launch_venture(self, venture: VentureOpportunity) -> None:
        """Launch a viable venture."""
        try:
            log.info(f"Launching venture: {venture.niche}")

            # Update status
            venture.status = VentureStatus.LAUNCHING

            # Create orchestrator for launch
            orchestrator = AgentOrchestrator(venture.id)

            # Launch workflow
            launch_config = {
                "mvp_design": {
                    "niche": venture.niche,
                    "target_audience": "global",
                    "requirements": "minimal viable product for rapid launch",
                },
                "marketing_strategy": {
                    "product": venture.niche,
                    "target_audience": "global",
                    "budget": venture.startup_cost,
                },
                "operations_monetization": {
                    "current_operations": "startup phase",
                    "revenue_data": f"Projected revenue: ${venture.revenue_potential:,.0f}",
                },
            }

            # Execute launch
            result = await orchestrator.execute_workflow(launch_config)

            if result.success:
                venture.status = VentureStatus.ACTIVE
                self.active_ventures += 1

                # Create income projection
                projection = self._create_income_projection(venture)
                self.income_projections[venture.id] = projection

                log.info(f"Venture {venture.niche} launched successfully")

                # Send launch notification
                await self._send_launch_notification(venture)
            else:
                venture.status = VentureStatus.FAILED
                log.error(f"Venture launch failed: {venture.niche}")

        except Exception as e:
            log.error(f"Venture launch failed: {venture.id}, error: {e}")
            venture.status = VentureStatus.FAILED

    def _create_income_projection(self, venture: VentureOpportunity) -> IncomeProjection:
        """Create income projection for venture."""
        try:
            # Base projection on market size and competition
            base_monthly = venture.revenue_potential / 12

            # Growth factors
            if venture.competition_level == "low":
                growth_factor = 1.5
            elif venture.competition_level == "medium":
                growth_factor = 1.2
            else:
                growth_factor = 1.0

            # Monthly projections
            month_1 = base_monthly * 0.1  # 10% of potential in first month
            month_3 = base_monthly * 0.3 * growth_factor
            month_6 = base_monthly * 0.6 * growth_factor
            month_12 = base_monthly * growth_factor

            # Calculate break-even
            total_investment = venture.startup_cost
            cumulative_revenue = 0
            break_even_month = 0

            for month in range(1, 13):
                if month == 1:
                    cumulative_revenue = month_1
                elif month == 3:
                    cumulative_revenue = month_1 + month_3
                elif month == 6:
                    cumulative_revenue = month_1 + month_3 + month_6
                elif month == 12:
                    cumulative_revenue = month_1 + month_3 + month_6 + month_12

                if cumulative_revenue >= total_investment and break_even_month == 0:
                    break_even_month = month

            roi_percentage = ((month_12 * 12) - total_investment) / total_investment * 100
            passive_income_potential = month_12 * 0.8  # 80% of month 12 as passive income

            return IncomeProjection(
                venture_id=venture.id,
                month_1=month_1,
                month_3=month_3,
                month_6=month_6,
                month_12=month_12,
                break_even_month=break_even_month,
                total_investment=total_investment,
                roi_percentage=roi_percentage,
                passive_income_potential=passive_income_potential,
            )

        except Exception as e:
            log.error(f"Failed to create income projection: {e}")
            return None

    async def _analyze_venture_performance(self, venture: VentureOpportunity) -> Dict[str, Any]:
        """Analyze venture performance."""
        try:
            # Get income projection
            projection = self.income_projections.get(venture.id)

            if not projection:
                return {"needs_optimization": False, "should_scale": False}

            # Simple performance analysis
            current_month = (datetime.utcnow() - venture.discovered_at).days // 30 + 1

            if current_month == 1:
                expected_revenue = projection.month_1
            elif current_month == 3:
                expected_revenue = projection.month_3
            elif current_month == 6:
                expected_revenue = projection.month_6
            else:
                expected_revenue = projection.month_12

            # Performance metrics (simplified - in production, use real revenue data)
            performance_ratio = 0.8  # 80% of expected revenue (simulated)

            needs_optimization = performance_ratio < 0.7
            should_scale = performance_ratio > 1.2 and current_month >= 3

            return {
                "needs_optimization": needs_optimization,
                "should_scale": should_scale,
                "performance_ratio": performance_ratio,
                "expected_revenue": expected_revenue,
                "current_month": current_month,
            }

        except Exception as e:
            log.error(f"Performance analysis failed: {venture.id}, error: {e}")
            return {"needs_optimization": False, "should_scale": False}

    async def _optimize_venture(self, venture: VentureOpportunity, performance: Dict[str, Any]) -> None:
        """Optimize underperforming venture."""
        try:
            log.info(f"Optimizing venture: {venture.niche}")

            # Create optimization workflow
            orchestrator = AgentOrchestrator(venture.id)

            optimization_config = {
                "analytics": {
                    "data": f"Venture: {venture.niche}, Performance: {performance['performance_ratio']:.2f}",
                    "metrics": "revenue,conversion,engagement",
                    "questions": "What optimizations can improve performance?",
                },
                "marketing_strategy": {
                    "product": venture.niche,
                    "target_audience": "optimized targeting",
                    "budget": venture.startup_cost * 0.2,  # 20% additional budget
                },
            }

            result = await orchestrator.execute_workflow(optimization_config)

            if result.success:
                log.info(f"Venture {venture.niche} optimized successfully")
            else:
                log.warning(f"Venture optimization failed: {venture.niche}")

        except Exception as e:
            log.error(f"Venture optimization failed: {venture.id}, error: {e}")

    async def _scale_venture(self, venture: VentureOpportunity) -> None:
        """Scale profitable venture."""
        try:
            log.info(f"Scaling venture: {venture.niche}")

            # Update status
            venture.status = VentureStatus.SCALING

            # Create scaling workflow
            orchestrator = AgentOrchestrator(venture.id)

            scaling_config = {
                "funding_investor": {
                    "startup_info": f"Profitable venture: {venture.niche}",
                    "funding_stage": "growth",
                    "target_amount": venture.revenue_potential * 0.5,  # 50% of revenue potential
                },
                "customer_support_scaling": {
                    "customer_queries": "scaling support operations",
                    "current_scale": "growing customer base",
                    "language": venture.language,
                },
            }

            result = await orchestrator.execute_workflow(scaling_config)

            if result.success:
                log.info("Venture {} scaled successfully".format(venture.niche))
            else:
                log.warning("Venture scaling failed: {}".format(venture.niche))

        except Exception as e:
            log.error("Venture scaling failed: {}, error: {}".format(venture.id, e))

    def _update_venture_statuses(self) -> None:
        """Update venture statuses based on time and performance."""
        current_time = datetime.utcnow()

        for venture in self.ventures.values():
            days_since_discovery = (current_time - venture.discovered_at).days

            # Auto-update statuses based on time
            if venture.status == VentureStatus.LAUNCHING and days_since_discovery > 7:
                venture.status = VentureStatus.ACTIVE

            elif venture.status == VentureStatus.ACTIVE and days_since_discovery > 30:
                venture.status = VentureStatus.MONETIZING

    async def _send_discovery_report(self, discovered_ventures: List[VentureOpportunity]) -> None:
        """Send discovery report via email/Slack."""
        try:
            if not discovered_ventures:
                return

            report = "🔍 **Daily Discovery Report**\n\n"
            report += f"**Ventures Discovered**: {len(discovered_ventures)}\n"
            report += f"**Total Ventures**: {len(self.ventures)}\n\n"

            for venture in discovered_ventures[:3]:  # Top 3
                report += f"• **{venture.niche}**\n"
                report += f"  - Market: ${venture.market_size:,.0f}\n"
                report += f"  - Revenue Potential: ${venture.revenue_potential:,.0f}\n"
                report += f"  - Competition: {venture.competition_level}\n\n"

            # Send to Slack
            alert_manager.send_slack_alert(report)

            # Send email if configured
            if config.monitoring.alert_email:
                alert_manager.send_email_alert("Daily Discovery Report", report)

        except Exception as e:
            log.error(f"Failed to send discovery report: {e}")

    async def _send_launch_notification(self, venture: VentureOpportunity) -> None:
        """Send launch notification."""
        try:
            notification = "🚀 **Venture Launched**\n\n"
            notification += f"**Venture**: {venture.niche}\n"
            notification += f"**Revenue Potential**: ${venture.revenue_potential:,.0f}\n"
            notification += f"**Startup Cost**: ${venture.startup_cost:.2f}\n"
            notification += f"**Active Ventures**: {self.active_ventures}\n"

            alert_manager.send_slack_alert(notification)

        except Exception as e:
            log.error(f"Failed to send launch notification: {e}")

    async def _generate_monthly_report(self) -> None:
        """Generate monthly performance report."""
        try:
            active_ventures = [
                v
                for v in self.ventures.values()
                if v.status in [VentureStatus.ACTIVE, VentureStatus.MONETIZING, VentureStatus.SCALING]
            ]

            total_projected_revenue = sum(
                self.income_projections.get(v.id, IncomeProjection(v.id, 0, 0, 0, 0, 0, 0, 0, 0)).month_12
                for v in active_ventures
            )

            report = "📊 **Monthly Performance Report**\n\n"
            report += f"**Active Ventures**: {len(active_ventures)}\n"
            report += f"**Total Ventures**: {len(self.ventures)}\n"
            report += f"**Projected Annual Revenue**: ${total_projected_revenue:,.0f}\n"
            report += f"**Remaining Budget**: ${budget_manager.get_remaining_budget():.2f}\n\n"

            # Top performing ventures
            top_ventures = sorted(
                active_ventures,
                key=lambda v: self.income_projections.get(
                    v.id, IncomeProjection(v.id, 0, 0, 0, 0, 0, 0, 0, 0)
                ).month_12,
                reverse=True,
            )[:3]

            report += "**Top Performing Ventures**:\n"
            for venture in top_ventures:
                projection = self.income_projections.get(venture.id)
                if projection:
                    report += f"• {venture.niche}: ${projection.month_12:,.0f}/month\n"

            alert_manager.send_slack_alert(report)

        except Exception as e:
            log.error(f"Failed to generate monthly report: {e}")

    def get_master_status(self) -> Dict[str, Any]:
        """Get master agent status."""
        return {
            "autonomy_level": self.autonomy_level.value,
            "scheduler_running": self.scheduler.running,
            "total_ventures": len(self.ventures),
            "active_ventures": self.active_ventures,
            "cycle_count": self.cycle_count,
            "total_revenue": self.total_revenue,
            "remaining_budget": budget_manager.get_remaining_budget(),
            "next_discovery": (
                self.scheduler.get_job("daily_discovery").next_run_time.isoformat()
                if self.scheduler.get_job("daily_discovery")
                else None
            ),
            "next_evaluation": (
                self.scheduler.get_job("weekly_evaluation").next_run_time.isoformat()
                if self.scheduler.get_job("weekly_evaluation")
                else None
            ),
        }

    def get_income_summary(self) -> Dict[str, Any]:
        """Get income summary across all ventures."""
        try:
            total_projected_annual = sum(proj.month_12 * 12 for proj in self.income_projections.values())

            total_passive_income = sum(proj.passive_income_potential for proj in self.income_projections.values())

            active_projections = [
                proj
                for proj in self.income_projections.values()
                if any(
                    v.id == proj.venture_id
                    and v.status in [VentureStatus.ACTIVE, VentureStatus.MONETIZING, VentureStatus.SCALING]
                    for v in self.ventures.values()
                )
            ]

            return {
                "total_projected_annual": total_projected_annual,
                "total_passive_income_monthly": total_passive_income,
                "active_ventures_count": len(active_projections),
                "average_roi": (
                    sum(proj.roi_percentage for proj in active_projections) / len(active_projections)
                    if active_projections
                    else 0
                ),
                "break_even_ventures": len([proj for proj in active_projections if proj.break_even_month <= 6]),
                "high_potential_ventures": len([proj for proj in active_projections if proj.roi_percentage > 200]),
            }

        except Exception as e:
            log.error(f"Failed to get income summary: {e}")
            return {}

    def shutdown(self) -> None:
        """Shutdown master agent."""
        try:
            self.scheduler.shutdown()
            log.info("Master Agent shutdown completed")
        except Exception as e:
            log.error(f"Master Agent shutdown failed: {e}")


# Global master agent instance
_master_agent = None


def get_master_agent(autonomy_level: AutonomyLevel = AutonomyLevel.SEMI_AUTONOMOUS) -> MasterAgent:
    """Get or create master agent instance."""
    global _master_agent
    if _master_agent is None:
        _master_agent = MasterAgent(autonomy_level)
    return _master_agent

"""Income Scenario Simulator for AutoPilot Ventures."""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import random
import math

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.figure import Figure
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from config import config
from utils import budget_manager, generate_id, log, security_utils, MetricsUtils

# Configure logging
logger = logging.getLogger(__name__)


class VentureType(Enum):
    """Types of ventures for income simulation."""

    SAAS = "saas"
    ECOMMERCE = "ecommerce"
    CONTENT_MONETIZATION = "content_monetization"
    DIGITAL_PRODUCTS = "digital_products"
    SUBSCRIPTION_SERVICE = "subscription_service"
    MICRO_SAAS = "micro_saas"
    AFFILIATE_MARKETING = "affiliate_marketing"
    ONLINE_COURSE = "online_course"
    MOBILE_APP = "mobile_app"
    API_SERVICE = "api_service"


class MarketCondition(Enum):
    """Market conditions affecting venture performance."""

    BULL_MARKET = "bull_market"
    BEAR_MARKET = "bear_market"
    STABLE_MARKET = "stable_market"
    VOLATILE_MARKET = "volatile_market"


@dataclass
class VentureScenario:
    """Venture scenario configuration."""

    venture_type: VentureType
    initial_investment: float
    market_condition: MarketCondition
    target_market_size: float
    competition_level: str
    marketing_budget: float
    time_to_market: int  # days
    team_size: int
    location: str
    language: str
    niche_specificity: float  # 0-1, how specific the niche is
    automation_level: float  # 0-1, how automated the venture is


@dataclass
class IncomeProjection:
    """Detailed income projection for a venture."""

    venture_id: str
    scenario: VentureScenario
    month_1: float
    month_3: float
    month_6: float
    month_12: float
    month_24: float
    break_even_month: int
    total_investment: float
    roi_percentage: float
    passive_income_potential: float
    monthly_recurring_revenue: float
    customer_lifetime_value: float
    customer_acquisition_cost: float
    churn_rate: float
    growth_rate: float
    market_share: float
    profitability_margin: float
    cash_flow_positive_month: int
    valuation_multiple: float
    projected_valuation: float


class IncomeSimulator:
    """Advanced income scenario simulator for ventures."""

    def __init__(self):
        """Initialize the income simulator."""
        self.venture_scenarios = {}
        self.income_projections = {}
        self.market_data = self._load_market_data()
        self.risk_factors = self._load_risk_factors()

        # Set random seed for reproducible results
        random.seed(42)
        np.random.seed(42)

    def _load_market_data(self) -> Dict[str, Any]:
        """Load market data for different venture types."""
        return {
            VentureType.SAAS.value: {
                "avg_mrr_growth": 0.15,
                "avg_churn_rate": 0.05,
                "avg_cac": 150.0,
                "avg_ltv": 3000.0,
                "avg_valuation_multiple": 10.0,
                "success_rate": 0.25,
            },
            VentureType.ECOMMERCE.value: {
                "avg_mrr_growth": 0.08,
                "avg_churn_rate": 0.02,
                "avg_cac": 25.0,
                "avg_ltv": 150.0,
                "avg_valuation_multiple": 3.0,
                "success_rate": 0.15,
            },
            VentureType.CONTENT_MONETIZATION.value: {
                "avg_mrr_growth": 0.12,
                "avg_churn_rate": 0.03,
                "avg_cac": 5.0,
                "avg_ltv": 200.0,
                "avg_valuation_multiple": 5.0,
                "success_rate": 0.30,
            },
            VentureType.DIGITAL_PRODUCTS.value: {
                "avg_mrr_growth": 0.10,
                "avg_churn_rate": 0.01,
                "avg_cac": 15.0,
                "avg_ltv": 100.0,
                "avg_valuation_multiple": 4.0,
                "success_rate": 0.35,
            },
            VentureType.SUBSCRIPTION_SERVICE.value: {
                "avg_mrr_growth": 0.18,
                "avg_churn_rate": 0.04,
                "avg_cac": 80.0,
                "avg_ltv": 1200.0,
                "avg_valuation_multiple": 8.0,
                "success_rate": 0.20,
            },
            VentureType.MICRO_SAAS.value: {
                "avg_mrr_growth": 0.20,
                "avg_churn_rate": 0.06,
                "avg_cac": 50.0,
                "avg_ltv": 800.0,
                "avg_valuation_multiple": 12.0,
                "success_rate": 0.40,
            },
            VentureType.AFFILIATE_MARKETING.value: {
                "avg_mrr_growth": 0.05,
                "avg_churn_rate": 0.01,
                "avg_cac": 2.0,
                "avg_ltv": 50.0,
                "avg_valuation_multiple": 2.0,
                "success_rate": 0.25,
            },
            VentureType.ONLINE_COURSE.value: {
                "avg_mrr_growth": 0.08,
                "avg_churn_rate": 0.02,
                "avg_cac": 30.0,
                "avg_ltv": 300.0,
                "avg_valuation_multiple": 6.0,
                "success_rate": 0.30,
            },
            VentureType.MOBILE_APP.value: {
                "avg_mrr_growth": 0.12,
                "avg_churn_rate": 0.08,
                "avg_cac": 100.0,
                "avg_ltv": 200.0,
                "avg_valuation_multiple": 7.0,
                "success_rate": 0.15,
            },
            VentureType.API_SERVICE.value: {
                "avg_mrr_growth": 0.16,
                "avg_churn_rate": 0.03,
                "avg_cac": 200.0,
                "avg_ltv": 5000.0,
                "avg_valuation_multiple": 15.0,
                "success_rate": 0.25,
            },
        }

    def _load_risk_factors(self) -> Dict[str, float]:
        """Load risk factors for different market conditions."""
        return {
            MarketCondition.BULL_MARKET.value: {
                "growth_multiplier": 1.3,
                "success_rate_multiplier": 1.2,
                "valuation_multiplier": 1.4,
            },
            MarketCondition.BEAR_MARKET.value: {
                "growth_multiplier": 0.7,
                "success_rate_multiplier": 0.8,
                "valuation_multiplier": 0.6,
            },
            MarketCondition.STABLE_MARKET.value: {
                "growth_multiplier": 1.0,
                "success_rate_multiplier": 1.0,
                "valuation_multiplier": 1.0,
            },
            MarketCondition.VOLATILE_MARKET.value: {
                "growth_multiplier": 0.9,
                "success_rate_multiplier": 0.9,
                "valuation_multiplier": 0.8,
            },
        }

    def create_venture_scenario(
        self,
        venture_type: VentureType,
        initial_investment: float,
        market_condition: MarketCondition = MarketCondition.STABLE_MARKET,
        target_market_size: float = 1000000.0,
        competition_level: str = "medium",
        marketing_budget: float = 1000.0,
        time_to_market: int = 90,
        team_size: int = 1,
        location: str = "US",
        language: str = "en",
        niche_specificity: float = 0.7,
        automation_level: float = 0.8,
    ) -> str:
        """Create a new venture scenario."""

        scenario_id = generate_id("scenario")

        scenario = VentureScenario(
            venture_type=venture_type,
            initial_investment=initial_investment,
            market_condition=market_condition,
            target_market_size=target_market_size,
            competition_level=competition_level,
            marketing_budget=marketing_budget,
            time_to_market=time_to_market,
            team_size=team_size,
            location=location,
            language=language,
            niche_specificity=niche_specificity,
            automation_level=automation_level,
        )

        self.venture_scenarios[scenario_id] = scenario

        log.info(
            "Venture scenario created",
            scenario_id=scenario_id,
            venture_type=venture_type.value,
            initial_investment=initial_investment,
            market_condition=market_condition.value,
        )

        return scenario_id

    def simulate_income_projection(self, scenario_id: str) -> IncomeProjection:
        """Simulate income projection for a venture scenario."""

        if scenario_id not in self.venture_scenarios:
            raise ValueError(f"Scenario {scenario_id} not found")

        scenario = self.venture_scenarios[scenario_id]
        market_data = self.market_data[scenario.venture_type.value]
        risk_factors = self.risk_factors[scenario.market_condition.value]

        # Calculate base metrics with market condition adjustments
        base_growth_rate = market_data["avg_mrr_growth"] * risk_factors["growth_multiplier"]
        base_churn_rate = market_data["avg_churn_rate"]
        base_cac = market_data["avg_cac"]
        base_ltv = market_data["avg_ltv"]

        # Apply scenario-specific adjustments
        growth_rate = self._adjust_growth_rate(base_growth_rate, scenario)
        churn_rate = self._adjust_churn_rate(base_churn_rate, scenario)
        cac = self._adjust_cac(base_cac, scenario)
        ltv = self._adjust_ltv(base_ltv, scenario)

        # Calculate monthly revenue projections
        monthly_revenues = self._calculate_monthly_revenues(scenario, growth_rate, churn_rate, cac, ltv)

        # Calculate key metrics
        break_even_month = self._calculate_break_even_month(scenario.initial_investment, monthly_revenues)

        total_investment = scenario.initial_investment + scenario.marketing_budget
        roi_percentage = self._calculate_roi(total_investment, monthly_revenues[23])  # 24 months

        passive_income_potential = self._calculate_passive_income_potential(monthly_revenues, scenario.automation_level)

        mrr_12_months = monthly_revenues[11]  # Month 12
        valuation_multiple = market_data["avg_valuation_multiple"] * risk_factors["valuation_multiplier"]
        projected_valuation = mrr_12_months * 12 * valuation_multiple

        # Create income projection
        projection = IncomeProjection(
            venture_id=scenario_id,
            scenario=scenario,
            month_1=monthly_revenues[0],
            month_3=monthly_revenues[2],
            month_6=monthly_revenues[5],
            month_12=monthly_revenues[11],
            month_24=monthly_revenues[23],
            break_even_month=break_even_month,
            total_investment=total_investment,
            roi_percentage=roi_percentage,
            passive_income_potential=passive_income_potential,
            monthly_recurring_revenue=mrr_12_months,
            customer_lifetime_value=ltv,
            customer_acquisition_cost=cac,
            churn_rate=churn_rate,
            growth_rate=growth_rate,
            market_share=self._calculate_market_share(scenario),
            profitability_margin=self._calculate_profitability_margin(monthly_revenues[11], scenario),
            cash_flow_positive_month=self._calculate_cash_flow_positive_month(monthly_revenues, scenario),
            valuation_multiple=valuation_multiple,
            projected_valuation=projected_valuation,
        )

        self.income_projections[scenario_id] = projection

        log.info(
            "Income projection simulated",
            scenario_id=scenario_id,
            roi_percentage=roi_percentage,
            break_even_month=break_even_month,
            projected_valuation=projected_valuation,
        )

        return projection

    def _adjust_growth_rate(self, base_rate: float, scenario: VentureScenario) -> float:
        """Adjust growth rate based on scenario factors."""
        adjustment = 1.0

        # Niche specificity impact
        adjustment *= 0.8 + scenario.niche_specificity * 0.4

        # Team size impact
        adjustment *= 0.9 + min(scenario.team_size, 5) * 0.02

        # Competition level impact
        competition_impact = {"low": 1.2, "medium": 1.0, "high": 0.8}
        adjustment *= competition_impact.get(scenario.competition_level, 1.0)

        # Marketing budget impact
        budget_ratio = scenario.marketing_budget / scenario.initial_investment
        adjustment *= 0.9 + min(budget_ratio, 0.5) * 0.2

        return base_rate * adjustment

    def _adjust_churn_rate(self, base_rate: float, scenario: VentureScenario) -> float:
        """Adjust churn rate based on scenario factors."""
        adjustment = 1.0

        # Automation level impact
        adjustment *= 1.2 - scenario.automation_level * 0.4

        # Team size impact
        adjustment *= 1.1 - min(scenario.team_size, 3) * 0.03

        return base_rate * adjustment

    def _adjust_cac(self, base_cac: float, scenario: VentureScenario) -> float:
        """Adjust customer acquisition cost based on scenario factors."""
        adjustment = 1.0

        # Competition level impact
        competition_impact = {"low": 0.8, "medium": 1.0, "high": 1.3}
        adjustment *= competition_impact.get(scenario.competition_level, 1.0)

        # Market size impact
        market_size_ratio = scenario.target_market_size / 1000000.0
        adjustment *= 1.1 - min(market_size_ratio, 1.0) * 0.1

        return base_cac * adjustment

    def _adjust_ltv(self, base_ltv: float, scenario: VentureScenario) -> float:
        """Adjust customer lifetime value based on scenario factors."""
        adjustment = 1.0

        # Niche specificity impact
        adjustment *= 1.1 + scenario.niche_specificity * 0.3

        # Automation level impact
        adjustment *= 1.0 + scenario.automation_level * 0.2

        return base_ltv * adjustment

    def _calculate_monthly_revenues(
        self, scenario: VentureScenario, growth_rate: float, churn_rate: float, cac: float, ltv: float
    ) -> List[float]:
        """Calculate monthly revenue projections for 24 months."""

        monthly_revenues = []
        current_revenue = 0.0
        current_customers = 0

        for month in range(24):
            # Calculate new customer acquisitions
            marketing_efficiency = min(scenario.marketing_budget / (month + 1), 1000) / 1000
            new_customers = int(marketing_efficiency * 50 * (1 + growth_rate * month))

            # Apply churn
            churned_customers = int(current_customers * churn_rate)
            current_customers = max(0, current_customers - churned_customers + new_customers)

            # Calculate revenue
            current_revenue = current_customers * (ltv / 12)  # Monthly value per customer

            # Apply market condition volatility
            volatility = (
                random.uniform(0.9, 1.1) if scenario.market_condition == MarketCondition.VOLATILE_MARKET else 1.0
            )
            current_revenue *= volatility

            monthly_revenues.append(current_revenue)

        return monthly_revenues

    def _calculate_break_even_month(self, initial_investment: float, monthly_revenues: List[float]) -> int:
        """Calculate break-even month."""
        cumulative_revenue = 0.0

        for month, revenue in enumerate(monthly_revenues):
            cumulative_revenue += revenue
            if cumulative_revenue >= initial_investment:
                return month + 1

        return 24  # Never breaks even

    def _calculate_roi(self, total_investment: float, final_revenue: float) -> float:
        """Calculate ROI percentage."""
        if total_investment == 0:
            return 0.0
        return ((final_revenue - total_investment) / total_investment) * 100

    def _calculate_passive_income_potential(self, monthly_revenues: List[float], automation_level: float) -> float:
        """Calculate passive income potential."""
        # Use month 12 revenue as base
        base_revenue = monthly_revenues[11]
        return base_revenue * automation_level * 0.8  # 80% of automated revenue is passive

    def _calculate_market_share(self, scenario: VentureScenario) -> float:
        """Calculate estimated market share."""
        # Simplified calculation based on target market size and competition
        competition_factor = {"low": 0.05, "medium": 0.02, "high": 0.01}

        base_share = competition_factor.get(scenario.competition_level, 0.02)
        return base_share * scenario.niche_specificity

    def _calculate_profitability_margin(self, monthly_revenue: float, scenario: VentureScenario) -> float:
        """Calculate profitability margin."""
        if monthly_revenue == 0:
            return 0.0

        # Simplified cost calculation
        operational_costs = scenario.initial_investment * 0.1  # 10% of initial investment per month
        profit = monthly_revenue - operational_costs

        return (profit / monthly_revenue) * 100 if monthly_revenue > 0 else 0.0

    def _calculate_cash_flow_positive_month(self, monthly_revenues: List[float], scenario: VentureScenario) -> int:
        """Calculate when cash flow becomes positive."""
        operational_costs = scenario.initial_investment * 0.1  # Monthly operational costs

        for month, revenue in enumerate(monthly_revenues):
            if revenue > operational_costs:
                return month + 1

        return 24  # Never cash flow positive

    def generate_portfolio_simulation(self, num_ventures: int = 10) -> Dict[str, Any]:
        """Generate a portfolio simulation with multiple ventures."""

        portfolio_scenarios = []
        portfolio_projections = []

        venture_types = list(VentureType)
        market_conditions = list(MarketCondition)

        for i in range(num_ventures):
            # Randomly select venture parameters
            venture_type = random.choice(venture_types)
            market_condition = random.choice(market_conditions)
            initial_investment = random.uniform(1000, 50000)
            marketing_budget = initial_investment * random.uniform(0.1, 0.5)

            # Create scenario
            scenario_id = self.create_venture_scenario(
                venture_type=venture_type,
                initial_investment=initial_investment,
                market_condition=market_condition,
                marketing_budget=marketing_budget,
                niche_specificity=random.uniform(0.5, 1.0),
                automation_level=random.uniform(0.6, 1.0),
            )

            # Simulate projection
            projection = self.simulate_income_projection(scenario_id)

            portfolio_scenarios.append(scenario_id)
            portfolio_projections.append(projection)

        # Calculate portfolio metrics
        total_investment = sum(p.total_investment for p in portfolio_projections)
        total_revenue_12m = sum(p.month_12 for p in portfolio_projections)
        total_revenue_24m = sum(p.month_24 for p in portfolio_projections)
        portfolio_roi = ((total_revenue_24m - total_investment) / total_investment) * 100

        # Calculate diversification metrics
        venture_type_distribution = {}
        for p in portfolio_projections:
            vtype = p.scenario.venture_type.value
            venture_type_distribution[vtype] = venture_type_distribution.get(vtype, 0) + 1

        return {
            "portfolio_id": generate_id("portfolio"),
            "num_ventures": num_ventures,
            "total_investment": total_investment,
            "total_revenue_12m": total_revenue_12m,
            "total_revenue_24m": total_revenue_24m,
            "portfolio_roi": portfolio_roi,
            "venture_type_distribution": venture_type_distribution,
            "scenarios": portfolio_scenarios,
            "projections": [p.__dict__ for p in portfolio_projections],
        }

    def create_income_report(self, scenario_id: str) -> Dict[str, Any]:
        """Create a comprehensive income report for a venture."""

        if scenario_id not in self.income_projections:
            raise ValueError(f"Projection for scenario {scenario_id} not found")

        projection = self.income_projections[scenario_id]

        # Calculate additional metrics (unused but kept for future use)
        _ = [
            projection.month_1,
            projection.month_3,
            projection.month_6,
            projection.month_12,
            projection.month_24,
        ]

        # Risk assessment
        risk_score = self._calculate_risk_score(projection)

        # Success probability
        success_probability = self._calculate_success_probability(projection)

        # Recommendations
        recommendations = self._generate_recommendations(projection)

        return {
            "venture_id": scenario_id,
            "venture_type": projection.scenario.venture_type.value,
            "market_condition": projection.scenario.market_condition.value,
            "financial_summary": {
                "initial_investment": projection.scenario.initial_investment,
                "total_investment": projection.total_investment,
                "break_even_month": projection.break_even_month,
                "cash_flow_positive_month": projection.cash_flow_positive_month,
                "roi_percentage": projection.roi_percentage,
                "projected_valuation": projection.projected_valuation,
            },
            "revenue_projections": {
                "month_1": projection.month_1,
                "month_3": projection.month_3,
                "month_6": projection.month_6,
                "month_12": projection.month_12,
                "month_24": projection.month_24,
                "monthly_recurring_revenue": projection.monthly_recurring_revenue,
            },
            "key_metrics": {
                "customer_lifetime_value": projection.customer_lifetime_value,
                "customer_acquisition_cost": projection.customer_acquisition_cost,
                "churn_rate": projection.churn_rate,
                "growth_rate": projection.growth_rate,
                "market_share": projection.market_share,
                "profitability_margin": projection.profitability_margin,
                "passive_income_potential": projection.passive_income_potential,
            },
            "risk_assessment": {
                "risk_score": risk_score,
                "success_probability": success_probability,
                "risk_factors": self._identify_risk_factors(projection),
            },
            "recommendations": recommendations,
            "scenario_details": {
                "target_market_size": projection.scenario.target_market_size,
                "competition_level": projection.scenario.competition_level,
                "marketing_budget": projection.scenario.marketing_budget,
                "team_size": projection.scenario.team_size,
                "niche_specificity": projection.scenario.niche_specificity,
                "automation_level": projection.scenario.automation_level,
            },
        }

    def _calculate_risk_score(self, projection: IncomeProjection) -> float:
        """Calculate risk score (0-100, higher = more risky)."""
        risk_score = 0.0

        # Break-even risk
        if projection.break_even_month > 18:
            risk_score += 30
        elif projection.break_even_month > 12:
            risk_score += 20
        elif projection.break_even_month > 6:
            risk_score += 10

        # ROI risk
        if projection.roi_percentage < 0:
            risk_score += 25
        elif projection.roi_percentage < 50:
            risk_score += 15
        elif projection.roi_percentage < 100:
            risk_score += 5

        # Churn risk
        if projection.churn_rate > 0.1:
            risk_score += 20
        elif projection.churn_rate > 0.05:
            risk_score += 10

        # Market condition risk
        if projection.scenario.market_condition == MarketCondition.BEAR_MARKET:
            risk_score += 15
        elif projection.scenario.market_condition == MarketCondition.VOLATILE_MARKET:
            risk_score += 10

        return min(risk_score, 100)

    def _calculate_success_probability(self, projection: IncomeProjection) -> float:
        """Calculate success probability (0-1)."""
        base_probability = self.market_data[projection.scenario.venture_type.value]["success_rate"]

        # Adjust based on risk factors
        risk_score = self._calculate_risk_score(projection)
        risk_adjustment = 1.0 - (risk_score / 100.0) * 0.5

        # Adjust based on scenario factors
        scenario_adjustment = 1.0

        # Niche specificity bonus
        scenario_adjustment *= 0.9 + projection.scenario.niche_specificity * 0.2

        # Automation level bonus
        scenario_adjustment *= 0.9 + projection.scenario.automation_level * 0.2

        # Team size bonus
        team_bonus = min(projection.scenario.team_size, 3) * 0.05
        scenario_adjustment *= 1.0 + team_bonus

        return min(base_probability * risk_adjustment * scenario_adjustment, 1.0)

    def _identify_risk_factors(self, projection: IncomeProjection) -> List[str]:
        """Identify key risk factors."""
        risk_factors = []

        if projection.break_even_month > 12:
            risk_factors.append("Long break-even period")

        if projection.roi_percentage < 50:
            risk_factors.append("Low ROI projection")

        if projection.churn_rate > 0.05:
            risk_factors.append("High churn rate")

        if projection.scenario.market_condition == MarketCondition.BEAR_MARKET:
            risk_factors.append("Bear market conditions")

        if projection.scenario.competition_level == "high":
            risk_factors.append("High competition")

        if projection.scenario.niche_specificity < 0.6:
            risk_factors.append("Low niche specificity")

        return risk_factors

    def _generate_recommendations(self, projection: IncomeProjection) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []

        if projection.break_even_month > 12:
            recommendations.append("Consider reducing initial investment or increasing marketing budget")

        if projection.churn_rate > 0.05:
            recommendations.append("Focus on customer retention strategies and product-market fit")

        if projection.scenario.automation_level < 0.8:
            recommendations.append("Increase automation to improve passive income potential")

        if projection.scenario.marketing_budget < projection.scenario.initial_investment * 0.2:
            recommendations.append("Consider increasing marketing budget for faster growth")

        if projection.scenario.team_size == 1:
            recommendations.append("Consider building a small team for better execution")

        if projection.customer_acquisition_cost > projection.customer_lifetime_value * 0.1:
            recommendations.append("Optimize customer acquisition channels to reduce CAC")

        return recommendations


def get_income_simulator() -> IncomeSimulator:
    """Get singleton income simulator instance."""
    if not hasattr(get_income_simulator, "_instance"):
        get_income_simulator._instance = IncomeSimulator()
    return get_income_simulator._instance

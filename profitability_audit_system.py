"""
Profitability Audit System for AutoPilot Ventures
Automatically monitors profit/loss metrics and manages venture lifecycle
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
from prometheus_client import Counter, Histogram, Gauge, Summary

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

class VentureStatus(Enum):
    ACTIVE = "active"
    UNDER_REVIEW = "under_review"
    TERMINATED = "terminated"
    SCALING = "scaling"
    OPTIMIZING = "optimizing"

class AuditAction(Enum):
    CONTINUE = "continue"
    OPTIMIZE = "optimize"
    SCALE = "scale"
    TERMINATE = "terminate"
    REDIRECT_RESOURCES = "redirect_resources"

@dataclass
class ProfitabilityMetrics:
    venture_id: str
    revenue: float
    costs: float
    profit: float
    profit_margin: float
    roi: float
    customer_acquisition_cost: float
    lifetime_value: float
    break_even_days: int
    cash_flow: float
    burn_rate: float
    runway_months: float
    timestamp: datetime

@dataclass
class AuditDecision:
    venture_id: str
    action: AuditAction
    reason: str
    confidence: float
    metrics: Dict[str, float]
    recommendations: List[str]
    timestamp: datetime
    executed: bool = False

@dataclass
class ResourceAllocation:
    venture_id: str
    cpu_allocation: float
    memory_allocation: float
    budget_allocation: float
    agent_priority: int
    optimization_priority: int
    timestamp: datetime

class ProfitabilityAuditSystem:
    """System for auditing venture profitability and managing lifecycle"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.venture_metrics = {}
        self.audit_decisions = {}
        self.resource_allocations = {}
        self.terminated_ventures = set()
        self.scaling_ventures = set()
        
        # Audit thresholds
        self.termination_thresholds = {
            "profit_margin": -0.2,  # -20% profit margin
            "roi": -0.5,  # -50% ROI
            "burn_rate": 1000,  # $1000/month burn rate
            "runway_months": 3,  # Less than 3 months runway
            "consecutive_losses": 3  # 3 consecutive months of losses
        }
        
        self.scaling_thresholds = {
            "profit_margin": 0.3,  # 30% profit margin
            "roi": 1.0,  # 100% ROI
            "growth_rate": 0.2,  # 20% monthly growth
            "customer_satisfaction": 0.8  # 80% satisfaction
        }
        
        # Metrics
        self.audits_performed = Counter('profitability_audits_total', 'Total profitability audits performed')
        self.ventures_terminated = Counter('ventures_terminated_total', 'Ventures terminated due to poor performance')
        self.ventures_scaled = Counter('ventures_scaled_total', 'Ventures scaled due to good performance')
        self.resources_redirected = Counter('resources_redirected_total', 'Resources redirected between ventures')
        self.total_profit = Gauge('total_profit', 'Total profit across all ventures')
        self.average_roi = Gauge('average_roi', 'Average ROI across all ventures')
        self.audit_duration = Histogram('audit_duration_seconds', 'Time taken for profitability audits')
        
        # Performance tracking
        self.venture_performance_history = defaultdict(list)
        self.audit_history = defaultdict(list)
    
    async def perform_profitability_audit(self, venture_id: str, 
                                        metrics: ProfitabilityMetrics) -> AuditDecision:
        """Perform comprehensive profitability audit for a venture"""
        start_time = time.time()
        
        try:
            # Store metrics
            self.venture_metrics[venture_id] = metrics
            self.venture_performance_history[venture_id].append(metrics)
            
            # Analyze profitability
            audit_result = await self._analyze_profitability(venture_id, metrics)
            
            # Make decision
            decision = await self._make_audit_decision(venture_id, audit_result)
            
            # Execute decision
            await self._execute_audit_decision(decision)
            
            # Update metrics
            self.audits_performed.inc()
            self.total_profit.set(await self._calculate_total_profit())
            self.average_roi.set(await self._calculate_average_roi())
            
            # Record audit duration
            audit_duration = time.time() - start_time
            self.audit_duration.observe(audit_duration)
            
            logger.info("Profitability audit completed", 
                      venture_id=venture_id, action=decision.action.value,
                      reason=decision.reason, confidence=decision.confidence,
                      duration=audit_duration)
            
            return decision
            
        except Exception as e:
            logger.error("Profitability audit failed", venture_id=venture_id, error=str(e))
            raise
    
    async def _analyze_profitability(self, venture_id: str, 
                                   metrics: ProfitabilityMetrics) -> Dict[str, Any]:
        """Analyze venture profitability comprehensively"""
        try:
            analysis = {
                "is_profitable": metrics.profit > 0,
                "profit_margin_healthy": metrics.profit_margin > 0.1,
                "roi_positive": metrics.roi > 0,
                "burn_rate_acceptable": metrics.burn_rate < self.termination_thresholds["burn_rate"],
                "runway_sufficient": metrics.runway_months > self.termination_thresholds["runway_months"],
                "growth_trend": await self._analyze_growth_trend(venture_id),
                "market_position": await self._analyze_market_position(venture_id),
                "competitive_advantage": await self._analyze_competitive_advantage(venture_id),
                "scalability_potential": await self._analyze_scalability_potential(venture_id),
                "risk_factors": await self._identify_risk_factors(venture_id, metrics)
            }
            
            # Calculate overall health score
            health_score = await self._calculate_health_score(analysis, metrics)
            analysis["health_score"] = health_score
            
            return analysis
            
        except Exception as e:
            logger.error("Profitability analysis failed", venture_id=venture_id, error=str(e))
            return {}
    
    async def _analyze_growth_trend(self, venture_id: str) -> Dict[str, Any]:
        """Analyze venture growth trend"""
        try:
            history = self.venture_performance_history[venture_id]
            
            if len(history) < 2:
                return {"trend": "insufficient_data", "growth_rate": 0.0}
            
            # Calculate growth rates
            revenue_growth = []
            profit_growth = []
            
            for i in range(1, len(history)):
                prev = history[i-1]
                curr = history[i]
                
                if prev.revenue > 0:
                    revenue_growth.append((curr.revenue - prev.revenue) / prev.revenue)
                
                if prev.profit != 0:
                    profit_growth.append((curr.profit - prev.profit) / abs(prev.profit))
            
            avg_revenue_growth = np.mean(revenue_growth) if revenue_growth else 0.0
            avg_profit_growth = np.mean(profit_growth) if profit_growth else 0.0
            
            return {
                "trend": "growing" if avg_revenue_growth > 0.1 else "declining" if avg_revenue_growth < -0.1 else "stable",
                "revenue_growth_rate": avg_revenue_growth,
                "profit_growth_rate": avg_profit_growth,
                "data_points": len(history)
            }
            
        except Exception as e:
            logger.error("Growth trend analysis failed", venture_id=venture_id, error=str(e))
            return {"trend": "error", "growth_rate": 0.0}
    
    async def _analyze_market_position(self, venture_id: str) -> Dict[str, Any]:
        """Analyze venture market position"""
        try:
            # This would analyze market share, competitive position, etc.
            # For now, return basic analysis
            return {
                "market_share": 0.01,  # 1% market share
                "competitive_position": "niche",
                "market_growth": 0.15,  # 15% market growth
                "barriers_to_entry": "medium"
            }
        except Exception as e:
            logger.error("Market position analysis failed", venture_id=venture_id, error=str(e))
            return {}
    
    async def _analyze_competitive_advantage(self, venture_id: str) -> Dict[str, Any]:
        """Analyze venture competitive advantages"""
        try:
            # This would analyze unique value propositions, technology advantages, etc.
            return {
                "unique_value_proposition": "strong",
                "technology_advantage": "medium",
                "cost_advantage": "low",
                "network_effects": "none"
            }
        except Exception as e:
            logger.error("Competitive advantage analysis failed", venture_id=venture_id, error=str(e))
            return {}
    
    async def _analyze_scalability_potential(self, venture_id: str) -> Dict[str, Any]:
        """Analyze venture scalability potential"""
        try:
            # This would analyze market size, operational scalability, etc.
            return {
                "market_size": "large",
                "operational_scalability": "high",
                "technology_scalability": "high",
                "financial_scalability": "medium"
            }
        except Exception as e:
            logger.error("Scalability analysis failed", venture_id=venture_id, error=str(e))
            return {}
    
    async def _identify_risk_factors(self, venture_id: str, 
                                   metrics: ProfitabilityMetrics) -> List[str]:
        """Identify risk factors for the venture"""
        try:
            risks = []
            
            if metrics.profit_margin < 0:
                risks.append("negative_profit_margin")
            
            if metrics.roi < 0:
                risks.append("negative_roi")
            
            if metrics.burn_rate > self.termination_thresholds["burn_rate"]:
                risks.append("high_burn_rate")
            
            if metrics.runway_months < self.termination_thresholds["runway_months"]:
                risks.append("insufficient_runway")
            
            if metrics.customer_acquisition_cost > metrics.lifetime_value * 0.3:
                risks.append("high_customer_acquisition_cost")
            
            return risks
            
        except Exception as e:
            logger.error("Risk factor identification failed", venture_id=venture_id, error=str(e))
            return []
    
    async def _calculate_health_score(self, analysis: Dict[str, Any], 
                                    metrics: ProfitabilityMetrics) -> float:
        """Calculate overall venture health score"""
        try:
            score = 0.0
            max_score = 100.0
            
            # Profitability (30 points)
            if analysis["is_profitable"]:
                score += 15
            if analysis["profit_margin_healthy"]:
                score += 15
            
            # ROI (20 points)
            if analysis["roi_positive"]:
                score += 20
            
            # Growth (20 points)
            if analysis["growth_trend"]["trend"] == "growing":
                score += 20
            elif analysis["growth_trend"]["trend"] == "stable":
                score += 10
            
            # Financial health (15 points)
            if analysis["burn_rate_acceptable"]:
                score += 7.5
            if analysis["runway_sufficient"]:
                score += 7.5
            
            # Market position (15 points)
            if analysis["market_position"]["competitive_position"] in ["leader", "strong"]:
                score += 15
            elif analysis["market_position"]["competitive_position"] == "niche":
                score += 10
            
            return min(score, max_score)
            
        except Exception as e:
            logger.error("Health score calculation failed", error=str(e))
            return 0.0
    
    async def _make_audit_decision(self, venture_id: str, 
                                 analysis: Dict[str, Any]) -> AuditDecision:
        """Make audit decision based on analysis"""
        try:
            health_score = analysis.get("health_score", 0.0)
            risks = analysis.get("risk_factors", [])
            
            # Determine action based on health score and risks
            if health_score < 30 or len(risks) >= 3:
                action = AuditAction.TERMINATE
                reason = f"Low health score ({health_score}) and {len(risks)} risk factors"
                confidence = 0.9
            elif health_score < 60:
                action = AuditAction.OPTIMIZE
                reason = f"Moderate health score ({health_score}) requires optimization"
                confidence = 0.7
            elif health_score >= 80:
                action = AuditAction.SCALE
                reason = f"High health score ({health_score}) indicates scaling potential"
                confidence = 0.8
            else:
                action = AuditAction.CONTINUE
                reason = f"Acceptable health score ({health_score}) - continue monitoring"
                confidence = 0.6
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(analysis, action)
            
            decision = AuditDecision(
                venture_id=venture_id,
                action=action,
                reason=reason,
                confidence=confidence,
                metrics=analysis,
                recommendations=recommendations,
                timestamp=datetime.utcnow()
            )
            
            self.audit_decisions[venture_id] = decision
            self.audit_history[venture_id].append(decision)
            
            return decision
            
        except Exception as e:
            logger.error("Audit decision making failed", venture_id=venture_id, error=str(e))
            raise
    
    async def _generate_recommendations(self, analysis: Dict[str, Any], 
                                      action: AuditAction) -> List[str]:
        """Generate recommendations based on analysis and action"""
        try:
            recommendations = []
            
            if action == AuditAction.TERMINATE:
                recommendations.extend([
                    "Immediately stop new investments",
                    "Sell or liquidate assets",
                    "Preserve customer data for future ventures",
                    "Document lessons learned"
                ])
            
            elif action == AuditAction.OPTIMIZE:
                if not analysis.get("is_profitable"):
                    recommendations.append("Focus on achieving profitability")
                if analysis.get("risk_factors"):
                    recommendations.append("Address identified risk factors")
                recommendations.extend([
                    "Optimize cost structure",
                    "Improve customer acquisition efficiency",
                    "Enhance product-market fit"
                ])
            
            elif action == AuditAction.SCALE:
                recommendations.extend([
                    "Increase marketing budget",
                    "Expand to new markets",
                    "Hire additional team members",
                    "Invest in technology infrastructure"
                ])
            
            return recommendations
            
        except Exception as e:
            logger.error("Recommendation generation failed", error=str(e))
            return []
    
    async def _execute_audit_decision(self, decision: AuditDecision):
        """Execute the audit decision"""
        try:
            venture_id = decision.venture_id
            
            if decision.action == AuditAction.TERMINATE:
                await self._terminate_venture(venture_id, decision)
            
            elif decision.action == AuditAction.SCALE:
                await self._scale_venture(venture_id, decision)
            
            elif decision.action == AuditAction.OPTIMIZE:
                await self._optimize_venture(venture_id, decision)
            
            elif decision.action == AuditAction.REDIRECT_RESOURCES:
                await self._redirect_resources(venture_id, decision)
            
            decision.executed = True
            
        except Exception as e:
            logger.error("Audit decision execution failed", 
                        venture_id=decision.venture_id, action=decision.action.value, error=str(e))
    
    async def _terminate_venture(self, venture_id: str, decision: AuditDecision):
        """Terminate an underperforming venture"""
        try:
            # Mark venture for termination
            self.terminated_ventures.add(venture_id)
            
            # Redirect resources to better performing ventures
            await self._redirect_resources_from_terminated(venture_id)
            
            # Update metrics
            self.ventures_terminated.inc()
            
            logger.info("Venture terminated", 
                      venture_id=venture_id, reason=decision.reason)
            
        except Exception as e:
            logger.error("Venture termination failed", venture_id=venture_id, error=str(e))
    
    async def _scale_venture(self, venture_id: str, decision: AuditDecision):
        """Scale a high-performing venture"""
        try:
            # Mark venture for scaling
            self.scaling_ventures.add(venture_id)
            
            # Allocate additional resources
            await self._allocate_scaling_resources(venture_id)
            
            # Update metrics
            self.ventures_scaled.inc()
            
            logger.info("Venture marked for scaling", 
                      venture_id=venture_id, reason=decision.reason)
            
        except Exception as e:
            logger.error("Venture scaling failed", venture_id=venture_id, error=str(e))
    
    async def _optimize_venture(self, venture_id: str, decision: AuditDecision):
        """Optimize an underperforming venture"""
        try:
            # Implement optimization recommendations
            for recommendation in decision.recommendations:
                await self._implement_optimization(venture_id, recommendation)
            
            logger.info("Venture optimization initiated", 
                      venture_id=venture_id, recommendations=decision.recommendations)
            
        except Exception as e:
            logger.error("Venture optimization failed", venture_id=venture_id, error=str(e))
    
    async def _redirect_resources(self, venture_id: str, decision: AuditDecision):
        """Redirect resources between ventures"""
        try:
            # Find target ventures for resource redirection
            target_ventures = await self._find_resource_targets(venture_id)
            
            # Redirect resources
            for target_venture in target_ventures:
                await self._transfer_resources(venture_id, target_venture)
            
            # Update metrics
            self.resources_redirected.inc()
            
            logger.info("Resources redirected", 
                      from_venture=venture_id, to_ventures=target_ventures)
            
        except Exception as e:
            logger.error("Resource redirection failed", venture_id=venture_id, error=str(e))
    
    async def _redirect_resources_from_terminated(self, terminated_venture_id: str):
        """Redirect resources from terminated venture to winners"""
        try:
            # Find best performing ventures
            best_ventures = await self._find_best_performing_ventures()
            
            # Calculate resources to redirect
            resources = await self._calculate_venture_resources(terminated_venture_id)
            
            # Distribute resources among best performers
            for venture_id in best_ventures:
                await self._allocate_additional_resources(venture_id, resources / len(best_ventures))
            
            logger.info("Resources redirected from terminated venture", 
                      terminated_venture=terminated_venture_id, 
                      target_ventures=best_ventures, resources=resources)
            
        except Exception as e:
            logger.error("Resource redirection from terminated venture failed", 
                        venture_id=terminated_venture_id, error=str(e))
    
    async def _find_best_performing_ventures(self) -> List[str]:
        """Find best performing ventures for resource allocation"""
        try:
            # Get all active ventures
            active_ventures = [vid for vid in self.venture_metrics.keys() 
                             if vid not in self.terminated_ventures]
            
            # Sort by health score
            venture_scores = []
            for venture_id in active_ventures:
                if venture_id in self.audit_decisions:
                    decision = self.audit_decisions[venture_id]
                    health_score = decision.metrics.get("health_score", 0.0)
                    venture_scores.append((venture_id, health_score))
            
            # Return top 20% of ventures
            venture_scores.sort(key=lambda x: x[1], reverse=True)
            top_count = max(1, len(venture_scores) // 5)
            
            return [venture_id for venture_id, _ in venture_scores[:top_count]]
            
        except Exception as e:
            logger.error("Best performing ventures search failed", error=str(e))
            return []
    
    async def _calculate_venture_resources(self, venture_id: str) -> float:
        """Calculate total resources allocated to a venture"""
        try:
            # This would calculate CPU, memory, budget, etc.
            # For now, return a default value
            return 1000.0  # $1000 worth of resources
        except Exception as e:
            logger.error("Venture resources calculation failed", venture_id=venture_id, error=str(e))
            return 0.0
    
    async def _allocate_additional_resources(self, venture_id: str, resources: float):
        """Allocate additional resources to a venture"""
        try:
            # Update resource allocation
            if venture_id in self.resource_allocations:
                current = self.resource_allocations[venture_id]
                current.budget_allocation += resources
                current.optimization_priority += 1
            else:
                self.resource_allocations[venture_id] = ResourceAllocation(
                    venture_id=venture_id,
                    cpu_allocation=1.0,
                    memory_allocation=2.0,
                    budget_allocation=resources,
                    agent_priority=1,
                    optimization_priority=1,
                    timestamp=datetime.utcnow()
                )
            
            logger.info("Additional resources allocated", 
                      venture_id=venture_id, resources=resources)
            
        except Exception as e:
            logger.error("Additional resource allocation failed", venture_id=venture_id, error=str(e))
    
    async def _calculate_total_profit(self) -> float:
        """Calculate total profit across all ventures"""
        try:
            total = 0.0
            for metrics in self.venture_metrics.values():
                total += metrics.profit
            return total
        except Exception as e:
            logger.error("Total profit calculation failed", error=str(e))
            return 0.0
    
    async def _calculate_average_roi(self) -> float:
        """Calculate average ROI across all ventures"""
        try:
            if not self.venture_metrics:
                return 0.0
            
            total_roi = sum(metrics.roi for metrics in self.venture_metrics.values())
            return total_roi / len(self.venture_metrics)
        except Exception as e:
            logger.error("Average ROI calculation failed", error=str(e))
            return 0.0
    
    async def _find_resource_targets(self, venture_id: str) -> List[str]:
        """Find target ventures for resource redirection"""
        try:
            # Find ventures with high potential but limited resources
            potential_targets = []
            
            for vid, allocation in self.resource_allocations.items():
                if vid != venture_id and vid not in self.terminated_ventures:
                    if allocation.optimization_priority > 2:  # High priority
                        potential_targets.append(vid)
            
            return potential_targets[:3]  # Top 3 targets
            
        except Exception as e:
            logger.error("Resource target search failed", venture_id=venture_id, error=str(e))
            return []
    
    async def _transfer_resources(self, from_venture: str, to_venture: str):
        """Transfer resources between ventures"""
        try:
            # Calculate transfer amount
            transfer_amount = 100.0  # $100 transfer
            
            # Update allocations
            if from_venture in self.resource_allocations:
                self.resource_allocations[from_venture].budget_allocation -= transfer_amount
            
            if to_venture in self.resource_allocations:
                self.resource_allocations[to_venture].budget_allocation += transfer_amount
            else:
                self.resource_allocations[to_venture] = ResourceAllocation(
                    venture_id=to_venture,
                    cpu_allocation=1.0,
                    memory_allocation=2.0,
                    budget_allocation=transfer_amount,
                    agent_priority=1,
                    optimization_priority=1,
                    timestamp=datetime.utcnow()
                )
            
            logger.info("Resources transferred", 
                      from_venture=from_venture, to_venture=to_venture, amount=transfer_amount)
            
        except Exception as e:
            logger.error("Resource transfer failed", 
                        from_venture=from_venture, to_venture=to_venture, error=str(e))
    
    async def _allocate_scaling_resources(self, venture_id: str):
        """Allocate scaling resources to a venture"""
        try:
            scaling_resources = ResourceAllocation(
                venture_id=venture_id,
                cpu_allocation=2.0,  # Double CPU
                memory_allocation=4.0,  # Double memory
                budget_allocation=2000.0,  # $2000 scaling budget
                agent_priority=1,  # High priority
                optimization_priority=1,
                timestamp=datetime.utcnow()
            )
            
            self.resource_allocations[venture_id] = scaling_resources
            
            logger.info("Scaling resources allocated", venture_id=venture_id)
            
        except Exception as e:
            logger.error("Scaling resource allocation failed", venture_id=venture_id, error=str(e))
    
    async def _implement_optimization(self, venture_id: str, recommendation: str):
        """Implement optimization recommendation"""
        try:
            # This would implement specific optimizations
            # For now, just log the implementation
            logger.info("Optimization implemented", 
                      venture_id=venture_id, recommendation=recommendation)
            
        except Exception as e:
            logger.error("Optimization implementation failed", 
                        venture_id=venture_id, recommendation=recommendation, error=str(e))
    
    async def get_audit_summary(self) -> Dict[str, Any]:
        """Get summary of audit system performance"""
        try:
            summary = {
                "total_ventures": len(self.venture_metrics),
                "active_ventures": len(self.venture_metrics) - len(self.terminated_ventures),
                "terminated_ventures": len(self.terminated_ventures),
                "scaling_ventures": len(self.scaling_ventures),
                "total_profit": await self._calculate_total_profit(),
                "average_roi": await self._calculate_average_roi(),
                "recent_decisions": [],
                "resource_allocations": {}
            }
            
            # Get recent decisions
            recent_decisions = sorted(
                self.audit_decisions.values(),
                key=lambda x: x.timestamp,
                reverse=True
            )[:10]
            
            summary["recent_decisions"] = [
                {
                    "venture_id": decision.venture_id,
                    "action": decision.action.value,
                    "reason": decision.reason,
                    "confidence": decision.confidence,
                    "timestamp": decision.timestamp.isoformat()
                }
                for decision in recent_decisions
            ]
            
            # Get resource allocations
            summary["resource_allocations"] = {
                venture_id: {
                    "cpu": allocation.cpu_allocation,
                    "memory": allocation.memory_allocation,
                    "budget": allocation.budget_allocation,
                    "priority": allocation.optimization_priority
                }
                for venture_id, allocation in self.resource_allocations.items()
            }
            
            return summary
            
        except Exception as e:
            logger.error("Audit summary generation failed", error=str(e))
            return {}

# Initialize the profitability audit system
async def initialize_profitability_audit(redis_url: str = "redis://localhost:6379") -> ProfitabilityAuditSystem:
    """Initialize the profitability audit system"""
    try:
        redis_client = redis.from_url(redis_url)
        audit_system = ProfitabilityAuditSystem(redis_client)
        
        logger.info("Profitability audit system initialized successfully")
        return audit_system
        
    except Exception as e:
        logger.error("Failed to initialize profitability audit system", error=str(e))
        raise

if __name__ == "__main__":
    # Example usage
    async def main():
        audit_system = await initialize_profitability_audit()
        
        # Example profitability metrics
        metrics = ProfitabilityMetrics(
            venture_id="venture123",
            revenue=5000.0,
            costs=4000.0,
            profit=1000.0,
            profit_margin=0.2,
            roi=0.25,
            customer_acquisition_cost=50.0,
            lifetime_value=200.0,
            break_even_days=30,
            cash_flow=800.0,
            burn_rate=500.0,
            runway_months=6.0,
            timestamp=datetime.utcnow()
        )
        
        # Perform audit
        decision = await audit_system.perform_profitability_audit("venture123", metrics)
        
        print(f"Audit decision: {decision.action.value}")
        print(f"Reason: {decision.reason}")
        print(f"Recommendations: {decision.recommendations}")
        
        # Get summary
        summary = await audit_system.get_audit_summary()
        print("Audit summary:", json.dumps(summary, indent=2))
    
    asyncio.run(main()) 
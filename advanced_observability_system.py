"""
Advanced Observability System for AutoPilot Ventures
Comprehensive agent lifecycle monitoring and auto-recovery capabilities
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Optional, Any, Set, Tuple
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

class AgentLifecycleStage(Enum):
    INITIALIZATION = "initialization"
    ACTIVE = "active"
    IDLE = "idle"
    ERROR = "error"
    RECOVERING = "recovering"
    TERMINATED = "terminated"

class RecoveryAction(Enum):
    RESTART_AGENT = "restart_agent"
    RESET_STATE = "reset_state"
    SCALE_RESOURCES = "scale_resources"
    FAILOVER = "failover"
    ESCALATE_HUMAN = "escalate_human"
    IGNORE = "ignore"

class MonitoringLevel(Enum):
    BASIC = "basic"
    STANDARD = "standard"
    ADVANCED = "advanced"
    ENTERPRISE = "enterprise"

@dataclass
class AgentLifecycleEvent:
    agent_id: str
    agent_type: str
    stage: AgentLifecycleStage
    timestamp: datetime
    metadata: Dict[str, Any]
    duration_seconds: Optional[float] = None
    error_message: Optional[str] = None
    recovery_action: Optional[RecoveryAction] = None

@dataclass
class AutoRecoveryScript:
    id: str
    name: str
    description: str
    trigger_conditions: Dict[str, Any]
    actions: List[Dict[str, Any]]
    success_criteria: Dict[str, Any]
    timeout_seconds: int
    max_retries: int
    created_at: datetime
    last_executed: Optional[datetime] = None
    success_rate: float = 0.0
    active: bool = True

@dataclass
class SystemHealthSnapshot:
    timestamp: datetime
    overall_health: float
    agent_health: Dict[str, float]
    resource_utilization: Dict[str, float]
    error_rates: Dict[str, float]
    recovery_actions: List[str]
    alerts: List[str]

class AdvancedObservabilitySystem:
    """Advanced observability system with comprehensive monitoring and auto-recovery"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.agent_lifecycles = defaultdict(list)
        self.auto_recovery_scripts = {}
        self.system_health_history = []
        self.active_monitoring = {}
        self.recovery_history = []
        
        # Monitoring thresholds
        self.monitoring_thresholds = {
            "agent_health_minimum": 0.7,
            "resource_utilization_maximum": 0.85,
            "error_rate_maximum": 0.05,
            "response_time_maximum": 5000,  # ms
            "memory_usage_maximum": 0.9,
            "cpu_usage_maximum": 0.8
        }
        
        # Recovery parameters
        self.recovery_parameters = {
            "max_recovery_attempts": 3,
            "recovery_timeout": 300,  # seconds
            "escalation_threshold": 2,
            "auto_recovery_enabled": True
        }
        
        # Metrics
        self.agent_lifecycle_events = Counter('agent_lifecycle_events_total', 'Agent lifecycle events', ['stage', 'agent_type'])
        self.recovery_actions_executed = Counter('recovery_actions_executed', 'Recovery actions executed', ['action_type'])
        self.system_health_score = Gauge('system_health_score', 'Overall system health score')
        self.agent_health_scores = Gauge('agent_health_scores', 'Individual agent health scores', ['agent_id'])
        self.recovery_success_rate = Gauge('recovery_success_rate', 'Auto-recovery success rate')
        self.monitoring_duration = Histogram('monitoring_duration_seconds', 'Time spent in monitoring operations')
        
        # Initialize auto-recovery scripts
        self._initialize_auto_recovery_scripts()
        
        logger.info("Advanced observability system initialized successfully")
    
    def _initialize_auto_recovery_scripts(self):
        """Initialize default auto-recovery scripts"""
        try:
            # Agent restart script
            restart_script = AutoRecoveryScript(
                id="agent_restart_script",
                name="Agent Restart Recovery",
                description="Automatically restart failed agents",
                trigger_conditions={
                    "agent_stage": AgentLifecycleStage.ERROR.value,
                    "error_count": 1,
                    "time_window_minutes": 5
                },
                actions=[
                    {"action": "stop_agent", "timeout": 30},
                    {"action": "wait", "duration": 10},
                    {"action": "start_agent", "timeout": 60},
                    {"action": "verify_health", "timeout": 30}
                ],
                success_criteria={
                    "agent_stage": AgentLifecycleStage.ACTIVE.value,
                    "health_score": 0.8
                },
                timeout_seconds=180,
                max_retries=2,
                created_at=datetime.utcnow()
            )
            self.auto_recovery_scripts[restart_script.id] = restart_script
            
            # Resource scaling script
            scaling_script = AutoRecoveryScript(
                id="resource_scaling_script",
                name="Resource Scaling Recovery",
                description="Scale resources for overloaded agents",
                trigger_conditions={
                    "cpu_usage": 0.9,
                    "memory_usage": 0.9,
                    "response_time_ms": 10000
                },
                actions=[
                    {"action": "scale_cpu", "factor": 1.5},
                    {"action": "scale_memory", "factor": 1.5},
                    {"action": "wait", "duration": 30},
                    {"action": "verify_performance", "timeout": 60}
                ],
                success_criteria={
                    "cpu_usage": 0.7,
                    "memory_usage": 0.7,
                    "response_time_ms": 5000
                },
                timeout_seconds=300,
                max_retries=1,
                created_at=datetime.utcnow()
            )
            self.auto_recovery_scripts[scaling_script.id] = scaling_script
            
            # State reset script
            reset_script = AutoRecoveryScript(
                id="state_reset_script",
                name="State Reset Recovery",
                description="Reset agent state for corrupted agents",
                trigger_conditions={
                    "agent_stage": AgentLifecycleStage.ERROR.value,
                    "error_type": "state_corruption",
                    "recovery_attempts": 2
                },
                actions=[
                    {"action": "backup_state", "timeout": 30},
                    {"action": "reset_state", "timeout": 60},
                    {"action": "restore_clean_state", "timeout": 30},
                    {"action": "verify_state", "timeout": 30}
                ],
                success_criteria={
                    "agent_stage": AgentLifecycleStage.ACTIVE.value,
                    "state_integrity": 0.9
                },
                timeout_seconds=240,
                max_retries=1,
                created_at=datetime.utcnow()
            )
            self.auto_recovery_scripts[reset_script.id] = reset_script
            
            logger.info(f"Initialized {len(self.auto_recovery_scripts)} auto-recovery scripts")
            
        except Exception as e:
            logger.error("Failed to initialize auto-recovery scripts", error=str(e))
    
    async def monitor_agent_lifecycle(self, agent_id: str, agent_type: str, 
                                    stage: AgentLifecycleStage, 
                                    metadata: Dict[str, Any] = None,
                                    error_message: str = None) -> str:
        """Monitor agent lifecycle events"""
        start_time = time.time()
        
        try:
            event_id = f"lifecycle_{int(time.time())}_{agent_id}"
            
            # Calculate duration if transitioning from previous stage
            duration_seconds = None
            if self.agent_lifecycles[agent_id]:
                previous_event = self.agent_lifecycles[agent_id][-1]
                duration_seconds = (datetime.utcnow() - previous_event.timestamp).total_seconds()
            
            event = AgentLifecycleEvent(
                agent_id=agent_id,
                agent_type=agent_type,
                stage=stage,
                timestamp=datetime.utcnow(),
                metadata=metadata or {},
                duration_seconds=duration_seconds,
                error_message=error_message
            )
            
            self.agent_lifecycles[agent_id].append(event)
            
            # Update metrics
            self.agent_lifecycle_events.labels(stage=stage.value, agent_type=agent_type).inc()
            
            # Check for recovery triggers
            if stage == AgentLifecycleStage.ERROR:
                await self._trigger_auto_recovery(agent_id, event)
            
            # Update agent health score
            await self._update_agent_health_score(agent_id, stage)
            
            # Update system health
            await self._update_system_health()
            
            # Record monitoring duration
            monitoring_duration = time.time() - start_time
            self.monitoring_duration.observe(monitoring_duration)
            
            logger.info("Agent lifecycle event recorded", 
                      event_id=event_id, agent_id=agent_id, stage=stage.value,
                      duration=duration_seconds, error_message=error_message)
            
            return event_id
            
        except Exception as e:
            logger.error("Agent lifecycle monitoring failed", error=str(e))
            raise
    
    async def _trigger_auto_recovery(self, agent_id: str, event: AgentLifecycleEvent):
        """Trigger auto-recovery for a failed agent"""
        try:
            if not self.recovery_parameters["auto_recovery_enabled"]:
                logger.info("Auto-recovery disabled, skipping recovery for agent", agent_id=agent_id)
                return
            
            # Find applicable recovery scripts
            applicable_scripts = await self._find_applicable_recovery_scripts(agent_id, event)
            
            if not applicable_scripts:
                logger.warning("No applicable recovery scripts found for agent", agent_id=agent_id)
                await self._escalate_to_human(agent_id, event, "No recovery scripts available")
                return
            
            # Execute recovery scripts
            for script in applicable_scripts:
                recovery_result = await self._execute_recovery_script(script, agent_id, event)
                
                if recovery_result["success"]:
                    logger.info("Auto-recovery successful", 
                              agent_id=agent_id, script_id=script.id)
                    break
                else:
                    logger.warning("Auto-recovery failed", 
                                 agent_id=agent_id, script_id=script.id, 
                                 error=recovery_result["error"])
            
        except Exception as e:
            logger.error("Auto-recovery triggering failed", error=str(e))
    
    async def _find_applicable_recovery_scripts(self, agent_id: str, 
                                              event: AgentLifecycleEvent) -> List[AutoRecoveryScript]:
        """Find recovery scripts applicable to the current situation"""
        try:
            applicable_scripts = []
            
            for script in self.auto_recovery_scripts.values():
                if not script.active:
                    continue
                
                # Check trigger conditions
                if await self._check_script_conditions(script, agent_id, event):
                    applicable_scripts.append(script)
            
            # Sort by priority (more specific scripts first)
            applicable_scripts.sort(key=lambda s: len(s.trigger_conditions), reverse=True)
            
            return applicable_scripts
            
        except Exception as e:
            logger.error("Recovery script finding failed", error=str(e))
            return []
    
    async def _check_script_conditions(self, script: AutoRecoveryScript, 
                                     agent_id: str, event: AgentLifecycleEvent) -> bool:
        """Check if a recovery script's conditions are met"""
        try:
            conditions = script.trigger_conditions
            
            # Check agent stage condition
            if "agent_stage" in conditions:
                if event.stage.value != conditions["agent_stage"]:
                    return False
            
            # Check error count condition
            if "error_count" in conditions:
                recent_errors = len([
                    e for e in self.agent_lifecycles[agent_id][-10:]  # Last 10 events
                    if e.stage == AgentLifecycleStage.ERROR
                ])
                if recent_errors < conditions["error_count"]:
                    return False
            
            # Check time window condition
            if "time_window_minutes" in conditions:
                time_window = timedelta(minutes=conditions["time_window_minutes"])
                recent_events = [
                    e for e in self.agent_lifecycles[agent_id]
                    if datetime.utcnow() - e.timestamp <= time_window
                ]
                if len(recent_events) < conditions.get("error_count", 1):
                    return False
            
            # Check resource conditions
            if "cpu_usage" in conditions:
                current_cpu = event.metadata.get("cpu_usage", 0)
                if current_cpu < conditions["cpu_usage"]:
                    return False
            
            if "memory_usage" in conditions:
                current_memory = event.metadata.get("memory_usage", 0)
                if current_memory < conditions["memory_usage"]:
                    return False
            
            if "response_time_ms" in conditions:
                current_response_time = event.metadata.get("response_time_ms", 0)
                if current_response_time < conditions["response_time_ms"]:
                    return False
            
            return True
            
        except Exception as e:
            logger.error("Script condition check failed", error=str(e))
            return False
    
    async def _execute_recovery_script(self, script: AutoRecoveryScript, 
                                     agent_id: str, event: AgentLifecycleEvent) -> Dict[str, Any]:
        """Execute a recovery script"""
        try:
            start_time = time.time()
            
            logger.info("Executing recovery script", 
                      script_id=script.id, agent_id=agent_id)
            
            # Execute actions
            for action in script.actions:
                action_result = await self._execute_recovery_action(action, agent_id)
                
                if not action_result["success"]:
                    return {
                        "success": False,
                        "error": f"Action failed: {action_result['error']}",
                        "script_id": script.id,
                        "action": action
                    }
            
            # Check success criteria
            success_check = await self._check_success_criteria(script, agent_id)
            
            if success_check["success"]:
                # Update script metrics
                script.last_executed = datetime.utcnow()
                script.success_rate = min(1.0, script.success_rate + 0.1)
                
                # Update recovery metrics
                self.recovery_actions_executed.labels(action_type=script.name).inc()
                self.recovery_success_rate.set(script.success_rate)
                
                # Record recovery history
                self.recovery_history.append({
                    "script_id": script.id,
                    "agent_id": agent_id,
                    "timestamp": datetime.utcnow(),
                    "success": True,
                    "duration": time.time() - start_time
                })
                
                return {"success": True, "script_id": script.id}
            else:
                return {
                    "success": False,
                    "error": f"Success criteria not met: {success_check['error']}",
                    "script_id": script.id
                }
            
        except Exception as e:
            logger.error("Recovery script execution failed", error=str(e))
            return {"success": False, "error": str(e)}
    
    async def _execute_recovery_action(self, action: Dict[str, Any], agent_id: str) -> Dict[str, Any]:
        """Execute a single recovery action"""
        try:
            action_type = action.get("action")
            timeout = action.get("timeout", 30)
            
            if action_type == "stop_agent":
                # Simulate agent stop
                await asyncio.sleep(1)
                return {"success": True}
            
            elif action_type == "start_agent":
                # Simulate agent start
                await asyncio.sleep(2)
                return {"success": True}
            
            elif action_type == "wait":
                duration = action.get("duration", 10)
                await asyncio.sleep(duration)
                return {"success": True}
            
            elif action_type == "verify_health":
                # Simulate health verification
                await asyncio.sleep(1)
                return {"success": True, "health_score": 0.9}
            
            elif action_type == "scale_cpu":
                factor = action.get("factor", 1.5)
                # Simulate CPU scaling
                await asyncio.sleep(1)
                return {"success": True, "new_cpu_allocation": factor}
            
            elif action_type == "scale_memory":
                factor = action.get("factor", 1.5)
                # Simulate memory scaling
                await asyncio.sleep(1)
                return {"success": True, "new_memory_allocation": factor}
            
            elif action_type == "backup_state":
                # Simulate state backup
                await asyncio.sleep(1)
                return {"success": True, "backup_id": f"backup_{int(time.time())}"}
            
            elif action_type == "reset_state":
                # Simulate state reset
                await asyncio.sleep(2)
                return {"success": True}
            
            elif action_type == "restore_clean_state":
                # Simulate state restoration
                await asyncio.sleep(1)
                return {"success": True}
            
            elif action_type == "verify_state":
                # Simulate state verification
                await asyncio.sleep(1)
                return {"success": True, "state_integrity": 0.95}
            
            else:
                return {"success": False, "error": f"Unknown action type: {action_type}"}
            
        except Exception as e:
            logger.error("Recovery action execution failed", error=str(e))
            return {"success": False, "error": str(e)}
    
    async def _check_success_criteria(self, script: AutoRecoveryScript, agent_id: str) -> Dict[str, Any]:
        """Check if recovery script success criteria are met"""
        try:
            criteria = script.success_criteria
            
            # Get current agent state
            current_events = self.agent_lifecycles[agent_id]
            if not current_events:
                return {"success": False, "error": "No agent events found"}
            
            current_event = current_events[-1]
            
            # Check agent stage
            if "agent_stage" in criteria:
                if current_event.stage.value != criteria["agent_stage"]:
                    return {"success": False, "error": f"Agent stage mismatch: expected {criteria['agent_stage']}, got {current_event.stage.value}"}
            
            # Check health score
            if "health_score" in criteria:
                current_health = current_event.metadata.get("health_score", 0.5)
                if current_health < criteria["health_score"]:
                    return {"success": False, "error": f"Health score too low: {current_health} < {criteria['health_score']}"}
            
            # Check resource usage
            if "cpu_usage" in criteria:
                current_cpu = current_event.metadata.get("cpu_usage", 1.0)
                if current_cpu > criteria["cpu_usage"]:
                    return {"success": False, "error": f"CPU usage too high: {current_cpu} > {criteria['cpu_usage']}"}
            
            if "memory_usage" in criteria:
                current_memory = current_event.metadata.get("memory_usage", 1.0)
                if current_memory > criteria["memory_usage"]:
                    return {"success": False, "error": f"Memory usage too high: {current_memory} > {criteria['memory_usage']}"}
            
            if "response_time_ms" in criteria:
                current_response_time = current_event.metadata.get("response_time_ms", float('inf'))
                if current_response_time > criteria["response_time_ms"]:
                    return {"success": False, "error": f"Response time too high: {current_response_time} > {criteria['response_time_ms']}"}
            
            return {"success": True}
            
        except Exception as e:
            logger.error("Success criteria check failed", error=str(e))
            return {"success": False, "error": str(e)}
    
    async def _escalate_to_human(self, agent_id: str, event: AgentLifecycleEvent, reason: str):
        """Escalate recovery to human intervention"""
        try:
            escalation = {
                "agent_id": agent_id,
                "agent_type": event.agent_type,
                "reason": reason,
                "timestamp": datetime.utcnow().isoformat(),
                "event_data": {
                    "stage": event.stage.value,
                    "error_message": event.error_message,
                    "metadata": event.metadata
                }
            }
            
            # Store escalation in Redis for human review
            await self.redis.setex(
                f"escalation:{agent_id}:{int(time.time())}",
                3600,  # 1 hour TTL
                json.dumps(escalation)
            )
            
            logger.warning("Recovery escalated to human", 
                          agent_id=agent_id, reason=reason)
            
        except Exception as e:
            logger.error("Human escalation failed", error=str(e))
    
    async def _update_agent_health_score(self, agent_id: str, stage: AgentLifecycleStage):
        """Update agent health score based on lifecycle stage"""
        try:
            # Calculate health score based on stage
            health_scores = {
                AgentLifecycleStage.ACTIVE: 1.0,
                AgentLifecycleStage.IDLE: 0.8,
                AgentLifecycleStage.INITIALIZATION: 0.6,
                AgentLifecycleStage.RECOVERING: 0.4,
                AgentLifecycleStage.ERROR: 0.1,
                AgentLifecycleStage.TERMINATED: 0.0
            }
            
            health_score = health_scores.get(stage, 0.5)
            
            # Update metric
            self.agent_health_scores.labels(agent_id=agent_id).set(health_score)
            
        except Exception as e:
            logger.error("Agent health score update failed", error=str(e))
    
    async def _update_system_health(self):
        """Update overall system health score"""
        try:
            if not self.agent_lifecycles:
                return
            
            # Calculate average health score across all agents
            total_health = 0.0
            agent_count = 0
            
            for agent_id, events in self.agent_lifecycles.items():
                if events:
                    latest_event = events[-1]
                    health_scores = {
                        AgentLifecycleStage.ACTIVE: 1.0,
                        AgentLifecycleStage.IDLE: 0.8,
                        AgentLifecycleStage.INITIALIZATION: 0.6,
                        AgentLifecycleStage.RECOVERING: 0.4,
                        AgentLifecycleStage.ERROR: 0.1,
                        AgentLifecycleStage.TERMINATED: 0.0
                    }
                    health_score = health_scores.get(latest_event.stage, 0.5)
                    total_health += health_score
                    agent_count += 1
            
            if agent_count > 0:
                system_health = total_health / agent_count
                self.system_health_score.set(system_health)
            
        except Exception as e:
            logger.error("System health update failed", error=str(e))
    
    async def create_health_snapshot(self) -> SystemHealthSnapshot:
        """Create a comprehensive system health snapshot"""
        try:
            # Calculate overall health
            overall_health = 0.0
            agent_health = {}
            resource_utilization = {}
            error_rates = {}
            recovery_actions = []
            alerts = []
            
            # Calculate agent health scores
            for agent_id, events in self.agent_lifecycles.items():
                if events:
                    latest_event = events[-1]
                    health_scores = {
                        AgentLifecycleStage.ACTIVE: 1.0,
                        AgentLifecycleStage.IDLE: 0.8,
                        AgentLifecycleStage.INITIALIZATION: 0.6,
                        AgentLifecycleStage.RECOVERING: 0.4,
                        AgentLifecycleStage.ERROR: 0.1,
                        AgentLifecycleStage.TERMINATED: 0.0
                    }
                    health_score = health_scores.get(latest_event.stage, 0.5)
                    agent_health[agent_id] = health_score
                    overall_health += health_score
            
            if agent_health:
                overall_health /= len(agent_health)
            
            # Calculate resource utilization (simplified)
            resource_utilization = {
                "cpu_usage": 0.6,
                "memory_usage": 0.7,
                "disk_usage": 0.5,
                "network_usage": 0.4
            }
            
            # Calculate error rates
            for agent_id, events in self.agent_lifecycles.items():
                recent_events = [e for e in events if datetime.utcnow() - e.timestamp <= timedelta(hours=1)]
                if recent_events:
                    error_count = len([e for e in recent_events if e.stage == AgentLifecycleStage.ERROR])
                    error_rates[agent_id] = error_count / len(recent_events)
            
            # Get recent recovery actions
            recent_recoveries = [r for r in self.recovery_history if datetime.utcnow() - r["timestamp"] <= timedelta(hours=1)]
            recovery_actions = [r["script_id"] for r in recent_recoveries]
            
            # Generate alerts
            if overall_health < self.monitoring_thresholds["agent_health_minimum"]:
                alerts.append("Low overall system health")
            
            for agent_id, health in agent_health.items():
                if health < self.monitoring_thresholds["agent_health_minimum"]:
                    alerts.append(f"Low health for agent {agent_id}")
            
            for resource, usage in resource_utilization.items():
                if usage > self.monitoring_thresholds.get(f"{resource}_maximum", 0.9):
                    alerts.append(f"High {resource} utilization")
            
            snapshot = SystemHealthSnapshot(
                timestamp=datetime.utcnow(),
                overall_health=overall_health,
                agent_health=agent_health,
                resource_utilization=resource_utilization,
                error_rates=error_rates,
                recovery_actions=recovery_actions,
                alerts=alerts
            )
            
            self.system_health_history.append(snapshot)
            
            # Keep only recent snapshots
            if len(self.system_health_history) > 1000:
                self.system_health_history = self.system_health_history[-1000:]
            
            return snapshot
            
        except Exception as e:
            logger.error("Health snapshot creation failed", error=str(e))
            raise
    
    async def get_observability_summary(self) -> Dict[str, Any]:
        """Get summary of observability system status"""
        try:
            summary = {
                "total_agents_monitored": len(self.agent_lifecycles),
                "total_recovery_scripts": len(self.auto_recovery_scripts),
                "active_recovery_scripts": len([s for s in self.auto_recovery_scripts.values() if s.active]),
                "total_recovery_actions": len(self.recovery_history),
                "recent_recovery_actions": len([r for r in self.recovery_history if datetime.utcnow() - r["timestamp"] <= timedelta(hours=1)]),
                "system_health_history": len(self.system_health_history),
                "agent_stages": {},
                "recovery_success_rates": {},
                "recent_alerts": []
            }
            
            # Get agent stage distribution
            stage_counts = defaultdict(int)
            for events in self.agent_lifecycles.values():
                if events:
                    stage_counts[events[-1].stage.value] += 1
            
            summary["agent_stages"] = dict(stage_counts)
            
            # Get recovery success rates
            for script in self.auto_recovery_scripts.values():
                summary["recovery_success_rates"][script.id] = script.success_rate
            
            # Get recent alerts from latest snapshot
            if self.system_health_history:
                latest_snapshot = self.system_health_history[-1]
                summary["recent_alerts"] = latest_snapshot.alerts
            
            return summary
            
        except Exception as e:
            logger.error("Observability summary generation failed", error=str(e))
            return {}

# Initialize the advanced observability system
async def initialize_advanced_observability(redis_url: str = "redis://localhost:6379") -> AdvancedObservabilitySystem:
    """Initialize the advanced observability system"""
    try:
        redis_client = redis.from_url(redis_url)
        observability_system = AdvancedObservabilitySystem(redis_client)
        
        logger.info("Advanced observability system initialized successfully")
        return observability_system
        
    except Exception as e:
        logger.error("Failed to initialize advanced observability system", error=str(e))
        raise

if __name__ == "__main__":
    # Example usage
    async def main():
        observability = await initialize_advanced_observability()
        
        # Example agent lifecycle monitoring
        await observability.monitor_agent_lifecycle(
            agent_id="marketing_agent_001",
            agent_type="marketing_strategy",
            stage=AgentLifecycleStage.ACTIVE,
            metadata={"cpu_usage": 0.6, "memory_usage": 0.7, "response_time_ms": 2000}
        )
        
        # Example error monitoring
        await observability.monitor_agent_lifecycle(
            agent_id="marketing_agent_001",
            agent_type="marketing_strategy",
            stage=AgentLifecycleStage.ERROR,
            metadata={"cpu_usage": 0.9, "memory_usage": 0.95, "response_time_ms": 15000},
            error_message="Memory exhaustion detected"
        )
        
        # Create health snapshot
        snapshot = await observability.create_health_snapshot()
        print(f"System health: {snapshot.overall_health:.2f}")
        print(f"Alerts: {snapshot.alerts}")
        
        # Get observability summary
        summary = await observability.get_observability_summary()
        print("Observability summary:", json.dumps(summary, indent=2))
    
    asyncio.run(main()) 
"""Performance monitoring system for AutoPilot Ventures autonomous agents."""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import time
from dataclasses import dataclass, asdict
import statistics

from prometheus_client import Counter, Gauge, Histogram, Summary
from utils import log

# Import autonomous enhancements
from autonomous_enhancements import (
    VectorMemoryManager,
    ReinforcementLearningEngine,
    AgentType
)

# Configure logging
logger = logging.getLogger(__name__)


# Prometheus metrics for autonomous features
AUTONOMOUS_AGENT_EXECUTIONS = Counter(
    'autonomous_agent_executions_total',
    'Total number of autonomous agent executions',
    ['agent_type', 'startup_id', 'success']
)

AUTONOMOUS_LEARNING_EPISODES = Counter(
    'autonomous_learning_episodes_total',
    'Total number of learning episodes',
    ['agent_type', 'startup_id']
)

AUTONOMOUS_CONFIDENCE_GAUGE = Gauge(
    'autonomous_agent_confidence',
    'Agent confidence levels',
    ['agent_type', 'startup_id']
)

AUTONOMOUS_MEMORY_OPERATIONS = Counter(
    'autonomous_memory_operations_total',
    'Total number of memory operations',
    ['operation_type', 'startup_id']
)

AUTONOMOUS_LEARNING_RATE = Gauge(
    'autonomous_learning_rate',
    'Current learning rate for agents',
    ['agent_type', 'startup_id']
)

AUTONOMOUS_PERFORMANCE_IMPROVEMENT = Gauge(
    'autonomous_performance_improvement',
    'Performance improvement over time',
    ['agent_type', 'startup_id', 'metric_type']
)

AUTONOMOUS_WORKFLOW_SUCCESS_RATE = Gauge(
    'autonomous_workflow_success_rate',
    'Success rate of autonomous workflows',
    ['startup_id']
)


@dataclass
class PerformanceSnapshot:
    """Snapshot of agent performance at a point in time."""
    
    timestamp: datetime
    agent_type: str
    startup_id: str
    execution_count: int
    success_count: int
    success_rate: float
    avg_confidence: float
    avg_execution_time: float
    total_cost: float
    learning_episodes: int
    memory_operations: int
    q_value_improvement: float


@dataclass
class LearningProgress:
    """Track learning progress over time."""
    
    agent_type: str
    startup_id: str
    baseline_performance: float
    current_performance: float
    improvement_percentage: float
    learning_rate: float
    episodes_completed: int
    last_improvement: datetime
    trend: str  # 'improving', 'stable', 'declining'


class AutonomousPerformanceMonitor:
    """Monitor and track autonomous agent performance improvements."""

    def __init__(self, startup_id: str):
        """Initialize performance monitor."""
        self.startup_id = startup_id
        self.snapshots: List[PerformanceSnapshot] = []
        self.learning_progress: Dict[str, LearningProgress] = {}
        self.baseline_metrics: Dict[str, Dict[str, float]] = {}
        
        # Initialize autonomous components
        self.vector_memory = VectorMemoryManager(startup_id)
        self.rl_engine = ReinforcementLearningEngine(startup_id)
        
        # Performance tracking
        self.performance_history: Dict[str, List[Dict[str, Any]]] = {}
        self.improvement_thresholds = {
            'success_rate': 0.05,  # 5% improvement
            'confidence': 0.1,     # 10% improvement
            'execution_time': -0.1, # 10% faster
            'cost': -0.1           # 10% cheaper
        }
        
        logger.info(f"Autonomous performance monitor initialized for startup {startup_id}")

    async def record_agent_execution(
        self,
        agent_type: str,
        success: bool,
        confidence: float,
        execution_time: float,
        cost: float,
        learning_data: Dict[str, Any]
    ):
        """Record agent execution for performance tracking."""
        try:
            # Update Prometheus metrics
            AUTONOMOUS_AGENT_EXECUTIONS.labels(
                agent_type=agent_type,
                startup_id=self.startup_id,
                success=success
            ).inc()
            
            AUTONOMOUS_CONFIDENCE_GAUGE.labels(
                agent_type=agent_type,
                startup_id=self.startup_id
            ).set(confidence)
            
            # Store performance data
            if agent_type not in self.performance_history:
                self.performance_history[agent_type] = []
            
            performance_data = {
                'timestamp': datetime.now(),
                'success': success,
                'confidence': confidence,
                'execution_time': execution_time,
                'cost': cost,
                'learning_data': learning_data
            }
            
            self.performance_history[agent_type].append(performance_data)
            
            # Keep only last 1000 executions per agent
            if len(self.performance_history[agent_type]) > 1000:
                self.performance_history[agent_type] = self.performance_history[agent_type][-1000:]
            
            # Check for performance improvements
            await self._check_performance_improvements(agent_type)
            
            logger.debug(f"Performance data recorded for agent {agent_type}")
            
        except Exception as e:
            logger.error(f"Error recording agent execution: {e}")

    async def record_learning_episode(
        self,
        agent_type: str,
        reward: float,
        state: str,
        action: str,
        next_state: str
    ):
        """Record learning episode for tracking improvements."""
        try:
            # Update Prometheus metrics
            AUTONOMOUS_LEARNING_EPISODES.labels(
                agent_type=agent_type,
                startup_id=self.startup_id
            ).inc()
            
            # Record memory operation
            AUTONOMOUS_MEMORY_OPERATIONS.labels(
                operation_type='learning_episode',
                startup_id=self.startup_id
            ).inc()
            
            # Update learning progress
            if agent_type not in self.learning_progress:
                await self._initialize_learning_progress(agent_type)
            
            progress = self.learning_progress[agent_type]
            progress.episodes_completed += 1
            
            # Calculate learning rate (simplified)
            if progress.episodes_completed > 10:
                recent_rewards = self._get_recent_rewards(agent_type, 10)
                if recent_rewards:
                    progress.learning_rate = statistics.mean(recent_rewards)
                    AUTONOMOUS_LEARNING_RATE.labels(
                        agent_type=agent_type,
                        startup_id=self.startup_id
                    ).set(progress.learning_rate)
            
            logger.debug(f"Learning episode recorded for agent {agent_type}")
            
        except Exception as e:
            logger.error(f"Error recording learning episode: {e}")

    async def record_memory_operation(self, operation_type: str, success: bool):
        """Record memory operation for tracking."""
        try:
            AUTONOMOUS_MEMORY_OPERATIONS.labels(
                operation_type=operation_type,
                startup_id=self.startup_id
            ).inc()
            
            logger.debug(f"Memory operation recorded: {operation_type}")
            
        except Exception as e:
            logger.error(f"Error recording memory operation: {e}")

    async def take_performance_snapshot(self, agent_type: str) -> PerformanceSnapshot:
        """Take a snapshot of current agent performance."""
        try:
            # Get current performance data
            if agent_type not in self.performance_history:
                return None
            
            recent_data = self.performance_history[agent_type][-100:]  # Last 100 executions
            
            if not recent_data:
                return None
            
            # Calculate metrics
            execution_count = len(recent_data)
            success_count = sum(1 for d in recent_data if d['success'])
            success_rate = success_count / execution_count if execution_count > 0 else 0
            avg_confidence = statistics.mean(d['confidence'] for d in recent_data)
            avg_execution_time = statistics.mean(d['execution_time'] for d in recent_data)
            total_cost = sum(d['cost'] for d in recent_data)
            
            # Get learning metrics
            learning_episodes = self.learning_progress.get(agent_type, LearningProgress(
                agent_type=agent_type,
                startup_id=self.startup_id,
                baseline_performance=0.0,
                current_performance=0.0,
                improvement_percentage=0.0,
                learning_rate=0.0,
                episodes_completed=0,
                last_improvement=datetime.now(),
                trend='stable'
            )).episodes_completed
            
            # Calculate Q-value improvement (simplified)
            q_value_improvement = 0.0
            if self.rl_engine:
                try:
                    # This would need to be implemented in the RL engine
                    q_value_improvement = 0.1  # Placeholder
                except:
                    pass
            
            snapshot = PerformanceSnapshot(
                timestamp=datetime.now(),
                agent_type=agent_type,
                startup_id=self.startup_id,
                execution_count=execution_count,
                success_count=success_count,
                success_rate=success_rate,
                avg_confidence=avg_confidence,
                avg_execution_time=avg_execution_time,
                total_cost=total_cost,
                learning_episodes=learning_episodes,
                memory_operations=0,  # Would need to track this
                q_value_improvement=q_value_improvement
            )
            
            self.snapshots.append(snapshot)
            
            # Keep only last 100 snapshots
            if len(self.snapshots) > 100:
                self.snapshots = self.snapshots[-100:]
            
            return snapshot
            
        except Exception as e:
            logger.error(f"Error taking performance snapshot: {e}")
            return None

    async def _initialize_learning_progress(self, agent_type: str):
        """Initialize learning progress tracking for an agent."""
        try:
            # Set baseline performance
            if agent_type not in self.baseline_metrics:
                await self._set_baseline_metrics(agent_type)
            
            baseline = self.baseline_metrics.get(agent_type, {})
            baseline_performance = baseline.get('success_rate', 0.5)
            
            self.learning_progress[agent_type] = LearningProgress(
                agent_type=agent_type,
                startup_id=self.startup_id,
                baseline_performance=baseline_performance,
                current_performance=baseline_performance,
                improvement_percentage=0.0,
                learning_rate=0.0,
                episodes_completed=0,
                last_improvement=datetime.now(),
                trend='stable'
            )
            
            logger.info(f"Learning progress initialized for agent {agent_type}")
            
        except Exception as e:
            logger.error(f"Error initializing learning progress: {e}")

    async def _set_baseline_metrics(self, agent_type: str):
        """Set baseline performance metrics for an agent."""
        try:
            # Use first 50 executions as baseline
            if agent_type in self.performance_history and len(self.performance_history[agent_type]) >= 50:
                baseline_data = self.performance_history[agent_type][:50]
                
                baseline_metrics = {
                    'success_rate': sum(1 for d in baseline_data if d['success']) / len(baseline_data),
                    'avg_confidence': statistics.mean(d['confidence'] for d in baseline_data),
                    'avg_execution_time': statistics.mean(d['execution_time'] for d in baseline_data),
                    'avg_cost': statistics.mean(d['cost'] for d in baseline_data)
                }
                
                self.baseline_metrics[agent_type] = baseline_metrics
                
                logger.info(f"Baseline metrics set for agent {agent_type}: {baseline_metrics}")
            
        except Exception as e:
            logger.error(f"Error setting baseline metrics: {e}")

    async def _check_performance_improvements(self, agent_type: str):
        """Check for performance improvements and update metrics."""
        try:
            if agent_type not in self.learning_progress:
                return
            
            progress = self.learning_progress[agent_type]
            
            # Get current performance
            current_snapshot = await self.take_performance_snapshot(agent_type)
            if not current_snapshot:
                return
            
            # Calculate improvements
            baseline = self.baseline_metrics.get(agent_type, {})
            
            success_rate_improvement = current_snapshot.success_rate - baseline.get('success_rate', 0.5)
            confidence_improvement = current_snapshot.avg_confidence - baseline.get('avg_confidence', 0.5)
            time_improvement = baseline.get('avg_execution_time', 10.0) - current_snapshot.avg_execution_time
            cost_improvement = baseline.get('avg_cost', 0.1) - current_snapshot.total_cost / current_snapshot.execution_count if current_snapshot.execution_count > 0 else 0
            
            # Update Prometheus metrics
            AUTONOMOUS_PERFORMANCE_IMPROVEMENT.labels(
                agent_type=agent_type,
                startup_id=self.startup_id,
                metric_type='success_rate'
            ).set(success_rate_improvement)
            
            AUTONOMOUS_PERFORMANCE_IMPROVEMENT.labels(
                agent_type=agent_type,
                startup_id=self.startup_id,
                metric_type='confidence'
            ).set(confidence_improvement)
            
            AUTONOMOUS_PERFORMANCE_IMPROVEMENT.labels(
                agent_type=agent_type,
                startup_id=self.startup_id,
                metric_type='execution_time'
            ).set(time_improvement)
            
            AUTONOMOUS_PERFORMANCE_IMPROVEMENT.labels(
                agent_type=agent_type,
                startup_id=self.startup_id,
                metric_type='cost'
            ).set(cost_improvement)
            
            # Update learning progress
            progress.current_performance = current_snapshot.success_rate
            progress.improvement_percentage = (success_rate_improvement / baseline.get('success_rate', 0.5)) * 100
            
            # Determine trend
            if success_rate_improvement > self.improvement_thresholds['success_rate']:
                progress.trend = 'improving'
                progress.last_improvement = datetime.now()
            elif success_rate_improvement < -self.improvement_thresholds['success_rate']:
                progress.trend = 'declining'
            else:
                progress.trend = 'stable'
            
            logger.debug(f"Performance improvement checked for {agent_type}: {progress.improvement_percentage:.2f}%")
            
        except Exception as e:
            logger.error(f"Error checking performance improvements: {e}")

    def _get_recent_rewards(self, agent_type: str, count: int) -> List[float]:
        """Get recent rewards for learning rate calculation."""
        try:
            # This would need to be implemented to track rewards
            # For now, return placeholder data
            return [0.1] * count
        except Exception as e:
            logger.error(f"Error getting recent rewards: {e}")
            return []

    def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        try:
            report = {
                'startup_id': self.startup_id,
                'timestamp': datetime.now().isoformat(),
                'agent_performance': {},
                'learning_progress': {},
                'overall_metrics': {},
                'improvements': {}
            }
            
            # Agent performance
            for agent_type in self.performance_history.keys():
                if self.performance_history[agent_type]:
                    recent_data = self.performance_history[agent_type][-50:]  # Last 50 executions
                    
                    report['agent_performance'][agent_type] = {
                        'total_executions': len(self.performance_history[agent_type]),
                        'recent_success_rate': sum(1 for d in recent_data if d['success']) / len(recent_data) if recent_data else 0,
                        'avg_confidence': statistics.mean(d['confidence'] for d in recent_data) if recent_data else 0,
                        'avg_execution_time': statistics.mean(d['execution_time'] for d in recent_data) if recent_data else 0,
                        'avg_cost': statistics.mean(d['cost'] for d in recent_data) if recent_data else 0
                    }
            
            # Learning progress
            for agent_type, progress in self.learning_progress.items():
                report['learning_progress'][agent_type] = asdict(progress)
            
            # Overall metrics
            if self.performance_history:
                all_executions = []
                for agent_data in self.performance_history.values():
                    all_executions.extend(agent_data)
                
                if all_executions:
                    report['overall_metrics'] = {
                        'total_executions': len(all_executions),
                        'overall_success_rate': sum(1 for d in all_executions if d['success']) / len(all_executions),
                        'avg_confidence': statistics.mean(d['confidence'] for d in all_executions),
                        'avg_execution_time': statistics.mean(d['execution_time'] for d in all_executions),
                        'total_cost': sum(d['cost'] for d in all_executions)
                    }
            
            # Improvements
            for agent_type, progress in self.learning_progress.items():
                report['improvements'][agent_type] = {
                    'improvement_percentage': progress.improvement_percentage,
                    'trend': progress.trend,
                    'learning_rate': progress.learning_rate,
                    'episodes_completed': progress.episodes_completed
                }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating performance report: {e}")
            return {'error': str(e)}

    def get_learning_insights(self) -> Dict[str, Any]:
        """Get insights about learning progress and improvements."""
        try:
            insights = {
                'startup_id': self.startup_id,
                'timestamp': datetime.now().isoformat(),
                'learning_summary': {},
                'recommendations': [],
                'trends': {}
            }
            
            # Learning summary
            total_episodes = sum(p.episodes_completed for p in self.learning_progress.values())
            avg_improvement = statistics.mean([p.improvement_percentage for p in self.learning_progress.values()]) if self.learning_progress else 0
            
            insights['learning_summary'] = {
                'total_learning_episodes': total_episodes,
                'average_improvement': avg_improvement,
                'agents_with_improvements': sum(1 for p in self.learning_progress.values() if p.improvement_percentage > 0),
                'agents_declining': sum(1 for p in self.learning_progress.values() if p.trend == 'declining')
            }
            
            # Generate recommendations
            for agent_type, progress in self.learning_progress.items():
                if progress.trend == 'declining':
                    insights['recommendations'].append({
                        'agent_type': agent_type,
                        'issue': 'Performance declining',
                        'recommendation': 'Review recent changes and consider adjusting learning parameters'
                    })
                elif progress.improvement_percentage > 20:
                    insights['recommendations'].append({
                        'agent_type': agent_type,
                        'issue': 'Strong improvement detected',
                        'recommendation': 'Consider increasing learning rate or exploring new strategies'
                    })
            
            # Trends
            for agent_type, progress in self.learning_progress.items():
                insights['trends'][agent_type] = {
                    'trend': progress.trend,
                    'improvement_rate': progress.improvement_percentage / max(progress.episodes_completed, 1),
                    'learning_efficiency': progress.learning_rate
                }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting learning insights: {e}")
            return {'error': str(e)}


# Factory function
def create_performance_monitor(startup_id: str) -> AutonomousPerformanceMonitor:
    """Create a performance monitor for autonomous agents."""
    return AutonomousPerformanceMonitor(startup_id) 
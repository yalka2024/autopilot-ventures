"""Advanced Intelligence Module for AutoPilot Ventures Phase 3."""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import pandas as pd
from collections import defaultdict
import mlflow
import plotly.graph_objects as go
import plotly.express as px
from dash import Dash, html, dcc, Input, Output
import threading
import time

from config import config
from utils import generate_id, log
from agent_message_bus import get_message_bus, MessageType, MessagePriority
from autonomous_enhancements import VectorMemoryManager

logger = logging.getLogger(__name__)


class IntelligenceType(Enum):
    """Types of advanced intelligence."""
    
    MONITORING = "monitoring"
    DECISION_TREES = "decision_trees"
    CROSS_VENTURE = "cross_venture"
    PREDICTIVE = "predictive"


@dataclass
class ExperimentResult:
    """MLflow experiment result."""
    
    experiment_id: str
    run_id: str
    metrics: Dict[str, float]
    parameters: Dict[str, Any]
    tags: Dict[str, str]
    timestamp: datetime
    status: str


@dataclass
class DecisionNode:
    """Node in dynamic decision tree."""
    
    node_id: str
    condition: Dict[str, Any]
    action: Dict[str, Any]
    confidence: float
    success_rate: float
    children: List[str] = field(default_factory=list)
    parent: Optional[str] = None
    usage_count: int = 0
    last_used: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CrossVenturePattern:
    """Pattern learned across multiple ventures."""
    
    pattern_id: str
    venture_ids: List[str]
    pattern_type: str
    success_rate: float
    confidence: float
    conditions: Dict[str, Any]
    actions: Dict[str, Any]
    timestamp: datetime
    usage_count: int = 0


@dataclass
class PredictionResult:
    """Prediction result from analytics."""
    
    prediction_id: str
    target: str
    predicted_value: float
    confidence: float
    timeframe: str
    factors: List[str]
    timestamp: datetime


class AdvancedMonitoring:
    """Advanced monitoring with MLflow integration."""
    
    def __init__(self, startup_id: str):
        self.startup_id = startup_id
        self.monitoring_id = generate_id("monitoring")
        
        # Initialize MLflow
        mlflow.set_tracking_uri(f"file:./mlruns/{startup_id}")
        self.experiment_name = f"autopilot_ventures_{startup_id}"
        
        # Create or get experiment
        try:
            self.experiment = mlflow.get_experiment_by_name(self.experiment_name)
            if self.experiment is None:
                self.experiment_id = mlflow.create_experiment(self.experiment_name)
            else:
                self.experiment_id = self.experiment.experiment_id
        except Exception as e:
            logger.warning(f"MLflow experiment creation failed: {e}")
            self.experiment_id = None
        
        # Performance tracking
        self.performance_metrics = defaultdict(list)
        self.anomaly_detection = {}
        self.alert_thresholds = {
            'success_rate': 0.7,
            'response_time': 30.0,
            'error_rate': 0.1,
            'cost_efficiency': 0.8
        }
        
        # Message bus for alerts
        self.message_bus = get_message_bus(startup_id)
        
        logger.info(f"Advanced monitoring initialized for startup {startup_id}")
    
    async def track_experiment(self, experiment_name: str, metrics: Dict[str, float], 
                             parameters: Dict[str, Any], tags: Dict[str, str] = None):
        """Track experiment with MLflow."""
        try:
            if self.experiment_id is None:
                return None
            
            mlflow.set_experiment(experiment_id=self.experiment_id)
            
            with mlflow.start_run(run_name=experiment_name):
                # Log metrics
                for metric_name, metric_value in metrics.items():
                    mlflow.log_metric(metric_name, metric_value)
                
                # Log parameters
                for param_name, param_value in parameters.items():
                    mlflow.log_param(param_name, param_value)
                
                # Log tags
                if tags:
                    for tag_name, tag_value in tags.items():
                        mlflow.set_tag(tag_name, tag_value)
                
                # Get run info
                run = mlflow.active_run()
                run_id = run.info.run_id
                
                # Store performance metrics
                self.performance_metrics[experiment_name].append({
                    'timestamp': datetime.utcnow(),
                    'metrics': metrics,
                    'run_id': run_id
                })
                
                # Check for anomalies
                await self._check_anomalies(experiment_name, metrics)
                
                logger.info(f"Experiment {experiment_name} tracked with run_id {run_id}")
                
                return ExperimentResult(
                    experiment_id=self.experiment_id,
                    run_id=run_id,
                    metrics=metrics,
                    parameters=parameters,
                    tags=tags or {},
                    timestamp=datetime.utcnow(),
                    status='completed'
                )
                
        except Exception as e:
            logger.error(f"Failed to track experiment: {e}")
            return None
    
    async def _check_anomalies(self, experiment_name: str, metrics: Dict[str, float]):
        """Check for performance anomalies."""
        try:
            for metric_name, current_value in metrics.items():
                if metric_name in self.alert_thresholds:
                    threshold = self.alert_thresholds[metric_name]
                    
                    # Simple anomaly detection
                    if metric_name == 'success_rate' and current_value < threshold:
                        await self._send_alert(f"Low success rate: {current_value} < {threshold}")
                    elif metric_name == 'error_rate' and current_value > threshold:
                        await self._send_alert(f"High error rate: {current_value} > {threshold}")
                    elif metric_name == 'response_time' and current_value > threshold:
                        await self._send_alert(f"Slow response time: {current_value} > {threshold}")
                    elif metric_name == 'cost_efficiency' and current_value < threshold:
                        await self._send_alert(f"Low cost efficiency: {current_value} < {threshold}")
                        
        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
    
    async def _send_alert(self, message: str):
        """Send alert through message bus."""
        try:
            await self.message_bus.broadcast_message(
                sender="advanced_monitoring",
                message_type=MessageType.ERROR_ALERT,
                content={
                    'alert_type': 'performance_anomaly',
                    'message': message,
                    'timestamp': datetime.utcnow().isoformat()
                },
                priority=MessagePriority.HIGH
            )
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")
    
    def get_performance_dashboard(self) -> Dict[str, Any]:
        """Get performance dashboard data."""
        dashboard_data = {}
        
        for experiment_name, metrics_list in self.performance_metrics.items():
            if metrics_list:
                # Calculate trends
                recent_metrics = metrics_list[-10:]  # Last 10 runs
                
                dashboard_data[experiment_name] = {
                    'total_runs': len(metrics_list),
                    'recent_trend': self._calculate_trend(recent_metrics),
                    'average_metrics': self._calculate_averages(metrics_list),
                    'best_performance': self._find_best_performance(metrics_list)
                }
        
        return dashboard_data
    
    def _calculate_trend(self, metrics_list: List[Dict]) -> str:
        """Calculate performance trend."""
        if len(metrics_list) < 2:
            return "insufficient_data"
        
        # Simple trend calculation
        first_avg = np.mean(list(metrics_list[0]['metrics'].values()))
        last_avg = np.mean(list(metrics_list[-1]['metrics'].values()))
        
        if last_avg > first_avg * 1.1:
            return "improving"
        elif last_avg < first_avg * 0.9:
            return "declining"
        else:
            return "stable"
    
    def _calculate_averages(self, metrics_list: List[Dict]) -> Dict[str, float]:
        """Calculate average metrics."""
        if not metrics_list:
            return {}
        
        all_metrics = defaultdict(list)
        for run in metrics_list:
            for metric_name, metric_value in run['metrics'].items():
                all_metrics[metric_name].append(metric_value)
        
        return {name: np.mean(values) for name, values in all_metrics.items()}
    
    def _find_best_performance(self, metrics_list: List[Dict]) -> Dict[str, Any]:
        """Find best performance run."""
        if not metrics_list:
            return {}
        
        # Find run with highest average metric value
        best_run = max(metrics_list, key=lambda x: np.mean(list(x['metrics'].values())))
        return {
            'run_id': best_run['run_id'],
            'metrics': best_run['metrics'],
            'timestamp': best_run['timestamp']
        }


class DynamicDecisionTree:
    """Dynamic decision tree with self-optimization."""
    
    def __init__(self, startup_id: str):
        self.startup_id = startup_id
        self.tree_id = generate_id("decision_tree")
        
        # Tree structure
        self.nodes: Dict[str, DecisionNode] = {}
        self.root_node_id: Optional[str] = None
        
        # Learning parameters
        self.learning_rate = 0.1
        self.exploration_rate = 0.2
        self.confidence_threshold = 0.7
        
        # Performance tracking
        self.decision_history = []
        self.optimization_history = []
        
        # Vector memory for context
        self.vector_memory = VectorMemoryManager(startup_id)
        
        logger.info(f"Dynamic decision tree initialized for startup {startup_id}")
    
    async def make_decision(self, context: Dict[str, Any], options: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Make decision using dynamic tree."""
        try:
            # Find best path through tree
            path = await self._traverse_tree(context)
            
            if path and path[-1] in self.nodes:
                node = self.nodes[path[-1]]
                
                # Check if we should explore
                if np.random.random() < self.exploration_rate or node.confidence < self.confidence_threshold:
                    decision = self._explore_decision(options)
                    decision_type = "exploration"
                else:
                    decision = node.action
                    decision_type = "exploitation"
                
                # Record decision
                decision_record = {
                    'decision_id': generate_id(),
                    'context': context,
                    'decision': decision,
                    'path': path,
                    'confidence': node.confidence,
                    'decision_type': decision_type,
                    'timestamp': datetime.utcnow()
                }
                
                self.decision_history.append(decision_record)
                
                return {
                    'decision': decision,
                    'confidence': node.confidence,
                    'path': path,
                    'decision_type': decision_type
                }
            else:
                # Create new node if no path found
                return await self._create_new_decision_node(context, options)
                
        except Exception as e:
            logger.error(f"Decision making failed: {e}")
            return {'decision': options[0], 'confidence': 0.0, 'decision_type': 'fallback'}
    
    async def _traverse_tree(self, context: Dict[str, Any]) -> List[str]:
        """Traverse tree to find best path."""
        if not self.root_node_id:
            return []
        
        path = [self.root_node_id]
        current_node_id = self.root_node_id
        
        while current_node_id in self.nodes:
            node = self.nodes[current_node_id]
            
            # Check if current node's condition matches context
            if self._evaluate_condition(node.condition, context):
                # Find best child
                best_child = None
                best_score = 0.0
                
                for child_id in node.children:
                    if child_id in self.nodes:
                        child = self.nodes[child_id]
                        score = child.confidence * child.success_rate
                        if score > best_score:
                            best_score = score
                            best_child = child_id
                
                if best_child:
                    path.append(best_child)
                    current_node_id = best_child
                else:
                    break
            else:
                break
        
        return path
    
    def _evaluate_condition(self, condition: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Evaluate if condition matches context."""
        try:
            for key, expected_value in condition.items():
                if key not in context:
                    return False
                
                actual_value = context[key]
                
                # Simple matching for now
                if isinstance(expected_value, dict):
                    if 'operator' in expected_value:
                        op = expected_value['operator']
                        val = expected_value['value']
                        
                        if op == 'equals' and actual_value != val:
                            return False
                        elif op == 'greater_than' and actual_value <= val:
                            return False
                        elif op == 'less_than' and actual_value >= val:
                            return False
                        elif op == 'contains' and val not in str(actual_value):
                            return False
                else:
                    if actual_value != expected_value:
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Condition evaluation failed: {e}")
            return False
    
    async def _create_new_decision_node(self, context: Dict[str, Any], options: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create new decision node."""
        try:
            # Choose random option for exploration
            decision = np.random.choice(options)
            
            # Create new node
            node_id = generate_id()
            new_node = DecisionNode(
                node_id=node_id,
                condition=context,
                action=decision,
                confidence=0.5,  # Initial confidence
                success_rate=0.5,  # Initial success rate
                usage_count=1,
                last_used=datetime.utcnow()
            )
            
            self.nodes[node_id] = new_node
            
            # Set as root if no root exists
            if not self.root_node_id:
                self.root_node_id = node_id
            
            return {
                'decision': decision,
                'confidence': 0.5,
                'path': [node_id],
                'decision_type': 'new_node'
            }
            
        except Exception as e:
            logger.error(f"Failed to create new decision node: {e}")
            return {'decision': options[0], 'confidence': 0.0, 'decision_type': 'fallback'}
    
    def _explore_decision(self, options: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Explore new decision options."""
        return np.random.choice(options)
    
    async def learn_from_outcome(self, decision_id: str, outcome: Dict[str, Any]):
        """Learn from decision outcome and optimize tree."""
        try:
            # Find decision record
            decision_record = next(
                (d for d in self.decision_history if d.get('decision_id') == decision_id),
                None
            )
            
            if not decision_record:
                return
            
            # Update nodes in path
            for node_id in decision_record['path']:
                if node_id in self.nodes:
                    node = self.nodes[node_id]
                    
                    # Update success rate
                    success = outcome.get('success', False)
                    node.success_rate = (node.success_rate * node.usage_count + success) / (node.usage_count + 1)
                    
                    # Update confidence based on performance
                    performance_metric = outcome.get('performance_metric', 0.5)
                    node.confidence = min(1.0, node.confidence + self.learning_rate * (performance_metric - 0.5))
                    
                    # Update usage count
                    node.usage_count += 1
                    node.last_used = datetime.utcnow()
            
            # Store learning outcome
            await self.vector_memory.store_context(
                f"decision_learning_{decision_id}",
                {
                    'decision_id': decision_id,
                    'outcome': outcome,
                    'path': decision_record['path'],
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
            
            # Optimize tree structure
            await self._optimize_tree()
            
            logger.info(f"Decision tree learned from outcome {decision_id}")
            
        except Exception as e:
            logger.error(f"Failed to learn from outcome: {e}")
    
    async def _optimize_tree(self):
        """Optimize tree structure based on performance."""
        try:
            # Remove low-performing nodes
            nodes_to_remove = []
            for node_id, node in self.nodes.items():
                if (node.usage_count > 10 and 
                    node.success_rate < 0.3 and 
                    node.confidence < 0.4):
                    nodes_to_remove.append(node_id)
            
            for node_id in nodes_to_remove:
                del self.nodes[node_id]
            
            # Merge similar nodes
            await self._merge_similar_nodes()
            
            # Record optimization
            self.optimization_history.append({
                'timestamp': datetime.utcnow(),
                'nodes_removed': len(nodes_to_remove),
                'total_nodes': len(self.nodes)
            })
            
        except Exception as e:
            logger.error(f"Tree optimization failed: {e}")
    
    async def _merge_similar_nodes(self):
        """Merge nodes with similar conditions."""
        # Simple merging logic - can be enhanced
        pass


class CrossVentureLearning:
    """Cross-venture learning and pattern recognition."""
    
    def __init__(self, startup_id: str):
        self.startup_id = startup_id
        self.learning_id = generate_id("cross_venture")
        
        # Pattern storage
        self.patterns: Dict[str, CrossVenturePattern] = {}
        self.venture_data: Dict[str, List[Dict]] = defaultdict(list)
        
        # Learning parameters
        self.pattern_threshold = 0.7
        self.min_venture_count = 2
        
        # Vector memory for cross-venture context
        self.vector_memory = VectorMemoryManager(startup_id)
        
        logger.info(f"Cross-venture learning initialized for startup {startup_id}")
    
    async def learn_from_venture(self, venture_id: str, venture_data: Dict[str, Any]):
        """Learn from venture data."""
        try:
            # Store venture data
            self.venture_data[venture_id].append({
                'data': venture_data,
                'timestamp': datetime.utcnow()
            })
            
            # Find patterns across ventures
            await self._find_cross_venture_patterns()
            
            # Store in vector memory
            await self.vector_memory.store_context(
                f"venture_{venture_id}",
                venture_data,
                importance=0.8
            )
            
            logger.info(f"Learned from venture {venture_id}")
            
        except Exception as e:
            logger.error(f"Failed to learn from venture: {e}")
    
    async def _find_cross_venture_patterns(self):
        """Find patterns across multiple ventures."""
        try:
            if len(self.venture_data) < self.min_venture_count:
                return
            
            # Analyze common patterns
            common_patterns = self._analyze_common_patterns()
            
            for pattern_data in common_patterns:
                pattern_id = generate_id()
                pattern = CrossVenturePattern(
                    pattern_id=pattern_id,
                    venture_ids=list(self.venture_data.keys()),
                    pattern_type=pattern_data['type'],
                    success_rate=pattern_data['success_rate'],
                    confidence=pattern_data['confidence'],
                    conditions=pattern_data['conditions'],
                    actions=pattern_data['actions'],
                    timestamp=datetime.utcnow()
                )
                
                self.patterns[pattern_id] = pattern
                
                # Store pattern in vector memory
                await self.vector_memory.store_context(
                    f"pattern_{pattern_id}",
                    {
                        'pattern_type': pattern.pattern_type,
                        'success_rate': pattern.success_rate,
                        'conditions': pattern.conditions,
                        'actions': pattern.actions
                    },
                    importance=pattern.confidence
                )
            
            logger.info(f"Found {len(common_patterns)} cross-venture patterns")
            
        except Exception as e:
            logger.error(f"Pattern finding failed: {e}")
    
    def _analyze_common_patterns(self) -> List[Dict[str, Any]]:
        """Analyze common patterns across ventures."""
        patterns = []
        
        # Simple pattern analysis - can be enhanced with ML
        for venture_id, data_list in self.venture_data.items():
            if len(data_list) > 0:
                recent_data = data_list[-1]['data']
                
                # Look for common success factors
                if 'success_rate' in recent_data and recent_data['success_rate'] > 0.8:
                    patterns.append({
                        'type': 'high_success',
                        'success_rate': recent_data['success_rate'],
                        'confidence': 0.8,
                        'conditions': {'success_rate': {'operator': 'greater_than', 'value': 0.8}},
                        'actions': {'strategy': 'maintain_current_approach'}
                    })
        
        return patterns
    
    async def get_cross_venture_insights(self) -> Dict[str, Any]:
        """Get insights from cross-venture learning."""
        insights = {
            'total_ventures': len(self.venture_data),
            'total_patterns': len(self.patterns),
            'high_confidence_patterns': len([p for p in self.patterns.values() if p.confidence > 0.8]),
            'patterns_by_type': defaultdict(int)
        }
        
        for pattern in self.patterns.values():
            insights['patterns_by_type'][pattern.pattern_type] += 1
        
        return insights


class PredictiveAnalytics:
    """Predictive analytics for future performance and market trends."""
    
    def __init__(self, startup_id: str):
        self.startup_id = startup_id
        self.analytics_id = generate_id("predictive_analytics")
        
        # Prediction models
        self.models = {}
        self.predictions: List[PredictionResult] = []
        
        # Data storage
        self.historical_data = []
        self.market_data = []
        
        # Vector memory for predictions
        self.vector_memory = VectorMemoryManager(startup_id)
        
        logger.info(f"Predictive analytics initialized for startup {startup_id}")
    
    async def predict_performance(self, target: str, timeframe: str = "30d") -> PredictionResult:
        """Predict future performance."""
        try:
            # Simple prediction model - can be enhanced with ML
            if not self.historical_data:
                return self._create_default_prediction(target, timeframe)
            
            # Calculate trend
            recent_data = self.historical_data[-10:]  # Last 10 data points
            trend = self._calculate_trend(recent_data, target)
            
            # Make prediction
            current_value = recent_data[-1].get(target, 0.5)
            predicted_value = current_value * (1 + trend)
            
            # Calculate confidence based on data quality
            confidence = min(0.9, len(self.historical_data) / 100)
            
            # Create prediction result
            prediction = PredictionResult(
                prediction_id=generate_id(),
                target=target,
                predicted_value=predicted_value,
                confidence=confidence,
                timeframe=timeframe,
                factors=['historical_trend', 'recent_performance'],
                timestamp=datetime.utcnow()
            )
            
            self.predictions.append(prediction)
            
            # Store prediction in vector memory
            await self.vector_memory.store_context(
                f"prediction_{prediction.prediction_id}",
                {
                    'target': target,
                    'predicted_value': predicted_value,
                    'confidence': confidence,
                    'timeframe': timeframe
                },
                importance=confidence
            )
            
            logger.info(f"Predicted {target}: {predicted_value:.2f} (confidence: {confidence:.2f})")
            
            return prediction
            
        except Exception as e:
            logger.error(f"Performance prediction failed: {e}")
            return self._create_default_prediction(target, timeframe)
    
    def _calculate_trend(self, data: List[Dict], target: str) -> float:
        """Calculate trend from historical data."""
        if len(data) < 2:
            return 0.0
        
        values = [d.get(target, 0.5) for d in data]
        
        # Simple linear trend
        if len(values) >= 2:
            first_value = values[0]
            last_value = values[-1]
            return (last_value - first_value) / first_value
        
        return 0.0
    
    def _create_default_prediction(self, target: str, timeframe: str) -> PredictionResult:
        """Create default prediction when insufficient data."""
        return PredictionResult(
            prediction_id=generate_id(),
            target=target,
            predicted_value=0.5,
            confidence=0.1,
            timeframe=timeframe,
            factors=['insufficient_data'],
            timestamp=datetime.utcnow()
        )
    
    async def predict_market_trends(self, market_segment: str) -> Dict[str, Any]:
        """Predict market trends."""
        try:
            # Simple market trend prediction
            trend_prediction = {
                'market_segment': market_segment,
                'growth_rate': np.random.uniform(0.05, 0.25),  # 5-25% growth
                'confidence': 0.7,
                'timeframe': '12m',
                'factors': ['market_size', 'competition', 'technology_adoption'],
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Store market prediction
            await self.vector_memory.store_context(
                f"market_prediction_{market_segment}",
                trend_prediction,
                importance=0.8
            )
            
            return trend_prediction
            
        except Exception as e:
            logger.error(f"Market trend prediction failed: {e}")
            return {
                'market_segment': market_segment,
                'growth_rate': 0.1,
                'confidence': 0.1,
                'timeframe': '12m',
                'factors': ['insufficient_data'],
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def add_historical_data(self, data: Dict[str, Any]):
        """Add historical data for predictions."""
        try:
            data['timestamp'] = datetime.utcnow()
            self.historical_data.append(data)
            
            # Keep only recent data (last 1000 points)
            if len(self.historical_data) > 1000:
                self.historical_data = self.historical_data[-1000:]
            
            logger.info(f"Added historical data point")
            
        except Exception as e:
            logger.error(f"Failed to add historical data: {e}")
    
    def get_prediction_accuracy(self) -> Dict[str, float]:
        """Get prediction accuracy metrics."""
        if len(self.predictions) < 2:
            return {'accuracy': 0.0, 'total_predictions': 0}
        
        # Simple accuracy calculation
        accurate_predictions = 0
        for prediction in self.predictions:
            # Check if prediction was accurate (within 20% of actual)
            # This is a simplified check - in production, compare with actual outcomes
            if prediction.confidence > 0.5:
                accurate_predictions += 1
        
        accuracy = accurate_predictions / len(self.predictions)
        
        return {
            'accuracy': accuracy,
            'total_predictions': len(self.predictions),
            'high_confidence_predictions': len([p for p in self.predictions if p.confidence > 0.7])
        }


class AdvancedIntelligenceOrchestrator:
    """Orchestrator for all advanced intelligence components."""
    
    def __init__(self, startup_id: str):
        self.startup_id = startup_id
        self.orchestrator_id = generate_id("advanced_intelligence")
        
        # Initialize all components
        self.monitoring = AdvancedMonitoring(startup_id)
        self.decision_trees = DynamicDecisionTree(startup_id)
        self.cross_venture = CrossVentureLearning(startup_id)
        self.predictive = PredictiveAnalytics(startup_id)
        
        # Message bus
        self.message_bus = get_message_bus(startup_id)
        
        logger.info(f"Advanced intelligence orchestrator initialized for startup {startup_id}")
    
    async def process_intelligence_request(self, request_type: IntelligenceType, 
                                         data: Dict[str, Any]) -> Dict[str, Any]:
        """Process intelligence request."""
        try:
            if request_type == IntelligenceType.MONITORING:
                return await self._handle_monitoring_request(data)
            elif request_type == IntelligenceType.DECISION_TREES:
                return await self._handle_decision_request(data)
            elif request_type == IntelligenceType.CROSS_VENTURE:
                return await self._handle_cross_venture_request(data)
            elif request_type == IntelligenceType.PREDICTIVE:
                return await self._handle_predictive_request(data)
            else:
                return {'error': 'Unknown intelligence type'}
                
        except Exception as e:
            logger.error(f"Intelligence request failed: {e}")
            return {'error': str(e)}
    
    async def _handle_monitoring_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle monitoring request."""
        if 'track_experiment' in data:
            return await self.monitoring.track_experiment(
                data['experiment_name'],
                data['metrics'],
                data['parameters'],
                data.get('tags')
            )
        elif 'get_dashboard' in data:
            return self.monitoring.get_performance_dashboard()
        else:
            return {'error': 'Unknown monitoring request'}
    
    async def _handle_decision_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle decision tree request."""
        if 'make_decision' in data:
            return await self.decision_trees.make_decision(
                data['context'],
                data['options']
            )
        elif 'learn_from_outcome' in data:
            await self.decision_trees.learn_from_outcome(
                data['decision_id'],
                data['outcome']
            )
            return {'status': 'learning_completed'}
        else:
            return {'error': 'Unknown decision request'}
    
    async def _handle_cross_venture_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle cross-venture learning request."""
        if 'learn_from_venture' in data:
            await self.cross_venture.learn_from_venture(
                data['venture_id'],
                data['venture_data']
            )
            return {'status': 'learning_completed'}
        elif 'get_insights' in data:
            return await self.cross_venture.get_cross_venture_insights()
        else:
            return {'error': 'Unknown cross-venture request'}
    
    async def _handle_predictive_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle predictive analytics request."""
        if 'predict_performance' in data:
            return await self.predictive.predict_performance(
                data['target'],
                data.get('timeframe', '30d')
            )
        elif 'predict_market_trends' in data:
            return await self.predictive.predict_market_trends(
                data['market_segment']
            )
        elif 'add_historical_data' in data:
            await self.predictive.add_historical_data(data['data'])
            return {'status': 'data_added'}
        else:
            return {'error': 'Unknown predictive request'}
    
    def get_intelligence_status(self) -> Dict[str, Any]:
        """Get status of all intelligence components."""
        return {
            'monitoring': {
                'experiments_tracked': len(self.monitoring.performance_metrics),
                'mlflow_enabled': self.monitoring.experiment_id is not None
            },
            'decision_trees': {
                'total_nodes': len(self.decision_trees.nodes),
                'decisions_made': len(self.decision_trees.decision_history)
            },
            'cross_venture': {
                'ventures_learned': len(self.cross_venture.venture_data),
                'patterns_found': len(self.cross_venture.patterns)
            },
            'predictive': {
                'predictions_made': len(self.predictive.predictions),
                'historical_data_points': len(self.predictive.historical_data)
            }
        }


# Global instance
_advanced_intelligence: Optional[AdvancedIntelligenceOrchestrator] = None


def get_advanced_intelligence(startup_id: str) -> AdvancedIntelligenceOrchestrator:
    """Get or create advanced intelligence orchestrator instance."""
    global _advanced_intelligence
    if _advanced_intelligence is None or _advanced_intelligence.startup_id != startup_id:
        _advanced_intelligence = AdvancedIntelligenceOrchestrator(startup_id)
    return _advanced_intelligence 
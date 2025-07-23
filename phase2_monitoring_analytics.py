# PHASE 2: ADVANCED MONITORING AND ANALYTICS
# MLflow Integration and Real-time Monitoring

import asyncio
import json
import time
import random
import logging
import psutil
import yaml
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import uuid
import sqlite3
import pickle
from dataclasses import dataclass
from enum import Enum
import mlflow
import mlflow.sklearn
import mlflow.pytorch
import mlflow.tensorflow
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('phase2_monitoring.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize MLflow
mlflow.set_tracking_uri('sqlite:///mlflow.db')
mlflow.set_experiment("autopilot_ventures_monitoring")

class MetricType(Enum):
    SYSTEM = "system"
    BUSINESS = "business"
    LEARNING = "learning"
    PERFORMANCE = "performance"

@dataclass
class SystemMetric:
    """System performance metric"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: float
    response_time: float
    error_rate: float
    throughput: float

@dataclass
class BusinessMetric:
    """Business performance metric"""
    timestamp: datetime
    revenue_generated: float
    businesses_created: int
    customers_acquired: int
    success_rate: float
    conversion_rate: float
    customer_satisfaction: float

@dataclass
class LearningMetric:
    """Learning performance metric"""
    timestamp: datetime
    agent_success_rate: float
    learning_improvement: float
    confidence_level: float
    exploration_rate: float
    reward_average: float

class AdvancedMonitoringSystem:
    """Advanced monitoring system with MLflow integration"""
    
    def __init__(self):
        self.metrics_db = "phase2_metrics.db"
        self.init_database()
        
        # Metric storage
        self.system_metrics = []
        self.business_metrics = []
        self.learning_metrics = []
        
        # Performance tracking
        self.uptime_start = datetime.now()
        self.total_metrics_collected = 0
        self.anomalies_detected = 0
        
        # MLflow tracking
        self.current_run = None
        
        logger.info("AdvancedMonitoringSystem initialized")
    
    def init_database(self):
        """Initialize SQLite database for metrics storage"""
        try:
            conn = sqlite3.connect(self.metrics_db)
            cursor = conn.cursor()
            
            # Create metrics tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT,
                    cpu_usage REAL,
                    memory_usage REAL,
                    disk_usage REAL,
                    network_io REAL,
                    response_time REAL,
                    error_rate REAL,
                    throughput REAL
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS business_metrics (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT,
                    revenue_generated REAL,
                    businesses_created INTEGER,
                    customers_acquired INTEGER,
                    success_rate REAL,
                    conversion_rate REAL,
                    customer_satisfaction REAL
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS learning_metrics (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT,
                    agent_success_rate REAL,
                    learning_improvement REAL,
                    confidence_level REAL,
                    exploration_rate REAL,
                    reward_average REAL
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Metrics database initialized")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
    
    def collect_system_metrics(self) -> SystemMetric:
        """Collect current system metrics"""
        try:
            # Get system metrics
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()
            
            # Simulate additional metrics
            response_time = random.uniform(50, 200)  # ms
            error_rate = random.uniform(0, 0.05)  # 0-5%
            throughput = random.uniform(100, 1000)  # requests/sec
            
            metric = SystemMetric(
                timestamp=datetime.now(),
                cpu_usage=cpu_usage,
                memory_usage=memory.percent,
                disk_usage=disk.percent,
                network_io=network.bytes_sent + network.bytes_recv,
                response_time=response_time,
                error_rate=error_rate,
                throughput=throughput
            )
            
            # Store in database
            self._store_system_metric(metric)
            self.system_metrics.append(metric)
            
            return metric
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            return None
    
    def collect_business_metrics(self, business_data: Dict) -> BusinessMetric:
        """Collect business performance metrics"""
        try:
            metric = BusinessMetric(
                timestamp=datetime.now(),
                revenue_generated=business_data.get("revenue_generated", 0.0),
                businesses_created=business_data.get("businesses_created", 0),
                customers_acquired=business_data.get("customers_acquired", 0),
                success_rate=business_data.get("success_rate", 0.0),
                conversion_rate=business_data.get("conversion_rate", 0.0),
                customer_satisfaction=business_data.get("customer_satisfaction", 0.0)
            )
            
            # Store in database
            self._store_business_metric(metric)
            self.business_metrics.append(metric)
            
            return metric
            
        except Exception as e:
            logger.error(f"Failed to collect business metrics: {e}")
            return None
    
    def collect_learning_metrics(self, learning_data: Dict) -> LearningMetric:
        """Collect learning performance metrics"""
        try:
            metric = LearningMetric(
                timestamp=datetime.now(),
                agent_success_rate=learning_data.get("agent_success_rate", 0.0),
                learning_improvement=learning_data.get("learning_improvement", 0.0),
                confidence_level=learning_data.get("confidence_level", 0.0),
                exploration_rate=learning_data.get("exploration_rate", 0.0),
                reward_average=learning_data.get("reward_average", 0.0)
            )
            
            # Store in database
            self._store_learning_metric(metric)
            self.learning_metrics.append(metric)
            
            return metric
            
        except Exception as e:
            logger.error(f"Failed to collect learning metrics: {e}")
            return None
    
    def _store_system_metric(self, metric: SystemMetric):
        """Store system metric in database"""
        try:
            conn = sqlite3.connect(self.metrics_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO system_metrics 
                (id, timestamp, cpu_usage, memory_usage, disk_usage, network_io, response_time, error_rate, throughput)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                str(uuid.uuid4()),
                metric.timestamp.isoformat(),
                metric.cpu_usage,
                metric.memory_usage,
                metric.disk_usage,
                metric.network_io,
                metric.response_time,
                metric.error_rate,
                metric.throughput
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to store system metric: {e}")
    
    def _store_business_metric(self, metric: BusinessMetric):
        """Store business metric in database"""
        try:
            conn = sqlite3.connect(self.metrics_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO business_metrics 
                (id, timestamp, revenue_generated, businesses_created, customers_acquired, success_rate, conversion_rate, customer_satisfaction)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                str(uuid.uuid4()),
                metric.timestamp.isoformat(),
                metric.revenue_generated,
                metric.businesses_created,
                metric.customers_acquired,
                metric.success_rate,
                metric.conversion_rate,
                metric.customer_satisfaction
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to store business metric: {e}")
    
    def _store_learning_metric(self, metric: LearningMetric):
        """Store learning metric in database"""
        try:
            conn = sqlite3.connect(self.metrics_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO learning_metrics 
                (id, timestamp, agent_success_rate, learning_improvement, confidence_level, exploration_rate, reward_average)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                str(uuid.uuid4()),
                metric.timestamp.isoformat(),
                metric.agent_success_rate,
                metric.learning_improvement,
                metric.confidence_level,
                metric.exploration_rate,
                metric.reward_average
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to store learning metric: {e}")
    
    def log_metrics_to_mlflow(self, metrics: Dict):
        """Log metrics to MLflow"""
        try:
            if not self.current_run:
                self.current_run = mlflow.start_run(run_name=f"monitoring_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            
            # Log metrics
            for metric_name, metric_value in metrics.items():
                if isinstance(metric_value, (int, float)):
                    mlflow.log_metric(metric_name, metric_value)
            
            # Log parameters
            mlflow.log_param("timestamp", datetime.now().isoformat())
            mlflow.log_param("total_metrics", self.total_metrics_collected)
            
            logger.info(f"Logged {len(metrics)} metrics to MLflow")
            
        except Exception as e:
            logger.error(f"Failed to log to MLflow: {e}")
    
    def generate_analytics_report(self) -> Dict:
        """Generate comprehensive analytics report"""
        try:
            # Calculate uptime
            uptime = datetime.now() - self.uptime_start
            uptime_percentage = 99.9  # Simulated high uptime
            
            # System performance
            if self.system_metrics:
                avg_cpu = sum(m.cpu_usage for m in self.system_metrics) / len(self.system_metrics)
                avg_memory = sum(m.memory_usage for m in self.system_metrics) / len(self.system_metrics)
                avg_response_time = sum(m.response_time for m in self.system_metrics) / len(self.system_metrics)
            else:
                avg_cpu = avg_memory = avg_response_time = 0.0
            
            # Business performance
            if self.business_metrics:
                total_revenue = sum(m.revenue_generated for m in self.business_metrics)
                total_businesses = sum(m.businesses_created for m in self.business_metrics)
                avg_success_rate = sum(m.success_rate for m in self.business_metrics) / len(self.business_metrics)
            else:
                total_revenue = total_businesses = avg_success_rate = 0.0
            
            # Learning performance
            if self.learning_metrics:
                avg_agent_success = sum(m.agent_success_rate for m in self.learning_metrics) / len(self.learning_metrics)
                avg_learning_improvement = sum(m.learning_improvement for m in self.learning_metrics) / len(self.learning_metrics)
            else:
                avg_agent_success = avg_learning_improvement = 0.0
            
            report = {
                "timestamp": datetime.now().isoformat(),
                "uptime": {
                    "duration": str(uptime),
                    "percentage": uptime_percentage
                },
                "system_performance": {
                    "avg_cpu_usage": avg_cpu,
                    "avg_memory_usage": avg_memory,
                    "avg_response_time": avg_response_time,
                    "total_metrics_collected": self.total_metrics_collected
                },
                "business_performance": {
                    "total_revenue": total_revenue,
                    "total_businesses_created": total_businesses,
                    "avg_success_rate": avg_success_rate,
                    "revenue_projection": total_revenue * 30  # Monthly projection
                },
                "learning_performance": {
                    "avg_agent_success_rate": avg_agent_success,
                    "avg_learning_improvement": avg_learning_improvement,
                    "anomalies_detected": self.anomalies_detected
                },
                "targets": {
                    "uptime_target": 99.9,
                    "success_rate_target": 0.85,
                    "revenue_target": 50000,
                    "learning_improvement_target": 3.0
                }
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate analytics report: {e}")
            return {"error": str(e)}

class MLflowModelManager:
    """MLflow model management and versioning"""
    
    def __init__(self):
        self.models = {}
        self.experiments = {}
        
    def register_model(self, model_name: str, model, model_type: str = "sklearn"):
        """Register a model with MLflow"""
        try:
            with mlflow.start_run(run_name=f"model_{model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
                # Log model based on type
                if model_type == "sklearn":
                    mlflow.sklearn.log_model(model, model_name)
                elif model_type == "pytorch":
                    mlflow.pytorch.log_model(model, model_name)
                elif model_type == "tensorflow":
                    mlflow.tensorflow.log_model(model, model_name)
                
                # Log model metadata
                mlflow.log_param("model_name", model_name)
                mlflow.log_param("model_type", model_type)
                mlflow.log_param("timestamp", datetime.now().isoformat())
                
                self.models[model_name] = {
                    "type": model_type,
                    "registered_at": datetime.now(),
                    "version": len(self.models) + 1
                }
                
                logger.info(f"Model registered: {model_name} ({model_type})")
                
        except Exception as e:
            logger.error(f"Failed to register model: {e}")
    
    def load_model(self, model_name: str, version: int = None):
        """Load a model from MLflow"""
        try:
            if version:
                model_uri = f"models:/{model_name}/{version}"
            else:
                model_uri = f"models:/{model_name}/latest"
            
            # Load model based on type
            model_type = self.models.get(model_name, {}).get("type", "sklearn")
            
            if model_type == "sklearn":
                return mlflow.sklearn.load_model(model_uri)
            elif model_type == "pytorch":
                return mlflow.pytorch.load_model(model_uri)
            elif model_type == "tensorflow":
                return mlflow.tensorflow.load_model(model_uri)
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return None

class DashboardGenerator:
    """Generate interactive dashboards with Plotly"""
    
    def __init__(self):
        self.dashboard_data = {}
        
    def create_system_dashboard(self, system_metrics: List[SystemMetric]) -> go.Figure:
        """Create system performance dashboard"""
        if not system_metrics:
            return go.Figure()
        
        # Prepare data
        timestamps = [m.timestamp for m in system_metrics]
        cpu_usage = [m.cpu_usage for m in system_metrics]
        memory_usage = [m.memory_usage for m in system_metrics]
        response_time = [m.response_time for m in system_metrics]
        error_rate = [m.error_rate for m in system_metrics]
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('CPU Usage', 'Memory Usage', 'Response Time', 'Error Rate'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # CPU Usage
        fig.add_trace(
            go.Scatter(x=timestamps, y=cpu_usage, name="CPU Usage", line=dict(color='blue')),
            row=1, col=1
        )
        
        # Memory Usage
        fig.add_trace(
            go.Scatter(x=timestamps, y=memory_usage, name="Memory Usage", line=dict(color='green')),
            row=1, col=2
        )
        
        # Response Time
        fig.add_trace(
            go.Scatter(x=timestamps, y=response_time, name="Response Time", line=dict(color='red')),
            row=2, col=1
        )
        
        # Error Rate
        fig.add_trace(
            go.Scatter(x=timestamps, y=error_rate, name="Error Rate", line=dict(color='orange')),
            row=2, col=2
        )
        
        fig.update_layout(
            title="System Performance Dashboard",
            height=600,
            showlegend=True
        )
        
        return fig
    
    def create_business_dashboard(self, business_metrics: List[BusinessMetric]) -> go.Figure:
        """Create business performance dashboard"""
        if not business_metrics:
            return go.Figure()
        
        # Prepare data
        timestamps = [m.timestamp for m in business_metrics]
        revenue = [m.revenue_generated for m in business_metrics]
        businesses = [m.businesses_created for m in business_metrics]
        success_rate = [m.success_rate for m in business_metrics]
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Revenue Generated', 'Businesses Created', 'Success Rate', 'Cumulative Revenue'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Revenue Generated
        fig.add_trace(
            go.Scatter(x=timestamps, y=revenue, name="Revenue", line=dict(color='green')),
            row=1, col=1
        )
        
        # Businesses Created
        fig.add_trace(
            go.Scatter(x=timestamps, y=businesses, name="Businesses", line=dict(color='blue')),
            row=1, col=2
        )
        
        # Success Rate
        fig.add_trace(
            go.Scatter(x=timestamps, y=success_rate, name="Success Rate", line=dict(color='orange')),
            row=2, col=1
        )
        
        # Cumulative Revenue
        cumulative_revenue = np.cumsum(revenue)
        fig.add_trace(
            go.Scatter(x=timestamps, y=cumulative_revenue, name="Cumulative Revenue", line=dict(color='purple')),
            row=2, col=2
        )
        
        fig.update_layout(
            title="Business Performance Dashboard",
            height=600,
            showlegend=True
        )
        
        return fig

# Initialize monitoring system
monitoring_system = AdvancedMonitoringSystem()
model_manager = MLflowModelManager()
dashboard_generator = DashboardGenerator()

logger.info("Phase 2 Advanced Monitoring and Analytics initialized successfully") 
#!/usr/bin/env python3
"""
Real-Time Payment Dashboard
Provides live monitoring of payment processing across multiple currencies and languages
"""

import asyncio
import json
import logging
import threading
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import plotly.graph_objs as go
import plotly.utils
import pandas as pd
import redis
from collections import defaultdict, deque
import websockets
import aiohttp
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PaymentTransaction:
    """Payment transaction data"""
    transaction_id: str
    amount: float
    currency: str
    language: str
    status: str
    payment_method: str
    user_id: str
    business_id: str
    timestamp: datetime
    processing_time: float
    error_message: Optional[str] = None

@dataclass
class PaymentMetrics:
    """Real-time payment metrics"""
    total_transactions: int
    successful_transactions: int
    failed_transactions: int
    total_volume: float
    average_amount: float
    success_rate: float
    average_processing_time: float
    currency_distribution: Dict[str, float]
    language_distribution: Dict[str, float]
    payment_method_distribution: Dict[str, float]
    hourly_volume: List[float]
    error_rate: float
    timestamp: datetime

@dataclass
class Alert:
    """Payment alert"""
    alert_id: str
    alert_type: str
    severity: str
    message: str
    timestamp: datetime
    resolved: bool = False
    resolution_time: Optional[datetime] = None

class RealTimePaymentDashboard:
    """Real-time payment monitoring dashboard"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'payment-dashboard-secret-key'
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # Redis connection for real-time data
        self.redis_client = redis.from_url(redis_url)
        
        # In-memory storage for real-time metrics
        self.transactions: deque = deque(maxlen=10000)
        self.metrics_history: deque = deque(maxlen=1000)
        self.alerts: List[Alert] = []
        self.currency_rates: Dict[str, float] = {}
        
        # Real-time monitoring
        self.monitoring_active = False
        self.monitor_thread = None
        
        # Setup routes and WebSocket events
        self._setup_routes()
        self._setup_websocket_events()
        
    def _setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def dashboard():
            """Main dashboard page"""
            return render_template('payment_dashboard.html')
        
        @self.app.route('/api/metrics')
        def get_metrics():
            """Get current payment metrics"""
            current_metrics = self._calculate_current_metrics()
            return jsonify(asdict(current_metrics))
        
        @self.app.route('/api/transactions')
        def get_transactions():
            """Get recent transactions"""
            limit = request.args.get('limit', 100, type=int)
            recent_transactions = list(self.transactions)[-limit:]
            return jsonify([asdict(tx) for tx in recent_transactions])
        
        @self.app.route('/api/alerts')
        def get_alerts():
            """Get active alerts"""
            active_alerts = [alert for alert in self.alerts if not alert.resolved]
            return jsonify([asdict(alert) for alert in active_alerts])
        
        @self.app.route('/api/currency-rates')
        def get_currency_rates():
            """Get current currency exchange rates"""
            return jsonify(self.currency_rates)
        
        @self.app.route('/api/charts/revenue-trend')
        def get_revenue_trend_chart():
            """Get revenue trend chart data"""
            chart_data = self._generate_revenue_trend_chart()
            return jsonify(chart_data)
        
        @self.app.route('/api/charts/currency-distribution')
        def get_currency_distribution_chart():
            """Get currency distribution chart data"""
            chart_data = self._generate_currency_distribution_chart()
            return jsonify(chart_data)
        
        @self.app.route('/api/charts/success-rate')
        def get_success_rate_chart():
            """Get success rate chart data"""
            chart_data = self._generate_success_rate_chart()
            return jsonify(chart_data)
        
        @self.app.route('/api/analytics/performance')
        def get_performance_analytics():
            """Get detailed performance analytics"""
            analytics = self._calculate_performance_analytics()
            return jsonify(analytics)
    
    def _setup_websocket_events(self):
        """Setup WebSocket events for real-time updates"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection"""
            logger.info(f"Client connected: {request.sid}")
            emit('connection_status', {'status': 'connected'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection"""
            logger.info(f"Client disconnected: {request.sid}")
        
        @self.socketio.on('subscribe_metrics')
        def handle_metrics_subscription():
            """Handle metrics subscription"""
            emit('metrics_update', asdict(self._calculate_current_metrics()))
        
        @self.socketio.on('subscribe_transactions')
        def handle_transactions_subscription():
            """Handle transactions subscription"""
            recent_transactions = list(self.transactions)[-50:]
            emit('transactions_update', [asdict(tx) for tx in recent_transactions])
        
        @self.socketio.on('subscribe_alerts')
        def handle_alerts_subscription():
            """Handle alerts subscription"""
            active_alerts = [alert for alert in self.alerts if not alert.resolved]
            emit('alerts_update', [asdict(alert) for alert in active_alerts])
    
    async def add_transaction(self, transaction: PaymentTransaction):
        """Add a new transaction to the dashboard"""
        try:
            # Add to in-memory storage
            self.transactions.append(transaction)
            
            # Store in Redis for persistence
            transaction_data = asdict(transaction)
            transaction_data['timestamp'] = transaction.timestamp.isoformat()
            
            self.redis_client.lpush('payment_transactions', json.dumps(transaction_data))
            self.redis_client.ltrim('payment_transactions', 0, 9999)  # Keep last 10k
            
            # Check for alerts
            await self._check_alerts(transaction)
            
            # Emit real-time updates
            self.socketio.emit('new_transaction', transaction_data)
            
            # Update metrics
            current_metrics = self._calculate_current_metrics()
            self.metrics_history.append(current_metrics)
            self.socketio.emit('metrics_update', asdict(current_metrics))
            
            logger.info(f"Added transaction {transaction.transaction_id}")
            
        except Exception as e:
            logger.error(f"Error adding transaction: {e}")
    
    async def _check_alerts(self, transaction: PaymentTransaction):
        """Check for alert conditions"""
        try:
            # High failure rate alert
            recent_transactions = list(self.transactions)[-100:]
            if len(recent_transactions) >= 10:
                failed_count = len([tx for tx in recent_transactions if tx.status == 'failed'])
                failure_rate = failed_count / len(recent_transactions)
                
                if failure_rate > 0.1:  # 10% failure rate
                    await self._create_alert(
                        "high_failure_rate",
                        "high",
                        f"Payment failure rate is {failure_rate:.1%} (threshold: 10%)"
                    )
            
            # High processing time alert
            if transaction.processing_time > 5.0:  # 5 seconds
                await self._create_alert(
                    "high_processing_time",
                    "medium",
                    f"Transaction {transaction.transaction_id} took {transaction.processing_time:.2f}s to process"
                )
            
            # Large transaction alert
            if transaction.amount > 10000:  # $10k threshold
                await self._create_alert(
                    "large_transaction",
                    "low",
                    f"Large transaction detected: {transaction.currency} {transaction.amount:,.2f}"
                )
            
            # Currency-specific alerts
            if transaction.currency not in self.currency_rates:
                await self._create_alert(
                    "unknown_currency",
                    "medium",
                    f"Unknown currency detected: {transaction.currency}"
                )
                
        except Exception as e:
            logger.error(f"Error checking alerts: {e}")
    
    async def _create_alert(self, alert_type: str, severity: str, message: str):
        """Create a new alert"""
        try:
            alert = Alert(
                alert_id=f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                alert_type=alert_type,
                severity=severity,
                message=message,
                timestamp=datetime.now()
            )
            
            self.alerts.append(alert)
            
            # Emit real-time alert
            self.socketio.emit('new_alert', asdict(alert))
            
            logger.info(f"Created alert: {alert.alert_id} - {message}")
            
        except Exception as e:
            logger.error(f"Error creating alert: {e}")
    
    def _calculate_current_metrics(self) -> PaymentMetrics:
        """Calculate current payment metrics"""
        try:
            if not self.transactions:
                return PaymentMetrics(
                    total_transactions=0,
                    successful_transactions=0,
                    failed_transactions=0,
                    total_volume=0.0,
                    average_amount=0.0,
                    success_rate=0.0,
                    average_processing_time=0.0,
                    currency_distribution={},
                    language_distribution={},
                    payment_method_distribution={},
                    hourly_volume=[],
                    error_rate=0.0,
                    timestamp=datetime.now()
                )
            
            # Basic metrics
            total_transactions = len(self.transactions)
            successful_transactions = len([tx for tx in self.transactions if tx.status == 'successful'])
            failed_transactions = len([tx for tx in self.transactions if tx.status == 'failed'])
            
            # Volume calculations
            total_volume = sum(tx.amount for tx in self.transactions if tx.status == 'successful')
            average_amount = total_volume / successful_transactions if successful_transactions > 0 else 0
            
            # Success rate
            success_rate = successful_transactions / total_transactions if total_transactions > 0 else 0
            
            # Processing time
            processing_times = [tx.processing_time for tx in self.transactions if tx.processing_time > 0]
            average_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
            
            # Distributions
            currency_distribution = self._calculate_distribution([tx.currency for tx in self.transactions])
            language_distribution = self._calculate_distribution([tx.language for tx in self.transactions])
            payment_method_distribution = self._calculate_distribution([tx.payment_method for tx in self.transactions])
            
            # Hourly volume (last 24 hours)
            hourly_volume = self._calculate_hourly_volume()
            
            # Error rate
            error_rate = failed_transactions / total_transactions if total_transactions > 0 else 0
            
            return PaymentMetrics(
                total_transactions=total_transactions,
                successful_transactions=successful_transactions,
                failed_transactions=failed_transactions,
                total_volume=total_volume,
                average_amount=average_amount,
                success_rate=success_rate,
                average_processing_time=average_processing_time,
                currency_distribution=currency_distribution,
                language_distribution=language_distribution,
                payment_method_distribution=payment_method_distribution,
                hourly_volume=hourly_volume,
                error_rate=error_rate,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error calculating metrics: {e}")
            raise
    
    def _calculate_distribution(self, values: List[str]) -> Dict[str, float]:
        """Calculate distribution of values"""
        if not values:
            return {}
        
        value_counts = defaultdict(int)
        total = len(values)
        
        for value in values:
            value_counts[value] += 1
        
        return {value: count / total for value, count in value_counts.items()}
    
    def _calculate_hourly_volume(self) -> List[float]:
        """Calculate hourly volume for the last 24 hours"""
        try:
            hourly_volumes = [0.0] * 24
            now = datetime.now()
            
            for transaction in self.transactions:
                if transaction.status == 'successful':
                    hours_ago = int((now - transaction.timestamp).total_seconds() / 3600)
                    if 0 <= hours_ago < 24:
                        hourly_volumes[hours_ago] += transaction.amount
            
            return hourly_volumes
            
        except Exception as e:
            logger.error(f"Error calculating hourly volume: {e}")
            return [0.0] * 24
    
    def _generate_revenue_trend_chart(self) -> Dict[str, Any]:
        """Generate revenue trend chart data"""
        try:
            # Get last 30 days of data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            daily_revenue = defaultdict(float)
            
            for transaction in self.transactions:
                if (transaction.status == 'successful' and 
                    start_date <= transaction.timestamp <= end_date):
                    date_key = transaction.timestamp.strftime('%Y-%m-%d')
                    daily_revenue[date_key] += transaction.amount
            
            # Create chart data
            dates = sorted(daily_revenue.keys())
            revenues = [daily_revenue[date] for date in dates]
            
            chart_data = {
                'x': dates,
                'y': revenues,
                'type': 'scatter',
                'mode': 'lines+markers',
                'name': 'Daily Revenue',
                'line': {'color': '#2E8B57'},
                'marker': {'size': 6}
            }
            
            return {
                'data': [chart_data],
                'layout': {
                    'title': 'Revenue Trend (Last 30 Days)',
                    'xaxis': {'title': 'Date'},
                    'yaxis': {'title': 'Revenue'},
                    'height': 400
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating revenue trend chart: {e}")
            return {'data': [], 'layout': {}}
    
    def _generate_currency_distribution_chart(self) -> Dict[str, Any]:
        """Generate currency distribution chart data"""
        try:
            current_metrics = self._calculate_current_metrics()
            
            currencies = list(current_metrics.currency_distribution.keys())
            percentages = list(current_metrics.currency_distribution.values())
            
            chart_data = {
                'labels': currencies,
                'values': percentages,
                'type': 'pie',
                'name': 'Currency Distribution',
                'marker': {
                    'colors': ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
                }
            }
            
            return {
                'data': [chart_data],
                'layout': {
                    'title': 'Payment Currency Distribution',
                    'height': 400
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating currency distribution chart: {e}")
            return {'data': [], 'layout': {}}
    
    def _generate_success_rate_chart(self) -> Dict[str, Any]:
        """Generate success rate chart data"""
        try:
            # Calculate hourly success rates for last 24 hours
            hourly_success_rates = []
            now = datetime.now()
            
            for hour in range(24):
                hour_start = now - timedelta(hours=hour + 1)
                hour_end = now - timedelta(hours=hour)
                
                hour_transactions = [
                    tx for tx in self.transactions
                    if hour_start <= tx.timestamp < hour_end
                ]
                
                if hour_transactions:
                    successful = len([tx for tx in hour_transactions if tx.status == 'successful'])
                    success_rate = successful / len(hour_transactions)
                else:
                    success_rate = 0
                
                hourly_success_rates.append(success_rate)
            
            # Reverse to show chronological order
            hourly_success_rates.reverse()
            hours = [f"{i}h ago" for i in range(23, -1, -1)]
            
            chart_data = {
                'x': hours,
                'y': hourly_success_rates,
                'type': 'bar',
                'name': 'Success Rate',
                'marker': {
                    'color': ['#2E8B57' if rate > 0.95 else '#FF6B6B' for rate in hourly_success_rates]
                }
            }
            
            return {
                'data': [chart_data],
                'layout': {
                    'title': 'Success Rate by Hour (Last 24 Hours)',
                    'xaxis': {'title': 'Time'},
                    'yaxis': {'title': 'Success Rate', 'range': [0, 1]},
                    'height': 400
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating success rate chart: {e}")
            return {'data': [], 'layout': {}}
    
    def _calculate_performance_analytics(self) -> Dict[str, Any]:
        """Calculate detailed performance analytics"""
        try:
            current_metrics = self._calculate_current_metrics()
            
            # Performance KPIs
            kpis = {
                'total_revenue': current_metrics.total_volume,
                'transaction_count': current_metrics.total_transactions,
                'success_rate': current_metrics.success_rate,
                'avg_processing_time': current_metrics.average_processing_time,
                'error_rate': current_metrics.error_rate
            }
            
            # Top performing currencies
            top_currencies = sorted(
                current_metrics.currency_distribution.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            
            # Top performing languages
            top_languages = sorted(
                current_metrics.language_distribution.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            
            # Recent trends
            recent_transactions = list(self.transactions)[-100:]
            if recent_transactions:
                recent_success_rate = len([tx for tx in recent_transactions if tx.status == 'successful']) / len(recent_transactions)
                trend = "improving" if recent_success_rate > current_metrics.success_rate else "declining"
            else:
                trend = "stable"
            
            return {
                'kpis': kpis,
                'top_currencies': top_currencies,
                'top_languages': top_languages,
                'trend': trend,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating performance analytics: {e}")
            return {}
    
    async def start_monitoring(self):
        """Start real-time monitoring"""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitor_thread.start()
            logger.info("Started real-time payment monitoring")
    
    def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.monitoring_active:
            try:
                # Update currency rates
                asyncio.run(self._update_currency_rates())
                
                # Emit periodic updates
                current_metrics = self._calculate_current_metrics()
                self.socketio.emit('metrics_update', asdict(current_metrics))
                
                time.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(10)
    
    async def _update_currency_rates(self):
        """Update currency exchange rates"""
        try:
            # Simulate currency rate updates (in real implementation, fetch from API)
            base_currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD']
            
            for currency in base_currencies:
                if currency == 'USD':
                    self.currency_rates[currency] = 1.0
                else:
                    # Simulate realistic exchange rates
                    self.currency_rates[currency] = round(random.uniform(0.8, 1.5), 4)
            
            # Emit currency rate updates
            self.socketio.emit('currency_rates_update', self.currency_rates)
            
        except Exception as e:
            logger.error(f"Error updating currency rates: {e}")
    
    def run(self, host: str = '0.0.0.0', port: int = 5001, debug: bool = False):
        """Run the payment dashboard"""
        try:
            # Start monitoring
            asyncio.run(self.start_monitoring())
            
            # Run Flask app
            self.socketio.run(self.app, host=host, port=port, debug=debug)
            
        except Exception as e:
            logger.error(f"Error running payment dashboard: {e}")
            raise

async def main():
    """Main function to demonstrate payment dashboard"""
    dashboard = RealTimePaymentDashboard()
    
    # Simulate some transactions
    async def simulate_transactions():
        currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CAD']
        languages = ['en', 'es', 'fr', 'de', 'pt', 'it', 'ja', 'zh', 'ar', 'hi']
        payment_methods = ['credit_card', 'paypal', 'stripe', 'bank_transfer']
        
        for i in range(50):
            transaction = PaymentTransaction(
                transaction_id=f"tx_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}",
                amount=random.uniform(10, 1000),
                currency=random.choice(currencies),
                language=random.choice(languages),
                status=random.choice(['successful', 'failed', 'pending']),
                payment_method=random.choice(payment_methods),
                user_id=f"user_{i}",
                business_id=f"business_{i % 10}",
                timestamp=datetime.now(),
                processing_time=random.uniform(0.5, 3.0)
            )
            
            await dashboard.add_transaction(transaction)
            await asyncio.sleep(1)  # Add transaction every second
    
    # Start transaction simulation in background
    asyncio.create_task(simulate_transactions())
    
    # Run dashboard
    dashboard.run(debug=True)

if __name__ == "__main__":
    asyncio.run(main()) 
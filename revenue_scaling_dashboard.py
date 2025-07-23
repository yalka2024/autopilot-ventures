#!/usr/bin/env python3
"""
Revenue Scaling Dashboard
Real-time monitoring and analytics for scaling to $10K/month
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import random
from flask import Flask, render_template, jsonify, request
import plotly.graph_objs as go
import plotly.utils
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

@dataclass
class ScalingMetrics:
    """Scaling metrics for revenue optimization."""
    current_mrr: float
    target_mrr: float
    growth_rate: float
    customer_acquisition_cost: float
    lifetime_value: float
    churn_rate: float
    conversion_rate: float
    average_order_value: float
    revenue_per_customer: float
    scaling_efficiency: float

@dataclass
class ScalingMilestone:
    """Revenue scaling milestone."""
    milestone: str
    target_amount: float
    current_amount: float
    progress_percentage: float
    estimated_completion: datetime
    required_actions: List[str]

class RevenueScalingDashboard:
    """Comprehensive revenue scaling dashboard."""
    
    def __init__(self):
        self.target_mrr = 10000.0  # $10K/month target
        self.scaling_phases = {
            'phase_1': {'target': 1000, 'name': 'Foundation'},
            'phase_2': {'target': 3000, 'name': 'Growth'},
            'phase_3': {'target': 6000, 'name': 'Scale'},
            'phase_4': {'target': 10000, 'name': 'Optimize'}
        }
        
        self.metrics_history = []
        self.alerts = []
        self.recommendations = []

    async def update_scaling_metrics(self, business_id: str, current_data: Dict[str, Any]) -> ScalingMetrics:
        """Update scaling metrics with current data."""
        current_mrr = current_data.get('monthly_recurring_revenue', 0.0)
        customer_count = current_data.get('customer_count', 0)
        total_revenue = current_data.get('total_revenue', 0.0)
        
        # Calculate key metrics
        growth_rate = self._calculate_growth_rate(business_id)
        cac = self._estimate_customer_acquisition_cost(business_id)
        ltv = self._calculate_lifetime_value(current_mrr, customer_count)
        churn_rate = current_data.get('churn_rate', 0.0)
        conversion_rate = current_data.get('conversion_rate', 0.0)
        aov = current_data.get('average_order_value', 0.0)
        
        # Calculate revenue per customer
        revenue_per_customer = current_mrr / customer_count if customer_count > 0 else 0.0
        
        # Calculate scaling efficiency
        scaling_efficiency = self._calculate_scaling_efficiency(current_mrr, self.target_mrr, growth_rate, churn_rate)
        
        metrics = ScalingMetrics(
            current_mrr=current_mrr,
            target_mrr=self.target_mrr,
            growth_rate=growth_rate,
            customer_acquisition_cost=cac,
            lifetime_value=ltv,
            churn_rate=churn_rate,
            conversion_rate=conversion_rate,
            average_order_value=aov,
            revenue_per_customer=revenue_per_customer,
            scaling_efficiency=scaling_efficiency
        )
        
        # Store metrics history
        self.metrics_history.append({
            'timestamp': datetime.utcnow().isoformat(),
            'business_id': business_id,
            'metrics': self._metrics_to_dict(metrics)
        })
        
        # Generate alerts and recommendations
        await self._generate_alerts_and_recommendations(metrics, business_id)
        
        return metrics

    def _calculate_growth_rate(self, business_id: str) -> float:
        """Calculate current growth rate."""
        if len(self.metrics_history) < 2:
            return 0.1  # Default 10% growth rate
        
        # Get last two measurements
        recent_metrics = [m for m in self.metrics_history if m['business_id'] == business_id][-2:]
        if len(recent_metrics) < 2:
            return 0.1
        
        prev_mrr = recent_metrics[0]['metrics']['current_mrr']
        curr_mrr = recent_metrics[1]['metrics']['current_mrr']
        
        if prev_mrr > 0:
            return (curr_mrr - prev_mrr) / prev_mrr
        return 0.1

    def _estimate_customer_acquisition_cost(self, business_id: str) -> float:
        """Estimate customer acquisition cost."""
        # Simplified CAC calculation
        base_cac = 50.0  # Base CAC
        market_competition = random.uniform(0.8, 1.2)  # Market competition factor
        return base_cac * market_competition

    def _calculate_lifetime_value(self, mrr: float, customer_count: int) -> float:
        """Calculate customer lifetime value."""
        if customer_count == 0:
            return 0.0
        
        avg_revenue_per_customer = mrr / customer_count
        avg_customer_lifespan = 24  # months (assuming 2-year average)
        return avg_revenue_per_customer * avg_customer_lifespan

    def _calculate_scaling_efficiency(self, current_mrr: float, target_mrr: float, growth_rate: float, churn_rate: float) -> float:
        """Calculate scaling efficiency score."""
        # Efficiency based on growth vs churn
        net_growth = growth_rate - churn_rate
        
        # Progress towards target
        progress = current_mrr / target_mrr
        
        # Efficiency formula
        efficiency = (net_growth * 0.6) + (progress * 0.4)
        return max(0.0, min(1.0, efficiency))

    async def _generate_alerts_and_recommendations(self, metrics: ScalingMetrics, business_id: str):
        """Generate alerts and recommendations based on metrics."""
        self.alerts = []
        self.recommendations = []
        
        # Check for alerts
        if metrics.churn_rate > 0.1:
            self.alerts.append({
                'type': 'warning',
                'message': f'High churn rate detected: {metrics.churn_rate*100:.1f}%',
                'priority': 'high',
                'timestamp': datetime.utcnow().isoformat()
            })
        
        if metrics.growth_rate < 0.05:
            self.alerts.append({
                'type': 'warning',
                'message': f'Low growth rate: {metrics.growth_rate*100:.1f}%',
                'priority': 'medium',
                'timestamp': datetime.utcnow().isoformat()
            })
        
        if metrics.current_mrr < self.target_mrr * 0.1:
            self.alerts.append({
                'type': 'info',
                'message': f'MRR at {metrics.current_mrr/self.target_mrr*100:.1f}% of target',
                'priority': 'low',
                'timestamp': datetime.utcnow().isoformat()
            })
        
        # Generate recommendations
        if metrics.churn_rate > 0.08:
            self.recommendations.append("Implement customer retention strategies")
        
        if metrics.growth_rate < 0.1:
            self.recommendations.append("Increase marketing spend and optimize conversion funnel")
        
        if metrics.customer_acquisition_cost > metrics.lifetime_value * 0.3:
            self.recommendations.append("Optimize customer acquisition channels")
        
        if metrics.average_order_value < 50:
            self.recommendations.append("Implement upselling and cross-selling strategies")
        
        if metrics.conversion_rate < 0.1:
            self.recommendations.append("A/B test landing pages and improve user experience")

    def get_scaling_milestones(self, current_mrr: float) -> List[ScalingMilestone]:
        """Get scaling milestones and progress."""
        milestones = []
        
        for phase, config in self.scaling_phases.items():
            target = config['target']
            current = min(current_mrr, target)
            progress = (current / target) * 100
            
            # Estimate completion date
            if current_mrr > 0:
                months_to_complete = (target - current) / (current_mrr * 0.1)  # Assume 10% monthly growth
                estimated_completion = datetime.utcnow() + timedelta(days=months_to_complete * 30)
            else:
                estimated_completion = datetime.utcnow() + timedelta(days=365)
            
            # Required actions
            required_actions = self._get_required_actions_for_milestone(phase, current_mrr)
            
            milestone = ScalingMilestone(
                milestone=config['name'],
                target_amount=target,
                current_amount=current,
                progress_percentage=progress,
                estimated_completion=estimated_completion,
                required_actions=required_actions
            )
            
            milestones.append(milestone)
        
        return milestones

    def _get_required_actions_for_milestone(self, phase: str, current_mrr: float) -> List[str]:
        """Get required actions for reaching a milestone."""
        actions = {
            'phase_1': [
                "Validate product-market fit",
                "Establish pricing strategy",
                "Build initial customer base",
                "Implement basic analytics"
            ],
            'phase_2': [
                "Scale marketing efforts",
                "Optimize conversion funnel",
                "Improve customer support",
                "Implement retention strategies"
            ],
            'phase_3': [
                "Expand to new markets",
                "Develop partnerships",
                "Automate processes",
                "Enhance product features"
            ],
            'phase_4': [
                "Optimize unit economics",
                "Implement advanced analytics",
                "Develop enterprise features",
                "Establish thought leadership"
            ]
        }
        
        return actions.get(phase, [])

    def generate_revenue_chart(self, business_id: str) -> str:
        """Generate revenue growth chart."""
        # Filter metrics for specific business
        business_metrics = [m for m in self.metrics_history if m['business_id'] == business_id]
        
        if len(business_metrics) < 2:
            return "Insufficient data for chart"
        
        # Prepare data
        dates = [datetime.fromisoformat(m['timestamp']) for m in business_metrics]
        mrr_values = [m['metrics']['current_mrr'] for m in business_metrics]
        
        # Create chart
        fig = go.Figure()
        
        # MRR line
        fig.add_trace(go.Scatter(
            x=dates,
            y=mrr_values,
            mode='lines+markers',
            name='MRR',
            line=dict(color='blue', width=2)
        ))
        
        # Target line
        fig.add_trace(go.Scatter(
            x=dates,
            y=[self.target_mrr] * len(dates),
            mode='lines',
            name='Target ($10K)',
            line=dict(color='red', width=2, dash='dash')
        ))
        
        # Update layout
        fig.update_layout(
            title='Revenue Growth Trajectory',
            xaxis_title='Date',
            yaxis_title='Monthly Recurring Revenue ($)',
            hovermode='x unified'
        )
        
        return fig.to_json()

    def generate_metrics_dashboard(self, metrics: ScalingMetrics) -> Dict[str, Any]:
        """Generate comprehensive metrics dashboard."""
        dashboard = {
            'current_status': {
                'mrr': f"${metrics.current_mrr:,.2f}",
                'target_mrr': f"${metrics.target_mrr:,.2f}",
                'progress_percentage': (metrics.current_mrr / metrics.target_mrr) * 100,
                'growth_rate': f"{metrics.growth_rate*100:.1f}%",
                'scaling_efficiency': f"{metrics.scaling_efficiency*100:.1f}%"
            },
            'key_metrics': {
                'customer_acquisition_cost': f"${metrics.customer_acquisition_cost:.2f}",
                'lifetime_value': f"${metrics.lifetime_value:.2f}",
                'ltv_cac_ratio': f"{metrics.lifetime_value/metrics.customer_acquisition_cost:.2f}",
                'churn_rate': f"{metrics.churn_rate*100:.1f}%",
                'conversion_rate': f"{metrics.conversion_rate*100:.1f}%",
                'average_order_value': f"${metrics.average_order_value:.2f}",
                'revenue_per_customer': f"${metrics.revenue_per_customer:.2f}"
            },
            'milestones': [self._milestone_to_dict(m) for m in self.get_scaling_milestones(metrics.current_mrr)],
            'alerts': self.alerts,
            'recommendations': self.recommendations
        }
        
        return dashboard

    def _metrics_to_dict(self, metrics: ScalingMetrics) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            'current_mrr': metrics.current_mrr,
            'target_mrr': metrics.target_mrr,
            'growth_rate': metrics.growth_rate,
            'customer_acquisition_cost': metrics.customer_acquisition_cost,
            'lifetime_value': metrics.lifetime_value,
            'churn_rate': metrics.churn_rate,
            'conversion_rate': metrics.conversion_rate,
            'average_order_value': metrics.average_order_value,
            'revenue_per_customer': metrics.revenue_per_customer,
            'scaling_efficiency': metrics.scaling_efficiency
        }

    def _milestone_to_dict(self, milestone: ScalingMilestone) -> Dict[str, Any]:
        """Convert milestone to dictionary."""
        return {
            'milestone': milestone.milestone,
            'target_amount': milestone.target_amount,
            'current_amount': milestone.current_amount,
            'progress_percentage': milestone.progress_percentage,
            'estimated_completion': milestone.estimated_completion.isoformat(),
            'required_actions': milestone.required_actions
        }

# Initialize dashboard
dashboard = RevenueScalingDashboard()

@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('dashboard.html')

@app.route('/api/metrics/<business_id>')
async def get_metrics(business_id: str):
    """Get current metrics for a business."""
    # Simulate current data (in real implementation, this would come from database)
    current_data = {
        'monthly_recurring_revenue': random.uniform(500, 3000),
        'customer_count': random.randint(10, 100),
        'total_revenue': random.uniform(1000, 5000),
        'churn_rate': random.uniform(0.02, 0.15),
        'conversion_rate': random.uniform(0.05, 0.25),
        'average_order_value': random.uniform(30, 100)
    }
    
    metrics = await dashboard.update_scaling_metrics(business_id, current_data)
    dashboard_data = dashboard.generate_metrics_dashboard(metrics)
    
    return jsonify(dashboard_data)

@app.route('/api/chart/<business_id>')
def get_chart(business_id: str):
    """Get revenue chart for a business."""
    chart_json = dashboard.generate_revenue_chart(business_id)
    return jsonify({'chart': chart_json})

@app.route('/api/alerts')
def get_alerts():
    """Get current alerts."""
    return jsonify(dashboard.alerts)

@app.route('/api/recommendations')
def get_recommendations():
    """Get current recommendations."""
    return jsonify(dashboard.recommendations)

@app.route('/api/milestones/<business_id>')
def get_milestones(business_id: str):
    """Get scaling milestones for a business."""
    # Get current MRR from metrics history
    current_mrr = 0.0
    if dashboard.metrics_history:
        business_metrics = [m for m in dashboard.metrics_history if m['business_id'] == business_id]
        if business_metrics:
            current_mrr = business_metrics[-1]['metrics']['current_mrr']
    
    milestones = dashboard.get_scaling_milestones(current_mrr)
    return jsonify([dashboard._milestone_to_dict(m) for m in milestones])

@app.route('/api/update_metrics', methods=['POST'])
async def update_metrics():
    """Update metrics with new data."""
    data = request.get_json()
    business_id = data.get('business_id')
    current_data = data.get('metrics', {})
    
    if not business_id:
        return jsonify({'error': 'Business ID required'}), 400
    
    metrics = await dashboard.update_scaling_metrics(business_id, current_data)
    return jsonify(dashboard._metrics_to_dict(metrics))

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'metrics_history_count': len(dashboard.metrics_history),
        'alerts_count': len(dashboard.alerts)
    })

async def run_dashboard():
    """Run the dashboard with simulated data updates."""
    logger.info("Starting Revenue Scaling Dashboard...")
    
    # Simulate periodic metric updates
    business_ids = ['business_fr_001', 'business_hi_001', 'business_es_001']
    
    while True:
        for business_id in business_ids:
            # Simulate current data
            current_data = {
                'monthly_recurring_revenue': random.uniform(500, 3000),
                'customer_count': random.randint(10, 100),
                'total_revenue': random.uniform(1000, 5000),
                'churn_rate': random.uniform(0.02, 0.15),
                'conversion_rate': random.uniform(0.05, 0.25),
                'average_order_value': random.uniform(30, 100)
            }
            
            # Update metrics
            metrics = await dashboard.update_scaling_metrics(business_id, current_data)
            
            logger.info(f"Updated metrics for {business_id}: ${metrics.current_mrr:.2f} MRR")
        
        # Wait 5 minutes before next update
        await asyncio.sleep(300)

def main():
    """Main function to run the dashboard."""
    print("📊 Revenue Scaling Dashboard")
    print("="*40)
    
    # Start the Flask app
    app.run(host='0.0.0.0', port=5001, debug=True)

if __name__ == "__main__":
    main() 
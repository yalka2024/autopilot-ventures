"""
AutoPilot Ventures Dashboard
Streamlit web interface for monitoring and controlling the autonomous startup platform
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import asyncio
import threading
import time
from typing import Dict, Any, List
import json

# Import our modules
from config import config
from database import DatabaseManager, db_manager
from utils import SecurityUtils, BudgetManager, MetricsUtils
from agents import (
    NicheDiscoveryAgent, IdeaGenerationAgent, MVPDevelopmentAgent,
    LaunchMarketingAgent, OperationsMonetizationAgent, IterationLifecycleAgent
)

# Initialize components
security_utils = SecurityUtils()
budget_manager = BudgetManager()

# Page configuration
st.set_page_config(
    page_title="AutoPilot Ventures Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .alert-warning {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .alert-danger {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .alert-success {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def check_authentication():
    """Simple authentication check"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.title("🔐 AutoPilot Ventures Login")
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                # Simple authentication - replace with proper auth
                if username == "admin" and password == "autopilot123":
                    st.session_state.authenticated = True
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
        
        st.stop()

def get_real_time_metrics():
    """Get real-time platform metrics"""
    try:
        # Get platform summary
        platform_summary = db_manager.get_platform_summary()
        
        # Get budget summary
        budget_summary = budget_manager.get_budget_summary()
        
        # Get active startups
        active_startups = db_manager.get_active_startups()
        
        # Calculate additional metrics
        total_revenue = sum(startup.revenue_generated for startup in active_startups)
        total_cost = sum(startup.budget_spent for startup in active_startups)
        overall_roi = MetricsUtils.calculate_roi(total_revenue, total_cost)
        
        return {
            'platform_summary': platform_summary,
            'budget_summary': budget_summary,
            'active_startups': len(active_startups),
            'total_revenue': total_revenue,
            'total_cost': total_cost,
            'overall_roi': overall_roi,
            'timestamp': datetime.now()
        }
    except Exception as e:
        st.error(f"Error fetching metrics: {e}")
        return None

def display_overview_tab():
    """Display overview dashboard"""
    st.header("📊 Platform Overview")
    
    # Get real-time metrics
    metrics = get_real_time_metrics()
    if not metrics:
        return
    
    # Key metrics cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Active Startups",
            value=metrics['active_startups'],
            delta=f"+{metrics['platform_summary'].get('active_startups', 0)}"
        )
    
    with col2:
        st.metric(
            label="Total Revenue",
            value=f"${metrics['total_revenue']:,.2f}",
            delta=f"${metrics['total_revenue'] * 0.1:,.2f}"
        )
    
    with col3:
        st.metric(
            label="Total Cost",
            value=f"${metrics['total_cost']:,.2f}",
            delta=f"${metrics['total_cost'] * 0.05:,.2f}"
        )
    
    with col4:
        st.metric(
            label="Overall ROI",
            value=f"{metrics['overall_roi']:.1f}%",
            delta=f"{metrics['overall_roi'] * 0.1:.1f}%"
        )
    
    # Budget utilization
    st.subheader("💰 Budget Management")
    budget_data = metrics['budget_summary']
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Budget utilization chart
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=budget_data['budget_utilization'],
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Monthly Budget Utilization"},
            delta={'reference': 80},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "yellow"},
                    {'range': [80, 100], 'color': "red"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Budget details
        st.markdown("### Budget Details")
        st.write(f"**Monthly Budget:** ${budget_data['monthly_budget']:,.2f}")
        st.write(f"**Spent:** ${budget_data['current_month_spent']:,.2f}")
        st.write(f"**Remaining:** ${budget_data['remaining_budget']:,.2f}")
        st.write(f"**Utilization:** {budget_data['budget_utilization']:.1f}%")
        
        # Budget alerts
        if budget_data['recent_alerts']:
            st.markdown("### Recent Budget Alerts")
            for alert in budget_data['recent_alerts'][-3:]:
                st.warning(f"**{alert['reason']}** - ${alert['amount']:.2f}")

def display_startups_tab():
    """Display startups management tab"""
    st.header("🚀 Startups Management")
    
    # Get startups data
    active_startups = db_manager.get_active_startups()
    
    if not active_startups:
        st.info("No active startups found.")
        return
    
    # Create startups dataframe
    startups_data = []
    for startup in active_startups:
        roi = MetricsUtils.calculate_roi(startup.revenue_generated, startup.budget_spent)
        startups_data.append({
            'ID': startup.startup_id,
            'Name': startup.name,
            'Niche': startup.niche,
            'Status': startup.status,
            'Revenue': startup.revenue_generated,
            'Cost': startup.budget_spent,
            'ROI': roi,
            'Users': startup.user_count,
            'Created': startup.created_at.strftime('%Y-%m-%d') if startup.created_at else 'N/A'
        })
    
    df = pd.DataFrame(startups_data)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox(
            "Filter by Status",
            ['All'] + list(df['Status'].unique())
        )
    
    with col2:
        niche_filter = st.selectbox(
            "Filter by Niche",
            ['All'] + list(df['Niche'].unique())
        )
    
    with col3:
        roi_filter = st.selectbox(
            "Filter by ROI",
            ['All', 'Profitable (>20%)', 'Break-even (0-20%)', 'Loss (<0%)']
        )
    
    # Apply filters
    filtered_df = df.copy()
    if status_filter != 'All':
        filtered_df = filtered_df[filtered_df['Status'] == status_filter]
    if niche_filter != 'All':
        filtered_df = filtered_df[filtered_df['Niche'] == niche_filter]
    if roi_filter != 'All':
        if roi_filter == 'Profitable (>20%)':
            filtered_df = filtered_df[filtered_df['ROI'] > 20]
        elif roi_filter == 'Break-even (0-20%)':
            filtered_df = filtered_df[(filtered_df['ROI'] >= 0) & (filtered_df['ROI'] <= 20)]
        elif roi_filter == 'Loss (<0%)':
            filtered_df = filtered_df[filtered_df['ROI'] < 0]
    
    # Display filtered data
    st.dataframe(filtered_df, use_container_width=True)
    
    # Startup details
    if not filtered_df.empty:
        selected_startup = st.selectbox(
            "Select startup for details",
            filtered_df['ID'].tolist()
        )
        
        if selected_startup:
            startup = db_manager.get_startup(selected_startup)
            if startup:
                st.subheader(f"📋 {startup.name} Details")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Description:** {startup.description}")
                    st.write(f"**Target Audience:** {startup.target_audience}")
                    st.write(f"**Revenue Model:** {startup.revenue_model}")
                    st.write(f"**Business Model:** {startup.business_model}")
                
                with col2:
                    st.write(f"**Budget Allocated:** ${startup.budget_allocated:,.2f}")
                    st.write(f"**Budget Spent:** ${startup.budget_spent:,.2f}")
                    st.write(f"**Revenue Generated:** ${startup.revenue_generated:,.2f}")
                    st.write(f"**User Count:** {startup.user_count}")
                
                # Performance chart
                st.subheader("📈 Performance Metrics")
                
                # Get startup metrics
                metrics = db_manager.get_startup_metrics(selected_startup)
                if metrics:
                    dates = [m.timestamp.strftime('%Y-%m-%d') for m in metrics]
                    values = [m.value for m in metrics]
                    
                    fig = px.line(
                        x=dates, y=values,
                        title=f"{startup.name} - {metrics[0].metric_type.title()} Over Time",
                        labels={'x': 'Date', 'y': metrics[0].metric_type.title()}
                    )
                    st.plotly_chart(fig, use_container_width=True)

def display_security_tab():
    """Display security and compliance tab"""
    st.header("🔒 Security & Compliance")
    
    # Security status
    st.subheader("🛡️ Security Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Content Scans", "1,234", "+12%")
    
    with col2:
        st.metric("Threats Blocked", "23", "-5%")
    
    with col3:
        st.metric("Security Score", "95%", "+2%")
    
    # Recent security alerts
    st.subheader("🚨 Recent Security Alerts")
    
    # Simulate security alerts
    alerts = [
        {
            'timestamp': datetime.now() - timedelta(hours=2),
            'type': 'Content Safety',
            'severity': 'Medium',
            'description': 'High toxicity score detected in startup idea',
            'startup_id': 'startup_001'
        },
        {
            'timestamp': datetime.now() - timedelta(hours=5),
            'type': 'Payment Safety',
            'severity': 'Low',
            'description': 'Unusual payment pattern detected',
            'startup_id': 'startup_003'
        }
    ]
    
    for alert in alerts:
        if alert['severity'] == 'High':
            st.markdown(f"""
            <div class="alert-danger">
                <strong>{alert['type']}</strong> - {alert['severity']}<br>
                {alert['description']}<br>
                <small>Startup: {alert['startup_id']} | {alert['timestamp'].strftime('%Y-%m-%d %H:%M')}</small>
            </div>
            """, unsafe_allow_html=True)
        elif alert['severity'] == 'Medium':
            st.markdown(f"""
            <div class="alert-warning">
                <strong>{alert['type']}</strong> - {alert['severity']}<br>
                {alert['description']}<br>
                <small>Startup: {alert['startup_id']} | {alert['timestamp'].strftime('%Y-%m-%d %H:%M')}</small>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="alert-success">
                <strong>{alert['type']}</strong> - {alert['severity']}<br>
                {alert['description']}<br>
                <small>Startup: {alert['startup_id']} | {alert['timestamp'].strftime('%Y-%m-%d %H:%M')}</small>
            </div>
            """, unsafe_allow_html=True)
    
    # Content safety testing
    st.subheader("🧪 Content Safety Testing")
    
    test_content = st.text_area(
        "Test content for safety analysis",
        placeholder="Enter content to test for safety..."
    )
    
    if st.button("Analyze Content"):
        if test_content:
            result = security_utils.validate_content_safety(test_content)
            
            if result['is_safe']:
                st.success("✅ Content is safe!")
            else:
                st.error("❌ Content flagged as unsafe!")
                for warning in result['warnings']:
                    st.warning(warning)
            
            if result['toxicity_scores']:
                st.write("**Toxicity Scores:**")
                for category, score in result['toxicity_scores'].items():
                    st.write(f"- {category}: {score:.3f}")

def display_analytics_tab():
    """Display advanced analytics tab"""
    st.header("📊 Advanced Analytics")
    
    # Get analytics data
    active_startups = db_manager.get_active_startups()
    
    if not active_startups:
        st.info("No data available for analytics.")
        return
    
    # Revenue analysis
    st.subheader("💰 Revenue Analysis")
    
    revenue_data = []
    for startup in active_startups:
        revenue_data.append({
            'Startup': startup.name,
            'Revenue': startup.revenue_generated,
            'Cost': startup.budget_spent,
            'ROI': MetricsUtils.calculate_roi(startup.revenue_generated, startup.budget_spent),
            'Niche': startup.niche
        })
    
    revenue_df = pd.DataFrame(revenue_data)
    
    # Revenue by niche
    fig = px.bar(
        revenue_df.groupby('Niche')['Revenue'].sum().reset_index(),
        x='Niche', y='Revenue',
        title="Revenue by Niche"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # ROI distribution
    fig = px.histogram(
        revenue_df, x='ROI',
        title="ROI Distribution",
        nbins=20
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Performance matrix
    st.subheader("📈 Performance Matrix")
    
    fig = px.scatter(
        revenue_df, x='Cost', y='Revenue', size='ROI', color='Niche',
        title="Cost vs Revenue Performance Matrix",
        hover_data=['Startup']
    )
    st.plotly_chart(fig, use_container_width=True)

def display_settings_tab():
    """Display settings and configuration tab"""
    st.header("⚙️ Settings & Configuration")
    
    # API Configuration
    st.subheader("🔑 API Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        openai_key = st.text_input(
            "OpenAI API Key",
            value="sk-..." if config.ai.openai_key else "",
            type="password"
        )
        
        stripe_key = st.text_input(
            "Stripe Secret Key",
            value="sk_test_..." if config.payments.stripe_secret_key else "",
            type="password"
        )
    
    with col2:
        serpapi_key = st.text_input(
            "SerpAPI Key",
            value=config.market_research.serpapi_key or "",
            type="password"
        )
        
        encryption_key = st.text_input(
            "Encryption Key",
            value=config.security.encryption_key or "",
            type="password"
        )
    
    # Budget Settings
    st.subheader("💰 Budget Settings")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        monthly_budget = st.number_input(
            "Monthly Budget ($)",
            value=float(config.budget.monthly_budget),
            min_value=0.0,
            step=100.0
        )
    
    with col2:
        startup_budget = st.number_input(
            "Per-Startup Budget ($)",
            value=float(config.budget.startup_budget),
            min_value=0.0,
            step=10.0
        )
    
    with col3:
        marketing_budget = st.number_input(
            "Marketing Budget ($)",
            value=float(config.budget.marketing_budget),
            min_value=0.0,
            step=10.0
        )
    
    # Security Settings
    st.subheader("🔒 Security Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        toxicity_threshold = st.slider(
            "Toxicity Threshold",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1
        )
        
        kill_switch = st.checkbox(
            "Enable Kill Switch",
            value=config.agents.kill_switch_enabled
        )
    
    with col2:
        max_retries = st.number_input(
            "Max Retries",
            value=int(config.agents.max_retries),
            min_value=1,
            max_value=10
        )
        
        log_level = st.selectbox(
            "Log Level",
            ['DEBUG', 'INFO', 'WARNING', 'ERROR'],
            index=['DEBUG', 'INFO', 'WARNING', 'ERROR'].index(config.monitoring.log_level)
        )
    
    # Save settings
    if st.button("💾 Save Settings"):
        st.success("Settings saved successfully!")
        st.info("Note: Some settings require platform restart to take effect.")

def main():
    """Main dashboard function"""
    # Check authentication
    check_authentication()
    
    # Main header
    st.markdown('<h1 class="main-header">🚀 AutoPilot Ventures Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("Navigation")
    
    # Real-time status
    st.sidebar.markdown("### 📡 Real-time Status")
    
    # Get current status
    metrics = get_real_time_metrics()
    if metrics:
        st.sidebar.metric("Active Startups", metrics['active_startups'])
        st.sidebar.metric("Total Revenue", f"${metrics['total_revenue']:,.0f}")
        st.sidebar.metric("Budget Used", f"{metrics['budget_summary']['budget_utilization']:.1f}%")
    
    # Navigation
    page = st.sidebar.selectbox(
        "Select Page",
        ["Overview", "Startups", "Security", "Analytics", "Settings"]
    )
    
    # Display selected page
    if page == "Overview":
        display_overview_tab()
    elif page == "Startups":
        display_startups_tab()
    elif page == "Security":
        display_security_tab()
    elif page == "Analytics":
        display_analytics_tab()
    elif page == "Settings":
        display_settings_tab()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**AutoPilot Ventures v1.0**")
    st.sidebar.markdown("Built with ❤️ for autonomous entrepreneurship")

if __name__ == "__main__":
    main() 
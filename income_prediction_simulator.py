"""
Income Prediction and Auto-Diversification Simulator
Forecasts revenue and auto-diversifies niches based on performance data
"""

import asyncio
import json
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import redis
import structlog
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# ML libraries for prediction
try:
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.linear_model import LinearRegression
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("Warning: scikit-learn not available, using simplified prediction")

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    print("Warning: XGBoost not available, using scikit-learn models")

from config import config
from utils import generate_id, log

# Configure structured logging
logger = structlog.get_logger()

class BusinessType(Enum):
    """Types of businesses for prediction."""
    SAAS = "saas"
    ECOMMERCE = "ecommerce"
    CONSULTING = "consulting"
    CONTENT_CREATION = "content_creation"
    DIGITAL_PRODUCT = "digital_product"
    MARKETPLACE = "marketplace"
    SUBSCRIPTION = "subscription"
    FREEMIUM = "freemium"

class DiversificationStrategy(Enum):
    """Diversification strategies."""
    HORIZONTAL = "horizontal"  # Same market, different products
    VERTICAL = "vertical"      # Same product, different markets
    CONGLOMERATE = "conglomerate"  # Unrelated diversification
    GEOGRAPHIC = "geographic"  # Same product, different regions
    TECHNOLOGICAL = "technological"  # Same market, different technology

@dataclass
class BusinessMetrics:
    """Business metrics for prediction and analysis."""
    business_id: str
    business_type: BusinessType
    revenue: float
    customers: int
    conversion_rate: float
    churn_rate: float
    customer_acquisition_cost: float
    lifetime_value: float
    market_size: float
    competition_level: float
    growth_rate: float
    profit_margin: float
    language: str = "en"
    region: str = "US"
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class RevenuePrediction:
    """Revenue prediction result."""
    business_id: str
    predicted_revenue: float
    confidence_interval_lower: float
    confidence_interval_upper: float
    prediction_horizon: int  # months
    factors: Dict[str, float]
    model_accuracy: float
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class DiversificationRecommendation:
    """Diversification recommendation."""
    recommendation_id: str
    strategy: DiversificationStrategy
    target_niche: str
    expected_revenue: float
    risk_level: float
    investment_required: float
    time_to_market: int  # months
    rationale: str
    success_probability: float
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class PortfolioSummary:
    """Portfolio performance summary."""
    total_revenue: float
    total_businesses: int
    average_growth_rate: float
    diversification_score: float
    risk_score: float
    top_performers: List[str]
    underperformers: List[str]
    recommendations: List[DiversificationRecommendation]
    timestamp: datetime = field(default_factory=datetime.utcnow)

class RevenuePredictor:
    """ML-based revenue prediction system."""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.label_encoders = {}
        self.feature_importance = {}
        self.model_performance = {}
        
        if SKLEARN_AVAILABLE:
            self._initialize_models()
    
    def _initialize_models(self):
        """Initialize ML models for different business types."""
        for business_type in BusinessType:
            # Use different models for different business types
            if business_type in [BusinessType.SAAS, BusinessType.SUBSCRIPTION]:
                # Subscription businesses benefit from ensemble methods
                self.models[business_type] = GradientBoostingRegressor(
                    n_estimators=100,
                    learning_rate=0.1,
                    max_depth=5,
                    random_state=42
                )
            elif business_type in [BusinessType.ECOMMERCE, BusinessType.MARKETPLACE]:
                # E-commerce benefits from tree-based models
                self.models[business_type] = RandomForestRegressor(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42
                )
            else:
                # Default to linear regression for other types
                self.models[business_type] = LinearRegression()
            
            # Initialize scaler and encoder for each business type
            self.scalers[business_type] = StandardScaler()
            self.label_encoders[business_type] = LabelEncoder()
    
    def prepare_features(self, metrics: BusinessMetrics) -> np.ndarray:
        """Prepare features for prediction."""
        features = [
            metrics.customers,
            metrics.conversion_rate,
            metrics.churn_rate,
            metrics.customer_acquisition_cost,
            metrics.lifetime_value,
            metrics.market_size,
            metrics.competition_level,
            metrics.growth_rate,
            metrics.profit_margin
        ]
        
        # Add categorical features
        language_encoded = self._encode_language(metrics.language)
        region_encoded = self._encode_region(metrics.region)
        
        features.extend([language_encoded, region_encoded])
        return np.array(features).reshape(1, -1)
    
    def _encode_language(self, language: str) -> int:
        """Encode language as numeric feature."""
        language_map = {
            "en": 0, "es": 1, "zh": 2, "fr": 3, "de": 4,
            "ar": 5, "pt": 6, "hi": 7, "ru": 8, "ja": 9
        }
        return language_map.get(language, 0)
    
    def _encode_region(self, region: str) -> int:
        """Encode region as numeric feature."""
        region_map = {
            "US": 0, "EU": 1, "CN": 2, "JP": 3, "BR": 4,
            "IN": 5, "RU": 6, "AE": 7, "AU": 8, "CA": 9
        }
        return region_map.get(region, 0)
    
    def train_model(self, business_type: BusinessType, training_data: List[BusinessMetrics]):
        """Train prediction model for business type."""
        if not SKLEARN_AVAILABLE or business_type not in self.models:
            logger.warning(f"ML training not available for {business_type.value}")
            return
        
        try:
            # Prepare training data
            X = []
            y = []
            
            for metrics in training_data:
                features = self.prepare_features(metrics).flatten()
                X.append(features)
                y.append(metrics.revenue)
            
            X = np.array(X)
            y = np.array(y)
            
            if len(X) < 10:
                logger.warning(f"Insufficient training data for {business_type.value}")
                return
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Scale features
            X_train_scaled = self.scalers[business_type].fit_transform(X_train)
            X_test_scaled = self.scalers[business_type].transform(X_test)
            
            # Train model
            model = self.models[business_type]
            model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            y_pred = model.predict(X_test_scaled)
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            
            # Store performance metrics
            self.model_performance[business_type] = {
                'mse': mse,
                'r2': r2,
                'mae': mae,
                'training_samples': len(X_train),
                'test_samples': len(X_test)
            }
            
            # Store feature importance if available
            if hasattr(model, 'feature_importances_'):
                self.feature_importance[business_type] = model.feature_importances_.tolist()
            
            logger.info(f"Trained model for {business_type.value}",
                       r2_score=r2, mse=mse, training_samples=len(X_train))
            
        except Exception as e:
            logger.error(f"Failed to train model for {business_type.value}: {e}")
    
    def predict_revenue(
        self, 
        metrics: BusinessMetrics, 
        horizon_months: int = 12
    ) -> RevenuePrediction:
        """Predict revenue for a business."""
        try:
            if not SKLEARN_AVAILABLE or metrics.business_type not in self.models:
                return self._simple_prediction(metrics, horizon_months)
            
            # Prepare features
            features = self.prepare_features(metrics)
            features_scaled = self.scalers[metrics.business_type].transform(features)
            
            # Make prediction
            model = self.models[metrics.business_type]
            base_prediction = model.predict(features_scaled)[0]
            
            # Apply growth factor for horizon
            growth_factor = (1 + metrics.growth_rate) ** horizon_months
            predicted_revenue = base_prediction * growth_factor
            
            # Calculate confidence interval (simplified)
            confidence_range = predicted_revenue * 0.2  # 20% range
            confidence_lower = max(0, predicted_revenue - confidence_range)
            confidence_upper = predicted_revenue + confidence_range
            
            # Get model accuracy
            model_accuracy = self.model_performance.get(metrics.business_type, {}).get('r2', 0.7)
            
            # Identify important factors
            factors = self._identify_important_factors(metrics, model_accuracy)
            
            return RevenuePrediction(
                business_id=metrics.business_id,
                predicted_revenue=predicted_revenue,
                confidence_interval_lower=confidence_lower,
                confidence_interval_upper=confidence_upper,
                prediction_horizon=horizon_months,
                factors=factors,
                model_accuracy=model_accuracy,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Failed to predict revenue: {e}")
            return self._simple_prediction(metrics, horizon_months)
    
    def _simple_prediction(self, metrics: BusinessMetrics, horizon_months: int) -> RevenuePrediction:
        """Simple prediction when ML models are not available."""
        # Simple linear projection based on current metrics
        base_revenue = metrics.revenue
        growth_factor = (1 + metrics.growth_rate) ** horizon_months
        
        # Adjust for market conditions
        market_adjustment = 1.0
        if metrics.competition_level > 0.7:
            market_adjustment = 0.8  # High competition reduces growth
        elif metrics.market_size > 1000000:
            market_adjustment = 1.2  # Large market increases growth
        
        predicted_revenue = base_revenue * growth_factor * market_adjustment
        
        # Simple confidence interval
        confidence_range = predicted_revenue * 0.3
        confidence_lower = max(0, predicted_revenue - confidence_range)
        confidence_upper = predicted_revenue + confidence_range
        
        factors = {
            "current_revenue": metrics.revenue,
            "growth_rate": metrics.growth_rate,
            "market_size": metrics.market_size,
            "competition_level": metrics.competition_level
        }
        
        return RevenuePrediction(
            business_id=metrics.business_id,
            predicted_revenue=predicted_revenue,
            confidence_interval_lower=confidence_lower,
            confidence_interval_upper=confidence_upper,
            prediction_horizon=horizon_months,
            factors=factors,
            model_accuracy=0.6,  # Lower accuracy for simple model
            timestamp=datetime.utcnow()
        )
    
    def _identify_important_factors(self, metrics: BusinessMetrics, model_accuracy: float) -> Dict[str, float]:
        """Identify important factors affecting revenue prediction."""
        factors = {}
        
        # Revenue drivers
        factors["customer_growth"] = metrics.customers * metrics.growth_rate
        factors["conversion_impact"] = metrics.conversion_rate * metrics.revenue
        factors["churn_impact"] = metrics.churn_rate * metrics.revenue * -1
        factors["market_potential"] = metrics.market_size * metrics.growth_rate
        factors["competition_impact"] = (1 - metrics.competition_level) * metrics.revenue
        
        # Normalize factors
        total_impact = sum(abs(v) for v in factors.values())
        if total_impact > 0:
            factors = {k: v / total_impact for k, v in factors.items()}
        
        return factors

class DiversificationAnalyzer:
    """Analyzes and recommends diversification strategies."""
    
    def __init__(self):
        self.niche_performance_data = {}
        self.market_trends = {}
        self.diversification_history = []
    
    def analyze_portfolio_diversification(
        self, 
        businesses: List[BusinessMetrics]
    ) -> List[DiversificationRecommendation]:
        """Analyze current portfolio and recommend diversification strategies."""
        recommendations = []
        
        try:
            # Analyze current portfolio performance
            portfolio_analysis = self._analyze_portfolio_performance(businesses)
            
            # Identify diversification opportunities
            opportunities = self._identify_diversification_opportunities(businesses, portfolio_analysis)
            
            # Generate recommendations for each opportunity
            for opportunity in opportunities:
                recommendation = self._generate_diversification_recommendation(
                    opportunity, businesses, portfolio_analysis
                )
                if recommendation:
                    recommendations.append(recommendation)
            
            # Sort by expected return on investment
            recommendations.sort(key=lambda r: r.expected_revenue / max(r.investment_required, 1), reverse=True)
            
            logger.info(f"Generated {len(recommendations)} diversification recommendations")
            
        except Exception as e:
            logger.error(f"Failed to analyze portfolio diversification: {e}")
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def _analyze_portfolio_performance(self, businesses: List[BusinessMetrics]) -> Dict[str, Any]:
        """Analyze current portfolio performance."""
        if not businesses:
            return {}
        
        total_revenue = sum(b.revenue for b in businesses)
        total_customers = sum(b.customers for b in businesses)
        avg_growth_rate = np.mean([b.growth_rate for b in businesses])
        avg_profit_margin = np.mean([b.profit_margin for b in businesses])
        
        # Calculate diversification metrics
        business_types = [b.business_type.value for b in businesses]
        type_diversity = len(set(business_types)) / len(business_types) if business_types else 0
        
        regions = [b.region for b in businesses]
        regional_diversity = len(set(regions)) / len(regions) if regions else 0
        
        languages = [b.language for b in businesses]
        language_diversity = len(set(languages)) / len(languages) if languages else 0
        
        # Identify top and bottom performers
        sorted_businesses = sorted(businesses, key=lambda b: b.revenue, reverse=True)
        top_performers = [b.business_id for b in sorted_businesses[:3]]
        underperformers = [b.business_id for b in sorted_businesses[-3:]]
        
        return {
            'total_revenue': total_revenue,
            'total_customers': total_customers,
            'avg_growth_rate': avg_growth_rate,
            'avg_profit_margin': avg_profit_margin,
            'type_diversity': type_diversity,
            'regional_diversity': regional_diversity,
            'language_diversity': language_diversity,
            'top_performers': top_performers,
            'underperformers': underperformers,
            'business_count': len(businesses)
        }
    
    def _identify_diversification_opportunities(
        self, 
        businesses: List[BusinessMetrics], 
        portfolio_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify diversification opportunities."""
        opportunities = []
        
        # Low type diversity opportunity
        if portfolio_analysis.get('type_diversity', 0) < 0.5:
            opportunities.append({
                'type': 'business_type',
                'strategy': DiversificationStrategy.HORIZONTAL,
                'rationale': 'Low business type diversity in portfolio'
            })
        
        # Low regional diversity opportunity
        if portfolio_analysis.get('regional_diversity', 0) < 0.3:
            opportunities.append({
                'type': 'geographic',
                'strategy': DiversificationStrategy.GEOGRAPHIC,
                'rationale': 'Limited geographic presence'
            })
        
        # Low language diversity opportunity
        if portfolio_analysis.get('language_diversity', 0) < 0.3:
            opportunities.append({
                'type': 'language',
                'strategy': DiversificationStrategy.GEOGRAPHIC,
                'rationale': 'Limited language coverage'
            })
        
        # High-performing business type expansion
        top_performers = portfolio_analysis.get('top_performers', [])
        for business_id in top_performers:
            business = next((b for b in businesses if b.business_id == business_id), None)
            if business and business.growth_rate > 0.1:
                opportunities.append({
                    'type': 'expansion',
                    'strategy': DiversificationStrategy.HORIZONTAL,
                    'rationale': f'Expand successful {business.business_type.value} model',
                    'base_business': business
                })
        
        return opportunities
    
    def _generate_diversification_recommendation(
        self, 
        opportunity: Dict[str, Any], 
        businesses: List[BusinessMetrics], 
        portfolio_analysis: Dict[str, Any]
    ) -> Optional[DiversificationRecommendation]:
        """Generate specific diversification recommendation."""
        try:
            strategy = opportunity['strategy']
            rationale = opportunity['rationale']
            
            # Determine target niche based on strategy
            target_niche = self._determine_target_niche(strategy, businesses, opportunity)
            
            # Calculate expected revenue
            expected_revenue = self._calculate_expected_revenue(strategy, target_niche, businesses)
            
            # Calculate risk level
            risk_level = self._calculate_risk_level(strategy, target_niche)
            
            # Calculate investment required
            investment_required = self._calculate_investment_required(strategy, target_niche)
            
            # Calculate time to market
            time_to_market = self._calculate_time_to_market(strategy, target_niche)
            
            # Calculate success probability
            success_probability = self._calculate_success_probability(strategy, target_niche, businesses)
            
            return DiversificationRecommendation(
                recommendation_id=generate_id("diversification"),
                strategy=strategy,
                target_niche=target_niche,
                expected_revenue=expected_revenue,
                risk_level=risk_level,
                investment_required=investment_required,
                time_to_market=time_to_market,
                rationale=rationale,
                success_probability=success_probability,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Failed to generate diversification recommendation: {e}")
            return None
    
    def _determine_target_niche(
        self, 
        strategy: DiversificationStrategy, 
        businesses: List[BusinessMetrics], 
        opportunity: Dict[str, Any]
    ) -> str:
        """Determine target niche for diversification."""
        if strategy == DiversificationStrategy.HORIZONTAL:
            # Same market, different products
            existing_types = [b.business_type.value for b in businesses]
            available_types = [bt.value for bt in BusinessType if bt.value not in existing_types]
            return available_types[0] if available_types else "digital_product"
        
        elif strategy == DiversificationStrategy.GEOGRAPHIC:
            # Same product, different regions
            existing_regions = [b.region for b in businesses]
            available_regions = ["EU", "CN", "JP", "BR", "IN", "AU"]
            for region in available_regions:
                if region not in existing_regions:
                    return f"global_{region.lower()}"
            return "global_expansion"
        
        elif strategy == DiversificationStrategy.VERTICAL:
            # Same product, different markets
            return "enterprise_market"
        
        else:
            return "emerging_technology"
    
    def _calculate_expected_revenue(
        self, 
        strategy: DiversificationStrategy, 
        target_niche: str, 
        businesses: List[BusinessMetrics]
    ) -> float:
        """Calculate expected revenue for diversification."""
        # Base revenue from similar businesses
        base_revenue = np.mean([b.revenue for b in businesses]) if businesses else 5000
        
        # Adjust based on strategy
        strategy_multipliers = {
            DiversificationStrategy.HORIZONTAL: 0.8,
            DiversificationStrategy.VERTICAL: 1.2,
            DiversificationStrategy.GEOGRAPHIC: 0.9,
            DiversificationStrategy.CONGLOMERATE: 0.6,
            DiversificationStrategy.TECHNOLOGICAL: 1.1
        }
        
        multiplier = strategy_multipliers.get(strategy, 1.0)
        return base_revenue * multiplier
    
    def _calculate_risk_level(self, strategy: DiversificationStrategy, target_niche: str) -> float:
        """Calculate risk level for diversification."""
        # Base risk levels by strategy
        base_risks = {
            DiversificationStrategy.HORIZONTAL: 0.4,
            DiversificationStrategy.VERTICAL: 0.6,
            DiversificationStrategy.GEOGRAPHIC: 0.5,
            DiversificationStrategy.CONGLOMERATE: 0.8,
            DiversificationStrategy.TECHNOLOGICAL: 0.7
        }
        
        base_risk = base_risks.get(strategy, 0.5)
        
        # Adjust for niche-specific risks
        if "enterprise" in target_niche:
            base_risk += 0.1
        elif "emerging" in target_niche:
            base_risk += 0.2
        
        return min(base_risk, 1.0)
    
    def _calculate_investment_required(self, strategy: DiversificationStrategy, target_niche: str) -> float:
        """Calculate investment required for diversification."""
        # Base investments by strategy
        base_investments = {
            DiversificationStrategy.HORIZONTAL: 10000,
            DiversificationStrategy.VERTICAL: 25000,
            DiversificationStrategy.GEOGRAPHIC: 15000,
            DiversificationStrategy.CONGLOMERATE: 50000,
            DiversificationStrategy.TECHNOLOGICAL: 30000
        }
        
        base_investment = base_investments.get(strategy, 20000)
        
        # Adjust for niche-specific requirements
        if "enterprise" in target_niche:
            base_investment *= 1.5
        elif "emerging" in target_niche:
            base_investment *= 1.3
        
        return base_investment
    
    def _calculate_time_to_market(self, strategy: DiversificationStrategy, target_niche: str) -> int:
        """Calculate time to market in months."""
        # Base time to market by strategy
        base_times = {
            DiversificationStrategy.HORIZONTAL: 3,
            DiversificationStrategy.VERTICAL: 6,
            DiversificationStrategy.GEOGRAPHIC: 4,
            DiversificationStrategy.CONGLOMERATE: 12,
            DiversificationStrategy.TECHNOLOGICAL: 8
        }
        
        base_time = base_times.get(strategy, 6)
        
        # Adjust for niche-specific requirements
        if "enterprise" in target_niche:
            base_time += 2
        elif "emerging" in target_niche:
            base_time += 3
        
        return base_time
    
    def _calculate_success_probability(
        self, 
        strategy: DiversificationStrategy, 
        target_niche: str, 
        businesses: List[BusinessMetrics]
    ) -> float:
        """Calculate success probability for diversification."""
        # Base success probabilities by strategy
        base_probabilities = {
            DiversificationStrategy.HORIZONTAL: 0.7,
            DiversificationStrategy.VERTICAL: 0.6,
            DiversificationStrategy.GEOGRAPHIC: 0.65,
            DiversificationStrategy.CONGLOMERATE: 0.4,
            DiversificationStrategy.TECHNOLOGICAL: 0.55
        }
        
        base_probability = base_probabilities.get(strategy, 0.6)
        
        # Adjust based on current portfolio performance
        if businesses:
            avg_growth = np.mean([b.growth_rate for b in businesses])
            avg_profit = np.mean([b.profit_margin for b in businesses])
            
            # Higher growth and profit margins increase success probability
            if avg_growth > 0.1:
                base_probability += 0.1
            if avg_profit > 0.2:
                base_probability += 0.1
        
        return min(base_probability, 0.95)

class IncomePredictionSimulator:
    """Main income prediction and auto-diversification simulator."""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client or redis.Redis.from_url(config.database.url.replace('sqlite', 'redis'))
        self.revenue_predictor = RevenuePredictor()
        self.diversification_analyzer = DiversificationAnalyzer()
        self.business_data = {}
        self.predictions = {}
        self.recommendations = {}
        
        logger.info("Income Prediction Simulator initialized")
    
    async def add_business_data(self, metrics: BusinessMetrics):
        """Add business metrics data for prediction."""
        try:
            self.business_data[metrics.business_id] = metrics
            
            # Store in Redis for persistence
            if self.redis_client:
                await self._store_business_data(metrics)
            
            # Retrain models if we have enough data
            await self._retrain_models_if_needed()
            
            logger.info(f"Added business data for {metrics.business_id}")
            
        except Exception as e:
            logger.error(f"Failed to add business data: {e}")
    
    async def _store_business_data(self, metrics: BusinessMetrics):
        """Store business data in Redis."""
        try:
            data = {
                'business_id': metrics.business_id,
                'business_type': metrics.business_type.value,
                'revenue': str(metrics.revenue),
                'customers': str(metrics.customers),
                'conversion_rate': str(metrics.conversion_rate),
                'churn_rate': str(metrics.churn_rate),
                'customer_acquisition_cost': str(metrics.customer_acquisition_cost),
                'lifetime_value': str(metrics.lifetime_value),
                'market_size': str(metrics.market_size),
                'competition_level': str(metrics.competition_level),
                'growth_rate': str(metrics.growth_rate),
                'profit_margin': str(metrics.profit_margin),
                'language': metrics.language,
                'region': metrics.region,
                'timestamp': metrics.timestamp.isoformat()
            }
            
            key = f"business_metrics:{metrics.business_id}"
            self.redis_client.hset(key, mapping=data)
            self.redis_client.expire(key, 86400 * 365)  # 1 year TTL
            
        except Exception as e:
            logger.error(f"Failed to store business data: {e}")
    
    async def _retrain_models_if_needed(self):
        """Retrain prediction models if we have enough new data."""
        try:
            # Group data by business type
            data_by_type = defaultdict(list)
            for metrics in self.business_data.values():
                data_by_type[metrics.business_type].append(metrics)
            
            # Retrain models for business types with sufficient data
            for business_type, data in data_by_type.items():
                if len(data) >= 10:  # Minimum 10 samples for training
                    self.revenue_predictor.train_model(business_type, data)
                    
        except Exception as e:
            logger.error(f"Failed to retrain models: {e}")
    
    async def predict_business_revenue(
        self, 
        business_id: str, 
        horizon_months: int = 12
    ) -> Optional[RevenuePrediction]:
        """Predict revenue for a specific business."""
        try:
            if business_id not in self.business_data:
                logger.warning(f"No data found for business: {business_id}")
                return None
            
            metrics = self.business_data[business_id]
            prediction = self.revenue_predictor.predict_revenue(metrics, horizon_months)
            
            # Store prediction
            self.predictions[business_id] = prediction
            
            logger.info(f"Predicted revenue for {business_id}: ${prediction.predicted_revenue:,.2f}")
            return prediction
            
        except Exception as e:
            logger.error(f"Failed to predict revenue for {business_id}: {e}")
            return None
    
    async def analyze_portfolio_diversification(self) -> PortfolioSummary:
        """Analyze current portfolio and generate diversification recommendations."""
        try:
            businesses = list(self.business_data.values())
            
            if not businesses:
                logger.warning("No business data available for portfolio analysis")
                return self._create_empty_portfolio_summary()
            
            # Generate diversification recommendations
            recommendations = self.diversification_analyzer.analyze_portfolio_diversification(businesses)
            
            # Create portfolio summary
            summary = self._create_portfolio_summary(businesses, recommendations)
            
            # Store recommendations
            self.recommendations = {r.recommendation_id: r for r in recommendations}
            
            logger.info(f"Generated portfolio analysis with {len(recommendations)} recommendations")
            return summary
            
        except Exception as e:
            logger.error(f"Failed to analyze portfolio diversification: {e}")
            return self._create_empty_portfolio_summary()
    
    def _create_portfolio_summary(
        self, 
        businesses: List[BusinessMetrics], 
        recommendations: List[DiversificationRecommendation]
    ) -> PortfolioSummary:
        """Create portfolio summary from business data and recommendations."""
        total_revenue = sum(b.revenue for b in businesses)
        total_businesses = len(businesses)
        average_growth_rate = np.mean([b.growth_rate for b in businesses])
        
        # Calculate diversification score
        business_types = [b.business_type.value for b in businesses]
        regions = [b.region for b in businesses]
        languages = [b.language for b in businesses]
        
        type_diversity = len(set(business_types)) / len(business_types) if business_types else 0
        regional_diversity = len(set(regions)) / len(regions) if regions else 0
        language_diversity = len(set(languages)) / len(languages) if languages else 0
        
        diversification_score = (type_diversity + regional_diversity + language_diversity) / 3
        
        # Calculate risk score
        avg_churn = np.mean([b.churn_rate for b in businesses])
        avg_competition = np.mean([b.competition_level for b in businesses])
        risk_score = (avg_churn + avg_competition) / 2
        
        # Identify top and underperformers
        sorted_businesses = sorted(businesses, key=lambda b: b.revenue, reverse=True)
        top_performers = [b.business_id for b in sorted_businesses[:3]]
        underperformers = [b.business_id for b in sorted_businesses[-3:]]
        
        return PortfolioSummary(
            total_revenue=total_revenue,
            total_businesses=total_businesses,
            average_growth_rate=average_growth_rate,
            diversification_score=diversification_score,
            risk_score=risk_score,
            top_performers=top_performers,
            underperformers=underperformers,
            recommendations=recommendations,
            timestamp=datetime.utcnow()
        )
    
    def _create_empty_portfolio_summary(self) -> PortfolioSummary:
        """Create empty portfolio summary when no data is available."""
        return PortfolioSummary(
            total_revenue=0.0,
            total_businesses=0,
            average_growth_rate=0.0,
            diversification_score=0.0,
            risk_score=0.0,
            top_performers=[],
            underperformers=[],
            recommendations=[],
            timestamp=datetime.utcnow()
        )
    
    async def get_simulation_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for the simulation system."""
        metrics = {
            "total_businesses": len(self.business_data),
            "total_predictions": len(self.predictions),
            "total_recommendations": len(self.recommendations),
            "model_performance": self.revenue_predictor.model_performance,
            "feature_importance": self.revenue_predictor.feature_importance
        }
        
        # Calculate prediction accuracy if we have historical data
        if len(self.predictions) > 0:
            avg_confidence = np.mean([p.model_accuracy for p in self.predictions.values()])
            metrics["average_prediction_confidence"] = avg_confidence
        
        return metrics

# Global instance
_income_simulator_instance = None

def get_income_prediction_simulator(redis_client: Optional[redis.Redis] = None) -> IncomePredictionSimulator:
    """Get global income prediction simulator instance."""
    global _income_simulator_instance
    if _income_simulator_instance is None:
        _income_simulator_instance = IncomePredictionSimulator(redis_client)
    return _income_simulator_instance 
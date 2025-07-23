# PHASE 3: ADVANCED INTELLIGENCE
# Dynamic Decision Trees, Cross-Venture Learning, and Predictive Analytics

import asyncio
import json
import time
import random
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import uuid
import sqlite3
import pickle
from dataclasses import dataclass
from enum import Enum
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('phase3_intelligence.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class VentureType(Enum):
    SAAS = "saas"
    ECOMMERCE = "ecommerce"
    MOBILE_APP = "mobile_app"
    CONSULTING = "consulting"
    MARKETPLACE = "marketplace"
    SUBSCRIPTION = "subscription"
    FREEMIUM = "freemium"
    B2B = "b2b"
    B2C = "b2c"

@dataclass
class VentureData:
    """Venture performance data"""
    venture_id: str
    venture_type: VentureType
    creation_date: datetime
    revenue: float
    customers: int
    success_score: float
    market_conditions: Dict[str, float]
    agent_performance: Dict[str, float]
    features: Dict[str, Any]

@dataclass
class PredictionResult:
    """Prediction result"""
    venture_id: str
    predicted_success: float
    predicted_revenue: float
    confidence: float
    risk_factors: List[str]
    recommendations: List[str]
    timestamp: datetime

class DynamicDecisionTree:
    """Dynamic decision tree for autonomous decision making"""
    
    def __init__(self, max_depth: int = 10, min_samples_split: int = 5):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.classifier = DecisionTreeClassifier(
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            random_state=42
        )
        self.regressor = DecisionTreeRegressor(
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_names = []
        self.accuracy_history = []
        self.last_training = None
        
        logger.info(f"DynamicDecisionTree initialized with max_depth={max_depth}")
    
    def extract_features(self, venture_data: VentureData) -> np.ndarray:
        """Extract features from venture data"""
        features = []
        
        # Basic venture features
        features.extend([
            venture_data.revenue,
            venture_data.customers,
            venture_data.success_score,
            (datetime.now() - venture_data.creation_date).days
        ])
        
        # Market conditions
        market_features = [
            venture_data.market_conditions.get("competition_level", 0.5),
            venture_data.market_conditions.get("market_size", 0.5),
            venture_data.market_conditions.get("growth_rate", 0.5),
            venture_data.market_conditions.get("barrier_to_entry", 0.5)
        ]
        features.extend(market_features)
        
        # Agent performance
        agent_features = [
            venture_data.agent_performance.get("niche_researcher", 0.7),
            venture_data.agent_performance.get("mvp_designer", 0.7),
            venture_data.agent_performance.get("marketing_strategist", 0.7),
            venture_data.agent_performance.get("analytics_agent", 0.7)
        ]
        features.extend(agent_features)
        
        # Venture type encoding
        venture_type_encoding = [0] * len(VentureType)
        venture_type_encoding[list(VentureType).index(venture_data.venture_type)] = 1
        features.extend(venture_type_encoding)
        
        return np.array(features)
    
    def prepare_training_data(self, ventures: List[VentureData]) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Prepare training data for decision trees"""
        if not ventures:
            return np.array([]), np.array([]), np.array([])
        
        # Extract features and labels
        X = []
        y_success = []  # Binary success (0/1)
        y_revenue = []  # Continuous revenue
        
        for venture in ventures:
            features = self.extract_features(venture)
            X.append(features)
            
            # Success label (1 if success_score > 0.7)
            y_success.append(1 if venture.success_score > 0.7 else 0)
            
            # Revenue label
            y_revenue.append(venture.revenue)
        
        X = np.array(X)
        y_success = np.array(y_success)
        y_revenue = np.array(y_revenue)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        return X_scaled, y_success, y_revenue
    
    def train(self, ventures: List[VentureData]) -> Dict[str, float]:
        """Train the decision trees"""
        try:
            X, y_success, y_revenue = self.prepare_training_data(ventures)
            
            if len(X) == 0:
                logger.warning("No training data available")
                return {"accuracy": 0.0, "mse": 0.0}
            
            # Split data
            X_train, X_test, y_success_train, y_success_test, y_revenue_train, y_revenue_test = train_test_split(
                X, y_success, y_revenue, test_size=0.2, random_state=42
            )
            
            # Train classifier (success prediction)
            self.classifier.fit(X_train, y_success_train)
            y_success_pred = self.classifier.predict(X_test)
            accuracy = accuracy_score(y_success_test, y_success_pred)
            
            # Train regressor (revenue prediction)
            self.regressor.fit(X_train, y_revenue_train)
            y_revenue_pred = self.regressor.predict(X_test)
            mse = np.mean((y_revenue_test - y_revenue_pred) ** 2)
            
            self.is_trained = True
            self.last_training = datetime.now()
            self.accuracy_history.append(accuracy)
            
            logger.info(f"Decision trees trained - Accuracy: {accuracy:.3f}, MSE: {mse:.2f}")
            
            return {"accuracy": accuracy, "mse": mse}
            
        except Exception as e:
            logger.error(f"Training failed: {e}")
            return {"accuracy": 0.0, "mse": 0.0}
    
    def predict(self, venture_data: VentureData) -> PredictionResult:
        """Make predictions for a venture"""
        try:
            if not self.is_trained:
                return PredictionResult(
                    venture_id=venture_data.venture_id,
                    predicted_success=0.5,
                    predicted_revenue=venture_data.revenue,
                    confidence=0.0,
                    risk_factors=["Model not trained"],
                    recommendations=["Train model with more data"],
                    timestamp=datetime.now()
                )
            
            # Extract features
            features = self.extract_features(venture_data)
            features_scaled = self.scaler.transform(features.reshape(1, -1))
            
            # Make predictions
            success_prob = self.classifier.predict_proba(features_scaled)[0][1]
            predicted_revenue = self.regressor.predict(features_scaled)[0]
            
            # Calculate confidence based on model performance
            confidence = np.mean(self.accuracy_history[-10:]) if self.accuracy_history else 0.5
            
            # Identify risk factors
            risk_factors = []
            if venture_data.success_score < 0.5:
                risk_factors.append("Low current success score")
            if venture_data.revenue < 1000:
                risk_factors.append("Low current revenue")
            if venture_data.customers < 10:
                risk_factors.append("Low customer base")
            
            # Generate recommendations
            recommendations = []
            if success_prob < 0.7:
                recommendations.append("Focus on improving market positioning")
            if predicted_revenue < venture_data.revenue * 1.2:
                recommendations.append("Optimize revenue generation strategies")
            if confidence < 0.8:
                recommendations.append("Gather more data for better predictions")
            
            return PredictionResult(
                venture_id=venture_data.venture_id,
                predicted_success=success_prob,
                predicted_revenue=predicted_revenue,
                confidence=confidence,
                risk_factors=risk_factors,
                recommendations=recommendations,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return PredictionResult(
                venture_id=venture_data.venture_id,
                predicted_success=0.5,
                predicted_revenue=venture_data.revenue,
                confidence=0.0,
                risk_factors=["Prediction error"],
                recommendations=["Check model status"],
                timestamp=datetime.now()
            )
    
    def optimize(self) -> Dict[str, Any]:
        """Optimize the decision trees"""
        try:
            if not self.is_trained:
                return {"optimized": False, "reason": "Model not trained"}
            
            # Prune trees to reduce overfitting
            self.classifier.max_depth = max(3, self.classifier.max_depth - 1)
            self.regressor.max_depth = max(3, self.regressor.max_depth - 1)
            
            # Update parameters
            self.classifier.min_samples_split = max(2, self.classifier.min_samples_split + 1)
            self.regressor.min_samples_split = max(2, self.regressor.min_samples_split + 1)
            
            logger.info("Decision trees optimized")
            
            return {"optimized": True, "new_max_depth": self.classifier.max_depth}
            
        except Exception as e:
            logger.error(f"Optimization failed: {e}")
            return {"optimized": False, "error": str(e)}

class CrossVentureLearning:
    """Cross-venture learning system for knowledge transfer"""
    
    def __init__(self):
        self.venture_database = {}
        self.knowledge_graph = {}
        self.learning_patterns = {}
        self.transfer_history = []
        
        logger.info("CrossVentureLearning initialized")
    
    def add_venture_data(self, venture_data: VentureData):
        """Add venture data to the learning system"""
        try:
            self.venture_database[venture_data.venture_id] = venture_data
            
            # Update knowledge graph
            venture_type = venture_data.venture_type.value
            if venture_type not in self.knowledge_graph:
                self.knowledge_graph[venture_type] = []
            
            self.knowledge_graph[venture_type].append({
                "venture_id": venture_data.venture_id,
                "success_score": venture_data.success_score,
                "revenue": venture_data.revenue,
                "features": venture_data.features
            })
            
            logger.info(f"Venture data added: {venture_data.venture_id}")
            
        except Exception as e:
            logger.error(f"Failed to add venture data: {e}")
    
    def find_similar_ventures(self, venture_data: VentureData, top_k: int = 5) -> List[Dict]:
        """Find similar ventures for knowledge transfer"""
        try:
            similar_ventures = []
            
            for venture_id, venture in self.venture_database.items():
                if venture_id == venture_data.venture_id:
                    continue
                
                # Calculate similarity score
                similarity = self._calculate_similarity(venture_data, venture)
                
                similar_ventures.append({
                    "venture_id": venture_id,
                    "venture_type": venture.venture_type.value,
                    "similarity": similarity,
                    "success_score": venture.success_score,
                    "revenue": venture.revenue,
                    "features": venture.features
                })
            
            # Sort by similarity and return top k
            similar_ventures.sort(key=lambda x: x["similarity"], reverse=True)
            return similar_ventures[:top_k]
            
        except Exception as e:
            logger.error(f"Failed to find similar ventures: {e}")
            return []
    
    def _calculate_similarity(self, venture1: VentureData, venture2: VentureData) -> float:
        """Calculate similarity between two ventures"""
        try:
            # Type similarity
            type_similarity = 1.0 if venture1.venture_type == venture2.venture_type else 0.3
            
            # Revenue similarity
            revenue_diff = abs(venture1.revenue - venture2.revenue)
            revenue_similarity = 1.0 / (1.0 + revenue_diff / 1000)
            
            # Success score similarity
            success_diff = abs(venture1.success_score - venture2.success_score)
            success_similarity = 1.0 - success_diff
            
            # Market conditions similarity
            market_similarity = 0.5  # Simplified for now
            
            # Weighted average
            similarity = (type_similarity * 0.3 + 
                         revenue_similarity * 0.3 + 
                         success_similarity * 0.3 + 
                         market_similarity * 0.1)
            
            return max(0.0, min(1.0, similarity))
            
        except Exception as e:
            logger.error(f"Similarity calculation failed: {e}")
            return 0.0
    
    def transfer_knowledge(self, source_venture_id: str, target_venture_id: str) -> Dict:
        """Transfer knowledge from one venture to another"""
        try:
            if source_venture_id not in self.venture_database or target_venture_id not in self.venture_database:
                return {"success": False, "error": "Venture not found"}
            
            source_venture = self.venture_database[source_venture_id]
            target_venture = self.venture_database[target_venture_id]
            
            # Extract transferable knowledge
            knowledge_transfer = {
                "source_venture": source_venture_id,
                "target_venture": target_venture_id,
                "timestamp": datetime.now().isoformat(),
                "transferred_features": {},
                "success_boost": 0.0,
                "revenue_boost": 0.0
            }
            
            # Transfer successful strategies
            if source_venture.success_score > target_venture.success_score:
                success_boost = (source_venture.success_score - target_venture.success_score) * 0.1
                knowledge_transfer["success_boost"] = success_boost
            
            # Transfer revenue strategies
            if source_venture.revenue > target_venture.revenue:
                revenue_boost = (source_venture.revenue - target_venture.revenue) * 0.05
                knowledge_transfer["revenue_boost"] = revenue_boost
            
            # Transfer market strategies
            for key in source_venture.market_conditions:
                if key in target_venture.market_conditions:
                    knowledge_transfer["transferred_features"][f"market_{key}"] = source_venture.market_conditions[key]
            
            # Record transfer
            self.transfer_history.append(knowledge_transfer)
            
            logger.info(f"Knowledge transferred: {source_venture_id} -> {target_venture_id}")
            
            return {"success": True, "transfer": knowledge_transfer}
            
        except Exception as e:
            logger.error(f"Knowledge transfer failed: {e}")
            return {"success": False, "error": str(e)}
    
    def get_learning_patterns(self) -> Dict:
        """Get learning patterns across ventures"""
        try:
            patterns = {}
            
            # Success patterns by venture type
            for venture_type, ventures in self.knowledge_graph.items():
                if ventures:
                    success_scores = [v["success_score"] for v in ventures]
                    revenues = [v["revenue"] for v in ventures]
                    
                    patterns[venture_type] = {
                        "count": len(ventures),
                        "avg_success": np.mean(success_scores),
                        "avg_revenue": np.mean(revenues),
                        "best_success": max(success_scores),
                        "best_revenue": max(revenues)
                    }
            
            # Overall patterns
            all_ventures = list(self.venture_database.values())
            if all_ventures:
                patterns["overall"] = {
                    "total_ventures": len(all_ventures),
                    "avg_success": np.mean([v.success_score for v in all_ventures]),
                    "avg_revenue": np.mean([v.revenue for v in all_ventures]),
                    "success_rate": sum(1 for v in all_ventures if v.success_score > 0.7) / len(all_ventures)
                }
            
            return patterns
            
        except Exception as e:
            logger.error(f"Failed to get learning patterns: {e}")
            return {}

class PredictiveAnalytics:
    """Predictive analytics for success and risk forecasting"""
    
    def __init__(self):
        self.forecast_models = {}
        self.risk_models = {}
        self.scaler = StandardScaler()
        self.is_trained = False
        
        logger.info("PredictiveAnalytics initialized")
    
    def train_forecast_models(self, ventures: List[VentureData]) -> Dict[str, float]:
        """Train forecasting models"""
        try:
            if len(ventures) < 10:
                return {"accuracy": 0.0, "reason": "Insufficient data"}
            
            # Prepare features
            X = []
            y_success = []
            y_revenue = []
            
            for venture in ventures:
                features = self._extract_forecast_features(venture)
                X.append(features)
                y_success.append(1 if venture.success_score > 0.7 else 0)
                y_revenue.append(venture.revenue)
            
            X = np.array(X)
            y_success = np.array(y_success)
            y_revenue = np.array(y_revenue)
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Split data
            X_train, X_test, y_success_train, y_success_test, y_revenue_train, y_revenue_test = train_test_split(
                X_scaled, y_success, y_revenue, test_size=0.2, random_state=42
            )
            
            # Train success prediction model
            self.forecast_models["success"] = RandomForestClassifier(n_estimators=100, random_state=42)
            self.forecast_models["success"].fit(X_train, y_success_train)
            
            # Train revenue prediction model
            self.forecast_models["revenue"] = RandomForestRegressor(n_estimators=100, random_state=42)
            self.forecast_models["revenue"].fit(X_train, y_revenue_train)
            
            # Evaluate models
            y_success_pred = self.forecast_models["success"].predict(X_test)
            y_revenue_pred = self.forecast_models["revenue"].predict(X_test)
            
            success_accuracy = accuracy_score(y_success_test, y_success_pred)
            revenue_mse = np.mean((y_revenue_test - y_revenue_pred) ** 2)
            
            self.is_trained = True
            
            logger.info(f"Forecast models trained - Success Accuracy: {success_accuracy:.3f}, Revenue MSE: {revenue_mse:.2f}")
            
            return {"accuracy": success_accuracy, "mse": revenue_mse}
            
        except Exception as e:
            logger.error(f"Forecast training failed: {e}")
            return {"accuracy": 0.0, "mse": 0.0}
    
    def _extract_forecast_features(self, venture: VentureData) -> np.ndarray:
        """Extract features for forecasting"""
        features = []
        
        # Basic features
        features.extend([
            venture.revenue,
            venture.customers,
            venture.success_score,
            (datetime.now() - venture.creation_date).days
        ])
        
        # Market features
        features.extend([
            venture.market_conditions.get("competition_level", 0.5),
            venture.market_conditions.get("market_size", 0.5),
            venture.market_conditions.get("growth_rate", 0.5)
        ])
        
        # Agent performance
        features.extend([
            venture.agent_performance.get("niche_researcher", 0.7),
            venture.agent_performance.get("mvp_designer", 0.7),
            venture.agent_performance.get("marketing_strategist", 0.7)
        ])
        
        return np.array(features)
    
    def forecast_success(self, venture_data: VentureData) -> Dict[str, Any]:
        """Forecast venture success"""
        try:
            if not self.is_trained:
                return {"predicted_success": 0.5, "confidence": 0.0, "risk_level": "unknown"}
            
            features = self._extract_forecast_features(venture_data)
            features_scaled = self.scaler.transform(features.reshape(1, -1))
            
            # Predict success probability
            success_prob = self.forecast_models["success"].predict_proba(features_scaled)[0][1]
            
            # Predict revenue
            predicted_revenue = self.forecast_models["revenue"].predict(features_scaled)[0]
            
            # Calculate confidence
            confidence = 0.8  # Simplified confidence calculation
            
            # Determine risk level
            if success_prob > 0.8:
                risk_level = "low"
            elif success_prob > 0.6:
                risk_level = "medium"
            else:
                risk_level = "high"
            
            return {
                "predicted_success": success_prob,
                "predicted_revenue": predicted_revenue,
                "confidence": confidence,
                "risk_level": risk_level,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Success forecasting failed: {e}")
            return {"predicted_success": 0.5, "confidence": 0.0, "risk_level": "unknown"}
    
    def get_global_forecast(self, ventures: List[VentureData]) -> Dict[str, Any]:
        """Get global forecast for all ventures"""
        try:
            if not ventures:
                return {"total_revenue": 0, "success_rate": 0, "growth_rate": 0}
            
            total_revenue = sum(v.revenue for v in ventures)
            success_rate = sum(1 for v in ventures if v.success_score > 0.7) / len(ventures)
            
            # Calculate growth rate (simplified)
            recent_ventures = [v for v in ventures if (datetime.now() - v.creation_date).days < 30]
            if recent_ventures:
                recent_revenue = sum(v.revenue for v in recent_ventures)
                growth_rate = (recent_revenue / len(recent_ventures)) / (total_revenue / len(ventures)) - 1
            else:
                growth_rate = 0.0
            
            return {
                "total_revenue": total_revenue,
                "success_rate": success_rate,
                "growth_rate": growth_rate,
                "venture_count": len(ventures),
                "monthly_projection": total_revenue * 30,  # 30-day projection
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Global forecast failed: {e}")
            return {"total_revenue": 0, "success_rate": 0, "growth_rate": 0}

# Initialize Phase 3 systems
dynamic_decision_tree = DynamicDecisionTree()
cross_venture_learning = CrossVentureLearning()
predictive_analytics = PredictiveAnalytics()

logger.info("Phase 3 Advanced Intelligence systems initialized successfully") 
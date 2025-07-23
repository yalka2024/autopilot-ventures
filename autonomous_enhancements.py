# PHASE 1: CORE AUTONOMOUS LEARNING SYSTEM
# Achieving 100% Autonomy Baseline

import asyncio
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import redis
import chromadb
from chromadb.config import Settings
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
import uuid
import pickle
import os
from dataclasses import dataclass
from enum import Enum

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('autopilot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AgentType(Enum):
    NICHE_RESEARCHER = "niche_researcher"
    MVP_DESIGNER = "mvp_designer"
    MARKETING_STRATEGIST = "marketing_strategist"
    CONTENT_CREATOR = "content_creator"
    ANALYTICS_AGENT = "analytics_agent"
    OPERATIONS_AGENT = "operations_agent"
    FUNDING_AGENT = "funding_agent"
    LEGAL_AGENT = "legal_agent"
    HR_AGENT = "hr_agent"
    SUPPORT_AGENT = "support_agent"
    MASTER_AGENT = "master_agent"

@dataclass
class Memory:
    """Vector memory entry for agent experiences"""
    id: str
    agent_type: AgentType
    action: str
    context: str
    outcome: str
    success_score: float
    timestamp: datetime
    importance_score: float
    embedding: Optional[List[float]] = None

@dataclass
class LearningOutcome:
    """Reinforcement learning outcome"""
    agent_id: str
    action: str
    state: str
    reward: float
    next_state: str
    success: bool
    confidence: float
    timestamp: datetime

class VectorMemoryManager:
    """Manages vector memory for agent experiences using ChromaDB"""
    
    def __init__(self, collection_name: str = "autopilot_ventures"):
        self.collection_name = collection_name
        self.client = chromadb.PersistentClient(path="./chroma_db")
        
        # Create or get collection
        try:
            self.collection = self.client.get_collection(collection_name)
        except:
            self.collection = self.client.create_collection(collection_name)
        
        # Initialize vectorizer for text embeddings
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.vectorizer_fitted = False
        
        logger.info(f"VectorMemoryManager initialized for collection: {collection_name}")
    
    def _get_text_embedding(self, text: str) -> List[float]:
        """Generate text embedding using TF-IDF"""
        try:
            if not self.vectorizer_fitted:
                # Fit on sample data first
                sample_texts = ["business creation", "market research", "revenue generation", "customer acquisition"]
                self.vectorizer.fit(sample_texts)
                self.vectorizer_fitted = True
            
            # Transform the input text
            embedding = self.vectorizer.transform([text]).toarray()[0]
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            # Return random embedding as fallback
            return np.random.rand(1000).tolist()
    
    async def add_memory(self, memory: Memory) -> bool:
        """Add a new memory to vector storage"""
        try:
            # Generate embedding for the memory
            text_for_embedding = f"{memory.action} {memory.context} {memory.outcome}"
            embedding = self._get_text_embedding(text_for_embedding)
            
            # Add to ChromaDB
            self.collection.add(
                embeddings=[embedding],
                documents=[f"{memory.action}: {memory.context}"],
                metadatas=[{
                    "agent_type": memory.agent_type.value,
                    "outcome": memory.outcome,
                    "success_score": memory.success_score,
                    "importance_score": memory.importance_score,
                    "timestamp": memory.timestamp.isoformat(),
                    "id": memory.id
                }],
                ids=[memory.id]
            )
            
            logger.info(f"Memory added: {memory.id} for agent {memory.agent_type.value}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding memory: {e}")
            return False
    
    async def search_similar_memories(self, query: str, agent_type: Optional[AgentType] = None, 
                                    limit: int = 10) -> List[Dict]:
        """Search for similar memories using vector similarity"""
        try:
            # Generate embedding for query
            query_embedding = self._get_text_embedding(query)
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where={"agent_type": agent_type.value} if agent_type else None
            )
            
            # Format results
            memories = []
            for i in range(len(results['ids'][0])):
                memory = {
                    "id": results['ids'][0][i],
                    "document": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i] if 'distances' in results else 0.0
                }
                memories.append(memory)
            
            logger.info(f"Found {len(memories)} similar memories for query: {query}")
            return memories
            
        except Exception as e:
            logger.error(f"Error searching memories: {e}")
            return []
    
    async def get_successful_patterns(self, agent_type: AgentType, min_success_score: float = 0.7) -> List[Dict]:
        """Get successful patterns for an agent type"""
        try:
            # Query for successful memories
            results = self.collection.query(
                query_texts=["successful business creation"],
                n_results=50,
                where={
                    "agent_type": agent_type.value,
                    "success_score": {"$gte": min_success_score}
                }
            )
            
            patterns = []
            for i in range(len(results['ids'][0])):
                pattern = {
                    "action": results['metadatas'][0][i].get('action', ''),
                    "context": results['documents'][0][i],
                    "success_score": results['metadatas'][0][i].get('success_score', 0.0),
                    "timestamp": results['metadatas'][0][i].get('timestamp', '')
                }
                patterns.append(pattern)
            
            logger.info(f"Found {len(patterns)} successful patterns for {agent_type.value}")
            return patterns
            
        except Exception as e:
            logger.error(f"Error getting successful patterns: {e}")
            return []

class SelfTuningAgent:
    """Self-tuning agent with reinforcement learning capabilities"""
    
    def __init__(self, agent_id: str, agent_type: AgentType, collection_name: str = "autopilot_ventures"):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.collection_name = collection_name
        
        # Q-learning parameters
        self.learning_rate = 0.1
        self.discount_factor = 0.95
        self.epsilon = 0.3  # Exploration rate
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.01
        
        # Q-table (stored in Redis)
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        self.q_table_key = f"q_table:{agent_id}"
        
        # Confidence tracking
        self.confidence_threshold = 0.7
        self.confidence_history = []
        
        # Performance metrics
        self.success_count = 0
        self.total_actions = 0
        self.recent_rewards = []
        
        logger.info(f"SelfTuningAgent initialized: {agent_id} ({agent_type.value})")
    
    def _get_q_value(self, state: str, action: str) -> float:
        """Get Q-value from Redis"""
        try:
            q_key = f"{self.q_table_key}:{state}:{action}"
            value = self.redis_client.get(q_key)
            return float(value) if value else 0.0
        except:
            return 0.0
    
    def _set_q_value(self, state: str, action: str, value: float):
        """Set Q-value in Redis"""
        try:
            q_key = f"{self.q_table_key}:{state}:{action}"
            self.redis_client.set(q_key, value)
        except Exception as e:
            logger.error(f"Error setting Q-value: {e}")
    
    def _get_available_actions(self, state: str) -> List[str]:
        """Get available actions for a state"""
        # Define action space based on agent type
        action_spaces = {
            AgentType.NICHE_RESEARCHER: ["research_market", "analyze_competition", "identify_opportunity", "validate_niche"],
            AgentType.MVP_DESIGNER: ["design_prototype", "create_wireframe", "define_features", "estimate_timeline"],
            AgentType.MARKETING_STRATEGIST: ["create_campaign", "target_audience", "set_budget", "measure_roi"],
            AgentType.CONTENT_CREATOR: ["write_copy", "create_visual", "optimize_seo", "schedule_content"],
            AgentType.ANALYTICS_AGENT: ["track_metrics", "analyze_data", "generate_report", "optimize_performance"],
            AgentType.OPERATIONS_AGENT: ["manage_processes", "optimize_workflow", "handle_issues", "scale_operations"],
            AgentType.FUNDING_AGENT: ["identify_investors", "prepare_pitch", "negotiate_terms", "close_deal"],
            AgentType.LEGAL_AGENT: ["review_contracts", "ensure_compliance", "protect_ip", "handle_disputes"],
            AgentType.HR_AGENT: ["recruit_talent", "manage_team", "develop_culture", "retain_employees"],
            AgentType.SUPPORT_AGENT: ["handle_inquiries", "resolve_issues", "provide_guidance", "escalate_problems"],
            AgentType.MASTER_AGENT: ["coordinate_agents", "make_decisions", "optimize_strategy", "manage_resources"]
        }
        
        return action_spaces.get(self.agent_type, ["default_action"])
    
    def choose_action(self, state: str) -> Tuple[str, float]:
        """Choose action using epsilon-greedy policy"""
        available_actions = self._get_available_actions(state)
        
        # Epsilon-greedy exploration
        if np.random.random() < self.epsilon:
            action = np.random.choice(available_actions)
            confidence = 0.5  # Low confidence for exploration
        else:
            # Choose best action based on Q-values
            q_values = [self._get_q_value(state, action) for action in available_actions]
            best_action_idx = np.argmax(q_values)
            action = available_actions[best_action_idx]
            confidence = min(0.9, max(0.1, q_values[best_action_idx] / 10))  # Normalize confidence
        
        self.confidence_history.append(confidence)
        return action, confidence
    
    def update_q_value(self, state: str, action: str, reward: float, next_state: str):
        """Update Q-value using Q-learning algorithm"""
        try:
            current_q = self._get_q_value(state, action)
            
            # Get max Q-value for next state
            next_actions = self._get_available_actions(next_state)
            next_q_values = [self._get_q_value(next_state, next_action) for next_action in next_actions]
            max_next_q = max(next_q_values) if next_q_values else 0
            
            # Q-learning update
            new_q = current_q + self.learning_rate * (reward + self.discount_factor * max_next_q - current_q)
            
            # Update Q-table
            self._set_q_value(state, action, new_q)
            
            # Update metrics
            self.total_actions += 1
            self.recent_rewards.append(reward)
            
            # Decay epsilon
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
            
            logger.debug(f"Q-value updated: {state} -> {action} = {new_q:.4f}")
            
        except Exception as e:
            logger.error(f"Error updating Q-value: {e}")
    
    def get_performance_metrics(self) -> Dict:
        """Get agent performance metrics"""
        avg_reward = np.mean(self.recent_rewards[-100:]) if self.recent_rewards else 0
        avg_confidence = np.mean(self.confidence_history[-100:]) if self.confidence_history else 0
        success_rate = self.success_count / max(1, self.total_actions)
        
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type.value,
            "total_actions": self.total_actions,
            "success_count": self.success_count,
            "success_rate": success_rate,
            "avg_reward": avg_reward,
            "avg_confidence": avg_confidence,
            "epsilon": self.epsilon,
            "recent_performance": self.recent_rewards[-10:] if self.recent_rewards else []
        }

class ReinforcementLearningEngine:
    """Central reinforcement learning engine for all agents"""
    
    def __init__(self, collection_name: str = "autopilot_ventures"):
        self.collection_name = collection_name
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        self.vector_memory = VectorMemoryManager(collection_name)
        
        # Learning outcomes storage
        self.outcomes_key = f"learning_outcomes:{collection_name}"
        
        # Pattern analysis
        self.pattern_clusters = {}
        self.trend_analysis = {}
        
        # Performance tracking
        self.global_metrics = {
            "total_episodes": 0,
            "total_rewards": 0,
            "success_rate": 0.0,
            "learning_rate": 0.0,
            "adaptation_score": 0.0
        }
        
        logger.info(f"ReinforcementLearningEngine initialized for: {collection_name}")
    
    async def register_learning_outcome(self, outcome: LearningOutcome) -> bool:
        """Register a learning outcome from an agent"""
        try:
            # Store in Redis
            outcome_data = {
                "agent_id": outcome.agent_id,
                "action": outcome.action,
                "state": outcome.state,
                "reward": outcome.reward,
                "next_state": outcome.next_state,
                "success": outcome.success,
                "confidence": outcome.confidence,
                "timestamp": outcome.timestamp.isoformat()
            }
            
            outcome_id = str(uuid.uuid4())
            self.redis_client.hset(self.outcomes_key, outcome_id, json.dumps(outcome_data))
            
            # Update global metrics
            self.global_metrics["total_episodes"] += 1
            self.global_metrics["total_rewards"] += outcome.reward
            
            if outcome.success:
                self.global_metrics["success_rate"] = (
                    (self.global_metrics["success_rate"] * (self.global_metrics["total_episodes"] - 1) + 1) / 
                    self.global_metrics["total_episodes"]
                )
            
            logger.info(f"Learning outcome registered: {outcome_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error registering learning outcome: {e}")
            return False
    
    async def analyze_patterns(self) -> Dict:
        """Analyze learning patterns across all agents"""
        try:
            # Get all learning outcomes
            outcomes_data = self.redis_client.hgetall(self.outcomes_key)
            outcomes = []
            
            for outcome_id, outcome_json in outcomes_data.items():
                outcome = json.loads(outcome_json)
                outcomes.append(outcome)
            
            if not outcomes:
                return {"patterns": [], "trends": {}}
            
            # Convert to DataFrame for analysis
            df = pd.DataFrame(outcomes)
            
            # Pattern clustering
            if len(df) > 10:
                # Cluster by reward values
                kmeans = KMeans(n_clusters=min(5, len(df)), random_state=42)
                df['reward_cluster'] = kmeans.fit_predict(df[['reward']].values)
                
                # Analyze patterns by cluster
                patterns = []
                for cluster_id in df['reward_cluster'].unique():
                    cluster_data = df[df['reward_cluster'] == cluster_id]
                    pattern = {
                        "cluster_id": int(cluster_id),
                        "avg_reward": cluster_data['reward'].mean(),
                        "success_rate": cluster_data['success'].mean(),
                        "common_actions": cluster_data['action'].value_counts().head(3).to_dict(),
                        "sample_size": len(cluster_data)
                    }
                    patterns.append(pattern)
            else:
                patterns = []
            
            # Trend analysis
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
            
            # Calculate moving averages
            if len(df) > 10:
                df['reward_ma'] = df['reward'].rolling(window=10).mean()
                df['success_ma'] = df['success'].rolling(window=10).mean()
                
                trends = {
                    "reward_trend": df['reward_ma'].iloc[-1] - df['reward_ma'].iloc[0],
                    "success_trend": df['success_ma'].iloc[-1] - df['success_ma'].iloc[0],
                    "recent_performance": df['reward'].tail(10).mean(),
                    "improvement_rate": (df['reward'].tail(10).mean() - df['reward'].head(10).mean()) / max(1, df['reward'].head(10).mean())
                }
            else:
                trends = {
                    "reward_trend": 0,
                    "success_trend": 0,
                    "recent_performance": df['reward'].mean() if len(df) > 0 else 0,
                    "improvement_rate": 0
                }
            
            # Update global metrics
            self.global_metrics["learning_rate"] = trends.get("improvement_rate", 0)
            self.global_metrics["adaptation_score"] = trends.get("success_trend", 0)
            
            return {
                "patterns": patterns,
                "trends": trends,
                "total_outcomes": len(outcomes)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing patterns: {e}")
            return {"patterns": [], "trends": {}}
    
    async def optimize_agent_strategies(self) -> Dict:
        """Optimize strategies based on learning outcomes"""
        try:
            # Get successful patterns
            successful_outcomes = []
            outcomes_data = self.redis_client.hgetall(self.outcomes_key)
            
            for outcome_id, outcome_json in outcomes_data.items():
                outcome = json.loads(outcome_json)
                if outcome.get('success', False) and outcome.get('reward', 0) > 5:
                    successful_outcomes.append(outcome)
            
            if not successful_outcomes:
                return {"optimizations": [], "recommendations": []}
            
            # Analyze successful patterns
            df = pd.DataFrame(successful_outcomes)
            
            # Find most successful actions
            action_success = df.groupby('action').agg({
                'reward': 'mean',
                'success': 'mean',
                'confidence': 'mean'
            }).sort_values('reward', ascending=False)
            
            # Generate optimizations
            optimizations = []
            for action, metrics in action_success.head(5).iterrows():
                optimization = {
                    "action": action,
                    "avg_reward": metrics['reward'],
                    "success_rate": metrics['success'],
                    "avg_confidence": metrics['confidence'],
                    "recommendation": f"Increase frequency of '{action}' action"
                }
                optimizations.append(optimization)
            
            # Generate recommendations
            recommendations = []
            if len(df) > 0:
                avg_confidence = df['confidence'].mean()
                if avg_confidence < 0.7:
                    recommendations.append("Increase confidence threshold for better decision quality")
                
                avg_reward = df['reward'].mean()
                if avg_reward < 5:
                    recommendations.append("Focus on high-reward actions and strategies")
                
                success_rate = df['success'].mean()
                if success_rate < 0.75:
                    recommendations.append("Improve success rate through better state understanding")
            
            return {
                "optimizations": optimizations,
                "recommendations": recommendations,
                "successful_patterns_count": len(successful_outcomes)
            }
            
        except Exception as e:
            logger.error(f"Error optimizing strategies: {e}")
            return {"optimizations": [], "recommendations": []}
    
    def get_global_metrics(self) -> Dict:
        """Get global learning metrics"""
        return self.global_metrics.copy()

# Singleton instance
_reinforcement_learning_engine = None

def get_reinforcement_learning_engine(collection_name: str = "autopilot_ventures") -> ReinforcementLearningEngine:
    """Get singleton instance of reinforcement learning engine"""
    global _reinforcement_learning_engine
    if _reinforcement_learning_engine is None:
        _reinforcement_learning_engine = ReinforcementLearningEngine(collection_name)
    return _reinforcement_learning_engine

class AutonomousConfig:
    """Configuration for autonomous system"""
    
    def __init__(self):
        self.vector_memory_enabled = True
        self.self_tuning_enabled = True
        self.reinforcement_learning_enabled = True
        self.server_port = 8000
        self.server_host = '0.0.0.0'
        self.autonomous_mode = True
        self.runtime_duration_days = 14
        self.success_rate_target = 0.85
        self.learning_improvement_target = 3.0
        self.uptime_target = 0.999
        self.intervention_reduction_target = 0.90
        self.startup_success_target = 0.75
        self.revenue_projection_target = 50000

# Initialize autonomous configuration
autonomous_config = AutonomousConfig()

# Initialize core systems
vector_memory = VectorMemoryManager()
reinforcement_engine = get_reinforcement_learning_engine()

# Create self-tuning agents
self_tuning_agents = {}
for agent_type in AgentType:
    agent_id = f"{agent_type.value}_agent"
    self_tuning_agents[agent_type] = SelfTuningAgent(agent_id, agent_type)

logger.info("Phase 1 Autonomous Learning System initialized successfully") 
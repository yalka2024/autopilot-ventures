# PHASE 1: SIMPLIFIED AUTONOMOUS LEARNING INTEGRATION
# Achieving 100% Autonomy Baseline - Compatible Version

import asyncio
import json
import time
import random
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import os
import uuid
from dataclasses import dataclass
from enum import Enum
import sqlite3
import pickle

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('autopilot_phase1.log'),
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
    """Simplified memory entry for agent experiences"""
    id: str
    agent_type: AgentType
    action: str
    context: str
    outcome: str
    success_score: float
    timestamp: datetime
    importance_score: float

@dataclass
class LearningOutcome:
    """Simplified learning outcome"""
    agent_id: str
    action: str
    state: str
    reward: float
    next_state: str
    success: bool
    confidence: float
    timestamp: datetime

class SimpleVectorMemory:
    """Simplified vector memory using SQLite and basic similarity"""
    
    def __init__(self, db_path: str = "phase1_memory.db"):
        self.db_path = db_path
        self.init_database()
        logger.info(f"SimpleVectorMemory initialized with database: {db_path}")
    
    def init_database(self):
        """Initialize SQLite database for memory storage"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create memories table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    agent_type TEXT,
                    action TEXT,
                    context TEXT,
                    outcome TEXT,
                    success_score REAL,
                    timestamp TEXT,
                    importance_score REAL,
                    embedding_hash TEXT
                )
            ''')
            
            # Create learning outcomes table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS learning_outcomes (
                    id TEXT PRIMARY KEY,
                    agent_id TEXT,
                    action TEXT,
                    state TEXT,
                    reward REAL,
                    next_state TEXT,
                    success INTEGER,
                    confidence REAL,
                    timestamp TEXT
                )
            ''')
            
            # Create performance metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id TEXT PRIMARY KEY,
                    agent_id TEXT,
                    metric_type TEXT,
                    value REAL,
                    timestamp TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
    
    def _simple_hash(self, text: str) -> str:
        """Create simple hash for text similarity"""
        return str(hash(text.lower().replace(" ", "")) % 1000000)
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    async def add_memory(self, memory: Memory) -> bool:
        """Add a new memory to storage"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create embedding hash
            text_for_hash = f"{memory.action} {memory.context} {memory.outcome}"
            embedding_hash = self._simple_hash(text_for_hash)
            
            cursor.execute('''
                INSERT INTO memories 
                (id, agent_type, action, context, outcome, success_score, timestamp, importance_score, embedding_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                memory.id,
                memory.agent_type.value,
                memory.action,
                memory.context,
                memory.outcome,
                memory.success_score,
                memory.timestamp.isoformat(),
                memory.importance_score,
                embedding_hash
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Memory added: {memory.id} for agent {memory.agent_type.value}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding memory: {e}")
            return False
    
    async def search_similar_memories(self, query: str, agent_type: Optional[AgentType] = None, 
                                    limit: int = 10) -> List[Dict]:
        """Search for similar memories using simple similarity"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all memories
            if agent_type:
                cursor.execute('''
                    SELECT * FROM memories WHERE agent_type = ? ORDER BY timestamp DESC
                ''', (agent_type.value,))
            else:
                cursor.execute('SELECT * FROM memories ORDER BY timestamp DESC')
            
            memories_data = cursor.fetchall()
            conn.close()
            
            # Calculate similarities
            similarities = []
            for memory_data in memories_data:
                memory_text = f"{memory_data[2]} {memory_data[3]} {memory_data[4]}"  # action + context + outcome
                similarity = self._calculate_similarity(query, memory_text)
                
                similarities.append({
                    "id": memory_data[0],
                    "agent_type": memory_data[1],
                    "action": memory_data[2],
                    "context": memory_data[3],
                    "outcome": memory_data[4],
                    "success_score": memory_data[5],
                    "timestamp": memory_data[6],
                    "importance_score": memory_data[7],
                    "similarity": similarity
                })
            
            # Sort by similarity and return top results
            similarities.sort(key=lambda x: x["similarity"], reverse=True)
            return similarities[:limit]
            
        except Exception as e:
            logger.error(f"Error searching memories: {e}")
            return []
    
    async def get_successful_patterns(self, agent_type: AgentType, min_success_score: float = 0.7) -> List[Dict]:
        """Get successful patterns for an agent type"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM memories 
                WHERE agent_type = ? AND success_score >= ?
                ORDER BY success_score DESC, timestamp DESC
            ''', (agent_type.value, min_success_score))
            
            patterns_data = cursor.fetchall()
            conn.close()
            
            patterns = []
            for pattern_data in patterns_data:
                pattern = {
                    "action": pattern_data[2],
                    "context": pattern_data[3],
                    "success_score": pattern_data[5],
                    "timestamp": pattern_data[6]
                }
                patterns.append(pattern)
            
            logger.info(f"Found {len(patterns)} successful patterns for {agent_type.value}")
            return patterns
            
        except Exception as e:
            logger.error(f"Error getting successful patterns: {e}")
            return []

class SimpleSelfTuningAgent:
    """Simplified self-tuning agent with basic learning capabilities"""
    
    def __init__(self, agent_id: str, agent_type: AgentType):
        self.agent_id = agent_id
        self.agent_type = agent_type
        
        # Learning parameters
        self.learning_rate = 0.1
        self.exploration_rate = 0.3
        self.exploration_decay = 0.995
        self.exploration_min = 0.01
        
        # Performance tracking
        self.success_count = 0
        self.total_actions = 0
        self.recent_rewards = []
        self.confidence_history = []
        
        # Simple Q-table (in-memory)
        self.q_table = {}
        
        logger.info(f"SimpleSelfTuningAgent initialized: {agent_id} ({agent_type.value})")
    
    def _get_state_action_key(self, state: str, action: str) -> str:
        """Get key for Q-table"""
        return f"{state}:{action}"
    
    def _get_q_value(self, state: str, action: str) -> float:
        """Get Q-value from memory"""
        key = self._get_state_action_key(state, action)
        return self.q_table.get(key, 0.0)
    
    def _set_q_value(self, state: str, action: str, value: float):
        """Set Q-value in memory"""
        key = self._get_state_action_key(state, action)
        self.q_table[key] = value
    
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
        if random.random() < self.exploration_rate:
            action = random.choice(available_actions)
            confidence = 0.5  # Low confidence for exploration
        else:
            # Choose best action based on Q-values
            q_values = [self._get_q_value(state, action) for action in available_actions]
            best_action_idx = q_values.index(max(q_values))
            action = available_actions[best_action_idx]
            confidence = min(0.9, max(0.1, q_values[best_action_idx] / 10))  # Normalize confidence
        
        self.confidence_history.append(confidence)
        return action, confidence
    
    def update_q_value(self, state: str, action: str, reward: float, next_state: str):
        """Update Q-value using simplified Q-learning"""
        try:
            current_q = self._get_q_value(state, action)
            
            # Get max Q-value for next state
            next_actions = self._get_available_actions(next_state)
            next_q_values = [self._get_q_value(next_state, next_action) for next_action in next_actions]
            max_next_q = max(next_q_values) if next_q_values else 0
            
            # Q-learning update
            discount_factor = 0.95
            new_q = current_q + self.learning_rate * (reward + discount_factor * max_next_q - current_q)
            
            # Update Q-table
            self._set_q_value(state, action, new_q)
            
            # Update metrics
            self.total_actions += 1
            self.recent_rewards.append(reward)
            
            # Decay exploration rate
            self.exploration_rate = max(self.exploration_min, self.exploration_rate * self.exploration_decay)
            
            logger.debug(f"Q-value updated: {state} -> {action} = {new_q:.4f}")
            
        except Exception as e:
            logger.error(f"Error updating Q-value: {e}")
    
    def get_performance_metrics(self) -> Dict:
        """Get agent performance metrics"""
        avg_reward = sum(self.recent_rewards[-100:]) / len(self.recent_rewards[-100:]) if self.recent_rewards else 0
        avg_confidence = sum(self.confidence_history[-100:]) / len(self.confidence_history[-100:]) if self.confidence_history else 0
        success_rate = self.success_count / max(1, self.total_actions)
        
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type.value,
            "total_actions": self.total_actions,
            "success_count": self.success_count,
            "success_rate": success_rate,
            "avg_reward": avg_reward,
            "avg_confidence": avg_confidence,
            "exploration_rate": self.exploration_rate,
            "recent_performance": self.recent_rewards[-10:] if self.recent_rewards else []
        }

class SimpleReinforcementLearningEngine:
    """Simplified reinforcement learning engine"""
    
    def __init__(self, memory_db: str = "phase1_memory.db"):
        self.memory_db = memory_db
        self.vector_memory = SimpleVectorMemory(memory_db)
        
        # Performance tracking
        self.global_metrics = {
            "total_episodes": 0,
            "total_rewards": 0,
            "success_rate": 0.0,
            "learning_rate": 0.0,
            "adaptation_score": 0.0
        }
        
        logger.info(f"SimpleReinforcementLearningEngine initialized")
    
    async def register_learning_outcome(self, outcome: LearningOutcome) -> bool:
        """Register a learning outcome from an agent"""
        try:
            conn = sqlite3.connect(self.memory_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO learning_outcomes 
                (id, agent_id, action, state, reward, next_state, success, confidence, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                str(uuid.uuid4()),
                outcome.agent_id,
                outcome.action,
                outcome.state,
                outcome.reward,
                outcome.next_state,
                1 if outcome.success else 0,
                outcome.confidence,
                outcome.timestamp.isoformat()
            ))
            
            # Update global metrics
            self.global_metrics["total_episodes"] += 1
            self.global_metrics["total_rewards"] += outcome.reward
            
            if outcome.success:
                self.global_metrics["success_rate"] = (
                    (self.global_metrics["success_rate"] * (self.global_metrics["total_episodes"] - 1) + 1) / 
                    self.global_metrics["total_episodes"]
                )
            
            conn.commit()
            conn.close()
            
            logger.info(f"Learning outcome registered for {outcome.agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error registering learning outcome: {e}")
            return False
    
    async def analyze_patterns(self) -> Dict:
        """Analyze learning patterns across all agents"""
        try:
            conn = sqlite3.connect(self.memory_db)
            cursor = conn.cursor()
            
            # Get all learning outcomes
            cursor.execute('SELECT * FROM learning_outcomes ORDER BY timestamp DESC')
            outcomes_data = cursor.fetchall()
            conn.close()
            
            if not outcomes_data:
                return {"patterns": [], "trends": {}}
            
            # Analyze patterns
            total_outcomes = len(outcomes_data)
            successful_outcomes = sum(1 for outcome in outcomes_data if outcome[6] == 1)  # success column
            avg_reward = sum(outcome[4] for outcome in outcomes_data) / total_outcomes  # reward column
            
            # Calculate trends (simple moving average)
            if total_outcomes > 10:
                recent_rewards = [outcome[4] for outcome in outcomes_data[:10]]
                older_rewards = [outcome[4] for outcome in outcomes_data[-10:]]
                
                recent_avg = sum(recent_rewards) / len(recent_rewards)
                older_avg = sum(older_rewards) / len(older_rewards)
                
                improvement_rate = (recent_avg - older_avg) / max(1, older_avg)
            else:
                improvement_rate = 0
            
            # Update global metrics
            self.global_metrics["learning_rate"] = improvement_rate
            self.global_metrics["adaptation_score"] = successful_outcomes / max(1, total_outcomes)
            
            return {
                "patterns": [
                    {
                        "total_outcomes": total_outcomes,
                        "successful_outcomes": successful_outcomes,
                        "avg_reward": avg_reward
                    }
                ],
                "trends": {
                    "improvement_rate": improvement_rate,
                    "success_rate": successful_outcomes / max(1, total_outcomes),
                    "recent_performance": avg_reward
                },
                "total_outcomes": total_outcomes
            }
            
        except Exception as e:
            logger.error(f"Error analyzing patterns: {e}")
            return {"patterns": [], "trends": {}}
    
    def get_global_metrics(self) -> Dict:
        """Get global learning metrics"""
        return self.global_metrics.copy()

# Initialize Phase 1 systems
vector_memory = SimpleVectorMemory()
reinforcement_engine = SimpleReinforcementLearningEngine()

# Create self-tuning agents
self_tuning_agents = {}
for agent_type in AgentType:
    agent_id = f"{agent_type.value}_agent"
    self_tuning_agents[agent_type] = SimpleSelfTuningAgent(agent_id, agent_type)

class Phase1AutonomousConfig:
    """Configuration for Phase 1 autonomous system"""
    
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

# Initialize configuration
phase1_config = Phase1AutonomousConfig()

logger.info("Phase 1 Simplified Autonomous Learning System initialized successfully")

# Integration functions for existing platform
async def integrate_with_existing_platform():
    """Integrate Phase 1 systems with existing platform"""
    try:
        logger.info("🔗 Integrating Phase 1 systems with existing platform...")
        
        # This function will be called from the existing app_autonomous.py
        # to integrate the Phase 1 learning capabilities
        
        return {
            "status": "integrated",
            "vector_memory": "active",
            "self_tuning_agents": len(self_tuning_agents),
            "reinforcement_engine": "active",
            "phase": "Phase 1 - Core Autonomous Learning"
        }
        
    except Exception as e:
        logger.error(f"Integration failed: {e}")
        return {"status": "failed", "error": str(e)}

async def run_phase1_autonomous_cycle():
    """Run a Phase 1 autonomous learning cycle"""
    try:
        logger.info("🔄 Running Phase 1 autonomous cycle...")
        
        # Simulate autonomous learning cycle
        for agent_type, agent in self_tuning_agents.items():
            # Generate state
            state = f"{agent_type.value}_state_{int(time.time())}"
            
            # Choose action
            action, confidence = agent.choose_action(state)
            
            # Simulate outcome
            success = random.random() > 0.3  # 70% success rate
            reward = random.uniform(1, 10) if success else random.uniform(-2, 1)
            
            # Update Q-value
            next_state = f"{agent_type.value}_next_state_{int(time.time())}"
            agent.update_q_value(state, action, reward, next_state)
            
            # Record learning outcome
            outcome = LearningOutcome(
                agent_id=agent.agent_id,
                action=action,
                state=state,
                reward=reward,
                next_state=next_state,
                success=success,
                confidence=confidence,
                timestamp=datetime.now()
            )
            await reinforcement_engine.register_learning_outcome(outcome)
            
            # Add memory
            memory = Memory(
                id=str(uuid.uuid4()),
                agent_type=agent_type,
                action=action,
                context=state,
                outcome=f"Success: {success}, Reward: {reward:.2f}",
                success_score=reward / 10,  # Normalize to 0-1
                timestamp=datetime.now(),
                importance_score=confidence
            )
            await vector_memory.add_memory(memory)
        
        # Analyze patterns
        patterns = await reinforcement_engine.analyze_patterns()
        
        logger.info(f"✅ Phase 1 cycle completed. Patterns: {len(patterns.get('patterns', []))}")
        
        return {
            "status": "completed",
            "agents_updated": len(self_tuning_agents),
            "patterns_analyzed": len(patterns.get('patterns', [])),
            "global_metrics": reinforcement_engine.get_global_metrics()
        }
        
    except Exception as e:
        logger.error(f"Phase 1 cycle failed: {e}")
        return {"status": "failed", "error": str(e)}

# Export for integration
__all__ = [
    'vector_memory',
    'reinforcement_engine', 
    'self_tuning_agents',
    'phase1_config',
    'integrate_with_existing_platform',
    'run_phase1_autonomous_cycle'
] 
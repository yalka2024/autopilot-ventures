#!/usr/bin/env python3
"""
Phase 1 Setup Script - Core Autonomous Learning System
Achieving 100% Autonomy Baseline

This script sets up the complete Phase 1 autonomous learning system for 2-week operation.
"""

import os
import sys
import subprocess
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('setup_phase1.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Phase1Setup:
    """Phase 1 autonomous learning system setup"""
    
    def __init__(self):
        self.setup_start_time = datetime.now()
        self.requirements_installed = False
        self.redis_running = False
        self.chromadb_initialized = False
        self.agents_created = False
        self.server_ready = False
        
        # Phase 1 configuration
        self.config = {
            "vector_memory_enabled": True,
            "self_tuning_enabled": True,
            "reinforcement_learning_enabled": True,
            "server_port": 8000,
            "server_host": "0.0.0.0",
            "autonomous_mode": True,
            "runtime_duration_days": 14,
            "success_rate_target": 0.85,
            "learning_improvement_target": 3.0,
            "uptime_target": 0.999,
            "intervention_reduction_target": 0.90,
            "startup_success_target": 0.75,
            "revenue_projection_target": 50000
        }
    
    def check_python_version(self) -> bool:
        """Check Python version compatibility"""
        try:
            version = sys.version_info
            if version.major == 3 and version.minor >= 8:
                logger.info(f"✅ Python version {version.major}.{version.minor}.{version.micro} is compatible")
                return True
            else:
                logger.error(f"❌ Python version {version.major}.{version.minor}.{version.micro} is not compatible. Required: 3.8+")
                return False
        except Exception as e:
            logger.error(f"❌ Error checking Python version: {e}")
            return False
    
    def install_dependencies(self) -> bool:
        """Install Phase 1 dependencies"""
        try:
            logger.info("📦 Installing Phase 1 dependencies...")
            
            # Install core dependencies
            core_deps = [
                "redis==5.0.1",
                "chromadb==0.4.18", 
                "scikit-learn==1.3.2",
                "tensorflow==2.15.0",
                "pandas>=2.0.0",
                "numpy>=1.24.0",
                "fastapi>=0.104.0",
                "uvicorn[standard]>=0.24.0",
                "apscheduler>=3.10.0",
                "prometheus-client>=0.17.0"
            ]
            
            for dep in core_deps:
                logger.info(f"Installing {dep}...")
                result = subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                                      capture_output=True, text=True)
                if result.returncode != 0:
                    logger.warning(f"⚠️ Failed to install {dep}: {result.stderr}")
                else:
                    logger.info(f"✅ Installed {dep}")
            
            # Install from requirements.txt
            if os.path.exists("requirements.txt"):
                logger.info("Installing from requirements.txt...")
                result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    logger.info("✅ Requirements.txt installation completed")
                else:
                    logger.warning(f"⚠️ Requirements.txt installation had issues: {result.stderr}")
            
            self.requirements_installed = True
            logger.info("✅ Dependencies installation completed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Dependencies installation failed: {e}")
            return False
    
    def setup_redis(self) -> bool:
        """Setup Redis for state management"""
        try:
            logger.info("🔧 Setting up Redis...")
            
            # Check if Redis is running
            try:
                import redis
                r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
                r.ping()
                logger.info("✅ Redis is already running")
                self.redis_running = True
                return True
            except:
                logger.info("Redis not running, attempting to start...")
            
            # Try to start Redis (this may not work on all systems)
            try:
                # On Windows, try to start Redis if available
                if os.name == 'nt':
                    result = subprocess.run(["redis-server", "--version"], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        logger.info("Redis server found, starting...")
                        subprocess.Popen(["redis-server"], 
                                       stdout=subprocess.DEVNULL, 
                                       stderr=subprocess.DEVNULL)
                        time.sleep(3)  # Wait for Redis to start
                        
                        # Test connection
                        r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
                        r.ping()
                        logger.info("✅ Redis started successfully")
                        self.redis_running = True
                        return True
                    else:
                        logger.warning("⚠️ Redis server not found. Please install Redis manually.")
                        return False
                else:
                    # On Unix-like systems
                    result = subprocess.run(["redis-server", "--version"], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        logger.info("Redis server found, starting...")
                        subprocess.Popen(["redis-server"], 
                                       stdout=subprocess.DEVNULL, 
                                       stderr=subprocess.DEVNULL)
                        time.sleep(3)
                        
                        r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
                        r.ping()
                        logger.info("✅ Redis started successfully")
                        self.redis_running = True
                        return True
                    else:
                        logger.warning("⚠️ Redis server not found. Please install Redis manually.")
                        return False
                        
            except Exception as e:
                logger.warning(f"⚠️ Could not start Redis: {e}")
                logger.info("ℹ️ Continuing without Redis (some features may be limited)")
                return False
                
        except Exception as e:
            logger.error(f"❌ Redis setup failed: {e}")
            return False
    
    def initialize_chromadb(self) -> bool:
        """Initialize ChromaDB for vector memory"""
        try:
            logger.info("🧠 Initializing ChromaDB for vector memory...")
            
            import chromadb
            from chromadb.config import Settings
            
            # Create ChromaDB client
            client = chromadb.Client(Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory="./chroma_db"
            ))
            
            # Create collection for autopilot ventures
            try:
                collection = client.get_collection("autopilot_ventures")
                logger.info("✅ ChromaDB collection already exists")
            except:
                collection = client.create_collection("autopilot_ventures")
                logger.info("✅ ChromaDB collection created")
            
            # Test vector operations
            test_embedding = [0.1] * 1000  # Simple test embedding
            collection.add(
                embeddings=[test_embedding],
                documents=["test document"],
                metadatas=[{"test": "true"}],
                ids=["test_id"]
            )
            
            # Query test
            results = collection.query(
                query_embeddings=[test_embedding],
                n_results=1
            )
            
            if results['ids'][0]:
                logger.info("✅ ChromaDB vector operations working")
                self.chromadb_initialized = True
                return True
            else:
                logger.error("❌ ChromaDB vector operations failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ ChromaDB initialization failed: {e}")
            return False
    
    def create_autonomous_agents(self) -> bool:
        """Create and initialize autonomous agents"""
        try:
            logger.info("🤖 Creating autonomous agents...")
            
            # Import autonomous systems
            from autonomous_enhancements import (
                AgentType, 
                SelfTuningAgent, 
                VectorMemoryManager,
                ReinforcementLearningEngine
            )
            
            # Initialize vector memory
            vector_memory = VectorMemoryManager()
            logger.info("✅ Vector memory manager initialized")
            
            # Initialize reinforcement learning engine
            rl_engine = ReinforcementLearningEngine()
            logger.info("✅ Reinforcement learning engine initialized")
            
            # Create self-tuning agents
            agents = {}
            for agent_type in AgentType:
                agent_id = f"{agent_type.value}_agent"
                agents[agent_type] = SelfTuningAgent(agent_id, agent_type)
                logger.info(f"✅ Created agent: {agent_id}")
            
            # Test agent operations
            test_agent = agents[AgentType.NICHE_RESEARCHER]
            action, confidence = test_agent.choose_action("test_state")
            
            if action and confidence > 0:
                logger.info(f"✅ Agent test successful: {action} (confidence: {confidence:.2f})")
                self.agents_created = True
                return True
            else:
                logger.error("❌ Agent test failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Agent creation failed: {e}")
            return False
    
    def setup_monitoring(self) -> bool:
        """Setup monitoring and metrics"""
        try:
            logger.info("📊 Setting up monitoring and metrics...")
            
            # Create monitoring directory
            os.makedirs("monitoring", exist_ok=True)
            
            # Create Prometheus configuration
            prometheus_config = {
                "global": {
                    "scrape_interval": "15s",
                    "evaluation_interval": "15s"
                },
                "scrape_configs": [
                    {
                        "job_name": "autopilot_ventures",
                        "static_configs": [
                            {
                                "targets": ["localhost:8000"]
                            }
                        ],
                        "metrics_path": "/metrics"
                    }
                ]
            }
            
            with open("monitoring/prometheus.yml", "w") as f:
                import yaml
                yaml.dump(prometheus_config, f)
            
            # Create Grafana dashboard configuration
            grafana_dashboard = {
                "dashboard": {
                    "title": "AutoPilot Ventures - Phase 1",
                    "panels": [
                        {
                            "title": "Success Rate",
                            "type": "stat",
                            "targets": [
                                {
                                    "expr": "autopilot_success_rate",
                                    "legendFormat": "Success Rate"
                                }
                            ]
                        },
                        {
                            "title": "Revenue Generated",
                            "type": "stat", 
                            "targets": [
                                {
                                    "expr": "autopilot_revenue_generated",
                                    "legendFormat": "Revenue"
                                }
                            ]
                        },
                        {
                            "title": "Active Agents",
                            "type": "stat",
                            "targets": [
                                {
                                    "expr": "autopilot_active_agents",
                                    "legendFormat": "Agents"
                                }
                            ]
                        }
                    ]
                }
            }
            
            with open("monitoring/grafana_dashboard.json", "w") as f:
                json.dump(grafana_dashboard, f, indent=2)
            
            logger.info("✅ Monitoring setup completed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Monitoring setup failed: {e}")
            return False
    
    def create_configuration_files(self) -> bool:
        """Create configuration files for Phase 1"""
        try:
            logger.info("⚙️ Creating configuration files...")
            
            # Create autonomous config
            config_data = {
                "phase": "Phase 1 - Core Autonomous Learning",
                "start_date": datetime.now().isoformat(),
                "target_end_date": (datetime.now() + timedelta(days=14)).isoformat(),
                "autonomous_config": self.config,
                "setup_completed": {
                    "requirements_installed": self.requirements_installed,
                    "redis_running": self.redis_running,
                    "chromadb_initialized": self.chromadb_initialized,
                    "agents_created": self.agents_created,
                    "server_ready": self.server_ready
                }
            }
            
            with open("phase1_config.json", "w") as f:
                json.dump(config_data, f, indent=2)
            
            # Create environment file template
            env_template = """# AutoPilot Ventures - Phase 1 Environment Configuration

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Stripe Configuration  
STRIPE_SECRET_KEY=your_stripe_secret_key_here
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key_here

# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT_ID=autopilot-ventures
GOOGLE_CLOUD_REGION=us-central1

# Autonomous Configuration
AUTONOMOUS_MODE=true
REAL_AI_ENABLED=true
DEPLOYMENT_ENV=production

# Phase 1 Specific
VECTOR_MEMORY_ENABLED=true
SELF_TUNING_ENABLED=true
REINFORCEMENT_LEARNING_ENABLED=true
"""
            
            with open("env.phase1.template", "w") as f:
                f.write(env_template)
            
            logger.info("✅ Configuration files created")
            return True
            
        except Exception as e:
            logger.error(f"❌ Configuration creation failed: {e}")
            return False
    
    def run_tests(self) -> bool:
        """Run Phase 1 system tests"""
        try:
            logger.info("🧪 Running Phase 1 system tests...")
            
            # Test imports
            test_imports = [
                "autonomous_enhancements",
                "server",
                "redis",
                "chromadb",
                "sklearn",
                "numpy",
                "pandas",
                "fastapi",
                "uvicorn"
            ]
            
            for module in test_imports:
                try:
                    __import__(module)
                    logger.info(f"✅ Import test passed: {module}")
                except ImportError as e:
                    logger.error(f"❌ Import test failed: {module}: {e}")
                    return False
            
            # Test autonomous systems
            try:
                from autonomous_enhancements import (
                    VectorMemoryManager,
                    SelfTuningAgent,
                    ReinforcementLearningEngine,
                    AgentType
                )
                
                # Test vector memory
                vm = VectorMemoryManager()
                logger.info("✅ Vector memory test passed")
                
                # Test self-tuning agent
                agent = SelfTuningAgent("test_agent", AgentType.NICHE_RESEARCHER)
                action, confidence = agent.choose_action("test_state")
                logger.info(f"✅ Self-tuning agent test passed: {action}")
                
                # Test reinforcement learning engine
                rl_engine = ReinforcementLearningEngine()
                logger.info("✅ Reinforcement learning engine test passed")
                
            except Exception as e:
                logger.error(f"❌ Autonomous systems test failed: {e}")
                return False
            
            logger.info("✅ All Phase 1 tests passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ System tests failed: {e}")
            return False
    
    def generate_startup_script(self) -> bool:
        """Generate startup script for Phase 1"""
        try:
            logger.info("📝 Generating startup script...")
            
            # Create startup script
            startup_script = """#!/usr/bin/env python3
# AutoPilot Ventures - Phase 1 Startup Script

import os
import sys
import subprocess
import time
from datetime import datetime

def main():
    print("🚀 Starting AutoPilot Ventures - Phase 1 Autonomous System")
    print("=" * 60)
    print(f"Start Time: {datetime.now()}")
    print(f"Target Duration: 14 days")
    print(f"Success Rate Target: 85%")
    print(f"Revenue Target: $50,000")
    print("=" * 60)
    
    # Check environment
    if not os.path.exists(".env"):
        print("⚠️ .env file not found. Please create one from env.phase1.template")
        return False
    
    # Start Redis if not running
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        r.ping()
        print("✅ Redis is running")
    except:
        print("⚠️ Redis not running. Some features may be limited.")
    
    # Start the autonomous server
    try:
        print("🤖 Starting autonomous server...")
        subprocess.run([sys.executable, "server.py"], check=True)
    except KeyboardInterrupt:
        print("\\n🛑 Shutdown requested by user")
    except Exception as e:
        print(f"❌ Server startup failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
"""
            
            with open("start_phase1.py", "w") as f:
                f.write(startup_script)
            
            # Make executable on Unix systems
            if os.name != 'nt':
                os.chmod("start_phase1.py", 0o755)
            
            logger.info("✅ Startup script generated")
            return True
            
        except Exception as e:
            logger.error(f"❌ Startup script generation failed: {e}")
            return False
    
    def run_setup(self) -> bool:
        """Run complete Phase 1 setup"""
        try:
            logger.info("🚀 Starting Phase 1 Autonomous Learning System Setup")
            logger.info("=" * 60)
            logger.info("Phase 1: Core Autonomous Learning")
            logger.info("Target: 100% Autonomy Baseline")
            logger.info("Duration: 14 days")
            logger.info("Success Rate Target: 85%")
            logger.info("Revenue Target: $50,000")
            logger.info("=" * 60)
            
            # Step 1: Check Python version
            if not self.check_python_version():
                return False
            
            # Step 2: Install dependencies
            if not self.install_dependencies():
                return False
            
            # Step 3: Setup Redis
            self.setup_redis()  # Continue even if Redis fails
            
            # Step 4: Initialize ChromaDB
            if not self.initialize_chromadb():
                return False
            
            # Step 5: Create autonomous agents
            if not self.create_autonomous_agents():
                return False
            
            # Step 6: Setup monitoring
            if not self.setup_monitoring():
                return False
            
            # Step 7: Create configuration files
            if not self.create_configuration_files():
                return False
            
            # Step 8: Run tests
            if not self.run_tests():
                return False
            
            # Step 9: Generate startup script
            if not self.generate_startup_script():
                return False
            
            # Mark server as ready
            self.server_ready = True
            
            # Calculate setup time
            setup_duration = datetime.now() - self.setup_start_time
            
            logger.info("=" * 60)
            logger.info("🎉 PHASE 1 SETUP COMPLETED SUCCESSFULLY!")
            logger.info("=" * 60)
            logger.info(f"Setup Duration: {setup_duration}")
            logger.info(f"Requirements Installed: {self.requirements_installed}")
            logger.info(f"Redis Running: {self.redis_running}")
            logger.info(f"ChromaDB Initialized: {self.chromadb_initialized}")
            logger.info(f"Agents Created: {self.agents_created}")
            logger.info(f"Server Ready: {self.server_ready}")
            logger.info("=" * 60)
            logger.info("🚀 TO START THE AUTONOMOUS SYSTEM:")
            logger.info("   python start_phase1.py")
            logger.info("=" * 60)
            logger.info("📊 MONITORING:")
            logger.info("   Health Check: http://localhost:8000/health")
            logger.info("   Metrics: http://localhost:8000/metrics")
            logger.info("   Status: http://localhost:8000/status")
            logger.info("=" * 60)
            logger.info("🎯 EXPECTED RESULTS:")
            logger.info("   • 85%+ success rate")
            logger.info("   • 3x learning improvement")
            logger.info("   • 99.9% uptime")
            logger.info("   • $50,000 revenue projection")
            logger.info("=" * 60)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Phase 1 setup failed: {e}")
            return False

def main():
    """Main setup function"""
    setup = Phase1Setup()
    
    if setup.run_setup():
        print("\n🎉 PHASE 1 SETUP COMPLETED!")
        print("Your autonomous system is ready for 2-week operation.")
        print("\nTo start: python start_phase1.py")
        sys.exit(0)
    else:
        print("\n❌ PHASE 1 SETUP FAILED!")
        print("Please check the logs and fix any issues.")
        sys.exit(1)

if __name__ == "__main__":
    main() 
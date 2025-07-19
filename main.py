"""Enhanced main application for AutoPilot Ventures platform."""

import asyncio
import argparse
import json
import logging
import sys
from typing import Dict, List, Optional, Any
from datetime import datetime

# Fix Unicode encoding issues on Windows
if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from config import config
from utils import budget_manager, generate_id, log, security_utils, alert_manager, secrets_manager
from database import db_manager
from orchestrator import get_orchestrator
from agents import (
    NicheResearchAgent,
    MVPDesignAgent,
    MarketingStrategyAgent,
    ContentCreationAgent,
    AnalyticsAgent,
    OperationsMonetizationAgent,
    FundingInvestorAgent,
    LegalComplianceAgent,
    HRTeamBuildingAgent,
    CustomerSupportScalingAgent,
)
from master_agent import get_master_agent, AutonomyLevel

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class AutoPilotVenturesApp:
    """Enhanced main application class."""

    def __init__(self):
        """Initialize the application."""
        self.startup_id = None
        self.orchestrator = None
        self.agents = {}
        self.master_agent = None
        self._initialize_agents()
        self._initialize_master_agent()

    def _initialize_agents(self) -> None:
        """Initialize all 10 AI agents."""
        try:
            # Create a temporary startup ID for agent initialization
            temp_startup_id = generate_id("startup")

            self.agents = {
                "niche_research": NicheResearchAgent(temp_startup_id),
                "mvp_design": MVPDesignAgent(temp_startup_id),
                "marketing_strategy": MarketingStrategyAgent(temp_startup_id),
                "content_creation": ContentCreationAgent(temp_startup_id),
                "analytics": AnalyticsAgent(temp_startup_id),
                "operations_monetization": OperationsMonetizationAgent(temp_startup_id),
                "funding_investor": FundingInvestorAgent(temp_startup_id),
                "legal_compliance": LegalComplianceAgent(temp_startup_id),
                "hr_team_building": HRTeamBuildingAgent(temp_startup_id),
                "customer_support_scaling": CustomerSupportScalingAgent(temp_startup_id),
            }
            logger.info(f"Initialized {len(self.agents)} AI agents")
        except Exception as e:
            logger.error(f"Failed to initialize agents: {e}")
            raise

    def _initialize_master_agent(self) -> None:
        """Initialize the master agent for autonomous operation."""
        try:
            # Initialize with semi-autonomous level by default
            autonomy_level = AutonomyLevel.SEMI_AUTONOMOUS
            self.master_agent = get_master_agent(autonomy_level)
            logger.info(f"Master Agent initialized with autonomy level: {autonomy_level.value}")
        except Exception as e:
            logger.error(f"Failed to initialize master agent: {e}")
            # Don't raise - master agent is optional for basic operation

    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check."""
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "2.0.0",
            "checks": {},
        }

        try:
            # Database health check
            try:
                stats = db_manager.get_database_stats()
                health_status["checks"]["database"] = {
                    "status": "healthy",
                    "startups_count": stats["startups"],
                    "agents_count": stats["agents"],
                    "tasks_count": stats["tasks"],
                }
            except Exception as e:
                health_status["checks"]["database"] = {"status": "unhealthy", "error": str(e)}
                health_status["status"] = "degraded"

            # Budget health check
            try:
                remaining_budget = budget_manager.get_remaining_budget()
                daily_spent = budget_manager.get_daily_spent()
                health_status["checks"]["budget"] = {
                    "status": "healthy",
                    "remaining_budget": remaining_budget,
                    "daily_spent": daily_spent,
                    "initial_budget": budget_manager.initial_budget,
                }
            except Exception as e:
                health_status["checks"]["budget"] = {"status": "unhealthy", "error": str(e)}
                health_status["status"] = "degraded"

            # Security health check
            try:
                # Test encryption/decryption
                test_data = "health_check_test"
                encrypted = security_utils.encrypt_data(test_data)
                decrypted = security_utils.decrypt_data(encrypted)

                if decrypted == test_data:
                    health_status["checks"]["security"] = {
                        "status": "healthy",
                        "encryption": "working",
                        "content_safety": "available",
                    }
                else:
                    health_status["checks"]["security"] = {
                        "status": "unhealthy",
                        "error": "Encryption/decryption mismatch",
                    }
                    health_status["status"] = "degraded"
            except Exception as e:
                health_status["checks"]["security"] = {"status": "unhealthy", "error": str(e)}
                health_status["status"] = "degraded"

            # Agent health check
            try:
                agent_status = {}
                for agent_type, agent in self.agents.items():
                    agent_status[agent_type] = {"status": "available", "agent_id": agent.agent_id}

                health_status["checks"]["agents"] = {
                    "status": "healthy",
                    "total_agents": len(self.agents),
                    "agent_details": agent_status,
                }
            except Exception as e:
                health_status["checks"]["agents"] = {"status": "unhealthy", "error": str(e)}
                health_status["status"] = "degraded"

            # Configuration health check
            try:
                health_status["checks"]["configuration"] = {
                    "status": "healthy",
                    "openai_key_configured": bool(config.ai.openai_key),
                    "model_name": config.ai.model_name,
                    "supported_languages": config.multilingual.supported_languages,
                    "monitoring_enabled": config.monitoring.metrics_enabled,
                }
            except Exception as e:
                health_status["checks"]["configuration"] = {"status": "unhealthy", "error": str(e)}
                health_status["status"] = "degraded"

            # Master Agent health check
            try:
                if self.master_agent:
                    master_status = self.master_agent.get_master_status()
                    health_status["checks"]["master_agent"] = {
                        "status": "healthy",
                        "autonomy_level": master_status.get("autonomy_level", "unknown"),
                        "active_ventures": master_status.get("active_ventures", 0),
                        "total_revenue": master_status.get("total_revenue", 0.0),
                        "scheduler_running": master_status.get("scheduler_running", False),
                    }
                else:
                    health_status["checks"]["master_agent"] = {
                        "status": "not_initialized",
                        "message": "Master Agent not available",
                    }
            except Exception as e:
                health_status["checks"]["master_agent"] = {"status": "unhealthy", "error": str(e)}
                health_status["status"] = "degraded"

        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["error"] = str(e)

        return health_status

    async def create_startup(self, name: str, description: str, niche: str, language: str = "en") -> Dict[str, Any]:
        """Create a new startup with enhanced features."""
        try:
            # Validate language
            if language not in config.multilingual.supported_languages:
                language = config.multilingual.default_language

            # Create startup
            startup = db_manager.create_startup(
                name=name,
                description=description,
                niche=niche,
                metadata={"language": language, "created_at": datetime.utcnow().isoformat(), "version": "2.0.0"},
            )

            self.startup_id = startup.id
            self.orchestrator = get_orchestrator(self.startup_id)

            # Log startup creation
            log.info("Startup created", startup_id=startup.id, name=name, niche=niche, language=language)

            return {
                "success": True,
                "startup_id": startup.id,
                "message": f'Startup "{name}" created successfully',
                "language": language,
                "budget_remaining": budget_manager.get_remaining_budget(),
            }

        except Exception as e:
            logger.error(f"Failed to create startup: {e}")
            return {"success": False, "error": str(e)}

    async def run_workflow(self, workflow_config: Dict[str, Any], language: str = "en") -> Dict[str, Any]:
        """Run complete workflow with all 10 agents."""
        if not self.orchestrator:
            return {"success": False, "error": "No startup initialized. Create a startup first."}

        try:
            # Add language context to workflow config
            workflow_config["language"] = language

            # Execute workflow
            result = await self.orchestrator.execute_workflow(workflow_config)

            return {
                "success": result.success,
                "workflow_id": result.workflow_id,
                "steps_completed": result.steps_completed,
                "steps_failed": result.steps_failed,
                "total_cost": result.total_cost,
                "execution_time": result.execution_time,
                "results": result.results,
                "budget_remaining": budget_manager.get_remaining_budget(),
            }

        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            return {"success": False, "error": str(e)}

    async def run_single_agent(self, agent_type: str, **kwargs) -> Dict[str, Any]:
        """Run a single agent."""
        if not self.orchestrator:
            return {"success": False, "error": "No startup initialized. Create a startup first."}

        try:
            result = await self.orchestrator.execute_single_agent(agent_type, **kwargs)
            return {
                "success": result["success"],
                "agent_type": agent_type,
                "data": result["data"],
                "cost": result["cost"],
                "message": result["message"],
                "budget_remaining": budget_manager.get_remaining_budget(),
            }

        except Exception as e:
            logger.error(f"Single agent execution failed: {e}")
            return {"success": False, "error": str(e)}

    def get_platform_status(self) -> Dict[str, Any]:
        """Get comprehensive platform status."""
        return {
            "platform_version": "2.0.0",
            "total_agents": len(self.agents),
            "agent_types": list(self.agents.keys()),
            "supported_languages": config.multilingual.supported_languages,
            "budget_status": {
                "remaining": budget_manager.get_remaining_budget(),
                "spent": budget_manager.initial_budget - budget_manager.get_remaining_budget(),
                "initial": budget_manager.initial_budget,
            },
            "monitoring": {
                "enabled": config.monitoring.metrics_enabled,
                "prometheus_port": config.monitoring.prometheus_port,
            },
            "security": {
                "secrets_manager": config.security.secrets_manager_type,
                "content_safety_threshold": config.security.content_safety_threshold,
            },
            "startup_id": self.startup_id,
            "orchestrator_available": self.orchestrator is not None,
            "master_agent_available": self.master_agent is not None,
        }

    async def multilingual_demo(self, language: str = "en") -> Dict[str, Any]:
        """Run multilingual demonstration with cultural context."""
        cultural_contexts = {
            "en": {
                "greeting": "Hello! Welcome to AutoPilot Ventures.",
                "context": "US/UK business culture",
                "communication_style": "Direct and professional",
            },
            "es": {
                "greeting": "¡Hola! Bienvenido a AutoPilot Ventures.",
                "context": "Latin American business culture",
                "communication_style": "Warm and relationship-focused",
            },
            "zh": {
                "greeting": "你好！欢迎来到AutoPilot Ventures。",
                "context": "Chinese business culture",
                "communication_style": "Respectful and hierarchical",
            },
            "fr": {
                "greeting": "Bonjour ! Bienvenue chez AutoPilot Ventures.",
                "context": "French business culture",
                "communication_style": "Formal and eloquent",
            },
            "de": {
                "greeting": "Hallo! Willkommen bei AutoPilot Ventures.",
                "context": "German business culture",
                "communication_style": "Precise and structured",
            },
            "ar": {
                "greeting": "مرحباً! أهلاً وسهلاً بك في AutoPilot Ventures.",
                "context": "Middle Eastern business culture",
                "communication_style": "Hospitality-focused and respectful",
            },
            "pt": {
                "greeting": "Olá! Bem-vindo ao AutoPilot Ventures.",
                "context": "Brazilian/Portuguese business culture",
                "communication_style": "Friendly and relationship-oriented",
            },
            "hi": {
                "greeting": "नमस्ते! AutoPilot Ventures में आपका स्वागत है।",
                "context": "Indian business culture",
                "communication_style": "Respectful and relationship-based",
            },
            "ru": {
                "greeting": "Привет! Добро пожаловать в AutoPilot Ventures.",
                "context": "Russian business culture",
                "communication_style": "Formal and direct",
            },
            "ja": {
                "greeting": "こんにちは！AutoPilot Venturesへようこそ。",
                "context": "Japanese business culture",
                "communication_style": "Polite and consensus-oriented",
            },
        }

        context = cultural_contexts.get(language, cultural_contexts["en"])

        # Create demo startup
        startup_result = await self.create_startup(
            name=f"Demo Startup ({language.upper()})",
            description=f"Multilingual demonstration startup for {language}",
            niche="Technology",
            language=language,
        )

        if not startup_result["success"]:
            return startup_result

        # Run demo workflow
        demo_config = {
            "niche_research": {
                "niche": "AI-powered business automation",
                "market_data": "Growing market with high demand",
            },
            "mvp_design": {
                "niche": "AI-powered business automation",
                "target_audience": "Small to medium businesses",
                "requirements": "User-friendly interface, automation features",
            },
            "marketing_strategy": {
                "product": "AI Business Automation Platform",
                "target_audience": "SMB owners and managers",
                "budget": 5000.0,
            },
        }

        workflow_result = await self.run_workflow(demo_config, language)

        return {
            "success": True,
            "language": language,
            "cultural_context": context,
            "startup_creation": startup_result,
            "workflow_execution": workflow_result,
            "message": f"Multilingual demo completed for {language}",
        }


async def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(description="AutoPilot Ventures Platform")
    parser.add_argument("--health-check", action="store_true", help="Run health check")
    parser.add_argument(
        "--create-startup", nargs=3, metavar=("NAME", "DESCRIPTION", "NICHE"), help="Create a new startup"
    )
    parser.add_argument("--run-workflow", type=str, help="Run workflow with config file")
    parser.add_argument("--run-agent", nargs=2, metavar=("AGENT_TYPE", "CONFIG_FILE"), help="Run single agent")
    parser.add_argument("--status", action="store_true", help="Show platform status")
    parser.add_argument("--multilingual-demo", type=str, help="Run multilingual demo (language code)")
    parser.add_argument("--language", type=str, default="en", help="Language for operations")
    parser.add_argument(
        "--autonomous-mode", type=str, choices=["manual", "semi", "full"], default="semi", help="Set autonomy level"
    )
    parser.add_argument("--start-autonomous", action="store_true", help="Start autonomous operation mode")
    parser.add_argument("--master-status", action="store_true", help="Show master agent status")
    parser.add_argument("--income-report", action="store_true", help="Generate income projection report")

    args = parser.parse_args()

    app = AutoPilotVenturesApp()

    # Set autonomy level if specified
    if args.autonomous_mode and app.master_agent:
        autonomy_map = {
            "manual": AutonomyLevel.MANUAL,
            "semi": AutonomyLevel.SEMI_AUTONOMOUS,
            "full": AutonomyLevel.FULLY_AUTONOMOUS,
        }
        app.master_agent.autonomy_level = autonomy_map[args.autonomous_mode]
        logger.info(f"Autonomy level set to: {args.autonomous_mode}")

    try:
        if args.health_check:
            print("🔍 Running health check...")
            health_status = await app.health_check()
            print(json.dumps(health_status, indent=2))

            if health_status["status"] == "healthy":
                print("✅ Health check passed!")
                sys.exit(0)
            else:
                print("❌ Health check failed!")
                sys.exit(1)

        elif args.create_startup:
            name, description, niche = args.create_startup
            print(f"🚀 Creating startup: {name}")
            result = await app.create_startup(name, description, niche, args.language)
            print(json.dumps(result, indent=2))

        elif args.run_workflow:
            print(f"🔄 Running workflow from {args.run_workflow}")
            with open(args.run_workflow, "r") as f:
                workflow_config = json.load(f)
            result = await app.run_workflow(workflow_config, args.language)
            print(json.dumps(result, indent=2))

        elif args.run_agent:
            agent_type, config_file = args.run_agent
            print(f"🤖 Running agent: {agent_type}")
            with open(config_file, "r") as f:
                agent_config = json.load(f)
            result = await app.run_single_agent(agent_type, **agent_config)
            print(json.dumps(result, indent=2))

        elif args.status:
            print("📊 Platform Status:")
            status = app.get_platform_status()
            print(json.dumps(status, indent=2))

        elif args.multilingual_demo:
            print(f"🌍 Running multilingual demo for {args.multilingual_demo}")
            result = await app.multilingual_demo(args.multilingual_demo)
            print(json.dumps(result, indent=2))

        elif args.start_autonomous:
            if not app.master_agent:
                print("❌ Master Agent not available. Cannot start autonomous mode.")
                sys.exit(1)
            print("🤖 Starting autonomous operation mode...")
            print("The platform will now run autonomously with scheduled cycles.")
            print("Press Ctrl+C to stop autonomous operation.")

            try:
                # Keep the application running for autonomous operation
                while True:
                    await asyncio.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                print("\n🛑 Stopping autonomous operation...")
                if app.master_agent:
                    app.master_agent.shutdown()
                print("✅ Autonomous operation stopped.")

        elif args.master_status:
            if not app.master_agent:
                print("❌ Master Agent not available.")
                sys.exit(1)
            print("🤖 Master Agent Status:")
            status = app.master_agent.get_master_status()
            print(json.dumps(status, indent=2))

        elif args.income_report:
            if not app.master_agent:
                print("❌ Master Agent not available.")
                sys.exit(1)
            print("💰 Income Projection Report:")
            income_summary = app.master_agent.get_income_summary()
            print(json.dumps(income_summary, indent=2))

        else:
            print("🎯 AutoPilot Ventures Platform v2.0.0")
            print("Available commands:")
            print("  --health-check          Run comprehensive health check")
            print("  --create-startup        Create a new startup")
            print("  --run-workflow          Run complete workflow")
            print("  --run-agent             Run single agent")
            print("  --status                Show platform status")
            print("  --multilingual-demo     Run multilingual demonstration")
            print("  --language              Set language for operations")
            print("  --autonomous-mode       Set autonomy level (manual/semi/full)")
            print("  --start-autonomous      Start autonomous operation mode")
            print("  --master-status         Show master agent status")
            print("  --income-report         Generate income projection report")
            print("\nExample:")
            print("  python main.py --health-check")
            print("  python main.py --create-startup 'My Startup' 'Description' 'Technology'")
            print("  python main.py --multilingual-demo es")
            print("  python main.py --start-autonomous --autonomous-mode full")
            print("  python main.py --master-status")
            print("  python main.py --income-report")

    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        # Cleanup
        if app.master_agent:
            app.master_agent.shutdown()
    except Exception as e:
        logger.error(f"Application error: {e}")
        print(f"❌ Error: {e}")
        # Cleanup on error
        if app.master_agent:
            app.master_agent.shutdown()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

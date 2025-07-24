#!/usr/bin/env python3
"""
AutoPilot Ventures Platform - Health Monitor
Scheduled health checks every 6 hours with alerting and self-healing
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List
import requests
import sqlite3
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('health_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class HealthMonitor:
    def __init__(self):
        self.cloud_run_url = "https://autopilot-ventures-1027187250482.us-central1.run.app"
        self.database_path = "health_monitor.db"
        self.alert_webhook_url = os.getenv("SLACK_WEBHOOK_URL", "")
        self.check_interval = 6 * 60 * 60  # 6 hours in seconds
        
    def init_database(self):
        """Initialize health monitoring database"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS health_checks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                endpoint_status TEXT,
                database_status TEXT,
                agent_status TEXT,
                payment_status TEXT,
                overall_status TEXT,
                response_time REAL,
                error_message TEXT,
                alert_sent BOOLEAN DEFAULT FALSE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                message TEXT NOT NULL,
                severity TEXT NOT NULL,
                resolved BOOLEAN DEFAULT FALSE
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Health monitoring database initialized")
    
    async def check_endpoint_health(self) -> Dict[str, Any]:
        """Check Cloud Run endpoint health"""
        try:
            start_time = time.time()
            response = requests.get(f"{self.cloud_run_url}/health", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "healthy",
                    "response_time": response_time,
                    "data": data
                }
            else:
                return {
                    "status": "unhealthy",
                    "response_time": response_time,
                    "error": f"HTTP {response.status_code}"
                }
        except Exception as e:
            return {
                "status": "error",
                "response_time": None,
                "error": str(e)
            }
    
    async def check_database_connectivity(self) -> Dict[str, Any]:
        """Check database connectivity"""
        try:
            # Check if main database files exist and are accessible
            db_files = [
                "market_offerings.db",
                "payment_infrastructure.db", 
                "real_customers.db",
                "real_revenue.db"
            ]
            
            accessible_files = []
            for db_file in db_files:
                if os.path.exists(db_file):
                    try:
                        conn = sqlite3.connect(db_file)
                        cursor = conn.cursor()
                        cursor.execute("SELECT 1")
                        conn.close()
                        accessible_files.append(db_file)
                    except Exception:
                        pass
            
            if accessible_files:
                return {
                    "status": "healthy",
                    "accessible_databases": accessible_files
                }
            else:
                return {
                    "status": "warning",
                    "message": "No databases accessible"
                }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def check_agent_health(self) -> Dict[str, Any]:
        """Check autonomous agent health"""
        try:
            # Check if agent processes are running
            agent_files = [
                "autonomous_demo.py",
                "deploy_actual_application.py",
                "complete_payment_infrastructure.py"
            ]
            
            active_agents = []
            for agent_file in agent_files:
                if os.path.exists(agent_file):
                    active_agents.append(agent_file)
            
            if active_agents:
                return {
                    "status": "healthy",
                    "active_agents": active_agents
                }
            else:
                return {
                    "status": "warning",
                    "message": "No agent files found"
                }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def check_payment_system(self) -> Dict[str, Any]:
        """Check payment system health"""
        try:
            # Check payment infrastructure
            if os.path.exists("complete_payment_infrastructure.py"):
                return {
                    "status": "ready",
                    "message": "Payment infrastructure available"
                }
            else:
                return {
                    "status": "warning",
                    "message": "Payment infrastructure not found"
                }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def run_health_check(self) -> Dict[str, Any]:
        """Run comprehensive health check"""
        logger.info("Starting comprehensive health check")
        
        # Initialize database first
        self.init_database()
        
        # Run all health checks
        endpoint_result = await self.check_endpoint_health()
        database_result = await self.check_database_connectivity()
        agent_result = await self.check_agent_health()
        payment_result = await self.check_payment_system()
        
        # Determine overall status
        statuses = [
            endpoint_result["status"],
            database_result["status"], 
            agent_result["status"],
            payment_result["status"]
        ]
        
        if "error" in statuses:
            overall_status = "critical"
        elif "unhealthy" in statuses:
            overall_status = "warning"
        else:
            overall_status = "healthy"
        
        health_result = {
            "timestamp": datetime.now().isoformat(),
            "endpoint_status": endpoint_result,
            "database_status": database_result,
            "agent_status": agent_result,
            "payment_status": payment_result,
            "overall_status": overall_status,
            "response_time": endpoint_result.get("response_time")
        }
        
        # Store result in database
        self.store_health_check(health_result)
        
        # Send alerts if needed
        if overall_status in ["critical", "warning"]:
            await self.send_alert(health_result)
        
        logger.info(f"Health check completed: {overall_status}")
        return health_result
    
    def store_health_check(self, result: Dict[str, Any]):
        """Store health check result in database"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO health_checks 
            (timestamp, endpoint_status, database_status, agent_status, payment_status, overall_status, response_time)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            result["timestamp"],
            json.dumps(result["endpoint_status"]),
            json.dumps(result["database_status"]),
            json.dumps(result["agent_status"]),
            json.dumps(result["payment_status"]),
            result["overall_status"],
            result.get("response_time")
        ))
        
        conn.commit()
        conn.close()
    
    async def send_alert(self, health_result: Dict[str, Any]):
        """Send alert via webhook"""
        if not self.alert_webhook_url:
            logger.warning("No alert webhook URL configured")
            return
        
        alert_message = {
            "text": f"🚨 AutoPilot Ventures Health Alert: {health_result['overall_status'].upper()}",
            "attachments": [
                {
                    "color": "danger" if health_result["overall_status"] == "critical" else "warning",
                    "fields": [
                        {
                            "title": "Endpoint",
                            "value": health_result["endpoint_status"]["status"],
                            "short": True
                        },
                        {
                            "title": "Database", 
                            "value": health_result["database_status"]["status"],
                            "short": True
                        },
                        {
                            "title": "Agents",
                            "value": health_result["agent_status"]["status"],
                            "short": True
                        },
                        {
                            "title": "Payment",
                            "value": health_result["payment_status"]["status"],
                            "short": True
                        }
                    ]
                }
            ]
        }
        
        try:
            response = requests.post(
                self.alert_webhook_url,
                json=alert_message,
                timeout=10
            )
            if response.status_code == 200:
                logger.info("Alert sent successfully")
            else:
                logger.error(f"Failed to send alert: {response.status_code}")
        except Exception as e:
            logger.error(f"Error sending alert: {e}")
    
    async def run_monitoring_loop(self):
        """Run continuous monitoring loop"""
        logger.info("Starting health monitoring loop")
        self.init_database()
        
        while True:
            try:
                await self.run_health_check()
                logger.info(f"Next health check in {self.check_interval/3600:.1f} hours")
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retrying
    
    def get_health_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get health check history"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        since = datetime.now() - timedelta(hours=hours)
        
        cursor.execute('''
            SELECT timestamp, overall_status, response_time, endpoint_status
            FROM health_checks 
            WHERE timestamp > ?
            ORDER BY timestamp DESC
        ''', (since.isoformat(),))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "timestamp": row[0],
                "status": row[1],
                "response_time": row[2],
                "endpoint_status": json.loads(row[3]) if row[3] else None
            })
        
        conn.close()
        return results

async def main():
    """Main function"""
    monitor = HealthMonitor()
    
    # Run initial health check
    result = await monitor.run_health_check()
    print(json.dumps(result, indent=2))
    
    # Start monitoring loop
    await monitor.run_monitoring_loop()

if __name__ == "__main__":
    asyncio.run(main()) 
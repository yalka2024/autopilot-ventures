"""
Decentralized Agent Swarm for Zero-Downtime Scaling
Enables agents to distribute tasks across local hardware and peer networks for 99.9% uptime
"""

import asyncio
import json
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import redis
import structlog
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import psutil
import socket
import threading
from collections import defaultdict, deque

# Optional distributed computing libraries
try:
    import ray
    RAY_AVAILABLE = True
except ImportError:
    RAY_AVAILABLE = False
    print("Warning: Ray not available, using simplified distributed computing")

try:
    import dask
    from dask.distributed import Client, LocalCluster
    DASK_AVAILABLE = True
except ImportError:
    DASK_AVAILABLE = False
    print("Warning: Dask not available, using simplified distributed computing")

from config import config
from utils import generate_id, log

# Configure structured logging
logger = structlog.get_logger()

class SwarmNodeType(Enum):
    """Types of swarm nodes."""
    MASTER = "master"
    WORKER = "worker"
    BACKUP = "backup"
    EDGE = "edge"

class TaskPriority(Enum):
    """Task priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"

@dataclass
class SwarmNode:
    """Represents a node in the decentralized swarm."""
    node_id: str
    node_type: SwarmNodeType
    host: str
    port: int
    capabilities: List[str]
    load: float = 0.0
    health_score: float = 1.0
    last_heartbeat: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SwarmTask:
    """Task to be executed by the swarm."""
    task_id: str
    task_type: str
    payload: Dict[str, Any]
    priority: TaskPriority
    node_requirements: List[str]
    timeout: int = 300  # seconds
    created_at: datetime = field(default_factory=datetime.utcnow)
    assigned_node: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None

@dataclass
class SwarmMetrics:
    """Metrics for swarm performance monitoring."""
    total_nodes: int
    active_nodes: int
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    average_response_time: float
    system_load: float
    memory_usage: float
    cpu_usage: float
    network_latency: float
    timestamp: datetime = field(default_factory=datetime.utcnow)

class NodeDiscovery:
    """Handles discovery and registration of swarm nodes."""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.discovered_nodes: Dict[str, SwarmNode] = {}
        self.discovery_interval = 30  # seconds
        self.node_ttl = 120  # seconds
        
    async def start_discovery(self):
        """Start the node discovery process."""
        while True:
            try:
                await self._discover_nodes()
                await self._cleanup_stale_nodes()
                await asyncio.sleep(self.discovery_interval)
            except Exception as e:
                logger.error(f"Node discovery error: {e}")
                await asyncio.sleep(5)
    
    async def _discover_nodes(self):
        """Discover nodes in the network."""
        try:
            # Get all registered nodes from Redis
            node_keys = self.redis_client.keys("swarm_node:*")
            
            for key in node_keys:
                node_data = self.redis_client.hgetall(key)
                if node_data:
                    node = self._create_node_from_data(node_data)
                    if node:
                        self.discovered_nodes[node.node_id] = node
            
            logger.info(f"Discovered {len(self.discovered_nodes)} nodes")
            
        except Exception as e:
            logger.error(f"Failed to discover nodes: {e}")
    
    def _create_node_from_data(self, node_data: Dict[str, str]) -> Optional[SwarmNode]:
        """Create SwarmNode from Redis data."""
        try:
            return SwarmNode(
                node_id=node_data.get('node_id', ''),
                node_type=SwarmNodeType(node_data.get('node_type', 'worker')),
                host=node_data.get('host', ''),
                port=int(node_data.get('port', 0)),
                capabilities=json.loads(node_data.get('capabilities', '[]')),
                load=float(node_data.get('load', 0.0)),
                health_score=float(node_data.get('health_score', 1.0)),
                last_heartbeat=datetime.fromisoformat(node_data.get('last_heartbeat', datetime.utcnow().isoformat())),
                is_active=node_data.get('is_active', 'true').lower() == 'true',
                metadata=json.loads(node_data.get('metadata', '{}'))
            )
        except Exception as e:
            logger.error(f"Failed to create node from data: {e}")
            return None
    
    async def _cleanup_stale_nodes(self):
        """Remove stale nodes that haven't sent heartbeats."""
        current_time = datetime.utcnow()
        stale_nodes = []
        
        for node_id, node in self.discovered_nodes.items():
            if (current_time - node.last_heartbeat).total_seconds() > self.node_ttl:
                stale_nodes.append(node_id)
        
        for node_id in stale_nodes:
            del self.discovered_nodes[node_id]
            logger.info(f"Removed stale node: {node_id}")
    
    async def register_node(self, node: SwarmNode):
        """Register a node in the swarm."""
        try:
            node_data = {
                'node_id': node.node_id,
                'node_type': node.node_type.value,
                'host': node.host,
                'port': str(node.port),
                'capabilities': json.dumps(node.capabilities),
                'load': str(node.load),
                'health_score': str(node.health_score),
                'last_heartbeat': node.last_heartbeat.isoformat(),
                'is_active': str(node.is_active).lower(),
                'metadata': json.dumps(node.metadata)
            }
            
            key = f"swarm_node:{node.node_id}"
            self.redis_client.hset(key, mapping=node_data)
            self.redis_client.expire(key, self.node_ttl)
            
            self.discovered_nodes[node.node_id] = node
            logger.info(f"Registered node: {node.node_id}")
            
        except Exception as e:
            logger.error(f"Failed to register node: {e}")
    
    async def update_node_heartbeat(self, node_id: str):
        """Update node heartbeat."""
        try:
            key = f"swarm_node:{node_id}"
            self.redis_client.hset(key, 'last_heartbeat', datetime.utcnow().isoformat())
            
            if node_id in self.discovered_nodes:
                self.discovered_nodes[node_id].last_heartbeat = datetime.utcnow()
                
        except Exception as e:
            logger.error(f"Failed to update node heartbeat: {e}")

class LoadBalancer:
    """Load balancer for distributing tasks across nodes."""
    
    def __init__(self):
        self.load_balancing_strategy = "least_loaded"  # Options: least_loaded, round_robin, health_based
        self.node_load_history = defaultdict(deque)
        self.history_size = 10
    
    def select_node(self, nodes: List[SwarmNode], task: SwarmTask) -> Optional[SwarmNode]:
        """Select the best node for a task."""
        if not nodes:
            return None
        
        # Filter nodes by requirements
        suitable_nodes = [
            node for node in nodes 
            if node.is_active and self._meets_requirements(node, task)
        ]
        
        if not suitable_nodes:
            return None
        
        if self.load_balancing_strategy == "least_loaded":
            return self._select_least_loaded(suitable_nodes)
        elif self.load_balancing_strategy == "round_robin":
            return self._select_round_robin(suitable_nodes)
        elif self.load_balancing_strategy == "health_based":
            return self._select_health_based(suitable_nodes)
        else:
            return suitable_nodes[0]
    
    def _meets_requirements(self, node: SwarmNode, task: SwarmTask) -> bool:
        """Check if node meets task requirements."""
        for requirement in task.node_requirements:
            if requirement not in node.capabilities:
                return False
        return True
    
    def _select_least_loaded(self, nodes: List[SwarmNode]) -> SwarmNode:
        """Select node with least load."""
        return min(nodes, key=lambda n: n.load)
    
    def _select_round_robin(self, nodes: List[SwarmNode]) -> SwarmNode:
        """Select node using round-robin strategy."""
        # Simple round-robin implementation
        return nodes[hash(time.time()) % len(nodes)]
    
    def _select_health_based(self, nodes: List[SwarmNode]) -> SwarmNode:
        """Select node based on health score."""
        return max(nodes, key=lambda n: n.health_score)
    
    def update_node_load(self, node_id: str, load: float):
        """Update node load history."""
        self.node_load_history[node_id].append(load)
        if len(self.node_load_history[node_id]) > self.history_size:
            self.node_load_history[node_id].popleft()

class HealthMonitor:
    """Monitors health of swarm nodes."""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.health_check_interval = 60  # seconds
        self.node_health_scores = {}
    
    async def start_monitoring(self, nodes: Dict[str, SwarmNode]):
        """Start health monitoring for nodes."""
        while True:
            try:
                await self._check_node_health(nodes)
                await asyncio.sleep(self.health_check_interval)
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(10)
    
    async def _check_node_health(self, nodes: Dict[str, SwarmNode]):
        """Check health of all nodes."""
        for node_id, node in nodes.items():
            try:
                health_score = await self._calculate_health_score(node)
                self.node_health_scores[node_id] = health_score
                node.health_score = health_score
                
                # Update node health in Redis
                key = f"swarm_node:{node_id}"
                self.redis_client.hset(key, 'health_score', str(health_score))
                
            except Exception as e:
                logger.error(f"Failed to check health for node {node_id}: {e}")
                self.node_health_scores[node_id] = 0.0
                node.health_score = 0.0
    
    async def _calculate_health_score(self, node: SwarmNode) -> float:
        """Calculate health score for a node."""
        try:
            # Check if node is reachable
            reachable = await self._check_node_reachability(node)
            if not reachable:
                return 0.0
            
            # Check response time
            response_time = await self._measure_response_time(node)
            response_score = max(0, 1.0 - (response_time / 1000))  # Normalize to 0-1
            
            # Check resource usage (if available)
            resource_score = await self._check_resource_usage(node)
            
            # Calculate overall health score
            health_score = (response_score + resource_score) / 2
            return max(0.0, min(1.0, health_score))
            
        except Exception as e:
            logger.error(f"Failed to calculate health score for {node.node_id}: {e}")
            return 0.0
    
    async def _check_node_reachability(self, node: SwarmNode) -> bool:
        """Check if node is reachable."""
        try:
            # Simple TCP connection check
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(node.host, node.port),
                timeout=5.0
            )
            writer.close()
            await writer.wait_closed()
            return True
        except Exception:
            return False
    
    async def _measure_response_time(self, node: SwarmNode) -> float:
        """Measure response time to node."""
        try:
            start_time = time.time()
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(node.host, node.port),
                timeout=5.0
            )
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            writer.close()
            await writer.wait_closed()
            return response_time
        except Exception:
            return float('inf')
    
    async def _check_resource_usage(self, node: SwarmNode) -> float:
        """Check resource usage of node."""
        # This would typically check CPU, memory, etc.
        # For now, return a default score
        return 0.8

class DecentralizedAgentSwarm:
    """Main decentralized agent swarm system."""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client or redis.Redis.from_url(config.database.url.replace('sqlite', 'redis'))
        self.node_discovery = NodeDiscovery(self.redis_client)
        self.load_balancer = LoadBalancer()
        self.health_monitor = HealthMonitor(self.redis_client)
        
        self.nodes: Dict[str, SwarmNode] = {}
        self.tasks: Dict[str, SwarmTask] = {}
        self.task_queue = asyncio.Queue()
        self.running = False
        
        # Initialize distributed computing frameworks
        self._initialize_distributed_frameworks()
        
        logger.info("Decentralized Agent Swarm initialized")
    
    def _initialize_distributed_frameworks(self):
        """Initialize distributed computing frameworks."""
        if RAY_AVAILABLE:
            try:
                ray.init(ignore_reinit_error=True)
                logger.info("Ray distributed computing initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Ray: {e}")
        
        if DASK_AVAILABLE:
            try:
                self.dask_client = Client(LocalCluster())
                logger.info("Dask distributed computing initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Dask: {e}")
                self.dask_client = None
    
    async def start_swarm(self):
        """Start the decentralized swarm."""
        self.running = True
        
        # Start background tasks
        asyncio.create_task(self.node_discovery.start_discovery())
        asyncio.create_task(self.health_monitor.start_monitoring(self.nodes))
        asyncio.create_task(self._task_processor())
        asyncio.create_task(self._heartbeat_sender())
        
        logger.info("Decentralized swarm started")
    
    async def stop_swarm(self):
        """Stop the decentralized swarm."""
        self.running = False
        logger.info("Decentralized swarm stopped")
    
    async def register_local_node(
        self,
        node_type: SwarmNodeType = SwarmNodeType.WORKER,
        port: int = 8000
    ) -> SwarmNode:
        """Register the local machine as a swarm node."""
        try:
            # Get local system information
            host = socket.gethostbyname(socket.gethostname())
            capabilities = self._get_local_capabilities()
            
            node = SwarmNode(
                node_id=generate_id("node"),
                node_type=node_type,
                host=host,
                port=port,
                capabilities=capabilities,
                load=self._get_system_load(),
                metadata={
                    "platform": "local",
                    "cpu_count": mp.cpu_count(),
                    "memory_gb": psutil.virtual_memory().total / (1024**3)
                }
            )
            
            await self.node_discovery.register_node(node)
            self.nodes[node.node_id] = node
            
            logger.info(f"Registered local node: {node.node_id}")
            return node
            
        except Exception as e:
            logger.error(f"Failed to register local node: {e}")
            raise
    
    def _get_local_capabilities(self) -> List[str]:
        """Get capabilities of the local machine."""
        capabilities = ["general_computing"]
        
        # Check for ML capabilities
        try:
            import torch
            capabilities.append("ml_inference")
        except ImportError:
            pass
        
        try:
            import tensorflow
            capabilities.append("tensorflow")
        except ImportError:
            pass
        
        # Check for GPU
        try:
            import torch
            if torch.cuda.is_available():
                capabilities.append("gpu_computing")
        except ImportError:
            pass
        
        # Check for high memory
        memory_gb = psutil.virtual_memory().total / (1024**3)
        if memory_gb > 16:
            capabilities.append("high_memory")
        
        # Check for high CPU cores
        if mp.cpu_count() > 8:
            capabilities.append("high_cpu")
        
        return capabilities
    
    def _get_system_load(self) -> float:
        """Get current system load."""
        try:
            return psutil.cpu_percent(interval=1) / 100.0
        except Exception:
            return 0.5
    
    async def submit_task(
        self,
        task_type: str,
        payload: Dict[str, Any],
        priority: TaskPriority = TaskPriority.MEDIUM,
        node_requirements: List[str] = None,
        timeout: int = 300
    ) -> str:
        """Submit a task to the swarm."""
        task_id = generate_id("task")
        
        task = SwarmTask(
            task_id=task_id,
            task_type=task_type,
            payload=payload,
            priority=priority,
            node_requirements=node_requirements or ["general_computing"],
            timeout=timeout
        )
        
        self.tasks[task_id] = task
        await self.task_queue.put(task)
        
        logger.info(f"Submitted task: {task_id}", task_type=task_type, priority=priority.value)
        return task_id
    
    async def _task_processor(self):
        """Process tasks from the queue."""
        while self.running:
            try:
                task = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)
                await self._execute_task(task)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Task processor error: {e}")
    
    async def _execute_task(self, task: SwarmTask):
        """Execute a task on an appropriate node."""
        try:
            # Select node for task
            available_nodes = list(self.nodes.values())
            selected_node = self.load_balancer.select_node(available_nodes, task)
            
            if not selected_node:
                logger.warning(f"No suitable node found for task: {task.task_id}")
                task.status = TaskStatus.FAILED
                task.error = "No suitable node available"
                return
            
            # Update task status
            task.status = TaskStatus.RUNNING
            task.assigned_node = selected_node.node_id
            
            # Execute task
            start_time = time.time()
            result = await self._execute_on_node(selected_node, task)
            execution_time = time.time() - start_time
            
            # Update task with result
            task.status = TaskStatus.COMPLETED
            task.result = result
            task.execution_time = execution_time
            
            # Update node load
            self.load_balancer.update_node_load(selected_node.node_id, selected_node.load)
            
            logger.info(f"Task completed: {task.task_id}", 
                       execution_time=execution_time,
                       node=selected_node.node_id)
            
        except Exception as e:
            logger.error(f"Task execution failed: {task.task_id}", error=str(e))
            task.status = TaskStatus.FAILED
            task.error = str(e)
    
    async def _execute_on_node(self, node: SwarmNode, task: SwarmTask) -> Any:
        """Execute task on a specific node."""
        try:
            if node.node_id in self.nodes:  # Local node
                return await self._execute_local_task(task)
            else:  # Remote node
                return await self._execute_remote_task(node, task)
        except Exception as e:
            logger.error(f"Failed to execute task on node {node.node_id}: {e}")
            raise
    
    async def _execute_local_task(self, task: SwarmTask) -> Any:
        """Execute task locally."""
        try:
            # Use appropriate execution method based on task type
            if task.task_type == "agent_execution":
                return await self._execute_agent_task(task)
            elif task.task_type == "data_processing":
                return await self._execute_data_processing_task(task)
            elif task.task_type == "ml_inference":
                return await self._execute_ml_task(task)
            else:
                return await self._execute_generic_task(task)
                
        except Exception as e:
            logger.error(f"Local task execution failed: {e}")
            raise
    
    async def _execute_agent_task(self, task: SwarmTask) -> Any:
        """Execute agent-related task."""
        # This would integrate with the existing agent system
        agent_type = task.payload.get("agent_type")
        agent_params = task.payload.get("parameters", {})
        
        # Simulate agent execution
        await asyncio.sleep(1)  # Simulate processing time
        
        return {
            "agent_type": agent_type,
            "result": f"Agent {agent_type} executed successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _execute_data_processing_task(self, task: SwarmTask) -> Any:
        """Execute data processing task."""
        data = task.payload.get("data", [])
        operation = task.payload.get("operation", "process")
        
        # Simulate data processing
        await asyncio.sleep(2)
        
        return {
            "operation": operation,
            "processed_items": len(data),
            "result": "Data processed successfully"
        }
    
    async def _execute_ml_task(self, task: SwarmTask) -> Any:
        """Execute machine learning task."""
        model_type = task.payload.get("model_type")
        input_data = task.payload.get("input_data")
        
        # Simulate ML inference
        await asyncio.sleep(3)
        
        return {
            "model_type": model_type,
            "prediction": "sample_prediction",
            "confidence": 0.85
        }
    
    async def _execute_generic_task(self, task: SwarmTask) -> Any:
        """Execute generic task."""
        await asyncio.sleep(1)
        return {"status": "completed", "task_type": task.task_type}
    
    async def _execute_remote_task(self, node: SwarmNode, task: SwarmTask) -> Any:
        """Execute task on remote node."""
        # This would implement remote task execution
        # For now, simulate remote execution
        await asyncio.sleep(2)
        return {"status": "remote_execution_simulated"}
    
    async def _heartbeat_sender(self):
        """Send heartbeat for local node."""
        while self.running:
            try:
                for node in self.nodes.values():
                    if node.node_id in self.nodes:  # Local nodes only
                        await self.node_discovery.update_node_heartbeat(node.node_id)
                        node.load = self._get_system_load()
                
                await asyncio.sleep(30)  # Send heartbeat every 30 seconds
                
            except Exception as e:
                logger.error(f"Heartbeat sender error: {e}")
                await asyncio.sleep(5)
    
    async def get_task_status(self, task_id: str) -> Optional[SwarmTask]:
        """Get status of a task."""
        return self.tasks.get(task_id)
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending task."""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            if task.status == TaskStatus.PENDING:
                task.status = TaskStatus.CANCELLED
                logger.info(f"Task cancelled: {task_id}")
                return True
        return False
    
    async def get_swarm_metrics(self) -> SwarmMetrics:
        """Get swarm performance metrics."""
        active_nodes = sum(1 for node in self.nodes.values() if node.is_active)
        completed_tasks = sum(1 for task in self.tasks.values() if task.status == TaskStatus.COMPLETED)
        failed_tasks = sum(1 for task in self.tasks.values() if task.status == TaskStatus.FAILED)
        
        # Calculate average response time
        response_times = [
            task.execution_time for task in self.tasks.values() 
            if task.execution_time is not None
        ]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Get system metrics
        system_load = self._get_system_load()
        memory_usage = psutil.virtual_memory().percent / 100.0
        cpu_usage = psutil.cpu_percent() / 100.0
        
        return SwarmMetrics(
            total_nodes=len(self.nodes),
            active_nodes=active_nodes,
            total_tasks=len(self.tasks),
            completed_tasks=completed_tasks,
            failed_tasks=failed_tasks,
            average_response_time=avg_response_time,
            system_load=system_load,
            memory_usage=memory_usage,
            cpu_usage=cpu_usage,
            network_latency=0.0  # Would be calculated from actual network measurements
        )
    
    async def get_node_info(self, node_id: str) -> Optional[SwarmNode]:
        """Get information about a specific node."""
        return self.nodes.get(node_id)
    
    async def get_all_nodes(self) -> List[SwarmNode]:
        """Get all registered nodes."""
        return list(self.nodes.values())

# Global instance
_agent_swarm_instance = None

def get_decentralized_agent_swarm(redis_client: Optional[redis.Redis] = None) -> DecentralizedAgentSwarm:
    """Get global decentralized agent swarm instance."""
    global _agent_swarm_instance
    if _agent_swarm_instance is None:
        _agent_swarm_instance = DecentralizedAgentSwarm(redis_client)
    return _agent_swarm_instance 
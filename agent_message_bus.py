"""Agent Message Bus for real-time agent communication and coordination."""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Callable, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import uuid

from config import config
from utils import generate_id, log

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Types of messages in the agent communication system."""
    
    DATA_SHARE = "data_share"
    DECISION_REQUEST = "decision_request"
    DECISION_RESPONSE = "decision_response"
    CONFLICT_ALERT = "conflict_alert"
    RESOURCE_REQUEST = "resource_request"
    RESOURCE_RESPONSE = "resource_response"
    STATUS_UPDATE = "status_update"
    ERROR_ALERT = "error_alert"
    SUCCESS_NOTIFICATION = "success_notification"


class MessagePriority(Enum):
    """Message priority levels."""
    
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class AgentMessage:
    """Message structure for agent communication."""
    
    id: str
    sender: str
    recipients: List[str]
    message_type: MessageType
    priority: MessagePriority
    content: Dict[str, Any]
    timestamp: datetime
    ttl: int = 300  # 5 minutes default TTL
    requires_response: bool = False
    response_to: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SharedContext:
    """Shared context data structure."""
    
    startup_id: str
    context_id: str
    data: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    access_count: int = 0
    ttl: int = 3600  # 1 hour default TTL


class ConflictResolver:
    """Handles conflicts between agent decisions."""
    
    def __init__(self):
        self.conflict_history = []
        self.resolution_strategies = {
            'budget_conflict': self._resolve_budget_conflict,
            'timeline_conflict': self._resolve_timeline_conflict,
            'resource_conflict': self._resolve_resource_conflict,
            'strategy_conflict': self._resolve_strategy_conflict,
        }
    
    def _resolve_budget_conflict(self, conflict_data: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve budget allocation conflicts."""
        total_budget = conflict_data.get('total_budget', 0)
        requests = conflict_data.get('requests', [])
        
        # Sort by priority and potential ROI
        sorted_requests = sorted(
            requests,
            key=lambda x: (x.get('priority', 1), x.get('estimated_roi', 0)),
            reverse=True
        )
        
        allocated = []
        remaining_budget = total_budget
        
        for request in sorted_requests:
            if remaining_budget >= request.get('amount', 0):
                allocated.append({
                    'agent': request['agent'],
                    'amount': request['amount'],
                    'reason': 'Budget available'
                })
                remaining_budget -= request['amount']
            else:
                allocated.append({
                    'agent': request['agent'],
                    'amount': remaining_budget,
                    'reason': 'Partial allocation'
                })
                break
        
        return {
            'resolution': 'budget_allocated',
            'allocations': allocated,
            'remaining_budget': remaining_budget
        }
    
    def _resolve_timeline_conflict(self, conflict_data: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve timeline conflicts between agents."""
        tasks = conflict_data.get('tasks', [])
        
        # Sort by dependencies and priority
        sorted_tasks = sorted(
            tasks,
            key=lambda x: (len(x.get('dependencies', [])), x.get('priority', 1)),
            reverse=True
        )
        
        timeline = []
        current_time = datetime.utcnow()
        
        for task in sorted_tasks:
            duration = task.get('estimated_duration', 1)
            timeline.append({
                'agent': task['agent'],
                'task': task['task'],
                'start_time': current_time.isoformat(),
                'end_time': (current_time + timedelta(days=duration)).isoformat(),
                'priority': task.get('priority', 1)
            })
            current_time += timedelta(days=duration)
        
        return {
            'resolution': 'timeline_created',
            'timeline': timeline
        }
    
    def _resolve_resource_conflict(self, conflict_data: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve resource allocation conflicts."""
        resources = conflict_data.get('resources', {})
        requests = conflict_data.get('requests', [])
        
        allocations = {}
        for resource_type, total_amount in resources.items():
            resource_requests = [
                req for req in requests 
                if req.get('resource_type') == resource_type
            ]
            
            # Allocate based on priority and need
            sorted_requests = sorted(
                resource_requests,
                key=lambda x: x.get('priority', 1),
                reverse=True
            )
            
            remaining = total_amount
            for request in sorted_requests:
                allocated = min(request.get('amount', 0), remaining)
                if allocated > 0:
                    allocations[f"{resource_type}_{request['agent']}"] = allocated
                    remaining -= allocated
        
        return {
            'resolution': 'resources_allocated',
            'allocations': allocations
        }
    
    def _resolve_strategy_conflict(self, conflict_data: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve strategic conflicts between agents."""
        strategies = conflict_data.get('strategies', [])
        
        # Score strategies based on multiple factors
        scored_strategies = []
        for strategy in strategies:
            score = (
                strategy.get('market_fit', 0) * 0.3 +
                strategy.get('roi_potential', 0) * 0.3 +
                strategy.get('feasibility', 0) * 0.2 +
                strategy.get('risk_level', 0) * 0.2
            )
            scored_strategies.append({
                'agent': strategy['agent'],
                'strategy': strategy['strategy'],
                'score': score
            })
        
        # Select best strategy
        best_strategy = max(scored_strategies, key=lambda x: x['score'])
        
        return {
            'resolution': 'strategy_selected',
            'selected_strategy': best_strategy,
            'all_strategies': scored_strategies
        }


class AgentMessageBus:
    """Real-time message bus for agent communication."""
    
    def __init__(self, startup_id: str):
        self.startup_id = startup_id
        self.bus_id = generate_id("message_bus")
        self.messages: Dict[str, AgentMessage] = {}
        self.subscribers: Dict[str, Set[str]] = defaultdict(set)
        self.shared_context: Dict[str, SharedContext] = {}
        self.conflict_resolver = ConflictResolver()
        self.message_queue = asyncio.Queue()
        self.processing_task = None
        self.is_running = False
        
        # Agent registry
        self.registered_agents: Set[str] = set()
        
        # Message handlers
        self.message_handlers: Dict[MessageType, List[Callable]] = defaultdict(list)
        
        logger.info(f"Message bus initialized for startup {startup_id}")
    
    async def start(self):
        """Start the message bus processing."""
        if self.is_running:
            return
        
        self.is_running = True
        self.processing_task = asyncio.create_task(self._process_messages())
        logger.info(f"Message bus started for startup {self.startup_id}")
    
    async def stop(self):
        """Stop the message bus processing."""
        self.is_running = False
        if self.processing_task:
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass
        logger.info(f"Message bus stopped for startup {self.startup_id}")
    
    def register_agent(self, agent_id: str, agent_type: str):
        """Register an agent with the message bus."""
        self.registered_agents.add(agent_id)
        self.subscribers[agent_type].add(agent_id)
        logger.info(f"Agent {agent_id} ({agent_type}) registered with message bus")
    
    def unregister_agent(self, agent_id: str, agent_type: str):
        """Unregister an agent from the message bus."""
        self.registered_agents.discard(agent_id)
        self.subscribers[agent_type].discard(agent_id)
        logger.info(f"Agent {agent_id} ({agent_type}) unregistered from message bus")
    
    async def send_message(
        self,
        sender: str,
        recipients: List[str],
        message_type: MessageType,
        content: Dict[str, Any],
        priority: MessagePriority = MessagePriority.NORMAL,
        requires_response: bool = False,
        response_to: Optional[str] = None
    ) -> str:
        """Send a message to specified recipients."""
        message_id = str(uuid.uuid4())
        message = AgentMessage(
            id=message_id,
            sender=sender,
            recipients=recipients,
            message_type=message_type,
            priority=priority,
            content=content,
            timestamp=datetime.utcnow(),
            requires_response=requires_response,
            response_to=response_to
        )
        
        self.messages[message_id] = message
        await self.message_queue.put(message)
        
        logger.info(f"Message {message_id} sent from {sender} to {recipients}")
        return message_id
    
    async def broadcast_message(
        self,
        sender: str,
        message_type: MessageType,
        content: Dict[str, Any],
        priority: MessagePriority = MessagePriority.NORMAL
    ) -> str:
        """Broadcast a message to all registered agents."""
        recipients = list(self.registered_agents)
        return await self.send_message(sender, recipients, message_type, content, priority)
    
    async def _process_messages(self):
        """Process messages in the queue."""
        while self.is_running:
            try:
                message = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)
                await self._handle_message(message)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing message: {e}")
    
    async def _handle_message(self, message: AgentMessage):
        """Handle a single message."""
        try:
            # Check TTL
            if (datetime.utcnow() - message.timestamp).total_seconds() > message.ttl:
                logger.warning(f"Message {message.id} expired, skipping")
                return
            
            # Handle based on message type
            if message.message_type == MessageType.CONFLICT_ALERT:
                await self._handle_conflict_alert(message)
            elif message.message_type == MessageType.DATA_SHARE:
                await self._handle_data_share(message)
            elif message.message_type == MessageType.RESOURCE_REQUEST:
                await self._handle_resource_request(message)
            else:
                # Generic message handling
                await self._notify_recipients(message)
                
        except Exception as e:
            logger.error(f"Error handling message {message.id}: {e}")
    
    async def _handle_conflict_alert(self, message: AgentMessage):
        """Handle conflict alerts and resolve them."""
        conflict_type = message.content.get('conflict_type')
        conflict_data = message.content.get('conflict_data', {})
        
        if conflict_type in self.conflict_resolver.resolution_strategies:
            resolution = self.conflict_resolver.resolution_strategies[conflict_type](conflict_data)
            
            # Send resolution to all involved agents
            resolution_message = await self.send_message(
                sender="conflict_resolver",
                recipients=message.recipients,
                message_type=MessageType.DECISION_RESPONSE,
                content={
                    'original_conflict': message.content,
                    'resolution': resolution
                },
                priority=MessagePriority.HIGH
            )
            
            logger.info(f"Conflict {conflict_type} resolved: {resolution_message}")
    
    async def _handle_data_share(self, message: AgentMessage):
        """Handle data sharing between agents."""
        data_key = message.content.get('data_key')
        data_value = message.content.get('data_value')
        
        if data_key and data_value:
            # Update shared context
            context_key = f"{self.startup_id}_{data_key}"
            if context_key in self.shared_context:
                self.shared_context[context_key].data.update(data_value)
                self.shared_context[context_key].updated_at = datetime.utcnow()
                self.shared_context[context_key].access_count += 1
            else:
                self.shared_context[context_key] = SharedContext(
                    startup_id=self.startup_id,
                    context_id=context_key,
                    data=data_value,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
            
            logger.info(f"Data shared: {data_key} = {data_value}")
    
    async def _handle_resource_request(self, message: AgentMessage):
        """Handle resource requests between agents."""
        resource_type = message.content.get('resource_type')
        amount = message.content.get('amount', 0)
        priority = message.content.get('priority', 1)
        
        # Simple resource allocation logic
        # In a real implementation, this would check actual resource availability
        allocation = min(amount, 100)  # Assume 100 units available
        
        response_content = {
            'request_id': message.content.get('request_id'),
            'resource_type': resource_type,
            'requested_amount': amount,
            'allocated_amount': allocation,
            'status': 'allocated' if allocation > 0 else 'denied'
        }
        
        await self.send_message(
            sender="resource_manager",
            recipients=[message.sender],
            message_type=MessageType.RESOURCE_RESPONSE,
            content=response_content,
            priority=MessagePriority.HIGH,
            response_to=message.id
        )
    
    async def _notify_recipients(self, message: AgentMessage):
        """Notify message recipients."""
        for recipient in message.recipients:
            if recipient in self.registered_agents:
                # In a real implementation, this would trigger callbacks
                # For now, we just log the notification
                logger.info(f"Message {message.id} delivered to {recipient}")
    
    def get_shared_context(self, context_key: str) -> Optional[SharedContext]:
        """Get shared context data."""
        full_key = f"{self.startup_id}_{context_key}"
        context = self.shared_context.get(full_key)
        
        if context:
            # Check TTL
            if (datetime.utcnow() - context.updated_at).total_seconds() > context.ttl:
                del self.shared_context[full_key]
                return None
            
            context.access_count += 1
            return context
        
        return None
    
    def set_shared_context(self, context_key: str, data: Dict[str, Any], ttl: int = 3600):
        """Set shared context data."""
        full_key = f"{self.startup_id}_{context_key}"
        now = datetime.utcnow()
        
        if full_key in self.shared_context:
            self.shared_context[full_key].data.update(data)
            self.shared_context[full_key].updated_at = now
        else:
            self.shared_context[full_key] = SharedContext(
                startup_id=self.startup_id,
                context_id=full_key,
                data=data,
                created_at=now,
                updated_at=now,
                ttl=ttl
            )
        
        logger.info(f"Shared context updated: {context_key}")
    
    def get_bus_status(self) -> Dict[str, Any]:
        """Get message bus status."""
        return {
            'bus_id': self.bus_id,
            'startup_id': self.startup_id,
            'is_running': self.is_running,
            'registered_agents': len(self.registered_agents),
            'pending_messages': self.message_queue.qsize(),
            'total_messages': len(self.messages),
            'shared_contexts': len(self.shared_context),
            'subscribers': {k: len(v) for k, v in self.subscribers.items()}
        }


# Global message bus instance
_message_bus: Optional[AgentMessageBus] = None


def get_message_bus(startup_id: str) -> AgentMessageBus:
    """Get or create message bus instance."""
    global _message_bus
    if _message_bus is None or _message_bus.startup_id != startup_id:
        if _message_bus:
            asyncio.create_task(_message_bus.stop())
        _message_bus = AgentMessageBus(startup_id)
        asyncio.create_task(_message_bus.start())
    return _message_bus 
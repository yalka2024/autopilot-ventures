#!/usr/bin/env python3
"""
PostgreSQL Database Implementation for AutoPilot Ventures Platform
Replaces SQLite for better scalability and production readiness
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from contextlib import contextmanager

import psycopg2
from psycopg2.extras import RealDictCursor, Json
from psycopg2.pool import SimpleConnectionPool
from sqlalchemy import (
    create_engine, Column, String, Integer, Float, DateTime, 
    Text, Boolean, ForeignKey, JSON, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.pool import QueuePool

from config import config
from utils import generate_id, TimeUtils

# Configure logging
logger = logging.getLogger(__name__)

# Create base class for models
Base = declarative_base()


class Startup(Base):
    """Startup model for storing startup information."""
    
    __tablename__ = 'startups'
    
    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    niche = Column(String(100))
    status = Column(String(20), default='active')
    budget_allocated = Column(Float, default=0.0)
    revenue = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata_json = Column(JSON)
    
    # Relationships
    agents = relationship("Agent", back_populates="startup", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="startup", cascade="all, delete-orphan")
    metrics = relationship("Metrics", back_populates="startup", cascade="all, delete-orphan")
    
    # Indexes for better performance
    __table_args__ = (
        Index('idx_startups_status', 'status'),
        Index('idx_startups_niche', 'niche'),
        Index('idx_startups_created_at', 'created_at'),
    )


class Agent(Base):
    """Agent model for storing agent information."""
    
    __tablename__ = 'agents'
    
    id = Column(String(50), primary_key=True)
    startup_id = Column(String(50), ForeignKey('startups.id'), nullable=False)
    agent_type = Column(String(50), nullable=False)
    status = Column(String(20), default='active')
    execution_count = Column(Integer, default=0)
    total_cost = Column(Float, default=0.0)
    success_rate = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata_json = Column(JSON)
    
    # Relationships
    startup = relationship("Startup", back_populates="agents")
    tasks = relationship("Task", back_populates="agent", cascade="all, delete-orphan")
    
    # Indexes for better performance
    __table_args__ = (
        Index('idx_agents_startup_id', 'startup_id'),
        Index('idx_agents_type', 'agent_type'),
        Index('idx_agents_status', 'status'),
    )


class Task(Base):
    """Task model for storing task information."""
    
    __tablename__ = 'tasks'
    
    id = Column(String(50), primary_key=True)
    startup_id = Column(String(50), ForeignKey('startups.id'), nullable=False)
    agent_id = Column(String(50), ForeignKey('agents.id'), nullable=False)
    task_type = Column(String(50), nullable=False)
    status = Column(String(20), default='pending')
    result = Column(Text)
    cost = Column(Float, default=0.0)
    duration = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    metadata_json = Column(JSON)
    
    # Relationships
    startup = relationship("Startup", back_populates="tasks")
    agent = relationship("Agent", back_populates="tasks")
    
    # Indexes for better performance
    __table_args__ = (
        Index('idx_tasks_startup_id', 'startup_id'),
        Index('idx_tasks_agent_id', 'agent_id'),
        Index('idx_tasks_status', 'status'),
        Index('idx_tasks_created_at', 'created_at'),
    )


class Metrics(Base):
    """Metrics model for storing performance metrics."""
    
    __tablename__ = 'metrics'
    
    id = Column(String(50), primary_key=True)
    startup_id = Column(String(50), ForeignKey('startups.id'), nullable=False)
    metric_type = Column(String(50), nullable=False)
    value = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    metadata_json = Column(JSON)
    
    # Relationships
    startup = relationship("Startup", back_populates="metrics")
    
    # Indexes for better performance
    __table_args__ = (
        Index('idx_metrics_startup_id', 'startup_id'),
        Index('idx_metrics_type', 'metric_type'),
        Index('idx_metrics_timestamp', 'timestamp'),
    )


class User(Base):
    """User model for authentication and authorization."""
    
    __tablename__ = 'users'
    
    id = Column(String(50), primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default='user')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    metadata_json = Column(JSON)
    
    # Indexes for better performance
    __table_args__ = (
        Index('idx_users_username', 'username'),
        Index('idx_users_email', 'email'),
        Index('idx_users_role', 'role'),
    )


class DatabaseManager:
    """Enhanced database manager with PostgreSQL support."""
    
    def __init__(self):
        """Initialize database manager."""
        self.engine = None
        self.SessionLocal = None
        self.connection_pool = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database connection and create tables."""
        try:
            # Get database configuration
            db_config = self._get_database_config()
            
            # Create SQLAlchemy engine with connection pooling
            self.engine = create_engine(
                db_config['url'],
                poolclass=QueuePool,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=config.debug.sql_echo
            )
            
            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            # Create connection pool for raw SQL operations
            self.connection_pool = SimpleConnectionPool(
                minconn=5,
                maxconn=20,
                **db_config['connection_params']
            )
            
            # Create tables
            Base.metadata.create_all(bind=self.engine)
            
            logger.info("PostgreSQL database initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL database: {e}")
            # Fallback to SQLite if PostgreSQL is not available
            self._fallback_to_sqlite()
    
    def _get_database_config(self):
        """Get database configuration from environment."""
        # Try PostgreSQL first
        if os.getenv('DATABASE_URL'):
            return {
                'url': os.getenv('DATABASE_URL'),
                'connection_params': self._parse_database_url(os.getenv('DATABASE_URL'))
            }
        
        # Default PostgreSQL configuration
        return {
            'url': 'postgresql://postgres:password@localhost:5432/autopilot_ventures',
            'connection_params': {
                'host': os.getenv('DB_HOST', 'localhost'),
                'port': int(os.getenv('DB_PORT', 5432)),
                'database': os.getenv('DB_NAME', 'autopilot_ventures'),
                'user': os.getenv('DB_USER', 'postgres'),
                'password': os.getenv('DB_PASSWORD', 'password')
            }
        }
    
    def _parse_database_url(self, url):
        """Parse database URL to connection parameters."""
        # Simple URL parsing for PostgreSQL
        if url.startswith('postgresql://'):
            parts = url.replace('postgresql://', '').split('@')
            if len(parts) == 2:
                auth, host_db = parts
                username, password = auth.split(':')
                host_port, database = host_db.split('/')
                host, port = host_port.split(':') if ':' in host_port else (host_port, '5432')
                
                return {
                    'host': host,
                    'port': int(port),
                    'database': database,
                    'user': username,
                    'password': password
                }
        
        return {}
    
    def _fallback_to_sqlite(self):
        """Fallback to SQLite if PostgreSQL is not available."""
        logger.warning("Falling back to SQLite database")
        
        sqlite_url = "sqlite:///autopilot_ventures.db"
        self.engine = create_engine(sqlite_url, echo=config.debug.sql_echo)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
    
    @contextmanager
    def get_session(self):
        """Get database session with automatic cleanup."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    @contextmanager
    def get_connection(self):
        """Get raw database connection from pool."""
        conn = self.connection_pool.getconn()
        try:
            yield conn
        finally:
            self.connection_pool.putconn(conn)
    
    def create_startup(self, name: str, description: str, niche: str, metadata: Dict = None) -> Dict:
        """Create a new startup."""
        try:
            with self.get_session() as session:
                startup = Startup(
                    id=generate_id("startup"),
                    name=name,
                    description=description,
                    niche=niche,
                    metadata_json=metadata or {}
                )
                session.add(startup)
                session.commit()
                
                logger.info(f"Created startup: {startup.id}")
                return {
                    'id': startup.id,
                    'name': startup.name,
                    'description': startup.description,
                    'niche': startup.niche,
                    'status': startup.status,
                    'created_at': startup.created_at.isoformat()
                }
                
        except Exception as e:
            logger.error(f"Failed to create startup: {e}")
            raise
    
    def create_agent(self, startup_id: str, agent_type: str, metadata: Dict = None) -> Dict:
        """Create a new agent."""
        try:
            with self.get_session() as session:
                agent = Agent(
                    id=generate_id("agent"),
                    startup_id=startup_id,
                    agent_type=agent_type,
                    metadata_json=metadata or {}
                )
                session.add(agent)
                session.commit()
                
                logger.info(f"Created agent: {agent.id}")
                return {
                    'id': agent.id,
                    'startup_id': agent.startup_id,
                    'agent_type': agent.agent_type,
                    'status': agent.status,
                    'created_at': agent.created_at.isoformat()
                }
                
        except Exception as e:
            logger.error(f"Failed to create agent: {e}")
            raise
    
    def create_task(self, startup_id: str, agent_id: str, task_type: str, metadata: Dict = None) -> Dict:
        """Create a new task."""
        try:
            with self.get_session() as session:
                task = Task(
                    id=generate_id("task"),
                    startup_id=startup_id,
                    agent_id=agent_id,
                    task_type=task_type,
                    metadata_json=metadata or {}
                )
                session.add(task)
                session.commit()
                
                logger.info(f"Created task: {task.id}")
                return {
                    'id': task.id,
                    'startup_id': task.startup_id,
                    'agent_id': task.agent_id,
                    'task_type': task.task_type,
                    'status': task.status,
                    'created_at': task.created_at.isoformat()
                }
                
        except Exception as e:
            logger.error(f"Failed to create task: {e}")
            raise
    
    def update_task(self, task_id: str, status: str, result: str = None, cost: float = 0.0, duration: float = 0.0) -> bool:
        """Update task status and results."""
        try:
            with self.get_session() as session:
                task = session.query(Task).filter(Task.id == task_id).first()
                if task:
                    task.status = status
                    if result:
                        task.result = result
                    if cost > 0:
                        task.cost = cost
                    if duration > 0:
                        task.duration = duration
                    if status in ['completed', 'failed']:
                        task.completed_at = datetime.utcnow()
                    
                    session.commit()
                    logger.info(f"Updated task: {task_id} - {status}")
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Failed to update task: {e}")
            return False
    
    def get_startup_metrics(self, startup_id: str, days: int = 30) -> Dict:
        """Get startup performance metrics."""
        try:
            with self.get_session() as session:
                # Get basic startup info
                startup = session.query(Startup).filter(Startup.id == startup_id).first()
                if not startup:
                    return {}
                
                # Get agent performance
                agents = session.query(Agent).filter(Agent.startup_id == startup_id).all()
                agent_metrics = []
                for agent in agents:
                    tasks = session.query(Task).filter(Task.agent_id == agent.id).all()
                    success_count = len([t for t in tasks if t.status == 'completed'])
                    total_cost = sum(t.cost for t in tasks)
                    
                    agent_metrics.append({
                        'agent_type': agent.agent_type,
                        'execution_count': len(tasks),
                        'success_rate': success_count / len(tasks) if tasks else 0,
                        'total_cost': total_cost,
                        'status': agent.status
                    })
                
                # Get recent tasks
                recent_tasks = session.query(Task).filter(
                    Task.startup_id == startup_id,
                    Task.created_at >= datetime.utcnow() - timedelta(days=days)
                ).order_by(Task.created_at.desc()).limit(10).all()
                
                return {
                    'startup': {
                        'id': startup.id,
                        'name': startup.name,
                        'status': startup.status,
                        'budget_allocated': startup.budget_allocated,
                        'revenue': startup.revenue,
                        'created_at': startup.created_at.isoformat()
                    },
                    'agents': agent_metrics,
                    'recent_tasks': [
                        {
                            'id': task.id,
                            'task_type': task.task_type,
                            'status': task.status,
                            'cost': task.cost,
                            'duration': task.duration,
                            'created_at': task.created_at.isoformat()
                        }
                        for task in recent_tasks
                    ]
                }
                
        except Exception as e:
            logger.error(f"Failed to get startup metrics: {e}")
            return {}
    
    def get_database_stats(self) -> Dict:
        """Get database statistics."""
        try:
            with self.get_session() as session:
                startup_count = session.query(Startup).count()
                agent_count = session.query(Agent).count()
                task_count = session.query(Task).count()
                user_count = session.query(User).count()
                
                # Get recent activity
                recent_tasks = session.query(Task).filter(
                    Task.created_at >= datetime.utcnow() - timedelta(hours=24)
                ).count()
                
                return {
                    'startups': startup_count,
                    'agents': agent_count,
                    'tasks': task_count,
                    'users': user_count,
                    'recent_tasks_24h': recent_tasks,
                    'database_type': 'PostgreSQL' if self.connection_pool else 'SQLite'
                }
                
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {}
    
    def cleanup_old_data(self, days: int = 90) -> int:
        """Clean up old data to maintain performance."""
        try:
            with self.get_session() as session:
                cutoff_date = datetime.utcnow() - timedelta(days=days)
                
                # Clean up old tasks
                old_tasks = session.query(Task).filter(Task.created_at < cutoff_date).delete()
                
                # Clean up old metrics
                old_metrics = session.query(Metrics).filter(Metrics.timestamp < cutoff_date).delete()
                
                session.commit()
                
                logger.info(f"Cleaned up {old_tasks} old tasks and {old_metrics} old metrics")
                return old_tasks + old_metrics
                
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
            return 0


# Global database manager instance
db_manager = DatabaseManager() 
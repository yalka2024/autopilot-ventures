"""Database models and management for AutoPilot Ventures platform."""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

from sqlalchemy import (
    create_engine, Column, String, Integer, Float, DateTime, 
    Text, Boolean, ForeignKey, JSON
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.exc import SQLAlchemyError

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
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'niche': self.niche,
            'status': self.status,
            'budget_allocated': self.budget_allocated,
            'revenue': self.revenue,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'metadata': self.metadata_json or {}
        }


class Agent(Base):
    """Agent model for storing AI agent information."""
    
    __tablename__ = 'agents'
    
    id = Column(String(50), primary_key=True)
    startup_id = Column(String(50), ForeignKey('startups.id'), nullable=False)
    agent_type = Column(String(50), nullable=False)
    status = Column(String(20), default='active')
    last_execution = Column(DateTime)
    execution_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata_json = Column(JSON)
    
    # Relationships
    startup = relationship("Startup", back_populates="agents")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'startup_id': self.startup_id,
            'agent_type': self.agent_type,
            'status': self.status,
            'last_execution': self.last_execution.isoformat() if self.last_execution else None,
            'execution_count': self.execution_count,
            'success_rate': self.success_rate,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'metadata': self.metadata_json or {}
        }


class Task(Base):
    """Task model for storing task information."""
    
    __tablename__ = 'tasks'
    
    id = Column(String(50), primary_key=True)
    startup_id = Column(String(50), ForeignKey('startups.id'), nullable=False)
    task_type = Column(String(50), nullable=False)
    status = Column(String(20), default='pending')
    priority = Column(Integer, default=1)
    description = Column(Text)
    result = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    metadata_json = Column(JSON)
    
    # Relationships
    startup = relationship("Startup", back_populates="tasks")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'startup_id': self.startup_id,
            'task_type': self.task_type,
            'status': self.status,
            'priority': self.priority,
            'description': self.description,
            'result': self.result,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'metadata': self.metadata_json or {}
        }


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
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'startup_id': self.startup_id,
            'metric_type': self.metric_type,
            'value': self.value,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'metadata': self.metadata_json or {}
        }


class DatabaseManager:
    """Database management class."""
    
    def __init__(self, database_url: Optional[str] = None):
        """Initialize database manager."""
        self.database_url = database_url or config.database.url
        self.engine = None
        self.SessionLocal = None
        self._initialize_database()
    
    def _initialize_database(self) -> None:
        """Initialize database connection and create tables."""
        try:
            # Create engine
            self.engine = create_engine(
                self.database_url,
                echo=False,
                pool_pre_ping=True
            )
            
            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            # Create tables
            Base.metadata.create_all(bind=self.engine)
            
            # Set proper permissions for SQLite file
            if 'sqlite' in self.database_url:
                db_path = self.database_url.replace('sqlite:///', '')
                if os.path.exists(db_path):
                    try:
                        os.chmod(db_path, 0o666)
                    except Exception as e:
                        logger.warning(f"Could not set database permissions: {e}")
            
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    def get_session(self) -> Session:
        """Get database session."""
        return self.SessionLocal()
    
    def create_startup(
        self, 
        name: str, 
        description: str = "", 
        niche: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Startup:
        """Create a new startup."""
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
            session.refresh(startup)
            return startup
    
    def get_startup(self, startup_id: str) -> Optional[Startup]:
        """Get startup by ID."""
        with self.get_session() as session:
            return session.query(Startup).filter(Startup.id == startup_id).first()
    
    def get_all_startups(self) -> List[Startup]:
        """Get all startups."""
        with self.get_session() as session:
            return session.query(Startup).all()
    
    def update_startup(
        self, 
        startup_id: str, 
        updates: Dict[str, Any]
    ) -> Optional[Startup]:
        """Update startup."""
        with self.get_session() as session:
            startup = session.query(Startup).filter(Startup.id == startup_id).first()
            if startup:
                for key, value in updates.items():
                    if hasattr(startup, key):
                        setattr(startup, key, value)
                startup.updated_at = datetime.utcnow()
                session.commit()
                session.refresh(startup)
            return startup
    
    def delete_startup(self, startup_id: str) -> bool:
        """Delete startup."""
        with self.get_session() as session:
            startup = session.query(Startup).filter(Startup.id == startup_id).first()
            if startup:
                session.delete(startup)
                session.commit()
                return True
            return False
    
    def create_agent(
        self, 
        startup_id: str, 
        agent_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Agent:
        """Create a new agent."""
        with self.get_session() as session:
            agent = Agent(
                id=generate_id("agent"),
                startup_id=startup_id,
                agent_type=agent_type,
                metadata_json=metadata or {}
            )
            session.add(agent)
            session.commit()
            session.refresh(agent)
            return agent
    
    def get_agents_by_startup(self, startup_id: str) -> List[Agent]:
        """Get agents by startup ID."""
        with self.get_session() as session:
            return session.query(Agent).filter(Agent.startup_id == startup_id).all()
    
    def update_agent(
        self, 
        agent_id: str, 
        updates: Dict[str, Any]
    ) -> Optional[Agent]:
        """Update agent."""
        with self.get_session() as session:
            agent = session.query(Agent).filter(Agent.id == agent_id).first()
            if agent:
                for key, value in updates.items():
                    if hasattr(agent, key):
                        setattr(agent, key, value)
                session.commit()
                session.refresh(agent)
            return agent
    
    def create_task(
        self, 
        startup_id: str, 
        task_type: str,
        description: str = "",
        priority: int = 1,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Task:
        """Create a new task."""
        with self.get_session() as session:
            task = Task(
                id=generate_id("task"),
                startup_id=startup_id,
                task_type=task_type,
                description=description,
                priority=priority,
                metadata_json=metadata or {}
            )
            session.add(task)
            session.commit()
            session.refresh(task)
            return task
    
    def get_tasks_by_startup(self, startup_id: str) -> List[Task]:
        """Get tasks by startup ID."""
        with self.get_session() as session:
            return session.query(Task).filter(Task.startup_id == startup_id).all()
    
    def update_task(
        self, 
        task_id: str, 
        updates: Dict[str, Any]
    ) -> Optional[Task]:
        """Update task."""
        with self.get_session() as session:
            task = session.query(Task).filter(Task.id == task_id).first()
            if task:
                for key, value in updates.items():
                    if hasattr(task, key):
                        setattr(task, key, value)
                session.commit()
                session.refresh(task)
            return task
    
    def create_metric(
        self, 
        startup_id: str, 
        metric_type: str,
        value: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Metrics:
        """Create a new metric."""
        with self.get_session() as session:
            metric = Metrics(
                id=generate_id("metric"),
                startup_id=startup_id,
                metric_type=metric_type,
                value=value,
                metadata_json=metadata or {}
            )
            session.add(metric)
            session.commit()
            session.refresh(metric)
            return metric
    
    def get_metrics_by_startup(
        self, 
        startup_id: str, 
        metric_type: Optional[str] = None
    ) -> List[Metrics]:
        """Get metrics by startup ID."""
        with self.get_session() as session:
            query = session.query(Metrics).filter(Metrics.startup_id == startup_id)
            if metric_type:
                query = query.filter(Metrics.metric_type == metric_type)
            return query.all()
    
    def backup_database(self, backup_path: str) -> bool:
        """Backup database."""
        try:
            if 'sqlite' in self.database_url:
                db_path = self.database_url.replace('sqlite:///', '')
                import shutil
                shutil.copy2(db_path, backup_path)
                return True
            else:
                logger.warning("Backup only supported for SQLite databases")
                return False
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return False
    
    def cleanup_old_data(self, days: int = 30) -> int:
        """Clean up old data."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        deleted_count = 0
        
        with self.get_session() as session:
            # Clean up old metrics
            old_metrics = session.query(Metrics).filter(
                Metrics.timestamp < cutoff_date
            ).all()
            for metric in old_metrics:
                session.delete(metric)
                deleted_count += 1
            
            # Clean up old tasks
            old_tasks = session.query(Task).filter(
                Task.created_at < cutoff_date
            ).all()
            for task in old_tasks:
                session.delete(task)
                deleted_count += 1
            
            session.commit()
        
        logger.info(f"Cleaned up {deleted_count} old records")
        return deleted_count
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        with self.get_session() as session:
            stats = {
                'startups': session.query(Startup).count(),
                'agents': session.query(Agent).count(),
                'tasks': session.query(Task).count(),
                'metrics': session.query(Metrics).count(),
                'active_startups': session.query(Startup).filter(
                    Startup.status == 'active'
                ).count(),
                'pending_tasks': session.query(Task).filter(
                    Task.status == 'pending'
                ).count()
            }
            return stats


# Global database manager instance
db_manager = DatabaseManager() 
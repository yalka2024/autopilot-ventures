#!/usr/bin/env python3
"""
Authentication System for AutoPilot Ventures Platform
Implements user authentication, JWT tokens, and role-based access control
"""

import os
import jwt
import bcrypt
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from functools import wraps
from dataclasses import dataclass
from enum import Enum

from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr

from config import config
from utils import generate_id, log
from database_postgresql import db_manager, User

# Configure logging
logger = logging.getLogger(__name__)

# Security configuration
security = HTTPBearer()

# JWT Configuration
JWT_SECRET = os.getenv('JWT_SECRET', 'your-super-secret-jwt-key-change-in-production')
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24


class UserRole(Enum):
    """User roles for access control."""
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"
    VIEWER = "viewer"


class Permission(Enum):
    """System permissions."""
    # Startup permissions
    CREATE_STARTUP = "create_startup"
    READ_STARTUP = "read_startup"
    UPDATE_STARTUP = "update_startup"
    DELETE_STARTUP = "delete_startup"
    
    # Agent permissions
    CREATE_AGENT = "create_agent"
    READ_AGENT = "read_agent"
    UPDATE_AGENT = "update_agent"
    DELETE_AGENT = "delete_agent"
    
    # Task permissions
    CREATE_TASK = "create_task"
    READ_TASK = "read_task"
    UPDATE_TASK = "update_task"
    DELETE_TASK = "delete_task"
    
    # System permissions
    READ_METRICS = "read_metrics"
    READ_LOGS = "read_logs"
    MANAGE_USERS = "manage_users"
    SYSTEM_CONFIG = "system_config"


@dataclass
class UserPermissions:
    """User permissions configuration."""
    role: UserRole
    permissions: List[Permission]


# Role-based permissions mapping
ROLE_PERMISSIONS = {
    UserRole.ADMIN: [
        Permission.CREATE_STARTUP, Permission.READ_STARTUP, Permission.UPDATE_STARTUP, Permission.DELETE_STARTUP,
        Permission.CREATE_AGENT, Permission.READ_AGENT, Permission.UPDATE_AGENT, Permission.DELETE_AGENT,
        Permission.CREATE_TASK, Permission.READ_TASK, Permission.UPDATE_TASK, Permission.DELETE_TASK,
        Permission.READ_METRICS, Permission.READ_LOGS, Permission.MANAGE_USERS, Permission.SYSTEM_CONFIG
    ],
    UserRole.MANAGER: [
        Permission.CREATE_STARTUP, Permission.READ_STARTUP, Permission.UPDATE_STARTUP,
        Permission.CREATE_AGENT, Permission.READ_AGENT, Permission.UPDATE_AGENT,
        Permission.CREATE_TASK, Permission.READ_TASK, Permission.UPDATE_TASK,
        Permission.READ_METRICS, Permission.READ_LOGS
    ],
    UserRole.USER: [
        Permission.READ_STARTUP, Permission.UPDATE_STARTUP,
        Permission.READ_AGENT, Permission.UPDATE_AGENT,
        Permission.CREATE_TASK, Permission.READ_TASK, Permission.UPDATE_TASK,
        Permission.READ_METRICS
    ],
    UserRole.VIEWER: [
        Permission.READ_STARTUP,
        Permission.READ_AGENT,
        Permission.READ_TASK,
        Permission.READ_METRICS
    ]
}


class UserCreate(BaseModel):
    """User creation model."""
    username: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.USER


class UserLogin(BaseModel):
    """User login model."""
    username: str
    password: str


class UserUpdate(BaseModel):
    """User update model."""
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class TokenResponse(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str
    expires_in: int
    user: Dict[str, Any]


class AuthManager:
    """Authentication and authorization manager."""
    
    def __init__(self):
        """Initialize authentication manager."""
        self.jwt_secret = JWT_SECRET
        self.jwt_algorithm = JWT_ALGORITHM
        self.jwt_expiration_hours = JWT_EXPIRATION_HOURS
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def create_user(self, username: str, email: str, password: str, role: UserRole = UserRole.USER) -> Dict[str, Any]:
        """Create a new user."""
        try:
            # Check if user already exists
            with db_manager.get_session() as session:
                existing_user = session.query(User).filter(
                    (User.username == username) | (User.email == email)
                ).first()
                
                if existing_user:
                    raise ValueError("User with this username or email already exists")
                
                # Create new user
                hashed_password = self.hash_password(password)
                user = User(
                    id=generate_id("user"),
                    username=username,
                    email=email,
                    password_hash=hashed_password,
                    role=role.value,
                    metadata_json={
                        'created_by': 'system',
                        'created_at': datetime.utcnow().isoformat()
                    }
                )
                
                session.add(user)
                session.commit()
                
                logger.info(f"Created user: {user.username} with role: {user.role}")
                
                return {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role,
                    'is_active': user.is_active,
                    'created_at': user.created_at.isoformat()
                }
                
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with username and password."""
        try:
            with db_manager.get_session() as session:
                user = session.query(User).filter(User.username == username).first()
                
                if not user or not user.is_active:
                    return None
                
                if not self.verify_password(password, user.password_hash):
                    return None
                
                # Update last login
                user.last_login = datetime.utcnow()
                session.commit()
                
                logger.info(f"User authenticated: {user.username}")
                
                return {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role,
                    'is_active': user.is_active,
                    'last_login': user.last_login.isoformat() if user.last_login else None
                }
                
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return None
    
    def create_access_token(self, user_data: Dict[str, Any]) -> str:
        """Create JWT access token."""
        try:
            expiration = datetime.utcnow() + timedelta(hours=self.jwt_expiration_hours)
            
            payload = {
                'sub': user_data['id'],
                'username': user_data['username'],
                'role': user_data['role'],
                'exp': expiration,
                'iat': datetime.utcnow()
            }
            
            token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
            return token
            
        except Exception as e:
            logger.error(f"Failed to create access token: {e}")
            raise
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and return user data."""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            
            # Check if user still exists and is active
            with db_manager.get_session() as session:
                user = session.query(User).filter(
                    User.id == payload['sub'],
                    User.is_active == True
                ).first()
                
                if not user:
                    return None
                
                return {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role,
                    'is_active': user.is_active
                }
                
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            return None
    
    def get_user_permissions(self, role: UserRole) -> List[Permission]:
        """Get permissions for a user role."""
        return ROLE_PERMISSIONS.get(role, [])
    
    def has_permission(self, user_role: UserRole, permission: Permission) -> bool:
        """Check if user role has specific permission."""
        permissions = self.get_user_permissions(user_role)
        return permission in permissions
    
    def update_user(self, user_id: str, update_data: UserUpdate) -> Dict[str, Any]:
        """Update user information."""
        try:
            with db_manager.get_session() as session:
                user = session.query(User).filter(User.id == user_id).first()
                
                if not user:
                    raise ValueError("User not found")
                
                if update_data.email is not None:
                    user.email = update_data.email
                
                if update_data.role is not None:
                    user.role = update_data.role.value
                
                if update_data.is_active is not None:
                    user.is_active = update_data.is_active
                
                session.commit()
                
                logger.info(f"Updated user: {user.username}")
                
                return {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role,
                    'is_active': user.is_active,
                    'updated_at': user.updated_at.isoformat()
                }
                
        except Exception as e:
            logger.error(f"Failed to update user: {e}")
            raise
    
    def delete_user(self, user_id: str) -> bool:
        """Delete user (soft delete by setting is_active to False)."""
        try:
            with db_manager.get_session() as session:
                user = session.query(User).filter(User.id == user_id).first()
                
                if not user:
                    return False
                
                user.is_active = False
                session.commit()
                
                logger.info(f"Deleted user: {user.username}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to delete user: {e}")
            return False
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users."""
        try:
            with db_manager.get_session() as session:
                users = session.query(User).all()
                
                return [
                    {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'role': user.role,
                        'is_active': user.is_active,
                        'created_at': user.created_at.isoformat(),
                        'last_login': user.last_login.isoformat() if user.last_login else None
                    }
                    for user in users
                ]
                
        except Exception as e:
            logger.error(f"Failed to get users: {e}")
            return []


# Global authentication manager instance
auth_manager = AuthManager()


# Dependency functions for FastAPI
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get current user from JWT token."""
    token = credentials.credentials
    user_data = auth_manager.verify_token(token)
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_data


def require_permission(permission: Permission):
    """Decorator to require specific permission."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: Dict[str, Any] = Depends(get_current_user), **kwargs):
            user_role = UserRole(current_user['role'])
            
            if not auth_manager.has_permission(user_role, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required: {permission.value}"
                )
            
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator


def require_role(role: UserRole):
    """Decorator to require specific role."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: Dict[str, Any] = Depends(get_current_user), **kwargs):
            user_role = UserRole(current_user['role'])
            
            if user_role != role and user_role != UserRole.ADMIN:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required role: {role.value}"
                )
            
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator


# Authentication endpoints (for FastAPI integration)
class AuthEndpoints:
    """Authentication endpoints for FastAPI."""
    
    @staticmethod
    async def register(user_data: UserCreate) -> Dict[str, Any]:
        """Register a new user."""
        try:
            user = auth_manager.create_user(
                username=user_data.username,
                email=user_data.email,
                password=user_data.password,
                role=user_data.role
            )
            
            return {
                'success': True,
                'message': 'User created successfully',
                'user': user
            }
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Registration failed: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    @staticmethod
    async def login(login_data: UserLogin) -> TokenResponse:
        """Login user and return access token."""
        try:
            user_data = auth_manager.authenticate_user(login_data.username, login_data.password)
            
            if not user_data:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid username or password"
                )
            
            access_token = auth_manager.create_access_token(user_data)
            
            return TokenResponse(
                access_token=access_token,
                token_type="bearer",
                expires_in=JWT_EXPIRATION_HOURS * 3600,
                user=user_data
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Login failed: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    @staticmethod
    async def get_profile(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        """Get current user profile."""
        return {
            'user': current_user,
            'permissions': auth_manager.get_user_permissions(UserRole(current_user['role']))
        }
    
    @staticmethod
    @require_role(UserRole.ADMIN)
    async def get_users(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        """Get all users (admin only)."""
        users = auth_manager.get_all_users()
        return {
            'users': users,
            'total': len(users)
        }
    
    @staticmethod
    @require_role(UserRole.ADMIN)
    async def update_user(
        user_id: str,
        update_data: UserUpdate,
        current_user: Dict[str, Any] = Depends(get_current_user)
    ) -> Dict[str, Any]:
        """Update user (admin only)."""
        try:
            user = auth_manager.update_user(user_id, update_data)
            return {
                'success': True,
                'message': 'User updated successfully',
                'user': user
            }
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            logger.error(f"User update failed: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    @staticmethod
    @require_role(UserRole.ADMIN)
    async def delete_user(
        user_id: str,
        current_user: Dict[str, Any] = Depends(get_current_user)
    ) -> Dict[str, Any]:
        """Delete user (admin only)."""
        success = auth_manager.delete_user(user_id)
        
        if success:
            return {
                'success': True,
                'message': 'User deleted successfully'
            }
        else:
            raise HTTPException(status_code=404, detail="User not found")


# Initialize default admin user
def initialize_default_admin():
    """Initialize default admin user if no users exist."""
    try:
        with db_manager.get_session() as session:
            user_count = session.query(User).count()
            
            if user_count == 0:
                # Create default admin user
                auth_manager.create_user(
                    username="admin",
                    email="admin@autopilotventures.com",
                    password="admin123",  # Change in production
                    role=UserRole.ADMIN
                )
                logger.info("Created default admin user")
                
    except Exception as e:
        logger.error(f"Failed to initialize default admin: {e}")


# Initialize on module import
initialize_default_admin() 
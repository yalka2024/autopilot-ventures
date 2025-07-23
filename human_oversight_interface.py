"""
Human Oversight Interface for AutoPilot Ventures
Web-based interface for human experts to review and approve critical AI decisions
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
import uuid
from enum import Enum
import structlog
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import redis
import jwt
from sqlalchemy import create_engine, Column, String, DateTime, Boolean, Text, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Database models
Base = declarative_base()

class ReviewDecision(Base):
    __tablename__ = "review_decisions"
    
    id = Column(String, primary_key=True)
    decision_type = Column(String, nullable=False)
    business_id = Column(String, nullable=True)
    agent_id = Column(String, nullable=True)
    decision_data = Column(Text, nullable=False)
    status = Column(String, default="pending")  # pending, approved, rejected
    priority = Column(String, default="medium")  # low, medium, high, critical
    created_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime, nullable=True)
    reviewer_id = Column(String, nullable=True)
    reviewer_comments = Column(Text, nullable=True)
    ai_confidence = Column(Integer, nullable=True)  # 0-100

class ExpertUser(Base):
    __tablename__ = "expert_users"
    
    id = Column(String, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    role = Column(String, nullable=False)  # admin, expert, reviewer
    permissions = Column(Text, nullable=False)  # JSON string of permissions
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

# Pydantic models for API
class DecisionReviewRequest(BaseModel):
    decision_type: str
    business_id: Optional[str] = None
    agent_id: Optional[str] = None
    decision_data: Dict[str, Any]
    priority: str = "medium"
    ai_confidence: Optional[int] = None

class ReviewResponse(BaseModel):
    review_id: str
    approved: bool
    reviewer_id: str
    comments: Optional[str] = None
    recommendations: Optional[List[str]] = None

class ExpertUserCreate(BaseModel):
    username: str
    email: str
    role: str
    permissions: List[str]

# FastAPI app
app = FastAPI(title="AutoPilot Ventures - Human Oversight Interface", version="2.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Database setup
DATABASE_URL = "postgresql://autopilot_user:autopilot_password_2024@localhost/autopilot_ventures"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

# Redis setup
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# JWT settings
JWT_SECRET = "your-jwt-secret-key"
JWT_ALGORITHM = "HS256"

class DecisionType(Enum):
    BUSINESS_LAUNCH = "business_launch"
    MAJOR_INVESTMENT = "major_investment"
    LEGAL_COMPLIANCE = "legal_compliance"
    FINANCIAL_COMMITMENT = "financial_commitment"
    PARTNERSHIP_AGREEMENT = "partnership_agreement"
    TECHNOLOGY_CHOICE = "technology_choice"
    MARKET_ENTRY = "market_entry"
    TEAM_HIRING = "team_hiring"

class PriorityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class HumanOversightManager:
    """Human oversight management system"""
    
    def __init__(self, db_session, redis_client):
        self.db = db_session
        self.redis = redis_client
        self.critical_decisions = [
            DecisionType.BUSINESS_LAUNCH.value,
            DecisionType.MAJOR_INVESTMENT.value,
            DecisionType.LEGAL_COMPLIANCE.value,
            DecisionType.FINANCIAL_COMMITMENT.value,
            DecisionType.PARTNERSHIP_AGREEMENT.value
        ]
        
        self.priority_thresholds = {
            "low": 0.3,
            "medium": 0.5,
            "high": 0.7,
            "critical": 0.9
        }
    
    async def submit_for_review(self, request: DecisionReviewRequest) -> str:
        """Submit a decision for human review"""
        try:
            review_id = str(uuid.uuid4())
            
            # Determine if human review is required
            requires_review = await self._requires_human_review(request)
            
            if not requires_review:
                logger.info("Decision does not require human review", 
                          decision_type=request.decision_type, business_id=request.business_id)
                return "auto_approved"
            
            # Create review record
            review_decision = ReviewDecision(
                id=review_id,
                decision_type=request.decision_type,
                business_id=request.business_id,
                agent_id=request.agent_id,
                decision_data=json.dumps(request.decision_data),
                priority=request.priority,
                ai_confidence=request.ai_confidence,
                status="pending"
            )
            
            self.db.add(review_decision)
            self.db.commit()
            
            # Send notification to appropriate experts
            await self._notify_experts(review_decision)
            
            logger.info("Decision submitted for human review", 
                      review_id=review_id, decision_type=request.decision_type)
            
            return review_id
            
        except Exception as e:
            logger.error("Error submitting decision for review", error=str(e))
            raise HTTPException(status_code=500, detail="Failed to submit for review")
    
    async def _requires_human_review(self, request: DecisionReviewRequest) -> bool:
        """Determine if a decision requires human review"""
        # Critical decisions always require review
        if request.decision_type in self.critical_decisions:
            return True
        
        # Low confidence decisions require review
        if request.ai_confidence and request.ai_confidence < 70:
            return True
        
        # High priority decisions require review
        if request.priority in ["high", "critical"]:
            return True
        
        # Financial decisions above threshold require review
        if request.decision_type == DecisionType.FINANCIAL_COMMITMENT.value:
            amount = request.decision_data.get('amount', 0)
            if amount > 10000:  # $10K threshold
                return True
        
        return False
    
    async def _notify_experts(self, review_decision: ReviewDecision):
        """Notify appropriate experts about pending review"""
        try:
            # Get experts based on decision type
            experts = await self._get_experts_for_decision_type(review_decision.decision_type)
            
            # Create notification
            notification = {
                "review_id": review_decision.id,
                "decision_type": review_decision.decision_type,
                "priority": review_decision.priority,
                "business_id": review_decision.business_id,
                "created_at": review_decision.created_at.isoformat(),
                "experts": experts
            }
            
            # Store notification in Redis for real-time updates
            await self.redis.lpush("pending_reviews", json.dumps(notification))
            await self.redis.expire("pending_reviews", 86400)  # 24 hours
            
            logger.info("Experts notified about pending review", 
                      review_id=review_decision.id, experts=experts)
            
        except Exception as e:
            logger.error("Error notifying experts", error=str(e))
    
    async def _get_experts_for_decision_type(self, decision_type: str) -> List[str]:
        """Get appropriate experts for decision type"""
        expert_mapping = {
            DecisionType.BUSINESS_LAUNCH.value: ["business_expert", "marketing_expert"],
            DecisionType.MAJOR_INVESTMENT.value: ["financial_expert", "investment_expert"],
            DecisionType.LEGAL_COMPLIANCE.value: ["legal_expert", "compliance_expert"],
            DecisionType.FINANCIAL_COMMITMENT.value: ["financial_expert", "accounting_expert"],
            DecisionType.PARTNERSHIP_AGREEMENT.value: ["business_expert", "legal_expert"],
            DecisionType.TECHNOLOGY_CHOICE.value: ["tech_expert", "architecture_expert"],
            DecisionType.MARKET_ENTRY.value: ["market_expert", "strategy_expert"],
            DecisionType.TEAM_HIRING.value: ["hr_expert", "business_expert"]
        }
        
        return expert_mapping.get(decision_type, ["general_expert"])
    
    async def get_pending_reviews(self, expert_role: str = None) -> List[Dict[str, Any]]:
        """Get pending reviews for an expert"""
        try:
            query = self.db.query(ReviewDecision).filter(ReviewDecision.status == "pending")
            
            if expert_role:
                # Filter by decision types the expert can review
                expert_decisions = await self._get_expert_decision_types(expert_role)
                query = query.filter(ReviewDecision.decision_type.in_(expert_decisions))
            
            reviews = query.order_by(ReviewDecision.created_at.desc()).all()
            
            return [
                {
                    "review_id": review.id,
                    "decision_type": review.decision_type,
                    "business_id": review.business_id,
                    "agent_id": review.agent_id,
                    "decision_data": json.loads(review.decision_data),
                    "priority": review.priority,
                    "ai_confidence": review.ai_confidence,
                    "created_at": review.created_at.isoformat(),
                    "time_elapsed": (datetime.utcnow() - review.created_at).total_seconds()
                }
                for review in reviews
            ]
            
        except Exception as e:
            logger.error("Error getting pending reviews", error=str(e))
            return []
    
    async def _get_expert_decision_types(self, expert_role: str) -> List[str]:
        """Get decision types an expert can review"""
        role_mapping = {
            "business_expert": [
                DecisionType.BUSINESS_LAUNCH.value,
                DecisionType.PARTNERSHIP_AGREEMENT.value,
                DecisionType.MARKET_ENTRY.value,
                DecisionType.TEAM_HIRING.value
            ],
            "financial_expert": [
                DecisionType.MAJOR_INVESTMENT.value,
                DecisionType.FINANCIAL_COMMITMENT.value
            ],
            "legal_expert": [
                DecisionType.LEGAL_COMPLIANCE.value,
                DecisionType.PARTNERSHIP_AGREEMENT.value
            ],
            "tech_expert": [
                DecisionType.TECHNOLOGY_CHOICE.value
            ],
            "admin": [dt.value for dt in DecisionType]  # Admin can review all
        }
        
        return role_mapping.get(expert_role, [])
    
    async def approve_decision(self, review_id: str, reviewer_id: str, 
                             comments: str = None, recommendations: List[str] = None) -> bool:
        """Approve a decision"""
        try:
            review = self.db.query(ReviewDecision).filter(ReviewDecision.id == review_id).first()
            
            if not review:
                raise HTTPException(status_code=404, detail="Review not found")
            
            if review.status != "pending":
                raise HTTPException(status_code=400, detail="Review already processed")
            
            # Update review
            review.status = "approved"
            review.reviewed_at = datetime.utcnow()
            review.reviewer_id = reviewer_id
            review.reviewer_comments = comments
            
            self.db.commit()
            
            # Notify AI system of approval
            await self._notify_ai_system(review_id, "approved", comments)
            
            logger.info("Decision approved", review_id=review_id, reviewer_id=reviewer_id)
            return True
            
        except Exception as e:
            logger.error("Error approving decision", error=str(e))
            return False
    
    async def reject_decision(self, review_id: str, reviewer_id: str, 
                            reason: str, recommendations: List[str] = None) -> bool:
        """Reject a decision"""
        try:
            review = self.db.query(ReviewDecision).filter(ReviewDecision.id == review_id).first()
            
            if not review:
                raise HTTPException(status_code=404, detail="Review not found")
            
            if review.status != "pending":
                raise HTTPException(status_code=400, detail="Review already processed")
            
            # Update review
            review.status = "rejected"
            review.reviewed_at = datetime.utcnow()
            review.reviewer_id = reviewer_id
            review.reviewer_comments = f"Rejected: {reason}"
            
            self.db.commit()
            
            # Notify AI system of rejection
            await self._notify_ai_system(review_id, "rejected", reason)
            
            logger.info("Decision rejected", review_id=review_id, reviewer_id=reviewer_id, reason=reason)
            return True
            
        except Exception as e:
            logger.error("Error rejecting decision", error=str(e))
            return False
    
    async def _notify_ai_system(self, review_id: str, decision: str, comments: str):
        """Notify AI system of human decision"""
        try:
            notification = {
                "review_id": review_id,
                "decision": decision,
                "comments": comments,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Store in Redis for AI system to pick up
            await self.redis.lpush("ai_decisions", json.dumps(notification))
            await self.redis.expire("ai_decisions", 86400)  # 24 hours
            
        except Exception as e:
            logger.error("Error notifying AI system", error=str(e))

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency to get current user
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# API endpoints
@app.post("/api/review/submit", response_model=Dict[str, str])
async def submit_for_review(
    request: DecisionReviewRequest,
    db = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Submit a decision for human review"""
    oversight_manager = HumanOversightManager(db, redis_client)
    review_id = await oversight_manager.submit_for_review(request)
    return {"review_id": review_id}

@app.get("/api/review/pending", response_model=List[Dict[str, Any]])
async def get_pending_reviews(
    expert_role: str = None,
    db = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Get pending reviews for an expert"""
    oversight_manager = HumanOversightManager(db, redis_client)
    reviews = await oversight_manager.get_pending_reviews(expert_role)
    return reviews

@app.post("/api/review/{review_id}/approve", response_model=Dict[str, bool])
async def approve_decision(
    review_id: str,
    response: ReviewResponse,
    db = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Approve a decision"""
    oversight_manager = HumanOversightManager(db, redis_client)
    success = await oversight_manager.approve_decision(
        review_id, response.reviewer_id, response.comments, response.recommendations
    )
    return {"success": success}

@app.post("/api/review/{review_id}/reject", response_model=Dict[str, bool])
async def reject_decision(
    review_id: str,
    response: ReviewResponse,
    db = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """Reject a decision"""
    oversight_manager = HumanOversightManager(db, redis_client)
    success = await oversight_manager.reject_decision(
        review_id, response.reviewer_id, response.comments, response.recommendations
    )
    return {"success": success}

@app.get("/api/review/stats", response_model=Dict[str, Any])
async def get_review_stats(db = Depends(get_db), current_user: str = Depends(get_current_user)):
    """Get review statistics"""
    try:
        total_reviews = db.query(ReviewDecision).count()
        pending_reviews = db.query(ReviewDecision).filter(ReviewDecision.status == "pending").count()
        approved_reviews = db.query(ReviewDecision).filter(ReviewDecision.status == "approved").count()
        rejected_reviews = db.query(ReviewDecision).filter(ReviewDecision.status == "rejected").count()
        
        # Average review time
        completed_reviews = db.query(ReviewDecision).filter(
            ReviewDecision.status.in_(["approved", "rejected"]),
            ReviewDecision.reviewed_at.isnot(None)
        ).all()
        
        avg_review_time = 0
        if completed_reviews:
            total_time = sum([
                (review.reviewed_at - review.created_at).total_seconds()
                for review in completed_reviews
            ])
            avg_review_time = total_time / len(completed_reviews)
        
        return {
            "total_reviews": total_reviews,
            "pending_reviews": pending_reviews,
            "approved_reviews": approved_reviews,
            "rejected_reviews": rejected_reviews,
            "approval_rate": approved_reviews / (approved_reviews + rejected_reviews) if (approved_reviews + rejected_reviews) > 0 else 0,
            "average_review_time_hours": avg_review_time / 3600
        }
        
    except Exception as e:
        logger.error("Error getting review stats", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get statistics")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "human_oversight_interface", "version": "2.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080) 
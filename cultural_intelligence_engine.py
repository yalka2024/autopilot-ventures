#!/usr/bin/env python3
"""
Native Cultural Intelligence Engine
Uses ChromaDB vector embeddings to adapt business models culturally beyond translations
"""

import asyncio
import json
import logging
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import redis
import structlog

# Vector database and embeddings
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("Warning: ChromaDB not available, using simplified cultural intelligence")

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("Warning: sentence-transformers not available, using simplified embeddings")

from config import config
from utils import generate_id, log

# Configure structured logging
logger = structlog.get_logger()

class CulturalDimension(Enum):
    """Cultural dimensions for business adaptation."""
    POWER_DISTANCE = "power_distance"
    INDIVIDUALISM_COLLECTIVISM = "individualism_collectivism"
    MASCULINITY_FEMININITY = "masculinity_femininity"
    UNCERTAINTY_AVOIDANCE = "uncertainty_avoidance"
    LONG_TERM_ORIENTATION = "long_term_orientation"
    INDULGENCE_RESTRAINT = "indulgence_restraint"

class BusinessAspect(Enum):
    """Business aspects that can be culturally adapted."""
    MARKETING_MESSAGING = "marketing_messaging"
    PRODUCT_DESIGN = "product_design"
    PRICING_STRATEGY = "pricing_strategy"
    PAYMENT_PREFERENCES = "payment_preferences"
    CUSTOMER_SERVICE = "customer_service"
    BRAND_POSITIONING = "brand_positioning"
    CONTENT_STYLE = "content_style"
    USER_INTERFACE = "user_interface"

@dataclass
class CulturalProfile:
    """Cultural profile for a specific country/region."""
    country_code: str
    language: str
    cultural_dimensions: Dict[CulturalDimension, float]
    business_preferences: Dict[BusinessAspect, Dict[str, Any]]
    market_characteristics: Dict[str, Any]
    payment_methods: List[str]
    communication_style: str
    risk_tolerance: float
    innovation_adoption: float
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class CulturalAdaptation:
    """Cultural adaptation recommendation."""
    business_aspect: BusinessAspect
    original_content: str
    adapted_content: str
    cultural_rationale: str
    confidence_score: float
    adaptation_type: str
    target_culture: str
    source_culture: str
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class CulturalInsight:
    """Cultural insight for business strategy."""
    insight_id: str
    insight_type: str
    description: str
    cultural_context: Dict[str, Any]
    business_implications: List[str]
    confidence: float
    source_data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)

class CulturalKnowledgeBase:
    """Knowledge base for cultural intelligence using ChromaDB."""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        self.client = None
        self.collections = {}
        self.embedding_model = None
        
        if CHROMADB_AVAILABLE:
            self._initialize_chromadb()
        
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            self._initialize_embeddings()
        
        # Initialize cultural profiles
        self._initialize_cultural_profiles()
    
    def _initialize_chromadb(self):
        """Initialize ChromaDB client and collections."""
        try:
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Create collections for different types of cultural data
            collections_to_create = [
                "cultural_profiles",
                "business_adaptations", 
                "market_insights",
                "payment_preferences",
                "communication_styles"
            ]
            
            for collection_name in collections_to_create:
                try:
                    self.collections[collection_name] = self.client.get_collection(collection_name)
                except:
                    self.collections[collection_name] = self.client.create_collection(collection_name)
            
            logger.info("ChromaDB initialized successfully", collections=list(self.collections.keys()))
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            self.client = None
    
    def _initialize_embeddings(self):
        """Initialize sentence transformer for embeddings."""
        try:
            # Use a multilingual model for better cultural understanding
            self.embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            logger.info("Sentence transformer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize sentence transformer: {e}")
            self.embedding_model = None
    
    def _initialize_cultural_profiles(self):
        """Initialize default cultural profiles for supported countries."""
        self.cultural_profiles = {
            "US": CulturalProfile(
                country_code="US",
                language="en",
                cultural_dimensions={
                    CulturalDimension.POWER_DISTANCE: 40,
                    CulturalDimension.INDIVIDUALISM_COLLECTIVISM: 91,
                    CulturalDimension.MASCULINITY_FEMININITY: 62,
                    CulturalDimension.UNCERTAINTY_AVOIDANCE: 46,
                    CulturalDimension.LONG_TERM_ORIENTATION: 26,
                    CulturalDimension.INDULGENCE_RESTRAINT: 68
                },
                business_preferences={
                    BusinessAspect.MARKETING_MESSAGING: {
                        "style": "direct",
                        "focus": "individual_benefits",
                        "tone": "confident"
                    },
                    BusinessAspect.PAYMENT_PREFERENCES: {
                        "preferred_methods": ["credit_card", "paypal"],
                        "trust_factors": ["security", "convenience"]
                    }
                },
                market_characteristics={
                    "competition_level": "high",
                    "innovation_adoption": "fast",
                    "price_sensitivity": "medium"
                },
                payment_methods=["credit_card", "paypal", "apple_pay", "google_pay"],
                communication_style="direct",
                risk_tolerance=0.7,
                innovation_adoption=0.8
            ),
            "JP": CulturalProfile(
                country_code="JP",
                language="ja",
                cultural_dimensions={
                    CulturalDimension.POWER_DISTANCE: 54,
                    CulturalDimension.INDIVIDUALISM_COLLECTIVISM: 46,
                    CulturalDimension.MASCULINITY_FEMININITY: 95,
                    CulturalDimension.UNCERTAINTY_AVOIDANCE: 92,
                    CulturalDimension.LONG_TERM_ORIENTATION: 88,
                    CulturalDimension.INDULGENCE_RESTRAINT: 42
                },
                business_preferences={
                    BusinessAspect.MARKETING_MESSAGING: {
                        "style": "respectful",
                        "focus": "quality_reliability",
                        "tone": "humble"
                    },
                    BusinessAspect.PAYMENT_PREFERENCES: {
                        "preferred_methods": ["cash", "bank_transfer"],
                        "trust_factors": ["reliability", "tradition"]
                    }
                },
                market_characteristics={
                    "competition_level": "very_high",
                    "innovation_adoption": "selective",
                    "price_sensitivity": "low"
                },
                payment_methods=["cash", "bank_transfer", "credit_card"],
                communication_style="indirect",
                risk_tolerance=0.3,
                innovation_adoption=0.6
            ),
            "BR": CulturalProfile(
                country_code="BR",
                language="pt",
                cultural_dimensions={
                    CulturalDimension.POWER_DISTANCE: 69,
                    CulturalDimension.INDIVIDUALISM_COLLECTIVISM: 38,
                    CulturalDimension.MASCULINITY_FEMININITY: 49,
                    CulturalDimension.UNCERTAINTY_AVOIDANCE: 76,
                    CulturalDimension.LONG_TERM_ORIENTATION: 44,
                    CulturalDimension.INDULGENCE_RESTRAINT: 59
                },
                business_preferences={
                    BusinessAspect.MARKETING_MESSAGING: {
                        "style": "emotional",
                        "focus": "social_connection",
                        "tone": "warm"
                    },
                    BusinessAspect.PAYMENT_PREFERENCES: {
                        "preferred_methods": ["pix", "boleto", "credit_card"],
                        "trust_factors": ["convenience", "social_proof"]
                    }
                },
                market_characteristics={
                    "competition_level": "medium",
                    "innovation_adoption": "moderate",
                    "price_sensitivity": "high"
                },
                payment_methods=["pix", "boleto", "credit_card", "paypal"],
                communication_style="warm",
                risk_tolerance=0.5,
                innovation_adoption=0.7
            )
        }
        
        # Add more countries as needed
        for country_code in ["CN", "ES", "FR", "DE", "AR", "IN", "RU", "AE"]:
            if country_code not in self.cultural_profiles:
                self.cultural_profiles[country_code] = self._create_default_profile(country_code)
    
    def _create_default_profile(self, country_code: str) -> CulturalProfile:
        """Create a default cultural profile for a country."""
        language_map = {
            "CN": "zh", "ES": "es", "FR": "fr", "DE": "de",
            "AR": "ar", "IN": "hi", "RU": "ru", "AE": "ar"
        }
        
        return CulturalProfile(
            country_code=country_code,
            language=language_map.get(country_code, "en"),
            cultural_dimensions={
                CulturalDimension.POWER_DISTANCE: 50,
                CulturalDimension.INDIVIDUALISM_COLLECTIVISM: 50,
                CulturalDimension.MASCULINITY_FEMININITY: 50,
                CulturalDimension.UNCERTAINTY_AVOIDANCE: 50,
                CulturalDimension.LONG_TERM_ORIENTATION: 50,
                CulturalDimension.INDULGENCE_RESTRAINT: 50
            },
            business_preferences={
                BusinessAspect.MARKETING_MESSAGING: {
                    "style": "balanced",
                    "focus": "value_proposition",
                    "tone": "professional"
                },
                BusinessAspect.PAYMENT_PREFERENCES: {
                    "preferred_methods": ["credit_card", "bank_transfer"],
                    "trust_factors": ["security", "reliability"]
                }
            },
            market_characteristics={
                "competition_level": "medium",
                "innovation_adoption": "moderate",
                "price_sensitivity": "medium"
            },
            payment_methods=["credit_card", "bank_transfer"],
            communication_style="balanced",
            risk_tolerance=0.5,
            innovation_adoption=0.6
        )
    
    async def add_cultural_data(
        self,
        collection_name: str,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
    ):
        """Add cultural data to ChromaDB collection."""
        if not self.client or collection_name not in self.collections:
            logger.warning(f"ChromaDB not available or collection {collection_name} not found")
            return
        
        try:
            collection = self.collections[collection_name]
            
            if ids is None:
                ids = [generate_id(f"cultural_{collection_name}") for _ in documents]
            
            # Generate embeddings if model is available
            embeddings = None
            if self.embedding_model:
                embeddings = self.embedding_model.encode(documents).tolist()
            
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids,
                embeddings=embeddings
            )
            
            logger.info(f"Added {len(documents)} documents to {collection_name}")
            
        except Exception as e:
            logger.error(f"Failed to add cultural data to {collection_name}: {e}")
    
    async def search_cultural_insights(
        self,
        query: str,
        collection_name: str = "cultural_profiles",
        n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for cultural insights using semantic search."""
        if not self.client or collection_name not in self.collections:
            logger.warning(f"ChromaDB not available or collection {collection_name} not found")
            return []
        
        try:
            collection = self.collections[collection_name]
            
            # Generate query embedding if model is available
            query_embedding = None
            if self.embedding_model:
                query_embedding = self.embedding_model.encode([query]).tolist()
            
            results = collection.query(
                query_texts=[query],
                query_embeddings=query_embedding,
                n_results=n_results
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to search cultural insights: {e}")
            return []

class CulturalIntelligenceEngine:
    """Main cultural intelligence engine for business adaptation."""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client or redis.Redis.from_url(config.database.url.replace('sqlite', 'redis'))
        self.knowledge_base = CulturalKnowledgeBase()
        self.adaptation_history = []
        self.insight_cache = {}
        
        logger.info("Cultural Intelligence Engine initialized")
    
    async def adapt_business_strategy(
        self,
        business_aspect: BusinessAspect,
        original_content: str,
        source_culture: str,
        target_culture: str,
        context: Dict[str, Any] = None
    ) -> CulturalAdaptation:
        """Adapt business strategy for target culture."""
        try:
            # Get cultural profiles
            source_profile = self.knowledge_base.cultural_profiles.get(source_culture)
            target_profile = self.knowledge_base.cultural_profiles.get(target_culture)
            
            if not source_profile or not target_profile:
                logger.warning(f"Cultural profiles not found for {source_culture} or {target_culture}")
                return self._create_default_adaptation(business_aspect, original_content, target_culture)
            
            # Analyze cultural differences
            cultural_differences = self._analyze_cultural_differences(source_profile, target_profile)
            
            # Generate adaptation
            adapted_content = await self._generate_cultural_adaptation(
                business_aspect, original_content, cultural_differences, context
            )
            
            # Create adaptation object
            adaptation = CulturalAdaptation(
                business_aspect=business_aspect,
                original_content=original_content,
                adapted_content=adapted_content,
                cultural_rationale=self._generate_cultural_rationale(cultural_differences, business_aspect),
                confidence_score=self._calculate_adaptation_confidence(cultural_differences),
                adaptation_type=self._determine_adaptation_type(business_aspect, cultural_differences),
                target_culture=target_culture,
                source_culture=source_culture
            )
            
            # Store adaptation
            self.adaptation_history.append(adaptation)
            await self._store_adaptation(adaptation)
            
            logger.info(f"Created cultural adaptation for {business_aspect.value}",
                       source_culture=source_culture,
                       target_culture=target_culture,
                       confidence=adaptation.confidence_score)
            
            return adaptation
            
        except Exception as e:
            logger.error(f"Failed to adapt business strategy: {e}")
            return self._create_default_adaptation(business_aspect, original_content, target_culture)
    
    def _analyze_cultural_differences(
        self, 
        source_profile: CulturalProfile, 
        target_profile: CulturalProfile
    ) -> Dict[str, float]:
        """Analyze differences between cultural profiles."""
        differences = {}
        
        for dimension in CulturalDimension:
            source_value = source_profile.cultural_dimensions.get(dimension, 50)
            target_value = target_profile.cultural_dimensions.get(dimension, 50)
            differences[dimension.value] = abs(target_value - source_value) / 100.0
        
        # Add business preference differences
        for aspect in BusinessAspect:
            source_prefs = source_profile.business_preferences.get(aspect, {})
            target_prefs = target_profile.business_preferences.get(aspect, {})
            
            # Calculate similarity score (simplified)
            common_keys = set(source_prefs.keys()) & set(target_prefs.keys())
            if common_keys:
                similarity = sum(1 for key in common_keys if source_prefs[key] == target_prefs[key]) / len(common_keys)
                differences[f"{aspect.value}_similarity"] = 1.0 - similarity
        
        return differences
    
    async def _generate_cultural_adaptation(
        self,
        business_aspect: BusinessAspect,
        original_content: str,
        cultural_differences: Dict[str, float],
        context: Dict[str, Any] = None
    ) -> str:
        """Generate culturally adapted content."""
        # This would typically use an LLM for content generation
        # For now, we'll use rule-based adaptation
        
        adaptation_rules = {
            BusinessAspect.MARKETING_MESSAGING: self._adapt_marketing_messaging,
            BusinessAspect.PRODUCT_DESIGN: self._adapt_product_design,
            BusinessAspect.PRICING_STRATEGY: self._adapt_pricing_strategy,
            BusinessAspect.PAYMENT_PREFERENCES: self._adapt_payment_preferences,
            BusinessAspect.CUSTOMER_SERVICE: self._adapt_customer_service,
            BusinessAspect.BRAND_POSITIONING: self._adapt_brand_positioning,
            BusinessAspect.CONTENT_STYLE: self._adapt_content_style,
            BusinessAspect.USER_INTERFACE: self._adapt_user_interface
        }
        
        adapter = adaptation_rules.get(business_aspect, self._adapt_generic)
        return adapter(original_content, cultural_differences, context)
    
    def _adapt_marketing_messaging(
        self, 
        content: str, 
        differences: Dict[str, float], 
        context: Dict[str, Any] = None
    ) -> str:
        """Adapt marketing messaging for cultural differences."""
        adapted = content
        
        # Adapt based on individualism vs collectivism
        if differences.get("individualism_collectivism", 0) > 0.3:
            if differences["individualism_collectivism"] > 0.5:
                # More individualistic culture
                adapted = adapted.replace("our team", "you")
                adapted = adapted.replace("we help", "you can achieve")
            else:
                # More collectivistic culture
                adapted = adapted.replace("you can", "we can help you")
                adapted = adapted.replace("individual", "community")
        
        # Adapt based on power distance
        if differences.get("power_distance", 0) > 0.3:
            if differences["power_distance"] > 0.5:
                # High power distance - more formal
                adapted = adapted.replace("hey", "dear")
                adapted = adapted.replace("thanks", "thank you very much")
            else:
                # Low power distance - more casual
                adapted = adapted.replace("dear", "hi")
                adapted = adapted.replace("thank you very much", "thanks")
        
        return adapted
    
    def _adapt_product_design(self, content: str, differences: Dict[str, float], context: Dict[str, Any] = None) -> str:
        """Adapt product design recommendations."""
        # Simplified adaptation
        return content
    
    def _adapt_pricing_strategy(self, content: str, differences: Dict[str, float], context: Dict[str, Any] = None) -> str:
        """Adapt pricing strategy for cultural preferences."""
        adapted = content
        
        # Adapt based on uncertainty avoidance
        if differences.get("uncertainty_avoidance", 0) > 0.3:
            if differences["uncertainty_avoidance"] > 0.5:
                # High uncertainty avoidance - emphasize guarantees
                adapted += " (with money-back guarantee)"
        
        return adapted
    
    def _adapt_payment_preferences(self, content: str, differences: Dict[str, float], context: Dict[str, Any] = None) -> str:
        """Adapt payment preferences."""
        return content
    
    def _adapt_customer_service(self, content: str, differences: Dict[str, float], context: Dict[str, Any] = None) -> str:
        """Adapt customer service approach."""
        return content
    
    def _adapt_brand_positioning(self, content: str, differences: Dict[str, float], context: Dict[str, Any] = None) -> str:
        """Adapt brand positioning."""
        return content
    
    def _adapt_content_style(self, content: str, differences: Dict[str, float], context: Dict[str, Any] = None) -> str:
        """Adapt content style."""
        return content
    
    def _adapt_user_interface(self, content: str, differences: Dict[str, float], context: Dict[str, Any] = None) -> str:
        """Adapt user interface recommendations."""
        return content
    
    def _adapt_generic(self, content: str, differences: Dict[str, float], context: Dict[str, Any] = None) -> str:
        """Generic adaptation fallback."""
        return content
    
    def _generate_cultural_rationale(
        self, 
        differences: Dict[str, float], 
        business_aspect: BusinessAspect
    ) -> str:
        """Generate rationale for cultural adaptation."""
        significant_differences = [
            (dim, diff) for dim, diff in differences.items() 
            if diff > 0.3
        ]
        
        if not significant_differences:
            return "Minimal cultural differences detected, adaptation not required."
        
        rationale_parts = []
        for dimension, difference in significant_differences:
            if "individualism_collectivism" in dimension:
                if difference > 0.5:
                    rationale_parts.append("High individualism-collectivism difference requires messaging adaptation")
                else:
                    rationale_parts.append("Moderate individualism-collectivism difference noted")
            
            elif "power_distance" in dimension:
                if difference > 0.5:
                    rationale_parts.append("High power distance difference requires formal communication style")
                else:
                    rationale_parts.append("Moderate power distance difference noted")
            
            elif "uncertainty_avoidance" in dimension:
                if difference > 0.5:
                    rationale_parts.append("High uncertainty avoidance requires additional guarantees and clarity")
                else:
                    rationale_parts.append("Moderate uncertainty avoidance difference noted")
        
        return "; ".join(rationale_parts) if rationale_parts else "Cultural adaptation applied based on profile analysis."
    
    def _calculate_adaptation_confidence(self, differences: Dict[str, float]) -> float:
        """Calculate confidence score for adaptation."""
        if not differences:
            return 0.5
        
        # Higher confidence for more significant differences
        max_difference = max(differences.values())
        base_confidence = min(max_difference * 1.5, 0.9)
        
        # Adjust based on number of significant differences
        significant_count = sum(1 for diff in differences.values() if diff > 0.3)
        confidence_boost = min(significant_count * 0.1, 0.2)
        
        return min(base_confidence + confidence_boost, 0.95)
    
    def _determine_adaptation_type(
        self, 
        business_aspect: BusinessAspect, 
        differences: Dict[str, float]
    ) -> str:
        """Determine the type of adaptation needed."""
        max_difference = max(differences.values()) if differences else 0
        
        if max_difference > 0.7:
            return "major_adaptation"
        elif max_difference > 0.4:
            return "moderate_adaptation"
        elif max_difference > 0.2:
            return "minor_adaptation"
        else:
            return "no_adaptation"
    
    def _create_default_adaptation(
        self, 
        business_aspect: BusinessAspect, 
        original_content: str, 
        target_culture: str
    ) -> CulturalAdaptation:
        """Create default adaptation when cultural profiles are not available."""
        return CulturalAdaptation(
            business_aspect=business_aspect,
            original_content=original_content,
            adapted_content=original_content,
            cultural_rationale="Default adaptation - cultural profile not available",
            confidence_score=0.3,
            adaptation_type="default",
            target_culture=target_culture,
            source_culture="unknown"
        )
    
    async def _store_adaptation(self, adaptation: CulturalAdaptation):
        """Store adaptation in Redis for persistence."""
        if not self.redis_client:
            return
        
        try:
            adaptation_data = {
                'business_aspect': adaptation.business_aspect.value,
                'original_content': adaptation.original_content,
                'adapted_content': adaptation.adapted_content,
                'cultural_rationale': adaptation.cultural_rationale,
                'confidence_score': adaptation.confidence_score,
                'adaptation_type': adaptation.adaptation_type,
                'target_culture': adaptation.target_culture,
                'source_culture': adaptation.source_culture,
                'timestamp': adaptation.timestamp.isoformat()
            }
            
            key = f"cultural_adaptation:{generate_id('adaptation')}"
            self.redis_client.hset(key, mapping=adaptation_data)
            self.redis_client.expire(key, 86400 * 30)  # 30 days TTL
            
        except Exception as e:
            logger.error(f"Failed to store adaptation: {e}")
    
    async def get_cultural_insights(
        self,
        query: str,
        target_culture: str,
        business_aspect: Optional[BusinessAspect] = None
    ) -> List[CulturalInsight]:
        """Get cultural insights for business strategy."""
        try:
            # Search knowledge base
            search_results = await self.knowledge_base.search_cultural_insights(
                query, "cultural_profiles", n_results=5
            )
            
            insights = []
            for i, result in enumerate(search_results.get('documents', [[]])[0]):
                metadata = search_results.get('metadatas', [[]])[0][i] if search_results.get('metadatas') else {}
                
                insight = CulturalInsight(
                    insight_id=generate_id("insight"),
                    insight_type="cultural_analysis",
                    description=result,
                    cultural_context=metadata,
                    business_implications=self._extract_business_implications(result, business_aspect),
                    confidence=0.7,  # Default confidence
                    source_data=metadata
                )
                
                insights.append(insight)
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to get cultural insights: {e}")
            return []
    
    def _extract_business_implications(
        self, 
        description: str, 
        business_aspect: Optional[BusinessAspect] = None
    ) -> List[str]:
        """Extract business implications from cultural insight."""
        implications = []
        
        if business_aspect == BusinessAspect.MARKETING_MESSAGING:
            implications.append("Consider adapting messaging tone and style")
            implications.append("Focus on cultural values in communication")
        
        elif business_aspect == BusinessAspect.PAYMENT_PREFERENCES:
            implications.append("Review payment method preferences")
            implications.append("Consider local payment solutions")
        
        else:
            implications.append("Apply cultural sensitivity in business decisions")
            implications.append("Consider local market characteristics")
        
        return implications
    
    async def get_cultural_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for cultural intelligence system."""
        metrics = {
            "total_adaptations": len(self.adaptation_history),
            "average_confidence": 0.0,
            "adaptation_types": {},
            "cultures_served": set(),
            "recent_adaptations": 0
        }
        
        if self.adaptation_history:
            metrics["average_confidence"] = np.mean([
                adaptation.confidence_score for adaptation in self.adaptation_history
            ])
            
            # Count adaptation types
            for adaptation in self.adaptation_history:
                adaptation_type = adaptation.adaptation_type
                metrics["adaptation_types"][adaptation_type] = metrics["adaptation_types"].get(adaptation_type, 0) + 1
                
                metrics["cultures_served"].add(adaptation.target_culture)
            
            # Count recent adaptations (last 7 days)
            week_ago = datetime.utcnow() - timedelta(days=7)
            metrics["recent_adaptations"] = sum(
                1 for adaptation in self.adaptation_history 
                if adaptation.timestamp > week_ago
            )
        
        metrics["cultures_served"] = list(metrics["cultures_served"])
        
        return metrics

# Global instance
_cultural_intelligence_instance = None

def get_cultural_intelligence_engine(redis_client: Optional[redis.Redis] = None) -> CulturalIntelligenceEngine:
    """Get global cultural intelligence engine instance."""
    global _cultural_intelligence_instance
    if _cultural_intelligence_instance is None:
        _cultural_intelligence_instance = CulturalIntelligenceEngine(redis_client)
    return _cultural_intelligence_instance 
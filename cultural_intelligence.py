"""Cultural Intelligence System for global market adaptation."""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import requests

from config import config
from utils import generate_id, log

logger = logging.getLogger(__name__)

# Simple translation function to avoid dependency conflicts
def translate_text(text: str, target_language: str) -> str:
    """Simple translation function using a free API."""
    try:
        # Use a simple translation service
        url = "https://api.mymemory.translated.net/get"
        params = {
            'q': text,
            'langpair': f'en|{target_language}'
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('responseData', {}).get('translatedText', text)
        return text
    except Exception as e:
        logger.warning(f"Translation failed: {e}")
        return text


class CulturalDimension(Enum):
    """Hofstede's cultural dimensions."""
    
    POWER_DISTANCE = "power_distance"
    INDIVIDUALISM = "individualism"
    MASCULINITY = "masculinity"
    UNCERTAINTY_AVOIDANCE = "uncertainty_avoidance"
    LONG_TERM_ORIENTATION = "long_term_orientation"
    INDULGENCE = "indulgence"


class MarketMaturity(Enum):
    """Market maturity levels."""
    
    EMERGING = "emerging"
    DEVELOPING = "developing"
    MATURE = "mature"
    SATURATED = "saturated"


@dataclass
class CulturalProfile:
    """Cultural profile for a specific region."""
    
    country_code: str
    country_name: str
    language: str
    population: int
    gdp_per_capita: float
    internet_penetration: float
    mobile_penetration: float
    ecommerce_adoption: float
    cultural_dimensions: Dict[str, float]
    market_maturity: MarketMaturity
    business_practices: Dict[str, Any]
    communication_style: Dict[str, Any]
    payment_preferences: List[str]
    social_media_platforms: List[str]
    seasonal_patterns: Dict[str, Any]
    regulatory_environment: Dict[str, Any]
    last_updated: datetime


@dataclass
class MarketOpportunity:
    """Market opportunity analysis."""
    
    country_code: str
    niche: str
    market_size: float
    competition_level: str
    entry_barriers: List[str]
    growth_potential: float
    cultural_fit_score: float
    regulatory_complexity: float
    recommended_approach: Dict[str, Any]
    estimated_timeline: int  # days
    risk_factors: List[str]
    success_probability: float


class CulturalIntelligenceAgent:
    """AI agent for cultural intelligence and market research."""
    
    def __init__(self, startup_id: str):
        self.startup_id = startup_id
        self.agent_id = generate_id("cultural_intelligence")
        self.cultural_profiles: Dict[str, CulturalProfile] = {}
        self.market_opportunities: Dict[str, MarketOpportunity] = {}
        
        # Initialize cultural profiles for supported countries
        self._initialize_cultural_profiles()
        
        logger.info(f"Cultural Intelligence Agent initialized for startup {startup_id}")
    
    def _initialize_cultural_profiles(self):
        """Initialize cultural profiles for supported countries."""
        profiles_data = {
            'US': {
                'country_name': 'United States',
                'language': 'en',
                'population': 331002651,
                'gdp_per_capita': 63416.0,
                'internet_penetration': 0.89,
                'mobile_penetration': 0.83,
                'ecommerce_adoption': 0.87,
                'cultural_dimensions': {
                    'power_distance': 40,
                    'individualism': 91,
                    'masculinity': 62,
                    'uncertainty_avoidance': 46,
                    'long_term_orientation': 26,
                    'indulgence': 68
                },
                'market_maturity': MarketMaturity.MATURE,
                'business_practices': {
                    'decision_making': 'individual',
                    'hierarchy': 'flat',
                    'communication': 'direct',
                    'negotiation': 'competitive'
                },
                'communication_style': {
                    'formality': 'low',
                    'context': 'low',
                    'directness': 'high',
                    'relationship_focus': 'low'
                },
                'payment_preferences': ['credit_card', 'paypal', 'apple_pay', 'google_pay'],
                'social_media_platforms': ['facebook', 'instagram', 'twitter', 'linkedin', 'tiktok'],
                'seasonal_patterns': {
                    'peak_seasons': ['holiday', 'back_to_school'],
                    'slow_seasons': ['january', 'summer']
                },
                'regulatory_environment': {
                    'complexity': 'medium',
                    'enforcement': 'strict',
                    'compliance_requirements': ['gdpr', 'ccpa', 'sox']
                }
            },
            'CN': {
                'country_name': 'China',
                'language': 'zh',
                'population': 1439323776,
                'gdp_per_capita': 10261.0,
                'internet_penetration': 0.70,
                'mobile_penetration': 0.95,
                'ecommerce_adoption': 0.85,
                'cultural_dimensions': {
                    'power_distance': 80,
                    'individualism': 20,
                    'masculinity': 66,
                    'uncertainty_avoidance': 30,
                    'long_term_orientation': 87,
                    'indulgence': 24
                },
                'market_maturity': MarketMaturity.MATURE,
                'business_practices': {
                    'decision_making': 'collective',
                    'hierarchy': 'steep',
                    'communication': 'indirect',
                    'negotiation': 'relationship_based'
                },
                'communication_style': {
                    'formality': 'high',
                    'context': 'high',
                    'directness': 'low',
                    'relationship_focus': 'high'
                },
                'payment_preferences': ['alipay', 'wechat_pay', 'union_pay'],
                'social_media_platforms': ['wechat', 'weibo', 'douyin', 'xiaohongshu'],
                'seasonal_patterns': {
                    'peak_seasons': ['spring_festival', 'singles_day', 'golden_week'],
                    'slow_seasons': ['summer', 'winter']
                },
                'regulatory_environment': {
                    'complexity': 'high',
                    'enforcement': 'strict',
                    'compliance_requirements': ['cybersecurity_law', 'data_protection']
                }
            },
            'ES': {
                'country_name': 'Spain',
                'language': 'es',
                'population': 46754778,
                'gdp_per_capita': 29600.0,
                'internet_penetration': 0.85,
                'mobile_penetration': 0.88,
                'ecommerce_adoption': 0.72,
                'cultural_dimensions': {
                    'power_distance': 57,
                    'individualism': 51,
                    'masculinity': 42,
                    'uncertainty_avoidance': 86,
                    'long_term_orientation': 48,
                    'indulgence': 44
                },
                'market_maturity': MarketMaturity.DEVELOPING,
                'business_practices': {
                    'decision_making': 'hierarchical',
                    'hierarchy': 'moderate',
                    'communication': 'formal',
                    'negotiation': 'relationship_based'
                },
                'communication_style': {
                    'formality': 'medium',
                    'context': 'medium',
                    'directness': 'medium',
                    'relationship_focus': 'medium'
                },
                'payment_preferences': ['credit_card', 'paypal', 'bizum'],
                'social_media_platforms': ['whatsapp', 'instagram', 'facebook', 'twitter'],
                'seasonal_patterns': {
                    'peak_seasons': ['christmas', 'summer_sales'],
                    'slow_seasons': ['january', 'september']
                },
                'regulatory_environment': {
                    'complexity': 'medium',
                    'enforcement': 'moderate',
                    'compliance_requirements': ['gdpr', 'spanish_data_protection']
                }
            }
        }
        
        for country_code, data in profiles_data.items():
            profile = CulturalProfile(
                country_code=country_code,
                country_name=data['country_name'],
                language=data['language'],
                population=data['population'],
                gdp_per_capita=data['gdp_per_capita'],
                internet_penetration=data['internet_penetration'],
                mobile_penetration=data['mobile_penetration'],
                ecommerce_adoption=data['ecommerce_adoption'],
                cultural_dimensions=data['cultural_dimensions'],
                market_maturity=data['market_maturity'],
                business_practices=data['business_practices'],
                communication_style=data['communication_style'],
                payment_preferences=data['payment_preferences'],
                social_media_platforms=data['social_media_platforms'],
                seasonal_patterns=data['seasonal_patterns'],
                regulatory_environment=data['regulatory_environment'],
                last_updated=datetime.utcnow()
            )
            self.cultural_profiles[country_code] = profile
    
    async def analyze_cultural_fit(
        self,
        product_concept: str,
        target_countries: List[str]
    ) -> Dict[str, Any]:
        """Analyze cultural fit of a product concept across countries."""
        results = {}
        
        for country_code in target_countries:
            if country_code not in self.cultural_profiles:
                continue
            
            profile = self.cultural_profiles[country_code]
            
            # Analyze cultural fit based on dimensions
            fit_score = self._calculate_cultural_fit_score(product_concept, profile)
            
            # Generate cultural adaptation recommendations
            adaptations = self._generate_cultural_adaptations(product_concept, profile)
            
            # Assess market readiness
            market_readiness = self._assess_market_readiness(profile)
            
            results[country_code] = {
                'cultural_fit_score': fit_score,
                'cultural_adaptations': adaptations,
                'market_readiness': market_readiness,
                'recommended_approach': self._generate_approach_recommendations(profile),
                'risk_factors': self._identify_risk_factors(profile),
                'success_probability': fit_score * market_readiness['overall_score']
            }
        
        return results
    
    def _calculate_cultural_fit_score(self, product_concept: str, profile: CulturalProfile) -> float:
        """Calculate cultural fit score for a product concept."""
        score = 0.5  # Base score
        
        # Analyze based on cultural dimensions
        dimensions = profile.cultural_dimensions
        
        # Individualism vs Collectivism
        if 'individual' in product_concept.lower() or 'personal' in product_concept.lower():
            if dimensions['individualism'] > 50:
                score += 0.1
            else:
                score -= 0.1
        
        # Power Distance
        if 'hierarchical' in product_concept.lower() or 'authority' in product_concept.lower():
            if dimensions['power_distance'] > 50:
                score += 0.1
            else:
                score -= 0.1
        
        # Uncertainty Avoidance
        if 'secure' in product_concept.lower() or 'safe' in product_concept.lower():
            if dimensions['uncertainty_avoidance'] > 50:
                score += 0.1
            else:
                score -= 0.05
        
        # Long-term Orientation
        if 'future' in product_concept.lower() or 'sustainable' in product_concept.lower():
            if dimensions['long_term_orientation'] > 50:
                score += 0.1
            else:
                score -= 0.05
        
        return max(0.0, min(1.0, score))
    
    def _generate_cultural_adaptations(self, product_concept: str, profile: CulturalProfile) -> Dict[str, Any]:
        """Generate cultural adaptation recommendations."""
        adaptations = {
            'communication_style': {},
            'business_practices': {},
            'marketing_approach': {},
            'product_features': {}
        }
        
        # Communication style adaptations
        if profile.communication_style['formality'] == 'high':
            adaptations['communication_style']['tone'] = 'formal_and_respectful'
            adaptations['communication_style']['addressing'] = 'use_titles_and_formal_names'
        else:
            adaptations['communication_style']['tone'] = 'casual_and_friendly'
            adaptations['communication_style']['addressing'] = 'use_first_names'
        
        # Business practices adaptations
        if profile.business_practices['decision_making'] == 'collective':
            adaptations['business_practices']['decision_process'] = 'involve_multiple_stakeholders'
            adaptations['business_practices']['approval_required'] = 'multiple_approvals'
        else:
            adaptations['business_practices']['decision_process'] = 'individual_decision_making'
            adaptations['business_practices']['approval_required'] = 'single_approval'
        
        # Marketing approach adaptations
        if profile.communication_style['relationship_focus'] == 'high':
            adaptations['marketing_approach']['focus'] = 'relationship_building'
            adaptations['marketing_approach']['channels'] = 'personal_networking_and_referrals'
        else:
            adaptations['marketing_approach']['focus'] = 'direct_value_proposition'
            adaptations['marketing_approach']['channels'] = 'digital_marketing_and_advertising'
        
        return adaptations
    
    def _assess_market_readiness(self, profile: CulturalProfile) -> Dict[str, Any]:
        """Assess market readiness for digital products."""
        scores = {
            'internet_infrastructure': profile.internet_penetration,
            'mobile_adoption': profile.mobile_penetration,
            'ecommerce_readiness': profile.ecommerce_adoption,
            'payment_system_maturity': len(profile.payment_preferences) / 5.0,
            'regulatory_clarity': 1.0 - (profile.regulatory_environment['complexity'] == 'high') * 0.3
        }
        
        overall_score = sum(scores.values()) / len(scores)
        
        return {
            'overall_score': overall_score,
            'component_scores': scores,
            'market_maturity': profile.market_maturity.value
        }
    
    def _generate_approach_recommendations(self, profile: CulturalProfile) -> Dict[str, Any]:
        """Generate market entry approach recommendations."""
        recommendations = {
            'entry_strategy': '',
            'partnership_approach': '',
            'localization_level': '',
            'timeline': '',
            'budget_allocation': {}
        }
        
        if profile.market_maturity == MarketMaturity.EMERGING:
            recommendations['entry_strategy'] = 'early_mover_advantage'
            recommendations['partnership_approach'] = 'local_partners_essential'
            recommendations['localization_level'] = 'high'
            recommendations['timeline'] = '6-12_months'
        elif profile.market_maturity == MarketMaturity.DEVELOPING:
            recommendations['entry_strategy'] = 'fast_follower'
            recommendations['partnership_approach'] = 'strategic_partnerships'
            recommendations['localization_level'] = 'medium'
            recommendations['timeline'] = '3-6_months'
        else:  # Mature or Saturated
            recommendations['entry_strategy'] = 'differentiation_focus'
            recommendations['partnership_approach'] = 'selective_partnerships'
            recommendations['localization_level'] = 'low'
            recommendations['timeline'] = '1-3_months'
        
        # Budget allocation based on market characteristics
        recommendations['budget_allocation'] = {
            'localization': 0.3 if recommendations['localization_level'] == 'high' else 0.1,
            'marketing': 0.4,
            'partnerships': 0.2 if 'partners' in recommendations['partnership_approach'] else 0.1,
            'compliance': 0.1 if profile.regulatory_environment['complexity'] == 'high' else 0.05,
            'operations': 0.2
        }
        
        return recommendations
    
    def _identify_risk_factors(self, profile: CulturalProfile) -> List[str]:
        """Identify potential risk factors for market entry."""
        risks = []
        
        if profile.regulatory_environment['complexity'] == 'high':
            risks.append('complex_regulatory_environment')
        
        if profile.internet_penetration < 0.7:
            risks.append('limited_internet_infrastructure')
        
        if profile.ecommerce_adoption < 0.6:
            risks.append('low_ecommerce_adoption')
        
        if len(profile.payment_preferences) < 2:
            risks.append('limited_payment_options')
        
        if profile.cultural_dimensions['uncertainty_avoidance'] > 70:
            risks.append('high_uncertainty_avoidance')
        
        return risks
    
    async def research_local_market(
        self,
        country_code: str,
        niche: str
    ) -> MarketOpportunity:
        """Research local market opportunities for a specific niche."""
        if country_code not in self.cultural_profiles:
            raise ValueError(f"No cultural profile for country {country_code}")
        
        profile = self.cultural_profiles[country_code]
        
        # Calculate market size based on population and adoption rates
        market_size = (
            profile.population * 
            profile.internet_penetration * 
            profile.ecommerce_adoption * 
            0.1  # Assume 10% of ecommerce users are in this niche
        )
        
        # Assess competition level based on market maturity
        competition_levels = {
            MarketMaturity.EMERGING: 'low',
            MarketMaturity.DEVELOPING: 'medium',
            MarketMaturity.MATURE: 'high',
            MarketMaturity.SATURATED: 'very_high'
        }
        
        competition_level = competition_levels[profile.market_maturity]
        
        # Identify entry barriers
        entry_barriers = []
        if profile.regulatory_environment['complexity'] == 'high':
            entry_barriers.append('regulatory_compliance')
        if profile.cultural_dimensions['power_distance'] > 70:
            entry_barriers.append('hierarchical_business_culture')
        if profile.ecommerce_adoption < 0.5:
            entry_barriers.append('low_digital_adoption')
        
        # Calculate growth potential
        growth_potential = (
            profile.internet_penetration * 
            profile.mobile_penetration * 
            (1 - profile.ecommerce_adoption)  # Room for growth
        )
        
        # Calculate cultural fit score
        cultural_fit_score = self._calculate_cultural_fit_score(niche, profile)
        
        # Assess regulatory complexity
        regulatory_complexity = 0.3 if profile.regulatory_environment['complexity'] == 'high' else 0.1
        
        # Generate recommended approach
        recommended_approach = self._generate_approach_recommendations(profile)
        
        # Estimate timeline
        timeline_map = {
            '6-12_months': 270,
            '3-6_months': 135,
            '1-3_months': 60
        }
        estimated_timeline = timeline_map.get(recommended_approach['timeline'], 90)
        
        # Identify risk factors
        risk_factors = self._identify_risk_factors(profile)
        
        # Calculate success probability
        success_probability = (
            cultural_fit_score * 
            growth_potential * 
            (1 - regulatory_complexity) * 
            (0.8 if competition_level in ['low', 'medium'] else 0.6)
        )
        
        opportunity = MarketOpportunity(
            country_code=country_code,
            niche=niche,
            market_size=market_size,
            competition_level=competition_level,
            entry_barriers=entry_barriers,
            growth_potential=growth_potential,
            cultural_fit_score=cultural_fit_score,
            regulatory_complexity=regulatory_complexity,
            recommended_approach=recommended_approach,
            estimated_timeline=estimated_timeline,
            risk_factors=risk_factors,
            success_probability=success_probability
        )
        
        self.market_opportunities[f"{country_code}_{niche}"] = opportunity
        
        return opportunity
    
    async def translate_content(
        self,
        content: str,
        target_language: str,
        cultural_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Translate content with cultural adaptation."""
        try:
            # Use simple translation function
            translated_text = translate_text(content, target_language)
            
            # Apply cultural adaptations if context provided
            if cultural_context:
                translated_text = self._apply_cultural_adaptations(
                    translated_text, target_language, cultural_context
                )
            
            return translated_text
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return content
    
    def _apply_cultural_adaptations(
        self,
        text: str,
        language: str,
        cultural_context: Dict[str, Any]
    ) -> str:
        """Apply cultural adaptations to translated text."""
        adapted_text = text
        
        # Apply formality adaptations
        if cultural_context.get('formality') == 'high':
            # Add formal elements based on language
            if language == 'es':
                adapted_text = f"Estimado cliente, {adapted_text}"
            elif language == 'zh':
                adapted_text = f"尊敬的客户，{adapted_text}"
        
        # Apply relationship focus adaptations
        if cultural_context.get('relationship_focus') == 'high':
            # Add relationship-building elements
            if language == 'es':
                adapted_text = f"Como parte de nuestra relación comercial, {adapted_text}"
        
        return adapted_text
    
    def get_cultural_profile(self, country_code: str) -> Optional[CulturalProfile]:
        """Get cultural profile for a country."""
        return self.cultural_profiles.get(country_code)
    
    def get_market_opportunity(self, country_code: str, niche: str) -> Optional[MarketOpportunity]:
        """Get market opportunity analysis."""
        return self.market_opportunities.get(f"{country_code}_{niche}")
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get agent status and statistics."""
        return {
            'agent_id': self.agent_id,
            'startup_id': self.startup_id,
            'cultural_profiles_count': len(self.cultural_profiles),
            'market_opportunities_count': len(self.market_opportunities),
            'supported_countries': list(self.cultural_profiles.keys()),
            'last_updated': datetime.utcnow().isoformat()
        }


# Global cultural intelligence agent instance
_cultural_agent: Optional[CulturalIntelligenceAgent] = None


def get_cultural_intelligence_agent(startup_id: str) -> CulturalIntelligenceAgent:
    """Get or create cultural intelligence agent instance."""
    global _cultural_agent
    if _cultural_agent is None or _cultural_agent.startup_id != startup_id:
        _cultural_agent = CulturalIntelligenceAgent(startup_id)
    return _cultural_agent 
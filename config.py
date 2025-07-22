"""Configuration management for AutoPilot Ventures platform."""

import os
from dataclasses import dataclass, field
from typing import List, Optional
from dotenv import load_dotenv
import base64
from cryptography.fernet import Fernet

# Load environment variables
load_dotenv()


@dataclass
class AIConfig:
    """AI configuration settings."""
    
    openai_key: str = field(
        default_factory=lambda: os.getenv('OPENAI_SECRET_KEY', '')
    )
    model_name: str = field(default='gpt-4')
    max_tokens: int = field(default=4000)
    temperature: float = field(default=0.7)
    serpapi_key: str = field(
        default_factory=lambda: os.getenv('SERPAPI_KEY', '')
    )
    rate_limit_per_minute: int = field(default=100)


@dataclass
class SecurityConfig:
    """Enhanced security configuration settings."""
    
    fernet_key: str = field(
        default_factory=lambda: os.getenv('FERNET_KEY', '')
    )
    allowed_domains: List[str] = field(
        default_factory=lambda: ['autopilotventures.com']
    )
    blacklisted_domains: List[str] = field(
        default_factory=lambda: ['malicious.com', 'spam.com']
    )
    content_safety_threshold: float = field(default=0.7)
    max_file_size: int = field(default=10 * 1024 * 1024)  # 10MB
    
    # New security settings
    secrets_manager_type: str = field(
        default_factory=lambda: os.getenv('SECRETS_MANAGER', 'env')
    )
    aws_region: str = field(
        default_factory=lambda: os.getenv('AWS_REGION', 'us-east-1')
    )
    azure_key_vault_url: str = field(
        default_factory=lambda: os.getenv('AZURE_KEY_VAULT_URL', '')
    )


@dataclass
class MonitoringConfig:
    """Monitoring and observability configuration."""
    
    prometheus_port: int = field(default=9090)
    metrics_enabled: bool = field(default=True)
    alerting_enabled: bool = field(default=True)
    alert_email: str = field(default='krystinvestments@gmail.com')
    slack_webhook_url: str = field(
        default_factory=lambda: os.getenv('SLACK_WEBHOOK_URL', '')
    )
    budget_alert_threshold: float = field(default=0.8)  # 80%


@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    
    url: str = field(
        default_factory=lambda: os.getenv(
            'DATABASE_URL', 'sqlite:///autopilot_ventures.db'
        )
    )
    backup_interval: int = field(default=24)  # hours
    max_startups: int = field(default=100)


@dataclass
class BudgetConfig:
    """Budget and pricing configuration."""
    
    initial_budget: float = field(default=500.0)
    cost_per_request: float = field(default=0.01)
    max_daily_spend: float = field(default=50.0)
    currency: str = field(default='USD')


@dataclass
class MultilingualConfig:
    """Multilingual support configuration."""
    
    supported_languages: List[str] = field(
        default_factory=lambda: [
            'en', 'es', 'zh', 'fr', 'de', 'ar', 'pt', 'hi', 'ru', 'ja'
        ]
    )
    default_language: str = field(default='en')
    translation_service: str = field(default='googletrans')


@dataclass
class StripeConfig:
    """Stripe payment processing configuration."""
    
    secret_key: str = field(
        default_factory=lambda: os.getenv('STRIPE_SECRET_KEY', '')
    )
    publishable_key: str = field(
        default_factory=lambda: os.getenv('STRIPE_PUBLISHABLE_KEY', '')
    )
    webhook_secret: str = field(
        default_factory=lambda: os.getenv('STRIPE_WEBHOOK_SECRET', '')
    )
    currency: str = field(default='usd')
    payment_methods: List[str] = field(
        default_factory=lambda: ['card', 'paypal', 'apple_pay', 'google_pay']
    )


@dataclass
class MessageBusConfig:
    """Agent message bus configuration."""
    
    max_message_queue_size: int = field(default=1000)
    message_ttl: int = field(default=300)  # 5 minutes
    context_ttl: int = field(default=3600)  # 1 hour
    max_concurrent_processing: int = field(default=10)
    enable_conflict_resolution: bool = field(default=True)
    enable_shared_context: bool = field(default=True)


@dataclass
class CulturalConfig:
    """Cultural intelligence configuration."""
    
    supported_countries: List[str] = field(
        default_factory=lambda: ['US', 'CN', 'ES', 'FR', 'DE', 'JP', 'BR', 'IN', 'RU', 'AE']
    )
    cultural_data_update_interval: int = field(default=30)  # days
    market_research_enabled: bool = field(default=True)
    translation_quality_threshold: float = field(default=0.8)


@dataclass
class Config:
    """Enhanced main configuration class."""
    
    ai: AIConfig = field(default_factory=AIConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    budget: BudgetConfig = field(default_factory=BudgetConfig)
    multilingual: MultilingualConfig = field(
        default_factory=MultilingualConfig
    )
    stripe: StripeConfig = field(default_factory=StripeConfig)
    message_bus: MessageBusConfig = field(default_factory=MessageBusConfig)
    cultural: CulturalConfig = field(default_factory=CulturalConfig)
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        self._validate_fernet_key()
        self._validate_openai_key()
        self._validate_stripe_config()
    
    def _validate_fernet_key(self):
        """Validate and fix Fernet key if needed."""
        if not self.security.fernet_key:
            # Generate a new key if none exists
            key = Fernet.generate_key()
            self.security.fernet_key = key.decode()
            return
        
        try:
            # Try to decode as base64
            if len(self.security.fernet_key) == 44:
                # Already base64 encoded
                Fernet(self.security.fernet_key.encode())
            else:
                # Try to encode as base64
                key_bytes = self.security.fernet_key.encode()
                if len(key_bytes) != 32:
                    raise ValueError("Invalid key length")
                self.security.fernet_key = base64.urlsafe_b64encode(
                    key_bytes
                ).decode()
        except Exception as e:
            # Generate new key if invalid
            print(f"Warning: Invalid Fernet key, generating new one: {e}")
            key = Fernet.generate_key()
            self.security.fernet_key = key.decode()
    
    def _validate_openai_key(self):
        """Validate OpenAI API key."""
        if not self.ai.openai_key:
            raise ValueError("OpenAI API key is required")
    
    def _validate_stripe_config(self):
        """Validate Stripe configuration."""
        if not self.stripe.secret_key:
            print("Warning: Stripe secret key not configured - payment processing disabled")
        if not self.stripe.webhook_secret:
            print("Warning: Stripe webhook secret not configured - webhook processing disabled")
    
    def __getattr__(self, name):
        """Backward compatibility for 'api' attribute."""
        if name == 'api':
            class APIConfig:
                def __init__(self, ai_config):
                    self.openai_api_key = ai_config.openai_key
                    self.model_name = ai_config.model_name
                    self.max_tokens = ai_config.max_tokens
                    self.temperature = ai_config.temperature
                    self.serpapi_key = ai_config.serpapi_key
            
            return APIConfig(self.ai)
        raise AttributeError(f"'{type(self).__name__}' has no attribute '{name}'")


# Global configuration instance
config = Config() 
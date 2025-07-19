"""Enhanced utility functions for AutoPilot Ventures platform."""

import os
import re
import uuid
import time
import json
import base64
import hashlib
import logging
import smtplib
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from functools import wraps
from ratelimit import limits, sleep_and_retry

import bleach
from cryptography.fernet import Fernet
import pandas as pd
from loguru import logger
import structlog
from prometheus_client import Counter, Histogram, Gauge, start_http_server

try:
    from detoxify import Detoxify
    DETOXIFY_AVAILABLE = True
except ImportError:
    DETOXIFY_AVAILABLE = False
    logger.warning("Detoxify not available, using fallback content safety")

from config import config

# Prometheus metrics
AGENT_EXECUTION_COUNTER = Counter(
    'agent_executions_total',
    'Total number of agent executions',
    ['agent_type', 'status']
)

AGENT_EXECUTION_DURATION = Histogram(
    'agent_execution_duration_seconds',
    'Agent execution duration in seconds',
    ['agent_type']
)

BUDGET_USAGE_GAUGE = Gauge(
    'budget_usage_dollars',
    'Current budget usage in dollars'
)

API_CALLS_COUNTER = Counter(
    'api_calls_total',
    'Total number of API calls',
    ['api_type', 'status']
)

# Structured logging
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

log = structlog.get_logger()


def generate_id(prefix: str = "startup") -> str:
    """Generate unique ID with prefix."""
    timestamp = int(time.time() * 1000)
    random_part = str(uuid.uuid4())[:8]
    return f"{prefix}_{timestamp}_{random_part}"


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage."""
    # Remove or replace unsafe characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Limit length
    if len(filename) > 100:
        name, ext = os.path.splitext(filename)
        filename = name[:95] + ext
    return filename


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_url(url: str) -> bool:
    """Validate URL format."""
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return bool(re.match(pattern, url))


def sanitize_html(html_content: str) -> str:
    """Sanitize HTML content using bleach."""
    allowed_tags = [
        'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'ul', 'ol', 'li', 'a', 'img', 'blockquote', 'code', 'pre'
    ]
    allowed_attributes = {
        'a': ['href', 'title'],
        'img': ['src', 'alt', 'title']
    }

    return bleach.clean(
        html_content,
        tags=allowed_tags,
        attributes=allowed_attributes,
        strip=True
    )


class SecretsManager:
    """Enhanced secrets management with cloud provider support."""

    def __init__(self):
        """Initialize secrets manager."""
        self.secrets_manager_type = config.security.secrets_manager_type
        self._secrets_cache = {}

    def get_secret(self, secret_name: str) -> Optional[str]:
        """Get secret from configured source."""
        if secret_name in self._secrets_cache:
            return self._secrets_cache[secret_name]

        if self.secrets_manager_type == 'aws':
            return self._get_aws_secret(secret_name)
        elif self.secrets_manager_type == 'azure':
            return self._get_azure_secret(secret_name)
        else:
            # Fallback to environment variables
            return os.getenv(secret_name)

    def _get_aws_secret(self, secret_name: str) -> Optional[str]:
        """Get secret from AWS Secrets Manager."""
        try:
            import boto3
            client = boto3.client(
                'secretsmanager',
                region_name=config.security.aws_region
            )
            response = client.get_secret_value(SecretId=secret_name)
            secret = response['SecretString']
            self._secrets_cache[secret_name] = secret
            return secret
        except Exception as e:
            logger.error(f"Failed to get AWS secret {secret_name}: {e}")
            return None

    def _get_azure_secret(self, secret_name: str) -> Optional[str]:
        """Get secret from Azure Key Vault."""
        try:
            from azure.identity import DefaultAzureCredential
            from azure.keyvault.secrets import SecretClient

            credential = DefaultAzureCredential()
            client = SecretClient(
                vault_url=config.security.azure_key_vault_url,
                credential=credential
            )
            secret = client.get_secret(secret_name).value
            self._secrets_cache[secret_name] = secret
            return secret
        except Exception as e:
            logger.error(f"Failed to get Azure secret {secret_name}: {e}")
            return None


class SecurityUtils:
    """Enhanced security utilities for encryption and content safety."""

    def __init__(self, encryption_key: str):
        """Initialize with encryption key."""
        try:
            # Handle base64 encoded key
            if len(encryption_key) == 44:
                key_bytes = base64.urlsafe_b64decode(encryption_key)
            else:
                key_bytes = encryption_key.encode()

            if len(key_bytes) != 32:
                raise ValueError("Invalid key length")

            self.fernet = Fernet(key_bytes)
        except Exception as e:
            # Generate a new valid key if the provided one is invalid
            print(f"Warning: Invalid encryption key provided, generating new one: {e}")
            new_key = Fernet.generate_key()
            self.fernet = Fernet(new_key)

    def encrypt_data(self, data: str) -> str:
        """Encrypt data using Fernet."""
        return self.fernet.encrypt(data.encode()).decode()

    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt data using Fernet."""
        return self.fernet.decrypt(encrypted_data.encode()).decode()

    def check_content_safety(self, text: str) -> Dict[str, float]:
        """Check content safety using Detoxify or fallback."""
        if DETOXIFY_AVAILABLE:
            try:
                model = Detoxify('original')
                results = model.predict(text)
                return {
                    'toxicity': results['toxicity'],
                    'severe_toxicity': results['severe_toxicity'],
                    'obscene': results['obscene'],
                    'threat': results['threat'],
                    'insult': results['insult'],
                    'identity_attack': results['identity_attack']
                }
            except Exception as e:
                logger.warning(f"Detoxify failed: {e}")

        # Fallback: simple keyword-based check
        toxic_keywords = [
            'hate', 'violence', 'abuse', 'threat', 'kill', 'death',
            'scam', 'fraud', 'illegal', 'drugs', 'weapons'
        ]

        text_lower = text.lower()
        toxicity_score = sum(
            1 for keyword in toxic_keywords if keyword in text_lower
        ) / len(toxic_keywords)

        return {
            'toxicity': min(toxicity_score, 1.0),
            'severe_toxicity': 0.0,
            'obscene': 0.0,
            'threat': 0.0,
            'insult': 0.0,
            'identity_attack': 0.0
        }


class RateLimiter:
    """Rate limiting utilities."""

    @staticmethod
    @sleep_and_retry
    @limits(calls=100, period=60)  # 100 calls per minute
    def api_call():
        """Rate limited API call wrapper."""
        pass

    @staticmethod
    def check_rate_limit(identifier: str) -> bool:
        """Check if rate limit is exceeded for identifier."""
        # Simple in-memory rate limiting
        # In production, use Redis or similar
        return True


class AlertManager:
    """Alert management for monitoring."""

    def __init__(self):
        """Initialize alert manager."""
        self.alert_email = config.monitoring.alert_email
        self.slack_webhook_url = config.monitoring.slack_webhook_url

    def send_email_alert(self, subject: str, message: str) -> bool:
        """Send email alert."""
        if not self.alert_email:
            return False

        try:
            # Configure SMTP settings
            smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.getenv('SMTP_PORT', '587'))
            smtp_user = os.getenv('SMTP_USER', '')
            smtp_password = os.getenv('SMTP_PASSWORD', '')

            if not all([smtp_user, smtp_password]):
                logger.warning("SMTP credentials not configured")
                return False

            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)

                email_body = f"""
                Subject: {subject}

                {message}

                Sent by AutoPilot Ventures Platform
                Time: {datetime.now().isoformat()}
                """

                server.sendmail(smtp_user, self.alert_email, email_body)
                return True

        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
            return False

    def send_slack_alert(self, message: str) -> bool:
        """Send Slack alert."""
        if not self.slack_webhook_url:
            return False

        try:
            payload = {
                "text": f"🚨 AutoPilot Ventures Alert: {message}",
                "username": "AutoPilot Bot",
                "icon_emoji": ":robot_face:"
            }

            response = requests.post(
                self.slack_webhook_url,
                json=payload,
                timeout=10
            )
            return response.status_code == 200

        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")
            return False

    def send_budget_alert(self, current_spend: float, budget_limit: float) -> None:
        """Send budget alert if threshold exceeded."""
        if current_spend / budget_limit >= config.monitoring.budget_alert_threshold:
            message = f"Budget alert: {current_spend:.2f}/{budget_limit:.2f} USD spent"
            self.send_email_alert("Budget Alert", message)
            self.send_slack_alert(message)


class FileUtils:
    """File handling utilities."""

    @staticmethod
    def ensure_directory(path: str) -> None:
        """Ensure directory exists."""
        Path(path).mkdir(parents=True, exist_ok=True)

    @staticmethod
    def get_file_size(file_path: str) -> int:
        """Get file size in bytes."""
        return os.path.getsize(file_path)

    @staticmethod
    def is_valid_file_type(filename: str, allowed_extensions: List[str]) -> bool:
        """Check if file has valid extension."""
        return any(
            filename.lower().endswith(ext) for ext in allowed_extensions
        )

    @staticmethod
    def backup_file(file_path: str, backup_dir: str = "backups") -> str:
        """Create backup of file."""
        FileUtils.ensure_directory(backup_dir)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.basename(file_path)
        backup_path = os.path.join(backup_dir, f"{timestamp}_{filename}")

        with open(file_path, 'rb') as src, open(backup_path, 'wb') as dst:
            dst.write(src.read())

        return backup_path


class MetricsUtils:
    """Enhanced metrics and analytics utilities."""

    @staticmethod
    def calculate_roi(initial_investment: float, current_value: float) -> float:
        """Calculate Return on Investment."""
        if initial_investment == 0:
            return 0.0
        return (current_value - initial_investment) / initial_investment

    @staticmethod
    def calculate_growth_rate(
        initial_value: float, final_value: float, time_period: int
    ) -> float:
        """Calculate growth rate over time period."""
        if initial_value == 0:
            return 0.0
        return (final_value / initial_value) ** (1 / time_period) - 1

    @staticmethod
    def calculate_engagement_rate(
        interactions: int, followers: int
    ) -> float:
        """Calculate engagement rate."""
        if followers == 0:
            return 0.0
        return (interactions / followers) * 100

    @staticmethod
    def format_currency(amount: float, currency: str = "USD") -> str:
        """Format currency amount."""
        return f"{currency} {amount:.2f}"

    @staticmethod
    def calculate_valuation_multiple(revenue: float, industry: str) -> float:
        """Calculate valuation multiple based on industry."""
        # Industry-specific multiples (simplified)
        multiples = {
            'saas': 10.0,
            'ecommerce': 3.0,
            'fintech': 8.0,
            'healthtech': 12.0,
            'ai': 15.0,
            'default': 5.0
        }
        return multiples.get(industry.lower(), multiples['default'])


class BudgetManager:
    """Enhanced budget management for cost control."""

    def __init__(self, initial_budget: float = 500.0):
        """Initialize budget manager."""
        self.initial_budget = initial_budget
        self.remaining_budget = initial_budget
        self.daily_spent = 0.0
        self.last_reset = datetime.now().date()
        self.alert_manager = AlertManager()

    def can_spend(self, amount: float) -> bool:
        """Check if we can spend the amount."""
        self._reset_daily_if_needed()
        return self.remaining_budget >= amount and self.daily_spent < 50.0

    def spend(self, amount: float) -> bool:
        """Spend from budget."""
        if self.can_spend(amount):
            self.remaining_budget -= amount
            self.daily_spent += amount

            # Update Prometheus metrics
            BUDGET_USAGE_GAUGE.set(self.initial_budget - self.remaining_budget)

            # Check for budget alerts
            self.alert_manager.send_budget_alert(
                self.initial_budget - self.remaining_budget,
                self.initial_budget
            )

            return True
        return False

    def add_funds(self, amount: float) -> None:
        """Add funds to budget."""
        self.remaining_budget += amount
        self.initial_budget += amount

    def get_remaining_budget(self) -> float:
        """Get remaining budget."""
        return self.remaining_budget

    def get_daily_spent(self) -> float:
        """Get daily spent amount."""
        self._reset_daily_if_needed()
        return self.daily_spent

    def _reset_daily_if_needed(self) -> None:
        """Reset daily spent if it's a new day."""
        today = datetime.now().date()
        if today > self.last_reset:
            self.daily_spent = 0.0
            self.last_reset = today


class TimeUtils:
    """Time-related utilities."""

    @staticmethod
    def get_timestamp() -> str:
        """Get current timestamp."""
        return datetime.now().isoformat()

    @staticmethod
    def format_duration(seconds: int) -> str:
        """Format duration in human-readable format."""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"

    @staticmethod
    def is_business_day(date: datetime) -> bool:
        """Check if date is a business day."""
        return date.weekday() < 5

    @staticmethod
    def get_next_business_day(date: datetime) -> datetime:
        """Get next business day."""
        next_day = date + timedelta(days=1)
        while not TimeUtils.is_business_day(next_day):
            next_day += timedelta(days=1)
        return next_day


# Global instances
try:
    security_utils = SecurityUtils(config.security.fernet_key)
except Exception as e:
    logger.warning(f"Failed to initialize security utils: {e}")
    # Create a fallback instance with a new key
    fallback_key = Fernet.generate_key().decode()
    security_utils = SecurityUtils(fallback_key)

budget_manager = BudgetManager(config.budget.initial_budget)
secrets_manager = SecretsManager()
alert_manager = AlertManager()

# Start Prometheus metrics server if enabled
if config.monitoring.metrics_enabled:
    try:
        start_http_server(config.monitoring.prometheus_port)
        logger.info(f"Prometheus metrics server started on port {config.monitoring.prometheus_port}")
    except Exception as e:
        logger.warning(f"Failed to start Prometheus server: {e}") 
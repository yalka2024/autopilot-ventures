#!/usr/bin/env python3
"""
Customer Acquisition Configuration
API keys and settings for real customer acquisition
"""

import os
from typing import Dict, List

class CustomerAcquisitionConfig:
    """Configuration for customer acquisition system"""
    
    # API Keys (replace with your actual keys)
    API_KEYS = {
        # Google Analytics 4
        "google_analytics": {
            "tracking_id": os.getenv("GOOGLE_ANALYTICS_TRACKING_ID", "GA4-XXXXXXXX"),
            "measurement_id": os.getenv("GOOGLE_ANALYTICS_MEASUREMENT_ID", "G-XXXXXXXX"),
            "api_secret": os.getenv("GOOGLE_ANALYTICS_API_SECRET", "")
        },
        
        # Email Marketing
        "mailchimp": {
            "api_key": os.getenv("MAILCHIMP_API_KEY", ""),
            "server_prefix": os.getenv("MAILCHIMP_SERVER_PREFIX", "us1"),
            "audience_id": os.getenv("MAILCHIMP_AUDIENCE_ID", "")
        },
        
        "convertkit": {
            "api_key": os.getenv("CONVERTKIT_API_KEY", ""),
            "form_id": os.getenv("CONVERTKIT_FORM_ID", "")
        },
        
        # Social Media
        "buffer": {
            "access_token": os.getenv("BUFFER_ACCESS_TOKEN", ""),
            "client_id": os.getenv("BUFFER_CLIENT_ID", ""),
            "client_secret": os.getenv("BUFFER_CLIENT_SECRET", "")
        },
        
        "hootsuite": {
            "api_key": os.getenv("HOOTSUITE_API_KEY", ""),
            "access_token": os.getenv("HOOTSUITE_ACCESS_TOKEN", "")
        },
        
        # Paid Advertising
        "google_ads": {
            "client_id": os.getenv("GOOGLE_ADS_CLIENT_ID", ""),
            "client_secret": os.getenv("GOOGLE_ADS_CLIENT_SECRET", ""),
            "developer_token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN", ""),
            "customer_id": os.getenv("GOOGLE_ADS_CUSTOMER_ID", "")
        },
        
        "facebook_ads": {
            "access_token": os.getenv("FACEBOOK_ADS_ACCESS_TOKEN", ""),
            "app_id": os.getenv("FACEBOOK_ADS_APP_ID", ""),
            "app_secret": os.getenv("FACEBOOK_ADS_APP_SECRET", ""),
            "ad_account_id": os.getenv("FACEBOOK_ADS_ACCOUNT_ID", "")
        },
        
        # Analytics & Tracking
        "hotjar": {
            "site_id": os.getenv("HOTJAR_SITE_ID", ""),
            "api_key": os.getenv("HOTJAR_API_KEY", "")
        },
        
        "mixpanel": {
            "project_token": os.getenv("MIXPANEL_PROJECT_TOKEN", ""),
            "api_secret": os.getenv("MIXPANEL_API_SECRET", "")
        },
        
        # SEO Tools
        "ahrefs": {
            "api_key": os.getenv("AHREFS_API_KEY", ""),
            "base_url": "https://api.ahrefs.com/v3"
        },
        
        "semrush": {
            "api_key": os.getenv("SEMRUSH_API_KEY", ""),
            "base_url": "https://api.semrush.com"
        }
    }
    
    # Campaign Settings
    CAMPAIGN_SETTINGS = {
        "default_budget": 100.0,
        "max_budget_per_campaign": 500.0,
        "target_cpa": 25.0,
        "target_roas": 3.0,
        "conversion_rate_target": 0.02,  # 2%
        "lead_quality_threshold": 15.0
    }
    
    # Content Settings
    CONTENT_SETTINGS = {
        "blog_posts_per_week": 3,
        "social_posts_per_day": 2,
        "email_newsletters_per_week": 1,
        "landing_pages_per_campaign": 1,
        "seo_keywords_per_niche": 10
    }
    
    # Targeting Settings
    TARGETING_SETTINGS = {
        "age_range": {"min": 25, "max": 55},
        "income_levels": ["middle", "upper_middle", "high"],
        "interests": ["business", "entrepreneurship", "technology", "marketing"],
        "behaviors": ["small_business_owners", "entrepreneurs", "digital_natives"],
        "locations": ["United States", "Canada", "United Kingdom", "Australia"]
    }
    
    # Email Sequences
    EMAIL_SEQUENCES = {
        "welcome_series": {
            "name": "Welcome Series",
            "emails": [
                {"day": 0, "subject": "Welcome to {business_name}!", "type": "welcome"},
                {"day": 2, "subject": "Your Success Roadmap", "type": "educational"},
                {"day": 5, "subject": "Customer Success Stories", "type": "social_proof"},
                {"day": 7, "subject": "Special Offer Just for You", "type": "promotional"}
            ]
        },
        "nurture_series": {
            "name": "Nurture Series",
            "emails": [
                {"day": 0, "subject": "5 Common {niche} Mistakes", "type": "educational"},
                {"day": 3, "subject": "The Ultimate {niche} Guide", "type": "educational"},
                {"day": 7, "subject": "How Top Performers Succeed", "type": "case_study"},
                {"day": 10, "subject": "Ready to Get Started?", "type": "cta"}
            ]
        },
        "reengagement": {
            "name": "Re-engagement Series",
            "emails": [
                {"day": 0, "subject": "We Miss You!", "type": "reengagement"},
                {"day": 3, "subject": "What's New at {business_name}", "type": "update"},
                {"day": 7, "subject": "Special Comeback Offer", "type": "promotional"}
            ]
        }
    }
    
    # Social Media Templates
    SOCIAL_MEDIA_TEMPLATES = {
        "linkedin": {
            "post_length": 1300,
            "hashtags_per_post": 3,
            "posting_frequency": "daily",
            "best_times": ["9:00", "12:00", "17:00"]
        },
        "twitter": {
            "post_length": 280,
            "hashtags_per_post": 2,
            "posting_frequency": "3x_daily",
            "best_times": ["8:00", "12:00", "17:00", "20:00"]
        },
        "facebook": {
            "post_length": 400,
            "hashtags_per_post": 2,
            "posting_frequency": "daily",
            "best_times": ["9:00", "15:00", "19:00"]
        },
        "instagram": {
            "post_length": 2200,
            "hashtags_per_post": 15,
            "posting_frequency": "daily",
            "best_times": ["11:00", "15:00", "19:00"]
        }
    }
    
    # Lead Scoring Criteria
    LEAD_SCORING = {
        "email_domain": {
            "gmail.com": 5,
            "yahoo.com": 3,
            "outlook.com": 4,
            "company.com": 15,
            "enterprise.com": 20
        },
        "source": {
            "organic_search": 15,
            "paid_advertising": 12,
            "social_media": 10,
            "email": 8,
            "referral": 20,
            "direct": 5
        },
        "engagement": {
            "page_views": {"1-2": 5, "3-5": 10, "6+": 15},
            "time_on_site": {"0-30s": 0, "30s-2m": 5, "2m-5m": 10, "5m+": 15},
            "form_submissions": 20,
            "email_opens": 5,
            "email_clicks": 10
        },
        "company_size": {
            "1-10": 5,
            "11-50": 10,
            "51-200": 15,
            "201-1000": 20,
            "1000+": 25
        }
    }
    
    @classmethod
    def get_api_key(cls, service: str, key_name: str = None) -> str:
        """Get API key for a service"""
        if service in cls.API_KEYS:
            if key_name:
                return cls.API_KEYS[service].get(key_name, "")
            return cls.API_KEYS[service]
        return ""
    
    @classmethod
    def is_configured(cls, service: str) -> bool:
        """Check if a service is properly configured"""
        if service not in cls.API_KEYS:
            return False
        
        service_config = cls.API_KEYS[service]
        if isinstance(service_config, dict):
            # Check if at least one key is configured
            return any(value for value in service_config.values())
        return bool(service_config)
    
    @classmethod
    def get_configured_services(cls) -> List[str]:
        """Get list of configured services"""
        return [service for service in cls.API_KEYS.keys() if cls.is_configured(service)]

# Environment variables template
ENV_TEMPLATE = """
# Customer Acquisition API Keys
# Copy these to your .env file and fill in your actual keys

# Google Analytics 4
GOOGLE_ANALYTICS_TRACKING_ID=GA4-XXXXXXXX
GOOGLE_ANALYTICS_MEASUREMENT_ID=G-XXXXXXXX
GOOGLE_ANALYTICS_API_SECRET=your_api_secret_here

# Email Marketing
MAILCHIMP_API_KEY=your_mailchimp_api_key_here
MAILCHIMP_SERVER_PREFIX=us1
MAILCHIMP_AUDIENCE_ID=your_audience_id_here

CONVERTKIT_API_KEY=your_convertkit_api_key_here
CONVERTKIT_FORM_ID=your_form_id_here

# Social Media
BUFFER_ACCESS_TOKEN=your_buffer_access_token_here
BUFFER_CLIENT_ID=your_buffer_client_id_here
BUFFER_CLIENT_SECRET=your_buffer_client_secret_here

HOOTSUITE_API_KEY=your_hootsuite_api_key_here
HOOTSUITE_ACCESS_TOKEN=your_hootsuite_access_token_here

# Paid Advertising
GOOGLE_ADS_CLIENT_ID=your_google_ads_client_id_here
GOOGLE_ADS_CLIENT_SECRET=your_google_ads_client_secret_here
GOOGLE_ADS_DEVELOPER_TOKEN=your_developer_token_here
GOOGLE_ADS_CUSTOMER_ID=your_customer_id_here

FACEBOOK_ADS_ACCESS_TOKEN=your_facebook_ads_access_token_here
FACEBOOK_ADS_APP_ID=your_app_id_here
FACEBOOK_ADS_APP_SECRET=your_app_secret_here
FACEBOOK_ADS_ACCOUNT_ID=your_ad_account_id_here

# Analytics & Tracking
HOTJAR_SITE_ID=your_hotjar_site_id_here
HOTJAR_API_KEY=your_hotjar_api_key_here

MIXPANEL_PROJECT_TOKEN=your_mixpanel_project_token_here
MIXPANEL_API_SECRET=your_mixpanel_api_secret_here

# SEO Tools
AHREFS_API_KEY=your_ahrefs_api_key_here
SEMRUSH_API_KEY=your_semrush_api_key_here
"""

def create_env_template():
    """Create .env template file"""
    with open(".env.template", "w") as f:
        f.write(ENV_TEMPLATE)
    print("✅ Created .env.template file")
    print("💡 Copy this to .env and fill in your actual API keys")

if __name__ == "__main__":
    create_env_template()
    
    print("🔧 Customer Acquisition Configuration")
    print("=" * 40)
    
    config = CustomerAcquisitionConfig()
    configured_services = config.get_configured_services()
    
    print(f"✅ Configured services: {len(configured_services)}")
    for service in configured_services:
        print(f"   • {service}")
    
    if not configured_services:
        print("❌ No services configured")
        print("💡 Set up your API keys in .env file") 
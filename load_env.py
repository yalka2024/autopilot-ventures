#!/usr/bin/env python3
"""
Environment Configuration Loader for AutoPilot Ventures
Loads API keys and configuration from .env file
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def load_environment():
    """Load environment variables from .env file"""
    
    # Find .env file
    env_path = Path('.env')
    if not env_path.exists():
        print("❌ .env file not found!")
        print("Please create a .env file with your API keys:")
        print("""
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Stripe Configuration  
STRIPE_SECRET_KEY=sk_test_your_stripe_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here

# Gumroad Configuration
GUMROAD_API_KEY=your_gumroad_api_key_here

# Alerting Configuration
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/your/webhook/url
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your/webhook/url

# Database Configuration
DATABASE_URL=postgresql://user:pass@host:port/db

# Other Configuration
FERNET_KEY=your_fernet_key_here
ENVIRONMENT=production
        """)
        return False
    
    # Load environment variables
    load_dotenv(env_path)
    
    # Check required environment variables (using existing .env variable names)
    required_vars = [
        'OPENAI_SECRET_KEY',  # Changed from OPENAI_API_KEY
        'STRIPE_SECRET_KEY', 
        'STRIPE_PUBLISHABLE_KEY'
        # Removed GUMROAD_API_KEY as it's not in the existing .env
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ Environment variables loaded successfully!")
    print(f"🔑 OpenAI API Key: {os.getenv('OPENAI_SECRET_KEY', 'Not set')[:20]}...")
    print(f"💳 Stripe Secret Key: {os.getenv('STRIPE_SECRET_KEY', 'Not set')[:20]}...")
    print(f"🔍 SerpAPI Key: {os.getenv('SERPAPI_KEY', 'Not set')[:20]}...")
    
    return True

def get_api_keys():
    """Get API keys for use in the application"""
    if not load_environment():
        return None
    
    return {
        'openai_api_key': os.getenv('OPENAI_SECRET_KEY'),
        'stripe_secret_key': os.getenv('STRIPE_SECRET_KEY'),
        'stripe_publishable_key': os.getenv('STRIPE_PUBLISHABLE_KEY'),
        'serpapi_key': os.getenv('SERPAPI_KEY'),
        'fernet_key': os.getenv('FERNET_KEY'),
        'jwt_secret': os.getenv('JWT_SECRET'),
        'environment': os.getenv('ENVIRONMENT', 'production')
    }

if __name__ == "__main__":
    if load_environment():
        print("🚀 Environment ready for AutoPilot Ventures!")
        sys.exit(0)
    else:
        print("❌ Environment configuration failed!")
        sys.exit(1) 
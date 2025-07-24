#!/usr/bin/env python3
"""
AutoPilot Ventures - Environment Setup Script
Helps users configure their environment variables for production deployment
"""

import os
import sys
from pathlib import Path

def create_env_file():
    """Create .env file from template"""
    
    # Check if .env already exists
    if Path('.env').exists():
        print("⚠️  .env file already exists!")
        response = input("Do you want to overwrite it? (y/N): ")
        if response.lower() != 'y':
            print("Setup cancelled.")
            return False
    
    # Read template
    template_path = Path('env.template')
    if not template_path.exists():
        print("❌ env.template not found!")
        return False
    
    with open(template_path, 'r') as f:
        template_content = f.read()
    
    print("🚀 AutoPilot Ventures Environment Setup")
    print("=" * 50)
    print("Please provide your API keys and configuration:")
    print()
    
    # Get user input for required values
    config = {}
    
    print("🔑 OpenAI API Key (required):")
    config['OPENAI_API_KEY'] = input("Enter your OpenAI API key: ").strip()
    
    print("\n💳 Stripe Configuration:")
    config['STRIPE_SECRET_KEY'] = input("Enter your Stripe Secret Key (sk_test_...): ").strip()
    config['STRIPE_PUBLISHABLE_KEY'] = input("Enter your Stripe Publishable Key (pk_test_...): ").strip()
    config['STRIPE_WEBHOOK_SECRET'] = input("Enter your Stripe Webhook Secret (optional): ").strip()
    
    print("\n🛒 Gumroad Configuration:")
    config['GUMROAD_API_KEY'] = input("Enter your Gumroad API Key: ").strip()
    
    print("\n🔔 Alerting Configuration (optional):")
    config['SLACK_WEBHOOK_URL'] = input("Enter your Slack Webhook URL (optional): ").strip()
    config['DISCORD_WEBHOOK_URL'] = input("Enter your Discord Webhook URL (optional): ").strip()
    
    print("\n🗄️ Database Configuration:")
    config['DATABASE_URL'] = input("Enter your Database URL (optional, default: SQLite): ").strip()
    
    print("\n🔐 Security Configuration:")
    config['FERNET_KEY'] = input("Enter your Fernet Key (optional, will generate if empty): ").strip()
    
    # Generate Fernet key if not provided
    if not config['FERNET_KEY']:
        from cryptography.fernet import Fernet
        config['FERNET_KEY'] = Fernet.generate_key().decode()
        print(f"✅ Generated Fernet key: {config['FERNET_KEY'][:20]}...")
    
    # Replace placeholders in template
    env_content = template_content
    for key, value in config.items():
        if value:  # Only replace if value is provided
            env_content = env_content.replace(f"{key}=your_{key.lower()}_here", f"{key}={value}")
            env_content = env_content.replace(f"{key}=sk-your-openai-api-key-here", f"{key}={value}")
            env_content = env_content.replace(f"{key}=sk_test_your_stripe_secret_key_here", f"{key}={value}")
            env_content = env_content.replace(f"{key}=pk_test_your_stripe_publishable_key_here", f"{key}={value}")
            env_content = env_content.replace(f"{key}=whsec_your_stripe_webhook_secret_here", f"{key}={value}")
            env_content = env_content.replace(f"{key}=your_gumroad_api_key_here", f"{key}={value}")
            env_content = env_content.replace(f"{key}=https://hooks.slack.com/services/your/slack/webhook/url", f"{key}={value}")
            env_content = env_content.replace(f"{key}=https://discord.com/api/webhooks/your/discord/webhook/url", f"{key}={value}")
            env_content = env_content.replace(f"{key}=postgresql://username:password@host:port/database_name", f"{key}={value}")
            env_content = env_content.replace(f"{key}=your_fernet_encryption_key_here", f"{key}={value}")
    
    # Write .env file
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("\n✅ .env file created successfully!")
    print("🔒 Remember to keep your API keys secure and never commit them to version control.")
    
    return True

def validate_environment():
    """Validate the environment configuration"""
    print("\n🔍 Validating environment configuration...")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check required variables
    required_vars = [
        'OPENAI_API_KEY',
        'STRIPE_SECRET_KEY',
        'STRIPE_PUBLISHABLE_KEY',
        'GUMROAD_API_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ All required environment variables are set!")
    print(f"🔑 OpenAI API Key: {os.getenv('OPENAI_API_KEY')[:20]}...")
    print(f"💳 Stripe Secret Key: {os.getenv('STRIPE_SECRET_KEY')[:20]}...")
    print(f"🛒 Gumroad API Key: {os.getenv('GUMROAD_API_KEY')[:20]}...")
    
    return True

def main():
    """Main setup function"""
    print("🚀 AutoPilot Ventures Environment Setup")
    print("=" * 50)
    
    # Check if .env exists
    if Path('.env').exists():
        print("📁 .env file found!")
        if validate_environment():
            print("\n✅ Environment is properly configured!")
            return True
        else:
            print("\n❌ Environment validation failed!")
            response = input("Do you want to reconfigure? (y/N): ")
            if response.lower() != 'y':
                return False
    
    # Create new .env file
    if create_env_file():
        return validate_environment()
    
    return False

if __name__ == "__main__":
    if main():
        print("\n🎉 Environment setup completed successfully!")
        print("🚀 You can now run the AutoPilot Ventures platform!")
        sys.exit(0)
    else:
        print("\n❌ Environment setup failed!")
        sys.exit(1) 
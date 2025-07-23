#!/usr/bin/env python3
"""
Fix Critical Components Script
Helps set up missing Stripe and Redis components for AutoPilot Ventures
"""

import os
import sys
import subprocess
import requests
from pathlib import Path

def check_stripe_config():
    """Check if Stripe is properly configured"""
    print("🔍 Checking Stripe configuration...")
    
    stripe_key = os.getenv('STRIPE_SECRET_KEY')
    if not stripe_key or stripe_key == 'sk_test_your_stripe_secret_key_here':
        print("❌ Stripe not configured!")
        print("\n📋 To fix Stripe:")
        print("1. Go to https://dashboard.stripe.com/")
        print("2. Create an account and get your API keys")
        print("3. Add to your .env file:")
        print("   STRIPE_SECRET_KEY=sk_test_your_actual_key")
        print("   STRIPE_PUBLISHABLE_KEY=pk_test_your_actual_key")
        print("   STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret")
        return False
    else:
        print("✅ Stripe configured!")
        return True

def check_redis_connection():
    """Check if Redis is running"""
    print("\n🔍 Checking Redis connection...")
    
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0, socket_connect_timeout=2)
        r.ping()
        print("✅ Redis is running!")
        return True
    except Exception as e:
        print("❌ Redis not running!")
        print(f"Error: {e}")
        print("\n📋 To fix Redis:")
        print("Option 1 - Docker (Recommended):")
        print("   docker run -d -p 6379:6379 redis:latest")
        print("\nOption 2 - Windows Installation:")
        print("   Download from: https://github.com/microsoftarchive/redis/releases")
        print("\nOption 3 - Redis Cloud (Free):")
        print("   Sign up at: https://redis.com/try-free/")
        return False

def check_env_file():
    """Check if .env file exists and has required variables"""
    print("\n🔍 Checking .env file...")
    
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ .env file not found!")
        print("\n📋 To create .env file:")
        print("1. Copy env.example to .env:")
        print("   cp env.example .env")
        print("2. Fill in your API keys:")
        print("   OPENAI_SECRET_KEY=sk-your-openai-key")
        print("   STRIPE_SECRET_KEY=sk-your-stripe-key")
        return False
    else:
        print("✅ .env file exists!")
        
        # Check for required variables
        required_vars = ['OPENAI_SECRET_KEY', 'STRIPE_SECRET_KEY']
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"⚠️  Missing variables: {', '.join(missing_vars)}")
            return False
        else:
            print("✅ All required variables configured!")
            return True

def install_redis_docker():
    """Install Redis using Docker"""
    print("\n🐳 Installing Redis with Docker...")
    
    try:
        # Check if Docker is installed
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Docker not installed!")
            print("Please install Docker Desktop from: https://www.docker.com/products/docker-desktop")
            return False
        
        # Check if Redis container is already running
        result = subprocess.run(['docker', 'ps', '--filter', 'name=redis'], capture_output=True, text=True)
        if 'redis' in result.stdout:
            print("✅ Redis container already running!")
            return True
        
        # Start Redis container
        print("Starting Redis container...")
        result = subprocess.run([
            'docker', 'run', '-d', 
            '--name', 'autopilot-redis',
            '-p', '6379:6379',
            'redis:latest'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Redis container started successfully!")
            return True
        else:
            print(f"❌ Failed to start Redis: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error installing Redis: {e}")
        return False

def create_env_template():
    """Create a template .env file"""
    print("\n📝 Creating .env template...")
    
    env_content = """# AutoPilot Ventures - Environment Configuration
# Copy this file to .env and fill in your actual values

# =============================================================================
# AI & API KEYS
# =============================================================================

# OpenAI API (Required)
OPENAI_SECRET_KEY=your_openai_api_key_here

# =============================================================================
# PAYMENT PROCESSING
# =============================================================================

# Stripe API (Required for monetization)
STRIPE_SECRET_KEY=your_stripe_secret_key_here
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key_here
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret_here

# =============================================================================
# DATABASE & CACHING
# =============================================================================

# Redis (Required for learning system)
REDIS_URL=redis://localhost:6379/0

# =============================================================================
# BUDGET & COST CONTROL
# =============================================================================

# Monthly budget limit (in USD)
MONTHLY_BUDGET=500.0

# Per-startup budget limit (in USD)
STARTUP_BUDGET=100.0

# =============================================================================
# SECURITY & ENCRYPTION
# =============================================================================

# Encryption key (auto-generated if not provided)
ENCRYPTION_KEY=your_encryption_key_here

# =============================================================================
# MONITORING & LOGGING
# =============================================================================

# Log level (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO

# =============================================================================
# AUTONOMOUS FEATURES
# =============================================================================

# Enable autonomous features
VECTOR_MEMORY_ENABLED=true
SELF_TUNING_ENABLED=true
REINFORCEMENT_LEARNING_ENABLED=true
AUTONOMOUS_WORKFLOW_ENABLED=true
"""
    
    try:
        with open('.env.template', 'w') as f:
            f.write(env_content)
        print("✅ .env.template created!")
        print("📋 Next steps:")
        print("1. Copy .env.template to .env")
        print("2. Fill in your actual API keys")
        print("3. Restart the application")
        return True
    except Exception as e:
        print(f"❌ Error creating .env template: {e}")
        return False

def test_components():
    """Test all components after fixes"""
    print("\n🧪 Testing components...")
    
    # Test Stripe
    try:
        import stripe
        if stripe.api_key:
            print("✅ Stripe import successful")
        else:
            print("❌ Stripe not configured")
    except ImportError:
        print("❌ Stripe not installed")
    
    # Test Redis
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0, socket_connect_timeout=2)
        r.ping()
        print("✅ Redis connection successful")
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
    
    # Test autonomous features
    try:
        from autonomous_enhancements import VectorMemoryManager
        print("✅ Autonomous features import successful")
    except Exception as e:
        print(f"❌ Autonomous features import failed: {e}")

def main():
    """Main function to fix critical components"""
    print("🚨 AutoPilot Ventures - Critical Components Fix")
    print("=" * 60)
    
    # Check current status
    stripe_ok = check_stripe_config()
    redis_ok = check_redis_connection()
    env_ok = check_env_file()
    
    print("\n📊 Current Status:")
    print(f"   Stripe: {'✅' if stripe_ok else '❌'}")
    print(f"   Redis:  {'✅' if redis_ok else '❌'}")
    print(f"   .env:   {'✅' if env_ok else '❌'}")
    
    # Offer fixes
    if not env_ok:
        print("\n🔧 Would you like to create a .env template? (y/n): ", end="")
        if input().lower() == 'y':
            create_env_template()
    
    if not redis_ok:
        print("\n🔧 Would you like to install Redis with Docker? (y/n): ", end="")
        if input().lower() == 'y':
            install_redis_docker()
    
    if not stripe_ok:
        print("\n🔧 Stripe configuration required!")
        print("Please:")
        print("1. Go to https://dashboard.stripe.com/")
        print("2. Create account and get API keys")
        print("3. Add keys to .env file")
    
    # Test after fixes
    print("\n🧪 Testing components after fixes...")
    test_components()
    
    print("\n" + "=" * 60)
    print("🎯 Next Steps:")
    print("1. Configure Stripe API keys")
    print("2. Start Redis server")
    print("3. Test autonomous features")
    print("4. Run: python integrate_autonomous_features.py test_startup")
    print("=" * 60)

if __name__ == "__main__":
    main() 
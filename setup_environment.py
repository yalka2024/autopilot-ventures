#!/usr/bin/env python3
"""
Environment setup script for AutoPilot Ventures platform.
This script helps configure the environment with proper keys and settings.
"""

import os
import sys
from pathlib import Path
from generate_fernet_key import generate_fernet_key, validate_fernet_key, test_key_functionality


def setup_environment():
    """Set up the environment for AutoPilot Ventures."""
    print("🚀 AutoPilot Ventures Environment Setup")
    print("=" * 50)
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found!")
        print("📋 Creating .env file from template...")
        
        # Copy from env.example if it exists
        example_file = Path("env.example")
        if example_file.exists():
            with open(example_file, 'r') as f:
                content = f.read()
            
            with open(env_file, 'w') as f:
                f.write(content)
            print("✅ Created .env file from template")
        else:
            print("❌ env.example not found. Please create .env file manually.")
            return False
    else:
        print("✅ .env file found")
    
    # Generate and set Fernet key
    print("\n🔑 Setting up encryption...")
    try:
        # Generate new key
        fernet_key = generate_fernet_key()
        
        if validate_fernet_key(fernet_key):
            print("✅ Fernet key generated and validated")
            
            if test_key_functionality(fernet_key):
                print("✅ Key functionality test passed")
            else:
                print("❌ Key functionality test failed")
                return False
        else:
            print("❌ Fernet key validation failed")
            return False
            
        # Update .env file with the key
        update_env_file(env_file, fernet_key)
        
    except Exception as e:
        print(f"❌ Failed to set up encryption: {e}")
        return False
    
    # Check required environment variables
    print("\n🔍 Checking environment configuration...")
    check_environment_variables()
    
    print("\n✅ Environment setup completed!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your API keys")
    print("2. Set OPENAI_SECRET_KEY for AI functionality")
    print("3. Set STRIPE_SECRET_KEY for payment processing")
    print("4. Run: python main.py --health-check")
    
    return True


def update_env_file(env_file: Path, fernet_key: str):
    """Update .env file with Fernet key."""
    try:
        # Read current content
        with open(env_file, 'r') as f:
            lines = f.readlines()
        
        # Update or add FERNET_KEY
        key_updated = False
        for i, line in enumerate(lines):
            if line.startswith("FERNET_KEY=") or line.startswith("ENCRYPTION_KEY="):
                lines[i] = f"FERNET_KEY={fernet_key}\n"
                key_updated = True
                break
        
        if not key_updated:
            # Find the security section and add the key
            for i, line in enumerate(lines):
                if "SECURITY & ENCRYPTION" in line:
                    # Insert after the section header
                    lines.insert(i + 2, f"FERNET_KEY={fernet_key}\n")
                    break
            else:
                # Add at the end if section not found
                lines.append(f"\n# Encryption key\nFERNET_KEY={fernet_key}\n")
        
        # Write back to file
        with open(env_file, 'w') as f:
            f.writelines(lines)
        
        print("✅ Fernet key added to .env file")
        
    except Exception as e:
        print(f"❌ Failed to update .env file: {e}")


def check_environment_variables():
    """Check if required environment variables are set."""
    required_vars = [
        "OPENAI_SECRET_KEY",
        "FERNET_KEY"
    ]
    
    optional_vars = [
        "STRIPE_SECRET_KEY",
        "STRIPE_PUBLISHABLE_KEY",
        "SERPAPI_KEY"
    ]
    
    print("\n📋 Required variables:")
    for var in required_vars:
        value = os.getenv(var)
        if value and value != f"your_{var.lower()}_here":
            print(f"  ✅ {var}: Set")
        else:
            print(f"  ❌ {var}: Not set or using placeholder")
    
    print("\n📋 Optional variables:")
    for var in optional_vars:
        value = os.getenv(var)
        if value and value != f"your_{var.lower()}_here":
            print(f"  ✅ {var}: Set")
        else:
            print(f"  ⚠️  {var}: Not set (optional)")


def main():
    """Main function."""
    try:
        success = setup_environment()
        if success:
            print("\n🎉 Setup completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Setup failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
AWS CLI Checker
Verifies AWS CLI installation and configuration
"""

import subprocess
import sys

def check_aws_cli():
    """Check if AWS CLI is installed"""
    try:
        result = subprocess.run(['aws', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ AWS CLI installed: {result.stdout.strip()}")
            return True
        else:
            print("❌ AWS CLI not found")
            return False
    except FileNotFoundError:
        print("❌ AWS CLI not installed")
        return False

def check_aws_config():
    """Check AWS configuration"""
    try:
        result = subprocess.run(['aws', 'sts', 'get-caller-identity'], capture_output=True, text=True)
        if result.returncode == 0:
            identity = result.stdout.strip()
            print(f"✅ AWS configured: {identity}")
            return True
        else:
            print(f"❌ AWS not configured: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error checking AWS config: {e}")
        return False

def check_region():
    """Check AWS region"""
    try:
        result = subprocess.run(['aws', 'configure', 'get', 'region'], capture_output=True, text=True)
        if result.returncode == 0:
            region = result.stdout.strip()
            print(f"✅ AWS Region: {region}")
            return region
        else:
            print("❌ No region configured")
            return None
    except Exception as e:
        print(f"❌ Error checking region: {e}")
        return None

def main():
    print("🔍 Checking AWS CLI Setup")
    print("=" * 30)
    
    # Check installation
    if not check_aws_cli():
        print("\n📋 To install AWS CLI:")
        print("  1. Download from: https://aws.amazon.com/cli/")
        print("  2. Or use: pip install awscli")
        return
    
    # Check configuration
    if not check_aws_config():
        print("\n📋 To configure AWS:")
        print("  1. Run: aws configure")
        print("  2. Enter your Access Key ID")
        print("  3. Enter your Secret Access Key")
        print("  4. Enter your region (e.g., us-east-1)")
        return
    
    # Check region
    region = check_region()
    if not region:
        print("\n📋 To set region:")
        print("  aws configure set region us-east-1")
        return
    
    print("\n✅ AWS CLI is ready!")
    print("\n📋 You can now run:")
    print("  python quick_check.py")
    print("  python diagnose_service.py")
    print("  python quick_check.py autopilot-ventures-v2")

if __name__ == "__main__":
    main() 
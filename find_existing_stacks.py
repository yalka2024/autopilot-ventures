#!/usr/bin/env python3
"""
Find Existing AutoPilot Stacks
Helps identify what stacks exist and check AWS CLI
"""

import subprocess
import sys
import os

def check_aws_cli():
    """Check if AWS CLI is available"""
    try:
        result = subprocess.run(['aws', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ AWS CLI found: {result.stdout.strip()}")
            return True
        else:
            print("❌ AWS CLI not working")
            return False
    except FileNotFoundError:
        print("❌ AWS CLI not installed")
        return False

def find_autopilot_stacks():
    """Find all AutoPilot stacks"""
    try:
        result = subprocess.run([
            'aws', 'cloudformation', 'list-stacks',
            '--query', 'StackSummaries[?contains(StackName, `autopilot`)].{Name:StackName,Status:StackStatus}',
            '--output', 'table'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("📋 Found AutoPilot stacks:")
            print(result.stdout)
            return True
        else:
            print(f"❌ Error listing stacks: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_all_stacks():
    """Check all stacks (not just autopilot)"""
    try:
        result = subprocess.run([
            'aws', 'cloudformation', 'list-stacks',
            '--query', 'StackSummaries[].{Name:StackName,Status:StackStatus}',
            '--output', 'table'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("📋 All CloudFormation stacks:")
            print(result.stdout)
            return True
        else:
            print(f"❌ Error listing all stacks: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_ecs_clusters():
    """Check all ECS clusters"""
    try:
        result = subprocess.run([
            'aws', 'ecs', 'list-clusters',
            '--output', 'text'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            clusters = result.stdout.strip().split('\n')
            print("📋 ECS clusters:")
            for cluster in clusters:
                if cluster:
                    print(f"  - {cluster}")
            return True
        else:
            print(f"❌ Error listing clusters: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🔍 Finding Existing AutoPilot Stacks")
    print("=" * 50)
    
    # Check AWS CLI
    if not check_aws_cli():
        print("\n📋 To install AWS CLI:")
        print("  1. Download from: https://aws.amazon.com/cli/")
        print("  2. Or use: pip install awscli")
        print("  3. Then run: aws configure")
        return
    
    print("\n1. Checking for AutoPilot stacks...")
    if not find_autopilot_stacks():
        print("\n2. Checking all stacks...")
        check_all_stacks()
    
    print("\n3. Checking ECS clusters...")
    check_ecs_clusters()
    
    print("\n" + "=" * 50)
    print("✅ Stack discovery complete!")
    
    print("\n📋 Next steps:")
    print("  1. If no AutoPilot stacks exist, create one:")
    print("     aws cloudformation create-stack --stack-name autopilot-ventures-v4 --template-body file://cloud-deployment.yml --capabilities CAPABILITY_NAMED_IAM --parameters ParameterKey=Environment,ParameterValue=production ParameterKey=AutonomyLevel,ParameterValue=fully_autonomous ParameterKey=BudgetThreshold,ParameterValue=50")
    print("  2. If stacks exist but with different names, update the diagnostic scripts")
    print("  3. If AWS CLI isn't working, check your AWS credentials")

if __name__ == "__main__":
    main() 
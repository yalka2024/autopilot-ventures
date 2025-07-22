#!/usr/bin/env python3
"""
AWS CLI Deployment Script for AutoPilot Ventures Stack 3
Uses AWS CLI instead of boto3 to avoid dependency issues.
"""

import subprocess
import sys
import os
import time
from datetime import datetime

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n🚀 {description}")
    print(f"Command: {command}")
    print("-" * 50)
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("✅ Success!")
        if result.stdout:
            print("Output:")
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed!")
        print(f"Error: {e}")
        if e.stdout:
            print("Stdout:")
            print(e.stdout)
        if e.stderr:
            print("Stderr:")
            print(e.stderr)
        return False

def check_aws_cli():
    """Check if AWS CLI is available."""
    return run_command("aws --version", "Checking AWS CLI")

def check_stack_exists(stack_name):
    """Check if stack exists using AWS CLI."""
    command = f"aws cloudformation describe-stacks --stack-name {stack_name}"
    return run_command(command, f"Checking if stack {stack_name} exists")

def delete_stack(stack_name):
    """Delete stack using AWS CLI."""
    command = f"aws cloudformation delete-stack --stack-name {stack_name}"
    return run_command(command, f"Deleting stack {stack_name}")

def create_stack_simple(stack_name):
    """Create stack with simplified template using AWS CLI."""
    command = f"""aws cloudformation create-stack \
  --stack-name {stack_name} \
  --template-body file://cloud-deployment.yml \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameters ParameterKey=Environment,ParameterValue=production ParameterKey=AutonomyLevel,ParameterValue=fully_autonomous ParameterKey=BudgetThreshold,ParameterValue=50"""
    
    return run_command(command, f"Creating stack {stack_name}")

def wait_for_stack_completion(stack_name, timeout_minutes=30):
    """Wait for stack to complete using AWS CLI."""
    print(f"\n⏳ Waiting for stack {stack_name} to complete...")
    
    start_time = time.time()
    timeout_seconds = timeout_minutes * 60
    
    while time.time() - start_time < timeout_seconds:
        try:
            command = f"aws cloudformation describe-stacks --stack-name {stack_name} --query 'Stacks[0].StackStatus' --output text"
            result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
            status = result.stdout.strip()
            
            print(f"Stack status: {status}")
            
            if status in ['CREATE_COMPLETE', 'UPDATE_COMPLETE']:
                print(f"✅ Stack {stack_name} completed successfully!")
                return True
            elif status in ['CREATE_FAILED', 'UPDATE_FAILED', 'ROLLBACK_COMPLETE']:
                print(f"❌ Stack {stack_name} failed: {status}")
                return False
            
            time.sleep(30)  # Wait 30 seconds before checking again
            
        except subprocess.CalledProcessError as e:
            print(f"Error checking stack status: {e}")
            time.sleep(30)
    
    print(f"⏰ Timeout waiting for stack {stack_name}")
    return False

def verify_deployment(stack_name):
    """Verify the deployment using AWS CLI."""
    print(f"\n🔍 Verifying deployment for stack {stack_name}...")
    
    # Check stack status
    command = f"aws cloudformation describe-stacks --stack-name {stack_name} --query 'Stacks[0].StackStatus' --output text"
    if run_command(command, "Checking stack status"):
        print("✅ Stack verification completed")
        return True
    else:
        print("❌ Stack verification failed")
        return False

def main():
    """Main deployment function."""
    stack_name = 'autopilot-ventures-3'
    
    print("🎯 AutoPilot Ventures Stack 3 Deployment (AWS CLI)")
    print("=" * 60)
    
    # Check AWS CLI
    if not check_aws_cli():
        print("❌ AWS CLI not found. Please install it first.")
        return 1
    
    # Check if template file exists
    if not os.path.exists('cloud-deployment.yml'):
        print("❌ cloud-deployment.yml not found!")
        return 1
    
    # Check current stack status
    print("\n📋 Checking current stack status...")
    check_stack_exists(stack_name)
    
    # Ask user if they want to delete existing stack
    print(f"\n⚠️  Stack {stack_name} might already exist.")
    print("Do you want to:")
    print("1. Delete existing stack and redeploy")
    print("2. Try to create new stack (might fail if exists)")
    print("3. Exit")
    
    choice = input("\nEnter your choice (1/2/3): ").strip()
    
    if choice == "1":
        # Delete and recreate
        if delete_stack(stack_name):
            print("✅ Stack deleted successfully")
            time.sleep(10)  # Wait for deletion to complete
        else:
            print("⚠️  Stack deletion failed or stack doesn't exist")
        
        # Create new stack
        if create_stack_simple(stack_name):
            success = wait_for_stack_completion(stack_name)
            if success:
                verify_deployment(stack_name)
                print("\n🎉 Deployment completed successfully!")
                print(f"Stack Name: {stack_name}")
                print("\n🚀 Your AutoPilot Ventures Stack 3 is now running!")
            else:
                print("\n❌ Deployment failed!")
                return 1
        else:
            print("\n❌ Stack creation failed!")
            return 1
    
    elif choice == "2":
        # Try to create new stack
        if create_stack_simple(stack_name):
            success = wait_for_stack_completion(stack_name)
            if success:
                verify_deployment(stack_name)
                print("\n🎉 Deployment completed successfully!")
                print(f"Stack Name: {stack_name}")
                print("\n🚀 Your AutoPilot Ventures Stack 3 is now running!")
            else:
                print("\n❌ Deployment failed!")
                return 1
        else:
            print("\n❌ Stack creation failed!")
            return 1
    
    elif choice == "3":
        print("👋 Exiting...")
        return 0
    
    else:
        print("❌ Invalid choice!")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 
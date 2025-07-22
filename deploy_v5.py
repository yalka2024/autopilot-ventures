#!/usr/bin/env python3
"""
Deploy AutoPilot Ventures V5 Stack
Creates a new stack with unique naming to avoid conflicts
"""

import subprocess
import sys
import time
from datetime import datetime

def run_command(command, description):
    """Run a command and return success status"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed")
            return True, result.stdout
        else:
            print(f"❌ {description} failed: {result.stderr}")
            return False, result.stderr
    except Exception as e:
        print(f"❌ {description} error: {e}")
        return False, str(e)

def check_stack_exists(stack_name):
    """Check if stack already exists"""
    command = f"aws cloudformation describe-stacks --stack-name {stack_name} --query 'Stacks[0].StackStatus' --output text"
    success, output = run_command(command, f"Checking if {stack_name} exists")
    return success

def delete_stack(stack_name):
    """Delete existing stack"""
    command = f"aws cloudformation delete-stack --stack-name {stack_name}"
    success, output = run_command(command, f"Deleting stack {stack_name}")
    if success:
        print("⏳ Waiting for stack deletion to complete...")
        time.sleep(30)  # Wait a bit for deletion to start
    return success

def create_stack(stack_name):
    """Create new stack"""
    command = f"""aws cloudformation create-stack \\
  --stack-name {stack_name} \\
  --template-body file://cloud-deployment.yml \\
  --capabilities CAPABILITY_NAMED_IAM \\
  --parameters ParameterKey=Environment,ParameterValue=production ParameterKey=AutonomyLevel,ParameterValue=fully_autonomous ParameterKey=BudgetThreshold,ParameterValue=50"""
    
    success, output = run_command(command, f"Creating stack {stack_name}")
    return success, output

def monitor_stack(stack_name):
    """Monitor stack creation progress"""
    print(f"⏳ Monitoring stack {stack_name} creation...")
    
    while True:
        command = f"aws cloudformation describe-stacks --stack-name {stack_name} --query 'Stacks[0].StackStatus' --output text"
        success, status = run_command(command, "Checking stack status")
        
        if not success:
            print("❌ Error checking stack status")
            break
            
        status = status.strip()
        print(f"📊 Current status: {status}")
        
        if status == 'CREATE_COMPLETE':
            print("🎉 Stack created successfully!")
            break
        elif status in ['CREATE_FAILED', 'ROLLBACK_COMPLETE', 'ROLLBACK_FAILED']:
            print("❌ Stack creation failed")
            check_stack_events(stack_name)
            break
        elif status == 'CREATE_IN_PROGRESS':
            print("⏳ Still creating...")
            time.sleep(30)
        else:
            print(f"⚠️  Unexpected status: {status}")
            time.sleep(30)

def check_stack_events(stack_name):
    """Check recent stack events for errors"""
    print(f"🔍 Checking events for {stack_name}...")
    command = f"aws cloudformation describe-stack-events --stack-name {stack_name} --max-items 10 --output table"
    success, output = run_command(command, "Getting stack events")
    if success:
        print("📋 Recent stack events:")
        print(output)

def main():
    stack_name = 'autopilot-ventures-F1'
    
    print("🚀 AutoPilot Ventures V5 Stack Deployment")
    print("=" * 50)
    print(f"Stack Name: {stack_name}")
    print(f"Template: cloud-deployment.yml")
    print(f"Region: us-east-1")
    print("=" * 50)
    
    # Check if stack exists
    if check_stack_exists(stack_name):
        print(f"\n⚠️  Stack {stack_name} already exists!")
        response = input("Do you want to delete it and create a new one? (y/n): ")
        if response.lower() == 'y':
            delete_stack(stack_name)
        else:
            print("❌ Deployment cancelled")
            return
    
    # Create new stack
    success, output = create_stack(stack_name)
    if success:
        print(f"✅ Stack creation initiated: {output.strip()}")
        monitor_stack(stack_name)
    else:
        print("❌ Failed to create stack")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
AutoPilot Ventures v5 Deployment Script
Final version with all dependency fixes applied
"""

import subprocess
import sys
import time
import json

def run_command(command, description):
    """Run a command and return the result"""
    print(f"\n🔧 {description}")
    print(f"Command: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            if result.stdout:
                print(f"Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} - FAILED")
            print(f"Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {description} - EXCEPTION: {str(e)}")
        return False

def main():
    print("🚀 AutoPilot Ventures v5 Deployment")
    print("=" * 50)
    
    # Step 1: Build Docker image
    if not run_command("docker build -t autopilot-ventures:latest .", "Building Docker image"):
        print("❌ Docker build failed. Please check the errors above.")
        return
    
    # Step 2: Tag image for ECR
    if not run_command("docker tag autopilot-ventures:latest 160277203814.dkr.ecr.us-east-1.amazonaws.com/autopilot-ventures:latest", "Tagging image for ECR"):
        print("❌ Image tagging failed.")
        return
    
    # Step 3: Authenticate with ECR
    if not run_command("aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 160277203814.dkr.ecr.us-east-1.amazonaws.com", "Authenticating with ECR"):
        print("❌ ECR authentication failed. Please ensure AWS CLI is installed and configured.")
        return
    
    # Step 4: Push image to ECR
    if not run_command("docker push 160277203814.dkr.ecr.us-east-1.amazonaws.com/autopilot-ventures:latest", "Pushing image to ECR"):
        print("❌ Image push failed.")
        return
    
    # Create CloudFormation stack
    print("🔧 Creating CloudFormation stack: autopilot-ventures-final")
    stack_command = [
        "aws", "cloudformation", "create-stack",
        "--region", "us-east-1",
        "--stack-name", "autopilot-ventures-final",
        "--template-body", "file://cloud-deployment.yml",
        "--capabilities", "CAPABILITY_NAMED_IAM",
        "--parameters",
        "ParameterKey=Environment,ParameterValue=production",
        "ParameterKey=AutonomyLevel,ParameterValue=fully_autonomous", 
        "ParameterKey=BudgetThreshold,ParameterValue=50",
        "ParameterKey=PublicSubnet1,ParameterValue=subnet-028bbe7733e9d9516",
        "ParameterKey=PublicSubnet2,ParameterValue=subnet-033606419f5f87330",
        "ParameterKey=PublicSubnet3,ParameterValue=subnet-038f5efbdc9615ca7",
        "ParameterKey=VPC,ParameterValue=vpc-0e6882b31d339a158"
    ]
    
    if not run_command(stack_command, "Creating CloudFormation stack: autopilot-ventures-final"):
        print("❌ Stack creation failed.")
        return
    
    print(f"\n🎉 Deployment initiated successfully!")
    print(f"Stack name: autopilot-ventures-final")
    print(f"Monitor progress with: aws cloudformation describe-stacks --stack-name autopilot-ventures-final")
    print(f"Check ECS service with: aws ecs describe-services --cluster autopilot-ventures-P-production-autopilot-ventures-final --services master-agent-service-final-production")

if __name__ == "__main__":
    main() 
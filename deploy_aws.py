#!/usr/bin/env python3
"""
AWS Deployment Script for AutoPilot Ventures Platform
"""

import boto3
import json
import time
import sys
from datetime import datetime

def print_status(message):
    print(f"📋 {message}")

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def print_warning(message):
    print(f"⚠️  {message}")

def deploy_aws_infrastructure():
    """Deploy AutoPilot Ventures infrastructure to AWS."""
    
    print("🚀 AutoPilot Ventures - AWS Deployment")
    print("=" * 50)
    
    # Initialize AWS clients
    cloudformation = boto3.client('cloudformation')
    ecr = boto3.client('ecr')
    ecs = boto3.client('ecs')
    
    # Configuration
    stack_name = 'autopilot-ventures-v5'
    template_file = 'cloud-deployment.yml'
    
    try:
        # Check if stack already exists
        print_status("Checking existing CloudFormation stack...")
        try:
            response = cloudformation.describe_stacks(StackName=stack_name)
            stack_status = response['Stacks'][0]['StackStatus']
            print_warning(f"Stack {stack_name} already exists with status: {stack_status}")
            
            if stack_status in ['CREATE_COMPLETE', 'UPDATE_COMPLETE']:
                print_success("Stack is already deployed and ready!")
                return True
            elif stack_status in ['CREATE_IN_PROGRESS', 'UPDATE_IN_PROGRESS']:
                print_status("Stack is currently being deployed...")
                return wait_for_stack_completion(cloudformation, stack_name)
            else:
                print_error(f"Stack is in an invalid state: {stack_status}")
                return False
                
        except cloudformation.exceptions.ClientError as e:
            if 'does not exist' in str(e):
                print_status("Stack does not exist, creating new deployment...")
            else:
                raise e
        
        # Read CloudFormation template
        print_status("Reading CloudFormation template...")
        with open(template_file, 'r') as f:
            template_body = f.read()
        
        # Prepare parameters
        parameters = [
            {
                'ParameterKey': 'Environment',
                'ParameterValue': 'production'
            },
            {
                'ParameterKey': 'AutonomyLevel',
                'ParameterValue': 'fully_autonomous'
            },
            {
                'ParameterKey': 'BudgetThreshold',
                'ParameterValue': '50'
            },
            {
                'ParameterKey': 'ImageUrl',
                'ParameterValue': '160277203814.dkr.ecr.us-east-1.amazonaws.com/autopilot-ventures:latest'
            }
        ]
        
        # Create CloudFormation stack
        print_status("Creating CloudFormation stack...")
        response = cloudformation.create_stack(
            StackName=stack_name,
            TemplateBody=template_body,
            Parameters=parameters,
            Capabilities=['CAPABILITY_NAMED_IAM'],
            OnFailure='ROLLBACK',
            Tags=[
                {
                    'Key': 'Project',
                    'Value': 'AutoPilot Ventures'
                },
                {
                    'Key': 'Environment',
                    'Value': 'production'
                },
                {
                    'Key': 'DeploymentDate',
                    'Value': datetime.now().isoformat()
                }
            ]
        )
        
        print_success(f"Stack creation initiated: {response['StackId']}")
        
        # Wait for stack completion
        return wait_for_stack_completion(cloudformation, stack_name)
        
    except Exception as e:
        print_error(f"Deployment failed: {str(e)}")
        return False

def wait_for_stack_completion(cloudformation, stack_name):
    """Wait for CloudFormation stack to complete."""
    
    print_status("Waiting for stack deployment to complete...")
    
    while True:
        try:
            response = cloudformation.describe_stacks(StackName=stack_name)
            stack_status = response['Stacks'][0]['StackStatus']
            
            print_status(f"Stack status: {stack_status}")
            
            if stack_status in ['CREATE_COMPLETE', 'UPDATE_COMPLETE']:
                print_success("Stack deployment completed successfully!")
                return True
            elif stack_status in ['CREATE_FAILED', 'UPDATE_FAILED', 'ROLLBACK_COMPLETE']:
                print_error(f"Stack deployment failed: {stack_status}")
                return False
            elif stack_status in ['CREATE_IN_PROGRESS', 'UPDATE_IN_PROGRESS']:
                print_status("Stack is still being deployed...")
                time.sleep(30)
            else:
                print_warning(f"Unknown stack status: {stack_status}")
                time.sleep(30)
                
        except Exception as e:
            print_error(f"Error checking stack status: {str(e)}")
            return False

def check_ecr_image():
    """Check if the ECR image exists and is accessible."""
    
    print_status("Checking ECR image...")
    
    try:
        ecr = boto3.client('ecr')
        
        # Check if repository exists
        response = ecr.describe_repositories(repositoryNames=['autopilot-ventures'])
        repository_uri = response['repositories'][0]['repositoryUri']
        
        # Check if latest image exists
        response = ecr.describe_images(
            repositoryName='autopilot-ventures',
            imageIds=[{'imageTag': 'latest'}]
        )
        
        if response['imageDetails']:
            print_success("ECR image found and accessible")
            return True
        else:
            print_warning("ECR image not found, you may need to build and push the image")
            return False
            
    except Exception as e:
        print_error(f"Error checking ECR image: {str(e)}")
        return False

def check_ecs_cluster():
    """Check ECS cluster status."""
    
    print_status("Checking ECS cluster...")
    
    try:
        ecs = boto3.client('ecs')
        
        # List clusters
        response = ecs.list_clusters()
        clusters = response['clusterArns']
        
        autopilot_clusters = [c for c in clusters if 'autopilot' in c.lower()]
        
        if autopilot_clusters:
            print_success(f"Found AutoPilot clusters: {len(autopilot_clusters)}")
            for cluster in autopilot_clusters:
                print_status(f"  - {cluster}")
            return True
        else:
            print_warning("No AutoPilot ECS clusters found")
            return False
            
    except Exception as e:
        print_error(f"Error checking ECS clusters: {str(e)}")
        return False

def main():
    """Main deployment function."""
    
    print("🔍 Pre-deployment checks...")
    
    # Check ECR image
    if not check_ecr_image():
        print_warning("ECR image check failed, but continuing with deployment...")
    
    # Check ECS clusters
    check_ecs_cluster()
    
    print("\n🚀 Starting AWS infrastructure deployment...")
    
    # Deploy infrastructure
    if deploy_aws_infrastructure():
        print_success("AWS deployment completed successfully!")
        
        print("\n📊 Deployment Summary:")
        print("  • CloudFormation Stack: autopilot-ventures-v5")
        print("  • Environment: production")
        print("  • Autonomy Level: fully_autonomous")
        print("  • Budget Threshold: $50")
        
        print("\n🔧 Next Steps:")
        print("  1. Check ECS service status: python diagnose_service.py")
        print("  2. Monitor logs: aws logs tail /ecs/master-agent-final-production")
        print("  3. Check CloudWatch metrics")
        print("  4. Test autonomous operation")
        
    else:
        print_error("AWS deployment failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 
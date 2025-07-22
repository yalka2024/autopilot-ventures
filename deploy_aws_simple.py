#!/usr/bin/env python3
"""
Simplified AWS Deployment Script for AutoPilot Ventures Platform
Uses existing ECS cluster and creates a simple task definition
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

def deploy_simple_task():
    """Deploy a simple task definition to the existing ECS cluster."""
    
    print("🚀 AutoPilot Ventures - Simple AWS Deployment")
    print("=" * 50)
    
    # Initialize AWS clients
    ecs = boto3.client('ecs')
    logs = boto3.client('logs')
    
    try:
        # Use existing cluster
        cluster_name = 'autopilot-ventures-manual-production'
        
        # Create log group
        log_group_name = '/ecs/autopilot-ventures-simple-production'
        try:
            logs.create_log_group(logGroupName=log_group_name)
            print_success("Log group created")
        except logs.exceptions.ResourceAlreadyExistsException:
            print_status("Log group already exists")
        
        # Create task definition
        print_status("Creating task definition...")
        
        task_definition = {
            'family': 'autopilot-ventures-simple-production',
            'networkMode': 'awsvpc',
            'requiresCompatibilities': ['FARGATE'],
            'cpu': '1024',
            'memory': '2048',
            'executionRoleArn': 'arn:aws:iam::160277203814:role/ecsTaskExecutionRole',
            'taskRoleArn': 'arn:aws:iam::160277203814:role/ecsTaskExecutionRole',
            'containerDefinitions': [
                {
                    'name': 'autopilot-ventures',
                    'image': '160277203814.dkr.ecr.us-east-1.amazonaws.com/autopilot-ventures:latest',
                    'command': ['python', 'main.py'],
                    'environment': [
                        {'name': 'ENVIRONMENT', 'value': 'production'},
                        {'name': 'AUTONOMY_LEVEL', 'value': 'fully_autonomous'},
                        {'name': 'BUDGET_THRESHOLD', 'value': '50'},
                        {'name': 'PHASE3_ENABLED', 'value': 'true'},
                        {'name': 'VECTOR_MEMORY_ENABLED', 'value': 'true'},
                        {'name': 'SELF_TUNING_ENABLED', 'value': 'true'},
                        {'name': 'REINFORCEMENT_LEARNING_ENABLED', 'value': 'true'},
                        {'name': 'AUTONOMOUS_WORKFLOW_ENABLED', 'value': 'true'},
                        {'name': 'PORT', 'value': '8000'},
                        {'name': 'HOST', 'value': '0.0.0.0'}
                    ],
                    'portMappings': [
                        {
                            'containerPort': 8000,
                            'protocol': 'tcp'
                        },
                        {
                            'containerPort': 9090,
                            'protocol': 'tcp'
                        }
                    ],
                    'logConfiguration': {
                        'logDriver': 'awslogs',
                        'options': {
                            'awslogs-group': log_group_name,
                            'awslogs-region': 'us-east-1',
                            'awslogs-stream-prefix': 'ecs'
                        }
                    },
                    'healthCheck': {
                        'command': ['CMD-SHELL', 'curl -f http://localhost:8000/health || exit 1'],
                        'interval': 30,
                        'timeout': 5,
                        'retries': 3,
                        'startPeriod': 60
                    }
                }
            ]
        }
        
        # Register task definition
        response = ecs.register_task_definition(**task_definition)
        task_def_arn = response['taskDefinition']['taskDefinitionArn']
        print_success(f"Task definition created: {task_def_arn}")
        
        # Update existing service or create new one
        service_name = 'autopilot-ventures-simple-service'
        
        try:
            # Try to update existing service
            ecs.update_service(
                cluster=cluster_name,
                service=service_name,
                taskDefinition=task_def_arn,
                forceNewDeployment=True
            )
            print_success("Service updated with new task definition")
        except ecs.exceptions.ServiceNotFoundException:
            # Create new service
            print_status("Creating new ECS service...")
            
            # Get default VPC and subnets
            ec2 = boto3.client('ec2')
            vpcs = ec2.describe_vpcs(Filters=[{'Name': 'isDefault', 'Values': ['true']}])
            vpc_id = vpcs['Vpcs'][0]['VpcId']
            
            subnets = ec2.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
            subnet_ids = [subnet['SubnetId'] for subnet in subnets['Subnets'][:2]]
            
            # Create security group
            sg_name = 'autopilot-simple-sg'
            try:
                sgs = ec2.describe_security_groups(Filters=[{'Name': 'group-name', 'Values': [sg_name]}])
                sg_id = sgs['SecurityGroups'][0]['GroupId']
            except:
                sg = ec2.create_security_group(
                    GroupName=sg_name,
                    Description='Security group for AutoPilot Ventures simple deployment'
                )
                sg_id = sg['GroupId']
                
                # Add ingress rules
                ec2.authorize_security_group_ingress(
                    GroupId=sg_id,
                    IpPermissions=[
                        {
                            'IpProtocol': 'tcp',
                            'FromPort': 8000,
                            'ToPort': 8000,
                            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                        },
                        {
                            'IpProtocol': 'tcp',
                            'FromPort': 9090,
                            'ToPort': 9090,
                            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                        }
                    ]
                )
            
            # Create service
            ecs.create_service(
                cluster=cluster_name,
                serviceName=service_name,
                taskDefinition=task_def_arn,
                desiredCount=1,
                launchType='FARGATE',
                networkConfiguration={
                    'awsvpcConfiguration': {
                        'subnets': subnet_ids,
                        'securityGroups': [sg_id],
                        'assignPublicIp': 'ENABLED'
                    }
                }
            )
            print_success("New ECS service created")
        
        # Wait for service to be stable
        print_status("Waiting for service to be stable...")
        waiter = ecs.get_waiter('services_stable')
        waiter.wait(
            cluster=cluster_name,
            services=[service_name],
            WaiterConfig={'Delay': 30, 'MaxAttempts': 20}
        )
        
        print_success("Service is now stable and running!")
        
        # Get service details
        service_response = ecs.describe_services(
            cluster=cluster_name,
            services=[service_name]
        )
        
        service = service_response['services'][0]
        print_status(f"Service Status: {service['status']}")
        print_status(f"Desired Count: {service['desiredCount']}")
        print_status(f"Running Count: {service['runningCount']}")
        
        if service['tasks']:
            task = service['tasks'][0]
            print_status(f"Task ARN: {task['taskArn']}")
            print_status(f"Task Status: {task['lastStatus']}")
        
        return True
        
    except Exception as e:
        print_error(f"Deployment failed: {str(e)}")
        return False

def main():
    """Main deployment function."""
    
    print("🔍 Starting simple AWS deployment...")
    
    # Deploy simple task
    if deploy_simple_task():
        print_success("Simple AWS deployment completed successfully!")
        
        print("\n📊 Deployment Summary:")
        print("  • Cluster: autopilot-ventures-manual-production")
        print("  • Service: autopilot-ventures-simple-service")
        print("  • Task Definition: autopilot-ventures-simple-production")
        print("  • Environment: production")
        print("  • Autonomy Level: fully_autonomous")
        
        print("\n🔧 Next Steps:")
        print("  1. Check service status: python diagnose_service.py")
        print("  2. Monitor logs: aws logs tail /ecs/autopilot-ventures-simple-production")
        print("  3. Test autonomous operation")
        print("  4. Check health endpoint")
        
    else:
        print_error("Simple AWS deployment failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 
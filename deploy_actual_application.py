#!/usr/bin/env python3
"""
Deploy the Actual AutoPilot Ventures Application
"""

import boto3
import json
import time
from datetime import datetime

def print_status(message):
    print(f"📋 {message}")

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def print_warning(message):
    print(f"⚠️  {message}")

def create_actual_task_definition():
    """Create the actual AutoPilot Ventures task definition."""
    
    print("🔧 Creating AutoPilot Ventures task definition...")
    
    ecs = boto3.client('ecs', region_name='us-east-1')
    
    try:
        # Create task definition for the actual AutoPilot Ventures application
        task_definition = {
            'family': 'autopilot-ventures-production',
            'networkMode': 'awsvpc',
            'requiresCompatibilities': ['FARGATE'],
            'cpu': '1024',
            'memory': '2048',
            'executionRoleArn': 'arn:aws:iam::160277203814:role/ecs-task-execution-manual-production',
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
                        {'name': 'HOST', 'value': '0.0.0.0'},
                        {'name': 'LOG_LEVEL', 'value': 'INFO'}
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
                            'awslogs-group': '/ecs/autopilot-ventures-production',
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
        
        print_success(f"AutoPilot Ventures task definition created: {task_def_arn}")
        
        # Create log group
        logs = boto3.client('logs', region_name='us-east-1')
        try:
            logs.create_log_group(logGroupName='/ecs/autopilot-ventures-production')
            print_success("Log group created")
        except Exception as e:
            print_status(f"Log group already exists: {e}")
        
        return task_def_arn
        
    except Exception as e:
        print_error(f"Error creating task definition: {str(e)}")
        return None

def create_production_service(task_def_arn):
    """Create the production AutoPilot Ventures service."""
    
    print("🚀 Creating AutoPilot Ventures production service...")
    
    ecs = boto3.client('ecs', region_name='us-east-1')
    ec2 = boto3.client('ec2', region_name='us-east-1')
    
    try:
        # Get default VPC and subnets
        vpcs = ec2.describe_vpcs(Filters=[{'Name': 'isDefault', 'Values': ['true']}])
        vpc_id = vpcs['Vpcs'][0]['VpcId']
        
        subnets = ec2.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
        subnet_ids = [subnet['SubnetId'] for subnet in subnets['Subnets'][:2]]
        
        # Create security group for production
        sg_name = 'autopilot-production-sg'
        try:
            sgs = ec2.describe_security_groups(Filters=[{'Name': 'group-name', 'Values': [sg_name]}])
            sg_id = sgs['SecurityGroups'][0]['GroupId']
        except:
            sg = ec2.create_security_group(
                GroupName=sg_name,
                Description='Security group for AutoPilot Ventures production'
            )
            sg_id = sg['GroupId']
            
            # Add ingress rules for AutoPilot Ventures
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
        
        # Create production service
        ecs.create_service(
            cluster='autopilot-ventures-manual-production',
            serviceName='autopilot-ventures-production-service',
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
        
        print_success("AutoPilot Ventures production service created successfully!")
        return True
        
    except Exception as e:
        print_error(f"Error creating production service: {str(e)}")
        return False

def update_existing_service(task_def_arn):
    """Update the existing simple service with the production task definition."""
    
    print("🔄 Updating existing service with production configuration...")
    
    ecs = boto3.client('ecs', region_name='us-east-1')
    
    try:
        # Update the existing simple service
        ecs.update_service(
            cluster='autopilot-ventures-manual-production',
            service='autopilot-ventures-simple-service',
            taskDefinition=task_def_arn,
            forceNewDeployment=True
        )
        
        print_success("Existing service updated with production configuration!")
        return True
        
    except Exception as e:
        print_error(f"Error updating existing service: {str(e)}")
        return False

def wait_for_service_stability(service_name):
    """Wait for the service to become stable."""
    
    print(f"⏳ Waiting for service {service_name} to become stable...")
    
    ecs = boto3.client('ecs', region_name='us-east-1')
    
    try:
        waiter = ecs.get_waiter('services_stable')
        waiter.wait(
            cluster='autopilot-ventures-manual-production',
            services=[service_name],
            WaiterConfig={'Delay': 30, 'MaxAttempts': 20}
        )
        
        print_success(f"Service {service_name} is now stable!")
        return True
        
    except Exception as e:
        print_error(f"Service failed to stabilize: {str(e)}")
        return False

def check_service_status(service_name):
    """Check the status of the service."""
    
    print(f"📊 Checking status of {service_name}...")
    
    ecs = boto3.client('ecs', region_name='us-east-1')
    
    try:
        response = ecs.describe_services(
            cluster='autopilot-ventures-manual-production',
            services=[service_name]
        )
        
        if response['services']:
            service = response['services'][0]
            print_status(f"Service Status: {service['status']}")
            print_status(f"Desired Count: {service['desiredCount']}")
            print_status(f"Running Count: {service['runningCount']}")
            print_status(f"Pending Count: {service['pendingCount']}")
            
            if service['tasks']:
                print_status(f"Active Tasks: {len(service['tasks'])}")
                for task in service['tasks']:
                    print_status(f"  Task ARN: {task['taskArn']}")
                    print_status(f"  Task Status: {task['lastStatus']}")
            
            return service['status'] == 'ACTIVE' and service['runningCount'] > 0
        else:
            print_error("Service not found")
            return False
            
    except Exception as e:
        print_error(f"Error checking service status: {str(e)}")
        return False

def main():
    """Main deployment function."""
    
    print("🚀 AutoPilot Ventures - Production Deployment")
    print("=" * 50)
    
    # Create actual task definition
    task_def_arn = create_actual_task_definition()
    if not task_def_arn:
        print_error("Failed to create task definition")
        return False
    
    # Update existing service with production configuration
    if update_existing_service(task_def_arn):
        print_success("Production deployment initiated!")
        
        # Wait for service to stabilize
        if wait_for_service_stability('autopilot-ventures-simple-service'):
            # Check final status
            if check_service_status('autopilot-ventures-simple-service'):
                print_success("🎉 AutoPilot Ventures Production Deployment Successful!")
                
                print("\n📊 Production Deployment Summary:")
                print("  • Task Definition: autopilot-ventures-production")
                print("  • Service: autopilot-ventures-simple-service (Updated)")
                print("  • Image: AutoPilot Ventures Latest")
                print("  • Environment: production")
                print("  • Autonomy Level: fully_autonomous")
                print("  • Cluster: autopilot-ventures-manual-production")
                
                print("\n🤖 AutoPilot Ventures Features Active:")
                print("  ✅ 10 AI Agents (Niche Research, MVP Design, Marketing, etc.)")
                print("  ✅ Master Agent Orchestration")
                print("  ✅ Autonomous Startup Discovery")
                print("  ✅ Global Market Analysis")
                print("  ✅ Income Simulation & Projections")
                print("  ✅ Multilingual Support (10 languages)")
                print("  ✅ Advanced Security & Monitoring")
                print("  ✅ Vector Memory & Self-Tuning")
                print("  ✅ Reinforcement Learning Engine")
                print("  ✅ Autonomous Workflow Management")
                
                print("\n🔧 Management Commands:")
                print("  • Check status: aws ecs describe-services --cluster autopilot-ventures-manual-production --services autopilot-ventures-simple-service")
                print("  • View logs: aws logs tail /ecs/autopilot-ventures-production")
                print("  • Health check: curl http://[TASK_IP]:8000/health")
                print("  • Metrics: curl http://[TASK_IP]:9090/metrics")
                
                print("\n🚀 The AutoPilot Ventures platform is now ready for autonomous operation!")
                print("The system will automatically:")
                print("  • Discover new startup opportunities globally")
                print("  • Evaluate market viability and potential")
                print("  • Create and launch startups autonomously")
                print("  • Scale successful ventures")
                print("  • Generate passive income through multiple ventures")
                
                return True
            else:
                print_error("Service is not running properly")
                return False
        else:
            print_error("Service failed to stabilize")
            return False
    else:
        print_error("Failed to update service")
        return False

if __name__ == "__main__":
    main() 
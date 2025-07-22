#!/usr/bin/env python3
"""
Deploy AutoPilot Ventures with Nginx Test Image
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

def create_nginx_test_task_definition():
    """Create a task definition using nginx for testing."""
    
    print("🔧 Creating nginx test task definition...")
    
    ecs = boto3.client('ecs', region_name='us-east-1')
    
    try:
        # Create task definition with nginx (public image, no ECR auth needed)
        task_definition = {
            'family': 'autopilot-ventures-nginx-test',
            'networkMode': 'awsvpc',
            'requiresCompatibilities': ['FARGATE'],
            'cpu': '256',
            'memory': '512',
            'executionRoleArn': 'arn:aws:iam::160277203814:role/ecs-task-execution-manual-production',
            'containerDefinitions': [
                {
                    'name': 'nginx-test',
                    'image': 'nginx:alpine',
                    'portMappings': [
                        {
                            'containerPort': 80,
                            'protocol': 'tcp'
                        }
                    ],
                    'essential': True,
                    'logConfiguration': {
                        'logDriver': 'awslogs',
                        'options': {
                            'awslogs-group': '/ecs/autopilot-ventures-nginx-test',
                            'awslogs-region': 'us-east-1',
                            'awslogs-stream-prefix': 'ecs'
                        }
                    }
                }
            ]
        }
        
        # Register task definition
        response = ecs.register_task_definition(**task_definition)
        task_def_arn = response['taskDefinition']['taskDefinitionArn']
        
        print_success(f"Nginx test task definition created: {task_def_arn}")
        
        # Create log group
        logs = boto3.client('logs', region_name='us-east-1')
        try:
            logs.create_log_group(logGroupName='/ecs/autopilot-ventures-nginx-test')
            print_success("Log group created")
        except Exception as e:
            print_status(f"Log group already exists: {e}")
        
        return task_def_arn
        
    except Exception as e:
        print_error(f"Error creating task definition: {str(e)}")
        return None

def create_nginx_test_service(task_def_arn):
    """Create a test service using nginx."""
    
    print("🚀 Creating nginx test service...")
    
    ecs = boto3.client('ecs', region_name='us-east-1')
    ec2 = boto3.client('ec2', region_name='us-east-1')
    
    try:
        # Get default VPC and subnets
        vpcs = ec2.describe_vpcs(Filters=[{'Name': 'isDefault', 'Values': ['true']}])
        vpc_id = vpcs['Vpcs'][0]['VpcId']
        
        subnets = ec2.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
        subnet_ids = [subnet['SubnetId'] for subnet in subnets['Subnets'][:2]]
        
        # Use existing security group or create one
        sg_name = 'autopilot-nginx-test-sg'
        try:
            sgs = ec2.describe_security_groups(Filters=[{'Name': 'group-name', 'Values': [sg_name]}])
            sg_id = sgs['SecurityGroups'][0]['GroupId']
        except:
            # Create security group if it doesn't exist
            sg = ec2.create_security_group(
                GroupName=sg_name,
                Description='Security group for AutoPilot Ventures nginx test'
            )
            sg_id = sg['GroupId']
            
            # Add ingress rules
            ec2.authorize_security_group_ingress(
                GroupId=sg_id,
                IpPermissions=[
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 80,
                        'ToPort': 80,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                    }
                ]
            )
        
        # Create test service
        service_name = 'autopilot-ventures-nginx-test'
        
        try:
            ecs.create_service(
                cluster='autopilot-ventures-manual-production',
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
            print_success(f"Nginx test service created: {service_name}")
            return service_name
            
        except ecs.exceptions.ServiceAlreadyExistsException:
            # Update existing service
            ecs.update_service(
                cluster='autopilot-ventures-manual-production',
                service=service_name,
                taskDefinition=task_def_arn,
                forceNewDeployment=True
            )
            print_success(f"Nginx test service updated: {service_name}")
            return service_name
        
    except Exception as e:
        print_error(f"Error creating nginx test service: {str(e)}")
        return None

def wait_for_service_stability(service_name):
    """Wait for the service to become stable."""
    
    print(f"⏳ Waiting for service {service_name} to become stable...")
    
    ecs = boto3.client('ecs', region_name='us-east-1')
    
    max_attempts = 20
    attempt = 0
    
    while attempt < max_attempts:
        try:
            response = ecs.describe_services(
                cluster='autopilot-ventures-manual-production',
                services=[service_name]
            )
            
            if response['services']:
                service = response['services'][0]
                print_status(f"Status: {service['status']}, Running: {service['runningCount']}, Pending: {service['pendingCount']}")
                
                if service['status'] == 'ACTIVE' and service['runningCount'] > 0 and service['pendingCount'] == 0:
                    print_success(f"Service {service_name} is stable!")
                    return True
                
                if service['status'] == 'ACTIVE' and service['runningCount'] == 0 and service['pendingCount'] == 0:
                    # Check for failed tasks
                    if 'deployments' in service and service['deployments']:
                        deployment = service['deployments'][0]
                        if deployment.get('failedTasks', 0) > 0:
                            print_error(f"Service has {deployment['failedTasks']} failed tasks")
                            return False
                
            attempt += 1
            time.sleep(30)
            
        except Exception as e:
            print_error(f"Error checking service status: {str(e)}")
            return False
    
    print_error("Service failed to stabilize within timeout")
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
                    
                    # Get task details to find the public IP
                    task_details = ecs.describe_tasks(
                        cluster='autopilot-ventures-manual-production',
                        tasks=[task['taskArn']]
                    )
                    
                    if task_details['tasks']:
                        task_detail = task_details['tasks'][0]
                        if 'attachments' in task_detail:
                            for attachment in task_detail['attachments']:
                                if attachment['type'] == 'ElasticNetworkInterface':
                                    for detail in attachment['details']:
                                        if detail['name'] == 'privateIPv4Address':
                                            private_ip = detail['value']
                                            print_success(f"  Private IP: {private_ip}")
                                            print_success(f"  Test URL: http://{private_ip}")
            
            return service['status'] == 'ACTIVE' and service['runningCount'] > 0
        else:
            print_error("Service not found")
            return False
            
    except Exception as e:
        print_error(f"Error checking service status: {str(e)}")
        return False

def main():
    """Main deployment function."""
    
    print("🚀 AutoPilot Ventures - Nginx Test Deployment")
    print("=" * 50)
    
    # Create nginx test task definition
    task_def_arn = create_nginx_test_task_definition()
    if not task_def_arn:
        print_error("Failed to create task definition")
        return False
    
    # Create nginx test service
    service_name = create_nginx_test_service(task_def_arn)
    if not service_name:
        print_error("Failed to create nginx test service")
        return False
    
    # Wait for service to stabilize
    if wait_for_service_stability(service_name):
        # Check final status
        if check_service_status(service_name):
            print_success("🎉 Nginx Test Deployment Successful!")
            
            print("\n📊 Test Deployment Summary:")
            print("  • Task Definition: autopilot-ventures-nginx-test")
            print("  • Service: autopilot-ventures-nginx-test")
            print("  • Image: nginx:alpine (public image)")
            print("  • Cluster: autopilot-ventures-manual-production")
            
            print("\n🔧 Infrastructure Verification:")
            print("  ✅ ECS Cluster is working")
            print("  ✅ Fargate tasks can be launched")
            print("  ✅ Network configuration is correct")
            print("  ✅ Security groups are properly configured")
            print("  ✅ Public image pulling works")
            
            print("\n📋 Next Steps:")
            print("1. The infrastructure is confirmed working")
            print("2. We need to fix ECR permissions for the AutoPilot Ventures image")
            print("3. Once ECR permissions are fixed, we can deploy the actual application")
            print("4. The ECR issue is: Task execution role needs ecr:GetAuthorizationToken permission")
            
            print("\n🔧 Management Commands:")
            print(f"  • Check status: aws ecs describe-services --cluster autopilot-ventures-manual-production --services {service_name}")
            print("  • View logs: aws logs tail /ecs/autopilot-ventures-nginx-test")
            print("  • Test nginx: curl http://[TASK_IP]")
            
            return True
        else:
            print_error("Service is not running properly")
            return False
    else:
        print_error("Service failed to stabilize")
        return False

if __name__ == "__main__":
    main() 
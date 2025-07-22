#!/usr/bin/env python3
"""
Fix IAM roles for AutoPilot Ventures ECS deployment
"""

import boto3
import json
from datetime import datetime

def print_status(message):
    print(f"📋 {message}")

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def print_warning(message):
    print(f"⚠️  {message}")

def create_ecs_execution_role():
    """Create the ECS task execution role with proper permissions."""
    
    print("🔧 Creating ECS Task Execution Role...")
    
    iam = boto3.client('iam')
    
    role_name = 'ecsTaskExecutionRole'
    
    try:
        # Check if role already exists
        try:
            iam.get_role(RoleName=role_name)
            print_status(f"Role {role_name} already exists")
            return f"arn:aws:iam::160277203814:role/{role_name}"
        except iam.exceptions.NoSuchEntityException:
            pass
        
        # Create trust policy for ECS tasks
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "ecs-tasks.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        
        # Create the role
        response = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='ECS Task Execution Role for AutoPilot Ventures'
        )
        
        role_arn = response['Role']['Arn']
        print_success(f"Created role: {role_arn}")
        
        # Attach the AWS managed policy for ECS task execution
        iam.attach_role_policy(
            RoleName=role_name,
            PolicyArn='arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy'
        )
        print_success("Attached AmazonECSTaskExecutionRolePolicy")
        
        # Create custom policy for additional permissions
        custom_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "logs:CreateLogGroup",
                        "logs:CreateLogStream",
                        "logs:PutLogEvents"
                    ],
                    "Resource": "*"
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "secretsmanager:GetSecretValue"
                    ],
                    "Resource": "*"
                }
            ]
        }
        
        iam.put_role_policy(
            RoleName=role_name,
            PolicyName='AutoPilotVenturesCustomPolicy',
            PolicyDocument=json.dumps(custom_policy)
        )
        print_success("Attached custom policy")
        
        return role_arn
        
    except Exception as e:
        print_error(f"Error creating role: {str(e)}")
        return None

def create_ecs_task_role():
    """Create the ECS task role for application permissions."""
    
    print("🔧 Creating ECS Task Role...")
    
    iam = boto3.client('iam')
    
    role_name = 'ecsTaskRole'
    
    try:
        # Check if role already exists
        try:
            iam.get_role(RoleName=role_name)
            print_status(f"Role {role_name} already exists")
            return f"arn:aws:iam::160277203814:role/{role_name}"
        except iam.exceptions.NoSuchEntityException:
            pass
        
        # Create trust policy for ECS tasks
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "ecs-tasks.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        
        # Create the role
        response = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='ECS Task Role for AutoPilot Ventures'
        )
        
        role_arn = response['Role']['Arn']
        print_success(f"Created role: {role_arn}")
        
        # Create policy for application permissions
        task_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:GetObject",
                        "s3:PutObject",
                        "s3:ListBucket"
                    ],
                    "Resource": "*"
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "logs:CreateLogGroup",
                        "logs:CreateLogStream",
                        "logs:PutLogEvents"
                    ],
                    "Resource": "*"
                }
            ]
        }
        
        iam.put_role_policy(
            RoleName=role_name,
            PolicyName='AutoPilotVenturesTaskPolicy',
            PolicyDocument=json.dumps(task_policy)
        )
        print_success("Attached task policy")
        
        return role_arn
        
    except Exception as e:
        print_error(f"Error creating task role: {str(e)}")
        return None

def update_task_definition():
    """Update the task definition with the correct role ARNs."""
    
    print("🔧 Updating task definition...")
    
    ecs = boto3.client('ecs')
    
    try:
        # Get the current task definition
        response = ecs.describe_task_definition(
            taskDefinition='autopilot-ventures-simple-production'
        )
        
        current_task_def = response['taskDefinition']
        
        # Create new task definition with updated roles
        new_task_def = {
            'family': current_task_def['family'],
            'networkMode': current_task_def['networkMode'],
            'requiresCompatibilities': current_task_def['requiresCompatibilities'],
            'cpu': current_task_def['cpu'],
            'memory': current_task_def['memory'],
            'executionRoleArn': 'arn:aws:iam::160277203814:role/ecsTaskExecutionRole',
            'taskRoleArn': 'arn:aws:iam::160277203814:role/ecsTaskRole',
            'containerDefinitions': current_task_def['containerDefinitions']
        }
        
        # Register new task definition
        response = ecs.register_task_definition(**new_task_def)
        new_task_def_arn = response['taskDefinition']['taskDefinitionArn']
        
        print_success(f"Updated task definition: {new_task_def_arn}")
        
        # Update the service to use the new task definition
        ecs.update_service(
            cluster='autopilot-ventures-manual-production',
            service='autopilot-ventures-simple-service',
            taskDefinition=new_task_def_arn,
            forceNewDeployment=True
        )
        
        print_success("Service updated with new task definition")
        return True
        
    except Exception as e:
        print_error(f"Error updating task definition: {str(e)}")
        return False

def main():
    """Main function to fix IAM roles and update deployment."""
    
    print("🔧 AutoPilot Ventures - IAM Role Fix")
    print("=" * 50)
    
    # Create execution role
    execution_role_arn = create_ecs_execution_role()
    if not execution_role_arn:
        print_error("Failed to create execution role")
        return False
    
    # Create task role
    task_role_arn = create_ecs_task_role()
    if not task_role_arn:
        print_error("Failed to create task role")
        return False
    
    # Update task definition
    if update_task_definition():
        print_success("IAM roles fixed and task definition updated!")
        
        print("\n📊 Next Steps:")
        print("  1. Wait a few minutes for the service to stabilize")
        print("  2. Check deployment status: python check_deployment_status.py")
        print("  3. Monitor logs: aws logs tail /ecs/autopilot-ventures-simple-production")
        
        return True
    else:
        print_error("Failed to update task definition")
        return False

if __name__ == "__main__":
    main() 
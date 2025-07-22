#!/usr/bin/env python3
"""
Create Simple Task Definition with Default ECS Roles
"""

import boto3

def create_simple_task():
    ecs = boto3.client('ecs', region_name='us-east-1')
    
    print("=== Creating Simple Task Definition ===")
    
    try:
        # Create new task definition with default ECS roles
        new_task_def = ecs.register_task_definition(
            family='master-agent-simple-production',
            networkMode='awsvpc',
            requiresCompatibilities=['FARGATE'],
            cpu='1024',
            memory='2048',
            # Use the existing ECS task execution role
            executionRoleArn='arn:aws:iam::160277203814:role/ecs-task-execution-manual-production',
            containerDefinitions=[
                {
                    'name': 'master-agent',
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
                        }
                    ],
                    'logConfiguration': {
                        'logDriver': 'awslogs',
                        'options': {
                            'awslogs-group': '/ecs/master-agent-simple-production',
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
        )
        
        new_task_def_arn = new_task_def['taskDefinition']['taskDefinitionArn']
        print(f"✅ New task definition created: {new_task_def_arn}")
        
        # Create log group
        logs = boto3.client('logs', region_name='us-east-1')
        try:
            logs.create_log_group(logGroupName='/ecs/master-agent-simple-production')
            print("✅ Log group created")
        except Exception as e:
            print(f"⚠️  Log group already exists: {e}")
        
        # Update service with new task definition
        print("Updating ECS service...")
        ecs.update_service(
            cluster='autopilot-ventures-manual-production',
            service='master-agent-service-manual-production',
            taskDefinition=new_task_def_arn,
            forceNewDeployment=True
        )
        
        print("✅ Service updated with new task definition!")
        print("\nThe service should now start tasks. Check with:")
        print("python diagnose_service.py")
        
    except Exception as e:
        print(f"❌ Error creating task definition: {e}")

if __name__ == "__main__":
    create_simple_task() 
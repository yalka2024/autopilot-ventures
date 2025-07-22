#!/usr/bin/env python3
"""
Fix ECS Service by creating new task definition and updating service
"""

import boto3

def fix_service():
    ecs = boto3.client('ecs', region_name='us-east-1')
    
    print("=== Fixing ECS Service ===")
    
    try:
        # Get current task definition
        current_task_def = ecs.describe_task_definition(
            taskDefinition='master-agent-manual-production'
        )
        
        print("Creating new task definition...")
        
        # Create new task definition with updated settings
        new_task_def = ecs.register_task_definition(
            family='master-agent-manual-production',
            networkMode='awsvpc',
            requiresCompatibilities=['FARGATE'],
            cpu='1024',
            memory='2048',
            executionRoleArn='arn:aws:iam::160277203814:role/ecs-task-execution-manual-production',
            taskRoleArn='arn:aws:iam::160277203814:role/ecs-service-manual-production',
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
                            'awslogs-group': '/ecs/master-agent-manual-production',
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
        
        # Update service with new task definition
        print("Updating service with new task definition...")
        ecs.update_service(
            cluster='autopilot-ventures-manual-production',
            service='master-agent-service-manual-production',
            taskDefinition=new_task_def_arn,
            desiredCount=1,
            forceNewDeployment=True
        )
        
        print("✅ Service updated successfully!")
        print("\nThe service should now start tasks. Check the AWS Console or run:")
        print("python diagnose_service.py")
        
    except Exception as e:
        print(f"❌ Error fixing service: {e}")

if __name__ == "__main__":
    fix_service() 
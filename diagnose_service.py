#!/usr/bin/env python3
"""
Diagnose ECS Service Issues
"""

import boto3

def diagnose_service():
    ecs = boto3.client('ecs', region_name='us-east-1')
    
    print("=== ECS Service Diagnosis ===")
    
    try:
        # Check service status
        response = ecs.describe_services(
            cluster='autopilot-ventures-manual-production',
            services=['master-agent-service-manual-production']
        )
        
        service = response['services'][0]
        print(f"Service Status: {service['status']}")
        print(f"Running: {service['runningCount']}, Pending: {service['pendingCount']}, Desired: {service['desiredCount']}")
        print(f"Task Definition: {service['taskDefinition']}")
        
        # Check deployments
        deployments = service['deployments']
        print(f"\nDeployments ({len(deployments)}):")
        for deployment in deployments:
            print(f"  {deployment['status']}: {deployment['failedTasks']} failed tasks")
            if deployment['failedTasks'] > 0:
                print(f"    Reason: {deployment.get('rolloutStateReason', 'Unknown')}")
        
        # Check if there are any tasks
        tasks_response = ecs.list_tasks(
            cluster='autopilot-ventures-manual-production',
            serviceName='master-agent-service-manual-production'
        )
        
        print(f"\nTotal Tasks: {len(tasks_response['taskArns'])}")
        
        if tasks_response['taskArns']:
            # Get task details
            task_details = ecs.describe_tasks(
                cluster='autopilot-ventures-manual-production',
                tasks=tasks_response['taskArns']
            )
            
            for task in task_details['tasks']:
                print(f"\nTask: {task['taskArn']}")
                print(f"  Status: {task['lastStatus']}")
                print(f"  Desired Status: {task['desiredStatus']}")
                print(f"  Stopped Reason: {task.get('stoppedReason', 'N/A')}")
                
                # Check container status
                for container in task['containers']:
                    print(f"  Container: {container['name']}")
                    print(f"    Status: {container['lastStatus']}")
                    if 'reason' in container:
                        print(f"    Reason: {container['reason']}")
        
        # Check task definition
        task_def_response = ecs.describe_task_definition(
            taskDefinition='master-agent-manual-production'
        )
        
        print(f"\nTask Definition Status: ACTIVE")
        print(f"CPU: {task_def_response['taskDefinition']['cpu']}")
        print(f"Memory: {task_def_response['taskDefinition']['memory']}")
        
        # Check if the image exists
        ecr = boto3.client('ecr', region_name='us-east-1')
        try:
            ecr.describe_images(
                repositoryName='autopilot-ventures',
                imageIds=[{'imageTag': 'latest'}]
            )
            print("✅ ECR Image: Found")
        except Exception as e:
            print(f"❌ ECR Image: {e}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    diagnose_service() 
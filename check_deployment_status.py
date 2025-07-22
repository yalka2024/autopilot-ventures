#!/usr/bin/env python3
"""
Check deployment status of AutoPilot Ventures platform
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

def check_deployment_status():
    """Check the status of the AutoPilot Ventures deployment."""
    
    print("🔍 AutoPilot Ventures - Deployment Status Check")
    print("=" * 50)
    
    # Initialize AWS clients
    ecs = boto3.client('ecs')
    logs = boto3.client('logs')
    
    try:
        # Check ECS service status
        cluster_name = 'autopilot-ventures-manual-production'
        service_name = 'autopilot-ventures-simple-service'
        
        print_status("Checking ECS service status...")
        
        response = ecs.describe_services(
            cluster=cluster_name,
            services=[service_name]
        )
        
        if not response['services']:
            print_error("Service not found")
            return False
        
        service = response['services'][0]
        
        print_status(f"Service Status: {service['status']}")
        print_status(f"Desired Count: {service['desiredCount']}")
        print_status(f"Running Count: {service['runningCount']}")
        print_status(f"Pending Count: {service['pendingCount']}")
        
        # Check tasks
        tasks = service.get('tasks', [])
        if tasks:
            print_status(f"Active Tasks: {len(tasks)}")
            for task in tasks:
                print_status(f"  Task ARN: {task['taskArn']}")
                print_status(f"  Task Status: {task['lastStatus']}")
                print_status(f"  Health Status: {task.get('healthStatus', 'N/A')}")
        else:
            print_warning("No tasks running")
        
        # Check recent events
        events = service.get('events', [])
        if events:
            print_status("Recent Events:")
            for event in events[:3]:
                print_status(f"  {event['createdAt']}: {event['message']}")
        else:
            print_warning("No recent events")
        
        # Check CloudWatch logs
        log_group_name = '/ecs/autopilot-ventures-simple-production'
        try:
            print_status("Checking CloudWatch logs...")
            
            # Get recent log streams
            streams_response = logs.describe_log_streams(
                logGroupName=log_group_name,
                orderBy='LastEventTime',
                descending=True,
                maxItems=5
            )
            
            if streams_response['logStreams']:
                print_status("Recent log streams:")
                for stream in streams_response['logStreams']:
                    print_status(f"  {stream['logStreamName']}")
                    
                    # Get recent events from the stream
                    events_response = logs.get_log_events(
                        logGroupName=log_group_name,
                        logStreamName=stream['logStreamName'],
                        startFromHead=False,
                        limit=5
                    )
                    
                    if events_response['events']:
                        print_status("    Recent events:")
                        for event in events_response['events']:
                            print_status(f"      {event['timestamp']}: {event['message'].strip()}")
            else:
                print_warning("No log streams found")
                
        except Exception as e:
            print_warning(f"Could not check logs: {str(e)}")
        
        # Overall status
        if service['status'] == 'ACTIVE' and service['runningCount'] > 0:
            print_success("✅ Deployment is successful and running!")
            return True
        elif service['status'] == 'ACTIVE' and service['runningCount'] == 0:
            print_warning("⚠️  Service is active but no tasks are running")
            return False
        else:
            print_error("❌ Service is not in expected state")
            return False
            
    except Exception as e:
        print_error(f"Error checking deployment status: {str(e)}")
        return False

def main():
    """Main function."""
    
    success = check_deployment_status()
    
    if success:
        print("\n🎉 AutoPilot Ventures is successfully deployed on AWS!")
        print("\n📊 Access Information:")
        print("  • ECS Cluster: autopilot-ventures-manual-production")
        print("  • ECS Service: autopilot-ventures-simple-service")
        print("  • Log Group: /ecs/autopilot-ventures-simple-production")
        
        print("\n🔧 Management Commands:")
        print("  • Check status: python check_deployment_status.py")
        print("  • View logs: aws logs tail /ecs/autopilot-ventures-simple-production")
        print("  • Stop service: aws ecs update-service --cluster autopilot-ventures-manual-production --service autopilot-ventures-simple-service --desired-count 0")
        
    else:
        print("\n❌ Deployment needs attention")
        print("Check the logs and service events for more details")

if __name__ == "__main__":
    main() 
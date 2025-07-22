#!/usr/bin/env python3
import boto3

def check_events():
    ecs = boto3.client('ecs', region_name='us-east-1')
    
    print("=== ECS Service Events ===")
    
    try:
        response = ecs.describe_services(
            cluster='autopilot-ventures-manual-production',
            services=['master-agent-service-manual-production']
        )
        
        service = response['services'][0]
        print(f"Service: {service['serviceName']}")
        print(f"Status: {service['status']}")
        print(f"Desired: {service['desiredCount']}, Running: {service['runningCount']}, Pending: {service['pendingCount']}")
        
        print("\nRecent Events:")
        for event in service['events'][:10]:
            print(f"  {event['createdAt']}: {event['message']}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_events() 
#!/usr/bin/env python3
"""
Monitor AutoPilot Ventures Service
"""

import boto3
import time

def monitor_service():
    ecs = boto3.client('ecs', region_name='us-east-1')
    
    print("=== AutoPilot Ventures Service Monitor ===")
    print("Monitoring service until it's fully running...")
    print("Press Ctrl+C to stop monitoring\n")
    
    try:
        while True:
            response = ecs.describe_services(
                cluster='autopilot-ventures-manual-production',
                services=['master-agent-service-manual-production']
            )
            
            service = response['services'][0]
            print(f"Status: {service['status']} | Running: {service['runningCount']} | Pending: {service['pendingCount']}")
            
            if service['runningCount'] > 0:
                print("\n🎉 SUCCESS! AutoPilot Ventures is now running!")
                print("\nYour platform is ready to use!")
                print("Access your AutoPilot Ventures platform at:")
                print("https://console.aws.amazon.com/ecs/home?region=us-east-1#/clusters/autopilot-ventures-manual-production/services")
                break
            
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    monitor_service() 
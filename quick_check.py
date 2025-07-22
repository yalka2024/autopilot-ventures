#!/usr/bin/env python3
"""
Quick MasterAgentService Check
Simple diagnostic without boto3 dependency
"""

import subprocess
import json
import sys

def run_aws_command(command):
    """Run AWS CLI command and return result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_stack_status(stack_name):
    """Check if stack exists and its status"""
    print(f"🔍 Checking stack: {stack_name}")
    
    success, output, error = run_aws_command(f"aws cloudformation describe-stacks --stack-name {stack_name} --query 'Stacks[0].StackStatus' --output text")
    
    if success:
        print(f"✅ Stack Status: {output.strip()}")
        return True
    else:
        print(f"❌ Stack not found or error: {error}")
        return False

def check_ecs_services(stack_name):
    """Check ECS services"""
    print(f"\n🔍 Checking ECS services for stack: {stack_name}")
    
    # List clusters
    success, output, error = run_aws_command("aws ecs list-clusters --output text")
    if not success:
        print(f"❌ Error listing clusters: {error}")
        return
    
    clusters = output.strip().split('\n')
    target_cluster = None
    
    for cluster in clusters:
        if stack_name in cluster:
            target_cluster = cluster
            break
    
    if not target_cluster:
        print("❌ No cluster found for this stack")
        return
    
    print(f"✅ Found cluster: {target_cluster}")
    
    # List services
    success, output, error = run_aws_command(f"aws ecs list-services --cluster {target_cluster} --output text")
    if not success:
        print(f"❌ Error listing services: {error}")
        return
    
    services = output.strip().split('\n')
    print(f"📋 Services in cluster:")
    for service in services:
        print(f"  - {service}")
        
        # Get service details
        success, details, error = run_aws_command(f"aws ecs describe-services --cluster {target_cluster} --services {service} --query 'services[0].{{Status:status,Desired:desiredCount,Running:runningCount,Pending:pendingCount}}' --output json")
        if success:
            service_info = json.loads(details)
            print(f"    Status: {service_info['Status']}")
            print(f"    Desired: {service_info['Desired']}, Running: {service_info['Running']}, Pending: {service_info['Pending']}")

def check_tasks(stack_name):
    """Check running tasks"""
    print(f"\n🔍 Checking tasks for stack: {stack_name}")
    
    # Find cluster
    success, output, error = run_aws_command("aws ecs list-clusters --output text")
    if not success:
        return
    
    clusters = output.strip().split('\n')
    target_cluster = None
    
    for cluster in clusters:
        if stack_name in cluster:
            target_cluster = cluster
            break
    
    if not target_cluster:
        print("❌ No cluster found")
        return
    
    # List tasks
    success, output, error = run_aws_command(f"aws ecs list-tasks --cluster {target_cluster} --output text")
    if not success:
        print(f"❌ Error listing tasks: {error}")
        return
    
    if not output.strip():
        print("❌ No tasks found")
        return
    
    tasks = output.strip().split('\n')
    print(f"📋 Found {len(tasks)} tasks:")
    
    for task in tasks:
        print(f"  Task: {task}")
        
        # Get task details
        success, details, error = run_aws_command(f"aws ecs describe-tasks --cluster {target_cluster} --tasks {task} --query 'tasks[0].{{Status:lastStatus,Health:healthStatus,StoppedReason:stoppedReason}}' --output json")
        if success:
            task_info = json.loads(details)
            print(f"    Status: {task_info['Status']}")
            print(f"    Health: {task_info.get('Health', 'UNKNOWN')}")
            if task_info.get('StoppedReason'):
                print(f"    Stopped Reason: {task_info['StoppedReason']}")

def check_logs(stack_name):
    """Check recent logs"""
    print(f"\n🔍 Checking logs for stack: {stack_name}")
    
    log_group = f"/ecs/master-agent-v2-production-{stack_name}"
    
    # Check if log group exists
    success, output, error = run_aws_command(f"aws logs describe-log-groups --log-group-name-prefix {log_group} --output text")
    if not success:
        print(f"❌ Error checking log groups: {error}")
        return
    
    if not output.strip():
        print("❌ No log groups found")
        return
    
    print(f"✅ Found log group: {log_group}")
    
    # Get recent log streams
    success, output, error = run_aws_command(f"aws logs describe-log-streams --log-group-name {log_group} --order-by LastEventTime --descending --max-items 3 --output text")
    if not success:
        print(f"❌ Error getting log streams: {error}")
        return
    
    streams = output.strip().split('\n')
    print(f"📋 Recent log streams:")
    
    for stream in streams:
        if stream:
            print(f"  Stream: {stream}")
            
            # Get recent events
            success, events, error = run_aws_command(f"aws logs get-log-events --log-group-name {log_group} --log-stream-name {stream} --start-time $(date -d '30 minutes ago' +%s)000 --limit 10 --output text")
            if success and events.strip():
                print(f"    Recent events:")
                for event in events.strip().split('\n')[:5]:
                    print(f"      {event}")

def main():
    if len(sys.argv) > 1:
        stack_name = sys.argv[1]
    else:
        stack_name = 'autopilot-ventures-v2'
    
    print(f"🔍 Quick Diagnostic for: {stack_name}")
    print("=" * 50)
    
    # Check stack
    if not check_stack_status(stack_name):
        print("\n❌ Stack not found or failed. Please check:")
        print("  1. Stack name is correct")
        print("  2. AWS CLI is configured")
        print("  3. Stack was created successfully")
        return
    
    # Check services
    check_ecs_services(stack_name)
    
    # Check tasks
    check_tasks(stack_name)
    
    # Check logs
    check_logs(stack_name)
    
    print("\n" + "=" * 50)
    print("✅ Quick diagnostic complete!")

if __name__ == "__main__":
    main() 
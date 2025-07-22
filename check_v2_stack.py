#!/usr/bin/env python3
"""
Check AutoPilot Ventures V2 Stack
Quick diagnostic for the existing v2 stack
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

def check_v2_stack():
    """Check the v2 stack status"""
    stack_name = 'autopilot-ventures-v2'
    
    print(f"🔍 Checking AutoPilot Ventures V2 Stack")
    print("=" * 50)
    
    # Check stack status
    print("1. Checking stack status...")
    success, output, error = run_aws_command(f"aws cloudformation describe-stacks --stack-name {stack_name} --query 'Stacks[0].StackStatus' --output text")
    
    if success:
        status = output.strip()
        print(f"✅ Stack Status: {status}")
        
        if status in ['CREATE_FAILED', 'UPDATE_FAILED', 'ROLLBACK_COMPLETE']:
            print("❌ Stack has failed - checking events...")
            check_stack_events(stack_name)
    else:
        print(f"❌ Stack not found: {error}")
        return
    
    # Check ECS cluster
    print("\n2. Checking ECS cluster...")
    success, output, error = run_aws_command("aws ecs list-clusters --output text")
    if success:
        clusters = output.strip().split('\n')
        v2_cluster = None
        
        for cluster in clusters:
            if 'autopilot-ventures-v2' in cluster:
                v2_cluster = cluster
                break
        
        if v2_cluster:
            print(f"✅ Found cluster: {v2_cluster}")
            check_ecs_services(v2_cluster)
        else:
            print("❌ No v2 cluster found")
    else:
        print(f"❌ Error listing clusters: {error}")
    
    # Check services
    print("\n3. Checking ECS services...")
    if 'v2_cluster' in locals() and v2_cluster:
        check_ecs_services(v2_cluster)
    
    # Check tasks
    print("\n4. Checking running tasks...")
    if 'v2_cluster' in locals() and v2_cluster:
        check_running_tasks(v2_cluster)
    
    # Check logs
    print("\n5. Checking logs...")
    check_v2_logs()

def check_stack_events(stack_name):
    """Check recent stack events"""
    success, output, error = run_aws_command(f"aws cloudformation describe-stack-events --stack-name {stack_name} --query 'StackEvents[0:10].{{Resource:LogicalResourceId,Status:ResourceStatus,Reason:ResourceStatusReason}}' --output json")
    
    if success:
        events = json.loads(output)
        print("📋 Recent stack events:")
        for event in events:
            status = event['Status']
            resource = event['Resource']
            reason = event.get('Reason', 'No reason')
            
            if 'FAILED' in status:
                print(f"❌ {resource}: {status}")
                print(f"   Reason: {reason}")
            elif 'COMPLETE' in status:
                print(f"✅ {resource}: {status}")

def check_ecs_services(cluster_arn):
    """Check ECS services in the cluster"""
    success, output, error = run_aws_command(f"aws ecs list-services --cluster {cluster_arn} --output text")
    
    if success and output.strip():
        services = output.strip().split('\n')
        print(f"📋 Services in cluster:")
        
        for service in services:
            print(f"  - {service}")
            
            # Get service details
            success, details, error = run_aws_command(f"aws ecs describe-services --cluster {cluster_arn} --services {service} --query 'services[0].{{Status:status,Desired:desiredCount,Running:runningCount,Pending:pendingCount}}' --output json")
            if success:
                service_info = json.loads(details)
                print(f"    Status: {service_info['Status']}")
                print(f"    Desired: {service_info['Desired']}, Running: {service_info['Running']}, Pending: {service_info['Pending']}")
    else:
        print("❌ No services found")

def check_running_tasks(cluster_arn):
    """Check running tasks"""
    success, output, error = run_aws_command(f"aws ecs list-tasks --cluster {cluster_arn} --output text")
    
    if success and output.strip():
        tasks = output.strip().split('\n')
        print(f"📋 Found {len(tasks)} tasks:")
        
        for task in tasks:
            print(f"  Task: {task}")
            
            # Get task details
            success, details, error = run_aws_command(f"aws ecs describe-tasks --cluster {cluster_arn} --tasks {task} --query 'tasks[0].{{Status:lastStatus,Health:healthStatus,StoppedReason:stoppedReason}}' --output json")
            if success:
                task_info = json.loads(details)
                print(f"    Status: {task_info['Status']}")
                print(f"    Health: {task_info.get('Health', 'UNKNOWN')}")
                if task_info.get('StoppedReason'):
                    print(f"    Stopped Reason: {task_info['StoppedReason']}")
    else:
        print("❌ No tasks found")

def check_v2_logs():
    """Check logs for v2 stack"""
    log_group = "/ecs/master-agent-v2-production-autopilot-ventures-v2"
    
    # Check if log group exists
    success, output, error = run_aws_command(f"aws logs describe-log-groups --log-group-name-prefix {log_group} --output text")
    
    if success and output.strip():
        print(f"✅ Found log group: {log_group}")
        
        # Get recent log streams
        success, output, error = run_aws_command(f"aws logs describe-log-streams --log-group-name {log_group} --order-by LastEventTime --descending --max-items 3 --output text")
        
        if success and output.strip():
            streams = output.strip().split('\n')
            print(f"📋 Recent log streams:")
            
            for stream in streams:
                if stream:
                    print(f"  Stream: {stream}")
                    
                    # Get recent events (last 10 minutes)
                    success, events, error = run_aws_command(f"aws logs get-log-events --log-group-name {log_group} --log-stream-name {stream} --limit 10 --output text")
                    if success and events.strip():
                        print(f"    Recent events:")
                        for event in events.strip().split('\n')[:5]:
                            print(f"      {event}")
        else:
            print("❌ No log streams found")
    else:
        print("❌ No log groups found")

def main():
    check_v2_stack()
    print("\n" + "=" * 50)
    print("✅ V2 Stack diagnostic complete!")

if __name__ == "__main__":
    main() 
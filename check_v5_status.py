#!/usr/bin/env python3
"""
AutoPilot Ventures F Status Checker
"""

import subprocess
import sys
import json

def run_command(command, description):
    """Run a command and return the result"""
    print(f"\n🔍 {description}")
    print(f"Command: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            if result.stdout:
                print(f"Output: {result.stdout.strip()}")
            return True, result.stdout
        else:
            print(f"❌ {description} - FAILED")
            print(f"Error: {result.stderr.strip()}")
            return False, result.stderr
    except Exception as e:
        print(f"❌ {description} - EXCEPTION: {str(e)}")
        return False, str(e)

def main():
    print("🔍 AutoPilot Ventures F1 Status Check")
    print("=" * 50)
    
    stack_name = "autopilot-ventures-F1"
    
    # Check CloudFormation stack status
    success, output = run_command(f"aws cloudformation describe-stacks --stack-name {stack_name} --query 'Stacks[0].StackStatus' --output text", 
                                 f"Checking CloudFormation stack status")
    
    if success:
        print(f"📊 Stack Status: {output.strip()}")
        
        if "CREATE_COMPLETE" in output:
            print("✅ Stack created successfully!")
            
            # Check ECS cluster
            cluster_name = f"autopilot-ventures-F1-production-{stack_name}"
            success, output = run_command(f"aws ecs describe-clusters --clusters {cluster_name}", 
                                        f"Checking ECS cluster: {cluster_name}")
            
            if success:
                # Check ECS service
                service_name = "master-agent-service-F1-production"
                success, output = run_command(f"aws ecs describe-services --cluster {cluster_name} --services {service_name}", 
                                            f"Checking ECS service: {service_name}")
                
                if success:
                    # Check running tasks
                    success, output = run_command(f"aws ecs list-tasks --cluster {cluster_name} --service-name {service_name}", 
                                                f"Checking running tasks")
                    
                    if success:
                        # Check logs
                        log_group = f"/ecs/master-agent-F1-production-{stack_name}"
                        success, output = run_command(f"aws logs describe-log-groups --log-group-name-prefix '{log_group}'", 
                                                    f"Checking CloudWatch logs")
        else:
            print(f"⏳ Stack is still being created. Status: {output.strip()}")
    else:
        print("❌ Could not check stack status. Please ensure AWS CLI is installed and configured.")

if __name__ == "__main__":
    main() 
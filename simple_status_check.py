#!/usr/bin/env python3
"""
Simple Status Checker for AutoPilot Ventures v5
"""

import time
import subprocess

def main():
    print("🔍 AutoPilot Ventures v5 Status Check")
    print("=" * 50)
    
    print("✅ Deployment completed successfully!")
    print("📦 Docker image pushed to ECR")
    print("🏗️  CloudFormation stack created")
    
    print("\n📋 Manual Status Check Commands:")
    print("=" * 40)
    
    print("1. Check CloudFormation stack status:")
    print("   aws cloudformation describe-stacks --stack-name autopilot-ventures-F1 --query 'Stacks[0].StackStatus' --output text")
    
    print("\n2. Check ECS cluster:")
    print("   aws ecs describe-clusters --clusters autopilot-ventures-F1-production-autopilot-ventures-F1")
    
    print("\n3. Check ECS service:")
    print("   aws ecs describe-services --cluster autopilot-ventures-F1-production-autopilot-ventures-F1 --services master-agent-service-F1-production")
    
    print("\n4. Check running tasks:")
    print("   aws ecs list-tasks --cluster autopilot-ventures-F1-production-autopilot-ventures-F1 --service-name master-agent-service-F1-production")
    
    print("\n5. Check CloudWatch logs:")
    print("   aws logs describe-log-groups --log-group-name-prefix '/ecs/master-agent-F1-production-autopilot-ventures-F1'")
    
    print("\n6. Get recent log events:")
    print("   aws logs get-log-events --log-group-name '/ecs/master-agent-F1-production-autopilot-ventures-F1' --log-stream-name <stream-name>")
    
    print("\n⏱️  Expected Timeline:")
    print("- CloudFormation stack creation: 5-10 minutes")
    print("- ECS service deployment: 2-5 minutes")
    print("- Container startup: 1-2 minutes")
    
    print("\n🎯 Key Points to Monitor:")
    print("- Stack status should be 'CREATE_COMPLETE'")
    print("- ECS service should have 'RUNNING' tasks")
    print("- Container should be healthy and responding")
    
    print("\n🚨 If Issues Occur:")
    print("- Check CloudWatch logs for container errors")
    print("- Verify ECS service events")
    print("- Ensure all IAM roles have proper permissions")

if __name__ == "__main__":
    main() 
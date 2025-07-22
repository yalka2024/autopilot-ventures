#!/usr/bin/env python3
"""
Check Rollback Issues for AutoPilot Ventures v5
"""

def main():
    print("🚨 AutoPilot Ventures v5 Rollback Analysis")
    print("=" * 50)
    
    print("❌ Stack Status: ROLLBACK_COMPLETE")
    print("This means the deployment failed and rolled back.")
    
    print("\n🔍 To diagnose the issue, run these commands:")
    print("=" * 40)
    
    print("1. Check failed resources:")
    print("   aws cloudformation describe-stack-events --stack-name autopilot-ventures-F1 --query 'StackEvents[?ResourceStatus==`CREATE_FAILED`].[LogicalResourceId,ResourceStatusReason]' --output table")
    
    print("\n2. Check all stack events:")
    print("   aws cloudformation describe-stack-events --stack-name autopilot-ventures-F1 --query 'StackEvents[?ResourceStatus==`CREATE_FAILED`]' --output json")
    
    print("\n3. Check specific resource failures:")
    print("   aws cloudformation describe-stack-events --stack-name autopilot-ventures-F1 --query 'StackEvents[?ResourceStatus==`CREATE_FAILED`].[LogicalResourceId,ResourceStatusReason,Timestamp]' --output table")
    
    print("\n🔧 Common Rollback Causes:")
    print("- ECS Task Definition issues")
    print("- IAM Role permission problems")
    print("- VPC/Subnet configuration errors")
    print("- ECR image pull issues")
    print("- Security Group rule conflicts")
    
    print("\n💡 Next Steps:")
    print("1. Run the diagnostic commands above")
    print("2. Check the specific error messages")
    print("3. Fix the identified issues")
    print("4. Delete the failed stack: aws cloudformation delete-stack --stack-name autopilot-ventures-F1")
    print("5. Redeploy with fixes")
    
    print("\n🚀 Quick Fix Options:")
    print("- Check if ECR repository exists")
    print("- Verify IAM roles have proper permissions")
    print("- Ensure VPC and subnets are available")
    print("- Check if the Docker image is accessible")

if __name__ == "__main__":
    main() 
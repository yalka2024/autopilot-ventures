#!/usr/bin/env python3
"""
Fix ECR Permissions for ECS Task Execution Role
"""

import boto3
import json

def print_status(message):
    print(f"📋 {message}")

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def fix_ecr_permissions():
    """Fix ECR permissions for the ECS task execution role."""
    
    print("🔧 Fixing ECR permissions for ECS task execution role...")
    
    iam = boto3.client('iam', region_name='us-east-1')
    
    try:
        # Create ECR policy document
        ecr_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "ecr:GetAuthorizationToken",
                        "ecr:BatchCheckLayerAvailability",
                        "ecr:GetDownloadUrlForLayer",
                        "ecr:BatchGetImage"
                    ],
                    "Resource": "*"
                }
            ]
        }
        
        # Create or update the ECR policy
        policy_name = "ECR-Pull-Policy"
        policy_arn = f"arn:aws:iam::160277203814:policy/{policy_name}"
        
        try:
            # Try to create the policy
            iam.create_policy(
                PolicyName=policy_name,
                PolicyDocument=json.dumps(ecr_policy),
                Description="Policy to allow ECS tasks to pull images from ECR"
            )
            print_success(f"Created ECR policy: {policy_name}")
        except iam.exceptions.EntityAlreadyExistsException:
            # Policy already exists, update it
            iam.create_policy_version(
                PolicyArn=policy_arn,
                PolicyDocument=json.dumps(ecr_policy),
                SetAsDefault=True
            )
            print_success(f"Updated ECR policy: {policy_name}")
        
        # Attach the policy to the ECS task execution role
        role_name = "ecs-task-execution-manual-production"
        
        try:
            iam.attach_role_policy(
                RoleName=role_name,
                PolicyArn=policy_arn
            )
            print_success(f"Attached ECR policy to role: {role_name}")
        except iam.exceptions.EntityAlreadyExistsException:
            print_status(f"Policy already attached to role: {role_name}")
        
        # Also ensure the role has the basic ECS task execution permissions
        ecs_policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
        
        try:
            iam.attach_role_policy(
                RoleName=role_name,
                PolicyArn=ecs_policy_arn
            )
            print_success(f"Attached ECS task execution policy to role: {role_name}")
        except iam.exceptions.EntityAlreadyExistsException:
            print_status(f"ECS policy already attached to role: {role_name}")
        
        print_success("ECR permissions fixed successfully!")
        return True
        
    except Exception as e:
        print_error(f"Error fixing ECR permissions: {str(e)}")
        return False

def verify_role_permissions():
    """Verify that the role has the correct permissions."""
    
    print("🔍 Verifying role permissions...")
    
    iam = boto3.client('iam', region_name='us-east-1')
    
    try:
        role_name = "ecs-task-execution-manual-production"
        
        # Get attached policies
        response = iam.list_attached_role_policies(RoleName=role_name)
        
        print_status("Attached policies:")
        for policy in response['AttachedPolicies']:
            print_status(f"  • {policy['PolicyName']} ({policy['PolicyArn']})")
        
        # Check if ECR policy is attached
        ecr_policy_found = any(
            'ECR-Pull-Policy' in policy['PolicyName'] 
            for policy in response['AttachedPolicies']
        )
        
        if ecr_policy_found:
            print_success("ECR permissions are correctly configured!")
            return True
        else:
            print_error("ECR permissions are not configured!")
            return False
            
    except Exception as e:
        print_error(f"Error verifying permissions: {str(e)}")
        return False

def main():
    """Main function."""
    
    print("🔧 ECR Permissions Fix")
    print("=" * 30)
    
    # Fix ECR permissions
    if fix_ecr_permissions():
        # Verify the fix
        if verify_role_permissions():
            print_success("🎉 ECR permissions fixed and verified!")
            
            print("\n📋 Next Steps:")
            print("1. The ECS service should now be able to pull images from ECR")
            print("2. You can force a new deployment to test the fix:")
            print("   aws ecs update-service --cluster autopilot-ventures-manual-production --service autopilot-ventures-simple-service --force-new-deployment")
            print("3. Monitor the deployment:")
            print("   aws ecs describe-services --cluster autopilot-ventures-manual-production --services autopilot-ventures-simple-service")
            
            return True
        else:
            print_error("Permissions verification failed")
            return False
    else:
        print_error("Failed to fix ECR permissions")
        return False

if __name__ == "__main__":
    main() 
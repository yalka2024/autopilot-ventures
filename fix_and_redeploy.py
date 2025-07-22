#!/usr/bin/env python3
"""
Fix and Redeploy AutoPilot Ventures v5
"""

import subprocess
import sys

def run_command(command, description):
    """Run a command and return the result"""
    print(f"\n🔧 {description}")
    print(f"Command: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            if result.stdout:
                print(f"Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} - FAILED")
            print(f"Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {description} - EXCEPTION: {str(e)}")
        return False

def main():
    print("🔧 AutoPilot Ventures v5 Fix and Redeploy")
    print("=" * 50)
    
    stack_name = "autopilot-ventures-F1"
    
    # Step 1: Delete the failed stack
    print(f"\n🗑️  Deleting failed stack: {stack_name}")
    delete_cmd = f"aws cloudformation delete-stack --stack-name {stack_name}"
    if not run_command(delete_cmd, "Deleting failed stack"):
        print("❌ Failed to delete stack. Please check AWS CLI.")
        return
    
    print("⏳ Waiting for stack deletion to complete...")
    print("Please wait a few minutes, then run the deployment again.")
    
    # Step 2: Check ECR repository
    print(f"\n🔍 Checking ECR repository...")
    check_ecr_cmd = "aws ecr describe-repositories --repository-names autopilot-ventures --query 'repositories[0].repositoryName' --output text"
    if not run_command(check_ecr_cmd, "Checking ECR repository"):
        print("❌ ECR repository might not exist. Creating...")
        create_ecr_cmd = "aws ecr create-repository --repository-name autopilot-ventures"
        run_command(create_ecr_cmd, "Creating ECR repository")
    
    # Step 3: Re-authenticate with ECR
    print(f"\n🔐 Re-authenticating with ECR...")
    auth_cmd = "aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 160277203814.dkr.ecr.us-east-1.amazonaws.com"
    run_command(auth_cmd, "Re-authenticating with ECR")
    
    # Step 4: Re-push image
    print(f"\n📦 Re-pushing Docker image...")
    push_cmd = "docker push 160277203814.dkr.ecr.us-east-1.amazonaws.com/autopilot-ventures:latest"
    if not run_command(push_cmd, "Re-pushing Docker image"):
        print("❌ Failed to push image. Please check Docker and ECR.")
        return
    
    # Step 5: Create stack with fixes
    print(f"\n🚀 Creating stack with fixes...")
    create_stack_cmd = f"""aws cloudformation create-stack \
        --stack-name {stack_name} \
        --template-body file://cloud-deployment.yml \
        --capabilities CAPABILITY_NAMED_IAM \
        --parameters \
            ParameterKey=Environment,ParameterValue=production \
            ParameterKey=AutonomyLevel,ParameterValue=fully_autonomous \
            ParameterKey=BudgetThreshold,ParameterValue=50"""
    
    if not run_command(create_stack_cmd, f"Creating CloudFormation stack: {stack_name}"):
        print("❌ Stack creation failed.")
        return
    
    print(f"\n🎉 Redeployment initiated!")
    print(f"Stack name: {stack_name}")
    print(f"Monitor with: aws cloudformation describe-stacks --stack-name {stack_name}")

if __name__ == "__main__":
    main() 
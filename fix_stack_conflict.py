#!/usr/bin/env python3
"""
Fix Stack Conflict Script
Handles the naming conflict issue and redeploys the Phase 3 stack.
"""

import boto3
import logging
import time
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StackConflictFixer:
    """Handles stack naming conflicts and redeployment."""
    
    def __init__(self, region: str = 'us-east-1'):
        self.region = region
        self.stack_name = 'autopilot-ventures-3'
        
        # Initialize AWS clients
        self.cloudformation = boto3.client('cloudformation', region_name=region)
        self.ecs = boto3.client('ecs', region_name=region)
        
        logger.info(f"Initialized conflict fixer for stack: {self.stack_name}")
    
    def check_stack_status(self) -> str:
        """Check the current status of the stack."""
        try:
            response = self.cloudformation.describe_stacks(
                StackName=self.stack_name
            )
            status = response['Stacks'][0]['StackStatus']
            logger.info(f"Stack status: {status}")
            return status
        except Exception as e:
            logger.info(f"Stack does not exist or error: {e}")
            return 'DOES_NOT_EXIST'
    
    def delete_failed_stack(self) -> bool:
        """Delete the failed stack to clean up resources."""
        logger.info(f"Deleting failed stack: {self.stack_name}")
        
        try:
            response = self.cloudformation.delete_stack(
                StackName=self.stack_name
            )
            logger.info(f"Stack deletion initiated: {response['ResponseMetadata']['RequestId']}")
            
            # Wait for deletion to complete
            return self.wait_for_stack_deletion()
            
        except Exception as e:
            logger.error(f"Failed to delete stack: {e}")
            return False
    
    def wait_for_stack_deletion(self, timeout_minutes: int = 30) -> bool:
        """Wait for stack deletion to complete."""
        logger.info(f"Waiting for stack {self.stack_name} to be deleted...")
        
        start_time = time.time()
        timeout_seconds = timeout_minutes * 60
        
        while time.time() - start_time < timeout_seconds:
            try:
                response = self.cloudformation.describe_stacks(
                    StackName=self.stack_name
                )
                
                stack_status = response['Stacks'][0]['StackStatus']
                logger.info(f"Stack status: {stack_status}")
                
                if stack_status == 'DELETE_COMPLETE':
                    logger.info(f"✅ Stack {self.stack_name} deleted successfully")
                    return True
                elif stack_status in ['DELETE_FAILED', 'ROLLBACK_COMPLETE']:
                    logger.error(f"❌ Stack deletion failed: {stack_status}")
                    return False
                
                time.sleep(30)  # Wait 30 seconds before checking again
                
            except self.cloudformation.exceptions.ClientError as e:
                if 'does not exist' in str(e):
                    logger.info(f"✅ Stack {self.stack_name} no longer exists")
                    return True
                else:
                    logger.error(f"Error checking stack status: {e}")
                    time.sleep(30)
        
        logger.error(f"⏰ Timeout waiting for stack deletion")
        return False
    
    def check_existing_clusters(self):
        """Check for existing ECS clusters that might conflict."""
        logger.info("Checking for existing ECS clusters...")
        
        try:
            response = self.ecs.list_clusters()
            
            conflicting_clusters = []
            for cluster_arn in response['clusterArns']:
                cluster_name = cluster_arn.split('/')[-1]
                if 'autopilot-ventures-phase3' in cluster_name:
                    conflicting_clusters.append(cluster_name)
                    logger.warning(f"⚠️  Found conflicting cluster: {cluster_name}")
            
            if conflicting_clusters:
                logger.warning(f"Found {len(conflicting_clusters)} potentially conflicting clusters:")
                for cluster in conflicting_clusters:
                    logger.warning(f"  - {cluster}")
            else:
                logger.info("✅ No conflicting clusters found")
            
            return conflicting_clusters
            
        except Exception as e:
            logger.error(f"Error checking clusters: {e}")
            return []
    
    def create_stack_with_unique_name(self) -> str:
        """Create stack with a unique name to avoid conflicts."""
        import subprocess
        
        # Generate unique stack name
        timestamp = datetime.utcnow().strftime('%Y%m%d-%H%M%S')
        unique_stack_name = f"autopilot-ventures-3-{timestamp}"
        
        logger.info(f"Creating stack with unique name: {unique_stack_name}")
        
        try:
            # Use AWS CLI to create stack with unique name
            command = [
                'aws', 'cloudformation', 'create-stack',
                '--stack-name', unique_stack_name,
                '--template-body', 'file://cloud-deployment.yml',
                '--capabilities', 'CAPABILITY_NAMED_IAM',
                '--parameters',
                'ParameterKey=Environment,ParameterValue=production',
                'ParameterKey=AutonomyLevel,ParameterValue=fully_autonomous',
                'ParameterKey=BudgetThreshold,ParameterValue=50'
            ]
            
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            
            logger.info(f"✅ Stack creation initiated: {unique_stack_name}")
            logger.info(f"Command output: {result.stdout}")
            
            return unique_stack_name
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Stack creation failed: {e}")
            logger.error(f"Error output: {e.stderr}")
            raise
    
    def fix_and_deploy(self) -> bool:
        """Main method to fix the conflict and redeploy."""
        logger.info("🔧 Starting conflict resolution and redeployment...")
        
        # Check current stack status
        status = self.check_stack_status()
        
        if status in ['CREATE_FAILED', 'ROLLBACK_COMPLETE']:
            logger.info("Found failed stack, cleaning up...")
            
            # Check for conflicting clusters
            conflicting_clusters = self.check_existing_clusters()
            
            # Delete failed stack
            if not self.delete_failed_stack():
                logger.error("Failed to delete the failed stack")
                return False
        
        elif status == 'DOES_NOT_EXIST':
            logger.info("No existing stack found, proceeding with deployment...")
        
        else:
            logger.info(f"Stack status is {status}, proceeding with deployment...")
        
        # Create new stack with unique name
        try:
            unique_stack_name = self.create_stack_with_unique_name()
            logger.info(f"✅ Deployment initiated with stack name: {unique_stack_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Deployment failed: {e}")
            return False


def main():
    """Main function to fix the stack conflict."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Fix AutoPilot Ventures Phase 3 stack conflict')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    
    args = parser.parse_args()
    
    # Initialize fixer
    fixer = StackConflictFixer(args.region)
    
    try:
        success = fixer.fix_and_deploy()
        
        if success:
            print("\n🎉 Stack conflict resolved and deployment initiated!")
            print("📋 Next steps:")
            print("  1. Monitor the deployment in AWS Console")
            print("  2. Check stack status with: aws cloudformation describe-stacks")
            print("  3. Verify deployment with: python deploy_phase3.py --verify-only")
        else:
            print("\n❌ Failed to resolve conflict and deploy")
            return 1
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 
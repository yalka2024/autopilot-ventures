#!/usr/bin/env python3
"""
ECS Stabilization Fix Script
Handles ECS service stabilization failures and redeploys with improved configuration.
"""

import boto3
import logging
import time
import subprocess
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ECSStabilizationFixer:
    """Handles ECS service stabilization issues."""
    
    def __init__(self, region: str = 'us-east-1'):
        self.region = region
        self.stack_name = 'autopilot-ventures-3'
        
        # Initialize AWS clients
        self.cloudformation = boto3.client('cloudformation', region_name=region)
        self.ecs = boto3.client('ecs', region_name=region)
        self.logs = boto3.client('logs', region_name=region)
        
        logger.info(f"Initialized ECS stabilization fixer for stack: {self.stack_name}")
    
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
    
    def check_ecs_services(self):
        """Check for existing ECS services that might conflict."""
        logger.info("Checking for existing ECS services...")
        
        try:
            # List all clusters
            clusters_response = self.ecs.list_clusters()
            
            for cluster_arn in clusters_response['clusterArns']:
                cluster_name = cluster_arn.split('/')[-1]
                if 'autopilot-ventures' in cluster_name:
                    logger.info(f"Found cluster: {cluster_name}")
                    
                    # List services in this cluster
                    try:
                        services_response = self.ecs.list_services(cluster=cluster_name)
                        
                        for service_arn in services_response['serviceArns']:
                            service_name = service_arn.split('/')[-1]
                            logger.warning(f"⚠️  Found service: {service_name} in cluster {cluster_name}")
                            
                            # Get service details
                            service_response = self.ecs.describe_services(
                                cluster=cluster_name,
                                services=[service_name]
                            )
                            
                            if service_response['services']:
                                service = service_response['services'][0]
                                logger.warning(f"  Status: {service['status']}")
                                logger.warning(f"  Desired Count: {service['desiredCount']}")
                                logger.warning(f"  Running Count: {service['runningCount']}")
                                
                    except Exception as e:
                        logger.warning(f"Could not check services in cluster {cluster_name}: {e}")
            
        except Exception as e:
            logger.error(f"Error checking ECS services: {e}")
    
    def create_stack_with_fixes(self) -> str:
        """Create stack with the improved configuration."""
        logger.info(f"Creating stack with stabilization fixes: {self.stack_name}")
        
        try:
            # Use AWS CLI to create stack with improved configuration
            command = [
                'aws', 'cloudformation', 'create-stack',
                '--stack-name', self.stack_name,
                '--template-body', 'file://cloud-deployment.yml',
                '--capabilities', 'CAPABILITY_NAMED_IAM',
                '--parameters',
                'ParameterKey=Environment,ParameterValue=production',
                'ParameterKey=AutonomyLevel,ParameterValue=fully_autonomous',
                'ParameterKey=BudgetThreshold,ParameterValue=50'
            ]
            
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            
            logger.info(f"✅ Stack creation initiated: {self.stack_name}")
            logger.info(f"Command output: {result.stdout}")
            
            return self.stack_name
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Stack creation failed: {e}")
            logger.error(f"Error output: {e.stderr}")
            raise
    
    def wait_for_stack_completion(self, timeout_minutes: int = 45) -> bool:
        """Wait for stack to complete creation with improved monitoring."""
        logger.info(f"Waiting for stack {self.stack_name} to complete...")
        
        start_time = time.time()
        timeout_seconds = timeout_minutes * 60
        
        while time.time() - start_time < timeout_seconds:
            try:
                response = self.cloudformation.describe_stacks(
                    StackName=self.stack_name
                )
                
                stack_status = response['Stacks'][0]['StackStatus']
                logger.info(f"Stack status: {stack_status}")
                
                if stack_status in ['CREATE_COMPLETE', 'UPDATE_COMPLETE']:
                    logger.info(f"✅ Stack {self.stack_name} completed successfully!")
                    return True
                elif stack_status in ['CREATE_FAILED', 'UPDATE_FAILED', 'ROLLBACK_COMPLETE']:
                    logger.error(f"❌ Stack {self.stack_name} failed: {stack_status}")
                    return False
                elif stack_status in ['CREATE_IN_PROGRESS', 'UPDATE_IN_PROGRESS']:
                    logger.info(f"⏳ Stack {self.stack_name} still in progress...")
                    
                    # Check ECS service status if stack is in progress
                    self.check_ecs_services()
                
                time.sleep(30)  # Wait 30 seconds before checking again
                
            except Exception as e:
                logger.error(f"Error checking stack status: {e}")
                time.sleep(30)
        
        logger.error(f"⏰ Timeout waiting for stack {self.stack_name}")
        return False
    
    def verify_ecs_service(self) -> bool:
        """Verify that the ECS service is running properly."""
        logger.info("Verifying ECS service...")
        
        try:
            # Find the cluster
            clusters_response = self.ecs.list_clusters()
            target_cluster = None
            
            for cluster_arn in clusters_response['clusterArns']:
                cluster_name = cluster_arn.split('/')[-1]
                if 'autopilot-ventures-1' in cluster_name:
                    target_cluster = cluster_name
                    break
            
            if not target_cluster:
                logger.error("❌ Could not find target cluster")
                return False
            
            logger.info(f"Found target cluster: {target_cluster}")
            
            # Check services in the cluster
            services_response = self.ecs.list_services(cluster=target_cluster)
            
            if not services_response['serviceArns']:
                logger.error("❌ No services found in cluster")
                return False
            
            for service_arn in services_response['serviceArns']:
                service_name = service_arn.split('/')[-1]
                logger.info(f"Checking service: {service_name}")
                
                service_response = self.ecs.describe_services(
                    cluster=target_cluster,
                    services=[service_name]
                )
                
                if service_response['services']:
                    service = service_response['services'][0]
                    logger.info(f"Service status: {service['status']}")
                    logger.info(f"Desired count: {service['desiredCount']}")
                    logger.info(f"Running count: {service['runningCount']}")
                    logger.info(f"Pending count: {service['pendingCount']}")
                    
                    if service['status'] == 'ACTIVE' and service['runningCount'] > 0:
                        logger.info("✅ ECS service is running properly")
                        return True
                    else:
                        logger.warning(f"⚠️  Service not fully stable: {service['status']}")
                        return False
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error verifying ECS service: {e}")
            return False
    
    def fix_and_deploy(self) -> bool:
        """Main method to fix the stabilization issue and redeploy."""
        logger.info("🔧 Starting ECS stabilization fix and redeployment...")
        
        # Check current stack status
        status = self.check_stack_status()
        
        if status in ['CREATE_FAILED', 'ROLLBACK_COMPLETE']:
            logger.info("Found failed stack, cleaning up...")
            
            # Check for existing ECS services
            self.check_ecs_services()
            
            # Delete failed stack
            if not self.delete_failed_stack():
                logger.error("Failed to delete the failed stack")
                return False
        
        elif status == 'DOES_NOT_EXIST':
            logger.info("No existing stack found, proceeding with deployment...")
        
        else:
            logger.info(f"Stack status is {status}, proceeding with deployment...")
        
        # Create new stack with fixes
        try:
            stack_name = self.create_stack_with_fixes()
            logger.info(f"✅ Deployment initiated with stack name: {stack_name}")
            
            # Wait for completion
            success = self.wait_for_stack_completion()
            
            if success:
                # Verify ECS service
                service_ok = self.verify_ecs_service()
                
                if service_ok:
                    logger.info("✅ ECS service verification passed")
                    return True
                else:
                    logger.warning("⚠️  ECS service verification failed")
                    return False
            else:
                logger.error("❌ Stack deployment failed")
                return False
            
        except Exception as e:
            logger.error(f"❌ Deployment failed: {e}")
            return False


def main():
    """Main function to fix the ECS stabilization issue."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Fix AutoPilot Ventures ECS stabilization')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    
    args = parser.parse_args()
    
    # Initialize fixer
    fixer = ECSStabilizationFixer(args.region)
    
    try:
        success = fixer.fix_and_deploy()
        
        if success:
            print("\n🎉 ECS stabilization fix completed successfully!")
            print("📋 Next steps:")
            print("  1. Monitor the ECS service in AWS Console")
            print("  2. Check service logs: aws logs tail /ecs/master-agent-1-production-{stack-name}")
            print("  3. Test health endpoint: curl http://{service-ip}:8000/health")
            print("  4. Verify deployment with: python deploy_phase3.py --verify-only")
        else:
            print("\n❌ Failed to fix ECS stabilization")
            return 1
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 
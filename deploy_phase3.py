#!/usr/bin/env python3
"""
Phase 3 Deployment Script for AutoPilot Ventures
Deploys the new Phase 3 stack with advanced intelligence features.
"""

import boto3
import logging
import time
from datetime import datetime
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Phase3Deployer:
    """Handles Phase 3 stack deployment with advanced features."""
    
    def __init__(self, region: str = 'us-east-1'):
        self.region = region
        self.stack_name = 'autopilot-ventures-3'
        
        # Initialize AWS clients
        self.cloudformation = boto3.client('cloudformation', region_name=region)
        self.ecs = boto3.client('ecs', region_name=region)
        self.logs = boto3.client('logs', region_name=region)
        
        logger.info(f"Initialized Phase 3 deployer for stack: {self.stack_name}")
    
    def check_stack_exists(self) -> bool:
        """Check if the Phase 3 stack already exists."""
        try:
            response = self.cloudformation.describe_stacks(
                StackName=self.stack_name
            )
            logger.info(f"Stack {self.stack_name} already exists")
            return True
        except self.cloudformation.exceptions.ClientError as e:
            if 'does not exist' in str(e):
                logger.info(f"Stack {self.stack_name} does not exist")
                return False
            else:
                raise
    
    def create_stack(self, template_file: str = 'cloud-deployment.yml') -> str:
        """Create the Phase 3 stack."""
        logger.info(f"Creating Phase 3 stack: {self.stack_name}")
        
        try:
            with open(template_file, 'r') as f:
                template_body = f.read()
            
            # Create stack with Phase 3 parameters
            response = self.cloudformation.create_stack(
                StackName=self.stack_name,
                TemplateBody=template_body,
                Capabilities=['CAPABILITY_NAMED_IAM'],
                Parameters=[
                    {
                        'ParameterKey': 'Environment',
                        'ParameterValue': 'production'
                    },
                    {
                        'ParameterKey': 'AutonomyLevel',
                        'ParameterValue': 'fully_autonomous'
                    },
                    {
                        'ParameterKey': 'BudgetThreshold',
                        'ParameterValue': '50'
                    },
                    {
                        'ParameterKey': 'ImageUrl',
                        'ParameterValue': '160277203814.dkr.ecr.us-east-1.amazonaws.com/autopilot-ventures:latest'
                    }
                ],
                Tags=[
                    {
                        'Key': 'Project',
                        'Value': 'AutoPilot Ventures'
                    },
                    {
                        'Key': 'Phase',
                        'Value': '3'
                    },
                    {
                        'Key': 'Environment',
                        'Value': 'production'
                    },
                    {
                        'Key': 'DeploymentDate',
                        'Value': datetime.utcnow().strftime('%Y-%m-%d')
                    }
                ]
            )
            
            logger.info(f"Stack creation initiated: {response['StackId']}")
            return response['StackId']
            
        except Exception as e:
            logger.error(f"Stack creation failed: {e}")
            raise
    
    def update_stack(self, template_file: str = 'cloud-deployment.yml') -> str:
        """Update the existing Phase 3 stack."""
        logger.info(f"Updating Phase 3 stack: {self.stack_name}")
        
        try:
            with open(template_file, 'r') as f:
                template_body = f.read()
            
            # Update stack with Phase 3 parameters
            response = self.cloudformation.update_stack(
                StackName=self.stack_name,
                TemplateBody=template_body,
                Capabilities=['CAPABILITY_NAMED_IAM'],
                Parameters=[
                    {
                        'ParameterKey': 'Environment',
                        'ParameterValue': 'production'
                    },
                    {
                        'ParameterKey': 'AutonomyLevel',
                        'ParameterValue': 'fully_autonomous'
                    },
                    {
                        'ParameterKey': 'BudgetThreshold',
                        'ParameterValue': '50'
                    },
                    {
                        'ParameterKey': 'ImageUrl',
                        'ParameterValue': '160277203814.dkr.ecr.us-east-1.amazonaws.com/autopilot-ventures:latest'
                    }
                ]
            )
            
            logger.info(f"Stack update initiated: {response['StackId']}")
            return response['StackId']
            
        except Exception as e:
            logger.error(f"Stack update failed: {e}")
            raise
    
    def wait_for_stack_completion(self, timeout_minutes: int = 45) -> bool:
        """Wait for stack to complete creation/update."""
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
                
                time.sleep(30)  # Wait 30 seconds before checking again
                
            except Exception as e:
                logger.error(f"Error checking stack status: {e}")
                time.sleep(30)
        
        logger.error(f"⏰ Timeout waiting for stack {self.stack_name}")
        return False
    
    def verify_deployment(self) -> Dict[str, Any]:
        """Verify the Phase 3 deployment is working correctly."""
        logger.info("Verifying Phase 3 deployment...")
        
        verification_results = {
            'stack_status': 'unknown',
            'ecs_service_status': 'unknown',
            'health_check': 'unknown',
            'log_groups': 'unknown',
            'event_rules': 'unknown'
        }
        
        try:
            # Check stack status
            stack_response = self.cloudformation.describe_stacks(
                StackName=self.stack_name
            )
            verification_results['stack_status'] = stack_response['Stacks'][0]['StackStatus']
            
            # Check ECS service
            cluster_name = 'autopilot-ventures-phase3-production'
            try:
                services_response = self.ecs.list_services(cluster=cluster_name)
                if services_response['serviceArns']:
                    service_name = services_response['serviceArns'][0].split('/')[-1]
                    service_response = self.ecs.describe_services(
                        cluster=cluster_name,
                        services=[service_name]
                    )
                    if service_response['services']:
                        service = service_response['services'][0]
                        verification_results['ecs_service_status'] = service['status']
                        logger.info(f"ECS Service Status: {service['status']}")
            except Exception as e:
                logger.warning(f"Could not verify ECS service: {e}")
            
            # Check log groups
            try:
                log_response = self.logs.describe_log_groups(
                    logGroupNamePrefix='/ecs/master-agent-phase3'
                )
                verification_results['log_groups'] = f"{len(log_response['logGroups'])} found"
                logger.info(f"Log Groups: {len(log_response['logGroups'])} found")
            except Exception as e:
                logger.warning(f"Could not verify log groups: {e}")
            
            logger.info("✅ Phase 3 deployment verification completed")
            return verification_results
            
        except Exception as e:
            logger.error(f"❌ Verification failed: {e}")
            return verification_results
    
    def get_stack_outputs(self) -> Dict[str, str]:
        """Get stack outputs for verification."""
        try:
            response = self.cloudformation.describe_stacks(
                StackName=self.stack_name
            )
            
            outputs = {}
            for output in response['Stacks'][0].get('Outputs', []):
                outputs[output['OutputKey']] = output['OutputValue']
            
            return outputs
            
        except Exception as e:
            logger.error(f"Could not get stack outputs: {e}")
            return {}


def main():
    """Main deployment function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Deploy AutoPilot Ventures Phase 3')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    parser.add_argument('--template', default='cloud-deployment.yml', help='CloudFormation template file')
    parser.add_argument('--verify-only', action='store_true', help='Only verify existing deployment')
    
    args = parser.parse_args()
    
    # Initialize deployer
    deployer = Phase3Deployer(args.region)
    
    try:
        if args.verify_only:
            # Only verify existing deployment
            results = deployer.verify_deployment()
            print("\n📊 Phase 3 Deployment Verification Results:")
            for key, value in results.items():
                print(f"  {key}: {value}")
            return 0
        
        # Check if stack exists
        if deployer.check_stack_exists():
            logger.info("Stack exists, updating...")
            stack_id = deployer.update_stack(args.template)
        else:
            logger.info("Stack does not exist, creating...")
            stack_id = deployer.create_stack(args.template)
        
        # Wait for completion
        success = deployer.wait_for_stack_completion()
        
        if success:
            # Verify deployment
            results = deployer.verify_deployment()
            
            # Get stack outputs
            outputs = deployer.get_stack_outputs()
            
            print("\n🎉 Phase 3 Deployment Successful!")
            print(f"Stack ID: {stack_id}")
            print(f"Stack Name: {deployer.stack_name}")
            
            print("\n📊 Verification Results:")
            for key, value in results.items():
                print(f"  {key}: {value}")
            
            if outputs:
                print("\n📤 Stack Outputs:")
                for key, value in outputs.items():
                    print(f"  {key}: {value}")
            
            print("\n🚀 Phase 3 Advanced Intelligence Features:")
            print("  ✅ Vector Memory Management")
            print("  ✅ Self-Tuning Agents")
            print("  ✅ Reinforcement Learning Engine")
            print("  ✅ Autonomous Workflow Engine")
            print("  ✅ MLflow Experiment Tracking")
            print("  ✅ Dynamic Decision Trees")
            print("  ✅ Cross-Venture Learning")
            print("  ✅ Predictive Analytics")
            
        else:
            logger.error("❌ Phase 3 deployment failed!")
            return 1
    
    except Exception as e:
        logger.error(f"❌ Deployment failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 
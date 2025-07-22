#!/usr/bin/env python3
"""
Stack Migration Script for AutoPilot Ventures
Safely migrates data and configuration between CloudFormation stacks.
"""

import boto3
import json
import logging
from datetime import datetime
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StackMigrator:
    """Handles safe migration between CloudFormation stacks."""
    
    def __init__(self, source_stack: str = 'autopilot-ventures', target_stack: str = 'autopilot-ventures-3', region: str = 'us-east-1'):
        self.source_stack = source_stack
        self.target_stack = target_stack
        self.region = region
        
        # Initialize AWS clients
        self.cloudformation = boto3.client('cloudformation', region_name=region)
        self.ecs = boto3.client('ecs', region_name=region)
        self.logs = boto3.client('logs', region_name=region)
        self.events = boto3.client('events', region_name=region)
        self.iam = boto3.client('iam', region_name=region)
        
        logger.info(f"Initialized migrator: {source_stack} -> {target_stack}")
    
    def export_stack_data(self) -> Dict[str, Any]:
        """Export all data from source stack."""
        logger.info("Exporting data from source stack...")
        
        exported_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'source_stack': self.source_stack,
            'target_stack': self.target_stack,
            'ecs_services': {},
            'log_groups': {},
            'event_rules': {},
            'iam_roles': {}
        }
        
        try:
            # Export ECS service configurations
            exported_data['ecs_services'] = self._export_ecs_services()
            
            # Export CloudWatch log groups
            exported_data['log_groups'] = self._export_log_groups()
            
            # Export EventBridge rules
            exported_data['event_rules'] = self._export_event_rules()
            
            # Export IAM roles
            exported_data['iam_roles'] = self._export_iam_roles()
            
            logger.info("Data export completed successfully")
            return exported_data
            
        except Exception as e:
            logger.error(f"Export failed: {e}")
            raise
    
    def _export_ecs_services(self) -> Dict[str, Any]:
        """Export ECS service configurations."""
        services_data = {}
        
        try:
            # Get cluster name from source stack
            cluster_name = f"autopilot-ventures-3-production-{self.source_stack}"
            
            # List services in cluster
            response = self.ecs.list_services(cluster=cluster_name)
            
            for service_arn in response['serviceArns']:
                service_name = service_arn.split('/')[-1]
                
                # Get service details
                service_response = self.ecs.describe_services(
                    cluster=cluster_name,
                    services=[service_name]
                )
                
                if service_response['services']:
                    service = service_response['services'][0]
                    services_data[service_name] = {
                        'taskDefinition': service['taskDefinition'],
                        'desiredCount': service['desiredCount'],
                        'launchType': service['launchType'],
                        'networkConfiguration': service['networkConfiguration']
                    }
            
            logger.info(f"Exported {len(services_data)} ECS services")
            return services_data
            
        except Exception as e:
            logger.error(f"ECS export failed: {e}")
            return {}
    
    def _export_log_groups(self) -> Dict[str, Any]:
        """Export CloudWatch log groups."""
        log_groups_data = {}
        
        try:
            # List log groups with autopilot prefix
            response = self.logs.describe_log_groups(
                logGroupNamePrefix=f'/ecs/master-agent-3'
            )
            
            for log_group in response['logGroups']:
                log_group_name = log_group['logGroupName']
                log_groups_data[log_group_name] = {
                    'retentionInDays': log_group.get('retentionInDays', 30),
                    'metricFilterCount': log_group.get('metricFilterCount', 0)
                }
            
            logger.info(f"Exported {len(log_groups_data)} log groups")
            return log_groups_data
            
        except Exception as e:
            logger.error(f"Log groups export failed: {e}")
            return {}
    
    def _export_event_rules(self) -> Dict[str, Any]:
        """Export EventBridge rules."""
        rules_data = {}
        
        try:
            # List rules with autopilot prefix
            response = self.events.list_rules(
                NamePrefix='autopilot'
            )
            
            for rule in response['Rules']:
                rule_name = rule['Name']
                rules_data[rule_name] = {
                    'scheduleExpression': rule.get('ScheduleExpression'),
                    'state': rule['State'],
                    'description': rule.get('Description', '')
                }
            
            logger.info(f"Exported {len(rules_data)} event rules")
            return rules_data
            
        except Exception as e:
            logger.error(f"Event rules export failed: {e}")
            return {}
    
    def _export_iam_roles(self) -> Dict[str, Any]:
        """Export IAM roles."""
        roles_data = {}
        
        try:
            # List roles with autopilot prefix
            response = self.iam.list_roles(
                PathPrefix='/'
            )
            
            for role in response['Roles']:
                role_name = role['RoleName']
                if 'autopilot' in role_name.lower():
                    # Get role policies
                    policies_response = self.iam.list_attached_role_policies(
                        RoleName=role_name
                    )
                    
                    roles_data[role_name] = {
                        'arn': role['Arn'],
                        'attachedPolicies': [p['PolicyArn'] for p in policies_response['AttachedPolicies']]
                    }
            
            logger.info(f"Exported {len(roles_data)} IAM roles")
            return roles_data
            
        except Exception as e:
            logger.error(f"IAM roles export failed: {e}")
            return {}
    
    def save_export_data(self, data: Dict[str, Any], filename: str = None):
        """Save exported data to file."""
        if not filename:
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            filename = f"stack_migration_{self.source_stack}_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        logger.info(f"Export data saved to {filename}")
        return filename
    
    def create_new_stack(self, template_file: str):
        """Create new stack with the target name."""
        logger.info(f"Creating new stack: {self.target_stack}")
        
        try:
            with open(template_file, 'r') as f:
                template_body = f.read()
            
            # Create new stack
            response = self.cloudformation.create_stack(
                StackName=self.target_stack,
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
                    }
                ]
            )
            
            logger.info(f"Stack creation initiated: {response['StackId']}")
            return response['StackId']
            
        except Exception as e:
            logger.error(f"Stack creation failed: {e}")
            raise
    
    def wait_for_stack_completion(self, stack_name: str, timeout_minutes: int = 30):
        """Wait for stack to complete creation/update."""
        logger.info(f"Waiting for stack {stack_name} to complete...")
        
        import time
        start_time = time.time()
        timeout_seconds = timeout_minutes * 60
        
        while time.time() - start_time < timeout_seconds:
            try:
                response = self.cloudformation.describe_stacks(
                    StackName=stack_name
                )
                
                stack_status = response['Stacks'][0]['StackStatus']
                logger.info(f"Stack status: {stack_status}")
                
                if stack_status in ['CREATE_COMPLETE', 'UPDATE_COMPLETE']:
                    logger.info(f"Stack {stack_name} completed successfully")
                    return True
                elif stack_status in ['CREATE_FAILED', 'UPDATE_FAILED', 'ROLLBACK_COMPLETE']:
                    logger.error(f"Stack {stack_name} failed: {stack_status}")
                    return False
                
                time.sleep(30)  # Wait 30 seconds before checking again
                
            except Exception as e:
                logger.error(f"Error checking stack status: {e}")
                time.sleep(30)
        
        logger.error(f"Timeout waiting for stack {stack_name}")
        return False


def main():
    """Main migration function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Migrate AutoPilot Ventures stack')
    parser.add_argument('--source', required=True, help='Source stack name')
    parser.add_argument('--target', required=True, help='Target stack name')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    parser.add_argument('--template', default='cloud-deployment.yml', help='CloudFormation template file')
    parser.add_argument('--export-only', action='store_true', help='Only export data, do not create new stack')
    
    args = parser.parse_args()
    
    # Initialize migrator
    migrator = StackMigrator(args.source, args.target, args.region)
    
    try:
        # Export data from source stack
        exported_data = migrator.export_stack_data()
        
        # Save export data
        filename = migrator.save_export_data(exported_data)
        
        if not args.export_only:
            # Create new stack
            stack_id = migrator.create_new_stack(args.template)
            
            # Wait for completion
            success = migrator.wait_for_stack_completion(args.target)
            
            if success:
                logger.info("Migration completed successfully!")
                logger.info(f"Export data: {filename}")
                logger.info(f"New stack: {stack_id}")
            else:
                logger.error("Migration failed!")
        else:
            logger.info(f"Export completed: {filename}")
    
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 
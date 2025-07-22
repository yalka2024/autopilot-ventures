#!/usr/bin/env python3
"""
Stack Status Checker for AutoPilot Ventures
Checks status of both old and new Phase 3 stacks.
"""

import boto3
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_stack_status(stack_name: str, region: str = 'us-east-1') -> dict:
    """Check the status of a specific stack."""
    cloudformation = boto3.client('cloudformation', region_name=region)
    
    try:
        response = cloudformation.describe_stacks(StackName=stack_name)
        stack = response['Stacks'][0]
        
        return {
            'exists': True,
            'name': stack['StackName'],
            'status': stack['StackStatus'],
            'creation_time': stack['CreationTime'],
            'last_updated': stack.get('LastUpdatedTime'),
            'description': stack.get('Description', 'No description'),
            'outputs': {output['OutputKey']: output['OutputValue'] for output in stack.get('Outputs', [])}
        }
    except cloudformation.exceptions.ClientError as e:
        if 'does not exist' in str(e):
            return {
                'exists': False,
                'name': stack_name,
                'status': 'DOES_NOT_EXIST',
                'error': str(e)
            }
        else:
            return {
                'exists': False,
                'name': stack_name,
                'status': 'ERROR',
                'error': str(e)
            }

def main():
    """Check status of both stacks."""
    stacks_to_check = [
        'autopilot-ventures',           # Old stack
        'autopilot-ventures-3'          # New stack with number 3
    ]
    
    print("🔍 AutoPilot Ventures Stack Status Check")
    print("=" * 50)
    
    for stack_name in stacks_to_check:
        print(f"\n📋 Checking stack: {stack_name}")
        print("-" * 30)
        
        status = check_stack_status(stack_name)
        
        if status['exists']:
            print(f"✅ Status: {status['status']}")
            print(f"📅 Created: {status['creation_time']}")
            if status['last_updated']:
                print(f"🔄 Updated: {status['last_updated']}")
            print(f"📝 Description: {status['description']}")
            
            if status['outputs']:
                print("📤 Outputs:")
                for key, value in status['outputs'].items():
                    print(f"  {key}: {value}")
        else:
            print(f"❌ Status: {status['status']}")
            if 'error' in status:
                print(f"⚠️  Error: {status['error']}")
    
    print("\n" + "=" * 50)
    print("🎯 Migration Recommendations:")
    print("=" * 50)
    
    old_status = check_stack_status('autopilot-ventures')
    new_status = check_stack_status('autopilot-ventures-1')
    
    if old_status['exists'] and not new_status['exists']:
        print("✅ Ready to create new stack with number 3")
        print("   Run: python deploy_phase3.py")
    elif old_status['exists'] and new_status['exists']:
        print("✅ Both stacks exist - ready for migration")
        print("   Run: python migrate_stack.py --source autopilot-ventures --target autopilot-ventures-3")
    elif not old_status['exists'] and new_status['exists']:
        print("✅ Only stack with number 3 exists - migration complete")
    else:
        print("❌ No stacks found - need to create initial deployment")
        print("   Run: python deploy_phase3.py")

if __name__ == "__main__":
    main() 
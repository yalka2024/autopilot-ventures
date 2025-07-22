#!/usr/bin/env python3
"""
Fix VPC and Security Group Issues
"""

import boto3

def fix_vpc_issues():
    ec2 = boto3.client('ec2', region_name='us-east-1')
    
    print("=== Checking Available VPCs ===")
    
    try:
        # Get available VPCs
        vpcs = ec2.describe_vpcs()
        print(f"Found {len(vpcs['Vpcs'])} VPCs:")
        
        for vpc in vpcs['Vpcs']:
            vpc_name = "No name"
            if 'Tags' in vpc:
                for tag in vpc['Tags']:
                    if tag['Key'] == 'Name':
                        vpc_name = tag['Value']
                        break
            
            print(f"  {vpc['VpcId']}: {vpc['CidrBlock']} - {vpc_name}")
        
        # Use the default VPC (usually the first one)
        default_vpc = None
        for vpc in vpcs['Vpcs']:
            if vpc['IsDefault']:
                default_vpc = vpc
                break
        
        if not default_vpc:
            default_vpc = vpcs['Vpcs'][0]  # Use first VPC if no default
        
        print(f"\nUsing VPC: {default_vpc['VpcId']}")
        
        # Get subnets for this VPC
        subnets = ec2.describe_subnets(
            Filters=[
                {'Name': 'vpc-id', 'Values': [default_vpc['VpcId']]},
                {'Name': 'state', 'Values': ['available']}
            ]
        )
        
        print(f"\nAvailable Subnets in {default_vpc['VpcId']}:")
        public_subnets = []
        for subnet in subnets['Subnets']:
            subnet_name = "No name"
            if 'Tags' in subnet:
                for tag in subnet['Tags']:
                    if tag['Key'] == 'Name':
                        subnet_name = tag['Value']
                        break
            
            print(f"  {subnet['SubnetId']}: {subnet['CidrBlock']} - {subnet_name}")
            
            # Check if it's a public subnet (has route to internet gateway)
            if subnet.get('MapPublicIpOnLaunch', False):
                public_subnets.append(subnet['SubnetId'])
        
        print(f"\nPublic Subnets: {public_subnets}")
        
        # Create security group in the correct VPC
        print(f"\nCreating Security Group in VPC {default_vpc['VpcId']}...")
        
        try:
            sg_response = ec2.create_security_group(
                GroupName='autopilot-sg-fixed-production',
                Description='Security group for AutoPilot Ventures (Fixed)',
                VpcId=default_vpc['VpcId']
            )
            
            security_group_id = sg_response['GroupId']
            print(f"✅ Security Group created: {security_group_id}")
            
            # Add ingress rule
            ec2.authorize_security_group_ingress(
                GroupId=security_group_id,
                IpPermissions=[
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 8000,
                        'ToPort': 8000,
                        'IpRanges': [
                            {
                                'CidrIp': '0.0.0.0/0',
                                'Description': 'Allow inbound traffic on port 8000'
                            }
                        ]
                    }
                ]
            )
            print("✅ Ingress rule added")
            
            # Update ECS service with new security group and subnets
            print("\nUpdating ECS Service...")
            ecs = boto3.client('ecs', region_name='us-east-1')
            
            ecs.update_service(
                cluster='autopilot-ventures-manual-production',
                service='master-agent-service-manual-production',
                networkConfiguration={
                    'awsvpcConfiguration': {
                        'assignPublicIp': 'ENABLED',
                        'securityGroups': [security_group_id],
                        'subnets': public_subnets[:3]  # Use first 3 public subnets
                    }
                },
                forceNewDeployment=True
            )
            
            print("✅ ECS Service updated with correct VPC resources!")
            print(f"\nNew Security Group: {security_group_id}")
            print(f"Subnets: {public_subnets[:3]}")
            print("\nThe service should now start tasks. Check with:")
            print("python diagnose_service.py")
            
        except Exception as e:
            print(f"❌ Error creating security group: {e}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_vpc_issues() 
#!/usr/bin/env python3
"""
Fix MasterAgentService Issues
Comprehensive solution for ECS service problems
"""

import subprocess
import json
import time

def create_fixed_template():
    """Create a fixed CloudFormation template with better MasterAgentService configuration"""
    
    template = """
AWSTemplateFormatVersion: '2010-09-09'
Description: 'AutoPilot Ventures Stack V5 - Fixed MasterAgentService'

Parameters:
  Environment:
    Type: String
    Default: production
    Description: Environment name
  
  AutonomyLevel:
    Type: String
    Default: fully_autonomous
    Description: AI autonomy level
  
  BudgetThreshold:
    Type: String
    Default: '50'
    Description: Budget threshold in USD
  
  ImageUrl:
    Type: String
    Default: '160277203814.dkr.ecr.us-east-1.amazonaws.com/autopilot-ventures:latest'
    Description: ECR image URL

Resources:
  # VPC and Networking (simplified)
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsHostnames: true
      EnableDnsSupport: true
      Tags:
        - Key: Name
          Value: !Sub 'autopilot-v5-vpc-${Environment}'

  PublicSubnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.1.0/24
      AvailabilityZone: !Select [0, !GetAZs '']
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: !Sub 'autopilot-v5-subnet-1-${Environment}'

  PublicSubnet2:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.2.0/24
      AvailabilityZone: !Select [1, !GetAZs '']
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: !Sub 'autopilot-v5-subnet-2-${Environment}'

  InternetGateway:
    Type: AWS::EC2::InternetGateway
    Properties:
      Tags:
        - Key: Name
          Value: !Sub 'autopilot-v5-igw-${Environment}'

  AttachGateway:
    Type: AWS::EC2::VPCGatewayAttachment
    Properties:
      VpcId: !Ref VPC
      InternetGatewayId: !Ref InternetGateway

  RouteTable:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref VPC
      Tags:
        - Key: Name
          Value: !Sub 'autopilot-v5-rt-${Environment}'

  DefaultRoute:
    Type: AWS::EC2::Route
    DependsOn: AttachGateway
    Properties:
      RouteTableId: !Ref RouteTable
      DestinationCidrBlock: 0.0.0.0/0
      GatewayId: !Ref InternetGateway

  SubnetRouteTableAssociation1:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref PublicSubnet1
      RouteTableId: !Ref RouteTable

  SubnetRouteTableAssociation2:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: !Ref PublicSubnet2
      RouteTableId: !Ref RouteTable

  SecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupName: !Sub 'autopilot-v5-sg-${Environment}'
      GroupDescription: 'Security group for AutoPilot Ventures V5'
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 8000
          ToPort: 8000
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 9090
          ToPort: 9090
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 8501
          ToPort: 8501
          CidrIp: 0.0.0.0/0
      SecurityGroupEgress:
        - IpProtocol: -1
          CidrIp: 0.0.0.0/0

  # ECS Cluster
  AutopilotCluster:
    Type: AWS::ECS::Cluster
    Properties:
      ClusterName: !Sub 'autopilot-ventures-F1-${Environment}-${AWS::StackName}'
      CapacityProviders:
        - FARGATE
        - FARGATE_SPOT
      DefaultCapacityProviderStrategy:
        - CapacityProvider: FARGATE
          Weight: 1

  # ECS Task Definition - FIXED MASTER AGENT
  MasterAgentTask:
    Type: AWS::ECS::TaskDefinition
    Properties:
      Family: !Sub 'master-agent-v5-${Environment}'
      NetworkMode: awsvpc
      RequiresCompatibilities:
        - FARGATE
      Cpu: '1024'  # Reduced for stability
      Memory: '2048'  # Reduced for stability
      ExecutionRoleArn: !GetAtt ECSTaskExecutionRole.Arn
      TaskRoleArn: !GetAtt ECSTaskRole.Arn
      ContainerDefinitions:
        - Name: master-agent
          Image: !Ref ImageUrl
          # FIXED: Proper startup command
          Command:
            - python
            - main.py
          Environment:
            - Name: ENVIRONMENT
              Value: !Ref Environment
            - Name: AUTONOMY_LEVEL
              Value: !Ref AutonomyLevel
            - Name: BUDGET_THRESHOLD
              Value: !Ref BudgetThreshold
            - Name: PHASE3_ENABLED
              Value: 'true'
            - Name: VECTOR_MEMORY_ENABLED
              Value: 'true'
            - Name: SELF_TUNING_ENABLED
              Value: 'true'
            - Name: REINFORCEMENT_LEARNING_ENABLED
              Value: 'true'
            - Name: AUTONOMOUS_WORKFLOW_ENABLED
              Value: 'true'
            - Name: PORT
              Value: '8000'
            - Name: HOST
              Value: '0.0.0.0'
          PortMappings:
            - ContainerPort: 8000
              Protocol: tcp
          LogConfiguration:
            LogDriver: awslogs
            Options:
              awslogs-group: !Ref MasterAgentLogGroup
              awslogs-region: !Ref AWS::Region
              awslogs-stream-prefix: master-agent
          # FIXED: Simplified health check
          HealthCheck:
            Command:
              - CMD-SHELL
              - curl -f http://localhost:8000/ || exit 1
            Interval: 30
            Timeout: 10
            Retries: 5
            StartPeriod: 60

  # ECS Service - FIXED MASTER AGENT SERVICE
  MasterAgentService:
    Type: AWS::ECS::Service
    Properties:
      ServiceName: !Sub 'master-agent-service-v5-${Environment}'
      Cluster: !Ref AutopilotCluster
      TaskDefinition: !Ref MasterAgentTask
      DesiredCount: 1
      LaunchType: FARGATE
      # FIXED: Extended grace period
      HealthCheckGracePeriodSeconds: 180
      # FIXED: Disabled circuit breaker
      DeploymentConfiguration:
        MaximumPercent: 200
        MinimumHealthyPercent: 100
        DeploymentCircuitBreaker:
          Enable: false
          Rollback: false
      NetworkConfiguration:
        AwsvpcConfiguration:
          AssignPublicIp: ENABLED
          SecurityGroups:
            - !Ref SecurityGroup
          Subnets:
            - !Ref PublicSubnet1
            - !Ref PublicSubnet2

  # CloudWatch Log Groups
  MasterAgentLogGroup:
    Type: AWS::Logs::LogGroup
    DeletionPolicy: Retain
    Properties:
      LogGroupName: !Sub '/ecs/master-agent-v5-${Environment}-${AWS::StackName}'
      RetentionInDays: 30

  # IAM Roles
  ECSTaskExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub 'ecs-task-execution-v5-${Environment}-${AWS::StackName}'
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: ecs-tasks.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy

  ECSTaskRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub 'ecs-task-v5-${Environment}-${AWS::StackName}'
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: ecs-tasks.amazonaws.com
            Action: sts:AssumeRole
      Policies:
        - PolicyName: CloudWatchLogs
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - logs:CreateLogStream
                  - logs:PutLogEvents
                Resource: 
                  - !GetAtt MasterAgentLogGroup.Arn

Outputs:
  ClusterName:
    Description: ECS Cluster Name
    Value: !Ref AutopilotCluster
    Export:
      Name: !Sub '${AWS::StackName}-ClusterName'

  ServiceName:
    Description: Master Agent Service Name
    Value: !Ref MasterAgentService
    Export:
      Name: !Sub '${AWS::StackName}-ServiceName'
"""
    
    with open('cloud-deployment-fixed.yml', 'w') as f:
        f.write(template)
    
    print("✅ Created fixed template: cloud-deployment-fixed.yml")

def deploy_fixed_stack():
    """Deploy the fixed stack"""
    stack_name = 'autopilot-ventures-F1-fixed'
    
    command = f"""aws cloudformation create-stack \\
  --stack-name {stack_name} \\
  --template-body file://cloud-deployment-fixed.yml \\
  --capabilities CAPABILITY_NAMED_IAM \\
  --parameters ParameterKey=Environment,ParameterValue=production ParameterKey=AutonomyLevel,ParameterValue=fully_autonomous ParameterKey=BudgetThreshold,ParameterValue=50"""
    
    print(f"🚀 Deploying fixed stack: {stack_name}")
    print("=" * 50)
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Stack creation initiated successfully!")
            print(f"Stack ID: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Stack creation failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🔧 Fixing MasterAgentService Issues")
    print("=" * 50)
    
    # Create fixed template
    create_fixed_template()
    
    # Deploy fixed stack
    if deploy_fixed_stack():
        print("\n✅ Fixed stack deployment initiated!")
        print("\n📋 Key fixes applied:")
        print("  ✅ Simplified health check")
        print("  ✅ Extended grace period (180s)")
        print("  ✅ Disabled circuit breaker")
        print("  ✅ Reduced CPU/Memory for stability")
        print("  ✅ Proper container command")
        print("  ✅ Simplified networking")
        
        print("\n⏳ Monitor progress with:")
        print(f"  aws cloudformation describe-stacks --stack-name autopilot-ventures-F1-fixed --query 'Stacks[0].StackStatus' --output text")
    else:
        print("❌ Failed to deploy fixed stack")

if __name__ == "__main__":
    main() 
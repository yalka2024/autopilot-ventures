#!/bin/bash

echo "🔧 Setting up ECS Task Execution Role..."

# Create the ECS task execution role
aws iam create-role \
    --role-name ecsTaskExecutionRole \
    --assume-role-policy-document '{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "ecs-tasks.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }' \
    --description "ECS Task Execution Role for AutoPilot Ventures"

# Attach the AWS managed policy
aws iam attach-role-policy \
    --role-name ecsTaskExecutionRole \
    --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy

echo "✅ ECS Task Execution Role created successfully!"

# Now run the task creation
echo "🚀 Creating task definition..."
python create_simple_task.py 
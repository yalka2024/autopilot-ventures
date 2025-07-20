#!/bin/bash

# AutoPilot Ventures ECR Deployment Script
# Run this script to deploy to AWS ECR

set -e

AWS_ACCOUNT_ID=${1:-""}
REGION=${2:-"us-east-1"}
REPOSITORY_NAME=${3:-"autopilot-ventures"}

echo "🚀 AutoPilot Ventures ECR Deployment"
echo "====================================="

# Get AWS Account ID if not provided
if [ -z "$AWS_ACCOUNT_ID" ]; then
    echo "Getting AWS Account ID..."
    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    if [ -z "$AWS_ACCOUNT_ID" ]; then
        echo "❌ Failed to get AWS Account ID. Please configure AWS CLI first."
        exit 1
    fi
    echo "✅ AWS Account ID: $AWS_ACCOUNT_ID"
fi

ECR_REPOSITORY_URI="$AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPOSITORY_NAME"

echo "📦 Creating ECR Repository..."
aws ecr create-repository --repository-name $REPOSITORY_NAME --region $REGION || echo "ℹ️  Repository might already exist, continuing..."

echo "🔐 Logging into ECR..."
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ECR_REPOSITORY_URI

echo "🏷️  Tagging Docker image..."
docker tag autopilot-ventures:latest $ECR_REPOSITORY_URI:latest

echo "📤 Pushing to ECR..."
docker push $ECR_REPOSITORY_URI:latest

echo "✅ Deployment completed successfully!"
echo "🔗 ECR Repository URI: $ECR_REPOSITORY_URI"
echo "🌐 View in AWS Console: https://console.aws.amazon.com/ecr/repositories/$REPOSITORY_NAME" 
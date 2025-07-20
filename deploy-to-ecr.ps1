# AutoPilot Ventures ECR Deployment Script
# Run this script to deploy to AWS ECR

param(
    [string]$AWSAccountId = "",
    [string]$Region = "us-east-1",
    [string]$RepositoryName = "autopilot-ventures"
)

Write-Host "🚀 AutoPilot Ventures ECR Deployment" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

# Get AWS Account ID if not provided
if (-not $AWSAccountId) {
    Write-Host "Getting AWS Account ID..." -ForegroundColor Yellow
    $AWSAccountId = aws sts get-caller-identity --query Account --output text
    if (-not $AWSAccountId) {
        Write-Host "❌ Failed to get AWS Account ID. Please configure AWS CLI first." -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ AWS Account ID: $AWSAccountId" -ForegroundColor Green
}

$ECRRepositoryUri = "$AWSAccountId.dkr.ecr.$Region.amazonaws.com/$RepositoryName"

Write-Host "📦 Creating ECR Repository..." -ForegroundColor Yellow
try {
    aws ecr create-repository --repository-name $RepositoryName --region $Region
    Write-Host "✅ ECR Repository created successfully" -ForegroundColor Green
} catch {
    Write-Host "ℹ️  Repository might already exist, continuing..." -ForegroundColor Yellow
}

Write-Host "🔐 Logging into ECR..." -ForegroundColor Yellow
aws ecr get-login-password --region $Region | docker login --username AWS --password-stdin $ECRRepositoryUri

Write-Host "🏷️  Tagging Docker image..." -ForegroundColor Yellow
docker tag autopilot-ventures:latest $ECRRepositoryUri`:latest

Write-Host "📤 Pushing to ECR..." -ForegroundColor Yellow
docker push $ECRRepositoryUri`:latest

Write-Host "✅ Deployment completed successfully!" -ForegroundColor Green
Write-Host "🔗 ECR Repository URI: $ECRRepositoryUri" -ForegroundColor Cyan
Write-Host "🌐 View in AWS Console: https://console.aws.amazon.com/ecr/repositories/$RepositoryName" -ForegroundColor Cyan 
#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Deploy AutoPilot Ventures to Google Cloud Run
    
.DESCRIPTION
    This script deploys the AutoPilot Ventures platform to Google Cloud Run
    with proper configuration for the web server.
#>

# Set error action preference
$ErrorActionPreference = "Stop"

Write-Host "🚀 AutoPilot Ventures - Google Cloud Run Deployment" -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Green

# Check if .env file exists
if (Test-Path ".env") {
    Write-Host "[SUCCESS] .env file found" -ForegroundColor Green
    
    # Load environment variables
    Get-Content ".env" | ForEach-Object {
        if ($_ -match "^([^=]+)=(.*)$") {
            $name = $matches[1]
            $value = $matches[2]
            [Environment]::SetEnvironmentVariable($name, $value, "Process")
        }
    }
    
    # Check required environment variables
    $requiredVars = @("OPENAI_SECRET_KEY")
    foreach ($var in $requiredVars) {
        if ([Environment]::GetEnvironmentVariable($var)) {
            Write-Host "[SUCCESS] $var loaded from .env file" -ForegroundColor Green
        } else {
            Write-Host "[WARNING] $var not found in .env file" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "[ERROR] .env file not found. Please create one with your API keys." -ForegroundColor Red
    exit 1
}

# Check if gcloud is installed
try {
    $gcloudVersion = gcloud version --format="value(version)" 2>$null
    if ($gcloudVersion) {
        Write-Host "[SUCCESS] Google Cloud SDK found: $gcloudVersion" -ForegroundColor Green
    } else {
        throw "gcloud not found"
    }
} catch {
    Write-Host "[ERROR] Google Cloud SDK not found. Please install it from: https://cloud.google.com/sdk/docs/install" -ForegroundColor Red
    exit 1
}

# Set project ID
$projectId = "autopilot-ventures-core"
Write-Host "[INFO] Using project ID: $projectId" -ForegroundColor Cyan

# Set project
Write-Host "[INFO] Setting Google Cloud project..." -ForegroundColor Cyan
gcloud config set project $projectId

# Check if billing is enabled
Write-Host "[INFO] Checking if billing is enabled..." -ForegroundColor Cyan
$billingEnabled = gcloud billing projects describe $projectId --format="value(billingEnabled)" 2>$null
if ($billingEnabled -eq "True") {
    Write-Host "[SUCCESS] Billing is enabled for project" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Billing is not enabled for project. Please enable billing in the Google Cloud Console." -ForegroundColor Red
    exit 1
}

# Enable required APIs
Write-Host "[INFO] Enabling required APIs..." -ForegroundColor Cyan
$apis = @(
    "run.googleapis.com",
    "cloudbuild.googleapis.com",
    "containerregistry.googleapis.com"
)

foreach ($api in $apis) {
    gcloud services enable $api --quiet
    Write-Host "[SUCCESS] Enabled API: $api" -ForegroundColor Green
}

# Build and deploy to Cloud Run
Write-Host "[INFO] Building and deploying to Cloud Run..." -ForegroundColor Cyan

$serviceName = "autopilot-ventures"
$region = "us-central1"
$imageUrl = "gcr.io/$projectId/$serviceName"

# Build and deploy
try {
    gcloud run deploy $serviceName `
        --source . `
        --platform managed `
        --region $region `
        --allow-unauthenticated `
        --port 8080 `
        --memory 2Gi `
        --cpu 2 `
        --max-instances 10 `
        --timeout 300 `
        --concurrency 80 `
        --set-env-vars "ENVIRONMENT=production,AUTONOMY_LEVEL=fully_autonomous,PHASE3_ENABLED=true,VECTOR_MEMORY_ENABLED=true,SELF_TUNING_ENABLED=true,REINFORCEMENT_LEARNING_ENABLED=true,AUTONOMOUS_WORKFLOW_ENABLED=true" `
        --quiet

    Write-Host "[SUCCESS] 🎉 Deployment complete!" -ForegroundColor Green
    
    # Get the service URL
    $serviceUrl = gcloud run services describe $serviceName --region $region --format="value(status.url)" 2>$null
    
    Write-Host ""
    Write-Host "[INFO] Your AutoPilot Ventures platform is now running at:" -ForegroundColor Cyan
    Write-Host "   $serviceUrl" -ForegroundColor White
    Write-Host ""
    Write-Host "[INFO] API Endpoints:" -ForegroundColor Cyan
    Write-Host "   Health check: $serviceUrl/health" -ForegroundColor White
    Write-Host "   API docs: $serviceUrl/docs" -ForegroundColor White
    Write-Host "   Status: $serviceUrl/status" -ForegroundColor White
    Write-Host ""
    Write-Host "[INFO] Your AI startup factory is ready to generate income! 🚀💰" -ForegroundColor Green
    
} catch {
    Write-Host "[ERROR] Deployment failed: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "[INFO] Troubleshooting tips:" -ForegroundColor Yellow
    Write-Host "   1. Check the logs: gcloud logs read --project=$projectId --limit=50"
    Write-Host "   2. Verify your .env file has all required variables"
    Write-Host "   3. Check if billing is enabled for the project"
    Write-Host "   4. Ensure you have the necessary permissions"
    exit 1
}

Write-Host ""
Write-Host "🎯 Next steps:" -ForegroundColor Cyan
Write-Host "   1. Test the health endpoint: $serviceUrl/health"
Write-Host "   2. Create your first business: POST $serviceUrl/create_business"
Write-Host "   3. Run a multilingual demo: POST $serviceUrl/multilingual_demo"
Write-Host "   4. Check the API documentation: $serviceUrl/docs"
Write-Host ""
Write-Host "🚀 Your autonomous income generation platform is live!" -ForegroundColor Green 
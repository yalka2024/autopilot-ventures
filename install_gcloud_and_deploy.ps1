# AutoPilot Ventures - Install gcloud CLI and Deploy Script
# This script installs Google Cloud CLI and deploys the platform

Write-Host "🚀 AutoPilot Ventures - Google Cloud CLI Setup and Deployment" -ForegroundColor Green
Write-Host ""

# Check if gcloud is already installed
try {
    $gcloudVersion = gcloud --version 2>$null
    if ($gcloudVersion) {
        Write-Host "✅ Google Cloud CLI is already installed!" -ForegroundColor Green
        Write-Host $gcloudVersion[0] -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Google Cloud CLI not found. Installing..." -ForegroundColor Red
    
    # Download and install Google Cloud CLI
    Write-Host "📥 Downloading Google Cloud CLI..." -ForegroundColor Cyan
    
    $installerUrl = "https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe"
    $installerPath = "$env:TEMP\GoogleCloudSDKInstaller.exe"
    
    try {
        Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath
        Write-Host "✅ Download completed!" -ForegroundColor Green
        
        Write-Host "🔧 Installing Google Cloud CLI..." -ForegroundColor Cyan
        Start-Process -FilePath $installerPath -ArgumentList "/S" -Wait
        
        # Refresh environment variables
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        
        Write-Host "✅ Installation completed!" -ForegroundColor Green
        Write-Host "🔄 Please restart your terminal/PowerShell to use gcloud commands" -ForegroundColor Yellow
        Write-Host ""
        
        # Ask user to restart
        $restart = Read-Host "Do you want to restart PowerShell now? (y/n)"
        if ($restart -eq 'y' -or $restart -eq 'Y') {
            Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\deploy_after_install.ps1"
            exit
        }
    } catch {
        Write-Host "❌ Failed to install Google Cloud CLI: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host ""
        Write-Host "📋 Manual Installation Instructions:" -ForegroundColor Yellow
        Write-Host "1. Visit: https://cloud.google.com/sdk/docs/install" -ForegroundColor White
        Write-Host "2. Download and install Google Cloud CLI" -ForegroundColor White
        Write-Host "3. Run: gcloud init" -ForegroundColor White
        Write-Host "4. Run: gcloud auth login" -ForegroundColor White
        exit 1
    }
}

# Function to deploy using Cloud Run (simpler alternative)
function Deploy-CloudRun {
    Write-Host "🚀 Deploying to Google Cloud Run..." -ForegroundColor Green
    
    # Build and deploy to Cloud Run
    gcloud run deploy autopilot-ventures `
        --image gcr.io/autopilot-ventures-core-466708/autopilot-ventures:latest `
        --region us-central1 `
        --platform managed `
        --allow-unauthenticated `
        --port 8080 `
        --memory 2Gi `
        --cpu 2 `
        --max-instances 10 `
        --min-instances 1 `
        --set-env-vars "PORT=8080,PYTHONPATH=/app"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Cloud Run deployment successful!" -ForegroundColor Green
        Write-Host "🌐 Your app will be available at the URL shown above" -ForegroundColor Yellow
    } else {
        Write-Host "❌ Cloud Run deployment failed" -ForegroundColor Red
    }
}

# Function to deploy using GKE
function Deploy-GKE {
    Write-Host "🚀 Deploying to Google Kubernetes Engine..." -ForegroundColor Green
    
    # Create GKE cluster
    Write-Host "🔧 Creating GKE cluster..." -ForegroundColor Cyan
    gcloud container clusters create autopilot-cluster `
        --region us-central1 `
        --num-nodes 3 `
        --min-nodes 1 `
        --max-nodes 10 `
        --enable-autoscaling `
        --machine-type e2-standard-2 `
        --disk-size 50 `
        --enable-network-policy `
        --enable-ip-alias `
        --workload-pool autopilot-ventures-core-466708.svc.id.goog
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ GKE cluster created successfully!" -ForegroundColor Green
        
        # Get cluster credentials
        Write-Host "🔑 Getting cluster credentials..." -ForegroundColor Cyan
        gcloud container clusters get-credentials autopilot-cluster --region=us-central1
        
        # Create namespace
        Write-Host "📁 Creating namespace..." -ForegroundColor Cyan
        kubectl create namespace autopilot-ventures 2>$null
        
        # Deploy application
        Write-Host "🚀 Deploying application..." -ForegroundColor Cyan
        kubectl apply -f k8s-deployment.yaml
        
        Write-Host "✅ GKE deployment successful!" -ForegroundColor Green
        Write-Host "📊 Check status with: kubectl get pods -n autopilot-ventures" -ForegroundColor Yellow
    } else {
        Write-Host "❌ GKE cluster creation failed" -ForegroundColor Red
    }
}

# Main deployment logic
Write-Host "🎯 Choose deployment method:" -ForegroundColor Yellow
Write-Host "1. Google Cloud Run (Recommended - Simpler)" -ForegroundColor White
Write-Host "2. Google Kubernetes Engine (Advanced)" -ForegroundColor White
Write-Host "3. Use existing Cloud Build (Push to GitHub)" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Enter your choice (1-3)"

switch ($choice) {
    "1" {
        Deploy-CloudRun
    }
    "2" {
        Deploy-GKE
    }
    "3" {
        Write-Host "🚀 Pushing to GitHub to trigger Cloud Build..." -ForegroundColor Green
        git add .
        git commit -m "Update Cloud Build configuration for automatic cluster creation"
        git push
        Write-Host "✅ Changes pushed! Cloud Build will now create the cluster automatically." -ForegroundColor Green
    }
    default {
        Write-Host "❌ Invalid choice. Please run the script again." -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "🎉 Setup complete! Your AutoPilot Ventures platform is being deployed." -ForegroundColor Green 
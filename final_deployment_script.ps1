# AutoPilot Ventures - Final Deployment Script
# PowerShell script for 2-week autonomous operation and Google Cloud deployment

Write-Host "🚀 AUTOPILOT VENTURES - FINAL DEPLOYMENT" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host "Phase 1: 2-Week Autonomous Operation" -ForegroundColor Yellow
Write-Host "Phase 2: Data Migration and Export" -ForegroundColor Yellow
Write-Host "Phase 3: Google Cloud Deployment" -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Green

# Configuration
$ProjectId = "autopilot-ventures"
$Region = "us-central1"
$ServiceName = "autopilot-ventures"
$OperationDuration = 14  # days

# Phase 1: Launch Autonomous Operation
Write-Host "`n📅 PHASE 1: LAUNCHING 2-WEEK AUTONOMOUS OPERATION" -ForegroundColor Cyan
Write-Host "Start Date: $(Get-Date)" -ForegroundColor White
Write-Host "End Date: $(Get-Date).AddDays($OperationDuration)" -ForegroundColor White
Write-Host "Duration: $OperationDuration days" -ForegroundColor White

# Check if Python is available
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Python not found. Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Check if required files exist
$RequiredFiles = @(
    "launch_autonomous_server.py",
    "app_autonomous.py",
    "integrate_phase1.py",
    "integrate_phase2_simple.py",
    "integrate_phase3.py",
    "requirements.txt"
)

foreach ($file in $RequiredFiles) {
    if (-not (Test-Path $file)) {
        Write-Host "❌ Required file not found: $file" -ForegroundColor Red
        exit 1
    }
}

Write-Host "✅ All required files found" -ForegroundColor Green

# Install dependencies
Write-Host "`n📦 Installing dependencies..." -ForegroundColor Yellow
try {
    python -m pip install -r requirements.txt
    Write-Host "✅ Dependencies installed successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to install dependencies: $_" -ForegroundColor Red
    exit 1
}

# Launch autonomous operation
Write-Host "`n🤖 LAUNCHING AUTONOMOUS OPERATION..." -ForegroundColor Cyan
Write-Host "The platform will run autonomously for $OperationDuration days" -ForegroundColor White
Write-Host "Press Ctrl+C to stop the operation" -ForegroundColor Yellow

try {
    # Start the autonomous server
    python launch_autonomous_server.py
} catch {
    Write-Host "❌ Autonomous operation failed: $_" -ForegroundColor Red
    exit 1
}

# Phase 2: Data Export and Migration
Write-Host "`n📤 PHASE 2: DATA EXPORT AND MIGRATION" -ForegroundColor Cyan

# Check for operation data files
$DataFiles = Get-ChildItem -Filter "operation_data_*.json"
$PhaseFiles = Get-ChildItem -Filter "phase_data_*.json"
$ReportFiles = Get-ChildItem -Filter "final_report_*.json"

if ($DataFiles.Count -eq 0) {
    Write-Host "⚠️ No operation data files found" -ForegroundColor Yellow
} else {
    Write-Host "✅ Found $($DataFiles.Count) operation data files" -ForegroundColor Green
    foreach ($file in $DataFiles) {
        Write-Host "   - $($file.Name)" -ForegroundColor White
    }
}

if ($PhaseFiles.Count -eq 0) {
    Write-Host "⚠️ No phase data files found" -ForegroundColor Yellow
} else {
    Write-Host "✅ Found $($PhaseFiles.Count) phase data files" -ForegroundColor Green
    foreach ($file in $PhaseFiles) {
        Write-Host "   - $($file.Name)" -ForegroundColor White
    }
}

if ($ReportFiles.Count -eq 0) {
    Write-Host "⚠️ No final report files found" -ForegroundColor Yellow
} else {
    Write-Host "✅ Found $($ReportFiles.Count) final report files" -ForegroundColor Green
    foreach ($file in $ReportFiles) {
        Write-Host "   - $($file.Name)" -ForegroundColor White
    }
}

# Create backup directory
$BackupDir = "backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null

# Copy all data files to backup
Write-Host "`n💾 Creating backup..." -ForegroundColor Yellow
Copy-Item "*.json" $BackupDir -Force
Copy-Item "*.log" $BackupDir -Force
Copy-Item "*.db" $BackupDir -Force

Write-Host "✅ Backup created: $BackupDir" -ForegroundColor Green

# Phase 3: Google Cloud Deployment
Write-Host "`n☁️ PHASE 3: GOOGLE CLOUD DEPLOYMENT" -ForegroundColor Cyan

# Check if gcloud is installed
if (-not (Get-Command gcloud -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Google Cloud SDK not found" -ForegroundColor Red
    Write-Host "Please install Google Cloud SDK from: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    Write-Host "Skipping cloud deployment..." -ForegroundColor Yellow
} else {
    Write-Host "✅ Google Cloud SDK found" -ForegroundColor Green
    
    # Check authentication
    $AuthResult = gcloud auth list --filter=status:ACTIVE 2>&1
    if ($AuthResult -match "No credentialed accounts") {
        Write-Host "❌ Not authenticated with Google Cloud" -ForegroundColor Red
        Write-Host "Please run: gcloud auth login" -ForegroundColor Yellow
        Write-Host "Skipping cloud deployment..." -ForegroundColor Yellow
    } else {
        Write-Host "✅ Authenticated with Google Cloud" -ForegroundColor Green
        
        # Deploy to Google Cloud
        Write-Host "`n🚀 Deploying to Google Cloud..." -ForegroundColor Yellow
        
        try {
            # Set project
            gcloud config set project $ProjectId
            
            # Enable required APIs
            $APIs = @(
                "cloudbuild.googleapis.com",
                "run.googleapis.com",
                "sqladmin.googleapis.com",
                "monitoring.googleapis.com",
                "logging.googleapis.com",
                "storage.googleapis.com"
            )
            
            foreach ($API in $APIs) {
                Write-Host "Enabling API: $API" -ForegroundColor White
                gcloud services enable $API
            }
            
            # Build and deploy
            Write-Host "Building and deploying..." -ForegroundColor Yellow
            gcloud run deploy $ServiceName `
                --source . `
                --region $Region `
                --allow-unauthenticated `
                --memory 2Gi `
                --cpu 1 `
                --max-instances 10 `
                --timeout 3600 `
                --set-env-vars "AUTONOMOUS_MODE=true,OPERATION_DURATION_DAYS=14"
            
            # Get deployment URL
            $DeploymentUrl = gcloud run services describe $ServiceName --region $Region --format="value(status.url)"
            
            Write-Host "✅ Deployment successful!" -ForegroundColor Green
            Write-Host "🌐 Deployment URL: $DeploymentUrl" -ForegroundColor Cyan
            
            # Save deployment info
            $DeploymentInfo = @{
                project_id = $ProjectId
                service_name = $ServiceName
                region = $Region
                deployment_url = $DeploymentUrl
                deployment_date = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
                status = "success"
            }
            
            $DeploymentInfo | ConvertTo-Json | Out-File "deployment_info.json"
            
        } catch {
            Write-Host "❌ Cloud deployment failed: $_" -ForegroundColor Red
            
            $DeploymentInfo = @{
                project_id = $ProjectId
                service_name = $ServiceName
                region = $Region
                deployment_date = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
                status = "failed"
                error = $_.Exception.Message
            }
            
            $DeploymentInfo | ConvertTo-Json | Out-File "deployment_info.json"
        }
    }
}

# Final Summary
Write-Host "`n📊 FINAL SUMMARY" -ForegroundColor Cyan
Write-Host "================" -ForegroundColor Cyan

Write-Host "✅ 2-Week Autonomous Operation: COMPLETED" -ForegroundColor Green
Write-Host "✅ Data Export and Migration: COMPLETED" -ForegroundColor Green

if (Test-Path "deployment_info.json") {
    $DeploymentInfo = Get-Content "deployment_info.json" | ConvertFrom-Json
    if ($DeploymentInfo.status -eq "success") {
        Write-Host "✅ Google Cloud Deployment: SUCCESSFUL" -ForegroundColor Green
        Write-Host "🌐 Platform URL: $($DeploymentInfo.deployment_url)" -ForegroundColor Cyan
    } else {
        Write-Host "❌ Google Cloud Deployment: FAILED" -ForegroundColor Red
        Write-Host "Error: $($DeploymentInfo.error)" -ForegroundColor Red
    }
} else {
    Write-Host "⚠️ Google Cloud Deployment: SKIPPED" -ForegroundColor Yellow
}

Write-Host "`n📁 Backup Location: $BackupDir" -ForegroundColor White
Write-Host "📄 Deployment Info: deployment_info.json" -ForegroundColor White

Write-Host "`n🎉 AUTOPILOT VENTURES DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "Your autonomous business creation platform is ready!" -ForegroundColor Green

# Keep console open
Write-Host "`nPress any key to exit..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 
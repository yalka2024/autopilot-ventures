# AutoPilot Ventures - Switch to Cloud Run Deployment
# This script helps switch from GKE to Cloud Run for simpler deployment

Write-Host "🚀 AutoPilot Ventures - Switching to Cloud Run Deployment" -ForegroundColor Green
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "cloudbuild-simple.yaml")) {
    Write-Host "❌ cloudbuild-simple.yaml not found. Please run this script from the project root." -ForegroundColor Red
    exit 1
}

Write-Host "📋 Current situation:" -ForegroundColor Yellow
Write-Host "- GKE cluster exists but has connectivity issues" -ForegroundColor White
Write-Host "- Cloud Run is a simpler alternative" -ForegroundColor White
Write-Host "- No cluster management required" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Do you want to switch to Cloud Run deployment? (y/n)"

if ($choice -eq 'y' -or $choice -eq 'Y') {
    Write-Host "🔄 Switching to Cloud Run deployment..." -ForegroundColor Cyan
    
    # Backup current cloudbuild.yaml
    if (Test-Path "cloudbuild.yaml") {
        Copy-Item "cloudbuild.yaml" "cloudbuild-gke.yaml"
        Write-Host "✅ Backed up current config as cloudbuild-gke.yaml" -ForegroundColor Green
    }
    
    # Copy simple config to main config
    Copy-Item "cloudbuild-simple.yaml" "cloudbuild.yaml"
    Write-Host "✅ Switched to Cloud Run configuration" -ForegroundColor Green
    
    # Commit and push the change
    Write-Host "📤 Committing and pushing changes..." -ForegroundColor Cyan
    git add cloudbuild.yaml cloudbuild-gke.yaml
    git commit -m "Switch to Cloud Run deployment for simpler setup"
    git push
    
    Write-Host ""
    Write-Host "🎉 Successfully switched to Cloud Run deployment!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Benefits of Cloud Run:" -ForegroundColor Yellow
    Write-Host "✅ No cluster management" -ForegroundColor Green
    Write-Host "✅ Faster deployment (2-3 minutes)" -ForegroundColor Green
    Write-Host "✅ Automatic scaling" -ForegroundColor Green
    Write-Host "✅ Pay only for what you use" -ForegroundColor Green
    Write-Host "✅ Built-in HTTPS" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 Your app will be deployed to Cloud Run automatically!" -ForegroundColor Yellow
    Write-Host "📊 Monitor at: https://console.cloud.google.com/run" -ForegroundColor White
    
} else {
    Write-Host "⏸️ Keeping current GKE configuration" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📋 To manually switch later:" -ForegroundColor Yellow
    Write-Host "1. Copy cloudbuild-simple.yaml to cloudbuild.yaml" -ForegroundColor White
    Write-Host "2. Commit and push the changes" -ForegroundColor White
    Write-Host "3. Or run this script again" -ForegroundColor White
} 
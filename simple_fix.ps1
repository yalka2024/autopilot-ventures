# Simple fix for AutoPilot Ventures deployment issues

Write-Host "🔧 AutoPilot Ventures - Simple Fix Script" -ForegroundColor Green
Write-Host ""

$PROJECT_ID = "autopilot-ventures-core-466708"

Write-Host "📋 Issues to Fix:" -ForegroundColor Yellow
Write-Host "1. QUOTA_EXCEEDED - Hit Google Cloud quota limits" -ForegroundColor Red
Write-Host "2. Permission denied - Service account lacks Cloud Run permissions" -ForegroundColor Red
Write-Host ""

# Check if gcloud is available
$gcloudCheck = gcloud --version 2>$null
if ($gcloudCheck) {
    Write-Host "✅ Google Cloud CLI found!" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "🔧 Fixing permissions..." -ForegroundColor Cyan
    
    # Get project number
    $projectNumber = gcloud projects describe $PROJECT_ID --format="value(projectNumber)"
    $cloudbuild_sa = "$projectNumber@cloudbuild.gserviceaccount.com"
    
    Write-Host "Cloud Build Service Account: $cloudbuild_sa" -ForegroundColor Yellow
    
    # Grant Cloud Run permissions
    Write-Host "Granting Cloud Run Admin role..." -ForegroundColor Cyan
    gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$cloudbuild_sa" --role="roles/run.admin"
    
    Write-Host "Granting Service Account User role..." -ForegroundColor Cyan
    gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$cloudbuild_sa" --role="roles/iam.serviceAccountUser"
    
    Write-Host "🧹 Cleaning up resources..." -ForegroundColor Cyan
    
    # Delete any existing failed services
    Write-Host "Deleting existing Cloud Run service..." -ForegroundColor Cyan
    gcloud run services delete autopilot-ventures --region=us-central1 --quiet 2>$null
    
    # Delete any existing GKE clusters
    Write-Host "Deleting existing GKE cluster..." -ForegroundColor Cyan
    gcloud container clusters delete autopilot-cluster --region=us-central1 --quiet 2>$null
    
    Write-Host "⏳ Waiting for cleanup..." -ForegroundColor Yellow
    Start-Sleep -Seconds 30
    
    Write-Host "🚀 Creating minimal deployment..." -ForegroundColor Cyan
    
    # Deploy with minimal resources
    gcloud run deploy autopilot-ventures --image gcr.io/$PROJECT_ID/autopilot-ventures:latest --region us-central1 --platform managed --allow-unauthenticated --port 8080 --memory 256Mi --cpu 1 --max-instances 1 --min-instances 0 --timeout 300
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Deployment successful!" -ForegroundColor Green
        Write-Host ""
        Write-Host "📋 Next steps:" -ForegroundColor Yellow
        Write-Host "1. Test the deployment at the URL above" -ForegroundColor White
        Write-Host "2. If successful, switch to full application" -ForegroundColor White
        Write-Host "3. Monitor quota usage in Google Cloud Console" -ForegroundColor White
    } else {
        Write-Host ""
        Write-Host "❌ Deployment failed!" -ForegroundColor Red
        Write-Host ""
        Write-Host "📋 Manual Steps:" -ForegroundColor Yellow
        Write-Host "1. Go to Google Cloud Console" -ForegroundColor White
        Write-Host "2. Check IAM permissions for Cloud Build service account" -ForegroundColor White
        Write-Host "3. Request quota increases if needed" -ForegroundColor White
        Write-Host "4. Try deploying manually through the console" -ForegroundColor White
    }
} else {
    Write-Host "❌ Google Cloud CLI not found. Please install it first:" -ForegroundColor Red
    Write-Host "Visit: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📋 Manual Steps to Fix:" -ForegroundColor Yellow
    Write-Host "1. Go to Google Cloud Console: https://console.cloud.google.com" -ForegroundColor White
    Write-Host "2. Select project: $PROJECT_ID" -ForegroundColor White
    Write-Host "3. Go to IAM and Admin section, then IAM" -ForegroundColor White
    Write-Host "4. Find the Cloud Build service account" -ForegroundColor White
    Write-Host "5. Add these roles:" -ForegroundColor White
    Write-Host "   - Cloud Run Admin" -ForegroundColor White
    Write-Host "   - Service Account User" -ForegroundColor White
    Write-Host "6. Go to Compute Engine section, then Quotas" -ForegroundColor White
    Write-Host "7. Request quota increases if needed" -ForegroundColor White
} 
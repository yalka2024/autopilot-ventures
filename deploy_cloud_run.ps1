# AutoPilot Ventures - Deploy to Google Cloud Run
# This is a simpler alternative to GKE deployment

Write-Host "🚀 AutoPilot Ventures - Deploying to Google Cloud Run" -ForegroundColor Green
Write-Host ""

# Check if gcloud is available
try {
    $gcloudVersion = gcloud --version 2>$null
    if ($gcloudVersion) {
        Write-Host "✅ Google Cloud CLI found!" -ForegroundColor Green
    } else {
        throw "gcloud not found"
    }
} catch {
    Write-Host "❌ Google Cloud CLI not found. Please install it first:" -ForegroundColor Red
    Write-Host "Visit: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
}

# Check if user is authenticated
try {
    $auth = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>$null
    if ($auth) {
        Write-Host "✅ Authenticated as: $auth" -ForegroundColor Green
    } else {
        Write-Host "❌ Not authenticated. Please run: gcloud auth login" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Authentication check failed. Please run: gcloud auth login" -ForegroundColor Red
    exit 1
}

# Set project
$PROJECT_ID = "autopilot-ventures-core-466708"
Write-Host "🔧 Setting project to: $PROJECT_ID" -ForegroundColor Cyan
gcloud config set project $PROJECT_ID

# Build and push Docker image
Write-Host "🔨 Building Docker image..." -ForegroundColor Cyan
gcloud builds submit --tag gcr.io/$PROJECT_ID/autopilot-ventures:latest .

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker build failed!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Docker image built and pushed successfully!" -ForegroundColor Green

# Deploy to Cloud Run
Write-Host "🚀 Deploying to Google Cloud Run..." -ForegroundColor Cyan

gcloud run deploy autopilot-ventures `
    --image gcr.io/$PROJECT_ID/autopilot-ventures:latest `
    --region us-central1 `
    --platform managed `
    --allow-unauthenticated `
    --port 8080 `
    --memory 2Gi `
    --cpu 2 `
    --max-instances 10 `
    --min-instances 1 `
    --set-env-vars "PORT=8080,PYTHONPATH=/app" `
    --set-env-vars "ENVIRONMENT=production" `
    --set-env-vars "LOG_LEVEL=INFO"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "🎉 Deployment successful!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Next steps:" -ForegroundColor Yellow
    Write-Host "1. Your app is now running on Cloud Run" -ForegroundColor White
    Write-Host "2. Check the URL above to access your application" -ForegroundColor White
    Write-Host "3. Monitor logs: gcloud logs tail --service=autopilot-ventures" -ForegroundColor White
    Write-Host ""
    Write-Host "🔗 Useful commands:" -ForegroundColor Yellow
    Write-Host "- View logs: gcloud logs tail --service=autopilot-ventures" -ForegroundColor White
    Write-Host "- Check status: gcloud run services describe autopilot-ventures --region=us-central1" -ForegroundColor White
    Write-Host "- Update deployment: gcloud run services update autopilot-ventures --image=gcr.io/$PROJECT_ID/autopilot-ventures:latest --region=us-central1" -ForegroundColor White
} else {
    Write-Host "❌ Cloud Run deployment failed!" -ForegroundColor Red
    exit 1
} 
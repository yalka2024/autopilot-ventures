# AutoPilot Ventures - Simple Deploy to Google Cloud
# This script uses a simpler approach for deployment

Write-Host "🚀 AutoPilot Ventures - Simple Deploy to Google Cloud" -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Green

# Configuration - using your existing project
$PROJECT_ID = "autopilot-ventures-core"
$REGION = "us-central1"
$SERVICE_NAME = "autopilot-ventures"

# Function to print colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Check if gcloud is installed
$gcloudPath = "C:\Users\yanp0\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"
if (Test-Path $gcloudPath) {
    Write-Success "Google Cloud SDK found at: $gcloudPath"
    $env:PATH += ";C:\Users\yanp0\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin"
} else {
    try {
        $null = gcloud version
        Write-Success "Google Cloud SDK found in PATH"
    } catch {
        Write-Error "Google Cloud SDK is not installed. Please install it first."
        Write-Status "Visit: https://cloud.google.com/sdk/docs/install"
        exit 1
    }
}

# Check if .env file exists and read API key
if (Test-Path ".env") {
    Write-Success ".env file found"
    
    # Read all environment variables from .env file
    $envVars = @{}
    Get-Content ".env" | ForEach-Object {
        if ($_ -match "^([^#][^=]+)=(.*)$") {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            $envVars[$key] = $value
        }
    }
    
    # Check for OpenAI key (either OPENAI_API_KEY or OPENAI_SECRET_KEY)
    if ($envVars.ContainsKey("OPENAI_API_KEY") -and $envVars["OPENAI_API_KEY"] -ne "your_openai_api_key_here") {
        $OPENAI_API_KEY = $envVars["OPENAI_API_KEY"]
        Write-Success "OPENAI_API_KEY loaded from .env file"
    } elseif ($envVars.ContainsKey("OPENAI_SECRET_KEY") -and $envVars["OPENAI_SECRET_KEY"] -ne "your_openai_secret_key_here") {
        $OPENAI_API_KEY = $envVars["OPENAI_SECRET_KEY"]
        Write-Success "OPENAI_SECRET_KEY loaded from .env file"
    } else {
        Write-Error "OPENAI_API_KEY or OPENAI_SECRET_KEY not found in .env file"
        exit 1
    }
    
    # Generate SECRET_KEY if not present
    if ($envVars.ContainsKey("SECRET_KEY") -and $envVars["SECRET_KEY"] -ne "your_secret_key_here") {
        $SECRET_KEY = $envVars["SECRET_KEY"]
        Write-Success "SECRET_KEY loaded from .env file"
    } else {
        $SECRET_KEY = -join ((33..126) | Get-Random -Count 64 | ForEach-Object {[char]$_})
        Write-Success "SECRET_KEY generated automatically"
    }
    
    # Check JWT_SECRET
    if ($envVars.ContainsKey("JWT_SECRET") -and $envVars["JWT_SECRET"] -ne "your_jwt_secret_here") {
        $JWT_SECRET = $envVars["JWT_SECRET"]
        Write-Success "JWT_SECRET loaded from .env file"
    } else {
        Write-Error "JWT_SECRET not found in .env file"
        exit 1
    }
    
} else {
    Write-Error ".env file not found"
    Write-Status "Please create .env file from env.gcp.example template"
    exit 1
}

Write-Status "Using project ID: $PROJECT_ID"

# Check if project exists
Write-Status "Checking Google Cloud project..."
try {
    $null = gcloud projects describe $PROJECT_ID
    Write-Success "Project $PROJECT_ID exists"
} catch {
    Write-Error "Project $PROJECT_ID not found or you don't have access"
    Write-Status "Please check your Google Cloud Console or create the project"
    Write-Status "Visit: https://console.cloud.google.com/projectcreate"
    exit 1
}

# Set project
Write-Status "Setting Google Cloud project..."
gcloud config set project $PROJECT_ID

# Check if billing is enabled
Write-Status "Checking if billing is enabled..."
try {
    $billingInfo = gcloud billing projects describe $PROJECT_ID --format="value(billingAccountName)"
    if ($billingInfo -and $billingInfo -ne "None") {
        Write-Success "Billing is enabled for project"
    } else {
        Write-Warning "Billing may not be enabled. Please check in Google Cloud Console"
        Write-Status "Visit: https://console.cloud.google.com/billing/projects/$PROJECT_ID"
    }
} catch {
    Write-Warning "Could not check billing status. Please ensure billing is enabled"
    Write-Status "Visit: https://console.cloud.google.com/billing/projects/$PROJECT_ID"
}

# Enable required APIs
Write-Status "Enabling required APIs..."
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Deploy to Cloud Run
Write-Status "Deploying to Cloud Run..."

# Deploy with individual environment variables
gcloud run deploy $SERVICE_NAME `
    --source . `
    --region $REGION `
    --platform managed `
    --allow-unauthenticated `
    --memory 2Gi `
    --cpu 2 `
    --max-instances 10 `
    --set-env-vars ENVIRONMENT=production `
    --set-env-vars AUTONOMY_LEVEL=fully_autonomous `
    --set-env-vars PHASE3_ENABLED=true `
    --set-env-vars "OPENAI_API_KEY=$OPENAI_API_KEY" `
    --set-env-vars "SECRET_KEY=$SECRET_KEY" `
    --set-env-vars "JWT_SECRET=$JWT_SECRET"

# Get service URL
try {
    $SERVICE_URL = gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)"
    
    Write-Success "🎉 Deployment complete!"
    Write-Status "Your AutoPilot Ventures platform is now running at:"
    Write-Host $SERVICE_URL -ForegroundColor Yellow
    Write-Status "Health check: $SERVICE_URL/health"
    Write-Status "Your AI startup factory is ready to generate income! 🚀💰"
} catch {
    Write-Warning "Deployment may have succeeded, but couldn't get service URL"
    Write-Status "Check Google Cloud Console for your service URL"
} 
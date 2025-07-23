# AutoPilot Ventures - Quick Deploy to Google Cloud
# Run this script to deploy your platform to Google Cloud

Write-Host "🚀 AutoPilot Ventures - Quick Deploy to Google Cloud" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green

# Configuration
$PROJECT_ID = "autopilot-ventures-core"
$REGION = "us-central1"
$SERVICE_NAME = "autopilot-ventures"

# Function to create project if it doesn't exist
function New-GoogleCloudProject {
    param([string]$ProjectId)
    
    Write-Status "Checking if project exists..."
    try {
        $null = gcloud projects describe $ProjectId 2>$null
        Write-Success "Project $ProjectId exists"
        return $true
    } catch {
        Write-Status "Project $ProjectId does not exist. Creating..."
        try {
            gcloud projects create $ProjectId --name="AutoPilot Ventures"
            Write-Success "Project $ProjectId created successfully"
            return $true
        } catch {
            Write-Error "Failed to create project. Please create it manually in Google Cloud Console"
            Write-Status "Visit: https://console.cloud.google.com/projectcreate"
            return $false
        }
    }
}

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

# Check if .env file exists and read all API keys
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
    
    # Check required keys (support both OPENAI_API_KEY and OPENAI_SECRET_KEY)
    $requiredKeys = @("JWT_SECRET")
    $missingKeys = @()
    
    # Check for OpenAI key (either OPENAI_API_KEY or OPENAI_SECRET_KEY)
    if ($envVars.ContainsKey("OPENAI_API_KEY") -and $envVars["OPENAI_API_KEY"] -ne "your_openai_api_key_here") {
        $OPENAI_API_KEY = $envVars["OPENAI_API_KEY"]
        Write-Success "OPENAI_API_KEY loaded from .env file"
    } elseif ($envVars.ContainsKey("OPENAI_SECRET_KEY") -and $envVars["OPENAI_SECRET_KEY"] -ne "your_openai_secret_key_here") {
        $OPENAI_API_KEY = $envVars["OPENAI_SECRET_KEY"]
        Write-Success "OPENAI_SECRET_KEY loaded from .env file"
    } else {
        $missingKeys += "OPENAI_API_KEY or OPENAI_SECRET_KEY"
    }
    
    # Check for SECRET_KEY or generate one
    if ($envVars.ContainsKey("SECRET_KEY") -and $envVars["SECRET_KEY"] -ne "your_secret_key_here") {
        $SECRET_KEY = $envVars["SECRET_KEY"]
        Write-Success "SECRET_KEY loaded from .env file"
    } else {
        # Generate a secure SECRET_KEY
        $SECRET_KEY = -join ((33..126) | Get-Random -Count 64 | ForEach-Object {[char]$_})
        Write-Success "SECRET_KEY generated automatically"
    }
    
    # Check JWT_SECRET
    if ($envVars.ContainsKey("JWT_SECRET") -and $envVars["JWT_SECRET"] -ne "your_jwt_secret_here") {
        $JWT_SECRET = $envVars["JWT_SECRET"]
        Write-Success "JWT_SECRET loaded from .env file"
    } else {
        $missingKeys += "JWT_SECRET"
    }
    
    if ($missingKeys.Count -gt 0) {
        Write-Error "Missing or not configured keys: $($missingKeys -join ', ')"
        Write-Status "Please configure these keys in your .env file"
        exit 1
    }
    
} else {
    Write-Error ".env file not found"
    Write-Status "Please create .env file from env.gcp.example template"
    exit 1
}

# Create project if it doesn't exist
if (-not (New-GoogleCloudProject -ProjectId $PROJECT_ID)) {
    exit 1
}

# Set project
Write-Status "Setting Google Cloud project..."
gcloud config set project $PROJECT_ID

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
$SERVICE_URL = gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)"

Write-Success "🎉 Deployment complete!"
Write-Status "Your AutoPilot Ventures platform is now running at:"
Write-Host $SERVICE_URL -ForegroundColor Yellow
Write-Status "Health check: $SERVICE_URL/health"
Write-Status "Your AI startup factory is ready to generate income! 🚀💰" 
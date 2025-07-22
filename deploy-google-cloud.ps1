# AutoPilot Ventures - Google Cloud Deployment Script for Windows
# This script deploys the platform to Google Cloud Platform

param(
    [string]$ProjectId = "autopilot-ventures",
    [string]$Region = "us-central1",
    [string]$Zone = "us-central1-a"
)

# Configuration
$ClusterName = "autopilot-cluster"
$ServiceName = "autopilot-ventures"
$ImageName = "gcr.io/$ProjectId/autopilot-ventures"
$Version = "latest"

Write-Host "🚀 AutoPilot Ventures - Google Cloud Deployment" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green

# Function to print colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Check if gcloud is installed
function Test-GCloud {
    try {
        $null = gcloud version
        Write-Success "Google Cloud SDK found"
    }
    catch {
        Write-Error "Google Cloud SDK is not installed. Please install it first."
        Write-Status "Visit: https://cloud.google.com/sdk/docs/install"
        exit 1
    }
}

# Check if kubectl is installed
function Test-Kubectl {
    try {
        $null = kubectl version --client
        Write-Success "kubectl found"
    }
    catch {
        Write-Error "kubectl is not installed. Please install it first."
        Write-Status "Visit: https://kubernetes.io/docs/tasks/tools/"
        exit 1
    }
}

# Check if Docker is installed
function Test-Docker {
    try {
        $null = docker version
        Write-Success "Docker found"
    }
    catch {
        Write-Error "Docker is not installed. Please install it first."
        Write-Status "Visit: https://docs.docker.com/get-docker/"
        exit 1
    }
}

# Set up Google Cloud project
function Setup-Project {
    Write-Status "Setting up Google Cloud project..."
    
    # Set the project
    gcloud config set project $ProjectId
    
    # Enable required APIs
    gcloud services enable container.googleapis.com
    gcloud services enable cloudbuild.googleapis.com
    gcloud services enable containerregistry.googleapis.com
    gcloud services enable compute.googleapis.com
    gcloud services enable sqladmin.googleapis.com
    gcloud services enable redis.googleapis.com
    
    Write-Success "Google Cloud project setup complete"
}

# Create GKE cluster
function New-GkeCluster {
    Write-Status "Creating GKE cluster..."
    
    gcloud container clusters create $ClusterName `
        --zone=$Zone `
        --num-nodes=3 `
        --machine-type=e2-standard-4 `
        --enable-autoscaling `
        --min-nodes=1 `
        --max-nodes=10 `
        --enable-autorepair `
        --enable-autoupgrade `
        --enable-ip-alias `
        --create-subnetwork="" `
        --network=default
    
    Write-Success "GKE cluster created successfully"
}

# Build and push Docker image
function Build-Image {
    Write-Status "Building and pushing Docker image..."
    
    # Configure Docker to use gcloud as a credential helper
    gcloud auth configure-docker
    
    # Build the image
    docker build -f Dockerfile.gcp -t $ImageName`:$Version .
    
    # Push to Google Container Registry
    docker push $ImageName`:$Version
    
    Write-Success "Docker image built and pushed successfully"
}

# Create PostgreSQL Cloud SQL instance
function New-CloudSqlInstance {
    Write-Status "Creating PostgreSQL database..."
    
    # Create Cloud SQL instance
    gcloud sql instances create autopilot-db `
        --database-version=POSTGRES_14 `
        --tier=db-f1-micro `
        --region=$Region `
        --storage-type=SSD `
        --storage-size=10GB `
        --backup-start-time=02:00 `
        --maintenance-window-day=SUN `
        --maintenance-window-hour=03
    
    # Create database
    gcloud sql databases create autopilot_ventures --instance=autopilot-db
    
    # Create user
    gcloud sql users create autopilot_user `
        --instance=autopilot-db `
        --password=autopilot_password_2024
    
    # Get connection info
    $DB_HOST = gcloud sql instances describe autopilot-db --format="value(connectionName)"
    Write-Success "Database created: $DB_HOST"
}

# Create Redis Memorystore instance
function New-RedisInstance {
    Write-Status "Creating Redis instance..."
    
    gcloud redis instances create autopilot-redis `
        --size=1 `
        --region=$Region `
        --redis-version=redis_6_x
    
    $REDIS_HOST = gcloud redis instances describe autopilot-redis --region=$Region --format="value(host)"
    Write-Success "Redis created: $REDIS_HOST"
}

# Create Kubernetes secrets
function New-KubernetesSecrets {
    Write-Status "Creating Kubernetes secrets..."
    
    # Create namespace
    kubectl create namespace autopilot-ventures --dry-run=client -o yaml | kubectl apply -f -
    
    # Check if environment variables exist
    if (-not $env:OPENAI_API_KEY) {
        Write-Error "OPENAI_API_KEY environment variable is required"
        exit 1
    }
    
    if (-not $env:SECRET_KEY) {
        Write-Error "SECRET_KEY environment variable is required"
        exit 1
    }
    
    # Create secrets
    kubectl create secret generic autopilot-secrets `
        --namespace=autopilot-ventures `
        --from-literal=openai-api-key="$env:OPENAI_API_KEY" `
        --from-literal=secret-key="$env:SECRET_KEY" `
        --from-literal=database-url="postgresql://autopilot_user:autopilot_password_2024@/autopilot_ventures?host=/cloudsql/$ProjectId`:$Region`:autopilot-db" `
        --from-literal=redis-host="$REDIS_HOST" `
        --dry-run=client -o yaml | kubectl apply -f -
    
    Write-Success "Kubernetes secrets created"
}

# Deploy to Kubernetes
function Deploy-Kubernetes {
    Write-Status "Deploying to Kubernetes..."
    
    # Apply the deployment
    kubectl apply -f k8s-deployment.yaml
    
    Write-Success "Kubernetes deployment created"
}

# Deploy to Cloud Run (alternative)
function Deploy-CloudRun {
    Write-Status "Deploying to Cloud Run..."
    
    gcloud run deploy $ServiceName `
        --image $ImageName`:$Version `
        --platform managed `
        --region $Region `
        --allow-unauthenticated `
        --memory 2Gi `
        --cpu 2 `
        --max-instances 10 `
        --set-env-vars ENVIRONMENT=production,PORT=8000 `
        --set-secrets OPENAI_API_KEY=openai-api-key:latest `
        --set-secrets SECRET_KEY=secret-key:latest `
        --set-secrets DATABASE_URL=database-url:latest `
        --set-secrets REDIS_HOST=redis-host:latest
    
    Write-Success "Cloud Run deployment complete"
}

# Get deployment status
function Get-DeploymentStatus {
    Write-Status "Getting deployment status..."
    
    # Get service URL
    $SERVICE_URL = gcloud run services describe $ServiceName --region=$Region --format="value(status.url)"
    
    Write-Success "AutoPilot Ventures is deployed!"
    Write-Status "Service URL: $SERVICE_URL"
    Write-Status "Health Check: $SERVICE_URL/health"
    Write-Status "Metrics: $SERVICE_URL:9090"
    
    # Test the deployment
    Write-Status "Testing deployment..."
    try {
        Invoke-WebRequest -Uri "$SERVICE_URL/health" -UseBasicParsing | Out-Null
        Write-Success "Health check passed!"
    }
    catch {
        Write-Warning "Health check failed, but deployment may still be starting"
    }
}

# Main deployment function
function Start-Deployment {
    Write-Status "Starting AutoPilot Ventures deployment to Google Cloud..."
    
    # Check prerequisites
    Test-GCloud
    Test-Kubectl
    Test-Docker
    
    # Check environment variables
    if (-not $env:OPENAI_API_KEY) {
        Write-Error "OPENAI_API_KEY environment variable is required"
        Write-Status "Please set it: `$env:OPENAI_API_KEY='your-api-key'"
        exit 1
    }
    
    if (-not $env:SECRET_KEY) {
        Write-Error "SECRET_KEY environment variable is required"
        Write-Status "Please set it: `$env:SECRET_KEY='your-secret-key'"
        exit 1
    }
    
    # Setup and deploy
    Setup-Project
    New-GkeCluster
    Build-Image
    New-CloudSqlInstance
    New-RedisInstance
    New-KubernetesSecrets
    Deploy-Kubernetes
    Deploy-CloudRun
    Get-DeploymentStatus
    
    Write-Success "🎉 AutoPilot Ventures deployment complete!"
    Write-Status "Your AI startup factory is now running on Google Cloud!"
}

# Run main deployment function
Start-Deployment 
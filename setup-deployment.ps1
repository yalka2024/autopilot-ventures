# AutoPilot Ventures - Deployment Setup Script
# This script prepares the environment for Google Cloud deployment

Write-Host "🚀 AutoPilot Ventures - Deployment Setup" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Green

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

# Check if .env file exists
function Test-EnvironmentFile {
    Write-Status "Checking environment configuration..."
    
    if (Test-Path ".env") {
        Write-Success "Environment file (.env) found"
    } else {
        Write-Warning "Environment file (.env) not found"
        Write-Status "Creating from template..."
        
        if (Test-Path "env.gcp.example") {
            Copy-Item "env.gcp.example" ".env"
            Write-Success "Environment file created from template"
            Write-Warning "Please edit .env file with your API keys before deployment"
        } else {
            Write-Error "env.gcp.example template not found"
            exit 1
        }
    }
}

# Check required files
function Test-RequiredFiles {
    Write-Status "Checking required files..."
    
    $requiredFiles = @(
        "Dockerfile.gcp",
        "k8s-deployment.yaml",
        "requirements_enhanced.txt",
        "main.py",
        "config.py"
    )
    
    $missingFiles = @()
    
    foreach ($file in $requiredFiles) {
        if (Test-Path $file) {
            Write-Success "✓ $file"
        } else {
            Write-Error "✗ $file (missing)"
            $missingFiles += $file
        }
    }
    
    if ($missingFiles.Count -gt 0) {
        Write-Error "Missing required files: $($missingFiles -join ', ')"
        exit 1
    }
}

# Generate secure keys
function New-SecureKeys {
    Write-Status "Generating secure keys..."
    
    # Generate SECRET_KEY if not set
    if (-not $env:SECRET_KEY) {
        $secretKey = -join ((33..126) | Get-Random -Count 64 | ForEach-Object {[char]$_})
        Write-Success "Generated SECRET_KEY"
        Write-Status "Set environment variable: `$env:SECRET_KEY='$secretKey'"
    } else {
        Write-Success "SECRET_KEY already set"
    }
    
    # Generate JWT_SECRET if not set
    if (-not $env:JWT_SECRET) {
        $jwtSecret = -join ((33..126) | Get-Random -Count 64 | ForEach-Object {[char]$_})
        Write-Success "Generated JWT_SECRET"
        Write-Status "Set environment variable: `$env:JWT_SECRET='$jwtSecret'"
    } else {
        Write-Success "JWT_SECRET already set"
    }
}

# Check prerequisites
function Test-Prerequisites {
    Write-Status "Checking prerequisites..."
    
    # Check Docker
    try {
        $null = docker version
        Write-Success "✓ Docker installed"
    } catch {
        Write-Error "✗ Docker not installed"
        Write-Status "Install Docker Desktop from: https://docs.docker.com/get-docker/"
    }
    
    # Check gcloud
    try {
        $null = gcloud version
        Write-Success "✓ Google Cloud SDK installed"
    } catch {
        Write-Error "✗ Google Cloud SDK not installed"
        Write-Status "Install from: https://cloud.google.com/sdk/docs/install"
    }
    
    # Check kubectl
    try {
        $null = kubectl version --client
        Write-Success "✓ kubectl installed"
    } catch {
        Write-Error "✗ kubectl not installed"
        Write-Status "Install from: https://kubernetes.io/docs/tasks/tools/"
    }
}

# Validate environment variables
function Test-EnvironmentVariables {
    Write-Status "Validating environment variables..."
    
    $requiredVars = @("OPENAI_API_KEY")
    $missingVars = @()
    
    foreach ($var in $requiredVars) {
        if (Get-Variable -Name "env:$var" -ErrorAction SilentlyContinue) {
            Write-Success "✓ $var is set"
        } else {
            Write-Warning "✗ $var is not set"
            $missingVars += $var
        }
    }
    
    if ($missingVars.Count -gt 0) {
        Write-Warning "Missing environment variables: $($missingVars -join ', ')"
        Write-Status "Please set them before deployment:"
        foreach ($var in $missingVars) {
            Write-Status "  `$env:$var='your-value'"
        }
    }
}

# Create deployment checklist
function New-DeploymentChecklist {
    Write-Status "Creating deployment checklist..."
    
    $checklist = @"
# AutoPilot Ventures - Deployment Checklist

## ✅ Prerequisites
- [ ] Google Cloud account with billing enabled
- [ ] Docker Desktop installed and running
- [ ] Google Cloud SDK installed
- [ ] kubectl installed
- [ ] OpenAI API key obtained

## 🔧 Environment Setup
- [ ] Environment file (.env) configured
- [ ] OPENAI_API_KEY set
- [ ] SECRET_KEY generated
- [ ] JWT_SECRET generated

## 🚀 Deployment Steps
1. [ ] Set environment variables:
   ```powershell
   `$env:OPENAI_API_KEY='your-openai-api-key'
   `$env:SECRET_KEY='your-secret-key'
   `$env:JWT_SECRET='your-jwt-secret'
   ```

2. [ ] Run deployment:
   ```powershell
   .\deploy-google-cloud.ps1
   ```

3. [ ] Verify deployment:
   ```powershell
   kubectl get pods -n autopilot-ventures
   kubectl get services -n autopilot-ventures
   ```

## 📊 Post-Deployment
- [ ] Check application health
- [ ] Monitor logs
- [ ] Set up domain and SSL
- [ ] Configure monitoring dashboards

## 💰 Expected Timeline
- Week 1-2: Setup and initial business creation
- Week 3-4: First income ($100-$500)
- Month 2: Break-even achieved
- Month 3: $5,000-$20,000/month
- Month 4: $20,000-$50,000/month
- Month 6: $100,000-$500,000/month

## 🔗 Useful Commands
```powershell
# Check deployment status
kubectl get pods -n autopilot-ventures

# View logs
kubectl logs -f deployment/autopilot-ventures -n autopilot-ventures

# Scale deployment
kubectl scale deployment autopilot-ventures --replicas=5 -n autopilot-ventures

# Get service URL
kubectl get service autopilot-ventures-service -n autopilot-ventures
```
"@

    $checklist | Out-File -FilePath "DEPLOYMENT_CHECKLIST.md" -Encoding UTF8
    Write-Success "Deployment checklist created: DEPLOYMENT_CHECKLIST.md"
}

# Main setup function
function Start-Setup {
    Write-Status "Starting deployment setup..."
    
    Test-RequiredFiles
    Test-EnvironmentFile
    Test-Prerequisites
    New-SecureKeys
    Test-EnvironmentVariables
    New-DeploymentChecklist
    
    Write-Success "🎉 Setup complete!"
    Write-Status "Next steps:"
    Write-Status "1. Edit .env file with your API keys"
    Write-Status "2. Set environment variables"
    Write-Status "3. Run: .\deploy-google-cloud.ps1"
    Write-Status ""
    Write-Status "See DEPLOYMENT_CHECKLIST.md for detailed instructions"
}

# Run setup
Start-Setup 
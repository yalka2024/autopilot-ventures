# deploy_autopilot.ps1 - Automated deployment script for AutoPilot Ventures

# Variables (adjust as needed)
$Region = "us-east-1"  # Change to your preferred AWS region (e.g., us-west-2)
$AccountId = "160277203814"  # Your AWS Account ID
$RepoName = "autopilot-ventures"
$ImageTag = "latest"
$StackName = "autopilot-ventures"
$BudgetThreshold = 50
$DockerImage = "${AccountId}.dkr.ecr.${Region}.amazonaws.com/${RepoName}:${ImageTag}"

# Check if Docker Desktop is installed and running
Write-Host "Checking Docker Desktop..." -ForegroundColor Green
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "Docker not found. Downloading and installing..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri "https://desktop.docker.com/win/stable/Docker%20Desktop%20Installer.exe" -OutFile "DockerDesktopInstaller.exe"
    Start-Process -Wait -FilePath "DockerDesktopInstaller.exe"
    Remove-Item "DockerDesktopInstaller.exe"
}
if (-not (Get-Process "Docker Desktop" -ErrorAction SilentlyContinue)) {
    Write-Host "Starting Docker Desktop..." -ForegroundColor Yellow
    Start-Process "Docker Desktop"
    Start-Sleep -Seconds 30  # Wait for Docker to start
}
if (-not (docker ps -q)) {
    Write-Host "Docker is not running or accessible. Please start Docker Desktop manually and retry." -ForegroundColor Red
    exit
}

# Build Docker Image
Write-Host "Building Docker image..." -ForegroundColor Green
docker build -t autopilot-ventures:$ImageTag .
if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker build failed. Check logs above." -ForegroundColor Red
    exit
}
Write-Host "Successfully tagged autopilot-ventures:$ImageTag" -ForegroundColor Green

# Test Docker Image Locally
Write-Host "Testing Docker image locally..." -ForegroundColor Green
docker run -d -p 8000:8000 --env-file .env autopilot-ventures:$ImageTag
Start-Sleep -Seconds 10  # Wait for container to start
$HealthResponse = Invoke-WebRequest -Uri http://localhost:8000/health -UseBasicParsing
if ($HealthResponse.StatusCode -eq 200) {
    Write-Host "Health check passed: $HealthResponse.Content" -ForegroundColor Green
} else {
    Write-Host "Health check failed with status $($HealthResponse.StatusCode). Check port 8000 conflicts." -ForegroundColor Red
    docker stop $(docker ps -q -f "ancestor=autopilot-ventures:$ImageTag")
    docker rm $(docker ps -q -f "ancestor=autopilot-ventures:$ImageTag")
    exit
}
docker stop $(docker ps -q -f "ancestor=autopilot-ventures:$ImageTag")
docker rm $(docker ps -q -f "ancestor=autopilot-ventures:$ImageTag")

# Install AWS CLI if not present
Write-Host "Checking AWS CLI..." -ForegroundColor Green
if (-not (Get-Command aws -ErrorAction SilentlyContinue)) {
    Write-Host "AWS CLI not found. Downloading and installing..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri "https://awscli.amazonaws.com/AWSCLIV2.msi" -OutFile "AWSCLIV2.msi"
    Start-Process msiexec -ArgumentList "/i AWSCLIV2.msi /quiet /norestart" -Wait
    Remove-Item "AWSCLIV2.msi"
}

# Configure AWS CLI
Write-Host "Configuring AWS CLI..." -ForegroundColor Green
$AccessKey = Read-Host "Enter AWS Access Key ID"
$SecretKey = Read-Host "Enter AWS Secret Access Key" -AsSecureString
$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($SecretKey)
$SecretKeyPlain = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
aws configure set aws_access_key_id $AccessKey
aws configure set aws_secret_access_key $SecretKeyPlain
aws configure set default.region $Region
aws configure set default.output json
Write-Host "AWS CLI configured with region $Region" -ForegroundColor Green

# Create ECR Repository
Write-Host "Creating ECR repository..." -ForegroundColor Green
aws ecr create-repository --repository-name $RepoName --region $Region
if ($LASTEXITCODE -ne 0) {
    Write-Host "ECR repository creation failed. Check region and permissions." -ForegroundColor Red
    exit
}
Write-Host "ECR repository created successfully" -ForegroundColor Green

# Log in to ECR and Push Docker Image
Write-Host "Logging in to ECR and pushing image..." -ForegroundColor Green
aws ecr get-login-password --region $Region | docker login --username AWS --password-stdin $AccountId.dkr.ecr.$Region.amazonaws.com
docker tag autopilot-ventures:$ImageTag $DockerImage
docker push $DockerImage
if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker push failed. Check login or network." -ForegroundColor Red
    exit
}
Write-Host "Docker image pushed successfully" -ForegroundColor Green

# Deploy with CloudFormation
Write-Host "Deploying with CloudFormation..." -ForegroundColor Green
aws cloudformation create-stack --stack-name $StackName --template-body file://cloud-deployment.yml --parameters ParameterKey=ImageUrl,ParameterValue=$DockerImage ParameterKey=BudgetThreshold,ParameterValue=$BudgetThreshold --region $Region
Write-Host "Stack creation started. Monitoring in AWS Console (~10 mins)..." -ForegroundColor Green
Start-Sleep -Seconds 600  # Wait 10 mins for stack creation
Write-Host "Check AWS Console (CloudFormation > Stacks) to verify deployment" -ForegroundColor Green

# Start Autonomous Operation (Manual Step)
Write-Host "Deployment complete. To start autonomous operation:" -ForegroundColor Green
Write-Host "1. Verify ECS tasks in AWS Console." -ForegroundColor Green
Write-Host "2. Trigger via CLI: python main.py --start-autonomous --autonomous-mode semi (if accessible)" -ForegroundColor Green
Write-Host "3. Or schedule in CloudFormation (e.g., EventBridge)." -ForegroundColor Green
Write-Host "Monitor with Grafana (port 3000) or CloudWatch." -ForegroundColor Green

Write-Host "Deployment script completed. Press any key to exit..." -ForegroundColor Green
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
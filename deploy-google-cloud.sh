#!/bin/bash

# AutoPilot Ventures - Google Cloud Deployment Script
# This script deploys the platform to Google Cloud Platform

set -e

echo "🚀 AutoPilot Ventures - Google Cloud Deployment"
echo "================================================"

# Configuration
PROJECT_ID="autopilot-ventures"
REGION="us-central1"
ZONE="us-central1-a"
CLUSTER_NAME="autopilot-cluster"
SERVICE_NAME="autopilot-ventures"
IMAGE_NAME="gcr.io/$PROJECT_ID/autopilot-ventures"
VERSION="latest"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if gcloud is installed
check_gcloud() {
    if ! command -v gcloud &> /dev/null; then
        print_error "Google Cloud SDK is not installed. Please install it first."
        print_status "Visit: https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
    print_success "Google Cloud SDK found"
}

# Check if kubectl is installed
check_kubectl() {
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl is not installed. Please install it first."
        print_status "Visit: https://kubernetes.io/docs/tasks/tools/"
        exit 1
    fi
    print_success "kubectl found"
}

# Set up Google Cloud project
setup_project() {
    print_status "Setting up Google Cloud project..."
    
    # Set the project
    gcloud config set project $PROJECT_ID
    
    # Enable required APIs
    gcloud services enable container.googleapis.com
    gcloud services enable cloudbuild.googleapis.com
    gcloud services enable containerregistry.googleapis.com
    gcloud services enable compute.googleapis.com
    gcloud services enable sqladmin.googleapis.com
    gcloud services enable redis.googleapis.com
    
    print_success "Google Cloud project setup complete"
}

# Create GKE cluster
create_cluster() {
    print_status "Creating GKE cluster..."
    
    gcloud container clusters create $CLUSTER_NAME \
        --zone=$ZONE \
        --num-nodes=3 \
        --machine-type=e2-standard-4 \
        --enable-autoscaling \
        --min-nodes=1 \
        --max-nodes=10 \
        --enable-autorepair \
        --enable-autoupgrade \
        --enable-ip-alias \
        --create-subnetwork="" \
        --network=default
    
    print_success "GKE cluster created successfully"
}

# Build and push Docker image
build_image() {
    print_status "Building and pushing Docker image..."
    
    # Configure Docker to use gcloud as a credential helper
    gcloud auth configure-docker
    
    # Build the image
    docker build -f Dockerfile.gcp -t $IMAGE_NAME:$VERSION .
    
    # Push to Google Container Registry
    docker push $IMAGE_NAME:$VERSION
    
    print_success "Docker image built and pushed successfully"
}

# Create PostgreSQL Cloud SQL instance
create_database() {
    print_status "Creating PostgreSQL database..."
    
    # Create Cloud SQL instance
    gcloud sql instances create autopilot-db \
        --database-version=POSTGRES_14 \
        --tier=db-f1-micro \
        --region=$REGION \
        --storage-type=SSD \
        --storage-size=10GB \
        --backup-start-time=02:00 \
        --maintenance-window-day=SUN \
        --maintenance-window-hour=03
    
    # Create database
    gcloud sql databases create autopilot_ventures --instance=autopilot-db
    
    # Create user
    gcloud sql users create autopilot_user \
        --instance=autopilot-db \
        --password=autopilot_password_2024
    
    # Get connection info
    DB_HOST=$(gcloud sql instances describe autopilot-db --format="value(connectionName)")
    print_success "Database created: $DB_HOST"
}

# Create Redis Memorystore instance
create_redis() {
    print_status "Creating Redis instance..."
    
    gcloud redis instances create autopilot-redis \
        --size=1 \
        --region=$REGION \
        --redis-version=redis_6_x
    
    REDIS_HOST=$(gcloud redis instances describe autopilot-redis --region=$REGION --format="value(host)")
    print_success "Redis created: $REDIS_HOST"
}

# Create Kubernetes secrets
create_secrets() {
    print_status "Creating Kubernetes secrets..."
    
    # Create namespace
    kubectl create namespace autopilot-ventures --dry-run=client -o yaml | kubectl apply -f -
    
    # Create secrets
    kubectl create secret generic autopilot-secrets \
        --namespace=autopilot-ventures \
        --from-literal=openai-api-key="$OPENAI_API_KEY" \
        --from-literal=secret-key="$SECRET_KEY" \
        --from-literal=database-url="postgresql://autopilot_user:autopilot_password_2024@$DB_HOST/autopilot_ventures" \
        --from-literal=redis-host="$REDIS_HOST" \
        --dry-run=client -o yaml | kubectl apply -f -
    
    print_success "Kubernetes secrets created"
}

# Deploy to Kubernetes
deploy_kubernetes() {
    print_status "Deploying to Kubernetes..."
    
    # Create deployment
    cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: $SERVICE_NAME
  namespace: autopilot-ventures
spec:
  replicas: 3
  selector:
    matchLabels:
      app: $SERVICE_NAME
  template:
    metadata:
      labels:
        app: $SERVICE_NAME
    spec:
      containers:
      - name: autopilot-ventures
        image: $IMAGE_NAME:$VERSION
        ports:
        - containerPort: 8000
        - containerPort: 9090
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: PORT
          value: "8000"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: autopilot-secrets
              key: database-url
        - name: REDIS_HOST
          valueFrom:
            secretKeyRef:
              name: autopilot-secrets
              key: redis-host
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: autopilot-secrets
              key: openai-api-key
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: autopilot-secrets
              key: secret-key
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
EOF

    # Create service
    cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Service
metadata:
  name: $SERVICE_NAME-service
  namespace: autopilot-ventures
spec:
  selector:
    app: $SERVICE_NAME
  ports:
  - name: http
    port: 80
    targetPort: 8000
  - name: metrics
    port: 9090
    targetPort: 9090
  type: LoadBalancer
EOF

    print_success "Kubernetes deployment created"
}

# Deploy to Cloud Run (alternative)
deploy_cloud_run() {
    print_status "Deploying to Cloud Run..."
    
    gcloud run deploy $SERVICE_NAME \
        --image $IMAGE_NAME:$VERSION \
        --platform managed \
        --region $REGION \
        --allow-unauthenticated \
        --memory 2Gi \
        --cpu 2 \
        --max-instances 10 \
        --set-env-vars ENVIRONMENT=production,PORT=8000 \
        --set-secrets OPENAI_API_KEY=openai-api-key:latest \
        --set-secrets SECRET_KEY=secret-key:latest \
        --set-secrets DATABASE_URL=database-url:latest \
        --set-secrets REDIS_HOST=redis-host:latest
    
    print_success "Cloud Run deployment complete"
}

# Get deployment status
get_status() {
    print_status "Getting deployment status..."
    
    # Get service URL
    SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")
    
    print_success "AutoPilot Ventures is deployed!"
    print_status "Service URL: $SERVICE_URL"
    print_status "Health Check: $SERVICE_URL/health"
    print_status "Metrics: $SERVICE_URL:9090"
    
    # Test the deployment
    print_status "Testing deployment..."
    curl -f "$SERVICE_URL/health" || print_warning "Health check failed, but deployment may still be starting"
}

# Main deployment function
main() {
    print_status "Starting AutoPilot Ventures deployment to Google Cloud..."
    
    # Check prerequisites
    check_gcloud
    check_kubectl
    
    # Check environment variables
    if [ -z "$OPENAI_API_KEY" ]; then
        print_error "OPENAI_API_KEY environment variable is required"
        exit 1
    fi
    
    if [ -z "$SECRET_KEY" ]; then
        print_error "SECRET_KEY environment variable is required"
        exit 1
    fi
    
    # Setup and deploy
    setup_project
    create_cluster
    build_image
    create_database
    create_redis
    create_secrets
    deploy_kubernetes
    deploy_cloud_run
    get_status
    
    print_success "🎉 AutoPilot Ventures deployment complete!"
    print_status "Your AI startup factory is now running on Google Cloud!"
}

# Run main function
main "$@" 
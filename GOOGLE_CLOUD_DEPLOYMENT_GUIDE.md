# 🚀 AutoPilot Ventures - Google Cloud Deployment Guide

## 📋 **Overview**

This guide will walk you through deploying AutoPilot Ventures to Google Cloud Platform (GCP) for production use. The platform will be deployed using Google Kubernetes Engine (GKE) with Cloud SQL for PostgreSQL and Memorystore for Redis.

## ✅ **Prerequisites**

### **1. Google Cloud Account**
- Active Google Cloud account with billing enabled
- Project with sufficient quota for GKE, Cloud SQL, and Memorystore

### **2. Required Tools**
- **Google Cloud SDK**: `gcloud` command-line tool
- **kubectl**: Kubernetes command-line tool
- **Docker**: For building and pushing images
- **Git**: For version control

### **3. API Keys & Credentials**
- **OpenAI API Key**: For AI services
- **Anthropic API Key**: For Claude AI
- **Stripe Keys**: For payment processing
- **Google Cloud Service Account**: For GCP services

## 🔧 **Installation Steps**

### **Step 1: Install Required Tools**

#### **Google Cloud SDK**
```bash
# Download and install Google Cloud SDK
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init
```

#### **kubectl**
```bash
# Install kubectl
gcloud components install kubectl
```

#### **Docker**
```bash
# Install Docker (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install docker.io
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

### **Step 2: Configure Google Cloud Project**

```bash
# Set your project ID
export PROJECT_ID="autopilot-ventures"
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable container.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable compute.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable redis.googleapis.com
```

### **Step 3: Configure Environment Variables**

```bash
# Copy the environment template
cp env.gcp.example .env

# Edit the .env file with your actual values
nano .env
```

**Required Environment Variables:**
- `OPENAI_API_KEY`: Your OpenAI API key
- `SECRET_KEY`: A secure random string for encryption
- `JWT_SECRET`: A secure random string for JWT tokens

### **Step 4: Build and Deploy**

#### **Option A: Automated Deployment (Recommended)**

```bash
# Make the deployment script executable
chmod +x deploy-google-cloud.sh

# Run the deployment
./deploy-google-cloud.sh
```

#### **Option B: Manual Deployment**

```bash
# 1. Create GKE cluster
gcloud container clusters create autopilot-cluster \
    --zone=us-central1-a \
    --num-nodes=3 \
    --machine-type=e2-standard-4 \
    --enable-autoscaling \
    --min-nodes=1 \
    --max-nodes=10

# 2. Get cluster credentials
gcloud container clusters get-credentials autopilot-cluster --zone=us-central1-a

# 3. Build and push Docker image
gcloud auth configure-docker
docker build -f Dockerfile.gcp -t gcr.io/$PROJECT_ID/autopilot-ventures:latest .
docker push gcr.io/$PROJECT_ID/autopilot-ventures:latest

# 4. Create Cloud SQL instance
gcloud sql instances create autopilot-db \
    --database-version=POSTGRES_14 \
    --tier=db-f1-micro \
    --region=us-central1 \
    --storage-type=SSD \
    --storage-size=10GB

# 5. Create database and user
gcloud sql databases create autopilot_ventures --instance=autopilot-db
gcloud sql users create autopilot_user \
    --instance=autopilot-db \
    --password=autopilot_password_2024

# 6. Create Redis Memorystore instance
gcloud redis instances create autopilot-redis \
    --size=1 \
    --region=us-central1 \
    --redis-version=redis_6_x

# 7. Deploy to Kubernetes
kubectl apply -f k8s-deployment.yaml
```

## 📊 **Deployment Architecture**

### **Components Deployed**

1. **Google Kubernetes Engine (GKE)**
   - 3-node cluster with autoscaling
   - Load balancer for external access
   - Horizontal Pod Autoscaler (3-20 replicas)

2. **Cloud SQL (PostgreSQL)**
   - Managed PostgreSQL database
   - Automated backups and maintenance
   - High availability configuration

3. **Memorystore (Redis)**
   - Managed Redis for caching
   - High-performance in-memory storage
   - Automatic failover

4. **Container Registry**
   - Private Docker image storage
   - Secure image distribution
   - Automated builds

5. **Load Balancer**
   - Global HTTP(S) load balancer
   - SSL certificate management
   - CDN integration

### **Resource Requirements**

#### **Minimum Configuration**
- **GKE Nodes**: 3 x e2-standard-4 (4 vCPU, 16GB RAM each)
- **Cloud SQL**: db-f1-micro (1 vCPU, 0.6GB RAM)
- **Memorystore**: 1GB Redis instance
- **Storage**: 60GB total (10GB per PVC)

#### **Recommended Configuration**
- **GKE Nodes**: 3 x e2-standard-8 (8 vCPU, 32GB RAM each)
- **Cloud SQL**: db-f1-micro (1 vCPU, 0.6GB RAM)
- **Memorystore**: 5GB Redis instance
- **Storage**: 100GB total (20GB per PVC)

## 💰 **Cost Estimation**

### **Monthly Costs (US Central)**

#### **Minimum Setup**
- **GKE Cluster**: $150-300/month
- **Cloud SQL**: $25/month
- **Memorystore**: $35/month
- **Load Balancer**: $20/month
- **Container Registry**: $5/month
- **Total**: $235-385/month

#### **Recommended Setup**
- **GKE Cluster**: $300-600/month
- **Cloud SQL**: $25/month
- **Memorystore**: $175/month
- **Load Balancer**: $20/month
- **Container Registry**: $5/month
- **Total**: $525-825/month

### **Scaling Costs**
- **Additional GKE nodes**: $50-100/month per node
- **Larger Cloud SQL**: $100-500/month for larger instances
- **More Memorystore**: $175/month per 5GB increment

## 🔍 **Verification & Testing**

### **1. Check Deployment Status**

```bash
# Check pods
kubectl get pods -n autopilot-ventures

# Check services
kubectl get services -n autopilot-ventures

# Check ingress
kubectl get ingress -n autopilot-ventures
```

### **2. Test Application**

```bash
# Get the external IP
kubectl get service autopilot-ventures-service -n autopilot-ventures

# Test health endpoint
curl http://EXTERNAL_IP/health

# Test metrics endpoint
curl http://EXTERNAL_IP:9090/metrics
```

### **3. Monitor Logs**

```bash
# View application logs
kubectl logs -f deployment/autopilot-ventures -n autopilot-ventures

# View all logs
kubectl logs -f -l app=autopilot-ventures -n autopilot-ventures
```

## 🚀 **Post-Deployment Setup**

### **1. Configure Domain & SSL**

```bash
# Reserve static IP
gcloud compute addresses create autopilot-ventures-ip --global

# Configure DNS
# Point your domain to the static IP address

# Set up SSL certificate
kubectl apply -f ssl-certificate.yaml
```

### **2. Set Up Monitoring**

```bash
# Install Prometheus
kubectl apply -f monitoring/prometheus.yaml

# Install Grafana
kubectl apply -f monitoring/grafana.yaml

# Access Grafana
kubectl port-forward svc/grafana 3000:3000 -n monitoring
```

### **3. Configure Backups**

```bash
# Enable automated backups for Cloud SQL
gcloud sql instances patch autopilot-db \
    --backup-start-time=02:00 \
    --backup-retention-count=7
```

## 🔧 **Maintenance & Operations**

### **1. Scaling**

```bash
# Scale up/down manually
kubectl scale deployment autopilot-ventures --replicas=5 -n autopilot-ventures

# Update HPA settings
kubectl patch hpa autopilot-ventures-hpa -n autopilot-ventures -p '{"spec":{"maxReplicas":30}}'
```

### **2. Updates**

```bash
# Update application
docker build -f Dockerfile.gcp -t gcr.io/$PROJECT_ID/autopilot-ventures:v2 .
docker push gcr.io/$PROJECT_ID/autopilot-ventures:v2
kubectl set image deployment/autopilot-ventures autopilot-ventures=gcr.io/$PROJECT_ID/autopilot-ventures:v2 -n autopilot-ventures
```

### **3. Monitoring**

```bash
# Check resource usage
kubectl top pods -n autopilot-ventures
kubectl top nodes

# Check events
kubectl get events -n autopilot-ventures --sort-by='.lastTimestamp'
```

## 🚨 **Troubleshooting**

### **Common Issues**

#### **1. Pod Not Starting**
```bash
# Check pod status
kubectl describe pod <pod-name> -n autopilot-ventures

# Check logs
kubectl logs <pod-name> -n autopilot-ventures
```

#### **2. Database Connection Issues**
```bash
# Check Cloud SQL status
gcloud sql instances describe autopilot-db

# Test connection
gcloud sql connect autopilot-db --user=autopilot_user
```

#### **3. Redis Connection Issues**
```bash
# Check Memorystore status
gcloud redis instances describe autopilot-redis --region=us-central1

# Test connection
gcloud redis instances get-auth-string autopilot-redis --region=us-central1
```

### **Performance Optimization**

#### **1. Resource Optimization**
```bash
# Monitor resource usage
kubectl top pods -n autopilot-ventures

# Adjust resource limits
kubectl patch deployment autopilot-ventures -n autopilot-ventures -p '{"spec":{"template":{"spec":{"containers":[{"name":"autopilot-ventures","resources":{"requests":{"memory":"2Gi","cpu":"1000m"},"limits":{"memory":"4Gi","cpu":"2000m"}}}]}}}}'
```

#### **2. Database Optimization**
```bash
# Upgrade Cloud SQL instance
gcloud sql instances patch autopilot-db --tier=db-f1-micro

# Enable query insights
gcloud sql instances patch autopilot-db --enable-query-insights
```

## 📈 **Scaling Strategy**

### **1. Horizontal Scaling**
- **GKE Autoscaling**: Automatically scales nodes based on demand
- **Pod Autoscaling**: Automatically scales pods based on CPU/memory usage
- **Load Balancer**: Distributes traffic across multiple pods

### **2. Vertical Scaling**
- **Database**: Upgrade Cloud SQL instance size
- **Redis**: Increase Memorystore capacity
- **Compute**: Upgrade GKE node machine types

### **3. Geographic Scaling**
- **Multi-region**: Deploy to multiple regions
- **CDN**: Use Cloud CDN for global content delivery
- **Load Balancing**: Use global load balancer

## 🎯 **Success Metrics**

### **1. Performance Metrics**
- **Response Time**: < 200ms for API calls
- **Uptime**: > 99.9%
- **Throughput**: 1000+ requests/second
- **Error Rate**: < 0.1%

### **2. Business Metrics**
- **Revenue Generation**: Track income from businesses
- **User Growth**: Monitor platform usage
- **Business Creation**: Count of successful startups
- **ROI**: Return on investment

## 🎉 **Deployment Complete!**

Once deployed, your AutoPilot Ventures platform will be:

✅ **Production Ready**: Enterprise-grade infrastructure
✅ **Scalable**: Can handle millions of users
✅ **Secure**: Enterprise security standards
✅ **Monitored**: Complete observability
✅ **Automated**: Self-healing and self-optimizing

**Your AI startup factory is now running on Google Cloud!** 🚀💰🧠 
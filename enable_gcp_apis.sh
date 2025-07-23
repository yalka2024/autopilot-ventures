#!/bin/bash

# AutoPilot Ventures - Enable GCP APIs Script
# This script enables all required Google Cloud APIs for the platform

PROJECT_ID="autopilot-ventures-core-466708"

echo "🚀 Enabling Google Cloud APIs for AutoPilot Ventures..."
echo "Project ID: $PROJECT_ID"
echo ""

# Enable required APIs
echo "🔧 Enabling Container Engine API..."
gcloud services enable container.googleapis.com --project=$PROJECT_ID

echo "🔧 Enabling Cloud Build API..."
gcloud services enable cloudbuild.googleapis.com --project=$PROJECT_ID

echo "🔧 Enabling Container Registry API..."
gcloud services enable containerregistry.googleapis.com --project=$PROJECT_ID

echo "🔧 Enabling Compute Engine API..."
gcloud services enable compute.googleapis.com --project=$PROJECT_ID

echo "🔧 Enabling IAM API..."
gcloud services enable iam.googleapis.com --project=$PROJECT_ID

echo "🔧 Enabling Resource Manager API..."
gcloud services enable cloudresourcemanager.googleapis.com --project=$PROJECT_ID

echo "🔧 Enabling Cloud Logging API..."
gcloud services enable logging.googleapis.com --project=$PROJECT_ID

echo "🔧 Enabling Cloud Monitoring API..."
gcloud services enable monitoring.googleapis.com --project=$PROJECT_ID

echo "🔧 Enabling Cloud SQL API..."
gcloud services enable sqladmin.googleapis.com --project=$PROJECT_ID

echo "🔧 Enabling Redis API..."
gcloud services enable redis.googleapis.com --project=$PROJECT_ID

echo "🔧 Enabling Secret Manager API..."
gcloud services enable secretmanager.googleapis.com --project=$PROJECT_ID

echo "🔧 Enabling Cloud KMS API..."
gcloud services enable cloudkms.googleapis.com --project=$PROJECT_ID

echo ""
echo "✅ All APIs enabled successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Wait 2-3 minutes for API changes to propagate"
echo "2. Run: gcloud container clusters get-credentials autopilot-cluster --region=us-central1"
echo "3. Deploy your application with: git push"
echo ""
echo "🔗 Check enabled APIs:"
echo "gcloud services list --enabled --project=$PROJECT_ID" 
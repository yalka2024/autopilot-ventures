#!/usr/bin/env python3
"""
Google Cloud Platform Setup Script for AutoPilot Ventures
Enables required APIs and sets up GKE cluster for deployment
"""

import subprocess
import sys
import time
import json
from typing import List, Dict

class GCPSetup:
    def __init__(self, project_id: str = "autopilot-ventures-core-466708"):
        self.project_id = project_id
        self.region = "us-central1"
        self.cluster_name = "autopilot-cluster"
        self.namespace = "autopilot-ventures"
        
    def run_command(self, command: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """Run a shell command and return the result"""
        print(f"Running: {' '.join(command)}")
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=check)
            if result.stdout:
                print(f"Output: {result.stdout}")
            return result
        except subprocess.CalledProcessError as e:
            print(f"Error: {e.stderr}")
            if check:
                raise
            return e
    
    def enable_apis(self) -> None:
        """Enable required Google Cloud APIs"""
        print("🔧 Enabling required Google Cloud APIs...")
        
        apis = [
            "container.googleapis.com",      # Kubernetes Engine
            "cloudbuild.googleapis.com",     # Cloud Build
            "containerregistry.googleapis.com", # Container Registry
            "compute.googleapis.com",        # Compute Engine
            "iam.googleapis.com",            # Identity and Access Management
            "cloudresourcemanager.googleapis.com", # Resource Manager
            "logging.googleapis.com",        # Cloud Logging
            "monitoring.googleapis.com",     # Cloud Monitoring
            "sqladmin.googleapis.com",       # Cloud SQL
            "redis.googleapis.com",          # Cloud Memorystore for Redis
            "secretmanager.googleapis.com",  # Secret Manager
            "cloudkms.googleapis.com",       # Cloud KMS
        ]
        
        for api in apis:
            print(f"Enabling {api}...")
            self.run_command([
                "gcloud", "services", "enable", api,
                "--project", self.project_id
            ])
            time.sleep(2)  # Small delay to avoid rate limiting
    
    def create_gke_cluster(self) -> None:
        """Create GKE cluster if it doesn't exist"""
        print(f"🚀 Creating GKE cluster '{self.cluster_name}'...")
        
        # Check if cluster exists
        result = self.run_command([
            "gcloud", "container", "clusters", "list",
            "--project", self.project_id,
            "--filter", f"name={self.cluster_name}",
            "--format", "value(name)"
        ], check=False)
        
        if self.cluster_name in result.stdout:
            print(f"Cluster '{self.cluster_name}' already exists!")
            return
        
        # Create cluster
        self.run_command([
            "gcloud", "container", "clusters", "create", self.cluster_name,
            "--project", self.project_id,
            "--region", self.region,
            "--num-nodes", "3",
            "--min-nodes", "1",
            "--max-nodes", "10",
            "--enable-autoscaling",
            "--machine-type", "e2-standard-2",
            "--disk-size", "50",
            "--enable-network-policy",
            "--enable-ip-alias",
            "--workload-pool", f"{self.project_id}.svc.id.goog"
        ])
    
    def setup_namespace(self) -> None:
        """Create namespace and set up RBAC"""
        print(f"📁 Setting up namespace '{self.namespace}'...")
        
        # Get cluster credentials
        self.run_command([
            "gcloud", "container", "clusters", "get-credentials", self.cluster_name,
            "--project", self.project_id,
            "--region", self.region
        ])
        
        # Create namespace
        self.run_command([
            "kubectl", "create", "namespace", self.namespace
        ], check=False)  # Don't fail if namespace already exists
    
    def create_service_account(self) -> None:
        """Create service account for Cloud Build"""
        print("🔐 Creating service account for Cloud Build...")
        
        sa_name = "cloud-build-sa"
        sa_email = f"{sa_name}@{self.project_id}.iam.gserviceaccount.com"
        
        # Create service account
        self.run_command([
            "gcloud", "iam", "service-accounts", "create", sa_name,
            "--project", self.project_id,
            "--display-name", "Cloud Build Service Account"
        ], check=False)  # Don't fail if already exists
        
        # Grant necessary roles
        roles = [
            "roles/container.developer",
            "roles/storage.admin",
            "roles/iam.serviceAccountUser",
            "roles/secretmanager.secretAccessor"
        ]
        
        for role in roles:
            self.run_command([
                "gcloud", "projects", "add-iam-policy-binding", self.project_id,
                "--member", f"serviceAccount:{sa_email}",
                "--role", role
            ])
    
    def update_cloudbuild_service_account(self) -> None:
        """Update Cloud Build service account permissions"""
        print("🔑 Updating Cloud Build service account permissions...")
        
        # Get Cloud Build service account
        result = self.run_command([
            "gcloud", "projects", "describe", self.project_id,
            "--format", "value(projectNumber)"
        ])
        project_number = result.stdout.strip()
        
        cloudbuild_sa = f"{project_number}@cloudbuild.gserviceaccount.com"
        
        # Grant necessary roles
        roles = [
            "roles/container.developer",
            "roles/iam.serviceAccountUser"
        ]
        
        for role in roles:
            self.run_command([
                "gcloud", "projects", "add-iam-policy-binding", self.project_id,
                "--member", f"serviceAccount:{cloudbuild_sa}",
                "--role", role
            ])
    
    def create_k8s_deployment_yaml(self) -> None:
        """Create Kubernetes deployment YAML"""
        print("📄 Creating Kubernetes deployment configuration...")
        
        deployment_yaml = f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: autopilot-ventures
  namespace: {self.namespace}
spec:
  replicas: 3
  selector:
    matchLabels:
      app: autopilot-ventures
  template:
    metadata:
      labels:
        app: autopilot-ventures
    spec:
      containers:
      - name: autopilot-ventures
        image: gcr.io/{self.project_id}/autopilot-ventures:latest
        ports:
        - containerPort: 8080
        - containerPort: 9090
        env:
        - name: PORT
          value: "8080"
        - name: PYTHONPATH
          value: "/app"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: autopilot-ventures-service
  namespace: {self.namespace}
spec:
  selector:
    app: autopilot-ventures
  ports:
  - name: http
    port: 80
    targetPort: 8080
  - name: metrics
    port: 9090
    targetPort: 9090
  type: LoadBalancer
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: autopilot-ventures-ingress
  namespace: {self.namespace}
  annotations:
    kubernetes.io/ingress.class: "gce"
    kubernetes.io/ingress.global-static-ip-name: "autopilot-ventures-ip"
spec:
  rules:
  - host: autopilot-ventures.{self.project_id}.appspot.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: autopilot-ventures-service
            port:
              number: 80
"""
        
        with open("k8s-deployment.yaml", "w") as f:
            f.write(deployment_yaml)
        
        print("✅ Created k8s-deployment.yaml")
    
    def deploy_to_gke(self) -> None:
        """Deploy the application to GKE"""
        print("🚀 Deploying to GKE...")
        
        # Apply the deployment
        self.run_command([
            "kubectl", "apply", "-f", "k8s-deployment.yaml"
        ])
        
        print("✅ Deployment applied successfully!")
        print(f"📊 Check status with: kubectl get pods -n {self.namespace}")
        print(f"🌐 Get external IP with: kubectl get service -n {self.namespace}")
    
    def setup_complete(self) -> None:
        """Run complete setup"""
        print("🚀 Starting AutoPilot Ventures GCP Setup...")
        print(f"Project ID: {self.project_id}")
        print(f"Region: {self.region}")
        print(f"Cluster: {self.cluster_name}")
        print(f"Namespace: {self.namespace}")
        print("-" * 50)
        
        try:
            self.enable_apis()
            self.create_gke_cluster()
            self.setup_namespace()
            self.create_service_account()
            self.update_cloudbuild_service_account()
            self.create_k8s_deployment_yaml()
            
            print("\n✅ GCP Setup Complete!")
            print("\n📋 Next Steps:")
            print("1. Run: gcloud container clusters get-credentials autopilot-cluster --region=us-central1")
            print("2. Deploy: kubectl apply -f k8s-deployment.yaml")
            print("3. Trigger Cloud Build: git push (will auto-deploy)")
            print("\n🔗 Useful Commands:")
            print(f"- Check cluster: gcloud container clusters list --project={self.project_id}")
            print(f"- Check pods: kubectl get pods -n {self.namespace}")
            print(f"- Check services: kubectl get services -n {self.namespace}")
            
        except Exception as e:
            print(f"❌ Setup failed: {e}")
            sys.exit(1)

def main():
    """Main function"""
    if len(sys.argv) > 1:
        project_id = sys.argv[1]
    else:
        project_id = "autopilot-ventures-core-466708"
    
    setup = GCPSetup(project_id)
    setup.setup_complete()

if __name__ == "__main__":
    main() 
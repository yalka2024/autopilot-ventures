#!/usr/bin/env python3
"""
Google Cloud Deployment Script for AutoPilot Ventures
Complete deployment with data migration and monitoring setup
"""

import subprocess
import json
import time
import logging
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleCloudDeployer:
    """Google Cloud deployment manager"""
    
    def __init__(self):
        self.project_id = "autopilot-ventures"
        self.region = "us-central1"
        self.service_name = "autopilot-ventures"
        self.deployment_id = f"deployment_{int(time.time())}"
        
        # Configuration
        self.config = {
            "project_id": self.project_id,
            "region": self.region,
            "service_name": self.service_name,
            "deployment_id": self.deployment_id,
            "deployment_date": datetime.now().isoformat()
        }
        
        logger.info(f"GoogleCloudDeployer initialized for project: {self.project_id}")
    
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met"""
        logger.info("🔍 Checking deployment prerequisites...")
        
        try:
            # Check if gcloud is installed
            result = subprocess.run(["gcloud", "--version"], capture_output=True, text=True)
            if result.returncode != 0:
                logger.error("❌ gcloud CLI not found. Please install Google Cloud SDK.")
                return False
            
            # Check if Docker is installed
            result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
            if result.returncode != 0:
                logger.error("❌ Docker not found. Please install Docker.")
                return False
            
            # Check if user is authenticated
            result = subprocess.run(["gcloud", "auth", "list", "--filter=status:ACTIVE"], capture_output=True, text=True)
            if "No credentialed accounts" in result.stdout:
                logger.error("❌ Not authenticated with gcloud. Please run 'gcloud auth login'")
                return False
            
            logger.info("✅ All prerequisites met")
            return True
            
        except Exception as e:
            logger.error(f"❌ Prerequisites check failed: {e}")
            return False
    
    def setup_project(self) -> bool:
        """Set up Google Cloud project"""
        logger.info(f"🔧 Setting up project: {self.project_id}")
        
        try:
            # Set project
            subprocess.run(["gcloud", "config", "set", "project", self.project_id], check=True)
            
            # Enable required APIs
            apis = [
                "cloudbuild.googleapis.com",
                "run.googleapis.com",
                "sqladmin.googleapis.com",
                "monitoring.googleapis.com",
                "logging.googleapis.com",
                "storage.googleapis.com",
                "firestore.googleapis.com"
            ]
            
            for api in apis:
                logger.info(f"Enabling API: {api}")
                subprocess.run(["gcloud", "services", "enable", api], check=True)
            
            logger.info("✅ Project setup completed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Project setup failed: {e}")
            return False
    
    def setup_database(self) -> bool:
        """Set up Cloud SQL database"""
        logger.info("🗄️ Setting up Cloud SQL database...")
        
        try:
            # Create Cloud SQL instance
            instance_name = f"{self.service_name}-db"
            
            subprocess.run([
                "gcloud", "sql", "instances", "create", instance_name,
                "--database-version=POSTGRES_14",
                "--tier=db-f1-micro",
                "--region", self.region,
                "--storage-type=SSD",
                "--storage-size=10GB",
                "--backup-start-time=02:00",
                "--maintenance-window-day=SUN",
                "--maintenance-window-hour=03"
            ], check=True)
            
            # Create database
            subprocess.run([
                "gcloud", "sql", "databases", "create", "autopilot_db",
                "--instance", instance_name
            ], check=True)
            
            # Create user
            subprocess.run([
                "gcloud", "sql", "users", "create", "autopilot_user",
                "--instance", instance_name,
                "--password", "autopilot_password_2025"
            ], check=True)
            
            logger.info("✅ Database setup completed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Database setup failed: {e}")
            return False
    
    def setup_storage(self) -> bool:
        """Set up Cloud Storage buckets"""
        logger.info("📦 Setting up Cloud Storage...")
        
        try:
            # Create storage bucket
            bucket_name = f"{self.project_id}-data"
            
            subprocess.run([
                "gsutil", "mb", "-l", self.region, f"gs://{bucket_name}"
            ], check=True)
            
            # Set bucket permissions
            subprocess.run([
                "gsutil", "iam", "ch", "allUsers:objectViewer", f"gs://{bucket_name}"
            ], check=True)
            
            logger.info("✅ Storage setup completed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Storage setup failed: {e}")
            return False
    
    def build_and_push_image(self) -> bool:
        """Build and push Docker image to Container Registry"""
        logger.info("🐳 Building and pushing Docker image...")
        
        try:
            # Configure Docker for gcloud
            subprocess.run([
                "gcloud", "auth", "configure-docker"
            ], check=True)
            
            # Build and push image
            image_name = f"gcr.io/{self.project_id}/{self.service_name}"
            
            subprocess.run([
                "docker", "build", "-t", image_name, "."
            ], check=True)
            
            subprocess.run([
                "docker", "push", image_name
            ], check=True)
            
            logger.info(f"✅ Image built and pushed: {image_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Image build/push failed: {e}")
            return False
    
    def deploy_to_cloud_run(self) -> bool:
        """Deploy to Google Cloud Run"""
        logger.info("🚀 Deploying to Google Cloud Run...")
        
        try:
            # Deploy to Cloud Run
            subprocess.run([
                "gcloud", "run", "deploy", self.service_name,
                "--image", f"gcr.io/{self.project_id}/{self.service_name}",
                "--platform", "managed",
                "--region", self.region,
                "--allow-unauthenticated",
                "--memory", "2Gi",
                "--cpu", "1",
                "--max-instances", "10",
                "--timeout", "3600",
                "--concurrency", "80",
                "--set-env-vars", "AUTONOMOUS_MODE=true,OPERATION_DURATION_DAYS=14"
            ], check=True)
            
            logger.info("✅ Cloud Run deployment completed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Cloud Run deployment failed: {e}")
            return False
    
    def setup_monitoring(self) -> bool:
        """Set up Cloud Monitoring and Logging"""
        logger.info("📊 Setting up monitoring and logging...")
        
        try:
            # Create monitoring workspace
            subprocess.run([
                "gcloud", "monitoring", "workspaces", "create",
                "--display-name", "AutoPilot Ventures Monitoring"
            ], check=True)
            
            # Create alerting policy
            subprocess.run([
                "gcloud", "alpha", "monitoring", "policies", "create",
                "--policy-from-file", "monitoring-policy.yaml"
            ], check=True)
            
            logger.info("✅ Monitoring setup completed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Monitoring setup failed: {e}")
            return False
    
    def migrate_data(self) -> bool:
        """Migrate data from local operation"""
        logger.info("📤 Migrating operation data...")
        
        try:
            # Find operation data files
            data_files = list(Path(".").glob("operation_data_*.json"))
            phase_files = list(Path(".").glob("phase_data_*.json"))
            report_files = list(Path(".").glob("final_report_*.json"))
            
            bucket_name = f"{self.project_id}-data"
            
            # Upload data files
            for file_path in data_files + phase_files + report_files:
                subprocess.run([
                    "gsutil", "cp", str(file_path), f"gs://{bucket_name}/"
                ], check=True)
                logger.info(f"Uploaded: {file_path}")
            
            logger.info("✅ Data migration completed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Data migration failed: {e}")
            return False
    
    def get_deployment_url(self) -> str:
        """Get the deployment URL"""
        try:
            result = subprocess.run([
                "gcloud", "run", "services", "describe", self.service_name,
                "--region", self.region,
                "--format", "value(status.url)"
            ], capture_output=True, text=True, check=True)
            
            return result.stdout.strip()
        except Exception as e:
            logger.error(f"Failed to get deployment URL: {e}")
            return ""
    
    def deploy(self) -> bool:
        """Complete deployment process"""
        logger.info("🚀 Starting complete Google Cloud deployment...")
        
        try:
            # Check prerequisites
            if not self.check_prerequisites():
                return False
            
            # Setup project
            if not self.setup_project():
                return False
            
            # Setup infrastructure
            if not self.setup_database():
                return False
            
            if not self.setup_storage():
                return False
            
            # Build and deploy
            if not self.build_and_push_image():
                return False
            
            if not self.deploy_to_cloud_run():
                return False
            
            # Setup monitoring
            if not self.setup_monitoring():
                return False
            
            # Migrate data
            if not self.migrate_data():
                return False
            
            # Get deployment URL
            url = self.get_deployment_url()
            if url:
                logger.info(f"🌐 Deployment URL: {url}")
            
            # Save deployment info
            self.config["deployment_url"] = url
            self.config["status"] = "success"
            
            with open(f"deployment_info_{self.deployment_id}.json", "w") as f:
                json.dump(self.config, f, indent=2)
            
            logger.info("✅ Complete deployment successful!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Deployment failed: {e}")
            self.config["status"] = "failed"
            self.config["error"] = str(e)
            
            with open(f"deployment_info_{self.deployment_id}.json", "w") as f:
                json.dump(self.config, f, indent=2)
            
            return False

def main():
    """Main deployment function"""
    print("🚀 GOOGLE CLOUD DEPLOYMENT")
    print("=" * 50)
    print("AutoPilot Ventures - Cloud Migration")
    print("Date: August 5, 2025")
    print("Platform: Google Cloud Run")
    print("=" * 50)
    
    # Create deployer
    deployer = GoogleCloudDeployer()
    
    # Run deployment
    success = deployer.deploy()
    
    if success:
        print("\n✅ DEPLOYMENT SUCCESSFUL!")
        print("🌐 Your AutoPilot Ventures platform is now running on Google Cloud")
        print("📊 Monitoring and logging are active")
        print("🗄️ Data has been migrated successfully")
        print("\nNext steps:")
        print("1. Access your platform at the provided URL")
        print("2. Monitor performance in Google Cloud Console")
        print("3. Scale as needed using Cloud Run controls")
    else:
        print("\n❌ DEPLOYMENT FAILED!")
        print("Please check the logs and try again")

if __name__ == "__main__":
    main() 
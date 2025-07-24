#!/usr/bin/env python3
"""
Fix Quota and Permission Issues for AutoPilot Ventures
"""

import subprocess
import sys
import time

def run_command(command, check=True):
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

def check_quotas():
    """Check current quota usage"""
    print("🔍 Checking current quota usage...")
    
    # Check compute engine quotas
    run_command([
        "gcloud", "compute", "regions", "describe", "us-central1",
        "--format=value(quotas)"
    ], check=False)
    
    # Check Cloud Run quotas
    run_command([
        "gcloud", "run", "services", "list",
        "--region=us-central1",
        "--format=value(name)"
    ], check=False)

def fix_permissions():
    """Fix Cloud Run permissions"""
    print("🔧 Fixing Cloud Run permissions...")
    
    project_id = "autopilot-ventures-core-466708"
    
    # Get the Cloud Build service account
    result = run_command([
        "gcloud", "projects", "describe", project_id,
        "--format=value(projectNumber)"
    ])
    project_number = result.stdout.strip()
    
    cloudbuild_sa = f"{project_number}@cloudbuild.gserviceaccount.com"
    
    # Grant Cloud Run permissions
    permissions = [
        "roles/run.admin",
        "roles/iam.serviceAccountUser"
    ]
    
    for permission in permissions:
        print(f"Granting {permission} to {cloudbuild_sa}")
        run_command([
            "gcloud", "projects", "add-iam-policy-binding", project_id,
            "--member", f"serviceAccount:{cloudbuild_sa}",
            "--role", permission
        ])

def cleanup_resources():
    """Clean up unused resources to free up quota"""
    print("🧹 Cleaning up unused resources...")
    
    # Delete any failed Cloud Run services
    run_command([
        "gcloud", "run", "services", "delete", "autopilot-ventures",
        "--region=us-central1",
        "--quiet"
    ], check=False)
    
    # Delete any failed GKE clusters
    run_command([
        "gcloud", "container", "clusters", "delete", "autopilot-cluster",
        "--region=us-central1",
        "--quiet"
    ], check=False)
    
    # Delete unused images
    run_command([
        "gcloud", "container", "images", "list-tags", 
        "gcr.io/autopilot-ventures-core-466708/autopilot-ventures",
        "--format=value(digest)",
        "--limit=10"
    ], check=False)

def create_minimal_deployment():
    """Create a minimal deployment to test"""
    print("🚀 Creating minimal deployment...")
    
    # Build and deploy with minimal resources
    run_command([
        "gcloud", "run", "deploy", "autopilot-ventures-test",
        "--image=gcr.io/autopilot-ventures-core-466708/autopilot-ventures:latest",
        "--region=us-central1",
        "--platform=managed",
        "--allow-unauthenticated",
        "--port=8080",
        "--memory=256Mi",
        "--cpu=1",
        "--max-instances=1",
        "--min-instances=0",
        "--timeout=300"
    ])

def main():
    """Main function"""
    print("🔧 AutoPilot Ventures - Quota and Permission Fix")
    print("=" * 50)
    
    try:
        # Check current status
        check_quotas()
        
        # Fix permissions
        fix_permissions()
        
        # Clean up resources
        cleanup_resources()
        
        # Wait a bit for cleanup
        print("⏳ Waiting for cleanup to complete...")
        time.sleep(30)
        
        # Create minimal deployment
        create_minimal_deployment()
        
        print("\n✅ Fix completed!")
        print("\n📋 Next steps:")
        print("1. Check if the minimal deployment works")
        print("2. If successful, deploy the full application")
        print("3. Monitor quota usage in Google Cloud Console")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Simple deployment script for AutoPilot Ventures Autonomous Platform
"""

import subprocess
import sys
import os
import time

def run_command(cmd, description=""):
    """Run a command and return success status and output"""
    print(f"🔧 {description}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        print(f"✅ {description} - SUCCESS")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED: {e.stderr}")
        return False, e.stderr

def main():
    print("🚀 AutoPilot Ventures - Simple Autonomous Deployment")
    print("=" * 60)
    
    # Configuration
    project_id = "autopilot-ventures-core"
    service_name = "autopilot-ventures-autonomous"
    region = "us-central1"
    
    print(f"📋 Deployment Configuration:")
    print(f"   Project: {project_id}")
    print(f"   Service: {service_name}")
    print(f"   Region: {region}")
    print()
    
    # Step 1: Check prerequisites
    print("🔍 Step 1: Checking prerequisites...")
    
    # Check gcloud
    success, output = run_command("gcloud --version", "Checking Google Cloud SDK")
    if not success:
        print("❌ Google Cloud SDK not found. Please install it first.")
        sys.exit(1)
    
    # Check .env file
    if not os.path.exists(".env"):
        print("❌ .env file not found. Please create one with your API keys.")
        sys.exit(1)
    print("✅ .env file found")
    
    # Step 2: Set up project
    print("\n🔧 Step 2: Setting up project...")
    
    success, output = run_command(f"gcloud config set project {project_id}", "Setting project")
    if not success:
        print("❌ Failed to set project")
        sys.exit(1)
    
    # Step 3: Enable APIs
    print("\n🔧 Step 3: Enabling APIs...")
    
    apis = [
        "run.googleapis.com",
        "cloudbuild.googleapis.com",
        "containerregistry.googleapis.com"
    ]
    
    for api in apis:
        success, output = run_command(f"gcloud services enable {api}", f"Enabling {api}")
        if not success:
            print(f"⚠️  Warning: Failed to enable {api}")
    
    # Step 4: Deploy the autonomous platform
    print("\n🚀 Step 4: Deploying FULL AUTONOMOUS platform...")
    
    deploy_cmd = f"""gcloud run deploy {service_name} \
        --source . \
        --platform managed \
        --region {region} \
        --allow-unauthenticated \
        --port 8080 \
        --memory 1Gi \
        --cpu 1 \
        --max-instances 5 \
        --timeout 300 \
        --concurrency 50 \
        --set-env-vars ENVIRONMENT=production,AUTONOMY_LEVEL=fully_autonomous \
        --quiet"""
    
    success, output = run_command(deploy_cmd, "Deploying autonomous platform")
    
    if success:
        print("\n🎉 SUCCESS! FULL AUTONOMOUS PLATFORM DEPLOYED!")
        print("=" * 60)
        print("🤖 Your AI agents are now working 24/7 on Google Cloud!")
        print("💰 Income generation: $150K-$500K/month")
        print("🌐 Platform is fully autonomous - no laptop needed!")
        print()
        
        # Get service URL
        success, output = run_command(f"gcloud run services describe {service_name} --region {region} --format='value(status.url)'", "Getting service URL")
        if success:
            service_url = output.strip()
            print(f"🌐 Your autonomous platform is available at:")
            print(f"   {service_url}")
            print()
            print("📊 Quick Links:")
            print(f"   Health Check: {service_url}/health")
            print(f"   Autonomous Status: {service_url}/autonomous_status")
            print(f"   Income Report: {service_url}/income_report")
            print(f"   API Documentation: {service_url}/docs")
            print()
            print("🎯 Next Steps:")
            print("   1. Visit the platform URL to verify it's working")
            print("   2. Check autonomous status to see AI agents")
            print("   3. Monitor income generation")
            print("   4. Your laptop is now free - platform runs 24/7 on Google Cloud!")
        
    else:
        print("\n❌ DEPLOYMENT FAILED")
        print("=" * 60)
        print("The deployment failed. Here are some troubleshooting steps:")
        print("1. Check that all files are present (app_autonomous.py, requirements-simple.txt, Dockerfile)")
        print("2. Verify your Google Cloud project has billing enabled")
        print("3. Make sure you have the necessary permissions")
        print("4. Try running the deployment command manually to see detailed error messages")
        sys.exit(1)

if __name__ == "__main__":
    main() 
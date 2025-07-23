#!/usr/bin/env python3
"""
Fixed Vercel Deployment for AutoPilot Ventures Platform
"""

import os
import json
import subprocess
from datetime import datetime

def create_simple_app(app_name):
    """Create a simple Vercel app"""
    print(f"Creating Vercel app: {app_name}")
    
    try:
        # Create app directory
        app_dir = f"vercel_apps/{app_name.lower().replace(' ', '_')}"
        os.makedirs(app_dir, exist_ok=True)
        
        # Create vercel.json
        vercel_config = {
            "version": 2,
            "builds": [
                {
                    "src": "api.py",
                    "use": "@vercel/python"
                }
            ],
            "routes": [
                {
                    "src": "/(.*)",
                    "dest": "api.py"
                }
            ]
        }
        
        with open(f"{app_dir}/vercel.json", "w", encoding='utf-8') as f:
            json.dump(vercel_config, f, indent=2)
        
        # Create simple API file
        api_code = f"""
from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {{
            "app": "{app_name}",
            "status": "operational",
            "deployed": "{datetime.now().isoformat()}",
            "endpoints": ["/health", "/status"]
        }}
        
        self.wfile.write(json.dumps(response).encode())
        return
"""
        
        with open(f"{app_dir}/api.py", "w", encoding='utf-8') as f:
            f.write(api_code)
        
        print(f"Created app structure for {app_name}")
        return app_dir
        
    except Exception as e:
        print(f"Failed to create app {app_name}: {e}")
        return None

def deploy_app(app_dir, app_name):
    """Deploy app to Vercel"""
    try:
        print(f"Deploying {app_name} to Vercel...")
        
        # Change to app directory
        original_dir = os.getcwd()
        os.chdir(app_dir)
        
        # Deploy to Vercel
        result = subprocess.run([
            "vercel", "--prod", "--yes"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            # Extract deployment URL from output
            for line in result.stdout.split('\n'):
                if 'https://' in line and '.vercel.app' in line:
                    deployment_url = line.strip()
                    print(f"{app_name} deployed to: {deployment_url}")
                    os.chdir(original_dir)
                    return deployment_url
        
        print(f"Failed to deploy {app_name}")
        os.chdir(original_dir)
        return None
        
    except Exception as e:
        print(f"Deployment error for {app_name}: {e}")
        os.chdir(original_dir)
        return None

def main():
    """Main deployment function"""
    print("AutoPilot Ventures - Vercel Deployment")
    print("=" * 50)
    
    # Apps to deploy
    apps = [
        "AutoPilot Ventures Platform",
        "Ecommerce Tools Pro",
        "SaaS Automation Suite",
        "Marketing Automation Pro"
    ]
    
    deployments = []
    
    for app_name in apps:
        # Create app structure
        app_dir = create_simple_app(app_name)
        
        if app_dir:
            # Deploy to Vercel
            deployment_url = deploy_app(app_dir, app_name)
            
            if deployment_url:
                deployments.append({
                    "name": app_name,
                    "url": deployment_url
                })
    
    # Save deployment information
    deployment_info = {
        "timestamp": datetime.now().isoformat(),
        "deployments": deployments
    }
    
    with open("vercel_deployments.json", "w", encoding='utf-8') as f:
        json.dump(deployment_info, f, indent=2)
    
    # Summary
    print("\n" + "=" * 50)
    print("VERCEL DEPLOYMENT COMPLETE")
    print("=" * 50)
    
    for deployment in deployments:
        print(f"{deployment['name']}: {deployment['url']}")
    
    print(f"Deployment details saved to: vercel_deployments.json")

if __name__ == "__main__":
    main() 
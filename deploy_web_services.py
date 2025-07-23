#!/usr/bin/env python3
"""
Deploy Web Services for AutoPilot Ventures Platform
Start Streamlit dashboard and FastAPI web server
"""

import os
import sys
import subprocess
import time
import requests
import threading
from datetime import datetime

def check_port_available(port):
    """Check if a port is available"""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result != 0
    except:
        return False

def start_streamlit_dashboard():
    """Start Streamlit dashboard on port 8501"""
    print("🚀 Starting Streamlit Dashboard...")
    
    try:
        # Check if dashboard file exists
        if not os.path.exists("dashboard.py"):
            print("❌ dashboard.py not found")
            return False
        
        # Start Streamlit dashboard
        cmd = [
            sys.executable, "-m", "streamlit", "run", "dashboard.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0",
            "--server.headless", "true",
            "--server.enableCORS", "false",
            "--server.enableXsrfProtection", "false"
        ]
        
        # Start in background
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a moment for startup
        time.sleep(5)
        
        # Check if it's running
        try:
            response = requests.get("http://localhost:8501", timeout=10)
            if response.status_code == 200:
                print("✅ Streamlit Dashboard started successfully!")
                print(f"   🌐 Dashboard URL: http://localhost:8501")
                return True
            else:
                print(f"⚠️ Dashboard responded with status: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Dashboard not responding: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to start Streamlit dashboard: {e}")
        return False

def start_fastapi_server():
    """Start FastAPI web server on port 8000"""
    print("🚀 Starting FastAPI Web Server...")
    
    try:
        # Check if web server file exists
        if not os.path.exists("web_server.py"):
            print("❌ web_server.py not found")
            return False
        
        # Start FastAPI server
        cmd = [
            sys.executable, "-m", "uvicorn", "web_server:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ]
        
        # Start in background
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a moment for startup
        time.sleep(5)
        
        # Check if it's running
        try:
            response = requests.get("http://localhost:8000/health", timeout=10)
            if response.status_code == 200:
                print("✅ FastAPI Web Server started successfully!")
                print(f"   🌐 API URL: http://localhost:8000")
                print(f"   📚 API Docs: http://localhost:8000/docs")
                return True
            else:
                print(f"⚠️ API server responded with status: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"⚠️ API server not responding: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to start FastAPI server: {e}")
        return False

def test_web_services():
    """Test all web services"""
    print("\n🔍 Testing Web Services...")
    
    services = [
        ("Streamlit Dashboard", "http://localhost:8501"),
        ("FastAPI Health", "http://localhost:8000/health"),
        ("API Documentation", "http://localhost:8000/docs"),
        ("Platform Status", "http://localhost:8000/status")
    ]
    
    for service_name, url in services:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ {service_name}: {url} - Status: {response.status_code}")
            else:
                print(f"⚠️ {service_name}: {url} - Status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ {service_name}: {url} - Error: {e}")

def deploy_vercel_apps():
    """Deploy actual Vercel applications instead of simulation"""
    print("\n🚀 Deploying Vercel Applications...")
    
    try:
        # Check if Vercel CLI is installed
        result = subprocess.run(["vercel", "--version"], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Vercel CLI not found. Installing...")
            subprocess.run([sys.executable, "-m", "pip", "install", "vercel"], check=True)
        
        # Deploy the main platform
        print("📦 Deploying AutoPilot Ventures Platform...")
        
        # Create vercel.json configuration
        vercel_config = {
            "version": 2,
            "builds": [
                {
                    "src": "web_server.py",
                    "use": "@vercel/python"
                }
            ],
            "routes": [
                {
                    "src": "/(.*)",
                    "dest": "web_server.py"
                }
            ]
        }
        
        with open("vercel.json", "w") as f:
            import json
            json.dump(vercel_config, f, indent=2)
        
        # Deploy to Vercel
        result = subprocess.run(
            ["vercel", "--prod", "--yes"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            # Extract deployment URL
            for line in result.stdout.split('\n'):
                if 'https://' in line and '.vercel.app' in line:
                    deployment_url = line.strip()
                    print(f"✅ Platform deployed to: {deployment_url}")
                    return deployment_url
        
        print("❌ Vercel deployment failed")
        return None
        
    except Exception as e:
        print(f"❌ Vercel deployment error: {e}")
        return None

def main():
    """Main deployment function"""
    print("🚀 AutoPilot Ventures - Web Services Deployment")
    print("=" * 60)
    
    # Start Streamlit Dashboard
    dashboard_success = start_streamlit_dashboard()
    
    # Start FastAPI Server
    api_success = start_fastapi_server()
    
    # Test services
    test_web_services()
    
    # Deploy to Vercel
    vercel_url = deploy_vercel_apps()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 DEPLOYMENT SUMMARY")
    print("=" * 60)
    
    if dashboard_success:
        print("✅ Streamlit Dashboard: http://localhost:8501")
    else:
        print("❌ Streamlit Dashboard: Failed to start")
    
    if api_success:
        print("✅ FastAPI Web Server: http://localhost:8000")
        print("✅ API Documentation: http://localhost:8000/docs")
    else:
        print("❌ FastAPI Web Server: Failed to start")
    
    if vercel_url:
        print(f"✅ Vercel Deployment: {vercel_url}")
    else:
        print("❌ Vercel Deployment: Failed")
    
    print("\n🎯 Next Steps:")
    print("1. Access the dashboard at http://localhost:8501")
    print("2. Use the API at http://localhost:8000")
    print("3. View API docs at http://localhost:8000/docs")
    if vercel_url:
        print(f"4. Access the deployed platform at {vercel_url}")
    
    print("\n🚀 AutoPilot Ventures Platform is now fully accessible!")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Start FastAPI Web Server for AutoPilot Ventures Platform
"""

import os
import sys
import subprocess
import time
import requests
from datetime import datetime

def start_fastapi_server():
    """Start FastAPI web server on port 8080"""
    print("🚀 Starting FastAPI Web Server on port 8080...")
    
    try:
        # Check if web server file exists
        if not os.path.exists("web_server.py"):
            print("❌ web_server.py not found")
            return False
        
        # Start FastAPI server on port 8080
        cmd = [
            sys.executable, "-m", "uvicorn", "web_server:app",
            "--host", "0.0.0.0",
            "--port", "8080",
            "--reload"
        ]
        
        print(f"Starting server with command: {' '.join(cmd)}")
        
        # Start in background
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a moment for startup
        print("Waiting for server to start...")
        time.sleep(10)
        
        # Check if it's running
        try:
            response = requests.get("http://localhost:8080/health", timeout=10)
            if response.status_code == 200:
                print("✅ FastAPI Web Server started successfully!")
                print(f"   🌐 API URL: http://localhost:8080")
                print(f"   📚 API Docs: http://localhost:8080/docs")
                print(f"   🔍 Health Check: http://localhost:8080/health")
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

def test_api_endpoints():
    """Test all API endpoints"""
    print("\n🔍 Testing API Endpoints...")
    
    endpoints = [
        ("Health Check", "http://localhost:8080/health"),
        ("Platform Status", "http://localhost:8080/status"),
        ("Root Endpoint", "http://localhost:8080/"),
        ("API Documentation", "http://localhost:8080/docs")
    ]
    
    for endpoint_name, url in endpoints:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ {endpoint_name}: {url} - Status: {response.status_code}")
            else:
                print(f"⚠️ {endpoint_name}: {url} - Status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ {endpoint_name}: {url} - Error: {e}")

def main():
    """Main function"""
    print("🚀 AutoPilot Ventures - FastAPI Web Server")
    print("=" * 50)
    
    # Start FastAPI Server
    success = start_fastapi_server()
    
    if success:
        # Test endpoints
        test_api_endpoints()
        
        print("\n" + "=" * 50)
        print("✅ WEB SERVER DEPLOYMENT COMPLETE")
        print("=" * 50)
        print("🌐 API URL: http://localhost:8080")
        print("📚 API Docs: http://localhost:8080/docs")
        print("🔍 Health Check: http://localhost:8080/health")
        print("📊 Platform Status: http://localhost:8080/status")
        print("\n🚀 Your AutoPilot Ventures API is now accessible!")
    else:
        print("\n❌ Failed to start web server")

if __name__ == "__main__":
    main() 
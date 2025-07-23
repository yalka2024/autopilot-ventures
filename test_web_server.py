"""
Test script for the AutoPilot Ventures web server
"""

import requests
import time
import subprocess
import sys
import os

def test_web_server():
    """Test the web server locally."""
    print("🧪 Testing AutoPilot Ventures Web Server")
    print("=" * 50)
    
    # Start the web server in a subprocess
    print("🚀 Starting web server...")
    try:
        # Set environment variables for testing
        env = os.environ.copy()
        env['PORT'] = '8080'
        env['OPENAI_API_KEY'] = 'test_key'
        env['SECRET_KEY'] = 'test_secret'
        env['JWT_SECRET'] = 'test_jwt_secret'
        
        # Start the server
        process = subprocess.Popen(
            [sys.executable, 'web_server.py'],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for server to start
        print("⏳ Waiting for server to start...")
        time.sleep(10)
        
        # Test endpoints
        base_url = "http://localhost:8080"
        
        print("\n📋 Testing endpoints:")
        
        # Test root endpoint
        print("  Testing / ...")
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            print("  ✅ Root endpoint working")
            print(f"  📄 Response: {response.json()}")
        else:
            print(f"  ❌ Root endpoint failed: {response.status_code}")
        
        # Test health endpoint
        print("  Testing /health ...")
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("  ✅ Health endpoint working")
            print(f"  📄 Response: {response.json()}")
        else:
            print(f"  ❌ Health endpoint failed: {response.status_code}")
        
        # Test status endpoint
        print("  Testing /status ...")
        response = requests.get(f"{base_url}/status", timeout=10)
        if response.status_code == 200:
            print("  ✅ Status endpoint working")
            print(f"  📄 Response: {response.json()}")
        else:
            print(f"  ❌ Status endpoint failed: {response.status_code}")
        
        print("\n🎉 All tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        # Stop the server
        if 'process' in locals():
            process.terminate()
            process.wait()
            print("🛑 Server stopped")

if __name__ == "__main__":
    test_web_server() 
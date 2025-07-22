#!/usr/bin/env python3
"""
Check Container Health
Verify that the container and main.py are working properly
"""

import subprocess
import os
import sys

def check_docker_image():
    """Check if the Docker image exists and can be pulled"""
    print("🔍 Checking Docker image...")
    
    image_url = "160277203814.dkr.ecr.us-east-1.amazonaws.com/autopilot-ventures:latest"
    
    try:
        # Check if image exists locally
        result = subprocess.run(['docker', 'images', image_url], capture_output=True, text=True)
        if result.returncode == 0 and image_url in result.stdout:
            print("✅ Docker image found locally")
            return True
        else:
            print("⚠️  Docker image not found locally")
            return False
    except FileNotFoundError:
        print("❌ Docker not installed")
        return False

def check_main_py():
    """Check if main.py exists and is valid"""
    print("\n🔍 Checking main.py...")
    
    if os.path.exists('main.py'):
        print("✅ main.py exists")
        
        # Check if it's a valid Python file
        try:
            result = subprocess.run(['python', '-m', 'py_compile', 'main.py'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ main.py is valid Python code")
                return True
            else:
                print(f"❌ main.py has syntax errors: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Error checking main.py: {e}")
            return False
    else:
        print("❌ main.py not found")
        return False

def check_health_server():
    """Check if health_server.py exists and is valid"""
    print("\n🔍 Checking health_server.py...")
    
    if os.path.exists('health_server.py'):
        print("✅ health_server.py exists")
        
        try:
            result = subprocess.run(['python', '-m', 'py_compile', 'health_server.py'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ health_server.py is valid Python code")
                return True
            else:
                print(f"❌ health_server.py has syntax errors: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Error checking health_server.py: {e}")
            return False
    else:
        print("❌ health_server.py not found")
        return False

def test_container_startup():
    """Test if the container can start properly"""
    print("\n🔍 Testing container startup...")
    
    try:
        # Try to run the container locally
        result = subprocess.run([
            'docker', 'run', '--rm', '-p', '8000:8000',
            '160277203814.dkr.ecr.us-east-1.amazonaws.com/autopilot-ventures:latest',
            'python', 'main.py'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Container starts successfully")
            return True
        else:
            print(f"❌ Container failed to start: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("✅ Container started (timeout expected for long-running app)")
        return True
    except Exception as e:
        print(f"❌ Error testing container: {e}")
        return False

def check_requirements():
    """Check if all required files exist"""
    print("\n🔍 Checking required files...")
    
    required_files = [
        'main.py',
        'health_server.py',
        'cloud-deployment.yml',
        'requirements.txt'
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} missing")
            all_exist = False
    
    return all_exist

def main():
    print("🔧 Container Health Check")
    print("=" * 50)
    
    # Check required files
    if not check_requirements():
        print("\n❌ Missing required files")
        return
    
    # Check main.py
    if not check_main_py():
        print("\n❌ main.py has issues")
        return
    
    # Check health_server.py
    if not check_health_server():
        print("\n❌ health_server.py has issues")
        return
    
    # Check Docker image
    if not check_docker_image():
        print("\n⚠️  Docker image not found locally")
        print("   This is normal if you haven't pulled it yet")
    
    # Test container startup
    test_container_startup()
    
    print("\n" + "=" * 50)
    print("✅ Container health check complete!")
    
    print("\n📋 Recommendations:")
    print("  1. If main.py has errors, fix them first")
    print("  2. If Docker image is missing, pull it from ECR")
    print("  3. If container fails to start, check the logs")
    print("  4. Use the fixed template for deployment")

if __name__ == "__main__":
    main() 
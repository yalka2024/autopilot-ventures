#!/usr/bin/env python3
"""
Fix All Dependency Conflicts
Comprehensive solution for AutoPilot Ventures dependencies
"""

import subprocess
import os
import shutil

def backup_original_requirements():
    """Backup the original requirements.txt"""
    if os.path.exists('requirements.txt'):
        shutil.copy('requirements.txt', 'requirements_backup.txt')
        print("✅ Backed up original requirements.txt")

def replace_requirements():
    """Replace requirements.txt with the fixed version"""
    if os.path.exists('requirements_fixed.txt'):
        shutil.copy('requirements_fixed.txt', 'requirements.txt')
        print("✅ Replaced requirements.txt with fixed version")
    else:
        print("❌ requirements_fixed.txt not found")

def build_docker_image():
    """Build the Docker image with fixed dependencies"""
    print("🔨 Building Docker image with fixed dependencies...")
    
    try:
        result = subprocess.run([
            'docker', 'build', '-t', 'autopilot-ventures:latest', '.'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Docker image built successfully!")
            return True
        else:
            print(f"❌ Docker build failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error building Docker image: {e}")
        return False

def tag_and_push_image():
    """Tag and push the image to ECR"""
    print("📤 Tagging and pushing image to ECR...")
    
    try:
        # Tag the image
        tag_result = subprocess.run([
            'docker', 'tag', 'autopilot-ventures:latest', 
            '160277203814.dkr.ecr.us-east-1.amazonaws.com/autopilot-ventures:latest'
        ], capture_output=True, text=True)
        
        if tag_result.returncode != 0:
            print(f"❌ Error tagging image: {tag_result.stderr}")
            return False
        
        # Push the image
        push_result = subprocess.run([
            'docker', 'push', '160277203814.dkr.ecr.us-east-1.amazonaws.com/autopilot-ventures:latest'
        ], capture_output=True, text=True)
        
        if push_result.returncode == 0:
            print("✅ Image pushed to ECR successfully!")
            return True
        else:
            print(f"❌ Error pushing image: {push_result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error with ECR operations: {e}")
        return False

def main():
    print("🔧 Fixing All Dependency Conflicts")
    print("=" * 50)
    
    # Step 1: Backup original
    backup_original_requirements()
    
    # Step 2: Replace with fixed requirements
    replace_requirements()
    
    # Step 3: Build Docker image
    if build_docker_image():
        print("\n✅ All dependencies fixed and Docker image built!")
        
        # Step 4: Push to ECR (optional)
        response = input("\nDo you want to push the image to ECR? (y/n): ")
        if response.lower() == 'y':
            tag_and_push_image()
    else:
        print("\n❌ Failed to build Docker image")
        print("📋 You can restore the original requirements with:")
        print("   copy requirements_backup.txt requirements.txt")

if __name__ == "__main__":
    main() 
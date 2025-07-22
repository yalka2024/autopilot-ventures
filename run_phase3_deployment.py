#!/usr/bin/env python3
"""
Phase 3 Deployment Runner
Simple script to deploy the new Phase 3 stack.
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n🚀 {description}")
    print(f"Command: {command}")
    print("-" * 50)
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("✅ Success!")
        if result.stdout:
            print("Output:")
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed!")
        print(f"Error: {e}")
        if e.stdout:
            print("Stdout:")
            print(e.stdout)
        if e.stderr:
            print("Stderr:")
            print(e.stderr)
        return False

def main():
    """Main deployment function."""
    print("🎯 AutoPilot Ventures Phase 3 Deployment")
    print("=" * 60)
    
    # Check if AWS CLI is available
    if not run_command("aws --version", "Checking AWS CLI"):
        print("❌ AWS CLI not found. Please install it first.")
        return 1
    
    # Check if template file exists
    if not os.path.exists('cloud-deployment.yml'):
        print("❌ cloud-deployment.yml not found!")
        return 1
    
    # Check current stack status
    print("\n📋 Checking current stack status...")
    run_command("python check_stacks.py", "Checking existing stacks")
    
    # Deploy Phase 3 stack
    print("\n🎯 Deploying Phase 3 Stack...")
    if run_command("python deploy_phase3.py", "Deploying Phase 3 stack"):
        print("\n🎉 Phase 3 deployment completed successfully!")
        
        # Verify deployment
        print("\n🔍 Verifying deployment...")
        run_command("python deploy_phase3.py --verify-only", "Verifying Phase 3 deployment")
        
        print("\n✅ Phase 3 Advanced Intelligence Platform is now running!")
        print("\n🚀 Features Available:")
        print("  • Vector Memory Management")
        print("  • Self-Tuning Agents")
        print("  • Reinforcement Learning Engine")
        print("  • Autonomous Workflow Engine")
        print("  • MLflow Experiment Tracking")
        print("  • Dynamic Decision Trees")
        print("  • Cross-Venture Learning")
        print("  • Predictive Analytics")
        
        return 0
    else:
        print("\n❌ Phase 3 deployment failed!")
        return 1

if __name__ == "__main__":
    exit(main()) 
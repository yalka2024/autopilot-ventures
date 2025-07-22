#!/usr/bin/env python3
"""
Startup script for AutoPilot Ventures
Runs both the main application and health server
"""

import asyncio
import subprocess
import sys
import os
import signal
import time
from concurrent.futures import ThreadPoolExecutor

def start_health_server():
    """Start the health server in a separate process."""
    try:
        print("🚀 Starting health server...")
        subprocess.run([sys.executable, "health_server.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Health server failed: {e}")
    except KeyboardInterrupt:
        print("🛑 Health server stopped")

def start_main_app():
    """Start the main AutoPilot Ventures application."""
    try:
        print("🚀 Starting main AutoPilot Ventures application...")
        subprocess.run([sys.executable, "main.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Main app failed: {e}")
    except KeyboardInterrupt:
        print("🛑 Main app stopped")

def main():
    """Start both applications."""
    print("🎯 AutoPilot Ventures Platform - Starting...")
    
    # Check if we should run in autonomous mode
    autonomous_mode = os.getenv('AUTONOMY_LEVEL', 'semi')
    
    if autonomous_mode in ['semi', 'full']:
        print(f"🤖 Starting in autonomous mode: {autonomous_mode}")
        # Run main app with autonomous mode
        cmd = [sys.executable, "main.py", "--start-autonomous", f"--autonomous-mode={autonomous_mode}"]
    else:
        print("🔧 Starting in manual mode")
        # Run main app normally
        cmd = [sys.executable, "main.py"]
    
    try:
        # Start health server in background
        with ThreadPoolExecutor(max_workers=1) as executor:
            health_future = executor.submit(start_health_server)
            
            # Give health server time to start
            time.sleep(2)
            
            # Start main application
            subprocess.run(cmd, check=True)
            
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
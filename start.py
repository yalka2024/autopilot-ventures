#!/usr/bin/env python3
"""
AutoPilot Ventures - Quick Start Script
Simple script to launch the platform with default settings
"""

import os
import sys
import subprocess
from pathlib import Path

def check_prerequisites():
    """Check if prerequisites are met"""
    print("🔍 Checking prerequisites...")
    
    # Check Python version
    if sys.version_info < (3, 11):
        print("❌ Python 3.11+ is required")
        return False
    
    # Check if requirements are installed
    try:
        import langchain
        import streamlit
        import sqlalchemy
        print("✅ Dependencies installed")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False
    
    # Check if .env file exists
    if not Path(".env").exists():
        print("⚠️  No .env file found")
        print("Creating .env from template...")
        if Path("env.example").exists():
            import shutil
            shutil.copy("env.example", ".env")
            print("✅ Created .env file from template")
            print("⚠️  Please edit .env with your API keys before starting")
            return False
        else:
            print("❌ No env.example file found")
            return False
    
    # Check OpenAI API key
    from dotenv import load_dotenv
    load_dotenv()
    
    if not os.getenv("OPENAI_SECRET_KEY"):
        print("❌ OPENAI_SECRET_KEY not found in .env file")
        print("Please add your OpenAI API key to the .env file")
        return False
    
    print("✅ All prerequisites met")
    return True

def create_directories():
    """Create necessary directories"""
    directories = [
        "data",
        "logs", 
        "startups",
        "templates",
        "uploads",
        "exports",
        "backups"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print("✅ Created necessary directories")

def start_platform():
    """Start the AutoPilot Ventures platform"""
    print("🚀 Starting AutoPilot Ventures...")
    
    # Default goals
    goals = ["productivity", "wellness", "technology"]
    
    # Start the platform
    try:
        from main import main
        sys.argv = ["main.py", "start", "--goals"] + goals
        main()
    except KeyboardInterrupt:
        print("\n⏹️  Platform stopped by user")
    except Exception as e:
        print(f"❌ Error starting platform: {e}")
        return False
    
    return True

def launch_dashboard():
    """Launch the web dashboard"""
    print("📊 Launching web dashboard...")
    
    try:
        # Start Streamlit dashboard
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "dashboard.py",
            "--server.port", "8501",
            "--server.headless", "true"
        ])
    except KeyboardInterrupt:
        print("\n⏹️  Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error launching dashboard: {e}")

def main():
    """Main startup function"""
    print("=" * 60)
    print("🚀 AutoPilot Ventures - Quick Start")
    print("=" * 60)
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Please fix the issues above.")
        return
    
    # Create directories
    create_directories()
    
    # Ask user what to do
    print("\nWhat would you like to do?")
    print("1. Start the platform (CLI mode)")
    print("2. Launch web dashboard only")
    print("3. Start platform and dashboard")
    print("4. Run tests")
    print("5. Exit")
    
    choice = input("\nEnter your choice (1-5): ").strip()
    
    if choice == "1":
        start_platform()
    elif choice == "2":
        launch_dashboard()
    elif choice == "3":
        print("Starting platform and dashboard...")
        # In a real implementation, you'd run both concurrently
        start_platform()
    elif choice == "4":
        print("Running tests...")
        subprocess.run([sys.executable, "main.py", "test", "--full"])
    elif choice == "5":
        print("Goodbye!")
    else:
        print("Invalid choice. Exiting.")

if __name__ == "__main__":
    main() 
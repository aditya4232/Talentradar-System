#!/usr/bin/env python3
"""
Setup script for TalentRadar
Installs dependencies and initializes the system
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"📦 {description}")
    print(f"{'='*60}")
    
    try:
        subprocess.check_call(command, shell=True)
        print(f"✅ {description} - SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        print(f"Error: {e}")
        return False

def main():
    print("""
    ╔════════════════════════════════════════════╗
    ║   🎯 TalentRadar Setup                     ║
    ║   AI-Powered Recruitment System            ║
    ╚════════════════════════════════════════════╝
    """)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        sys.exit(1)
    
    print(f"✅ Python version: {sys.version}")
    
    # Navigate to backend directory
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    os.chdir(backend_dir)
    
    # Install dependencies
    if not run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing Python dependencies"
    ):
        print("\n⚠️  Some dependencies failed to install. Please check the errors above.")
        return
    
    # Create .env file if it doesn't exist
    if not os.path.exists('.env'):
        print("\n📝 Creating .env file...")
        try:
            with open('.env.example', 'r') as src:
                with open('.env', 'w') as dst:
                    dst.write(src.read())
            print("✅ .env file created (you can add API keys later)")
        except Exception as e:
            print(f"⚠️  Could not create .env file: {e}")
    
    print(f"""
    
    ╔════════════════════════════════════════════╗
    ║   ✅ Setup Complete!                       ║
    ╚════════════════════════════════════════════╝
    
    🚀 Quick Start:
    
    1. Start the backend:
       cd backend
       python main.py
    
    2. Open frontend/index.html in your browser
       or run:
       cd frontend
       python -m http.server 3000
    
    3. Start searching for candidates!
    
    📚 Documentation: README.md
    🔧 API Docs: http://localhost:8000/docs
    
    💡 Optional: Add API keys to backend/.env for:
       - Serper API (Google search)
       - GitHub Token (better rate limits)
    
    Note: System works with mock data without API keys!
    """)

if __name__ == "__main__":
    main()

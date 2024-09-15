"""
Streamlit Cloud Deployment Script for Job Application Tracker

This script helps prepare the application for deployment to Streamlit Cloud
"""

import os
import subprocess
import shutil

def check_files():
    """Check if all required files are present"""
    required_files = [
        'app.py',
        'database.py', 
        'job_utils.py',
        'requirements.txt',
        'README.md',
        '.streamlit/config.toml'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    else:
        print("✅ All required files present!")
        return True

def test_local():
    """Test the application locally"""
    print("🧪 Testing application locally...")
    
    try:
        # Test imports
        import streamlit as st
        import pandas as pd
        import plotly.express as px
        from database import JobApplicationDB
        from job_utils import JobInfoScraper, AutoFillGenerator
        
        print("✅ All imports working correctly!")
        
        # Test database initialization
        db = JobApplicationDB()
        stats = db.get_application_stats()
        print(f"✅ Database working! Found {stats['total_applications']} applications")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing application: {e}")
        return False

def create_gitignore():
    """Create .gitignore file for the repository"""
    gitignore_content = """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv
.env

# Streamlit
*.db
*.sqlite
*.sqlite3

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Temp files
temp/
tmp/
*.tmp

# Excel exports
job_applications_*.xlsx
"""
    
    with open('.gitignore', 'w') as f:
        f.write(gitignore_content.strip())
    
    print("✅ Created .gitignore file")

def deployment_checklist():
    """Show deployment checklist"""
    print("\n" + "="*50)
    print("🚀 STREAMLIT CLOUD DEPLOYMENT CHECKLIST")
    print("="*50)
    
    checklist = [
        "✅ All code files are ready",
        "📱 Test the app locally first",
        "🔧 Create a GitHub repository",
        "📤 Push your code to GitHub",
        "🌐 Go to share.streamlit.io",
        "🔐 Sign in with GitHub account",
        "➕ Click 'New app'",
        "📂 Select your repository",
        "📄 Set main file: app.py",
        "🎯 Click Deploy!",
        "⏱️ Wait for deployment (2-5 minutes)",
        "🎉 Get your public URL!"
    ]
    
    for item in checklist:
        print(f"  {item}")
    
    print("\n💡 Pro Tips:")
    print("  - Make sure your repo is public")
    print("  - Include all files in the repository")
    print("  - Test locally before deploying")
    print("  - Use the public URL in your portfolio")

def main():
    """Main deployment preparation function"""
    print("🎯 Job Application Tracker - Deployment Preparation")
    print("="*50)
    
    # Check files
    if not check_files():
        return
    
    # Test locally
    if not test_local():
        print("❌ Please fix errors before deploying")
        return
    
    # Create .gitignore
    create_gitignore()
    
    # Show deployment checklist
    deployment_checklist()
    
    print(f"\n✅ Ready for deployment!")
    print(f"📁 Current directory: {os.getcwd()}")
    print(f"🌟 Your Job Application Tracker is ready to be deployed!")

if __name__ == "__main__":
    main()

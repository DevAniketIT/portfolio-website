#!/usr/bin/env python3
"""
AI Automation Portfolio - Quick Launch Script
Helps users get started with the AI automation tools
"""

import os
import sys
import subprocess
from pathlib import Path

def print_banner():
    print("""
🤖 ============================================ 🤖
    AI AUTOMATION PORTFOLIO - QUICK LAUNCH
🤖 ============================================ 🤖

Week 3: AI Integration + Automation Portfolio
Built for Fiverr services (₹2,000-5,000 per project)
""")

def check_python():
    """Check Python installation"""
    print("✅ Checking Python installation...")
    python_version = sys.version_info
    if python_version.major >= 3 and python_version.minor >= 8:
        print(f"✅ Python {python_version.major}.{python_version.minor} detected - Compatible!")
        return True
    else:
        print(f"❌ Python {python_version.major}.{python_version.minor} detected - Need Python 3.8+")
        return False

def check_requirements():
    """Check if requirements are installed"""
    print("\n📦 Checking required packages...")
    required_packages = [
        'streamlit', 'openai', 'python-dotenv', 'pandas', 
        'python-docx', 'PyPDF2', 'email-validator'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - Missing")
            missing_packages.append(package)
    
    return missing_packages

def install_requirements():
    """Install missing requirements"""
    print("\n📥 Installing requirements...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ All packages installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install packages. Please run manually:")
        print("pip install -r requirements.txt")
        return False

def check_env_file():
    """Check for environment file"""
    print("\n🔧 Checking environment configuration...")
    
    env_file = Path('.env')
    env_template = Path('.env.template')
    
    if env_file.exists():
        print("✅ .env file found")
        return True
    elif env_template.exists():
        print("⚠️  .env file not found, but .env.template exists")
        print("📝 Please copy .env.template to .env and add your OpenAI API key")
        return False
    else:
        print("❌ No environment configuration found")
        return False

def get_openai_key():
    """Get OpenAI API key from user"""
    print("\n🔑 OpenAI API Key Setup:")
    print("You need an OpenAI API key to use these applications.")
    print("Get one at: https://platform.openai.com/api-keys")
    print("$20 credit is enough for 100+ projects!\n")
    
    api_key = input("Enter your OpenAI API key (or press Enter to skip): ").strip()
    
    if api_key:
        # Save to .env file
        with open('.env', 'w') as f:
            f.write(f"OPENAI_API_KEY={api_key}\n")
        print("✅ API key saved to .env file")
        return True
    else:
        print("⚠️  Skipped API key setup. Add it later to .env file or in the app sidebar.")
        return False

def show_applications():
    """Display available applications"""
    print("""
🚀 Available Applications:

1. 📄 Resume Optimizer (resume-optimizer/app.py)
   • AI-powered ATS-compatible resume analysis
   • Keyword extraction and optimization
   • Fiverr pricing: ₹2,000-5,000

2. 💼 LinkedIn Post Generator (linkedin-generator/app.py)
   • Professional content creation with bulk processing
   • Multiple post types and optimization
   • Fiverr pricing: ₹2,000-8,000

3. 📧 Email Responder (email-responder/app.py)
   • Automated professional email responses
   • Customer service templates
   • Fiverr pricing: ₹2,500-8,000
""")

def launch_application():
    """Launch selected application"""
    print("\nWhich application would you like to launch?")
    print("1. Resume Optimizer")
    print("2. LinkedIn Post Generator") 
    print("3. Email Responder")
    print("4. All applications info")
    print("5. Exit")
    
    choice = input("\nEnter your choice (1-5): ").strip()
    
    apps = {
        '1': ('resume-optimizer/app.py', 'Resume Optimizer'),
        '2': ('linkedin-generator/app.py', 'LinkedIn Post Generator'),
        '3': ('email-responder/app.py', 'Email Responder')
    }
    
    if choice in apps:
        app_path, app_name = apps[choice]
        print(f"\n🚀 Launching {app_name}...")
        print(f"Command: streamlit run {app_path}")
        print("\n📝 Note: The app will open in your browser automatically.")
        print("🔧 Add your OpenAI API key in the sidebar to activate AI features.")
        print("❌ Press Ctrl+C to stop the application.\n")
        
        try:
            subprocess.run(['streamlit', 'run', app_path])
        except KeyboardInterrupt:
            print("\n👋 Application stopped. Thanks for using AI Automation Portfolio!")
        except FileNotFoundError:
            print("❌ Streamlit not found. Please install requirements first.")
    
    elif choice == '4':
        show_business_info()
    elif choice == '5':
        print("👋 Goodbye! Good luck with your AI automation business!")
    else:
        print("❌ Invalid choice. Please try again.")
        launch_application()

def show_business_info():
    """Show business and revenue information"""
    print("""
💰 FIVERR BUSINESS OPPORTUNITY:

📊 Revenue Potential (Conservative):
   • Resume Services: 10 projects × ₹3,000 = ₹30,000/month
   • LinkedIn Content: 8 packages × ₹4,000 = ₹32,000/month
   • Email Automation: 5 setups × ₹4,000 = ₹20,000/month
   • TOTAL: ₹82,000/month (part-time)

🎯 Target Customers:
   • Small business owners needing professional communication
   • Job seekers wanting optimized resumes
   • Marketing professionals requiring content
   • HR departments seeking efficiency

📈 Growth Strategy:
   1. Launch 3 core gigs on Fiverr
   2. Build reviews with quality service delivery
   3. Add premium packages and upsells
   4. Scale to ₹100,000+/month within 6 months

📚 Resources:
   • README.md - Complete project overview
   • BUSINESS_GUIDE.md - Detailed Fiverr strategy
   • PROJECT_SUMMARY.md - Technical specifications

🚀 Next Steps:
   1. Test all applications locally
   2. Create Fiverr seller account
   3. Launch your first gig
   4. Start your AI automation empire!
""")
    
    input("\nPress Enter to continue...")
    launch_application()

def main():
    """Main application launcher"""
    print_banner()
    
    # Check Python version
    if not check_python():
        print("Please upgrade to Python 3.8+ and try again.")
        return
    
    # Check requirements
    missing = check_requirements()
    if missing:
        print(f"\n📥 Missing packages: {', '.join(missing)}")
        install_choice = input("Install missing packages? (y/n): ").lower().strip()
        if install_choice == 'y':
            if not install_requirements():
                return
        else:
            print("❌ Cannot continue without required packages.")
            return
    
    # Check environment file
    check_env_file()
    
    # Setup API key if needed
    if not os.getenv('OPENAI_API_KEY'):
        get_openai_key()
    
    # Show applications
    show_applications()
    
    # Launch application
    launch_application()

if __name__ == "__main__":
    main()

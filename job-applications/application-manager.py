#!/usr/bin/env python3
"""
Job Application Manager
Automates the job application process and tracks applications
"""

import json
import os
import datetime
import webbrowser
from typing import Dict, List, Optional
import requests

class JobApplicationManager:
    def __init__(self, data_file: str = "applications.json"):
        self.data_file = data_file
        self.applications = self.load_applications()
        
        # Your portfolio links
        self.portfolio_links = {
            "live_app": "https://aniket-job-tracker.streamlit.app",
            "api_docs": "https://job-tracker-api-aniket.onrender.com/docs",
            "github": "https://github.com/aniketkumar7/aniket-portfolio",
            "price_monitor": "https://github.com/aniketkumar7/aniket-portfolio/tree/main/price-monitor",
            "web_scraper": "https://github.com/aniketkumar7/aniket-portfolio/tree/main/ai-automation/freelancing-toolkit/web-scraping"
        }
        
    def load_applications(self) -> List[Dict]:
        """Load applications from JSON file"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                return json.load(f)
        return []
    
    def save_applications(self):
        """Save applications to JSON file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.applications, f, indent=2, default=str)
    
    def add_application(self, company: str, position: str, application_url: str = "", 
                       contact_person: str = "", notes: str = "", application_type: str = "job"):
        """Add a new job application"""
        application = {
            "id": len(self.applications) + 1,
            "company": company,
            "position": position,
            "application_type": application_type,  # "job" or "freelance"
            "application_date": datetime.datetime.now().isoformat(),
            "status": "Applied",
            "application_url": application_url,
            "contact_person": contact_person,
            "notes": notes,
            "follow_up_date": (datetime.datetime.now() + datetime.timedelta(days=7)).isoformat(),
            "portfolio_links_sent": list(self.portfolio_links.keys())
        }
        
        self.applications.append(application)
        self.save_applications()
        print(f"✅ Added application for {company} - {position}")
        return application
    
    def update_status(self, application_id: int, status: str, notes: str = ""):
        """Update application status"""
        for app in self.applications:
            if app["id"] == application_id:
                app["status"] = status
                app["last_updated"] = datetime.datetime.now().isoformat()
                if notes:
                    app["notes"] += f"\n[{datetime.datetime.now().strftime('%Y-%m-%d')}] {notes}"
                self.save_applications()
                print(f"✅ Updated {app['company']} status to: {status}")
                return
        print(f"❌ Application with ID {application_id} not found")
    
    def get_follow_ups_due(self) -> List[Dict]:
        """Get applications that need follow-up"""
        today = datetime.datetime.now()
        due_follow_ups = []
        
        for app in self.applications:
            if app["status"] in ["Applied", "Interview Scheduled"]:
                follow_up_date = datetime.datetime.fromisoformat(app["follow_up_date"])
                if follow_up_date <= today:
                    due_follow_ups.append(app)
        
        return due_follow_ups
    
    def generate_application_email(self, company: str, position: str = "Full-Stack Python Developer", 
                                  why_company: str = "") -> str:
        """Generate personalized application email"""
        
        template = f"""Subject: {position} - Aniket Kumar - Live Portfolio Included

Hi {company} Team,

I'm a Full-Stack Python Developer with production experience in API development and web applications, and I'm excited about the opportunity to contribute to {company}.

## Recent Project: Built and deployed a comprehensive job tracking system:
• Live App: {self.portfolio_links['live_app']}
• API Docs: {self.portfolio_links['api_docs']}  
• GitHub: {self.portfolio_links['github']}

## The system features:
- FastAPI backend with 15+ endpoints
- PostgreSQL database with migrations
- Streamlit frontend with analytics dashboard
- Automated email notifications
- Production deployment on Render & Streamlit Cloud
- Real-time job application tracking
- RESTful API with full CRUD operations

## Additional Projects:
- Price Monitor System: Automated web scraping with email alerts
- AI Automation Toolkit: Freelancing automation tools
- Universal Web Scraper: E-commerce data extraction system

## Why {company}:
{why_company if why_company else f"I'm particularly drawn to {company}'s innovative approach and would love to discuss how my experience building scalable Python applications can contribute to your team's success."}

Portfolio Links:
- Live Demo: {self.portfolio_links['live_app']}
- API Documentation: {self.portfolio_links['api_docs']}
- Full Portfolio: {self.portfolio_links['github']}

Best regards,
Aniket Kumar
Email: [your-email]
LinkedIn: [your-linkedin]
Portfolio: [your-portfolio-website]"""

        return template
    
    def generate_freelance_proposal(self, client_name: str, project_type: str = "web_scraping", 
                                   project_details: str = "") -> str:
        """Generate freelance proposal"""
        
        if project_type == "web_scraping":
            template = f"""Subject: Python Web Scraping Expert - Fast Delivery & Live Demo

Hi {client_name},

I'm a Python developer specializing in web scraping and automation with a proven track record of delivering high-quality solutions.

## Recent Project - Price Monitor System:
I've built and deployed a comprehensive price monitoring system that demonstrates my expertise:
• Live System: Tracks product prices across multiple e-commerce sites
• Features: Email alerts, price history, automated data collection
• Tech Stack: Python, BeautifulSoup, Selenium, PostgreSQL, FastAPI
• GitHub: {self.portfolio_links['price_monitor']}

{project_details}

## Portfolio Links:
- Universal Scraper: {self.portfolio_links['web_scraper']}
- API Documentation: {self.portfolio_links['api_docs']}
- Live Demo: {self.portfolio_links['live_app']}

Timeline: 3-5 days for completion
Rate: $25-35/hour

Ready to start immediately. Let's discuss your specific requirements!

Best regards,
Aniket Kumar"""

        return template
    
    def show_statistics(self):
        """Show application statistics"""
        if not self.applications:
            print("No applications tracked yet.")
            return
            
        total = len(self.applications)
        statuses = {}
        types = {"job": 0, "freelance": 0}
        
        for app in self.applications:
            status = app["status"]
            app_type = app.get("application_type", "job")
            
            statuses[status] = statuses.get(status, 0) + 1
            types[app_type] += 1
        
        print("\n📊 APPLICATION STATISTICS")
        print("=" * 30)
        print(f"Total Applications: {total}")
        print(f"Job Applications: {types['job']}")
        print(f"Freelance Proposals: {types['freelance']}")
        print("\nStatus Breakdown:")
        for status, count in statuses.items():
            print(f"  {status}: {count}")
        
        # Follow-ups due
        follow_ups = self.get_follow_ups_due()
        if follow_ups:
            print(f"\n⚠️  {len(follow_ups)} applications need follow-up!")
    
    def list_applications(self, status_filter: Optional[str] = None):
        """List all applications"""
        apps_to_show = self.applications
        
        if status_filter:
            apps_to_show = [app for app in self.applications if app["status"] == status_filter]
        
        if not apps_to_show:
            print("No applications found.")
            return
            
        print(f"\n📋 APPLICATIONS ({len(apps_to_show)})")
        print("=" * 50)
        
        for app in apps_to_show:
            print(f"ID: {app['id']} | {app['company']} - {app['position']}")
            print(f"   Status: {app['status']} | Applied: {app['application_date'][:10]}")
            if app.get('notes'):
                print(f"   Notes: {app['notes']}")
            print()
    
    def open_portfolio_links(self):
        """Open portfolio links in browser"""
        print("🌐 Opening portfolio links...")
        webbrowser.open(self.portfolio_links["live_app"])
        webbrowser.open(self.portfolio_links["api_docs"])
        webbrowser.open(self.portfolio_links["github"])


def main():
    """Main CLI interface"""
    manager = JobApplicationManager()
    
    while True:
        print("\n🎯 JOB APPLICATION MANAGER")
        print("=" * 30)
        print("1. Add job application")
        print("2. Add freelance proposal")
        print("3. Update application status")
        print("4. Generate application email")
        print("5. Generate freelance proposal")
        print("6. View statistics")
        print("7. List applications")
        print("8. Check follow-ups due")
        print("9. Open portfolio links")
        print("0. Exit")
        
        choice = input("\nEnter your choice: ").strip()
        
        if choice == "1":
            company = input("Company name: ").strip()
            position = input("Position (default: Full-Stack Python Developer): ").strip()
            if not position:
                position = "Full-Stack Python Developer"
            url = input("Application URL (optional): ").strip()
            contact = input("Contact person (optional): ").strip()
            notes = input("Notes (optional): ").strip()
            
            manager.add_application(company, position, url, contact, notes, "job")
            
        elif choice == "2":
            company = input("Client/Company name: ").strip()
            project = input("Project title: ").strip()
            url = input("Project URL (optional): ").strip()
            notes = input("Project details: ").strip()
            
            manager.add_application(company, project, url, "", notes, "freelance")
            
        elif choice == "3":
            manager.list_applications()
            try:
                app_id = int(input("Enter application ID to update: "))
                status = input("New status: ").strip()
                notes = input("Additional notes (optional): ").strip()
                manager.update_status(app_id, status, notes)
            except ValueError:
                print("Invalid ID")
                
        elif choice == "4":
            company = input("Company name: ").strip()
            position = input("Position (optional): ").strip()
            why_company = input("Why this company? (optional): ").strip()
            
            email = manager.generate_application_email(company, position, why_company)
            print("\n" + "="*50)
            print(email)
            print("="*50)
            
        elif choice == "5":
            client = input("Client name: ").strip()
            project_type = input("Project type (web_scraping/api/automation): ").strip()
            details = input("Project details: ").strip()
            
            proposal = manager.generate_freelance_proposal(client, project_type, details)
            print("\n" + "="*50)
            print(proposal)
            print("="*50)
            
        elif choice == "6":
            manager.show_statistics()
            
        elif choice == "7":
            status_filter = input("Filter by status (optional): ").strip()
            if not status_filter:
                status_filter = None
            manager.list_applications(status_filter)
            
        elif choice == "8":
            follow_ups = manager.get_follow_ups_due()
            if follow_ups:
                print(f"\n⚠️  {len(follow_ups)} FOLLOW-UPS DUE:")
                print("=" * 30)
                for app in follow_ups:
                    print(f"• {app['company']} - {app['position']}")
                    print(f"  Applied: {app['application_date'][:10]}")
                    print(f"  Follow-up due: {app['follow_up_date'][:10]}")
                    print()
            else:
                print("✅ No follow-ups due!")
                
        elif choice == "9":
            manager.open_portfolio_links()
            
        elif choice == "0":
            break
        else:
            print("Invalid choice!")

if __name__ == "__main__":
    main()

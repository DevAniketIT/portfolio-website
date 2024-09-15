"""
Demo data script for Job Application Tracker
Run this to populate the database with sample data for testing
"""

from database import JobApplicationDB
from datetime import date, timedelta
import random

def add_demo_data():
    db = JobApplicationDB()
    
    # Sample companies and positions
    sample_data = [
        {
            'company_name': 'Google',
            'job_title': 'Software Engineer',
            'job_url': 'https://careers.google.com/jobs/results/123456789/',
            'application_date': (date.today() - timedelta(days=30)).strftime('%Y-%m-%d'),
            'status': 'Interview Scheduled',
            'salary_range': '$120,000 - $180,000',
            'location': 'Mountain View, CA',
            'job_description': 'Join our team to build scalable systems that serve billions of users worldwide. You will work on cutting-edge technologies and collaborate with world-class engineers.',
            'contact_person': 'Sarah Johnson',
            'contact_email': 'sarah.johnson@google.com',
            'notes': 'Applied through referral from John. Strong fit for the role.',
            'follow_up_date': (date.today() + timedelta(days=3)).strftime('%Y-%m-%d'),
            'source': 'Referral'
        },
        {
            'company_name': 'Microsoft',
            'job_title': 'Python Developer',
            'job_url': 'https://careers.microsoft.com/us/en/job/1234567',
            'application_date': (date.today() - timedelta(days=25)).strftime('%Y-%m-%d'),
            'status': 'Applied',
            'salary_range': '$110,000 - $160,000',
            'location': 'Seattle, WA',
            'job_description': 'Work on Azure services using Python. Build robust, scalable applications that power Microsoft\'s cloud infrastructure.',
            'contact_person': 'Mike Chen',
            'contact_email': 'mike.chen@microsoft.com',
            'notes': 'Found through LinkedIn. Great company culture.',
            'follow_up_date': (date.today() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'source': 'LinkedIn'
        },
        {
            'company_name': 'Amazon',
            'job_title': 'Data Analyst',
            'job_url': 'https://amazon.jobs/en/jobs/1234567',
            'application_date': (date.today() - timedelta(days=20)).strftime('%Y-%m-%d'),
            'status': 'Rejected',
            'salary_range': '$90,000 - $130,000',
            'location': 'Austin, TX',
            'job_description': 'Analyze large datasets to drive business decisions. Work with cross-functional teams to identify trends and opportunities.',
            'contact_person': '',
            'contact_email': '',
            'notes': 'Quick rejection - might have been automated screening.',
            'follow_up_date': '',
            'source': 'Company Website',
            'rejection_reason': 'Not enough SQL experience'
        },
        {
            'company_name': 'Meta',
            'job_title': 'Full Stack Developer',
            'job_url': 'https://www.metacareers.com/jobs/1234567890123456/',
            'application_date': (date.today() - timedelta(days=15)).strftime('%Y-%m-%d'),
            'status': 'Interview Completed',
            'salary_range': '$130,000 - $200,000',
            'location': 'Menlo Park, CA',
            'job_description': 'Build features for Facebook and Instagram using React, Python, and GraphQL. Impact billions of users worldwide.',
            'contact_person': 'Jessica Liu',
            'contact_email': 'jessica.liu@meta.com',
            'notes': 'Great interview! Waiting to hear back about next steps.',
            'follow_up_date': (date.today() + timedelta(days=5)).strftime('%Y-%m-%d'),
            'source': 'LinkedIn'
        },
        {
            'company_name': 'Netflix',
            'job_title': 'Backend Engineer',
            'job_url': 'https://jobs.netflix.com/jobs/1234567',
            'application_date': (date.today() - timedelta(days=12)).strftime('%Y-%m-%d'),
            'status': 'Applied',
            'salary_range': '$140,000 - $220,000',
            'location': 'Los Gatos, CA',
            'job_description': 'Work on microservices that power Netflix streaming platform. Ensure high availability and scalability.',
            'contact_person': '',
            'contact_email': '',
            'notes': 'Dream job! Really hoping to hear back.',
            'follow_up_date': (date.today() + timedelta(days=2)).strftime('%Y-%m-%d'),
            'source': 'Indeed'
        },
        {
            'company_name': 'Spotify',
            'job_title': 'Machine Learning Engineer',
            'job_url': 'https://www.lifeatspotify.com/jobs/1234567',
            'application_date': (date.today() - timedelta(days=8)).strftime('%Y-%m-%d'),
            'status': 'Rejected',
            'salary_range': '$125,000 - $175,000',
            'location': 'New York, NY',
            'job_description': 'Build recommendation systems and ML models to enhance user experience on Spotify platform.',
            'contact_person': 'Alex Rodriguez',
            'contact_email': 'alex.rodriguez@spotify.com',
            'notes': 'They wanted more ML experience than I have.',
            'follow_up_date': '',
            'source': 'Company Website',
            'rejection_reason': 'Insufficient machine learning experience'
        },
        {
            'company_name': 'Airbnb',
            'job_title': 'Product Analyst',
            'job_url': 'https://careers.airbnb.com/positions/1234567',
            'application_date': (date.today() - timedelta(days=5)).strftime('%Y-%m-%d'),
            'status': 'Applied',
            'salary_range': '$100,000 - $150,000',
            'location': 'San Francisco, CA',
            'job_description': 'Drive product decisions through data analysis. Work closely with product managers to optimize user experience.',
            'contact_person': 'Emma Davis',
            'contact_email': 'emma.davis@airbnb.com',
            'notes': 'Love their mission and culture. Applied after attending their tech talk.',
            'follow_up_date': (date.today() + timedelta(days=7)).strftime('%Y-%m-%d'),
            'source': 'Recruiter'
        },
        {
            'company_name': 'Tesla',
            'job_title': 'Software Engineer - Autopilot',
            'job_url': 'https://www.tesla.com/careers/job/1234567',
            'application_date': (date.today() - timedelta(days=3)).strftime('%Y-%m-%d'),
            'status': 'Applied',
            'salary_range': '$120,000 - $180,000',
            'location': 'Palo Alto, CA',
            'job_description': 'Develop software for Tesla\'s autonomous driving features. Work on computer vision and neural networks.',
            'contact_person': '',
            'contact_email': '',
            'notes': 'Cutting-edge technology. Would be amazing to work on self-driving cars.',
            'follow_up_date': (date.today() + timedelta(days=10)).strftime('%Y-%m-%d'),
            'source': 'LinkedIn'
        }
    ]
    
    # Add sample applications
    print("Adding sample applications...")
    for app_data in sample_data:
        app_id = db.add_application(app_data)
        print(f"Added application {app_id}: {app_data['company_name']} - {app_data['job_title']}")
    
    # Add some follow-ups
    print("\nAdding follow-up reminders...")
    follow_ups = [
        {
            'application_id': 1,
            'follow_up_date': (date.today() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'follow_up_type': 'Email',
            'notes': 'Follow up on interview next steps'
        },
        {
            'application_id': 2,
            'follow_up_date': (date.today()).strftime('%Y-%m-%d'),
            'follow_up_type': 'LinkedIn Message',
            'notes': 'Connect with hiring manager'
        },
        {
            'application_id': 4,
            'follow_up_date': (date.today() + timedelta(days=2)).strftime('%Y-%m-%d'),
            'follow_up_type': 'Email',
            'notes': 'Thank you note for interview'
        }
    ]
    
    for follow_up in follow_ups:
        db.add_followup(
            follow_up['application_id'],
            follow_up['follow_up_date'],
            follow_up['follow_up_type'],
            follow_up['notes']
        )
        print(f"Added follow-up for application {follow_up['application_id']}")
    
    print(f"\n✅ Demo data successfully added!")
    print(f"📊 Total applications: {len(sample_data)}")
    print(f"📅 Follow-ups created: {len(follow_ups)}")
    print(f"\n🚀 Run 'streamlit run app.py' to see your data!")

if __name__ == "__main__":
    add_demo_data()

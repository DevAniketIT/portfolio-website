import sqlite3
import pandas as pd
from datetime import datetime, date
import os

class JobApplicationDB:
    def __init__(self, db_path="job_applications.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create main applications table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT NOT NULL,
                job_title TEXT NOT NULL,
                job_url TEXT,
                application_date DATE NOT NULL,
                status TEXT NOT NULL DEFAULT 'Applied',
                salary_range TEXT,
                location TEXT,
                job_description TEXT,
                contact_person TEXT,
                contact_email TEXT,
                notes TEXT,
                follow_up_date DATE,
                rejection_reason TEXT,
                source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create follow-ups table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS followups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                application_id INTEGER,
                follow_up_date DATE NOT NULL,
                follow_up_type TEXT NOT NULL,
                notes TEXT,
                completed BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (application_id) REFERENCES applications (id)
            )
        ''')
        
        # Create interview stages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                application_id INTEGER,
                interview_date DATETIME,
                interview_type TEXT,
                interviewer_name TEXT,
                interview_notes TEXT,
                result TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (application_id) REFERENCES applications (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_application(self, application_data):
        """Add a new job application"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO applications 
            (company_name, job_title, job_url, application_date, status, salary_range, 
             location, job_description, contact_person, contact_email, notes, 
             follow_up_date, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            application_data['company_name'],
            application_data['job_title'],
            application_data['job_url'],
            application_data['application_date'],
            application_data['status'],
            application_data['salary_range'],
            application_data['location'],
            application_data['job_description'],
            application_data['contact_person'],
            application_data['contact_email'],
            application_data['notes'],
            application_data['follow_up_date'],
            application_data['source']
        ))
        
        application_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return application_id
    
    def get_all_applications(self):
        """Retrieve all applications as pandas DataFrame"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM applications ORDER BY application_date DESC", conn)
        conn.close()
        return df
    
    def get_application_by_id(self, app_id):
        """Get specific application by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM applications WHERE id = ?", (app_id,))
        result = cursor.fetchone()
        conn.close()
        return result
    
    def update_application_status(self, app_id, status, rejection_reason=None):
        """Update application status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if rejection_reason:
            cursor.execute('''
                UPDATE applications 
                SET status = ?, rejection_reason = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (status, rejection_reason, app_id))
        else:
            cursor.execute('''
                UPDATE applications 
                SET status = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (status, app_id))
        
        conn.commit()
        conn.close()
    
    def add_followup(self, application_id, follow_up_date, follow_up_type, notes):
        """Add a follow-up reminder"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO followups (application_id, follow_up_date, follow_up_type, notes)
            VALUES (?, ?, ?, ?)
        ''', (application_id, follow_up_date, follow_up_type, notes))
        
        conn.commit()
        conn.close()
    
    def get_pending_followups(self):
        """Get all pending follow-ups"""
        conn = sqlite3.connect(self.db_path)
        query = '''
            SELECT f.*, a.company_name, a.job_title 
            FROM followups f
            JOIN applications a ON f.application_id = a.id
            WHERE f.completed = FALSE AND f.follow_up_date <= date('now')
            ORDER BY f.follow_up_date ASC
        '''
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    def complete_followup(self, followup_id):
        """Mark a follow-up as completed"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE followups SET completed = TRUE WHERE id = ?", (followup_id,))
        conn.commit()
        conn.close()
    
    def get_application_stats(self):
        """Get application statistics"""
        conn = sqlite3.connect(self.db_path)
        
        # Total applications
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM applications")
        total_apps = cursor.fetchone()[0]
        
        # Status breakdown
        status_df = pd.read_sql_query('''
            SELECT status, COUNT(*) as count 
            FROM applications 
            GROUP BY status
        ''', conn)
        
        # Applications by month
        monthly_df = pd.read_sql_query('''
            SELECT 
                strftime('%Y-%m', application_date) as month,
                COUNT(*) as applications
            FROM applications
            GROUP BY strftime('%Y-%m', application_date)
            ORDER BY month DESC
        ''', conn)
        
        # Response rate
        cursor.execute('''
            SELECT COUNT(*) FROM applications 
            WHERE status IN ('Interview Scheduled', 'Interview Completed', 'Offer Received', 'Hired')
        ''')
        responses = cursor.fetchone()[0]
        
        response_rate = (responses / total_apps * 100) if total_apps > 0 else 0
        
        conn.close()
        
        return {
            'total_applications': total_apps,
            'status_breakdown': status_df,
            'monthly_applications': monthly_df,
            'response_rate': response_rate
        }
    
    def get_rejection_analysis(self):
        """Analyze rejection patterns"""
        conn = sqlite3.connect(self.db_path)
        
        rejection_reasons = pd.read_sql_query('''
            SELECT rejection_reason, COUNT(*) as count
            FROM applications
            WHERE status = 'Rejected' AND rejection_reason IS NOT NULL
            GROUP BY rejection_reason
            ORDER BY count DESC
        ''', conn)
        
        # Time to rejection analysis
        time_to_rejection = pd.read_sql_query('''
            SELECT 
                company_name,
                job_title,
                application_date,
                updated_at,
                julianday(updated_at) - julianday(application_date) as days_to_rejection
            FROM applications
            WHERE status = 'Rejected'
            ORDER BY days_to_rejection DESC
        ''', conn)
        
        conn.close()
        
        return {
            'rejection_reasons': rejection_reasons,
            'time_to_rejection': time_to_rejection
        }
    
    def delete_application(self, app_id):
        """Delete an application and related data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Delete related follow-ups first
        cursor.execute("DELETE FROM followups WHERE application_id = ?", (app_id,))
        cursor.execute("DELETE FROM interviews WHERE application_id = ?", (app_id,))
        cursor.execute("DELETE FROM applications WHERE id = ?", (app_id,))
        
        conn.commit()
        conn.close()

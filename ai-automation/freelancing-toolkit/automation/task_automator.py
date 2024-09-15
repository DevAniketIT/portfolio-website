#!/usr/bin/env python3
"""
Task Automator
Automates common business tasks and workflows.
Perfect for Upwork Python automation gigs.
"""

import os
import shutil
import schedule
import time
import smtplib
import zipfile
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from email.mime.base import MimeBase
from email import encoders
import logging
import json
from typing import List, Dict, Any

class TaskAutomator:
    def __init__(self, config_file: str = "automation_config.json"):
        """Initialize the task automator with configuration"""
        self.config = self.load_config(config_file)
        self.setup_logging()
    
    def load_config(self, config_file: str) -> Dict:
        """Load configuration from JSON file"""
        default_config = {
            "email": {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "",
                "password": ""
            },
            "file_operations": {
                "watch_folders": [],
                "backup_folders": [],
                "cleanup_folders": []
            },
            "api_endpoints": {},
            "schedules": {}
        }
        
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
        
        return default_config
    
    def setup_logging(self):
        """Setup logging for automation tasks"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'automation_{datetime.now().strftime("%Y%m")}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def file_organizer(self, source_folder: str, rules: Dict[str, str]):
        """
        Organize files based on extension rules
        
        Args:
            source_folder: Folder to organize
            rules: Dictionary mapping file extensions to destination folders
        """
        source_path = Path(source_folder)
        
        if not source_path.exists():
            self.logger.error(f"Source folder does not exist: {source_folder}")
            return
        
        organized_count = 0
        
        for file_path in source_path.iterdir():
            if file_path.is_file():
                file_ext = file_path.suffix.lower()
                
                if file_ext in rules:
                    dest_folder = Path(rules[file_ext])
                    dest_folder.mkdir(parents=True, exist_ok=True)
                    
                    dest_path = dest_folder / file_path.name
                    
                    # Handle duplicate names
                    counter = 1
                    original_dest = dest_path
                    while dest_path.exists():
                        name_part = original_dest.stem
                        ext_part = original_dest.suffix
                        dest_path = dest_folder / f"{name_part}_{counter}{ext_part}"
                        counter += 1
                    
                    shutil.move(str(file_path), str(dest_path))
                    organized_count += 1
                    self.logger.info(f"Moved {file_path.name} to {dest_path}")
        
        self.logger.info(f"Organized {organized_count} files from {source_folder}")
    
    def backup_folders(self, folders: List[str], backup_location: str):
        """
        Create compressed backups of specified folders
        """
        backup_path = Path(backup_location)
        backup_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for folder in folders:
            folder_path = Path(folder)
            if folder_path.exists():
                backup_name = f"{folder_path.name}_backup_{timestamp}.zip"
                backup_file = backup_path / backup_name
                
                with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for file_path in folder_path.rglob('*'):
                        if file_path.is_file():
                            arcname = file_path.relative_to(folder_path)
                            zipf.write(file_path, arcname)
                
                self.logger.info(f"Backup created: {backup_file}")
            else:
                self.logger.warning(f"Folder not found for backup: {folder}")
    
    def cleanup_old_files(self, folder: str, days_old: int = 30, file_pattern: str = "*"):
        """
        Delete files older than specified days
        """
        folder_path = Path(folder)
        if not folder_path.exists():
            return
        
        cutoff_date = datetime.now() - timedelta(days=days_old)
        deleted_count = 0
        
        for file_path in folder_path.glob(file_pattern):
            if file_path.is_file():
                file_modified_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                
                if file_modified_time < cutoff_date:
                    file_path.unlink()
                    deleted_count += 1
                    self.logger.info(f"Deleted old file: {file_path}")
        
        self.logger.info(f"Deleted {deleted_count} old files from {folder}")
    
    def send_email(self, to_email: str, subject: str, body: str, attachments: List[str] = None):
        """
        Send email with optional attachments
        """
        try:
            msg = MimeMultipart()
            msg['From'] = self.config['email']['username']
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MimeText(body, 'plain'))
            
            # Add attachments
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, "rb") as attachment:
                            part = MimeBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                        
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {os.path.basename(file_path)}'
                        )
                        msg.attach(part)
            
            # Send email
            server = smtplib.SMTP(self.config['email']['smtp_server'], self.config['email']['smtp_port'])
            server.starttls()
            server.login(self.config['email']['username'], self.config['email']['password'])
            text = msg.as_string()
            server.sendmail(self.config['email']['username'], to_email, text)
            server.quit()
            
            self.logger.info(f"Email sent successfully to {to_email}")
            
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
    
    def generate_report(self, data_file: str, report_type: str = "summary"):
        """
        Generate automated reports from data files
        """
        try:
            # Read data (supports CSV, Excel)
            if data_file.endswith('.csv'):
                df = pd.read_csv(data_file)
            elif data_file.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(data_file)
            else:
                raise ValueError("Unsupported file format")
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if report_type == "summary":
                # Generate summary statistics
                summary = {
                    "total_records": len(df),
                    "columns": list(df.columns),
                    "date_generated": datetime.now().isoformat(),
                    "summary_stats": df.describe().to_dict() if len(df) > 0 else {}
                }
                
                report_file = f"summary_report_{timestamp}.json"
                with open(report_file, 'w') as f:
                    json.dump(summary, f, indent=2)
            
            elif report_type == "excel":
                # Generate Excel report with multiple sheets
                report_file = f"detailed_report_{timestamp}.xlsx"
                with pd.ExcelWriter(report_file) as writer:
                    df.to_excel(writer, sheet_name='Raw_Data', index=False)
                    df.describe().to_excel(writer, sheet_name='Statistics')
            
            self.logger.info(f"Report generated: {report_file}")
            return report_file
            
        except Exception as e:
            self.logger.error(f"Failed to generate report: {e}")
            return None
    
    def api_data_sync(self, endpoint_name: str):
        """
        Sync data from API endpoints
        """
        if endpoint_name not in self.config['api_endpoints']:
            self.logger.error(f"API endpoint not configured: {endpoint_name}")
            return
        
        endpoint_config = self.config['api_endpoints'][endpoint_name]
        
        try:
            headers = endpoint_config.get('headers', {})
            response = requests.get(endpoint_config['url'], headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            # Save data
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"{endpoint_name}_data_{timestamp}.json"
            
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.logger.info(f"API data synced from {endpoint_name}: {output_file}")
            
            # Convert to Excel if needed
            if isinstance(data, list) and data:
                df = pd.DataFrame(data)
                excel_file = f"{endpoint_name}_data_{timestamp}.xlsx"
                df.to_excel(excel_file, index=False)
                self.logger.info(f"Excel file created: {excel_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to sync data from {endpoint_name}: {e}")
    
    def schedule_tasks(self):
        """
        Setup scheduled tasks based on configuration
        """
        schedules_config = self.config.get('schedules', {})
        
        for task_name, task_config in schedules_config.items():
            task_type = task_config.get('type')
            frequency = task_config.get('frequency')
            time_str = task_config.get('time', '09:00')
            
            if task_type == 'file_organization':
                if frequency == 'daily':
                    schedule.every().day.at(time_str).do(
                        self.file_organizer, 
                        task_config['source_folder'], 
                        task_config['rules']
                    )
                elif frequency == 'weekly':
                    schedule.every().week.do(
                        self.file_organizer, 
                        task_config['source_folder'], 
                        task_config['rules']
                    )
            
            elif task_type == 'backup':
                if frequency == 'daily':
                    schedule.every().day.at(time_str).do(
                        self.backup_folders,
                        task_config['folders'],
                        task_config['backup_location']
                    )
            
            elif task_type == 'cleanup':
                if frequency == 'weekly':
                    schedule.every().week.do(
                        self.cleanup_old_files,
                        task_config['folder'],
                        task_config.get('days_old', 30)
                    )
        
        self.logger.info("Scheduled tasks configured")
    
    def run_scheduler(self):
        """
        Run the task scheduler
        """
        self.schedule_tasks()
        
        self.logger.info("Task scheduler started")
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

def main():
    automator = TaskAutomator()
    
    # Example usage
    print("Task Automator initialized")
    print("Available methods:")
    print("1. file_organizer(source_folder, rules)")
    print("2. backup_folders(folders, backup_location)")
    print("3. cleanup_old_files(folder, days_old)")
    print("4. send_email(to_email, subject, body, attachments)")
    print("5. generate_report(data_file, report_type)")
    print("6. api_data_sync(endpoint_name)")
    print("7. run_scheduler()")

if __name__ == "__main__":
    main()

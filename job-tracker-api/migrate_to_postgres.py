"""
Database Migration Script: SQLite to PostgreSQL

This script migrates all data from the existing SQLite database to PostgreSQL,
including applications, followups/interactions, and validates data integrity.
"""

import os
import sys
import json
import sqlite3
import logging
from datetime import datetime, date
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Add current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from postgresql_db import JobApplicationDB, create_database_instance
from models import ApplicationStatus, JobType, RemoteType, Priority, InteractionType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migration.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class MigrationStats:
    """Statistics for tracking migration progress."""
    applications_total: int = 0
    applications_migrated: int = 0
    applications_failed: int = 0
    followups_total: int = 0
    followups_migrated: int = 0
    followups_failed: int = 0
    interviews_total: int = 0
    interviews_migrated: int = 0
    interviews_failed: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    def duration(self) -> float:
        """Get migration duration in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0


class SQLiteDataExtractor:
    """Extracts data from existing SQLite database."""
    
    def __init__(self, sqlite_path: str):
        self.sqlite_path = sqlite_path
        self.connection = None
    
    def connect(self):
        """Connect to SQLite database."""
        try:
            self.connection = sqlite3.connect(self.sqlite_path)
            self.connection.row_factory = sqlite3.Row  # Enable column access by name
            logger.info(f"Connected to SQLite database: {self.sqlite_path}")
        except Exception as e:
            logger.error(f"Failed to connect to SQLite database: {e}")
            raise
    
    def disconnect(self):
        """Disconnect from SQLite database."""
        if self.connection:
            self.connection.close()
            logger.info("Disconnected from SQLite database")
    
    def get_table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database."""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name=?
        """, (table_name,))
        return cursor.fetchone() is not None
    
    def get_applications(self) -> List[Dict[str, Any]]:
        """Extract all applications from SQLite database."""
        if not self.get_table_exists('applications'):
            logger.warning("Applications table does not exist in SQLite database")
            return []
        
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM applications ORDER BY id")
        
        applications = []
        for row in cursor.fetchall():
            app_data = dict(row)
            
            # Convert date strings to date objects
            for date_field in ['application_date', 'deadline']:
                if app_data.get(date_field):
                    try:
                        if isinstance(app_data[date_field], str):
                            app_data[date_field] = datetime.strptime(
                                app_data[date_field], '%Y-%m-%d'
                            ).date()
                    except ValueError:
                        logger.warning(f"Invalid date format for {date_field}: {app_data[date_field]}")
                        app_data[date_field] = None
            
            # Convert datetime strings to datetime objects
            for datetime_field in ['created_at', 'updated_at']:
                if app_data.get(datetime_field):
                    try:
                        if isinstance(app_data[datetime_field], str):
                            # Handle multiple datetime formats
                            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S.%f']:
                                try:
                                    app_data[datetime_field] = datetime.strptime(
                                        app_data[datetime_field], fmt
                                    )
                                    break
                                except ValueError:
                                    continue
                    except (ValueError, TypeError):
                        logger.warning(f"Invalid datetime format for {datetime_field}: {app_data[datetime_field]}")
                        app_data[datetime_field] = datetime.now()
            
            # Convert enum string values to enum instances
            try:
                if app_data.get('status'):
                    app_data['status'] = ApplicationStatus(app_data['status'])
                if app_data.get('job_type'):
                    app_data['job_type'] = JobType(app_data['job_type'])
                if app_data.get('remote_type'):
                    app_data['remote_type'] = RemoteType(app_data['remote_type'])
                if app_data.get('priority'):
                    app_data['priority'] = Priority(app_data['priority'])
            except ValueError as e:
                logger.warning(f"Invalid enum value in application {app_data.get('id')}: {e}")
            
            applications.append(app_data)
        
        logger.info(f"Extracted {len(applications)} applications from SQLite")
        return applications
    
    def get_followups_and_history(self) -> List[Dict[str, Any]]:
        """
        Extract followup data from various possible sources.
        
        This looks for:
        1. application_history table (if exists)
        2. followups table (if exists)  
        3. interactions table (if exists)
        """
        followups = []
        
        # Check for application_history table (from existing code)
        if self.get_table_exists('application_history'):
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM application_history ORDER BY created_at")
            
            for row in cursor.fetchall():
                history_data = dict(row)
                
                # Convert to followup format
                followup_data = {
                    'application_id': history_data.get('application_id'),
                    'interaction_type': history_data.get('interaction_type', 'follow_up'),
                    'title': history_data.get('title', 'Interaction'),
                    'description': history_data.get('description'),
                    'interaction_date': history_data.get('interaction_date'),
                    'old_status': history_data.get('old_status'),
                    'new_status': history_data.get('new_status'),
                    'outcome': history_data.get('outcome'),
                    'follow_up_needed': history_data.get('follow_up_needed', False),
                    'follow_up_date': history_data.get('follow_up_date'),
                    'notes': history_data.get('description'),  # Use description as notes
                    'created_at': history_data.get('created_at'),
                    'updated_at': history_data.get('created_at')  # Use created_at as updated_at
                }
                
                # Convert date strings to date objects
                for date_field in ['interaction_date', 'follow_up_date']:
                    if followup_data.get(date_field):
                        try:
                            if isinstance(followup_data[date_field], str):
                                followup_data[date_field] = datetime.strptime(
                                    followup_data[date_field], '%Y-%m-%d'
                                ).date()
                        except ValueError:
                            followup_data[date_field] = None
                
                # Convert datetime strings
                for datetime_field in ['created_at', 'updated_at']:
                    if followup_data.get(datetime_field):
                        try:
                            if isinstance(followup_data[datetime_field], str):
                                followup_data[datetime_field] = datetime.strptime(
                                    followup_data[datetime_field], '%Y-%m-%d %H:%M:%S'
                                )
                        except ValueError:
                            followup_data[datetime_field] = datetime.now()
                
                # Convert enum values
                try:
                    if followup_data.get('interaction_type'):
                        # Map old values to new enum values
                        interaction_type_map = {
                            'application': InteractionType.APPLICATION,
                            'email': InteractionType.EMAIL,
                            'phone_call': InteractionType.PHONE_CALL,
                            'interview': InteractionType.INTERVIEW,
                            'follow_up': InteractionType.FOLLOW_UP,
                            'networking': InteractionType.NETWORKING,
                            'other': InteractionType.OTHER
                        }
                        interaction_type_str = followup_data['interaction_type'].lower()
                        if interaction_type_str in interaction_type_map:
                            followup_data['interaction_type'] = interaction_type_map[interaction_type_str]
                        else:
                            followup_data['interaction_type'] = InteractionType.OTHER
                    
                    if followup_data.get('old_status'):
                        followup_data['old_status'] = ApplicationStatus(followup_data['old_status'])
                    if followup_data.get('new_status'):
                        followup_data['new_status'] = ApplicationStatus(followup_data['new_status'])
                
                except ValueError as e:
                    logger.warning(f"Invalid enum value in followup: {e}")
                
                followups.append(followup_data)
            
            logger.info(f"Extracted {len(followups)} followup records from application_history")
        
        # Check for dedicated followups table
        elif self.get_table_exists('followups'):
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM followups ORDER BY created_at")
            
            for row in cursor.fetchall():
                followup_data = dict(row)
                # Process similar to above...
                followups.append(followup_data)
            
            logger.info(f"Extracted {len(followups)} followup records from followups table")
        
        return followups
    
    def get_interviews(self) -> List[Dict[str, Any]]:
        """Extract interview data if interviews table exists."""
        if not self.get_table_exists('interviews'):
            logger.info("No interviews table found in SQLite database")
            return []
        
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM interviews ORDER BY created_at")
        
        interviews = []
        for row in cursor.fetchall():
            interview_data = dict(row)
            
            # Convert date strings to date objects
            for date_field in ['interview_date', 'follow_up_date']:
                if interview_data.get(date_field):
                    try:
                        if isinstance(interview_data[date_field], str):
                            interview_data[date_field] = datetime.strptime(
                                interview_data[date_field], '%Y-%m-%d'
                            ).date()
                    except ValueError:
                        interview_data[date_field] = None
            
            # Convert datetime strings
            for datetime_field in ['created_at', 'updated_at']:
                if interview_data.get(datetime_field):
                    try:
                        if isinstance(interview_data[datetime_field], str):
                            interview_data[datetime_field] = datetime.strptime(
                                interview_data[datetime_field], '%Y-%m-%d %H:%M:%S'
                            )
                    except ValueError:
                        interview_data[datetime_field] = datetime.now()
            
            interviews.append(interview_data)
        
        logger.info(f"Extracted {len(interviews)} interview records from SQLite")
        return interviews


class PostgreSQLMigrator:
    """Handles migration to PostgreSQL database."""
    
    def __init__(self, postgres_db: JobApplicationDB):
        self.postgres_db = postgres_db
        self.id_mapping = {}  # Maps old SQLite IDs to new PostgreSQL IDs
    
    def create_schema(self):
        """Create PostgreSQL schema/tables."""
        logger.info("Creating PostgreSQL schema...")
        self.postgres_db.init_db()
        logger.info("PostgreSQL schema created successfully")
    
    def migrate_applications(self, applications: List[Dict[str, Any]]) -> int:
        """Migrate applications to PostgreSQL."""
        migrated_count = 0
        failed_count = 0
        
        logger.info(f"Migrating {len(applications)} applications...")
        
        for i, app_data in enumerate(applications, 1):
            try:
                old_id = app_data.pop('id', None)  # Remove old ID
                
                # Create application in PostgreSQL
                new_id = self.postgres_db.create_application(app_data)
                
                if new_id:
                    self.id_mapping[old_id] = new_id
                    migrated_count += 1
                    
                    if i % 10 == 0:  # Progress update every 10 records
                        logger.info(f"Migrated {i}/{len(applications)} applications...")
                else:
                    failed_count += 1
                    logger.error(f"Failed to create application: {app_data.get('company_name', 'Unknown')}")
                    
            except Exception as e:
                failed_count += 1
                logger.error(f"Error migrating application {old_id}: {e}")
        
        logger.info(f"Applications migration complete: {migrated_count} migrated, {failed_count} failed")
        return migrated_count
    
    def migrate_followups(self, followups: List[Dict[str, Any]]) -> int:
        """Migrate followups to PostgreSQL."""
        migrated_count = 0
        failed_count = 0
        
        logger.info(f"Migrating {len(followups)} followups...")
        
        for i, followup_data in enumerate(followups, 1):
            try:
                old_app_id = followup_data.get('application_id')
                
                # Map to new application ID
                if old_app_id in self.id_mapping:
                    followup_data['application_id'] = self.id_mapping[old_app_id]
                    
                    # Remove old ID if present
                    followup_data.pop('id', None)
                    
                    # Create followup in PostgreSQL
                    new_id = self.postgres_db.create_followup(followup_data)
                    
                    if new_id:
                        migrated_count += 1
                        
                        if i % 10 == 0:
                            logger.info(f"Migrated {i}/{len(followups)} followups...")
                    else:
                        failed_count += 1
                        logger.error(f"Failed to create followup for application {old_app_id}")
                else:
                    failed_count += 1
                    logger.warning(f"Skipping followup - application {old_app_id} not found in mapping")
                    
            except Exception as e:
                failed_count += 1
                logger.error(f"Error migrating followup: {e}")
        
        logger.info(f"Followups migration complete: {migrated_count} migrated, {failed_count} failed")
        return migrated_count
    
    def migrate_interviews(self, interviews: List[Dict[str, Any]]) -> int:
        """Migrate interviews to PostgreSQL."""
        migrated_count = 0
        failed_count = 0
        
        logger.info(f"Migrating {len(interviews)} interviews...")
        
        for i, interview_data in enumerate(interviews, 1):
            try:
                old_app_id = interview_data.get('application_id')
                
                # Map to new application ID
                if old_app_id in self.id_mapping:
                    interview_data['application_id'] = self.id_mapping[old_app_id]
                    
                    # Remove old ID if present
                    interview_data.pop('id', None)
                    
                    # Create interview in PostgreSQL
                    new_id = self.postgres_db.create_interview(interview_data)
                    
                    if new_id:
                        migrated_count += 1
                        
                        if i % 10 == 0:
                            logger.info(f"Migrated {i}/{len(interviews)} interviews...")
                    else:
                        failed_count += 1
                        logger.error(f"Failed to create interview for application {old_app_id}")
                else:
                    failed_count += 1
                    logger.warning(f"Skipping interview - application {old_app_id} not found in mapping")
                    
            except Exception as e:
                failed_count += 1
                logger.error(f"Error migrating interview: {e}")
        
        logger.info(f"Interviews migration complete: {migrated_count} migrated, {failed_count} failed")
        return migrated_count


class DataIntegrityValidator:
    """Validates data integrity after migration."""
    
    def __init__(self, sqlite_extractor: SQLiteDataExtractor, postgres_db: JobApplicationDB):
        self.sqlite_extractor = sqlite_extractor
        self.postgres_db = postgres_db
    
    def validate_applications(self, original_count: int) -> bool:
        """Validate application migration."""
        postgres_count = len(self.postgres_db.get_applications()['items'])
        
        if postgres_count == original_count:
            logger.info(f"✓ Application count matches: {postgres_count}")
            return True
        else:
            logger.error(f"✗ Application count mismatch: SQLite={original_count}, PostgreSQL={postgres_count}")
            return False
    
    def validate_data_integrity(self, sqlite_applications: List[Dict[str, Any]]) -> Dict[str, bool]:
        """Perform comprehensive data integrity validation."""
        results = {}
        
        logger.info("Starting data integrity validation...")
        
        # Validate application count
        postgres_apps = self.postgres_db.get_applications(limit=10000)  # Get all applications
        results['application_count'] = len(postgres_apps['items']) == len(sqlite_applications)
        
        if results['application_count']:
            logger.info(f"✓ Application count validation passed: {len(postgres_apps['items'])}")
        else:
            logger.error(f"✗ Application count validation failed: SQLite={len(sqlite_applications)}, PostgreSQL={len(postgres_apps['items'])}")
        
        # Validate sample data consistency
        if postgres_apps['items'] and sqlite_applications:
            sample_passed = 0
            sample_total = min(5, len(postgres_apps['items']))
            
            for i in range(sample_total):
                pg_app = postgres_apps['items'][i]
                # Find corresponding SQLite app by company name and job title
                sqlite_app = next(
                    (app for app in sqlite_applications 
                     if app.get('company_name') == pg_app.get('company_name') 
                     and app.get('job_title') == pg_app.get('job_title')), 
                    None
                )
                
                if sqlite_app:
                    # Compare key fields
                    if (pg_app.get('company_name') == sqlite_app.get('company_name') and
                        pg_app.get('job_title') == sqlite_app.get('job_title') and
                        str(pg_app.get('status')) == str(sqlite_app.get('status'))):
                        sample_passed += 1
            
            results['sample_data'] = sample_passed == sample_total
            
            if results['sample_data']:
                logger.info(f"✓ Sample data validation passed: {sample_passed}/{sample_total}")
            else:
                logger.warning(f"⚠ Sample data validation partial: {sample_passed}/{sample_total}")
        
        # Validate schema structure
        try:
            # Test basic database operations
            test_app = {
                'company_name': 'Migration Test Company',
                'job_title': 'Migration Test Position',
                'status': ApplicationStatus.APPLIED,
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
            
            test_id = self.postgres_db.create_application(test_app)
            if test_id:
                retrieved = self.postgres_db.get_application(test_id)
                self.postgres_db.delete_application(test_id)  # Cleanup
                results['schema_operations'] = retrieved is not None
            else:
                results['schema_operations'] = False
                
        except Exception as e:
            logger.error(f"Schema validation failed: {e}")
            results['schema_operations'] = False
        
        if results['schema_operations']:
            logger.info("✓ Schema operations validation passed")
        else:
            logger.error("✗ Schema operations validation failed")
        
        return results


def run_migration(sqlite_path: str, postgres_url: str, validate_only: bool = False) -> MigrationStats:
    """
    Run the complete migration process.
    
    Args:
        sqlite_path: Path to SQLite database file
        postgres_url: PostgreSQL connection URL
        validate_only: If True, only validate without migrating
        
    Returns:
        MigrationStats with results
    """
    stats = MigrationStats()
    stats.start_time = datetime.now()
    
    logger.info("=" * 60)
    logger.info("Starting SQLite to PostgreSQL Migration")
    logger.info("=" * 60)
    logger.info(f"SQLite path: {sqlite_path}")
    logger.info(f"PostgreSQL URL: {postgres_url}")
    logger.info(f"Validate only: {validate_only}")
    logger.info("")
    
    try:
        # Initialize connections
        logger.info("1. Initializing database connections...")
        sqlite_extractor = SQLiteDataExtractor(sqlite_path)
        sqlite_extractor.connect()
        
        postgres_db = create_database_instance(postgres_url, echo=False)
        migrator = PostgreSQLMigrator(postgres_db)
        
        # Extract data from SQLite
        logger.info("2. Extracting data from SQLite...")
        applications = sqlite_extractor.get_applications()
        followups = sqlite_extractor.get_followups_and_history()
        interviews = sqlite_extractor.get_interviews()
        
        stats.applications_total = len(applications)
        stats.followups_total = len(followups)
        stats.interviews_total = len(interviews)
        
        logger.info(f"Data extraction summary:")
        logger.info(f"  - Applications: {stats.applications_total}")
        logger.info(f"  - Followups: {stats.followups_total}")
        logger.info(f"  - Interviews: {stats.interviews_total}")
        logger.info("")
        
        if not validate_only:
            # Create PostgreSQL schema
            logger.info("3. Creating PostgreSQL schema...")
            migrator.create_schema()
            
            # Migrate applications
            logger.info("4. Migrating applications...")
            stats.applications_migrated = migrator.migrate_applications(applications)
            stats.applications_failed = stats.applications_total - stats.applications_migrated
            
            # Migrate followups
            logger.info("5. Migrating followups...")
            stats.followups_migrated = migrator.migrate_followups(followups)
            stats.followups_failed = stats.followups_total - stats.followups_migrated
            
            # Migrate interviews
            logger.info("6. Migrating interviews...")
            stats.interviews_migrated = migrator.migrate_interviews(interviews)
            stats.interviews_failed = stats.interviews_total - stats.interviews_migrated
            
            logger.info("")
        
        # Validate data integrity
        logger.info("7. Validating data integrity...")
        validator = DataIntegrityValidator(sqlite_extractor, postgres_db)
        validation_results = validator.validate_data_integrity(applications)
        
        # Print validation results
        logger.info("Validation results:")
        for check, passed in validation_results.items():
            status = "✓ PASS" if passed else "✗ FAIL"
            logger.info(f"  - {check.replace('_', ' ').title()}: {status}")
        
        all_passed = all(validation_results.values())
        if all_passed:
            logger.info("✓ All validation checks passed!")
        else:
            logger.warning("⚠ Some validation checks failed - please review")
        
        sqlite_extractor.disconnect()
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise
    
    finally:
        stats.end_time = datetime.now()
    
    # Print summary
    logger.info("")
    logger.info("=" * 60)
    logger.info("Migration Summary")
    logger.info("=" * 60)
    logger.info(f"Duration: {stats.duration():.2f} seconds")
    logger.info(f"Applications: {stats.applications_migrated}/{stats.applications_total} migrated")
    logger.info(f"Followups: {stats.followups_migrated}/{stats.followups_total} migrated") 
    logger.info(f"Interviews: {stats.interviews_migrated}/{stats.interviews_total} migrated")
    
    if not validate_only:
        total_migrated = stats.applications_migrated + stats.followups_migrated + stats.interviews_migrated
        total_items = stats.applications_total + stats.followups_total + stats.interviews_total
        success_rate = (total_migrated / total_items * 100) if total_items > 0 else 0
        logger.info(f"Overall success rate: {success_rate:.1f}%")
    
    logger.info("Migration completed!")
    
    return stats


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate SQLite database to PostgreSQL")
    parser.add_argument("--sqlite", required=True, help="Path to SQLite database file")
    parser.add_argument("--postgres", required=True, help="PostgreSQL connection URL")
    parser.add_argument("--validate-only", action="store_true", help="Only validate, don't migrate")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        stats = run_migration(args.sqlite, args.postgres, args.validate_only)
        
        # Save migration report
        report = {
            'timestamp': datetime.now().isoformat(),
            'sqlite_path': args.sqlite,
            'postgres_url': args.postgres,
            'validate_only': args.validate_only,
            'duration_seconds': stats.duration(),
            'applications': {
                'total': stats.applications_total,
                'migrated': stats.applications_migrated,
                'failed': stats.applications_failed
            },
            'followups': {
                'total': stats.followups_total,
                'migrated': stats.followups_migrated,
                'failed': stats.followups_failed
            },
            'interviews': {
                'total': stats.interviews_total,
                'migrated': stats.interviews_migrated,
                'failed': stats.interviews_failed
            }
        }
        
        with open('migration_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info("Migration report saved to migration_report.json")
        
        # Exit with appropriate code
        total_failed = stats.applications_failed + stats.followups_failed + stats.interviews_failed
        sys.exit(1 if total_failed > 0 else 0)
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        sys.exit(1)

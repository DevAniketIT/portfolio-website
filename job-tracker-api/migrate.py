#!/usr/bin/env python3
"""
Database migration script for Job Application Tracker API.

This script handles database initialization and schema migrations.
It can be run standalone or imported by other modules.
"""

import os
import sys
import logging
import argparse
from typing import Optional
from postgresql_db import create_database_instance, Base
from sqlalchemy import text
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_migration(database_url: Optional[str] = None, force: bool = False) -> bool:
    """
    Run database migrations.
    
    Args:
        database_url: Database connection string
        force: Whether to force recreation of tables
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Get database URL
        if not database_url:
            database_url = os.getenv('DATABASE_URL')
        
        if not database_url:
            logger.error("DATABASE_URL not provided and not found in environment")
            return False
        
        logger.info("Starting database migration...")
        logger.info(f"Database URL: {database_url.split('@')[0]}@***")  # Hide password
        
        # Create database instance
        db = create_database_instance(database_url, echo=False)
        
        # Test connection
        logger.info("Testing database connection...")
        session = db.get_session()
        try:
            session.execute(text("SELECT 1"))
            logger.info("✅ Database connection successful")
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False
        finally:
            session.close()
        
        # Create tables
        logger.info("Creating database tables...")
        
        if force:
            logger.warning("FORCE mode enabled - dropping existing tables")
            Base.metadata.drop_all(bind=db.engine)
        
        # Create all tables
        Base.metadata.create_all(bind=db.engine)
        
        # Verify tables were created
        logger.info("Verifying table creation...")
        session = db.get_session()
        try:
            # Check if applications table exists and has correct structure
            result = session.execute(text("""
                SELECT COUNT(*) as table_count 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('applications', 'followups', 'interviews')
            """))
            table_count = result.scalar()
            
            if table_count >= 3:
                logger.info("✅ All required tables created successfully")
                
                # Log table information
                result = session.execute(text("""
                    SELECT table_name, 
                           (SELECT count(*) FROM information_schema.columns 
                            WHERE table_name = t.table_name) as column_count
                    FROM information_schema.tables t
                    WHERE table_schema = 'public' 
                    AND table_name IN ('applications', 'followups', 'interviews')
                    ORDER BY table_name
                """))
                
                for row in result:
                    logger.info(f"  📋 Table '{row.table_name}': {row.column_count} columns")
                
            else:
                logger.error(f"❌ Expected 3 tables, found {table_count}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Table verification failed: {e}")
            return False
        finally:
            session.close()
        
        # Run any custom migrations
        if not run_custom_migrations(db):
            logger.warning("⚠️ Some custom migrations failed, but core tables are ready")
        
        logger.info("🎉 Database migration completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        return False


def run_custom_migrations(db) -> bool:
    """
    Run any custom migrations or data seeding.
    
    Args:
        db: Database instance
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("Running custom migrations...")
        session = db.get_session()
        
        try:
            # Example: Create indexes for better performance
            logger.info("Creating performance indexes...")
            
            indexes = [
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_applications_status ON applications (status)",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_applications_company ON applications (company_name)",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_applications_date ON applications (application_date)",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_followups_app_id ON followups (application_id)",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_interviews_app_id ON interviews (application_id)",
            ]
            
            for index_sql in indexes:
                try:
                    session.execute(text(index_sql))
                    logger.info(f"  ✓ Created index: {index_sql.split()[-1]}")
                except Exception as e:
                    logger.warning(f"  ⚠️ Index creation skipped: {e}")
            
            session.commit()
            
            # Example: Insert default data if needed
            logger.info("Checking for default data...")
            
            # You can add default data insertion here
            # For example:
            # - Default application statuses
            # - System configuration
            # - Sample data for testing
            
            logger.info("✅ Custom migrations completed")
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"❌ Custom migrations failed: {e}")
            return False
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"❌ Custom migrations setup failed: {e}")
        return False


def check_migration_status(database_url: Optional[str] = None) -> bool:
    """
    Check the current migration status.
    
    Args:
        database_url: Database connection string
        
    Returns:
        True if database is properly migrated, False otherwise
    """
    try:
        if not database_url:
            database_url = os.getenv('DATABASE_URL')
        
        if not database_url:
            logger.error("DATABASE_URL not provided")
            return False
        
        db = create_database_instance(database_url, echo=False)
        session = db.get_session()
        
        try:
            # Check if core tables exist
            result = session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('applications', 'followups', 'interviews')
                ORDER BY table_name
            """))
            
            tables = [row.table_name for row in result]
            expected_tables = ['applications', 'followups', 'interviews']
            
            logger.info("Database migration status:")
            for table in expected_tables:
                if table in tables:
                    logger.info(f"  ✅ {table}")
                else:
                    logger.info(f"  ❌ {table} (missing)")
            
            return len(tables) == len(expected_tables)
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return False


def main():
    """Main entry point for migration script."""
    parser = argparse.ArgumentParser(description='Database migration tool')
    parser.add_argument('--database-url', help='Database connection URL')
    parser.add_argument('--force', action='store_true', 
                       help='Force recreation of tables (DESTRUCTIVE)')
    parser.add_argument('--check', action='store_true', 
                       help='Check migration status without making changes')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if args.check:
        logger.info("Checking database migration status...")
        success = check_migration_status(args.database_url)
        if success:
            logger.info("✅ Database is properly migrated")
            sys.exit(0)
        else:
            logger.error("❌ Database migration required")
            sys.exit(1)
    else:
        logger.info("Starting database migration...")
        success = run_migration(args.database_url, args.force)
        
        if success:
            logger.info("🎉 Migration completed successfully!")
            sys.exit(0)
        else:
            logger.error("❌ Migration failed!")
            sys.exit(1)


if __name__ == '__main__':
    main()

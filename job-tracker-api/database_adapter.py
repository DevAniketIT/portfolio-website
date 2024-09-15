"""
Database Abstraction Layer for Dual Database Support

This module provides a clean abstraction layer that supports both SQLite and PostgreSQL
backends with automatic environment-based detection and connection pooling.
"""

import os
import asyncio
import sqlite3
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any, Union
from datetime import datetime, timedelta
import logging
from contextlib import asynccontextmanager

# PostgreSQL support (optional dependency)
try:
    import asyncpg
    from asyncpg.pool import Pool
    ASYNCPG_AVAILABLE = True
except ImportError:
    ASYNCPG_AVAILABLE = False
    Pool = None

# SQLAlchemy ORM support (optional dependency)  
try:
    from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker, relationship
    from sqlalchemy.pool import StaticPool
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    declarative_base = None

# Import existing price monitor for SQLite operations
try:
    from price_monitor_system import PriceMonitor
    PRICE_MONITOR_AVAILABLE = True
except ImportError:
    PRICE_MONITOR_AVAILABLE = False

logger = logging.getLogger(__name__)

# SQLAlchemy Models (if available)
if SQLALCHEMY_AVAILABLE:
    Base = declarative_base()
    
    class Product(Base):
        __tablename__ = 'products'
        
        id = Column(Integer, primary_key=True, autoincrement=True)
        name = Column(String(200), nullable=False)
        url = Column(Text, unique=True, nullable=False)
        target_price = Column(Float)
        current_price = Column(Float)
        last_checked = Column(DateTime)
        created_at = Column(DateTime, default=datetime.utcnow)
        active = Column(Boolean, default=True)
        
        price_history = relationship("PriceHistory", back_populates="product", cascade="all, delete-orphan")
        alerts = relationship("Alert", back_populates="product", cascade="all, delete-orphan")
    
    class PriceHistory(Base):
        __tablename__ = 'price_history'
        
        id = Column(Integer, primary_key=True, autoincrement=True)
        product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
        price = Column(Float, nullable=False)
        availability = Column(Boolean, default=True)
        timestamp = Column(DateTime, default=datetime.utcnow)
        
        product = relationship("Product", back_populates="price_history")
    
    class Alert(Base):
        __tablename__ = 'alerts'
        
        id = Column(Integer, primary_key=True, autoincrement=True)
        product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
        alert_type = Column(String(50), nullable=False)
        message = Column(Text, nullable=False)
        sent_at = Column(DateTime, default=datetime.utcnow)
        
        product = relationship("Product", back_populates="alerts")


class DatabaseAdapter(ABC):
    """Abstract base class defining the database interface"""
    
    @abstractmethod
    async def connect(self) -> None:
        """Initialize database connection"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Close database connection"""
        pass
    
    @abstractmethod
    async def create_tables(self) -> None:
        """Create database tables if they don't exist"""
        pass
    
    # Product operations
    @abstractmethod
    async def create_product(self, name: str, url: str, target_price: Optional[float] = None) -> int:
        """Create a new product and return its ID"""
        pass
    
    @abstractmethod
    async def get_product(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Get a product by ID"""
        pass
    
    @abstractmethod
    async def get_products(self, active_only: bool = True, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get products with optional filtering and pagination"""
        pass
    
    @abstractmethod
    async def update_product(self, product_id: int, **kwargs) -> bool:
        """Update a product. Returns True if successful"""
        pass
    
    @abstractmethod
    async def delete_product(self, product_id: int) -> bool:
        """Delete a product. Returns True if successful"""
        pass
    
    # Price history operations
    @abstractmethod
    async def add_price_history(self, product_id: int, price: float, availability: bool = True) -> int:
        """Add a price history entry"""
        pass
    
    @abstractmethod
    async def get_price_history(self, product_id: int, days: int = 30, limit: int = 100) -> List[Dict[str, Any]]:
        """Get price history for a product"""
        pass
    
    # Alert operations
    @abstractmethod
    async def create_alert(self, product_id: int, alert_type: str, message: str) -> int:
        """Create a new alert"""
        pass
    
    @abstractmethod
    async def get_alerts(self, days: int = 7, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent alerts"""
        pass
    
    # Analytics and reporting
    @abstractmethod
    async def get_product_statistics(self, product_id: int) -> Dict[str, Any]:
        """Get statistics for a specific product"""
        pass
    
    @abstractmethod
    async def get_summary_stats(self) -> Dict[str, Any]:
        """Get overall summary statistics"""
        pass


class SQLiteAdapter(DatabaseAdapter):
    """SQLite adapter that wraps the existing database.py SQLite operations"""
    
    def __init__(self, database_path: str = "price_data.db"):
        self.database_path = database_path
        self.price_monitor = None
        self._engine = None
        self._session_maker = None
        
    async def connect(self) -> None:
        """Initialize SQLite connection"""
        try:
            if PRICE_MONITOR_AVAILABLE:
                # Use existing PriceMonitor for compatibility
                self.price_monitor = PriceMonitor(self.database_path)
                logger.info(f"SQLite adapter connected using PriceMonitor: {self.database_path}")
            
            if SQLALCHEMY_AVAILABLE:
                # Also setup SQLAlchemy for more advanced operations
                self._engine = create_engine(
                    f"sqlite:///{self.database_path}",
                    poolclass=StaticPool,
                    connect_args={"check_same_thread": False}
                )
                self._session_maker = sessionmaker(autocommit=False, autoflush=False, bind=self._engine)
                logger.info("SQLAlchemy ORM initialized for SQLite")
                
        except Exception as e:
            logger.error(f"Failed to connect to SQLite: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Close SQLite connection"""
        if self._engine:
            self._engine.dispose()
        logger.info("SQLite adapter disconnected")
    
    async def create_tables(self) -> None:
        """Create SQLite tables"""
        if self.price_monitor:
            # Tables are created automatically by PriceMonitor
            pass
        elif SQLALCHEMY_AVAILABLE and self._engine:
            Base.metadata.create_all(bind=self._engine)
        else:
            # Fallback to manual table creation
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Create products table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    url TEXT UNIQUE NOT NULL,
                    target_price REAL,
                    current_price REAL,
                    last_checked TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    active BOOLEAN DEFAULT 1
                )
            ''')
            
            # Create price_history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER,
                    price REAL NOT NULL,
                    availability BOOLEAN,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products (id)
                )
            ''')
            
            # Create alerts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER,
                    alert_type TEXT,
                    message TEXT,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products (id)
                )
            ''')
            
            conn.commit()
            conn.close()
    
    async def create_product(self, name: str, url: str, target_price: Optional[float] = None) -> int:
        """Create a new product"""
        if self.price_monitor:
            return self.price_monitor.add_product(name, url, target_price)
        else:
            # Direct SQLite implementation
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            try:
                cursor.execute(
                    "INSERT INTO products (name, url, target_price) VALUES (?, ?, ?)",
                    (name, url, target_price)
                )
                product_id = cursor.lastrowid
                conn.commit()
                return product_id
            except sqlite3.IntegrityError:
                return None
            finally:
                conn.close()
    
    async def get_product(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Get a product by ID"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT p.*, 
                   COALESCE(h.price_points, 0) as price_points,
                   h.lowest_price,
                   h.highest_price
            FROM products p
            LEFT JOIN (
                SELECT product_id,
                       COUNT(*) as price_points,
                       MIN(price) as lowest_price,
                       MAX(price) as highest_price
                FROM price_history
                WHERE product_id = ?
                GROUP BY product_id
            ) h ON p.id = h.product_id
            WHERE p.id = ?
        ''', (product_id, product_id))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        return None
    
    async def get_products(self, active_only: bool = True, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get products with optional filtering"""
        if self.price_monitor:
            # Use existing PriceMonitor functionality
            report = self.price_monitor.get_summary_report()
            products = []
            
            if not report['products'].empty:
                df = report['products']
                if active_only:
                    df = df[df['active'] == 1]
                
                # Apply pagination
                df = df.iloc[offset:offset+limit]
                
                for _, row in df.iterrows():
                    products.append(row.to_dict())
            
            return products
        else:
            # Direct implementation
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            where_clause = "WHERE p.active = 1" if active_only else ""
            cursor.execute(f'''
                SELECT p.*, 
                       COALESCE(h.price_points, 0) as price_points,
                       h.lowest_price,
                       h.highest_price
                FROM products p
                LEFT JOIN (
                    SELECT product_id,
                           COUNT(*) as price_points,
                           MIN(price) as lowest_price,
                           MAX(price) as highest_price
                    FROM price_history
                    GROUP BY product_id
                ) h ON p.id = h.product_id
                {where_clause}
                ORDER BY p.created_at DESC
                LIMIT ? OFFSET ?
            ''', (limit, offset))
            
            rows = cursor.fetchall()
            conn.close()
            
            products = []
            if rows:
                columns = [desc[0] for desc in cursor.description]
                products = [dict(zip(columns, row)) for row in rows]
            
            return products
    
    async def update_product(self, product_id: int, **kwargs) -> bool:
        """Update a product"""
        if not kwargs:
            return False
            
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        # Build dynamic update query
        set_clauses = []
        values = []
        
        for key, value in kwargs.items():
            if key in ['name', 'target_price', 'current_price', 'active', 'last_checked']:
                set_clauses.append(f"{key} = ?")
                values.append(value)
        
        if not set_clauses:
            conn.close()
            return False
        
        values.append(product_id)
        query = f"UPDATE products SET {', '.join(set_clauses)} WHERE id = ?"
        
        cursor.execute(query, values)
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        return rows_affected > 0
    
    async def delete_product(self, product_id: int) -> bool:
        """Delete a product"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        return rows_affected > 0
    
    async def add_price_history(self, product_id: int, price: float, availability: bool = True) -> int:
        """Add a price history entry"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO price_history (product_id, price, availability) VALUES (?, ?, ?)",
            (product_id, price, availability)
        )
        
        history_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return history_id
    
    async def get_price_history(self, product_id: int, days: int = 30, limit: int = 100) -> List[Dict[str, Any]]:
        """Get price history for a product"""
        if self.price_monitor:
            df = self.price_monitor.get_price_history(product_id, days)
            if df.empty:
                return []
            
            # Convert to list of dicts and apply limit
            return df.head(limit).to_dict('records')
        else:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, price, availability, timestamp
                FROM price_history
                WHERE product_id = ?
                AND timestamp >= datetime('now', '-{} days')
                ORDER BY timestamp DESC
                LIMIT ?
            '''.format(days), (product_id, limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            if rows:
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
            
            return []
    
    async def create_alert(self, product_id: int, alert_type: str, message: str) -> int:
        """Create a new alert"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO alerts (product_id, alert_type, message) VALUES (?, ?, ?)",
            (product_id, alert_type, message)
        )
        
        alert_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return alert_id
    
    async def get_alerts(self, days: int = 7, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent alerts"""
        if self.price_monitor:
            report = self.price_monitor.get_summary_report()
            if not report['recent_alerts'].empty:
                df = report['recent_alerts'].head(limit)
                return df.to_dict('records')
            return []
        else:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT a.id, a.alert_type, a.message, a.sent_at, p.name as product_name
                FROM alerts a
                JOIN products p ON a.product_id = p.id
                WHERE a.sent_at >= datetime('now', '-{} days')
                ORDER BY a.sent_at DESC
                LIMIT ?
            '''.format(days), (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            if rows:
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
            
            return []
    
    async def get_product_statistics(self, product_id: int) -> Dict[str, Any]:
        """Get statistics for a specific product"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as price_points,
                MIN(price) as lowest_price,
                MAX(price) as highest_price,
                AVG(price) as average_price,
                MIN(timestamp) as first_tracked,
                MAX(timestamp) as last_updated
            FROM price_history
            WHERE product_id = ?
        ''', (product_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        
        return {}
    
    async def get_summary_stats(self) -> Dict[str, Any]:
        """Get overall summary statistics"""
        if self.price_monitor:
            report = self.price_monitor.get_summary_report()
            return report.get('summary', {})
        else:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Get basic counts
            cursor.execute('SELECT COUNT(*) FROM products')
            total_products = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM products WHERE active = 1')
            active_products = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM price_history')
            total_price_points = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM alerts WHERE sent_at >= datetime("now", "-7 days")')
            recent_alerts = cursor.fetchone()[0]
            
            cursor.execute('SELECT AVG(current_price) FROM products WHERE current_price IS NOT NULL')
            avg_price = cursor.fetchone()[0] or 0
            
            conn.close()
            
            return {
                'total_products': total_products,
                'active_products': active_products,
                'total_price_points': total_price_points,
                'recent_alerts': recent_alerts,
                'avg_current_price': avg_price
            }


class PostgreSQLAdapter(DatabaseAdapter):
    """PostgreSQL adapter using SQLAlchemy ORM with connection pooling"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.pool: Optional[Pool] = None
        self._engine = None
        self._session_maker = None
        
    async def connect(self) -> None:
        """Initialize PostgreSQL connection with pooling"""
        if not ASYNCPG_AVAILABLE:
            raise RuntimeError("asyncpg is required for PostgreSQL support. Install with: pip install asyncpg")
        
        try:
            # Create connection pool for raw queries
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=5,
                max_size=20,
                command_timeout=60,
                server_settings={
                    'application_name': 'price_monitor_api',
                }
            )
            
            # Also setup SQLAlchemy ORM if available
            if SQLALCHEMY_AVAILABLE:
                # Convert asyncpg URL to SQLAlchemy format if needed
                sync_url = self.database_url.replace('postgresql://', 'postgresql+psycopg2://')
                self._engine = create_engine(
                    sync_url,
                    pool_size=10,
                    max_overflow=20,
                    pool_timeout=30,
                    pool_recycle=3600
                )
                self._session_maker = sessionmaker(autocommit=False, autoflush=False, bind=self._engine)
            
            logger.info("PostgreSQL adapter connected with connection pooling")
            
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Close PostgreSQL connections"""
        if self.pool:
            await self.pool.close()
        if self._engine:
            self._engine.dispose()
        logger.info("PostgreSQL adapter disconnected")
    
    async def create_tables(self) -> None:
        """Create PostgreSQL tables"""
        if SQLALCHEMY_AVAILABLE and self._engine:
            # Use SQLAlchemy to create tables
            Base.metadata.create_all(bind=self._engine)
        else:
            # Fallback to manual table creation
            async with self.pool.acquire() as conn:
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS products (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(200) NOT NULL,
                        url TEXT UNIQUE NOT NULL,
                        target_price DECIMAL(10,2),
                        current_price DECIMAL(10,2),
                        last_checked TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        active BOOLEAN DEFAULT TRUE
                    )
                ''')
                
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS price_history (
                        id SERIAL PRIMARY KEY,
                        product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
                        price DECIMAL(10,2) NOT NULL,
                        availability BOOLEAN DEFAULT TRUE,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS alerts (
                        id SERIAL PRIMARY KEY,
                        product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
                        alert_type VARCHAR(50) NOT NULL,
                        message TEXT NOT NULL,
                        sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create indexes for performance
                await conn.execute('CREATE INDEX IF NOT EXISTS idx_products_active ON products(active)')
                await conn.execute('CREATE INDEX IF NOT EXISTS idx_price_history_product_id ON price_history(product_id)')
                await conn.execute('CREATE INDEX IF NOT EXISTS idx_price_history_timestamp ON price_history(timestamp)')
                await conn.execute('CREATE INDEX IF NOT EXISTS idx_alerts_product_id ON alerts(product_id)')
    
    async def create_product(self, name: str, url: str, target_price: Optional[float] = None) -> int:
        """Create a new product"""
        async with self.pool.acquire() as conn:
            try:
                row = await conn.fetchrow(
                    "INSERT INTO products (name, url, target_price) VALUES ($1, $2, $3) RETURNING id",
                    name, url, target_price
                )
                return row['id']
            except asyncpg.UniqueViolationError:
                return None
    
    async def get_product(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Get a product by ID"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow('''
                SELECT p.*, 
                       COALESCE(h.price_points, 0) as price_points,
                       h.lowest_price,
                       h.highest_price
                FROM products p
                LEFT JOIN (
                    SELECT product_id,
                           COUNT(*) as price_points,
                           MIN(price) as lowest_price,
                           MAX(price) as highest_price
                    FROM price_history
                    WHERE product_id = $1
                    GROUP BY product_id
                ) h ON p.id = h.product_id
                WHERE p.id = $1
            ''', product_id)
            
            return dict(row) if row else None
    
    async def get_products(self, active_only: bool = True, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get products with optional filtering"""
        async with self.pool.acquire() as conn:
            query = '''
                SELECT p.*, 
                       COALESCE(h.price_points, 0) as price_points,
                       h.lowest_price,
                       h.highest_price
                FROM products p
                LEFT JOIN (
                    SELECT product_id,
                           COUNT(*) as price_points,
                           MIN(price) as lowest_price,
                           MAX(price) as highest_price
                    FROM price_history
                    GROUP BY product_id
                ) h ON p.id = h.product_id
                WHERE ($1 = FALSE OR p.active = TRUE)
                ORDER BY p.created_at DESC
                LIMIT $2 OFFSET $3
            '''
            
            rows = await conn.fetch(query, active_only, limit, offset)
            return [dict(row) for row in rows]
    
    async def update_product(self, product_id: int, **kwargs) -> bool:
        """Update a product"""
        if not kwargs:
            return False
        
        # Filter valid fields
        valid_fields = ['name', 'target_price', 'current_price', 'active', 'last_checked']
        updates = {k: v for k, v in kwargs.items() if k in valid_fields}
        
        if not updates:
            return False
        
        # Build dynamic query
        set_clauses = []
        values = []
        param_count = 1
        
        for field, value in updates.items():
            set_clauses.append(f"{field} = ${param_count}")
            values.append(value)
            param_count += 1
        
        values.append(product_id)
        query = f"UPDATE products SET {', '.join(set_clauses)} WHERE id = ${param_count} RETURNING id"
        
        async with self.pool.acquire() as conn:
            result = await conn.fetchrow(query, *values)
            return result is not None
    
    async def delete_product(self, product_id: int) -> bool:
        """Delete a product"""
        async with self.pool.acquire() as conn:
            result = await conn.execute("DELETE FROM products WHERE id = $1", product_id)
            return result == "DELETE 1"
    
    async def add_price_history(self, product_id: int, price: float, availability: bool = True) -> int:
        """Add a price history entry"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "INSERT INTO price_history (product_id, price, availability) VALUES ($1, $2, $3) RETURNING id",
                product_id, price, availability
            )
            return row['id']
    
    async def get_price_history(self, product_id: int, days: int = 30, limit: int = 100) -> List[Dict[str, Any]]:
        """Get price history for a product"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch('''
                SELECT id, price, availability, timestamp
                FROM price_history
                WHERE product_id = $1
                AND timestamp >= NOW() - INTERVAL '%d days'
                ORDER BY timestamp DESC
                LIMIT $2
            ''' % days, product_id, limit)
            
            return [dict(row) for row in rows]
    
    async def create_alert(self, product_id: int, alert_type: str, message: str) -> int:
        """Create a new alert"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "INSERT INTO alerts (product_id, alert_type, message) VALUES ($1, $2, $3) RETURNING id",
                product_id, alert_type, message
            )
            return row['id']
    
    async def get_alerts(self, days: int = 7, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent alerts"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch('''
                SELECT a.id, a.alert_type, a.message, a.sent_at, p.name as product_name
                FROM alerts a
                JOIN products p ON a.product_id = p.id
                WHERE a.sent_at >= NOW() - INTERVAL '%d days'
                ORDER BY a.sent_at DESC
                LIMIT $1
            ''' % days, limit)
            
            return [dict(row) for row in rows]
    
    async def get_product_statistics(self, product_id: int) -> Dict[str, Any]:
        """Get statistics for a specific product"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow('''
                SELECT 
                    COUNT(*) as price_points,
                    MIN(price) as lowest_price,
                    MAX(price) as highest_price,
                    AVG(price) as average_price,
                    MIN(timestamp) as first_tracked,
                    MAX(timestamp) as last_updated
                FROM price_history
                WHERE product_id = $1
            ''', product_id)
            
            return dict(row) if row else {}
    
    async def get_summary_stats(self) -> Dict[str, Any]:
        """Get overall summary statistics"""
        async with self.pool.acquire() as conn:
            # Get basic counts in one query for efficiency
            row = await conn.fetchrow('''
                SELECT 
                    (SELECT COUNT(*) FROM products) as total_products,
                    (SELECT COUNT(*) FROM products WHERE active = TRUE) as active_products,
                    (SELECT COUNT(*) FROM price_history) as total_price_points,
                    (SELECT COUNT(*) FROM alerts WHERE sent_at >= NOW() - INTERVAL '7 days') as recent_alerts,
                    (SELECT AVG(current_price) FROM products WHERE current_price IS NOT NULL) as avg_current_price
            ''')
            
            return dict(row) if row else {}


def get_database_adapter() -> DatabaseAdapter:
    """
    Factory function that returns the appropriate database adapter based on environment variables.
    
    Environment variables:
    - DATABASE_TYPE: 'sqlite' or 'postgresql' (defaults to 'sqlite')
    - DATABASE_URL: Connection string for PostgreSQL
    
    Returns:
        DatabaseAdapter: Appropriate adapter instance
    """
    database_type = os.getenv('DATABASE_TYPE', 'sqlite').lower()
    
    if database_type == 'postgresql':
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            logger.warning("DATABASE_URL not found for PostgreSQL. Falling back to SQLite.")
            return SQLiteAdapter()
        
        if not ASYNCPG_AVAILABLE:
            logger.warning("asyncpg not available for PostgreSQL. Falling back to SQLite.")
            return SQLiteAdapter()
        
        logger.info("Using PostgreSQL adapter")
        return PostgreSQLAdapter(database_url)
    
    else:
        # Default to SQLite
        database_path = os.getenv('SQLITE_DATABASE_PATH', 'price_data.db')
        logger.info(f"Using SQLite adapter: {database_path}")
        return SQLiteAdapter(database_path)


# Context manager for database operations
@asynccontextmanager
async def get_db_connection():
    """Context manager for database connections"""
    adapter = get_database_adapter()
    try:
        await adapter.connect()
        await adapter.create_tables()
        yield adapter
    finally:
        await adapter.disconnect()


# Utility functions for common operations
async def initialize_database():
    """Initialize database with proper tables and indexes"""
    async with get_db_connection() as db:
        await db.create_tables()
        logger.info("Database initialized successfully")


async def migrate_sqlite_to_postgresql(sqlite_path: str, postgresql_url: str):
    """
    Utility function to migrate data from SQLite to PostgreSQL.
    Useful when upgrading from development to production.
    """
    if not ASYNCPG_AVAILABLE:
        raise RuntimeError("asyncpg is required for PostgreSQL migration")
    
    # Create adapters
    sqlite_adapter = SQLiteAdapter(sqlite_path)
    postgres_adapter = PostgreSQLAdapter(postgresql_url)
    
    try:
        # Connect to both databases
        await sqlite_adapter.connect()
        await postgres_adapter.connect()
        await postgres_adapter.create_tables()
        
        # Migrate products
        products = await sqlite_adapter.get_products(active_only=False, limit=10000)
        logger.info(f"Migrating {len(products)} products...")
        
        product_id_mapping = {}
        for product in products:
            old_id = product['id']
            new_id = await postgres_adapter.create_product(
                product['name'],
                product['url'],
                product.get('target_price')
            )
            if new_id:
                product_id_mapping[old_id] = new_id
                
                # Update additional fields
                await postgres_adapter.update_product(
                    new_id,
                    current_price=product.get('current_price'),
                    last_checked=product.get('last_checked'),
                    active=product.get('active', True)
                )
        
        # Migrate price history
        logger.info("Migrating price history...")
        for old_id, new_id in product_id_mapping.items():
            history = await sqlite_adapter.get_price_history(old_id, days=365, limit=10000)
            for entry in history:
                await postgres_adapter.add_price_history(
                    new_id,
                    entry['price'],
                    entry.get('availability', True)
                )
        
        # Migrate alerts
        logger.info("Migrating alerts...")
        alerts = await sqlite_adapter.get_alerts(days=365, limit=10000)
        for alert in alerts:
            old_product_id = alert.get('product_id')
            if old_product_id in product_id_mapping:
                new_product_id = product_id_mapping[old_product_id]
                await postgres_adapter.create_alert(
                    new_product_id,
                    alert['alert_type'],
                    alert['message']
                )
        
        logger.info("Migration completed successfully!")
        
    finally:
        await sqlite_adapter.disconnect()
        await postgres_adapter.disconnect()

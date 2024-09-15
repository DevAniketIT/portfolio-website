# Price Monitor REST API with FastAPI
# Professional API for price monitoring system with PostgreSQL support

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import asyncio
import asyncpg
import json
from datetime import datetime, timedelta
import os
from contextlib import asynccontextmanager
import logging
from price_monitor_system import PriceMonitor  # Import our existing system

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic Models for API
class ProductCreate(BaseModel):
    name: str = Field(..., description="Product name", max_length=200)
    url: str = Field(..., description="Product URL")
    target_price: Optional[float] = Field(None, description="Target price for alerts", gt=0)

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    target_price: Optional[float] = Field(None, gt=0)
    active: Optional[bool] = None

class ProductResponse(BaseModel):
    id: int
    name: str
    url: str
    target_price: Optional[float]
    current_price: Optional[float]
    last_checked: Optional[datetime]
    created_at: datetime
    active: bool
    price_points: Optional[int] = 0
    lowest_price: Optional[float]
    highest_price: Optional[float]

class PriceHistoryResponse(BaseModel):
    id: int
    price: float
    availability: bool
    timestamp: datetime

class AlertResponse(BaseModel):
    id: int
    alert_type: str
    message: str
    sent_at: datetime
    product_name: str

class PriceCheckRequest(BaseModel):
    product_ids: Optional[List[int]] = Field(None, description="Specific product IDs to check. If empty, checks all active products")

# Database connection management
class Database:
    def __init__(self):
        self.pool = None
        # Try PostgreSQL first, fallback to SQLite
        self.use_postgres = os.getenv("DATABASE_URL") is not None
        self.sqlite_monitor = PriceMonitor() if not self.use_postgres else None
    
    async def init_postgres(self):
        """Initialize PostgreSQL connection pool"""
        try:
            database_url = os.getenv("DATABASE_URL")
            if not database_url:
                raise ValueError("DATABASE_URL not found")
            
            self.pool = await asyncpg.create_pool(database_url)
            await self.create_postgres_tables()
            logger.info("PostgreSQL connected successfully")
            
        except Exception as e:
            logger.error(f"PostgreSQL connection failed: {e}")
            logger.info("Falling back to SQLite")
            self.use_postgres = False
            self.sqlite_monitor = PriceMonitor()
    
    async def create_postgres_tables(self):
        """Create PostgreSQL tables"""
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
            
            # Create indexes for better performance
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_products_active ON products(active)')
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_price_history_product_id ON price_history(product_id)')
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_price_history_timestamp ON price_history(timestamp)')
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_alerts_product_id ON alerts(product_id)')

    async def close(self):
        """Close database connections"""
        if self.use_postgres and self.pool:
            await self.pool.close()

# Initialize database
db = Database()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    if os.getenv("DATABASE_URL"):
        await db.init_postgres()
    yield
    # Shutdown
    await db.close()

# Initialize FastAPI with lifespan
app = FastAPI(
    title="Price Monitor API",
    description="Professional price monitoring system with multi-platform support",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database dependency
async def get_db():
    if db.use_postgres:
        async with db.pool.acquire() as conn:
            yield conn
    else:
        yield db.sqlite_monitor

# API Endpoints

@app.get("/", response_model=Dict[str, Any])
async def root():
    """API health check and information"""
    return {
        "message": "Price Monitor API",
        "version": "1.0.0",
        "database": "PostgreSQL" if db.use_postgres else "SQLite",
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/products", response_model=List[ProductResponse])
async def get_products(
    active_only: bool = True,
    limit: int = Field(100, le=1000),
    offset: int = Field(0, ge=0),
    db_conn=Depends(get_db)
):
    """Get all monitored products"""
    try:
        if db.use_postgres:
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
            rows = await db_conn.fetch(query, active_only, limit, offset)
            
            products = []
            for row in rows:
                products.append(ProductResponse(
                    id=row['id'],
                    name=row['name'],
                    url=row['url'],
                    target_price=float(row['target_price']) if row['target_price'] else None,
                    current_price=float(row['current_price']) if row['current_price'] else None,
                    last_checked=row['last_checked'],
                    created_at=row['created_at'],
                    active=row['active'],
                    price_points=row['price_points'],
                    lowest_price=float(row['lowest_price']) if row['lowest_price'] else None,
                    highest_price=float(row['highest_price']) if row['highest_price'] else None
                ))
            return products
        
        else:
            # SQLite fallback
            report = db_conn.get_summary_report()
            products = []
            
            if not report['products'].empty:
                for _, product in report['products'].iterrows():
                    products.append(ProductResponse(
                        id=int(product['id']),
                        name=product['name'],
                        url=product['url'],
                        target_price=float(product['target_price']) if pd.notna(product['target_price']) else None,
                        current_price=float(product['current_price']) if pd.notna(product['current_price']) else None,
                        last_checked=pd.to_datetime(product['last_checked']) if pd.notna(product['last_checked']) else None,
                        created_at=pd.to_datetime(product['created_at']),
                        active=bool(product['active']),
                        price_points=int(product['price_points']) if pd.notna(product['price_points']) else 0,
                        lowest_price=float(product['lowest_price']) if pd.notna(product['lowest_price']) else None,
                        highest_price=float(product['highest_price']) if pd.notna(product['highest_price']) else None
                    ))
            
            # Apply filters
            if active_only:
                products = [p for p in products if p.active]
            
            return products[offset:offset+limit]
            
    except Exception as e:
        logger.error(f"Error getting products: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve products")

@app.post("/products", response_model=ProductResponse)
async def create_product(
    product: ProductCreate,
    background_tasks: BackgroundTasks,
    db_conn=Depends(get_db)
):
    """Add a new product to monitor"""
    try:
        if db.use_postgres:
            query = '''
                INSERT INTO products (name, url, target_price)
                VALUES ($1, $2, $3)
                RETURNING id, name, url, target_price, current_price, last_checked, created_at, active
            '''
            row = await db_conn.fetchrow(query, product.name, product.url, product.target_price)
            
            product_response = ProductResponse(
                id=row['id'],
                name=row['name'],
                url=row['url'],
                target_price=float(row['target_price']) if row['target_price'] else None,
                current_price=float(row['current_price']) if row['current_price'] else None,
                last_checked=row['last_checked'],
                created_at=row['created_at'],
                active=row['active'],
                price_points=0,
                lowest_price=None,
                highest_price=None
            )
            
            # Schedule initial price check
            background_tasks.add_task(check_single_product_postgres, row['id'])
            
        else:
            # SQLite fallback
            product_id = db_conn.add_product(product.name, product.url, product.target_price)
            if not product_id:
                raise HTTPException(status_code=400, detail="Product URL already exists")
            
            # Get the created product details
            import sqlite3
            conn = sqlite3.connect(db_conn.database_path)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
            row = cursor.fetchone()
            conn.close()
            
            product_response = ProductResponse(
                id=row[0],
                name=row[1],
                url=row[2],
                target_price=row[3],
                current_price=row[4],
                last_checked=pd.to_datetime(row[5]) if row[5] else None,
                created_at=pd.to_datetime(row[6]),
                active=bool(row[7]),
                price_points=0,
                lowest_price=None,
                highest_price=None
            )
        
        return product_response
        
    except asyncpg.UniqueViolationError:
        raise HTTPException(status_code=400, detail="Product URL already exists")
    except Exception as e:
        logger.error(f"Error creating product: {e}")
        raise HTTPException(status_code=500, detail="Failed to create product")

@app.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db_conn=Depends(get_db)):
    """Get a specific product by ID"""
    try:
        if db.use_postgres:
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
                    WHERE product_id = $1
                    GROUP BY product_id
                ) h ON p.id = h.product_id
                WHERE p.id = $1
            '''
            row = await db_conn.fetchrow(query, product_id)
            
            if not row:
                raise HTTPException(status_code=404, detail="Product not found")
            
            return ProductResponse(
                id=row['id'],
                name=row['name'],
                url=row['url'],
                target_price=float(row['target_price']) if row['target_price'] else None,
                current_price=float(row['current_price']) if row['current_price'] else None,
                last_checked=row['last_checked'],
                created_at=row['created_at'],
                active=row['active'],
                price_points=row['price_points'],
                lowest_price=float(row['lowest_price']) if row['lowest_price'] else None,
                highest_price=float(row['highest_price']) if row['highest_price'] else None
            )
        else:
            # SQLite fallback - implement similar logic
            raise HTTPException(status_code=501, detail="SQLite implementation needed")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting product {product_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve product")

@app.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db_conn=Depends(get_db)
):
    """Update a product"""
    try:
        if db.use_postgres:
            # Build dynamic update query
            fields = []
            values = []
            param_count = 1
            
            if product_update.name is not None:
                fields.append(f"name = ${param_count}")
                values.append(product_update.name)
                param_count += 1
            
            if product_update.target_price is not None:
                fields.append(f"target_price = ${param_count}")
                values.append(product_update.target_price)
                param_count += 1
            
            if product_update.active is not None:
                fields.append(f"active = ${param_count}")
                values.append(product_update.active)
                param_count += 1
            
            if not fields:
                raise HTTPException(status_code=400, detail="No fields to update")
            
            values.append(product_id)  # For WHERE clause
            query = f'''
                UPDATE products 
                SET {", ".join(fields)}
                WHERE id = ${param_count}
                RETURNING id, name, url, target_price, current_price, last_checked, created_at, active
            '''
            
            row = await db_conn.fetchrow(query, *values)
            
            if not row:
                raise HTTPException(status_code=404, detail="Product not found")
            
            return ProductResponse(
                id=row['id'],
                name=row['name'],
                url=row['url'],
                target_price=float(row['target_price']) if row['target_price'] else None,
                current_price=float(row['current_price']) if row['current_price'] else None,
                last_checked=row['last_checked'],
                created_at=row['created_at'],
                active=row['active']
            )
        else:
            # SQLite fallback
            raise HTTPException(status_code=501, detail="SQLite implementation needed")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating product {product_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update product")

@app.delete("/products/{product_id}")
async def delete_product(product_id: int, db_conn=Depends(get_db)):
    """Delete a product"""
    try:
        if db.use_postgres:
            result = await db_conn.execute("DELETE FROM products WHERE id = $1", product_id)
            if result == "DELETE 0":
                raise HTTPException(status_code=404, detail="Product not found")
            return {"message": "Product deleted successfully"}
        else:
            # SQLite fallback
            raise HTTPException(status_code=501, detail="SQLite implementation needed")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting product {product_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete product")

@app.get("/products/{product_id}/price-history", response_model=List[PriceHistoryResponse])
async def get_price_history(
    product_id: int,
    days: int = Field(30, ge=1, le=365),
    limit: int = Field(100, ge=1, le=1000),
    db_conn=Depends(get_db)
):
    """Get price history for a product"""
    try:
        if db.use_postgres:
            query = '''
                SELECT id, price, availability, timestamp
                FROM price_history
                WHERE product_id = $1
                AND timestamp >= NOW() - INTERVAL '%d days'
                ORDER BY timestamp DESC
                LIMIT $2
            ''' % days
            
            rows = await db_conn.fetch(query, product_id, limit)
            
            return [
                PriceHistoryResponse(
                    id=row['id'],
                    price=float(row['price']),
                    availability=row['availability'],
                    timestamp=row['timestamp']
                )
                for row in rows
            ]
        else:
            # SQLite fallback
            df = db_conn.get_price_history(product_id, days)
            if df.empty:
                return []
            
            history = []
            for _, row in df.head(limit).iterrows():
                history.append(PriceHistoryResponse(
                    id=0,  # SQLite doesn't have ID in price history
                    price=float(row['price']),
                    availability=bool(row['availability']),
                    timestamp=pd.to_datetime(row['timestamp'])
                ))
            return history
            
    except Exception as e:
        logger.error(f"Error getting price history for product {product_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve price history")

@app.post("/track")
async def trigger_price_check(
    request: PriceCheckRequest = PriceCheckRequest(),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db_conn=Depends(get_db)
):
    """Trigger price check for specific products or all active products"""
    try:
        if request.product_ids:
            # Check specific products
            if db.use_postgres:
                for product_id in request.product_ids:
                    background_tasks.add_task(check_single_product_postgres, product_id)
            else:
                for product_id in request.product_ids:
                    background_tasks.add_task(db_conn.check_single_product, product_id)
            
            message = f"Price check triggered for {len(request.product_ids)} products"
        else:
            # Check all active products
            if db.use_postgres:
                background_tasks.add_task(check_all_products_postgres)
            else:
                background_tasks.add_task(db_conn.check_all_products)
            
            message = "Price check triggered for all active products"
        
        return {
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "scheduled"
        }
        
    except Exception as e:
        logger.error(f"Error triggering price check: {e}")
        raise HTTPException(status_code=500, detail="Failed to trigger price check")

@app.get("/alerts", response_model=List[AlertResponse])
async def get_recent_alerts(
    days: int = Field(7, ge=1, le=30),
    limit: int = Field(50, ge=1, le=200),
    db_conn=Depends(get_db)
):
    """Get recent price alerts"""
    try:
        if db.use_postgres:
            query = '''
                SELECT a.id, a.alert_type, a.message, a.sent_at, p.name as product_name
                FROM alerts a
                JOIN products p ON a.product_id = p.id
                WHERE a.sent_at >= NOW() - INTERVAL '%d days'
                ORDER BY a.sent_at DESC
                LIMIT $1
            ''' % days
            
            rows = await db_conn.fetch(query, limit)
            
            return [
                AlertResponse(
                    id=row['id'],
                    alert_type=row['alert_type'],
                    message=row['message'],
                    sent_at=row['sent_at'],
                    product_name=row['product_name']
                )
                for row in rows
            ]
        else:
            # SQLite fallback
            report = db_conn.get_summary_report()
            alerts = []
            
            if not report['recent_alerts'].empty:
                for _, alert in report['recent_alerts'].head(limit).iterrows():
                    alerts.append(AlertResponse(
                        id=int(alert['id']),
                        alert_type=alert['alert_type'],
                        message=alert['message'],
                        sent_at=pd.to_datetime(alert['sent_at']),
                        product_name=alert['product_name']
                    ))
            
            return alerts
            
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve alerts")

# Background task functions for PostgreSQL
async def check_single_product_postgres(product_id: int):
    """Background task to check a single product price with PostgreSQL"""
    try:
        # This would use the PostgreSQL connection to check prices
        # For now, we'll use the existing PriceMonitor as a fallback
        monitor = PriceMonitor()
        monitor.check_single_product(product_id)
        logger.info(f"Price check completed for product {product_id}")
    except Exception as e:
        logger.error(f"Error in background price check for product {product_id}: {e}")

async def check_all_products_postgres():
    """Background task to check all active products with PostgreSQL"""
    try:
        monitor = PriceMonitor()
        monitor.check_all_products()
        logger.info("Price check completed for all products")
    except Exception as e:
        logger.error(f"Error in background price check for all products: {e}")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint for monitoring"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "database": {
            "type": "PostgreSQL" if db.use_postgres else "SQLite",
            "connected": False
        },
        "services": {
            "api": "operational",
            "price_monitoring": "operational"
        },
        "metrics": {
            "uptime_seconds": 0,
            "active_products": 0,
            "last_price_check": None
        }
    }
    
    try:
        # Test database connection
        if db.use_postgres and db.pool:
            async with db.pool.acquire() as conn:
                # Simple query to test connection
                await conn.fetchval("SELECT 1")
                health_status["database"]["connected"] = True
                
                # Get metrics from database
                active_count = await conn.fetchval(
                    "SELECT COUNT(*) FROM products WHERE active = TRUE"
                )
                health_status["metrics"]["active_products"] = active_count
                
                # Get last price check time
                last_check = await conn.fetchval(
                    "SELECT MAX(timestamp) FROM price_history"
                )
                if last_check:
                    health_status["metrics"]["last_price_check"] = last_check.isoformat()
                    
        elif not db.use_postgres and db.sqlite_monitor:
            # SQLite health check
            health_status["database"]["connected"] = True
            # Add SQLite metrics if needed
            
    except Exception as e:
        logger.error(f"Health check database error: {e}")
        health_status["status"] = "degraded"
        health_status["database"]["connected"] = False
        health_status["services"]["price_monitoring"] = "degraded"
    
    # Set overall status based on critical components
    if not health_status["database"]["connected"]:
        health_status["status"] = "unhealthy"
    
    return health_status


# Additional monitoring endpoints
@app.get("/metrics")
async def get_metrics():
    """Detailed metrics endpoint for monitoring systems"""
    try:
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "database_type": "PostgreSQL" if db.use_postgres else "SQLite",
            "products": {
                "total": 0,
                "active": 0,
                "inactive": 0
            },
            "price_checks": {
                "total_today": 0,
                "successful_today": 0,
                "failed_today": 0,
                "last_check": None
            },
            "alerts": {
                "total_today": 0,
                "price_drops": 0,
                "availability_changes": 0
            }
        }
        
        if db.use_postgres and db.pool:
            async with db.pool.acquire() as conn:
                # Product metrics
                total_products = await conn.fetchval("SELECT COUNT(*) FROM products")
                active_products = await conn.fetchval(
                    "SELECT COUNT(*) FROM products WHERE active = TRUE"
                )
                
                metrics["products"]["total"] = total_products
                metrics["products"]["active"] = active_products
                metrics["products"]["inactive"] = total_products - active_products
                
                # Price check metrics for today
                today = datetime.utcnow().date()
                price_checks_today = await conn.fetchval(
                    "SELECT COUNT(*) FROM price_history WHERE timestamp::date = $1",
                    today
                )
                metrics["price_checks"]["total_today"] = price_checks_today
                
                # Last price check
                last_check = await conn.fetchval(
                    "SELECT MAX(timestamp) FROM price_history"
                )
                if last_check:
                    metrics["price_checks"]["last_check"] = last_check.isoformat()
                
                # Alert metrics for today
                alerts_today = await conn.fetchval(
                    "SELECT COUNT(*) FROM alerts WHERE sent_at::date = $1",
                    today
                )
                metrics["alerts"]["total_today"] = alerts_today
        
        return metrics
        
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve metrics")

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "price_monitor_api:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )

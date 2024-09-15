"""
Example usage of the Database Adapter

This example demonstrates how to use the database abstraction layer
with both SQLite and PostgreSQL backends.
"""

import asyncio
import os
from database_adapter import get_database_adapter, get_db_connection, initialize_database

async def main():
    """Example of using the database adapter"""
    
    # Set environment variables for this example
    # For SQLite (default)
    os.environ['DATABASE_TYPE'] = 'sqlite'
    os.environ['SQLITE_DATABASE_PATH'] = 'example_price_data.db'
    
    # For PostgreSQL (uncomment to test PostgreSQL)
    # os.environ['DATABASE_TYPE'] = 'postgresql'  
    # os.environ['DATABASE_URL'] = 'postgresql://user:password@localhost:5432/price_monitor'
    
    print("🗄️  Database Adapter Example")
    print("=" * 40)
    
    try:
        # Method 1: Using context manager (recommended)
        print("\n📊 Using context manager approach:")
        async with get_db_connection() as db:
            print(f"Connected to database: {type(db).__name__}")
            
            # Create a sample product
            product_id = await db.create_product(
                name="iPhone 15 Pro",
                url="https://example.com/iphone-15-pro",
                target_price=999.99
            )
            
            if product_id:
                print(f"✅ Created product with ID: {product_id}")
                
                # Add some price history
                await db.add_price_history(product_id, 1199.99, True)
                await db.add_price_history(product_id, 1149.99, True)
                await db.add_price_history(product_id, 1099.99, True)
                print("📈 Added price history entries")
                
                # Get product details
                product = await db.get_product(product_id)
                if product:
                    print(f"📦 Product: {product['name']}")
                    print(f"💰 Current Price: ${product.get('current_price', 'N/A')}")
                    print(f"🎯 Target Price: ${product.get('target_price', 'N/A')}")
                
                # Get price history
                history = await db.get_price_history(product_id, days=30)
                print(f"📊 Price history entries: {len(history)}")
                
                # Create an alert
                alert_id = await db.create_alert(
                    product_id, 
                    "price_drop", 
                    "Price dropped below $1150!"
                )
                print(f"🚨 Created alert with ID: {alert_id}")
                
                # Update product
                success = await db.update_product(
                    product_id, 
                    current_price=1049.99,
                    active=True
                )
                print(f"🔄 Updated product: {'✅' if success else '❌'}")
                
                # Get statistics
                stats = await db.get_product_statistics(product_id)
                print(f"📈 Product Statistics:")
                print(f"  - Price points: {stats.get('price_points', 0)}")
                print(f"  - Lowest price: ${stats.get('lowest_price', 'N/A')}")
                print(f"  - Highest price: ${stats.get('highest_price', 'N/A')}")
        
        # Method 2: Manual adapter management
        print("\n🔧 Using manual adapter management:")
        adapter = get_database_adapter()
        await adapter.connect()
        await adapter.create_tables()
        
        try:
            # Get all products
            products = await adapter.get_products(active_only=True, limit=10)
            print(f"📦 Found {len(products)} active products")
            
            # Get summary statistics
            summary = await adapter.get_summary_stats()
            print(f"📊 Summary Statistics:")
            print(f"  - Total products: {summary.get('total_products', 0)}")
            print(f"  - Active products: {summary.get('active_products', 0)}")
            print(f"  - Total price points: {summary.get('total_price_points', 0)}")
            print(f"  - Recent alerts: {summary.get('recent_alerts', 0)}")
            
            # Get recent alerts
            alerts = await adapter.get_alerts(days=7)
            print(f"🚨 Recent alerts: {len(alerts)}")
            for alert in alerts:
                print(f"  - {alert['alert_type']}: {alert['message']}")
                
        finally:
            await adapter.disconnect()
        
        print("\n✅ Database adapter example completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

async def test_migration_example():
    """Example of migrating from SQLite to PostgreSQL"""
    print("\n🔄 Migration Example")
    print("=" * 30)
    
    # This is just a demo - don't run unless you have PostgreSQL set up
    sqlite_path = "example_price_data.db"
    postgresql_url = "postgresql://user:password@localhost:5432/price_monitor_test"
    
    print(f"Migration from {sqlite_path} to PostgreSQL would:")
    print("1. Connect to both databases")
    print("2. Create tables in PostgreSQL") 
    print("3. Migrate all products")
    print("4. Migrate price history")
    print("5. Migrate alerts")
    print("6. Update foreign key relationships")
    
    # Uncomment to actually run migration (requires PostgreSQL setup)
    # from database_adapter import migrate_sqlite_to_postgresql
    # await migrate_sqlite_to_postgresql(sqlite_path, postgresql_url)

async def performance_test():
    """Simple performance test of the database adapter"""
    print("\n⚡ Performance Test")
    print("=" * 25)
    
    import time
    
    async with get_db_connection() as db:
        # Test bulk operations
        start_time = time.time()
        
        # Create multiple products
        product_ids = []
        for i in range(10):
            product_id = await db.create_product(
                name=f"Test Product {i}",
                url=f"https://example.com/product-{i}",
                target_price=100.0 + i
            )
            if product_id:
                product_ids.append(product_id)
        
        creation_time = time.time() - start_time
        print(f"📦 Created {len(product_ids)} products in {creation_time:.2f}s")
        
        # Add price history for each
        start_time = time.time()
        for product_id in product_ids:
            for j in range(5):
                await db.add_price_history(
                    product_id, 
                    100.0 + j, 
                    True
                )
        
        history_time = time.time() - start_time
        print(f"📊 Added price history in {history_time:.2f}s")
        
        # Read operations
        start_time = time.time()
        products = await db.get_products(limit=100)
        read_time = time.time() - start_time
        print(f"📖 Read {len(products)} products in {read_time:.2f}s")
        
        total_time = creation_time + history_time + read_time
        print(f"⚡ Total test time: {total_time:.2f}s")

if __name__ == "__main__":
    print("🚀 Database Adapter Examples")
    print("=" * 50)
    
    # Run main example
    asyncio.run(main())
    
    # Run migration example (demo only)
    asyncio.run(test_migration_example())
    
    # Run performance test
    asyncio.run(performance_test())
    
    print("\n🎉 All examples completed!")
    print("\nTo use in production:")
    print("1. Set DATABASE_TYPE=postgresql in your .env file")
    print("2. Set DATABASE_URL to your PostgreSQL connection string") 
    print("3. Install required dependencies: pip install asyncpg sqlalchemy")
    print("4. Use get_database_adapter() in your API endpoints")

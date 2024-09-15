# Day 3: Functions and Dictionaries + File Organizer Project
# Advanced structures and automation project

import os
import shutil
from datetime import datetime
from pathlib import Path

print("=== Day 3: Functions and Dictionaries ===\n")

# 1. FUNCTIONS - Building reusable code blocks
print("=== Functions ===")

def calculate_discount(original_price, discount_percent):
    """Calculate discounted price - useful for price comparison"""
    if not isinstance(original_price, (int, float)) or original_price < 0:
        return None
    if not isinstance(discount_percent, (int, float)) or discount_percent < 0 or discount_percent > 100:
        return None
    
    return original_price * (1 - discount_percent / 100)

def format_currency(amount):
    """Format number as currency"""
    return f"${amount:.2f}"

def analyze_price_trend(prices):
    """Analyze price trend from a list of prices"""
    if len(prices) < 2:
        return "Insufficient data"
    
    increasing = sum(1 for i in range(1, len(prices)) if prices[i] > prices[i-1])
    decreasing = sum(1 for i in range(1, len(prices)) if prices[i] < prices[i-1])
    
    if increasing > decreasing:
        return "📈 Trending UP"
    elif decreasing > increasing:
        return "📉 Trending DOWN"
    else:
        return "➡️ Stable"

# Test functions
test_price = 999.99
test_discount = 15
discounted = calculate_discount(test_price, test_discount)
print(f"Original: {format_currency(test_price)}")
print(f"Discount: {test_discount}%")
print(f"Sale Price: {format_currency(discounted)}")

test_prices = [1000, 950, 900, 920, 880, 860]
trend = analyze_price_trend(test_prices)
print(f"Price trend: {trend}")

# 2. DICTIONARIES - Perfect for structured scraped data
print("\n=== Dictionaries ===")

# Product information (like scraped data structure)
product_catalog = {
    "smartphones": {
        "iphone_15": {
            "name": "iPhone 15",
            "brand": "Apple",
            "price": 999.99,
            "specs": {
                "storage": "128GB",
                "color": "Blue",
                "screen": "6.1 inch"
            },
            "availability": True,
            "reviews": {"rating": 4.5, "count": 1250}
        },
        "galaxy_s24": {
            "name": "Galaxy S24",
            "brand": "Samsung",
            "price": 899.99,
            "specs": {
                "storage": "256GB",
                "color": "Black",
                "screen": "6.2 inch"
            },
            "availability": False,
            "reviews": {"rating": 4.3, "count": 890}
        }
    }
}

# Accessing nested dictionary data
for category, products in product_catalog.items():
    print(f"\n📱 Category: {category.title()}")
    for product_id, product_info in products.items():
        name = product_info["name"]
        price = format_currency(product_info["price"])
        rating = product_info["reviews"]["rating"]
        availability = "✅ Available" if product_info["availability"] else "❌ Out of Stock"
        
        print(f"  • {name}: {price} - ⭐{rating} - {availability}")

# Dictionary methods
print("\n=== Dictionary Operations ===")
sample_product = product_catalog["smartphones"]["iphone_15"]

print("Keys:", list(sample_product.keys()))
print("Has 'price' key:", "price" in sample_product)
print("Get color:", sample_product["specs"].get("color", "Unknown"))

# 3. ADVANCED FUNCTIONS
print("\n=== Advanced Functions ===")

def process_product_data(products_dict, min_rating=0, max_price=float('inf')):
    """Process and filter product data"""
    filtered_products = []
    
    for category, products in products_dict.items():
        for product_id, product_info in products.items():
            rating = product_info["reviews"]["rating"]
            price = product_info["price"]
            
            if rating >= min_rating and price <= max_price:
                filtered_products.append({
                    "id": product_id,
                    "name": product_info["name"],
                    "price": price,
                    "rating": rating,
                    "category": category
                })
    
    return filtered_products

# Filter products
affordable_phones = process_product_data(product_catalog, min_rating=4.0, max_price=950)
print("Affordable phones with good ratings:")
for product in affordable_phones:
    print(f"  • {product['name']}: {format_currency(product['price'])} - ⭐{product['rating']}")

print("\n" + "="*50)
print("🚀 AUTOMATION PROJECT: FILE ORGANIZER")
print("="*50)

# 4. FILE ORGANIZER PROJECT
class FileOrganizer:
    """Organize files in Downloads folder by type and date"""
    
    def __init__(self, source_folder=None):
        if source_folder is None:
            # Default to Downloads folder
            self.source_folder = Path.home() / "Downloads"
        else:
            self.source_folder = Path(source_folder)
        
        self.file_categories = {
            "Documents": ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt'],
            "Images": ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg'],
            "Videos": ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv'],
            "Audio": ['.mp3', '.wav', '.flac', '.aac', '.ogg'],
            "Archives": ['.zip', '.rar', '.7z', '.tar', '.gz'],
            "Executables": ['.exe', '.msi', '.dmg', '.deb', '.rpm'],
            "Spreadsheets": ['.xls', '.xlsx', '.csv', '.ods'],
            "Code": ['.py', '.js', '.html', '.css', '.cpp', '.java', '.go']
        }
    
    def get_file_category(self, file_path):
        """Determine file category based on extension"""
        extension = file_path.suffix.lower()
        
        for category, extensions in self.file_categories.items():
            if extension in extensions:
                return category
        
        return "Others"
    
    def create_organized_structure(self, dry_run=True):
        """Create organized folder structure"""
        results = {
            "processed": 0,
            "moved": 0,
            "skipped": 0,
            "categories": {}
        }
        
        if not self.source_folder.exists():
            return {"error": f"Source folder does not exist: {self.source_folder}"}
        
        # Create organized folder
        organized_folder = self.source_folder / "Organized"
        
        if not dry_run and not organized_folder.exists():
            organized_folder.mkdir(exist_ok=True)
        
        # Process files
        for file_path in self.source_folder.iterdir():
            if file_path.is_file() and file_path.name != ".DS_Store":
                results["processed"] += 1
                
                category = self.get_file_category(file_path)
                
                if category not in results["categories"]:
                    results["categories"][category] = []
                
                results["categories"][category].append(file_path.name)
                
                if not dry_run:
                    # Create category folder
                    category_folder = organized_folder / category
                    category_folder.mkdir(exist_ok=True)
                    
                    # Create date subfolder
                    file_date = datetime.fromtimestamp(file_path.stat().st_mtime)
                    date_folder = category_folder / file_date.strftime("%Y-%m")
                    date_folder.mkdir(exist_ok=True)
                    
                    # Move file
                    destination = date_folder / file_path.name
                    try:
                        shutil.move(str(file_path), str(destination))
                        results["moved"] += 1
                    except Exception as e:
                        results["skipped"] += 1
                        print(f"Error moving {file_path.name}: {e}")
                else:
                    results["moved"] += 1
        
        return results

def demo_file_organizer():
    """Demo the file organizer (dry run)"""
    print("📁 File Organizer Demo")
    
    # Create a demo folder structure for testing
    demo_folder = Path("demo_downloads")
    
    if not demo_folder.exists():
        demo_folder.mkdir(exist_ok=True)
        
        # Create sample files
        sample_files = [
            "report.pdf", "photo.jpg", "music.mp3", "video.mp4",
            "data.csv", "script.py", "archive.zip", "document.docx"
        ]
        
        for filename in sample_files:
            (demo_folder / filename).touch()
        
        print(f"Created demo folder with {len(sample_files)} sample files")
    
    # Run organizer in dry-run mode
    organizer = FileOrganizer(demo_folder)
    results = organizer.create_organized_structure(dry_run=True)
    
    print(f"\n📊 Organization Results (Dry Run):")
    print(f"Files processed: {results['processed']}")
    print(f"Files to be moved: {results['moved']}")
    print(f"Files skipped: {results['skipped']}")
    
    print(f"\n📂 Files by category:")
    for category, files in results["categories"].items():
        print(f"  {category}: {len(files)} files")
        for file in files[:3]:  # Show first 3 files
            print(f"    • {file}")
        if len(files) > 3:
            print(f"    ... and {len(files) - 3} more")
    
    # Clean up demo folder
    shutil.rmtree(demo_folder, ignore_errors=True)

if __name__ == "__main__":
    # Run the demo
    demo_file_organizer()
    
    print("\n✅ Day 3 Complete! You've built a real automation tool!")
    print("📚 HackerRank Focus: Functions, dictionaries, string manipulation")
    print("🎯 Next: Web Scraping with requests and BeautifulSoup")
    
    print(f"\n💡 To use the real file organizer on your Downloads folder:")
    print(f"organizer = FileOrganizer()")
    print(f"results = organizer.create_organized_structure(dry_run=False)")

# Day 2: Lists, Loops, and Control Flow
# Essential structures for data processing and web scraping

print("=== Day 2: Lists, Loops, and Control Flow ===\n")

# 1. LISTS - Core data structure for scraped data
print("=== Working with Lists ===")

# Creating lists (like scraped product data)
products = ["iPhone 15", "Galaxy S24", "Pixel 8", "OnePlus 12"]
prices = [999.99, 899.99, 699.99, 799.99]
in_stock = [True, False, True, True]

print(f"Products: {products}")
print(f"Prices: {prices}")
print(f"Stock Status: {in_stock}")

# List operations
products.append("Xiaomi 14")  # Adding new scraped item
print(f"After adding item: {products}")

# Accessing elements
print(f"First product: {products[0]}")
print(f"Last product: {products[-1]}")
print(f"Product count: {len(products)}")

# List slicing (useful for pagination)
print(f"First 3 products: {products[:3]}")
print(f"Last 2 products: {products[-2:]}")

# 2. LOOPS - Essential for processing scraped data
print("\n=== For Loops ===")

# Basic for loop
print("All products:")
for i, product in enumerate(products):
    if i < len(prices):
        print(f"{i+1}. {product} - ${prices[i]}")
    else:
        print(f"{i+1}. {product} - Price TBD")

# List comprehension (powerful for data transformation)
discounted_prices = [price * 0.9 for price in prices]  # 10% discount
print(f"\nDiscounted prices: {discounted_prices}")

# Filtering with list comprehension
affordable_products = [products[i] for i, price in enumerate(prices) if price < 800]
print(f"Affordable products (< $800): {affordable_products}")

# 3. WHILE LOOPS
print("\n=== While Loops ===")

# Simulating pagination in web scraping
page = 1
max_pages = 3
scraped_items = []

while page <= max_pages:
    # Simulate scraping a page
    items_on_page = [f"Item {i + (page-1)*5}" for i in range(1, 6)]
    scraped_items.extend(items_on_page)
    print(f"Scraped page {page}: {items_on_page}")
    page += 1

print(f"Total scraped items: {len(scraped_items)}")

# 4. CONDITIONAL STATEMENTS
print("\n=== Conditional Logic ===")

def categorize_product(price):
    """Categorize products by price - useful for scraped data analysis"""
    if price < 500:
        return "Budget"
    elif price < 800:
        return "Mid-range"
    elif price < 1200:
        return "Premium"
    else:
        return "Luxury"

# Apply categorization to products
for product, price in zip(products[:len(prices)], prices):
    category = categorize_product(price)
    availability = "✅ Available" if prices.index(price) < len(in_stock) and in_stock[prices.index(price)] else "❌ Out of Stock"
    print(f"{product}: ${price} - {category} - {availability}")

# 5. NESTED LOOPS (for complex data structures)
print("\n=== Nested Data Processing ===")

# Simulating multiple product categories
categories = {
    "Smartphones": [
        {"name": "iPhone 15", "price": 999.99, "rating": 4.5},
        {"name": "Galaxy S24", "price": 899.99, "rating": 4.3}
    ],
    "Laptops": [
        {"name": "MacBook Pro", "price": 1999.99, "rating": 4.7},
        {"name": "Dell XPS", "price": 1299.99, "rating": 4.4}
    ]
}

print("Product Catalog:")
for category, items in categories.items():
    print(f"\n📱 {category}:")
    for item in items:
        rating_stars = "⭐" * int(item["rating"])
        print(f"  • {item['name']}: ${item['price']} {rating_stars}")

# 6. PRACTICE EXERCISES
print("\n=== Practice Exercises ===")

# Exercise 1: Price tracking simulation
price_history = [999.99, 949.99, 899.99, 879.99, 899.99]
product_name = "iPhone 15"

print(f"\nPrice history for {product_name}:")
for i, price in enumerate(price_history):
    trend = ""
    if i > 0:
        if price > price_history[i-1]:
            trend = "📈 UP"
        elif price < price_history[i-1]:
            trend = "📉 DOWN"
        else:
            trend = "➡️ SAME"
    
    print(f"Day {i+1}: ${price} {trend}")

# Find best price
min_price = min(price_history)
max_price = max(price_history)
current_price = price_history[-1]

print(f"\n📊 Price Analysis:")
print(f"Lowest price: ${min_price}")
print(f"Highest price: ${max_price}")
print(f"Current price: ${current_price}")
print(f"Savings from peak: ${max_price - current_price:.2f}")

if __name__ == "__main__":
    print("\n✅ Day 2 Complete! Practice list problems on HackerRank.")
    print("📚 HackerRank Focus: List comprehensions, loops, nested lists")
    print("🎯 Tomorrow: Functions and Dictionaries")

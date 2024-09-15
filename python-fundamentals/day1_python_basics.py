# Day 1: Python Basics Review - Variables and Data Types
# Review fundamentals before moving to advanced concepts

# 1. VARIABLES AND DATA TYPES
print("=== Day 1: Variables and Data Types ===\n")

# Basic variable assignment
name = "Python Developer"
age = 25
salary = 75000.50
is_employed = True

print(f"Name: {name} (type: {type(name).__name__})")
print(f"Age: {age} (type: {type(age).__name__})")
print(f"Salary: ${salary} (type: {type(salary).__name__})")
print(f"Employed: {is_employed} (type: {type(is_employed).__name__})\n")

# 2. STRINGS - Essential for web scraping
print("=== String Operations ===")
text = "Web Scraping with Python"
print(f"Original: {text}")
print(f"Uppercase: {text.upper()}")
print(f"Lowercase: {text.lower()}")
print(f"Split: {text.split()}")
print(f"Replace: {text.replace('Python', 'BeautifulSoup')}")
print(f"Length: {len(text)}")

# String formatting (crucial for URLs and data processing)
product_name = "iPhone 15"
price = 999.99
url_template = "https://amazon.com/search?q={}&price={}"
formatted_url = url_template.format(product_name.replace(" ", "+"), price)
print(f"Formatted URL: {formatted_url}\n")

# 3. NUMBERS AND CALCULATIONS
print("=== Number Operations ===")
base_price = 100
discount_percent = 15
final_price = base_price * (1 - discount_percent / 100)
print(f"Base Price: ${base_price}")
print(f"Discount: {discount_percent}%")
print(f"Final Price: ${final_price:.2f}\n")

# 4. PRACTICE EXERCISES
print("=== Practice Exercises ===")

# Exercise 1: Create variables for a product listing
product_id = "PROD001"
product_name = "Gaming Laptop"
original_price = 1299.99
discount = 20
stock_quantity = 15

discounted_price = original_price * (1 - discount / 100)

print("Product Information:")
print(f"ID: {product_id}")
print(f"Name: {product_name}")
print(f"Original Price: ${original_price}")
print(f"Discount: {discount}%")
print(f"Sale Price: ${discounted_price:.2f}")
print(f"In Stock: {stock_quantity > 0}")
print(f"Stock Level: {stock_quantity} units")

if __name__ == "__main__":
    print("\n✅ Day 1 Complete! Practice these concepts on HackerRank.")
    print("📚 HackerRank Focus: Python introduction problems")
    print("🎯 Tomorrow: Lists, Dictionaries, and Control Flow")

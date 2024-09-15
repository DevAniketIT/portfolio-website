# Day 4: Web Scraping Fundamentals
# Learn requests, BeautifulSoup, and basic scraping techniques

import requests
from bs4 import BeautifulSoup
import time
import json
from urllib.parse import urljoin
import pandas as pd

print("=== Day 4: Web Scraping Fundamentals ===\n")

# 1. REQUESTS LIBRARY BASICS
print("=== 1. Making HTTP Requests ===")

def basic_request_example():
    """Demonstrate basic HTTP requests"""
    
    # Example 1: Simple GET request
    url = "https://httpbin.org/get"
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print(f"Content Type: {response.headers.get('content-type')}")
        print(f"Response Length: {len(response.text)} characters")
        
        # Parse JSON response
        data = response.json()
        print(f"Your IP Address: {data.get('origin', 'Unknown')}")
        
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

def headers_and_user_agents():
    """Demonstrate using headers and user agents"""
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    url = "https://httpbin.org/headers"
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        print("\n=== Request Headers ===")
        for header, value in data['headers'].items():
            print(f"{header}: {value}")
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

# 2. BEAUTIFULSOUP BASICS
print("\n=== 2. HTML Parsing with BeautifulSoup ===")

def parse_html_example():
    """Demonstrate HTML parsing techniques"""
    
    # Sample HTML (like what you'd get from a product page)
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sample Product Page</title>
    </head>
    <body>
        <div class="container">
            <div class="product" id="product-1">
                <h1 class="product-title">iPhone 15 Pro</h1>
                <div class="price">
                    <span class="current-price">$999.99</span>
                    <span class="old-price">$1199.99</span>
                </div>
                <div class="rating">
                    <span class="stars">★★★★☆</span>
                    <span class="review-count">(1,245 reviews)</span>
                </div>
                <p class="description">Latest iPhone with advanced camera system</p>
                <div class="availability">In Stock</div>
            </div>
            
            <div class="product" id="product-2">
                <h1 class="product-title">Galaxy S24 Ultra</h1>
                <div class="price">
                    <span class="current-price">$1199.99</span>
                </div>
                <div class="rating">
                    <span class="stars">★★★★★</span>
                    <span class="review-count">(892 reviews)</span>
                </div>
                <p class="description">Samsung's flagship with S Pen</p>
                <div class="availability">Out of Stock</div>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Parse HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    print("📄 Parsing HTML Content:")
    
    # Find elements by different methods
    print("\n1. Find by tag:")
    title = soup.find('title')
    print(f"Page title: {title.text if title else 'Not found'}")
    
    print("\n2. Find by class:")
    products = soup.find_all('div', class_='product')
    print(f"Found {len(products)} products")
    
    print("\n3. Find by ID:")
    product1 = soup.find('div', id='product-1')
    if product1:
        name = product1.find('h1', class_='product-title').text
        price = product1.find('span', class_='current-price').text
        print(f"Product 1: {name} - {price}")
    
    print("\n4. CSS Selectors:")
    all_prices = soup.select('.current-price')
    for i, price in enumerate(all_prices, 1):
        print(f"Product {i} price: {price.text}")
    
    return soup

def extract_product_data(soup):
    """Extract structured data from parsed HTML"""
    
    products = []
    
    for product_div in soup.find_all('div', class_='product'):
        # Extract product information
        product_data = {}
        
        # Product name
        title_elem = product_div.find('h1', class_='product-title')
        product_data['name'] = title_elem.text.strip() if title_elem else 'N/A'
        
        # Current price
        price_elem = product_div.find('span', class_='current-price')
        if price_elem:
            # Remove $ symbol and convert to float
            price_text = price_elem.text.strip().replace('$', '').replace(',', '')
            try:
                product_data['price'] = float(price_text)
            except ValueError:
                product_data['price'] = 0.0
        else:
            product_data['price'] = 0.0
        
        # Old price (if exists)
        old_price_elem = product_div.find('span', class_='old-price')
        if old_price_elem:
            old_price_text = old_price_elem.text.strip().replace('$', '').replace(',', '')
            try:
                product_data['old_price'] = float(old_price_text)
                product_data['discount_percent'] = round(((product_data['old_price'] - product_data['price']) / product_data['old_price']) * 100, 2)
            except ValueError:
                product_data['old_price'] = product_data['price']
                product_data['discount_percent'] = 0.0
        else:
            product_data['old_price'] = product_data['price']
            product_data['discount_percent'] = 0.0
        
        # Rating and reviews
        stars_elem = product_div.find('span', class_='stars')
        product_data['rating'] = len(stars_elem.text) if stars_elem else 0
        
        reviews_elem = product_div.find('span', class_='review-count')
        if reviews_elem:
            # Extract number from "(1,245 reviews)" format
            reviews_text = reviews_elem.text.strip()
            import re
            reviews_match = re.search(r'\(([\d,]+)', reviews_text)
            if reviews_match:
                product_data['review_count'] = int(reviews_match.group(1).replace(',', ''))
            else:
                product_data['review_count'] = 0
        else:
            product_data['review_count'] = 0
        
        # Description
        desc_elem = product_div.find('p', class_='description')
        product_data['description'] = desc_elem.text.strip() if desc_elem else 'N/A'
        
        # Availability
        avail_elem = product_div.find('div', class_='availability')
        product_data['in_stock'] = 'in stock' in avail_elem.text.lower() if avail_elem else False
        
        products.append(product_data)
    
    return products

# 3. WEB SCRAPING BEST PRACTICES
print("\n=== 3. Web Scraping Best Practices ===")

class WebScraper:
    """A basic web scraper with best practices"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def get_page(self, url, delay=1):
        """Fetch a web page with error handling and rate limiting"""
        
        try:
            # Rate limiting - be respectful
            time.sleep(delay)
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()  # Raises an HTTPError for bad responses
            
            return response
            
        except requests.exceptions.Timeout:
            print(f"❌ Timeout error for {url}")
            return None
        except requests.exceptions.ConnectionError:
            print(f"❌ Connection error for {url}")
            return None
        except requests.exceptions.HTTPError as e:
            print(f"❌ HTTP error {e.response.status_code} for {url}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Request error: {e}")
            return None
    
    def parse_quotes_example(self):
        """Example: Scraping quotes from quotes.toscrape.com"""
        
        url = "http://quotes.toscrape.com/"
        
        print(f"🌐 Scraping quotes from: {url}")
        
        response = self.get_page(url)
        if not response:
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        quotes = []
        
        # Find all quote containers
        quote_divs = soup.find_all('div', class_='quote')
        
        for quote_div in quote_divs:
            quote_data = {}
            
            # Extract quote text
            text_elem = quote_div.find('span', class_='text')
            quote_data['text'] = text_elem.text.strip() if text_elem else 'N/A'
            
            # Extract author
            author_elem = quote_div.find('small', class_='author')
            quote_data['author'] = author_elem.text.strip() if author_elem else 'Unknown'
            
            # Extract tags
            tag_elems = quote_div.find_all('a', class_='tag')
            quote_data['tags'] = [tag.text.strip() for tag in tag_elems]
            
            quotes.append(quote_data)
        
        return quotes

# 4. PRACTICAL EXERCISES
print("\n=== 4. Practical Exercises ===")

def demo_scraping():
    """Demonstrate the scraping techniques"""
    
    # Basic request examples
    print("🔄 Making basic requests...")
    basic_request_example()
    headers_and_user_agents()
    
    # HTML parsing examples
    print("\n📊 Parsing HTML...")
    soup = parse_html_example()
    
    # Data extraction
    print("\n🔍 Extracting structured data...")
    products = extract_product_data(soup)
    
    print(f"\n📦 Extracted {len(products)} products:")
    for product in products:
        print(f"• {product['name']}: ${product['price']}")
        if product['discount_percent'] > 0:
            print(f"  💰 {product['discount_percent']}% discount!")
        print(f"  ⭐ Rating: {product['rating']}/5 ({product['review_count']} reviews)")
        print(f"  📦 {'✅ In Stock' if product['in_stock'] else '❌ Out of Stock'}")
        print()
    
    # Real website scraping example
    print("🌐 Live scraping example...")
    scraper = WebScraper()
    quotes = scraper.parse_quotes_example()
    
    if quotes:
        print(f"\n💬 Found {len(quotes)} quotes:")
        for i, quote in enumerate(quotes[:3], 1):  # Show first 3
            print(f"{i}. \"{quote['text']}\" - {quote['author']}")
            print(f"   Tags: {', '.join(quote['tags'])}")
        
        if len(quotes) > 3:
            print(f"   ... and {len(quotes) - 3} more quotes")
    
    # Save data to CSV
    if products:
        df = pd.DataFrame(products)
        csv_filename = 'scraped_products.csv'
        df.to_csv(csv_filename, index=False)
        print(f"\n💾 Saved product data to {csv_filename}")
        print(f"📊 Data shape: {df.shape[0]} rows, {df.shape[1]} columns")

if __name__ == "__main__":
    demo_scraping()
    
    print("\n✅ Day 4 Complete! You've learned web scraping fundamentals!")
    print("🎯 Key Skills Acquired:")
    print("   • Making HTTP requests with proper headers")
    print("   • Parsing HTML with BeautifulSoup")
    print("   • Extracting structured data")
    print("   • Handling errors and rate limiting")
    print("   • Saving data to CSV files")
    print("\n📚 Tomorrow: Advanced scraping techniques and price monitoring")
    print("💰 Freelance Tip: Many clients need basic data extraction - you're ready for $20-30/hour jobs!")
